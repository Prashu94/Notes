# Practice Test 02 — Security (DVA-C02)

**15 questions** · Domain 2 (26%) · Recommended time: 25 minutes

---

## Questions

### 1
A Lambda function needs to read credentials from a database that must be rotated every 30 days automatically. Which service should store the credentials?

A) Lambda environment variables  
B) AWS Systems Manager Parameter Store (String)  
C) AWS Secrets Manager  
D) Hardcoded in the deployment package  

### 2
A developer needs to encrypt sensitive data in a Lambda environment variable at rest. What should be configured?

A) S3 bucket encryption  
B) KMS key on the Lambda function configuration  
C) CloudTrail logging  
D) VPC encryption  

### 3
An application uses server-side encryption with AWS KMS (SSE-KMS) for S3 objects. The Lambda execution role can read objects but gets Access Denied on decrypt.

What is missing?

A) S3 bucket policy allowing Lambda  
B) KMS key policy granting the Lambda execution role `kms:Decrypt` permission  
C) Enable S3 Transfer Acceleration  
D) Configure S3 Object Lock  

### 4
A web application needs user registration, sign-in, and password reset. Which Cognito feature should be used?

A) Cognito Identity Pool  
B) Cognito User Pool  
C) IAM User with login profile  
D) AWS SSO  

### 5
Which IAM policy evaluation rule always takes precedence?

A) Explicit Allow  
B) Explicit Deny  
C) Permission boundary Allow  
D) Resource-based policy Allow  

### 6
A developer must ensure API calls to AWS services use encrypted connections. Which IAM condition key enforces this?

A) `aws:SourceIp`  
B) `aws:SecureTransport`  
C) `aws:MultiFactorAuthPresent`  
D) `aws:RequestedRegion`  

### 7
A multi-tenant SaaS application stores data in DynamoDB. Each tenant's data must be isolated. What is the BEST application-level pattern?

A) Separate DynamoDB table per tenant  
B) Include tenantId in the partition key and filter all queries by tenantId  
C) Use one shared IAM role for all tenants  
D) Disable encryption  

### 8
A Lambda function needs to assume a role in another AWS account to access resources. Which STS operation should the code call?

A) GetSessionToken  
B) AssumeRole  
C) GetFederationToken  
D) GetCallerIdentity  

### 9
What is the difference between client-side encryption and server-side encryption (SSE)?

A) SSE is less secure than client-side  
B) Client-side encrypts data before sending to AWS; SSE encrypts at the storage layer  
C) They are identical  
D) SSE requires customer-managed keys only  

### 10
A developer logs application events but must not log user credit card numbers. Which practice should be followed?

A) Log all data for debugging  
B) Sanitize and mask sensitive data before logging  
C) Disable all logging  
D) Store card numbers in CloudWatch Logs encrypted with SSE-S3  

### 11
An API Gateway endpoint must validate JWT tokens from a mobile app. Which authorizer type should be configured?

A) IAM authorizer  
B) Cognito User Pool authorizer  
C) No authorizer — validate in Lambda only  
D) Resource policy  

### 12
A developer needs to generate TLS certificates for a development API Gateway custom domain. Which service provides free public certificates?

A) AWS Private CA  
B) AWS Certificate Manager (ACM)  
C) Self-signed certificates in Lambda  
D) AWS KMS  

### 13
Cross-account access requires permissions in which policies? (Select TWO.)

A) Identity-based policy in source account  
B) Trust policy on the role in target account  
C) S3 bucket ACL only  
D) CloudWatch alarm policy  
E) Permissions policy on the role in target account  

### 14
A Lambda function retrieves secrets at the start of every invocation, causing latency. How should the developer optimize?

A) Hardcode secrets in the handler  
B) Cache the secret in a global variable outside the handler, retrieved once per execution environment  
C) Disable secret rotation  
D) Use plaintext environment variables  

### 15
Which encryption option provides an audit trail of key usage via CloudTrail?

A) SSE-S3  
B) SSE-KMS with customer managed CMK  
C) Client-side encryption with self-managed keys  
D) Unencrypted storage  

---

See [answers.md](answers.md)
