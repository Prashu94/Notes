# AWS Key Management Service (KMS) - SAA-C03 Certification Guide

## Table of Contents
1. [Introduction to AWS KMS](#introduction-to-aws-kms)
2. [KMS Fundamentals](#kms-fundamentals)
3. [Key Management](#key-management)
4. [AWS Service Integration](#aws-service-integration)
5. [Security and Compliance](#security-and-compliance)
6. [Exam Scenarios and Use Cases](#exam-scenarios-and-use-cases)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Cost Optimization](#cost-optimization)
10. [AWS CLI Commands Reference](#aws-cli-commands-reference)
11. [Exam Tips and Key Takeaways](#exam-tips-and-key-takeaways)

---

## Introduction to AWS KMS

AWS Key Management Service (KMS) is a managed service that makes it easy for you to create and control the cryptographic keys used to encrypt your data. KMS is integrated with most AWS services to help protect data at rest and in transit.

### Key Benefits
- **Centralized Key Management**: Single point of control for encryption keys
- **Integrated with AWS Services**: Seamless encryption across AWS ecosystem
- **Compliance**: Meets various compliance requirements (FIPS 140-2, Common Criteria)
- **Audit Trail**: Complete logging through AWS CloudTrail
- **High Availability**: Multi-AZ deployment with 99.999% availability SLA

### KMS Use Cases
- **Data at Rest Encryption**: EBS volumes, S3 objects, RDS databases
- **Data in Transit Encryption**: Application-level encryption
- **Digital Signing**: Code signing, document signing
- **Compliance Requirements**: Meeting regulatory standards
- **Cross-Account Access**: Secure data sharing between AWS accounts

---

## KMS Fundamentals

### Encryption Basics

#### Symmetric vs Asymmetric Encryption
- **Symmetric Encryption**: Uses the same key for encryption and decryption
  - Faster performance
  - Used for bulk data encryption
  - AES-256 is the standard
- **Asymmetric Encryption**: Uses public/private key pairs
  - Slower performance
  - Used for key exchange and digital signatures
  - RSA and ECC algorithms

#### Encryption at Rest vs In Transit
- **At Rest**: Data stored on disk (EBS, S3, RDS)
- **In Transit**: Data moving between systems (TLS/SSL)

### KMS Key Types

#### Customer Master Keys (CMKs) - Now called KMS Keys
1. **AWS Managed Keys**
   - Created and managed by AWS services
   - Prefix: `aws/service-name` (e.g., `aws/s3`, `aws/ebs`)
   - Free to use
   - Cannot be deleted
   - Automatic rotation every 3 years

2. **Customer Managed Keys**
   - Created and managed by you
   - Full control over key policies and permissions
   - $1/month per key
   - Optional automatic rotation (yearly)
   - Can be deleted (with 7-30 day waiting period)

3. **AWS Owned Keys**
   - Owned and managed by AWS
   - Used in shared AWS services
   - Not visible in your account
   - No additional charges

#### Key Specifications
- **Symmetric Keys (AES-256)**
  - Default key type
  - Used for encrypt/decrypt operations
  - Maximum 4 KB of data per operation
  
- **Asymmetric Keys**
  - RSA keys (2048, 3072, 4096 bits)
  - ECC keys (256, 384, 521 bits)
  - Used for encrypt/decrypt or sign/verify

### Key Policies

#### Resource-Based Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:user/ExampleUser"},
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Key Policy Elements
- **Principal**: Who can use the key
- **Action**: What operations are allowed
- **Resource**: Which keys the policy applies to
- **Condition**: Additional constraints

### Data Keys

#### Envelope Encryption
KMS uses envelope encryption for large data:
1. **Data Encryption Key (DEK)**: Encrypts the actual data
2. **Key Encryption Key (KEK)**: Encrypts the DEK
3. KMS generates and encrypts DEKs with your CMK

#### GenerateDataKey API
- Returns plaintext and encrypted versions of DEK
- Use plaintext DEK to encrypt data, then discard it
- Store encrypted DEK with encrypted data
- Use Decrypt API to get plaintext DEK for decryption

### Encryption Context

#### Purpose and Benefits
- Additional authenticated data (AAD)
- Key-value pairs for additional security
- Logged in CloudTrail for auditing
- Cannot be used to decrypt without correct context

#### Example Usage
```json
{
  "Department": "Finance",
  "Project": "Alpha",
  "FilePath": "/secure/financial-data.csv"
}
```

### Multi-Region Keys

#### Features
- Same key ID and key material across regions
- Encrypted in one region, decrypt in another
- Disaster recovery and global applications
- Each replica can have different key policies

#### Use Cases
- Cross-region backup and restore
- Global applications requiring consistent encryption
- Disaster recovery scenarios

---

## Key Management

### Key Creation

#### Creating Customer Managed Keys
1. **Console Creation**
   - Navigate to KMS in AWS Console
   - Choose key type (symmetric/asymmetric)
   - Define key policy
   - Set key administrators and users

2. **CLI Creation**
```bash
aws kms create-key \
    --description "My application key" \
    --key-usage ENCRYPT_DECRYPT \
    --key-spec SYMMETRIC_DEFAULT
```

3. **CloudFormation Template**
```yaml
Resources:
  MyKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: "My application encryption key"
      KeyPolicy:
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Action: "kms:*"
            Resource: "*"
  
  MyKMSKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: alias/my-app-key
      TargetKeyId: !Ref MyKMSKey
```

### Key Rotation

#### Automatic Rotation
- **Customer Managed Keys**: Optional, yearly rotation
- **AWS Managed Keys**: Automatic, every 3 years
- **Process**: AWS generates new key material, keeps old versions
- **Backward Compatibility**: Old encrypted data remains accessible

#### Manual Rotation
- Create new key
- Update applications to use new key
- Re-encrypt data with new key
- Delete old key (after transition period)

#### Rotation Best Practices
- Enable automatic rotation for customer managed keys
- Monitor rotation through CloudWatch
- Test applications with rotated keys
- Document key rotation procedures

### Key Deletion

#### Scheduled Deletion
- **Waiting Period**: 7 to 30 days (default 30)
- **Purpose**: Prevent accidental deletion
- **During Period**: Key cannot be used for cryptographic operations
- **Cancellation**: Can cancel deletion before period expires

#### Key Deletion Process
1. Schedule deletion with waiting period
2. Monitor CloudWatch alarms for key usage
3. Verify no applications depend on the key
4. Key automatically deleted after waiting period

#### Pre-Deletion Checklist
- [ ] Identify all encrypted resources using the key
- [ ] Migrate data to new keys if needed
- [ ] Update application configurations
- [ ] Remove key from IAM policies
- [ ] Check CloudTrail logs for recent usage

### Key States

#### Key State Lifecycle
1. **Creating**: Key is being created
2. **Enabled**: Key is ready for cryptographic operations
3. **Disabled**: Key exists but cannot be used
4. **PendingDeletion**: Scheduled for deletion
5. **PendingImport**: Waiting for key material import
6. **PendingReplicaCreation**: Multi-region key replica being created
7. **Unavailable**: Key material unavailable (rare)

#### State Transitions
- **Enable/Disable**: Immediate state change
- **Deletion**: Requires waiting period
- **Import**: Manual process for BYOK (Bring Your Own Key)

### Key Material Import (BYOK)

#### When to Use BYOK
- Regulatory requirements for key control
- Integration with existing key management systems
- Specific entropy requirements
- Air-gapped key generation

#### BYOK Process
1. Create KMS key without key material
2. Download public key and import token
3. Encrypt your key material with public key
4. Import encrypted key material
5. Set expiration for key material (optional)

#### BYOK Limitations
- No automatic rotation
- Manual key material management
- Key material can expire
- More complex operational overhead

---

## AWS Service Integration

### Amazon S3 Encryption

#### S3 Server-Side Encryption Options
1. **SSE-S3 (AES-256)**
   - AWS managed encryption keys
   - No additional cost
   - Automatic for new buckets (default)

2. **SSE-KMS**
   - KMS managed keys
   - Additional KMS charges apply
   - Granular access control via key policies
   - CloudTrail logging of key usage

3. **SSE-C (Customer Provided)**
   - Customer manages encryption keys
   - Keys provided with each request
   - AWS does not store keys

#### S3 Bucket Encryption Configuration
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

#### S3 Bucket Key
- Reduces KMS API calls by using S3-generated data keys
- Decreases KMS costs for high-volume operations
- One key per bucket per day (by default)
- CloudTrail shows bucket-level operations instead of object-level

### Amazon EBS Encryption

#### EBS Encryption Features
- **Default Encryption**: Encrypt all new volumes by default
- **In-Transit Encryption**: Between EC2 and EBS
- **Snapshot Encryption**: Encrypted snapshots from encrypted volumes
- **Performance**: Minimal impact on IOPS and throughput

#### Creating Encrypted EBS Volumes
```bash
# Create encrypted volume
aws ec2 create-volume \
    --size 100 \
    --volume-type gp3 \
    --availability-zone us-east-1a \
    --encrypted \
    --kms-key-id alias/my-ebs-key
```

#### EBS Encryption Scenarios
- **Encrypt Existing Volume**: Create snapshot → Copy with encryption → Create volume from encrypted snapshot
- **Cross-Region**: Copy encrypted snapshot to another region with different KMS key
- **Cross-Account**: Share encrypted snapshots using KMS key policies

### Amazon RDS Encryption

#### RDS Encryption at Rest
- **Supported Engines**: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server
- **Key Management**: AWS managed or customer managed KMS keys
- **Encryption Scope**: DB instance, logs, automated backups, snapshots, read replicas

#### Enabling RDS Encryption
```bash
# Create encrypted RDS instance
aws rds create-db-instance \
    --db-instance-identifier mydb \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username admin \
    --master-user-password mypassword \
    --storage-encrypted \
    --kms-key-id alias/my-rds-key
```

#### RDS Encryption Limitations
- Cannot enable encryption on existing unencrypted instances
- Cannot disable encryption once enabled
- Read replicas inherit encryption from master
- Cross-region replicas can use different KMS keys

### AWS Lambda Encryption

#### Lambda Environment Variable Encryption
```python
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Environment variables are automatically decrypted
    db_password = os.environ['DB_PASSWORD']
    
    # Manual encryption/decryption example
    kms = boto3.client('kms')
    try:
        # Decrypt data
        response = kms.decrypt(
            CiphertextBlob=encrypted_data,
            EncryptionContext={'purpose': 'lambda-secrets'}
        )
        plaintext = response['Plaintext'].decode()
    except ClientError as e:
        print(f"Decryption failed: {e}")
        return {'statusCode': 500}
    
    return {'statusCode': 200}
```

#### Lambda Encryption Options
- **Environment Variables**: Encrypted at rest using AWS managed or customer managed keys
- **Function Code**: Encrypted in transit and at rest
- **Dead Letter Queues**: Can be encrypted with KMS

### Amazon CloudWatch Logs

#### Log Group Encryption
- Encrypt log streams within a log group
- Use AWS managed or customer managed KMS keys
- Retroactive encryption not supported
- Must specify encryption at log group creation

```bash
# Create encrypted log group
aws logs create-log-group \
    --log-group-name /my/application/logs \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
```

### Amazon SNS and SQS

#### SNS Topic Encryption
```bash
# Create encrypted SNS topic
aws sns create-topic \
    --name my-encrypted-topic \
    --attributes KmsMasterKeyId=alias/my-sns-key
```

#### SQS Queue Encryption
```bash
# Create encrypted SQS queue
aws sqs create-queue \
    --queue-name my-encrypted-queue \
    --attributes KmsMasterKeyId=alias/my-sqs-key,KmsDataKeyReusePeriodSeconds=300
```

### AWS Systems Manager Parameter Store

#### Parameter Encryption Types
- **Standard Parameters**: Free, up to 4KB
- **Advanced Parameters**: Additional charges, up to 8KB
- **SecureString**: Encrypted using KMS

```bash
# Create encrypted parameter
aws ssm put-parameter \
    --name "/myapp/db/password" \
    --value "mysecretpassword" \
    --type "SecureString" \
    --key-id "alias/my-app-key"
```

### Cross-Service Integration Patterns

#### Shared KMS Keys
- Single key for multiple services
- Simplified key management
- Consistent access control
- Cost optimization through key reuse

#### Service-Specific Keys
- Granular access control
- Service isolation
- Independent rotation schedules
- Compliance requirements

#### Cross-Account Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCrossAccountAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT-B:root"
      },
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": "s3.us-east-1.amazonaws.com"
        }
      }
    }
  ]
}
```

---

## Security and Compliance

### Compliance Standards

#### FIPS 140-2 Level 2
- **Validation**: KMS meets FIPS 140-2 Level 2 requirements
- **Hardware Security Modules (HSMs)**: FIPS validated HSMs protect keys
- **Government Workloads**: Required for many US government applications
- **Compliance Evidence**: AWS provides compliance attestations

#### Common Criteria
- **ISO/IEC 15408**: International security evaluation standard
- **Evaluation Assurance Level (EAL)**: KMS meets EAL 4+ requirements
- **Global Recognition**: Accepted in multiple countries
- **Third-Party Validation**: Independent security evaluation

#### Industry Compliance Frameworks
- **PCI DSS**: Payment card industry data security standard
- **HIPAA**: Health Insurance Portability and Accountability Act
- **SOX**: Sarbanes-Oxley Act requirements
- **GDPR**: General Data Protection Regulation

### CloudTrail Integration

#### KMS API Logging
```json
{
  "eventTime": "2023-01-15T10:30:00Z",
  "eventName": "Decrypt",
  "eventSource": "kms.amazonaws.com",
  "sourceIPAddress": "203.0.113.1",
  "userAgent": "aws-cli/2.0.0",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDACKCEVSQ6C2EXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/ExampleUser",
    "accountId": "123456789012",
    "userName": "ExampleUser"
  },
  "requestParameters": {
    "keyId": "arn:aws:kms:us-east-1:123456789012:key/1234abcd-12ab-34cd-56ef-1234567890ab",
    "encryptionContext": {
      "SecretARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:MyTestDatabaseSecret-a1b2c3"
    }
  }
}
```

#### Monitoring Key Usage
- **API Calls**: All KMS API calls logged to CloudTrail
- **Encryption Context**: Provides additional audit information
- **Cross-Service Usage**: Service-specific logs show KMS integration
- **Real-Time Monitoring**: CloudWatch integration for alerting

### Key Policies and IAM

#### Principle of Least Privilege
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEncryptionOnly",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/ApplicationRole"
      },
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "kms:EncryptionContext:Application": "MyApp"
        }
      }
    }
  ]
}
```

#### IAM vs Key Policies
- **IAM Policies**: Identity-based permissions
- **Key Policies**: Resource-based permissions
- **Effective Permissions**: Union of both policy types
- **Key Policy Required**: At minimum, must allow root account access

#### Conditional Access Controls
```json
{
  "Condition": {
    "StringEquals": {
      "kms:ViaService": "s3.us-east-1.amazonaws.com"
    },
    "Bool": {
      "kms:GrantIsForAWSResource": "true"
    },
    "DateGreaterThan": {
      "aws:CurrentTime": "2023-01-01T00:00:00Z"
    }
  }
}
```

### Grants

#### When to Use Grants
- Temporary permissions
- Service-to-service delegation
- Cross-account access without key policy changes
- Programmatic access control

#### Grant Operations
```bash
# Create grant
aws kms create-grant \
    --key-id 1234abcd-12ab-34cd-56ef-1234567890ab \
    --grantee-principal arn:aws:iam::123456789012:role/ExampleRole \
    --operations Decrypt GenerateDataKey \
    --constraints EncryptionContextSubset={Department=Finance}

# List grants
aws kms list-grants --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Retire grant
aws kms retire-grant --key-id 1234abcd-12ab-34cd-56ef-1234567890ab --grant-token <token>
```

### Monitoring and Alerting

#### CloudWatch Metrics
- **NumberOfRequestsSucceeded**: Successful API calls
- **NumberOfRequestsFailed**: Failed API calls  
- **ApiCallCount**: Total API calls per key
- **KeyUsage**: Frequency of key operations

#### CloudWatch Alarms
```bash
# Create alarm for unusual key activity
aws cloudwatch put-metric-alarm \
    --alarm-name "KMS-HighUsage" \
    --alarm-description "Alarm for high KMS key usage" \
    --metric-name NumberOfRequestsSucceeded \
    --namespace AWS/KMS \
    --statistic Sum \
    --period 300 \
    --threshold 1000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=KeyId,Value=1234abcd-12ab-34cd-56ef-1234567890ab
```

#### Security Monitoring Best Practices
- Monitor failed decrypt attempts
- Alert on key policy changes
- Track cross-account access patterns
- Monitor key deletion attempts
- Set up notifications for unusual usage patterns

### Data Protection Strategies

#### Defense in Depth
1. **Network Security**: VPC, security groups, NACLs
2. **IAM Controls**: Least privilege access
3. **Encryption**: Data at rest and in transit
4. **Monitoring**: CloudTrail, CloudWatch
5. **Backup**: Regular encrypted backups

#### Key Segmentation Strategies
- **Environment-Based**: Separate keys for dev/test/prod
- **Application-Based**: One key per application
- **Data Classification**: Keys based on data sensitivity
- **Geographic**: Regional key distribution

---

## Exam Scenarios and Use Cases

### Common SAA-C03 Exam Scenarios

#### Scenario 1: S3 Cross-Region Replication with Encryption
**Question Type**: You need to replicate encrypted S3 objects to another region.

**Key Points**:
- Source bucket uses SSE-KMS encryption
- Destination bucket in different region
- Maintain encryption during replication

**Solution**:
```json
{
  "Role": "arn:aws:iam::123456789012:role/replication-role",
  "Rules": [
    {
      "Status": "Enabled",
      "Filter": {"Prefix": "documents/"},
      "ReplicaKmsKeyID": "arn:aws:kms:us-west-2:123456789012:key/destination-key-id",
      "Destination": {
        "Bucket": "arn:aws:s3:::destination-bucket",
        "StorageClass": "STANDARD_IA"
      }
    }
  ]
}
```

#### Scenario 2: Cross-Account EBS Snapshot Sharing
**Question Type**: Share encrypted EBS snapshots between AWS accounts.

**Requirements**:
- Account A has encrypted EBS snapshots
- Need to share with Account B
- Maintain security controls

**Solution Steps**:
1. Modify KMS key policy to allow Account B
2. Share snapshot with Account B
3. Account B creates volume from shared snapshot

**KMS Key Policy Addition**:
```json
{
  "Sid": "AllowAccountBAccess",
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::ACCOUNT-B:root"},
  "Action": [
    "kms:Decrypt",
    "kms:GenerateDataKey",
    "kms:CreateGrant"
  ],
  "Resource": "*"
}
```

#### Scenario 3: Lambda Function Environment Variable Encryption
**Question Type**: Secure sensitive data in Lambda environment variables.

**Options Analysis**:
- **SSE with AWS managed key**: Basic encryption, no additional cost
- **SSE with customer managed key**: Granular control, additional KMS costs
- **Client-side encryption**: Manual implementation required

**Best Practice**:
```python
import boto3
import os

def lambda_handler(event, context):
    # Environment variable automatically decrypted
    api_key = os.environ['ENCRYPTED_API_KEY']
    
    # Use the decrypted value
    return process_with_api_key(api_key)
```

#### Scenario 4: RDS Multi-AZ with Encryption
**Question Type**: Design highly available encrypted database solution.

**Requirements**:
- Multi-AZ deployment
- Encryption at rest
- Read replicas in different region

**Solution Architecture**:
- Primary RDS instance with KMS encryption
- Multi-AZ standby automatically encrypted
- Cross-region read replica with region-specific KMS key

#### Scenario 5: CloudTrail Log Encryption
**Question Type**: Secure audit logs for compliance requirements.

**Implementation**:
```bash
aws cloudtrail create-trail \
    --name ComplianceTrail \
    --s3-bucket-name compliance-logs-bucket \
    --kms-key-id alias/cloudtrail-key \
    --include-global-service-events \
    --is-multi-region-trail
```

### Decision Trees for Exam Questions

#### Encryption Key Selection Decision Tree
```
Need encryption for AWS service?
├── Yes
│   ├── Need granular access control?
│   │   ├── Yes → Customer Managed KMS Key
│   │   └── No → AWS Managed Key
│   ├── Need cross-region replication?
│   │   └── Yes → Multi-Region KMS Key
│   └── Need cross-account access?
│       └── Yes → Customer Managed Key + Key Policy
└── No → No encryption needed
```

#### Key Rotation Decision Tree
```
Key rotation needed?
├── Customer Managed Key
│   ├── Automatic rotation available? → Yes → Enable automatic
│   └── Complex rotation needed? → Yes → Manual rotation
├── AWS Managed Key
│   └── Automatic every 3 years (no control)
└── AWS Owned Key
    └── Managed by AWS (no visibility)
```

### Cost Optimization Scenarios

#### Scenario: High-Volume S3 Operations
**Problem**: High KMS costs due to frequent S3 operations

**Solutions**:
1. **Enable S3 Bucket Keys**: Reduce KMS API calls
2. **Use SSE-S3**: For less sensitive data
3. **Client-side encryption**: Reduce KMS dependency

**Cost Comparison**:
- Standard KMS: $0.03 per 10,000 requests
- With Bucket Key: ~99% reduction in KMS requests
- SSE-S3: No KMS charges

#### Scenario: Multi-Service Key Usage
**Problem**: Separate keys for each service increase costs

**Solution**: Shared KMS key for related services
```json
{
  "Sid": "AllowMultiServiceAccess",
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
  "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"],
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "kms:ViaService": [
        "s3.us-east-1.amazonaws.com",
        "lambda.us-east-1.amazonaws.com",
        "rds.us-east-1.amazonaws.com"
      ]
    }
  }
}
```

### Performance Considerations

#### KMS Request Limits
- **Shared limit**: 5,500-30,000 requests/second (varies by region)
- **Per-key limit**: None (uses shared quota)
- **Burst capability**: Available for short periods

#### Performance Optimization Strategies
1. **Data Key Caching**: Reduce KMS calls for encryption
2. **Connection Pooling**: Reuse KMS connections
3. **Regional Distribution**: Use appropriate regions
4. **Async Operations**: Non-blocking KMS calls where possible

```python
# Data key caching example
from aws_encryption_sdk import encrypt, decrypt
from aws_encryption_sdk.caches import LocalCryptoMaterialsCache
from aws_encryption_sdk.key_providers import KMSMasterKeyProvider

# Create cache
cache = LocalCryptoMaterialsCache(capacity=100)

# Create key provider with cache
key_provider = KMSMasterKeyProvider(
    key_ids=['arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012'],
    cache=cache
)
```

---

## Best Practices

### Security Best Practices

#### Key Management
- **Enable key rotation**: Automatic rotation for customer managed keys
- **Use least privilege**: Grant minimum necessary permissions
- **Separate keys by environment**: Dev, test, production isolation
- **Monitor key usage**: CloudTrail and CloudWatch integration
- **Regular access reviews**: Audit key policies and grants

#### Access Control
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RestrictToSpecificServices",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:role/ApplicationRole"},
      "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": ["s3.us-east-1.amazonaws.com"],
          "kms:EncryptionContext:application": "MySecureApp"
        }
      }
    }
  ]
}
```

#### Network Security
- **VPC Endpoints**: Private connectivity to KMS
- **Network ACLs**: Additional layer of security
- **Security Groups**: Control access to KMS endpoints

### Operational Best Practices

#### Automation
- **CloudFormation**: Infrastructure as code for keys
- **AWS Config**: Monitor key configuration compliance
- **Systems Manager**: Automated key management tasks

#### Documentation
- **Key inventory**: Maintain comprehensive key catalog
- **Access patterns**: Document who uses which keys
- **Rotation schedules**: Track key rotation status
- **Emergency procedures**: Key compromise response plan

#### Backup and Recovery
- **Cross-region replication**: Multi-region keys for DR
- **Key material backup**: For imported keys (BYOK)
- **Policy versioning**: Maintain key policy history

### Cost Optimization Best Practices

#### Key Consolidation
- Use shared keys for related applications
- Eliminate unused keys after proper validation
- Regular cost analysis and optimization

#### Request Optimization
```python
# Batch operations to reduce KMS calls
def encrypt_multiple_items(items, data_key):
    """Use single data key for multiple items"""
    encrypted_items = []
    for item in items:
        # Use same data key for multiple encryptions
        encrypted_item = encrypt_with_data_key(item, data_key)
        encrypted_items.append(encrypted_item)
    return encrypted_items
```

#### Service-Specific Optimizations
- **S3**: Enable bucket keys for high-volume operations
- **EBS**: Use default encryption with AWS managed keys for development
- **Lambda**: Cache decrypted environment variables

---

## Troubleshooting

### Common Issues and Solutions

#### Access Denied Errors

**Issue**: `AccessDeniedException` when using KMS
**Causes**:
- Insufficient IAM permissions
- Missing key policy permissions
- Incorrect encryption context
- Key disabled or deleted

**Debugging Steps**:
1. Check IAM policy permissions
2. Verify key policy allows the action
3. Confirm key state (enabled/disabled)
4. Validate encryption context matches

**Solution Example**:
```bash
# Check key policy
aws kms get-key-policy --key-id alias/my-key --policy-name default

# Check IAM permissions
aws iam simulate-principal-policy \
    --policy-source-arn arn:aws:iam::123456789012:user/testuser \
    --action-names kms:Decrypt \
    --resource-arns arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
```

#### Key State Issues

**Issue**: Key in wrong state for operations
**States and Solutions**:
- **Disabled**: Enable key with `enable-key` command
- **PendingDeletion**: Cancel deletion with `cancel-key-deletion`
- **Unavailable**: Check for service issues, contact AWS support

```bash
# Enable disabled key
aws kms enable-key --key-id alias/my-key

# Cancel key deletion
aws kms cancel-key-deletion --key-id alias/my-key
```

#### Encryption Context Mismatches

**Issue**: Decryption fails due to incorrect encryption context
**Solution**: Ensure exact match of encryption context

```python
# Correct usage with encryption context
import boto3

kms = boto3.client('kms')

# Encrypt with context
response = kms.encrypt(
    KeyId='alias/my-key',
    Plaintext='sensitive data',
    EncryptionContext={
        'purpose': 'user-data',
        'department': 'finance'
    }
)

# Decrypt with same context
decrypted = kms.decrypt(
    CiphertextBlob=response['CiphertextBlob'],
    EncryptionContext={
        'purpose': 'user-data',
        'department': 'finance'  # Must match exactly
    }
)
```

#### Cross-Region Issues

**Issue**: Key not accessible in different region
**Solutions**:
- Use multi-region keys for cross-region access
- Create region-specific keys and update applications
- Use cross-region replication with appropriate keys

#### Performance Issues

**Issue**: High latency or throttling
**Causes**:
- Exceeding service limits
- Inefficient key usage patterns
- Network connectivity issues

**Solutions**:
- Implement data key caching
- Use regional endpoints
- Optimize request patterns
- Consider VPC endpoints for private connectivity

### Monitoring and Alerting Setup

#### CloudWatch Dashboard
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/KMS", "NumberOfRequestsSucceeded", "KeyId", "alias/my-key"],
          ["AWS/KMS", "NumberOfRequestsFailed", "KeyId", "alias/my-key"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "KMS API Calls"
      }
    }
  ]
}
```

#### CloudWatch Alarms
```bash
# Alert on failed KMS requests
aws cloudwatch put-metric-alarm \
    --alarm-name "KMS-FailedRequests" \
    --alarm-description "Alert on KMS failures" \
    --metric-name NumberOfRequestsFailed \
    --namespace AWS/KMS \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold
```

---

## Cost Optimization

### KMS Pricing Model

#### Key Storage Costs
- **Customer Managed Keys**: $1.00 per month per key
- **AWS Managed Keys**: No additional charge
- **Multi-Region Keys**: $1.00 per month per region

#### API Request Costs
- **First 20,000 requests/month**: Free
- **Additional requests**: $0.03 per 10,000 requests
- **Asymmetric key operations**: Higher costs (varies by algorithm)

### Cost Optimization Strategies

#### Key Consolidation
```bash
# Audit key usage to identify consolidation opportunities
aws logs filter-log-events \
    --log-group-name CloudTrail/KMSLogs \
    --filter-pattern "{ $.eventSource = kms.amazonaws.com }" \
    --start-time 1640995200000 \
    --end-time 1643673600000
```

#### S3 Bucket Key Implementation
```yaml
# CloudFormation template with bucket key
Resources:
  MyS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !Ref MyKMSKey
            BucketKeyEnabled: true
```

#### Cost Monitoring
```bash
# Create Cost and Usage Report for KMS
aws cur put-report-definition \
    --report-definition '{
        "ReportName": "KMS-Usage-Report",
        "TimeUnit": "DAILY",
        "Format": "textORcsv",
        "Compression": "GZIP",
        "AdditionalSchemaElements": ["RESOURCES"],
        "S3Bucket": "my-billing-reports-bucket",
        "S3Prefix": "kms-reports/",
        "S3Region": "us-east-1",
        "AdditionalArtifacts": ["REDSHIFT", "QUICKSIGHT"]
    }'
```

---

## AWS CLI Commands Reference

### Creating KMS Keys

#### Create a Symmetric KMS Key
```bash
# Create a standard symmetric key for encryption/decryption
aws kms create-key \
  --description "My application encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --origin AWS_KMS

# Create a symmetric key with tags
aws kms create-key \
  --description "Production database encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --tags TagKey=Environment,TagValue=Production TagKey=Application,TagValue=Database

# Create a symmetric key with automatic rotation enabled
KEY_ID=$(aws kms create-key \
  --description "Auto-rotating encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --query 'KeyMetadata.KeyId' \
  --output text)

aws kms enable-key-rotation --key-id $KEY_ID
```

#### Create Asymmetric KMS Keys
```bash
# Create RSA key pair for encryption/decryption
aws kms create-key \
  --description "RSA key for asymmetric encryption" \
  --key-usage ENCRYPT_DECRYPT \
  --key-spec RSA_4096

# Create RSA key pair for signing/verification
aws kms create-key \
  --description "RSA key for digital signatures" \
  --key-usage SIGN_VERIFY \
  --key-spec RSA_4096

# Create ECC key pair for signing
aws kms create-key \
  --description "ECC key for digital signatures" \
  --key-usage SIGN_VERIFY \
  --key-spec ECC_NIST_P384
```

### Key Aliases

#### Create and Manage Aliases
```bash
# Create an alias for a key
aws kms create-alias \
  --alias-name alias/my-application-key \
  --target-key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Update an alias to point to a different key
aws kms update-alias \
  --alias-name alias/my-application-key \
  --target-key-id abcd1234-ab12-cd34-ef56-abcdef123456

# List all aliases
aws kms list-aliases

# List aliases for a specific key
aws kms list-aliases \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Delete an alias
aws kms delete-alias \
  --alias-name alias/old-application-key
```

### Encrypting and Decrypting Data

#### Symmetric Encryption Operations
```bash
# Encrypt plaintext data (max 4KB)
aws kms encrypt \
  --key-id alias/my-application-key \
  --plaintext "Sensitive data to encrypt" \
  --output text \
  --query CiphertextBlob | base64 --decode > encrypted_data.bin

# Encrypt with encryption context for additional security
aws kms encrypt \
  --key-id alias/my-application-key \
  --plaintext fileb://plaintext.txt \
  --encryption-context Department=Finance,Purpose=Audit \
  --query CiphertextBlob \
  --output text | base64 --decode > encrypted.bin

# Decrypt encrypted data
aws kms decrypt \
  --ciphertext-blob fileb://encrypted_data.bin \
  --query Plaintext \
  --output text | base64 --decode

# Decrypt with encryption context validation
aws kms decrypt \
  --ciphertext-blob fileb://encrypted.bin \
  --encryption-context Department=Finance,Purpose=Audit \
  --query Plaintext \
  --output text | base64 --decode
```

#### Re-encryption Operations
```bash
# Re-encrypt data with a different key (for key rotation)
aws kms re-encrypt \
  --ciphertext-blob fileb://old_encrypted.bin \
  --destination-key-id alias/new-application-key \
  --query CiphertextBlob \
  --output text | base64 --decode > new_encrypted.bin

# Re-encrypt with new encryption context
aws kms re-encrypt \
  --ciphertext-blob fileb://encrypted.bin \
  --source-encryption-context Department=Finance \
  --destination-key-id alias/my-key \
  --destination-encryption-context Department=Finance,Rotated=true \
  --query CiphertextBlob \
  --output text | base64 --decode > rotated.bin
```

### Data Key Generation

#### Generate Data Keys for Envelope Encryption
```bash
# Generate a 256-bit data key
aws kms generate-data-key \
  --key-id alias/my-application-key \
  --key-spec AES_256 \
  --query '{Plaintext:Plaintext,CiphertextBlob:CiphertextBlob}'

# Generate data key with encryption context
aws kms generate-data-key \
  --key-id alias/my-application-key \
  --key-spec AES_256 \
  --encryption-context Application=MyApp,Environment=Production

# Generate data key without plaintext (for distributed systems)
aws kms generate-data-key-without-plaintext \
  --key-id alias/my-application-key \
  --key-spec AES_256

# Generate a random 32-byte data key
aws kms generate-data-key \
  --key-id alias/my-application-key \
  --number-of-bytes 32

# Generate random bytes for salts, IVs, etc.
aws kms generate-random \
  --number-of-bytes 32 \
  --query Plaintext \
  --output text | base64 --decode > random_bytes.bin
```

### Key Policies and Permissions

#### View and Update Key Policies
```bash
# Get the key policy for a key
aws kms get-key-policy \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab \
  --policy-name default

# Create a key policy JSON file
cat > key-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key for encryption",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:role/MyAppRole"},
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow attachment of persistent resources",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:role/MyAppRole"},
      "Action": [
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {"kms:GrantIsForAWSResource": "true"}
      }
    }
  ]
}
EOF

# Update the key policy
aws kms put-key-policy \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab \
  --policy-name default \
  --policy file://key-policy.json
```

### Grants Management

#### Create and Manage Grants
```bash
# Create a grant for an IAM role to use a key
aws kms create-grant \
  --key-id alias/my-application-key \
  --grantee-principal arn:aws:iam::123456789012:role/MyAppRole \
  --operations Encrypt Decrypt GenerateDataKey DescribeKey

# Create a grant with constraints
aws kms create-grant \
  --key-id alias/my-application-key \
  --grantee-principal arn:aws:iam::123456789012:role/MyAppRole \
  --operations Encrypt Decrypt \
  --constraints EncryptionContextSubset={Department=Finance} \
  --retiring-principal arn:aws:iam::123456789012:role/AdminRole

# List grants for a key
aws kms list-grants \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Retire a grant
aws kms retire-grant \
  --grant-token <grant-token-from-create-grant>

# Revoke a grant
aws kms revoke-grant \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab \
  --grant-id 1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd
```

### Key Rotation

#### Enable and Manage Automatic Rotation
```bash
# Enable automatic key rotation (yearly)
aws kms enable-key-rotation \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Check if key rotation is enabled
aws kms get-key-rotation-status \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Disable key rotation
aws kms disable-key-rotation \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# List key rotations (shows rotation history)
aws kms list-key-rotations \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Rotate key on-demand (for customer managed keys)
aws kms rotate-key-on-demand \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab
```

### Key State Management

#### Enable, Disable, and Delete Keys
```bash
# Describe a key to check its status
aws kms describe-key \
  --key-id alias/my-application-key

# Disable a key (prevents its use but keeps it for decryption)
aws kms disable-key \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Enable a previously disabled key
aws kms enable-key \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Schedule key deletion (7-30 day waiting period)
aws kms schedule-key-deletion \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab \
  --pending-window-in-days 30

# Cancel key deletion
aws kms cancel-key-deletion \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab
```

### Importing Key Material

#### Import External Key Material
```bash
# Step 1: Create a key with no key material (EXTERNAL origin)
KEY_ID=$(aws kms create-key \
  --description "Key with imported material" \
  --origin EXTERNAL \
  --query 'KeyMetadata.KeyId' \
  --output text)

# Step 2: Download wrapping key and import token
aws kms get-parameters-for-import \
  --key-id $KEY_ID \
  --wrapping-algorithm RSAES_OAEP_SHA_256 \
  --wrapping-key-spec RSA_2048 \
  --query '{PublicKey:PublicKey,ImportToken:ImportToken}' > import-params.json

# Extract and save the public key
jq -r '.PublicKey' import-params.json | base64 --decode > wrapping-key.bin

# Extract and save the import token
jq -r '.ImportToken' import-params.json | base64 --decode > import-token.bin

# Step 3: Generate or obtain your key material (256-bit for AES-256)
openssl rand -out key-material.bin 32

# Step 4: Encrypt your key material with the wrapping key
openssl pkeyutl \
  -encrypt \
  -in key-material.bin \
  -out encrypted-key-material.bin \
  -inkey wrapping-key.bin \
  -keyform DER \
  -pubin \
  -pkeyopt rsa_padding_mode:oaep \
  -pkeyopt rsa_oaep_md:sha256

# Step 5: Import the encrypted key material
aws kms import-key-material \
  --key-id $KEY_ID \
  --encrypted-key-material fileb://encrypted-key-material.bin \
  --import-token fileb://import-token.bin \
  --expiration-model KEY_MATERIAL_DOES_NOT_EXPIRE

# Delete imported key material (keeps the key metadata)
aws kms delete-imported-key-material \
  --key-id $KEY_ID
```

### Listing and Describing Keys

#### Query KMS Keys
```bash
# List all KMS keys in the account
aws kms list-keys

# List keys with pagination
aws kms list-keys --max-results 10

# Describe a specific key
aws kms describe-key \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# List resource tags for a key
aws kms list-resource-tags \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab

# Tag a key
aws kms tag-resource \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab \
  --tags TagKey=CostCenter,TagValue=Engineering TagKey=Owner,TagValue=SecurityTeam

# Untag a key
aws kms untag-resource \
  --key-id 1234abcd-12ab-34cd-56ef-1234567890ab \
  --tag-keys CostCenter Owner
```

### Multi-Region Keys

#### Create and Manage Multi-Region Keys
```bash
# Create a multi-region primary key
PRIMARY_KEY_ID=$(aws kms create-key \
  --description "Multi-region primary key" \
  --multi-region \
  --query 'KeyMetadata.KeyId' \
  --output text)

# Replicate the key to another region
aws kms replicate-key \
  --key-id $PRIMARY_KEY_ID \
  --replica-region eu-west-1 \
  --description "EU replica of primary key"

# List all replicas of a multi-region key
aws kms describe-key \
  --key-id $PRIMARY_KEY_ID \
  --query 'KeyMetadata.MultiRegionConfiguration'

# Update primary region (promote a replica)
REPLICA_KEY_ID="mrk-1234567890abcdef"
aws kms update-primary-region \
  --key-id $PRIMARY_KEY_ID \
  --primary-region eu-west-1
```

### Signing and Verification (Asymmetric Keys)

#### Digital Signatures
```bash
# Create an asymmetric key for signing
SIGN_KEY_ID=$(aws kms create-key \
  --description "Digital signature key" \
  --key-usage SIGN_VERIFY \
  --key-spec RSA_4096 \
  --query 'KeyMetadata.KeyId' \
  --output text)

# Sign a message
aws kms sign \
  --key-id $SIGN_KEY_ID \
  --message fileb://message.txt \
  --message-type RAW \
  --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 \
  --query Signature \
  --output text | base64 --decode > signature.bin

# Get the public key for verification
aws kms get-public-key \
  --key-id $SIGN_KEY_ID \
  --query PublicKey \
  --output text | base64 --decode > public-key.der

# Verify a signature
aws kms verify \
  --key-id $SIGN_KEY_ID \
  --message fileb://message.txt \
  --message-type RAW \
  --signature fileb://signature.bin \
  --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256
```

### CloudWatch Integration

#### Monitor KMS Usage
```bash
# Get CloudWatch metrics for KMS usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/KMS \
  --metric-name NumberOfCalls \
  --dimensions Name=KeyId,Value=1234abcd-12ab-34cd-56ef-1234567890ab \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400 \
  --statistics Sum

# Set up CloudWatch alarm for KMS key usage
aws cloudwatch put-metric-alarm \
  --alarm-name kms-high-usage \
  --alarm-description "Alert when KMS key usage is high" \
  --metric-name NumberOfCalls \
  --namespace AWS/KMS \
  --statistic Sum \
  --period 300 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## Exam Tips and Key Takeaways

### Must-Know Concepts for SAA-C03

#### Core KMS Concepts
1. **Envelope Encryption**: KMS encrypts data keys, not data directly
2. **Key Types**: AWS managed vs Customer managed vs AWS owned
3. **Key Policies**: Resource-based policies are required
4. **Grants**: Temporary, programmatic permissions
5. **Multi-Region Keys**: Same key material across regions

#### Service Integration Patterns
- **S3**: SSE-KMS with bucket keys for cost optimization
- **EBS**: Default encryption for all volumes
- **RDS**: Cannot encrypt existing unencrypted instances
- **Lambda**: Environment variables encrypted at rest
- **CloudWatch Logs**: Encryption at log group creation only

#### Security Best Practices
- Always enable key rotation for customer managed keys
- Use encryption context for additional security
- Implement least privilege access
- Monitor key usage through CloudTrail
- Use VPC endpoints for private connectivity

### Common Exam Question Patterns

#### Scenario-Based Questions
1. **Cross-region replication**: Multi-region keys or region-specific keys
2. **Cross-account access**: Key policies with external account principals
3. **Compliance requirements**: Customer managed keys with audit trails
4. **Cost optimization**: AWS managed keys vs customer managed keys
5. **Performance**: Data key caching and request optimization

#### Distractor Analysis
- **AWS CloudHSM**: For dedicated hardware requirements (not typical KMS use)
- **Client-side encryption**: When KMS integration isn't available
- **AWS Secrets Manager**: For secret rotation, not general encryption
- **AWS Certificate Manager**: For SSL/TLS certificates, not data encryption

### Exam Day Quick Reference

#### Key Decision Factors
```
Choose Customer Managed Key when:
- Need key rotation control
- Require cross-account access
- Need detailed access logging
- Compliance requires customer control

Choose AWS Managed Key when:
- Simple encryption needs
- Cost optimization priority  
- No custom access control required
- Standard AWS service integration
```

#### Common CLI Commands
```bash
# Key operations
aws kms create-key --description "My key"
aws kms enable-key-rotation --key-id alias/my-key
aws kms get-key-rotation-status --key-id alias/my-key

# Encryption operations
aws kms encrypt --key-id alias/my-key --plaintext "data"
aws kms decrypt --ciphertext-blob fileb://encrypted-data

# Policy operations
aws kms get-key-policy --key-id alias/my-key --policy-name default
aws kms put-key-policy --key-id alias/my-key --policy-name default --policy file://policy.json
```

#### Performance Limits
- **API Requests**: 5,500-30,000 requests/second (region dependent)
- **Key Count**: No limit on keys per account
- **Data Size**: 4 KB maximum per Encrypt/Decrypt operation
- **Grants**: 10,000 grants per key maximum

---

## Summary

AWS KMS is a fundamental service for the SAA-C03 exam, appearing in multiple domains including security, storage, compute, and databases. Key exam focus areas include:

- Understanding when to use different key types
- Implementing proper access controls and policies
- Integrating KMS with other AWS services
- Optimizing for cost and performance
- Troubleshooting common encryption issues

Master these concepts with hands-on practice in the AWS console and CLI to ensure exam success. Remember that KMS questions often combine multiple AWS services, so understanding integration patterns is crucial for the Solutions Architect Associate certification.