# AWS Secrets Manager - SAA-C03 Study Guide

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Security and Compliance](#security-and-compliance)
4. [Integration with AWS Services](#integration-with-aws-services)
5. [Pricing Model](#pricing-model)
6. [Common Use Cases](#common-use-cases)
7. [Best Practices](#best-practices)
8. [Exam Tips and Common Scenarios](#exam-tips-and-common-scenarios)
9. [Hands-on Examples](#hands-on-examples)
10. [AWS CLI Commands Reference](#aws-cli-commands-reference)
11. [Comparison with Other Services](#comparison-with-other-services)

---

## Overview

### What is AWS Secrets Manager?

AWS Secrets Manager is a fully managed service that helps you protect access to your applications, services, and IT resources without the upfront investment and on-going maintenance costs of operating your own infrastructure. It enables you to easily rotate, manage, and retrieve database credentials, API keys, and other secrets throughout their lifecycle.

### Key Benefits

- **Centralized Secret Storage**: Store and manage secrets in a central location
- **Automatic Rotation**: Built-in rotation capabilities for supported services
- **Fine-grained Access Control**: Integration with AWS IAM for precise access management
- **Encryption**: Secrets are encrypted at rest and in transit
- **Audit and Compliance**: CloudTrail integration for comprehensive logging
- **Cross-Region Replication**: Replicate secrets across multiple regions for disaster recovery

### Core Concepts

- **Secret**: A set of credentials (username/password), database connection string, API key, or other sensitive information
- **Version**: Each time a secret is updated, a new version is created with a unique version ID
- **Rotation**: The process of periodically updating secret values to enhance security
- **Lambda Function**: Custom code that handles the rotation logic for unsupported services

---

## Key Features

### 1. Secret Storage and Retrieval

#### Supported Secret Types
- Database credentials (RDS, DocumentDB, Redshift)
- API keys and tokens
- SSH keys
- Third-party service credentials
- Custom key-value pairs

#### Secret Formats
```json
{
  "username": "admin",
  "password": "MySecretPassword123!",
  "engine": "mysql",
  "host": "mydb.cluster-abc123.us-east-1.rds.amazonaws.com",
  "port": 3306,
  "dbname": "mydb"
}
```

### 2. Automatic Rotation

#### Built-in Rotation Support
- **Amazon RDS**: MySQL, PostgreSQL, Oracle, SQL Server, MariaDB
- **Amazon DocumentDB**
- **Amazon Redshift**
- **Amazon ElastiCache** (Redis AUTH)

#### Custom Rotation
- Use Lambda functions for unsupported services
- Configurable rotation schedules (days, weeks, months)
- Multi-user rotation strategy for zero-downtime rotations

#### Rotation Process
1. **Create New Version**: Generate new credentials
2. **Set Pending**: Mark new version as pending
3. **Test Connection**: Validate new credentials work
4. **Finish**: Make new version current, mark old as previous

### 3. Encryption and Security

#### Encryption at Rest
- Uses AWS KMS for encryption
- Option to use AWS managed keys or customer managed keys
- Envelope encryption for enhanced security

#### Encryption in Transit
- All API calls use HTTPS/TLS
- SDK automatically encrypts data in transit

#### Access Control
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/MyRole"
      },
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:MySecret-abc123"
    }
  ]
}
```

---

## Security and Compliance

### IAM Integration

#### Key Permissions
- `secretsmanager:GetSecretValue` - Retrieve secret values
- `secretsmanager:CreateSecret` - Create new secrets
- `secretsmanager:UpdateSecret` - Update existing secrets
- `secretsmanager:DeleteSecret` - Delete secrets
- `secretsmanager:RotateSecret` - Initiate rotation
- `secretsmanager:DescribeSecret` - Get secret metadata

#### Resource-Based Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSpecificRole",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/DatabaseRole"
      },
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "secretsmanager:ResourceTag/Environment": "Production"
        }
      }
    }
  ]
}
```

### VPC Endpoints

#### Private Connectivity
- Access Secrets Manager from VPC without internet gateway
- Enhanced security by keeping traffic within AWS network
- Reduced data transfer costs

#### VPC Endpoint Policy Example
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "*"
    }
  ]
}
```

### Compliance Features

- **SOC 1, 2, 3** compliant
- **PCI DSS Level 1** compliant
- **HIPAA** eligible
- **FedRAMP** authorized
- **ISO 27001** certified
- **GDPR** compliant

---

## Integration with AWS Services

### 1. Amazon RDS Integration

#### Automatic Setup
- Secrets Manager can automatically manage RDS credentials
- Built-in rotation for master user credentials
- Zero-downtime rotation using clone user strategy

#### Configuration Example
```bash
# Create secret for RDS instance
aws secretsmanager create-secret \
    --name "rds-db-credentials/mydb" \
    --description "RDS MySQL credentials" \
    --secret-string '{"username":"admin","password":"MyPassword123!"}'

# Enable automatic rotation
aws secretsmanager rotate-secret \
    --secret-id "rds-db-credentials/mydb" \
    --rotation-lambda-arn "arn:aws:lambda:region:account:function:SecretsManagerRDSMySQLRotationSingleUser"
```

### 2. AWS Lambda Integration

#### Retrieving Secrets in Lambda
```python
import boto3
import json

def lambda_handler(event, context):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId='rds-db-credentials/mydb'
        )
    except ClientError as e:
        raise e
    
    secret = json.loads(get_secret_value_response['SecretString'])
    
    # Use the secret
    username = secret['username']
    password = secret['password']
    
    return {
        'statusCode': 200,
        'body': json.dumps('Secret retrieved successfully')
    }
```

### 3. Amazon ECS/EKS Integration

#### ECS Task Definition
```json
{
  "family": "my-app",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "my-container",
      "image": "my-app:latest",
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds-db-credentials/mydb-abc123:password::"
        }
      ]
    }
  ]
}
```

#### Kubernetes Secret Store CSI Driver
```yaml
apiVersion: v1
kind: SecretProviderClass
metadata:
  name: app-secrets
spec:
  provider: aws
  parameters:
    objects: |
      - objectName: "rds-db-credentials/mydb"
        objectType: "secretsmanager"
```

### 4. AWS CloudFormation Integration

#### Template Example
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MySecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: MyApplicationSecret
      Description: Secret for my application
      GenerateSecretString:
        SecretStringTemplate: '{"username": "admin"}'
        GenerateStringKey: 'password'
        PasswordLength: 32
        ExcludeCharacters: '"@/\'
        
  SecretRotation:
    Type: AWS::SecretsManager::RotationSchedule
    Properties:
      SecretId: !Ref MySecret
      RotationLambdaArn: !GetAtt RotationLambda.Arn
      RotationInterval: 30
```

---

## Pricing Model

### Cost Components

#### 1. Secret Storage
- **$0.40 per secret per month**
- Charged for each secret regardless of size (up to 64KB)
- Prorated for partial months

#### 2. API Calls
- **$0.05 per 10,000 API requests**
- Includes CreateSecret, GetSecretValue, UpdateSecret, etc.
- First 10,000 requests per month are free

#### 3. Rotation
- **No additional charges** for rotation using AWS Lambda
- Standard Lambda charges apply for custom rotation functions

### Cost Optimization Strategies

#### 1. Consolidate Secrets
```json
// Instead of multiple secrets
{
  "database_user": "admin",
  "database_password": "password123"
}

// Use single secret with multiple values
{
  "database": {
    "username": "admin",
    "password": "password123"
  },
  "api": {
    "key": "api_key_here",
    "secret": "api_secret_here"
  }
}
```

#### 2. Implement Caching
- Cache secrets in application memory
- Use reasonable TTL values (5-15 minutes)
- Implement cache refresh before expiration

#### 3. Optimize API Calls
- Batch secret retrieval when possible
- Use DescribeSecret for metadata only
- Implement proper error handling to avoid retry storms

---

## Common Use Cases

### 1. Database Connection Management

#### Scenario: Multi-tier Web Application
```python
import boto3
import pymysql
import json

class DatabaseManager:
    def __init__(self, secret_name, region='us-east-1'):
        self.secret_name = secret_name
        self.region = region
        self.client = boto3.client('secretsmanager', region_name=region)
        
    def get_connection(self):
        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secret = json.loads(response['SecretString'])
            
            connection = pymysql.connect(
                host=secret['host'],
                user=secret['username'],
                password=secret['password'],
                database=secret['dbname'],
                port=secret['port']
            )
            return connection
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
```

### 2. API Key Management

#### Scenario: Third-party Service Integration
```python
import requests
import boto3
import json

class ThirdPartyAPIClient:
    def __init__(self, secret_name):
        self.secret_name = secret_name
        self.secrets_client = boto3.client('secretsmanager')
        self._api_key = None
        
    def _get_api_key(self):
        if not self._api_key:
            response = self.secrets_client.get_secret_value(
                SecretId=self.secret_name
            )
            secret = json.loads(response['SecretString'])
            self._api_key = secret['api_key']
        return self._api_key
    
    def make_api_call(self, endpoint, data):
        headers = {
            'Authorization': f'Bearer {self._get_api_key()}',
            'Content-Type': 'application/json'
        }
        response = requests.post(endpoint, json=data, headers=headers)
        return response.json()
```

### 3. Cross-Region Disaster Recovery

#### Setup Cross-Region Replication
```bash
# Replicate secret to DR region
aws secretsmanager replicate-secret-to-regions \
    --secret-id "arn:aws:secretsmanager:us-east-1:123456789012:secret:MySecret-abc123" \
    --add-replica-regions Region=us-west-2,KmsKeyId=alias/aws/secretsmanager \
    --force-overwrite-replica-secret
```

### 4. Container Orchestration

#### Docker Compose with Secrets
```yaml
version: '3.8'
services:
  web:
    image: my-web-app
    environment:
      - AWS_REGION=us-east-1
      - SECRET_ARN=arn:aws:secretsmanager:us-east-1:123456789012:secret:app-secrets-abc123
    depends_on:
      - db
  
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    external: true
```

---

## Best Practices

### 1. Security Best Practices

#### Principle of Least Privilege
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:app/prod/database-*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        },
        "IpAddress": {
          "aws:SourceIp": "10.0.0.0/8"
        }
      }
    }
  ]
}
```

#### Use Customer Managed KMS Keys
```bash
# Create KMS key for Secrets Manager
aws kms create-key \
    --description "Secrets Manager encryption key" \
    --key-usage ENCRYPT_DECRYPT \
    --key-spec SYMMETRIC_DEFAULT

# Create alias
aws kms create-alias \
    --alias-name alias/secretsmanager-key \
    --target-key-id <key-id>
```

### 2. Rotation Best Practices

#### Implement Multi-User Rotation
```python
def multi_user_rotation_strategy():
    """
    Best practice for zero-downtime database rotation
    """
    # Step 1: Create clone user with same permissions
    # Step 2: Update secret with clone user credentials
    # Step 3: Test clone user access
    # Step 4: Drop original user
    # Step 5: Rename clone user to original name
    pass
```

#### Rotation Schedule Considerations
- **High-security environments**: Weekly rotation
- **Standard environments**: Monthly rotation
- **Low-risk environments**: Quarterly rotation
- **Compliance requirements**: Follow industry standards (PCI-DSS: 90 days)

### 3. Application Integration Best Practices

#### Implement Secret Caching
```python
import time
from threading import Lock

class SecretCache:
    def __init__(self, ttl_seconds=300):  # 5 minutes default
        self.cache = {}
        self.ttl = ttl_seconds
        self.lock = Lock()
        
    def get_secret(self, secret_name):
        with self.lock:
            now = time.time()
            if (secret_name in self.cache and 
                now - self.cache[secret_name]['timestamp'] < self.ttl):
                return self.cache[secret_name]['value']
            
            # Fetch from Secrets Manager
            client = boto3.client('secretsmanager')
            response = client.get_secret_value(SecretId=secret_name)
            
            self.cache[secret_name] = {
                'value': response['SecretString'],
                'timestamp': now
            }
            
            return response['SecretString']
```

#### Handle Rotation Gracefully
```python
def get_secret_with_fallback(secret_name):
    """
    Handle secret rotation by trying current version first,
    then falling back to previous version
    """
    client = boto3.client('secretsmanager')
    
    try:
        # Try current version
        response = client.get_secret_value(
            SecretId=secret_name,
            VersionStage='AWSCURRENT'
        )
        return json.loads(response['SecretString'])
    except Exception:
        try:
            # Fallback to previous version
            response = client.get_secret_value(
                SecretId=secret_name,
                VersionStage='AWSPENDING'
            )
            return json.loads(response['SecretString'])
        except Exception as e:
            raise Exception(f"Failed to retrieve secret: {e}")
```

### 4. Monitoring and Alerting

#### CloudWatch Metrics
- `SecretsManagerSuccessfulRequests`
- `SecretsManagerClientErrors`
- `SecretsManagerServerErrors`
- `SecretsManagerRotationSuccessful`
- `SecretsManagerRotationFailed`

#### CloudWatch Alarms
```json
{
  "AlarmName": "SecretsManager-RotationFailure",
  "ComparisonOperator": "GreaterThanThreshold",
  "EvaluationPeriods": 1,
  "MetricName": "RotationFailed",
  "Namespace": "AWS/SecretsManager",
  "Period": 300,
  "Statistic": "Sum",
  "Threshold": 0,
  "ActionsEnabled": true,
  "AlarmActions": [
    "arn:aws:sns:us-east-1:123456789012:secrets-manager-alerts"
  ]
}
```

---

## Exam Tips and Common Scenarios

### SAA-C03 Exam Focus Areas

#### 1. When to Use Secrets Manager vs. Other Services

**Use Secrets Manager when:**
- Need automatic rotation of secrets
- Storing database credentials
- Require fine-grained access control
- Need cross-region replication
- Compliance requirements for secret management

**Use Parameter Store when:**
- Storing configuration values (non-secret)
- Need hierarchical organization
- Cost is a primary concern
- Simple string values without rotation

**Use Systems Manager Session Manager when:**
- Need secure shell access to EC2 instances
- Want to eliminate SSH keys
- Require session logging and auditing

#### 2. Common Exam Scenarios

##### Scenario 1: Database Credential Rotation
**Question**: "A company needs to automatically rotate RDS database passwords every 30 days for compliance. What's the most efficient solution?"

**Answer**: Use AWS Secrets Manager with automatic rotation enabled. Configure a 30-day rotation schedule using the built-in RDS rotation Lambda function.

##### Scenario 2: Container Secret Management
**Question**: "An application running on ECS needs to access database credentials without hardcoding them in the container image. How should this be implemented?"

**Answer**: Store credentials in Secrets Manager and reference them in the ECS task definition using the `secrets` parameter. The ECS agent will retrieve the secrets at runtime.

##### Scenario 3: Cross-Region Disaster Recovery
**Question**: "A multi-region application needs access to the same secrets in both primary and DR regions. What's the best approach?"

**Answer**: Use Secrets Manager cross-region replication to automatically replicate secrets to the DR region. This ensures consistency and availability during failover.

##### Scenario 4: Cost Optimization
**Question**: "A startup wants to manage secrets cost-effectively while maintaining security. They have 50 different secrets. What's the recommendation?"

**Answer**: Consolidate related secrets into fewer secret objects (each can contain multiple key-value pairs up to 64KB). Implement client-side caching to reduce API calls.

### Key Exam Points to Remember

1. **Automatic Rotation**: Built-in support for RDS, DocumentDB, Redshift
2. **Encryption**: Always encrypted at rest (KMS) and in transit (TLS)
3. **Cross-Region**: Supports replication for disaster recovery
4. **Integration**: Native integration with RDS, ECS, Lambda, CloudFormation
5. **Pricing**: $0.40/secret/month + $0.05/10K API calls
6. **VPC Endpoints**: Support for private connectivity
7. **IAM**: Fine-grained access control with resource-based policies
8. **Versioning**: Automatic versioning with each update
9. **CloudTrail**: All API calls are logged for auditing
10. **Compliance**: Meets various compliance standards (SOC, PCI-DSS, HIPAA)

### Common Mistakes to Avoid

1. **Over-segmentation**: Creating too many individual secrets instead of consolidating
2. **Ignoring Caching**: Making unnecessary API calls without client-side caching
3. **Wrong Service Choice**: Using Secrets Manager for non-secret configuration data
4. **Insufficient IAM**: Not implementing principle of least privilege
5. **Missing Rotation**: Not enabling automatic rotation for supported services
6. **Region Mismatch**: Not considering cross-region requirements upfront
7. **Cost Ignorance**: Not understanding the pricing model implications
8. **No Monitoring**: Failing to set up proper monitoring and alerting

---

## Hands-on Examples

### Example 1: Complete RDS Integration Setup

#### Step 1: Create RDS Instance with Secrets Manager
```bash
# Create the secret first
aws secretsmanager create-secret \
    --name "rds/mysql/credentials" \
    --description "RDS MySQL master credentials" \
    --generate-secret-string '{
        "SecretStringTemplate":"{\"username\": \"admin\"}",
        "GenerateStringKey": "password",
        "PasswordLength": 32,
        "ExcludeCharacters": "\"@/\\"
    }'

# Get the secret ARN
SECRET_ARN=$(aws secretsmanager describe-secret \
    --secret-id "rds/mysql/credentials" \
    --query "ARN" --output text)

# Create RDS instance using the secret
aws rds create-db-instance \
    --db-instance-identifier mydb \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username admin \
    --manage-master-user-password \
    --master-user-secret-kms-key-id alias/aws/secretsmanager \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-12345678
```

#### Step 2: Enable Automatic Rotation
```bash
# Create rotation Lambda function (using AWS-provided template)
aws lambda create-function \
    --function-name SecretsManagerRDSMySQLRotationSingleUser \
    --runtime python3.9 \
    --role arn:aws:iam::123456789012:role/SecretsManagerRotationRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://rotation-function.zip

# Enable rotation
aws secretsmanager rotate-secret \
    --secret-id "rds/mysql/credentials" \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSMySQLRotationSingleUser \
    --rotation-rules AutomaticallyAfterDays=30
```

### Example 2: Lambda Function with Error Handling
```python
import boto3
import json
import pymysql
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DatabaseConnection:
    def __init__(self, secret_name, region_name='us-east-1'):
        self.secret_name = secret_name
        self.region_name = region_name
        self.connection = None
        
    def get_secret(self):
        """Retrieve secret from AWS Secrets Manager"""
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )
        
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            logger.error(f"Error retrieving secret: {e}")
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise e
        else:
            secret = json.loads(get_secret_value_response['SecretString'])
            return secret
    
    def connect(self):
        """Establish database connection using secrets"""
        secret = self.get_secret()
        
        try:
            self.connection = pymysql.connect(
                host=secret['host'],
                user=secret['username'],
                password=secret['password'],
                database=secret.get('dbname', 'mysql'),
                port=secret.get('port', 3306),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=60,
                read_timeout=60,
                write_timeout=60
            )
            logger.info("Database connection established successfully")
            return self.connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

def lambda_handler(event, context):
    """Lambda function handler"""
    db = DatabaseConnection('rds/mysql/credentials')
    
    try:
        # Connect to database
        connection = db.connect()
        
        # Perform database operations
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"Database version: {version}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Database operation successful',
                'version': version
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
    finally:
        if db.connection:
            db.connection.close()
            logger.info("Database connection closed")
```

### Example 3: ECS Task with Secrets Manager Integration
```json
{
  "family": "web-app-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "web-app",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DB_HOST",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds/mysql/credentials-abc123:host::"
        },
        {
          "name": "DB_USERNAME",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds/mysql/credentials-abc123:username::"
        },
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds/mysql/credentials-abc123:password::"
        },
        {
          "name": "API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:api/credentials-def456:api_key::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/web-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "essential": true
    }
  ]
}
```

### Example 4: CloudFormation Template for Complete Setup
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Complete Secrets Manager setup with RDS and Lambda'

Parameters:
  Environment:
    Type: String
    Default: 'production'
    AllowedValues: ['development', 'staging', 'production']
  
  DBInstanceClass:
    Type: String
    Default: 'db.t3.micro'
    
Resources:
  # KMS Key for encryption
  SecretsManagerKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: 'KMS Key for Secrets Manager encryption'
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Effect: Allow
            Principal:
              Service: secretsmanager.amazonaws.com
            Action:
              - 'kms:Decrypt'
              - 'kms:GenerateDataKey'
            Resource: '*'

  SecretsManagerKMSKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub 'alias/secretsmanager-${Environment}'
      TargetKeyId: !Ref SecretsManagerKMSKey

  # Database credentials secret
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub 'rds/${Environment}/mysql-credentials'
      Description: 'RDS MySQL credentials for application'
      KmsKeyId: !Ref SecretsManagerKMSKey
      GenerateSecretString:
        SecretStringTemplate: '{"username": "admin"}'
        GenerateStringKey: 'password'
        PasswordLength: 32
        ExcludeCharacters: '"@/\'
        RequireEachIncludedType: true
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Application
          Value: WebApp

  # RDS Subnet Group
  DatabaseSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: 'Subnet group for RDS database'
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      Tags:
        - Key: Name
          Value: !Sub 'db-subnet-group-${Environment}'

  # RDS Instance
  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub 'mysql-${Environment}'
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: '8.0.35'
      AllocatedStorage: '20'
      StorageType: gp2
      StorageEncrypted: true
      MasterUsername: !Sub '{{resolve:secretsmanager:${DatabaseSecret}:SecretString:username}}'
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${DatabaseSecret}:SecretString:password}}'
      DBSubnetGroupName: !Ref DatabaseSubnetGroup
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      BackupRetentionPeriod: 7
      MultiAZ: !If [IsProduction, true, false]
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Lambda execution role for rotation
  RotationLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        - 'arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole'
      Policies:
        - PolicyName: SecretsManagerRotationPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - 'secretsmanager:DescribeSecret'
                  - 'secretsmanager:GetSecretValue'
                  - 'secretsmanager:PutSecretValue'
                  - 'secretsmanager:UpdateSecretVersionStage'
                Resource: !Ref DatabaseSecret
              - Effect: Allow
                Action:
                  - 'kms:Decrypt'
                  - 'kms:GenerateDataKey'
                Resource: !GetAtt SecretsManagerKMSKey.Arn

  # Secret rotation schedule
  SecretRotationSchedule:
    Type: AWS::SecretsManager::RotationSchedule
    DependsOn: DatabaseInstance
    Properties:
      SecretId: !Ref DatabaseSecret
      RotationLambdaArn: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:SecretsManagerRDSMySQLRotationSingleUser'
      RotationInterval: 30
      RotationImmediate: false

  # API Gateway secret for external services
  ApiSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub 'api/${Environment}/external-service'
      Description: 'API keys for external service integration'
      KmsKeyId: !Ref SecretsManagerKMSKey
      SecretString: !Sub |
        {
          "api_key": "your-api-key-here",
          "api_secret": "your-api-secret-here",
          "webhook_url": "https://api.example.com/webhook",
          "environment": "${Environment}"
        }

Conditions:
  IsProduction: !Equals [!Ref Environment, 'production']

Outputs:
  DatabaseSecretArn:
    Description: 'ARN of the database secret'
    Value: !Ref DatabaseSecret
    Export:
      Name: !Sub '${AWS::StackName}-DatabaseSecretArn'
      
  ApiSecretArn:
    Description: 'ARN of the API secret'
    Value: !Ref ApiSecret
    Export:
      Name: !Sub '${AWS::StackName}-ApiSecretArn'
      
  KMSKeyArn:
    Description: 'ARN of the KMS key used for encryption'
    Value: !GetAtt SecretsManagerKMSKey.Arn
    Export:
      Name: !Sub '${AWS::StackName}-KMSKeyArn'
```

---

## AWS CLI Commands Reference

### Creating Secrets

#### Create Basic Secrets
```bash
# Create a simple secret with a string value
aws secretsmanager create-secret \
  --name MyApplicationSecret \
  --description "Secret for my application" \
  --secret-string "MySecretValue123!"

# Create a secret with JSON structure
aws secretsmanager create-secret \
  --name prod/db/credentials \
  --description "Production database credentials" \
  --secret-string '{"username":"admin","password":"MyP@ssw0rd!","engine":"mysql","host":"mydb.cluster-abc123.us-east-1.rds.amazonaws.com","port":3306,"dbname":"production"}'

# Create a secret from a JSON file
cat > db-secret.json <<EOF
{
  "username": "admin",
  "password": "SecurePassword123!",
  "engine": "postgres",
  "host": "mydb.abc123.us-east-1.rds.amazonaws.com",
  "port": 5432,
  "dbClusterIdentifier": "my-db-cluster"
}
EOF

aws secretsmanager create-secret \
  --name prod/postgres/master \
  --description "Production PostgreSQL master credentials" \
  --secret-string file://db-secret.json

# Create a secret with tags
aws secretsmanager create-secret \
  --name prod/api/key \
  --description "Production API key" \
  --secret-string "api-key-12345" \
  --tags Key=Environment,Value=Production Key=Application,Value=WebAPI Key=CostCenter,Value=Engineering

# Create a secret with KMS encryption
aws secretsmanager create-secret \
  --name sensitive/data \
  --description "Highly sensitive data" \
  --secret-string "VerySecretData" \
  --kms-key-id alias/my-custom-key
```

#### Create Secrets for Different Services
```bash
# RDS MySQL database secret
aws secretsmanager create-secret \
  --name prod/rds/mysql/admin \
  --description "RDS MySQL admin credentials" \
  --secret-string '{"username":"admin","password":"MyDBPassword123!","engine":"mysql","host":"mydb.cluster-abc123.us-east-1.rds.amazonaws.com","port":3306,"dbInstanceIdentifier":"mydb-instance"}'

# DocumentDB secret
aws secretsmanager create-secret \
  --name prod/docdb/credentials \
  --description "DocumentDB credentials" \
  --secret-string '{"username":"docdbadmin","password":"DocDBPass123!","engine":"docdb","host":"docdb-cluster.cluster-abc123.us-east-1.docdb.amazonaws.com","port":27017}'

# Redshift secret
aws secretsmanager create-secret \
  --name prod/redshift/admin \
  --description "Redshift admin credentials" \
  --secret-string '{"username":"redshiftadmin","password":"RedshiftPass123!","host":"redshift-cluster.abc123.us-east-1.redshift.amazonaws.com","port":5439,"dbname":"analytics"}'

# API key secret
aws secretsmanager create-secret \
  --name prod/external/stripe-api-key \
  --description "Stripe API key for payment processing" \
  --secret-string '{"api_key":"sk_live_abc123xyz789","publishable_key":"pk_live_def456uvw012"}'
```

### Retrieving Secret Values

#### Get Secret Values
```bash
# Get the current secret value
aws secretsmanager get-secret-value \
  --secret-id MyApplicationSecret

# Get secret value and extract just the secret string
aws secretsmanager get-secret-value \
  --secret-id prod/db/credentials \
  --query SecretString \
  --output text

# Parse JSON secret and extract specific field
aws secretsmanager get-secret-value \
  --secret-id prod/db/credentials \
  --query SecretString \
  --output text | jq -r '.password'

# Get a specific version of a secret
aws secretsmanager get-secret-value \
  --secret-id MyApplicationSecret \
  --version-id a1b2c3d4-5678-90ab-cdef-1234567890ab

# Get secret value by version stage
aws secretsmanager get-secret-value \
  --secret-id MyApplicationSecret \
  --version-stage AWSPREVIOUS

# Get random password generated by Secrets Manager
aws secretsmanager get-random-password \
  --password-length 32 \
  --exclude-characters "/@\"'"

# Get random password with specific requirements
aws secretsmanager get-random-password \
  --password-length 24 \
  --require-each-included-type \
  --exclude-characters "O0Il1|" \
  --exclude-punctuation
```

### Updating Secrets

#### Update Secret Values
```bash
# Update a secret's value (creates new version)
aws secretsmanager update-secret \
  --secret-id MyApplicationSecret \
  --secret-string "NewSecretValue456!"

# Update a JSON secret
aws secretsmanager update-secret \
  --secret-id prod/db/credentials \
  --secret-string '{"username":"admin","password":"NewP@ssw0rd!","engine":"mysql","host":"mydb.cluster-abc123.us-east-1.rds.amazonaws.com","port":3306}'

# Update secret from a file
aws secretsmanager update-secret \
  --secret-id prod/api/config \
  --secret-string file://new-config.json

# Update secret description
aws secretsmanager update-secret \
  --secret-id MyApplicationSecret \
  --description "Updated description for my application secret"

# Update secret's KMS key
aws secretsmanager update-secret \
  --secret-id MyApplicationSecret \
  --kms-key-id alias/new-encryption-key

# Put a new secret value with client request token (idempotent)
aws secretsmanager put-secret-value \
  --secret-id MyApplicationSecret \
  --secret-string "NewValue" \
  --client-request-token "unique-token-12345"
```

### Secret Rotation

#### Configure and Manage Rotation
```bash
# Enable automatic rotation with a Lambda function
aws secretsmanager rotate-secret \
  --secret-id prod/rds/mysql/admin \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation \
  --rotation-rules AutomaticallyAfterDays=30

# Rotate a secret immediately
aws secretsmanager rotate-secret \
  --secret-id MyApplicationSecret

# Update rotation configuration
aws secretsmanager rotate-secret \
  --secret-id prod/db/credentials \
  --rotation-rules '{"AutomaticallyAfterDays":60,"Duration":"2h","ScheduleExpression":"cron(0 2 1 * ? *)"}'

# Cancel rotation in progress
aws secretsmanager cancel-rotate-secret \
  --secret-id MyApplicationSecret \
  --version-id a1b2c3d4-5678-90ab-cdef-1234567890ab
```

#### Set Up Rotation for RDS
```bash
# Create RDS MySQL rotation configuration
aws secretsmanager rotate-secret \
  --secret-id prod/rds/mysql/admin \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSMySQLRotation \
  --rotation-rules AutomaticallyAfterDays=30

# Create rotation for RDS PostgreSQL
aws secretsmanager rotate-secret \
  --secret-id prod/rds/postgres/admin \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSPostgreSQLRotation \
  --rotation-rules '{"AutomaticallyAfterDays":90,"Duration":"3h"}'

# Rotation with alternating users strategy
cat > rotation-config.json <<EOF
{
  "AutomaticallyAfterDays": 30,
  "Duration": "2h",
  "RotationType": "AlternatingUsers"
}
EOF

aws secretsmanager rotate-secret \
  --secret-id prod/db/credentials \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:MyRotationFunction \
  --rotation-rules file://rotation-config.json
```

### Deleting and Restoring Secrets

#### Delete Secrets
```bash
# Schedule secret deletion with recovery window (7-30 days)
aws secretsmanager delete-secret \
  --secret-id MyApplicationSecret \
  --recovery-window-in-days 30

# Delete secret immediately (no recovery - use with caution)
aws secretsmanager delete-secret \
  --secret-id old-unused-secret \
  --force-delete-without-recovery

# Restore a deleted secret
aws secretsmanager restore-secret \
  --secret-id MyApplicationSecret

# Check if a secret is scheduled for deletion
aws secretsmanager describe-secret \
  --secret-id MyApplicationSecret \
  --query 'DeletedDate'
```

### Tagging Secrets

#### Manage Secret Tags
```bash
# Add tags to an existing secret
aws secretsmanager tag-resource \
  --secret-id MyApplicationSecret \
  --tags Key=Environment,Value=Production Key=Owner,Value=DevOps Key=Compliance,Value=PCI-DSS

# List tags for a secret
aws secretsmanager describe-secret \
  --secret-id MyApplicationSecret \
  --query Tags

# Remove tags from a secret
aws secretsmanager untag-resource \
  --secret-id MyApplicationSecret \
  --tag-keys Environment Owner
```

### Listing and Describing Secrets

#### Query Secrets
```bash
# List all secrets
aws secretsmanager list-secrets

# List secrets with specific tag
aws secretsmanager list-secrets \
  --filters Key=tag-key,Values=Environment Key=tag-value,Values=Production

# List secrets by name pattern
aws secretsmanager list-secrets \
  --filters Key=name,Values=prod/*

# Describe a specific secret (metadata only)
aws secretsmanager describe-secret \
  --secret-id MyApplicationSecret

# List all versions of a secret
aws secretsmanager list-secret-version-ids \
  --secret-id MyApplicationSecret

# Get secrets with pagination
aws secretsmanager list-secrets \
  --max-results 10

# List secrets modified after a specific date
aws secretsmanager list-secrets \
  --query "SecretList[?LastChangedDate>'2024-01-01']"
```

### Resource Policies

#### Manage Secret Resource Policies
```bash
# Create a resource policy for cross-account access
cat > secret-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:root"
      },
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/MyApplicationRole"
      },
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:ListSecretVersionIds"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "secretsmanager:VersionStage": "AWSCURRENT"
        }
      }
    }
  ]
}
EOF

# Attach resource policy to secret
aws secretsmanager put-resource-policy \
  --secret-id MyApplicationSecret \
  --resource-policy file://secret-policy.json

# Get the resource policy for a secret
aws secretsmanager get-resource-policy \
  --secret-id MyApplicationSecret

# Delete resource policy
aws secretsmanager delete-resource-policy \
  --secret-id MyApplicationSecret

# Validate resource policy
aws secretsmanager validate-resource-policy \
  --resource-policy file://secret-policy.json
```

### Secret Replication

#### Replicate Secrets Across Regions
```bash
# Replicate secret to another region
aws secretsmanager replicate-secret-to-regions \
  --secret-id MyApplicationSecret \
  --add-replica-regions Region=eu-west-1,KmsKeyId=alias/my-key-eu

# Replicate to multiple regions
aws secretsmanager replicate-secret-to-regions \
  --secret-id prod/db/credentials \
  --add-replica-regions \
    Region=eu-west-1,KmsKeyId=arn:aws:kms:eu-west-1:123456789012:key/abc123 \
    Region=ap-southeast-1,KmsKeyId=alias/my-key-asia

# Update replication configuration
aws secretsmanager replicate-secret-to-regions \
  --secret-id MyApplicationSecret \
  --add-replica-regions Region=us-west-2 \
  --force-overwrite-replica-secret

# Remove replication from regions
aws secretsmanager remove-regions-from-replication \
  --secret-id MyApplicationSecret \
  --remove-replica-regions eu-west-1 ap-southeast-1

# Stop replication and promote replica to standalone
aws secretsmanager stop-replication-to-replica \
  --secret-id MyApplicationSecret
```

### Batch Operations

#### Perform Batch Secret Operations
```bash
# Create multiple secrets from a CSV file
while IFS=, read -r name value description; do
  aws secretsmanager create-secret \
    --name "$name" \
    --description "$description" \
    --secret-string "$value"
done < secrets.csv

# Rotate all secrets with a specific tag
for secret in $(aws secretsmanager list-secrets \
  --filters Key=tag-key,Values=AutoRotate \
  --query 'SecretList[].Name' \
  --output text); do
  echo "Rotating secret: $secret"
  aws secretsmanager rotate-secret --secret-id "$secret"
done

# Export all secret names and descriptions
aws secretsmanager list-secrets \
  --query 'SecretList[].[Name,Description]' \
  --output table

# Backup secret metadata to JSON
aws secretsmanager list-secrets \
  --output json > secrets-backup.json
```

### Integration with Other Services

#### Use Secrets in ECS Task Definitions
```bash
# Reference secret in ECS task definition
cat > task-definition.json <<EOF
{
  "family": "my-app",
  "containerDefinitions": [
    {
      "name": "my-container",
      "image": "my-app:latest",
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/db/credentials:password::"
        },
        {
          "name": "API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/api/key::"
        }
      ]
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### Use Secrets in Lambda Environment Variables
```bash
# Create Lambda function with secret reference (using extension)
aws lambda create-function \
  --function-name my-function \
  --runtime python3.9 \
  --role arn:aws:iam::123456789012:role/lambda-role \
  --handler index.handler \
  --zip-file fileb://function.zip \
  --environment Variables="{SECRET_ARN=arn:aws:secretsmanager:us-east-1:123456789012:secret:MySecret}"

# Update Lambda to use Secrets Manager extension layer
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4
```

### Monitoring and Auditing

#### Monitor Secret Usage
```bash
# Get CloudTrail events for secret access
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=MyApplicationSecret \
  --max-results 10

# Create CloudWatch alarm for secret retrieval
aws cloudwatch put-metric-alarm \
  --alarm-name secrets-manager-high-retrieval \
  --alarm-description "Alert on high secret retrievals" \
  --metric-name SecretsManagerGetSecretValue \
  --namespace AWS/SecretsManager \
  --statistic Sum \
  --period 300 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Enable CloudWatch logging for rotation
aws secretsmanager update-secret \
  --secret-id MyApplicationSecret \
  --description "Secret with CloudWatch logging enabled"
```

---

## Comparison with Other Services

### AWS Secrets Manager vs. AWS Systems Manager Parameter Store

| Feature | Secrets Manager | Parameter Store |
|---------|-----------------|-----------------|
| **Primary Use Case** | Secrets (passwords, keys) | Configuration data |
| **Automatic Rotation** | ✅ Built-in support | ❌ No native support |
| **Encryption** | Always encrypted | Optional encryption |
| **Pricing** | $0.40/secret/month | Free tier available |
| **Size Limit** | 64 KB per secret | 4 KB (Standard), 8 KB (Advanced) |
| **Versioning** | Automatic | Manual |
| **Cross-Region Replication** | ✅ Native support | ❌ Manual setup required |
| **Fine-grained IAM** | ✅ Resource-based policies | ✅ Resource-based policies |
| **API Rate Limits** | 5,000 requests/second | 1,000 requests/second (Standard) |

### When to Choose Each Service

#### Choose Secrets Manager when:
- Managing database credentials that need rotation
- Storing API keys for third-party services
- Need cross-region disaster recovery
- Compliance requires secret rotation
- Working with containerized applications (ECS/EKS)

#### Choose Parameter Store when:
- Storing application configuration
- Managing environment variables
- Need hierarchical organization (/app/env/config)
- Cost optimization is critical
- Simple key-value storage without rotation

#### Choose Both when:
- Use Parameter Store for configuration data
- Use Secrets Manager for sensitive credentials
- Reference Secrets Manager ARNs in Parameter Store for indirection

### AWS Secrets Manager vs. HashiCorp Vault

| Feature | AWS Secrets Manager | HashiCorp Vault |
|---------|-------------------|-----------------|
| **Deployment** | Fully managed | Self-managed or Cloud |
| **Integration** | Native AWS integration | Multi-cloud support |
| **Rotation** | Built-in for AWS services | Extensive plugin ecosystem |
| **High Availability** | Managed by AWS | Configure yourself |
| **Compliance** | AWS compliance inheritance | Custom compliance setup |
| **Learning Curve** | Low (AWS native) | Moderate to High |
| **Cost Model** | Pay-per-use | License + Infrastructure |
| **Secret Engines** | Limited types | Extensive variety |

---

## Summary

AWS Secrets Manager is a critical service for the SAA-C03 exam, focusing on secure secret storage, automatic rotation, and integration with other AWS services. Key exam points include:

1. **Automatic rotation** capabilities for RDS and other AWS services
2. **Integration patterns** with ECS, Lambda, and CloudFormation  
3. **Security features** including encryption and IAM integration
4. **Cost considerations** and optimization strategies
5. **Comparison** with Parameter Store and when to use each
6. **Cross-region replication** for disaster recovery scenarios
7. **Best practices** for implementation and monitoring

Remember that Secrets Manager is designed specifically for sensitive data that requires rotation, while Parameter Store is better suited for configuration data. Understanding when to use each service and how they integrate with other AWS services is crucial for the exam and real-world implementations.

The service's tight integration with AWS services, automatic rotation capabilities, and security features make it an essential component of well-architected applications on AWS.