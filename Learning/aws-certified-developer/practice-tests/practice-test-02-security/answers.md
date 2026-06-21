# Practice Test 02 — Answers

1. **C** — Secrets Manager supports automatic rotation via Lambda functions on a schedule.
2. **B** — Configure `KmsKeyArn` on the Lambda function to encrypt environment variables at rest.
3. **B** — SSE-KMS requires both S3 read permission AND `kms:Decrypt` on the CMK key policy.
4. **B** — User Pools handle user directory, authentication, and sign-up/sign-in flows.
5. **B** — Explicit Deny always wins over any Allow in IAM policy evaluation.
6. **B** — `"aws:SecureTransport": "true"` condition ensures HTTPS-only access.
7. **B** — Tenant ID in partition key ensures data isolation; validate tenantId from JWT in every request.
8. **B** — `AssumeRole` exchanges credentials for a cross-account role.
9. **B** — Client-side = encrypt before upload; SSE = AWS encrypts at storage layer.
10. **B** — Sanitize/mask PII and sensitive data before writing to logs.
11. **B** — Cognito User Pool authorizer validates JWT tokens automatically at API Gateway.
12. **B** — ACM provides free public TLS certificates integrated with API Gateway and CloudFront.
13. **A and E** — Source account needs permission to assume role; target role needs trust policy (B) and permissions policy (E). Question asks for TWO from listed — A (identity policy allowing sts:AssumeRole) and E (permissions on target role).
14. **B** — Cache secrets in global scope; retrieved once per warm execution environment.
15. **B** — CMK usage is logged in CloudTrail; SSE-S3 (AWS managed) does not provide key-level audit.
