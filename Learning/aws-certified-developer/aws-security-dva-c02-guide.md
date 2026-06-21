# AWS Security for Developers — DVA-C02 Guide

Cognito, IAM, KMS, Secrets Manager, and STS — from an **application developer** perspective.

---

## Amazon Cognito

### User Pools vs Identity Pools

| | User Pools | Identity Pools |
|--|-----------|----------------|
| **Purpose** | User directory (auth) | Federated AWS credentials |
| **Provides** | JWT tokens | Temporary AWS credentials via STS |
| **Sign-up/sign-in** | Yes | No (uses external identity) |
| **Social login** | Yes (Google, Facebook, etc.) | Via User Pool or directly |
| **API Gateway integration** | Cognito authorizer | IAM auth with temp credentials |
| **Use case** | Authenticate users to your app | Grant S3/DynamoDB access from mobile |

### Typical Architecture

```
Mobile/Web App
    │
    ├── Sign in → Cognito User Pool → JWT tokens
    │                                      │
    │                                      ▼
    │                              API Gateway (Cognito authorizer) → Lambda
    │
    └── Get AWS creds → Cognito Identity Pool → STS → Temp credentials → S3 upload
```

### JWT Tokens

| Token | Purpose | Lifetime |
|-------|---------|----------|
| **ID token** | User identity claims (profile) | 1 hour (default) |
| **Access token** | Authorize API access | 1 hour |
| **Refresh token** | Get new ID/access tokens | 30 days (default) |

### Lambda Access to Claims

```python
claims = event['requestContext']['authorizer']['claims']
user_id = claims['sub']
email = claims.get('email')
groups = claims.get('cognito:groups', '').split(',')
```

---

## IAM for Developers

### Execution Roles (Not Users)

| Compute | Role type |
|---------|-----------|
| Lambda | Execution role |
| EC2 | Instance profile role |
| ECS/Fargate | Task role |
| API Gateway | Execution role (for AWS service integration) |

### Resource-Based Policies

Services that support resource policies (grant access TO the resource):
- Lambda, S3, SNS, SQS, KMS, Secrets Manager

**Cross-service example:** S3 bucket policy allowing Lambda execution role to read objects.

### STS Operations (Developer-Relevant)

| Operation | Use case |
|-----------|----------|
| `AssumeRole` | Cross-account, elevated temp access |
| `AssumeRoleWithWebIdentity` | Mobile/web federated login |
| `GetSessionToken` | MFA-protected API access |
| `GetCallerIdentity` | Debug which identity is active |

---

## AWS KMS

### Encryption for Developers

```python
# Encrypt data
encrypted = kms.encrypt(KeyId='alias/app-key', Plaintext=b'secret')['CiphertextBlob']

# Decrypt
plaintext = kms.decrypt(CiphertextBlob=encrypted)['Plaintext']

# S3 with KMS
s3.put_object(Bucket='b', Key='f', Body=data,
    ServerSideEncryption='aws:kms', SSEKMSKeyId='alias/app-key')

# DynamoDB with CMK — set at table level in console/IaC
```

### Key Types

| Type | Control | Rotation | Cost |
|------|---------|----------|------|
| AWS owned | AWS | Automatic | Free |
| AWS managed | AWS (per service) | Automatic annual | Free |
| Customer managed (CMK) | You (key policy) | Optional automatic | $1/month + API calls |

### Lambda Environment Variable Encryption

Enable KMS key on function — env vars encrypted at rest, decrypted at runtime.

---

## AWS Secrets Manager

```python
import boto3, json

# Cache outside handler
_secret_cache = None

def get_db_credentials():
    global _secret_cache
    if _secret_cache is None:
        client = boto3.client('secretsmanager')
        resp = client.get_secret_value(SecretId='prod/database')
        _secret_cache = json.loads(resp['SecretString'])
    return _secret_cache
```

**Automatic rotation:** Lambda function rotates secret on schedule (e.g., every 30 days) — no application code change if using standard rotation templates.

**vs Parameter Store SecureString:**

| | Secrets Manager | SSM SecureString |
|--|----------------|-----------------|
| Auto rotation | Yes | No |
| Cost | ~$0.40/secret/month | Free |
| Cross-region replication | Yes | No |

> **Exam default:** Secrets Manager for credentials needing rotation; Parameter Store for config values.

---

## Encryption Summary

| Data location | At rest | In transit |
|--------------|---------|------------|
| S3 | SSE-S3, SSE-KMS, SSE-C | HTTPS (enforce with bucket policy) |
| DynamoDB | AWS owned, AWS managed, CMK | HTTPS |
| Lambda env vars | KMS encryption | N/A |
| Secrets Manager | KMS (automatic) | HTTPS |
| API Gateway | N/A | TLS (ACM certificate) |

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| User sign-up for mobile app | Cognito User Pool |
| Mobile app uploads to S3 directly | Cognito Identity Pool + IAM role |
| API validates user JWT | Cognito User Pool authorizer on API Gateway |
| Database password auto-rotation | Secrets Manager |
| Encrypt Lambda environment variables | KMS key on function |
| Audit KMS key usage | CloudTrail |
| Cross-account encrypted S3 access | KMS key policy + bucket policy |
| Temporary cross-account access in code | STS AssumeRole |

---

## Related Guides

- [Domain 2 — Security](domain-02-security.md)
- [API Gateway Guide](aws-api-gateway-dva-c02-guide.md)
