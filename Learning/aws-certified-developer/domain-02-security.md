# Domain 2: Security (26%) — DVA-C02

Maps to **Task 2.1** (authentication/authorization), **Task 2.2** (encryption), and **Task 2.3** (sensitive data in code).

See [Security Guide](aws-security-dva-c02-guide.md) for full service coverage.

---

## Task 2.1: Authentication and Authorization

### Skill 2.1.1 — Federated Access (Cognito, IAM)

| Need | Solution |
|------|----------|
| User sign-up/sign-in for web/mobile app | **Cognito User Pool** |
| Exchange identity for AWS credentials | **Cognito Identity Pool** |
| Enterprise SSO (SAML) | Cognito User Pool + SAML IdP, or IAM Identity Center |
| Server-to-server AWS access | **IAM role** (never IAM user keys in code) |
| Cross-account access | STS `AssumeRole` |

### Skill 2.1.2 — Bearer Tokens

- Cognito User Pool returns **JWT tokens** (ID, Access, Refresh)
- Client sends `Authorization: Bearer <access_token>` to API Gateway
- API Gateway Cognito authorizer validates JWT signature and expiry
- Lambda receives claims in `event.requestContext.authorizer.claims`

### Skill 2.1.3–2.1.4 — Programmatic Access

```python
# Lambda uses execution role automatically — no keys needed
# EC2/ECS uses instance/task role via metadata service

# Explicit assume role (cross-account)
sts = boto3.client('sts')
creds = sts.assume_role(
    RoleArn='arn:aws:iam::ACCOUNT:role/AppRole',
    RoleSessionName='app-session'
)['Credentials']
```

### Skill 2.1.5 — Assume IAM Role

Trust policy defines **who** can assume; permissions policy defines **what** they can do.

### Skill 2.1.6 — IAM Permissions for Applications

**Least privilege execution role example for Lambda reading DynamoDB:**

```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem",
    "dynamodb:Query"
  ],
  "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/Orders"
}
```

### Skill 2.1.7 — Application-Level Authorization

Fine-grained access beyond IAM — implement in Lambda:

```python
def lambda_handler(event, context):
    claims = event['requestContext']['authorizer']['claims']
    user_role = claims.get('custom:role', 'user')
    
    if user_role != 'admin' and event['httpMethod'] == 'DELETE':
        return {'statusCode': 403, 'body': 'Forbidden'}
```

Also: **Cognito groups**, **custom attributes**, **resource-based policies** (S3 bucket policy per user prefix).

### Skill 2.1.8 — Cross-Service Auth in Microservices

- Each microservice has its own **IAM role**
- Service A calls Service B via **IAM auth on API Gateway** (SigV4 signing)
- Or use **Cognito tokens** passed through; validate at each service
- **Resource-based policies** on Lambda allow specific services to invoke

---

## Task 2.2: Encryption

### Skill 2.2.1 — Encryption at Rest vs In Transit

| | At Rest | In Transit |
|--|---------|------------|
| **What** | Data stored on disk | Data moving over network |
| **How** | SSE-S3, SSE-KMS, SSE-C, client-side | TLS/HTTPS |
| **Developer action** | Set encryption params on upload/create | Use HTTPS endpoints; enforce in IAM |

### Skill 2.2.3 — Client-Side vs Server-Side

| | Client-side | Server-side |
|--|------------|-------------|
| **Encrypt where** | Before sending to AWS | At AWS storage layer |
| **Key management** | You manage entirely | AWS or KMS manages |
| **Use when** | Maximum control; zero-trust | Standard cloud encryption |

### Skill 2.2.4 — Using KMS Keys

```python
# Encrypt with KMS CMK
kms = boto3.client('kms')
encrypted = kms.encrypt(
    KeyId='alias/my-app-key',
    Plaintext=b'sensitive data'
)['CiphertextBlob']

# S3 upload with KMS encryption
s3.put_object(
    Bucket='my-bucket',
    Key='file.txt',
    Body=data,
    ServerSideEncryption='aws:kms',
    SSEKMSKeyId='alias/my-app-key'
)
```

**KMS key types:**
- **AWS managed** — AWS creates and manages (aws/s3, aws/dynamodb)
- **Customer managed (CMK)** — You control policy, rotation, access
- **AWS owned** — Free, shared across accounts

### Skill 2.2.6 — Cross-Account Encryption

- Share CMK via **key policy** allowing external account
- Or use **S3 bucket policy** + SSE-KMS with cross-account key access
- External account needs `kms:Decrypt` on the key AND `s3:GetObject` on bucket

### Skill 2.2.7 — Key Rotation

- **AWS managed keys** — automatic annual rotation
- **Customer managed CMK** — enable automatic rotation (annual) or manual rotation
- Rotating key material doesn't require re-encrypting data (KMS tracks key versions)

---

## Task 2.3: Sensitive Data in Application Code

### Skill 2.3.1 — Data Classification

| Type | Examples | Handling |
|------|----------|----------|
| **PII** | Name, email, SSN | Encrypt, minimize collection, audit access |
| **PHI** | Medical records | HIPAA controls, encryption, access logging |
| **Credentials** | API keys, passwords | Secrets Manager, never in code/git |
| **Financial** | Credit card numbers | PCI DSS, tokenization |

### Skill 2.3.2 — Encrypt Environment Variables

```yaml
# SAM template — KMS-encrypted env vars
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Environment:
      Variables:
        API_KEY: !Ref ApiKeyParam
    KmsKeyArn: !GetAtt AppKey.Arn
```

Or retrieve from Secrets Manager at runtime (preferred for secrets).

### Skill 2.3.3 — Secret Management

| | Secrets Manager | Parameter Store (SecureString) |
|--|----------------|-------------------------------|
| Rotation | Automatic via Lambda | Manual |
| Cost | ~$0.40/secret/month | Free (Standard) |
| Use in Lambda | Retrieve at init (cache in global scope) | Same pattern |

```python
# Cache secret outside handler for warm start reuse
secret = None

def get_secret():
    global secret
    if secret is None:
        client = boto3.client('secretsmanager')
        secret = json.loads(
            client.get_secret_value(SecretId='prod/db')['SecretString']
        )
    return secret

def lambda_handler(event, context):
    db_creds = get_secret()
    ...
```

### Skill 2.3.4–2.3.5 — Sanitize and Mask Data

- **Never log** passwords, tokens, full credit card numbers
- **Mask in logs:** `****-****-****-1234`
- **Sanitize inputs** — prevent injection attacks
- **Redact in responses** — don't - don't return internal IDs unnecessarily

### Skill 2.3.6 — Multi-Tenant Data Access

Patterns for SaaS applications:
- **Partition key per tenant** — `tenantId#userId` in DynamoDB
- **IAM policy with tenant condition** — restrict S3 prefix per tenant
- **Cognito custom attribute** — `custom:tenantId` in JWT; validate in Lambda
- **Row-level security** — filter all queries by tenant ID in application code

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Mobile app needs temporary S3 upload credentials | Cognito Identity Pool |
| API needs user authentication | Cognito User Pool + API Gateway authorizer |
| Lambda needs database password with auto-rotation | Secrets Manager |
| Encrypt Lambda environment variables | KMS key on function config |
| Cross-account S3 access with encryption | Bucket policy + KMS key policy |
| Fine-grained "admin only" delete | Application-level auth in Lambda code |

**Next:** [Domain 3 — Deployment](domain-03-deployment.md) | [Security Guide](aws-security-dva-c02-guide.md)
