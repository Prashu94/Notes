# DVA Domain 2 — Security (26%)

Skills 2.1 through 2.3. IAM administration of users and groups is out of scope. Using roles, tokens, keys, and secrets in the application is the whole domain.

## Auth

User pool JWT on the API. Identity pool only when the client needs AWS credentials. IAM auth when the caller is another AWS principal and you want SigV4. A Lambda authorizer when the token is not a Cognito JWT. Verify the token. Do not trust a tenant id from the body when the token says a different tenant.

`AssumeRole` for a cross-account hop. `AssumeRoleWithWebIdentity` for GitHub and for EKS IRSA. Pass `ExternalId` for a vendor. Cache temporary credentials only until `Expiration`.

Least privilege is the action and the ARN. `dynamodb:LeadingKeys` is the multi-tenant IAM condition when you vend credentials. Verified Permissions or a check in code is the per-document rule.

## Encryption

TLS in transit. SSE-KMS when you need a key policy. Client-side when AWS must not see plaintext. Encryption context on encrypt and decrypt. Cross-account reads need the key policy and `kms:Decrypt`. Rotation on for customer managed symmetric keys. Disabling a key stops decrypt. That is an incident control and an outage if you do it by mistake.

ACM for the API's public name in the right Region. Private CA for internal names. A dev cert from `openssl` is fine on a laptop and is not the production story.

## Secrets

Secrets Manager for rotating passwords. Parameter Store SecureString for rare config. Lambda environment variables with a customer managed key only if you accept they are still retrievable by anyone who can read the configuration and decrypt. Do not log the secret, the token, or the full event if the event contains a password. API Gateway access logs that print the body will leak it.

Multi-tenant: the partition key starts with the tenant id from the token. The update expression cannot be pointed at another tenant by a field in the JSON.

## Exercise

A function logs `event` at INFO. The event is an API Gateway proxy request. The body is `{"password":"..."}`. The role also has `s3:*`. List the two defects and the IAM fix.

Answer: stop logging the body, or redact `password` first. Replace `s3:*` with `s3:GetObject` and `s3:PutObject` on the one prefix. If the password is a secret the function needs later, read it from Secrets Manager instead of the client sending it on every call.

## What this domain is actually grading

IAM administration of users and groups is out of scope. You do not design the organization's permission sets. You do write the role the function assumes, the condition on the queue, the check on the token, and the line that must not log the secret. Every item is "the code or the resource policy is wider than the sentence."

## Tokens and authorizers

A user-pool JWT is verified by API Gateway when you attach a JWT authorizer, or by your code when the token arrives at a Lambda authorizer or at the function. Verification means the signature, the issuer, the audience, and the expiry. Decoding the middle section of the JWT and trusting it is the bug. Anyone can forge that JSON.

The tenant id comes from a claim, not from the body and not from a query string. The body is attacker-controlled even after authentication, because an authenticated user can ask for someone else's tenant. A fine-grained check is `dynamodb:LeadingKeys` when you vend AWS credentials (identity pool or a role scoped to a tenant prefix), or a condition in the code that compares the key to the claim before the write. Verified Permissions is the policy engine when the rules are "this user can edit this document" and they do not fit an IAM condition.

| Caller | Mechanism |
| --- | --- |
| A browser user of your API | User pool, JWT authorizer |
| A browser that must call S3 or DynamoDB itself | Identity pool, exchanging the user-pool token for temporary AWS credentials. Scope those credentials. Do not hand out a role that can read the whole bucket |
| Another AWS account or a service | IAM auth, SigV4. API Gateway `AWS_IAM`, or a resource policy |
| A token that is not a Cognito JWT | A Lambda authorizer. Cache the result for the TTL you can tolerate. A long cache on a revoked token is the incident |
| GitHub Actions, or an EKS pod | `AssumeRoleWithWebIdentity`. The trust policy's condition pins the repo and the branch, or the Kubernetes service account |
| A vendor that assumes your role | `sts:ExternalId` |
| A person with an IAM user, which you should be deleting | MFA and `aws:MultiFactorAuthPresent` on the sensitive calls |

Cache temporary credentials only until `Expiration`. `ExpiredToken` means you cached past it. Refresh by assuming the role again. Do not refresh by shipping a new access key.

Cognito identity pools have an authenticated role and an unauthenticated role. The unauthenticated role is the one that accidentally gets `s3:*` in a tutorial. If the app does not need anonymous AWS access, do not enable it.

## Least privilege in the policies you write

Name the action and the ARN. `s3:GetObject` on `arn:aws:s3:::bucket/prefix/*`. `dynamodb:PutItem` and `dynamodb:GetItem` on one table. `sqs:ReceiveMessage`, `DeleteMessage`, and `GetQueueAttributes` on one queue. `kms:Decrypt` on one key, often with an encryption-context condition so the same key cannot be used for a different bucket.

A wildcard action with a specific resource is still wrong when the stem says least privilege. A specific action with `Resource: *` is wrong when the service supports resource-level permissions. Some actions only support `*`. The exam's wrong answer is the wildcard on an action that has a resource ARN, not the obscure action that cannot be scoped.

The execution role and the task role are different. The execution role pulls the image and writes logs. The task role reads the table. Putting the table permissions on the execution role means every task that uses that execution role has them, including tasks that should not. Lambda has one role. That role should still be one function's role, not a shared `lambda-admin` role used by every function in the account.

Resource policies on the function, the queue, and the bucket are the other half. A function policy that allows `principal: *` plus an authorizer you forgot to attach is a public function. API Gateway's permission to invoke the function should be the API's source ARN, not every API in the account.

## Encryption in the code path

TLS is the transit answer. You do not disable certificate verification to make a lab pass. SSE-KMS is the at-rest answer when a key policy must exist. You pass the key id when you `PutObject` if the bucket policy requires `aws:kms`. You do not log the data key. Encryption context on `Encrypt` and `Decrypt` must match. A decrypt without the same context fails, which is the point.

Cross-account reads need the key policy and `kms:Decrypt`. A bucket policy is not a key policy. Disabling the key stops decrypt for everyone, including you. That is an incident control. Rotation does not invalidate old ciphertext.

Certificates: ACM for the API's public name, in the API's Region, and in `us-east-1` if the front door is CloudFront. Private CA for internal names. A certificate bundled in the repo expires, and it is the outage.

## Secrets, logs, and multi-tenant data

Secrets Manager for a password that rotates. The SDK cache has a TTL. Do not fetch the secret on every invocation if the value is stable for minutes, and do not cache it for days. Parameter Store SecureString for configuration that is secret and does not rotate. A Lambda environment variable encrypted with a customer managed key is still readable by anyone who can `GetFunctionConfiguration` and `kms:Decrypt`. It is acceptable for non-secret configuration. It is the wrong place for a database password the stem says must rotate.

Do not log the event if the event is an API Gateway proxy request. The body, the `Authorization` header, and the query string are the leaks. Log the request id, the route, and the status you returned. API Gateway access logs that include `$context.requestOverride` or the full body will store the password in the log group. The log group then needs the same protection as the secret, which means you already lost.

Multi-tenant rows: the partition key starts with the tenant id from the token. An update expression that takes the key from the JSON lets a tenant overwrite another tenant's item if they can guess the key. Ignore the body's tenant field.

## Exercises

1. The identity pool's authenticated role allows `s3:GetObject` on `*`. What can any signed-in user do, and what condition or ARN fixes it?
2. A Lambda authorizer caches for 3600 seconds. You revoke a user. What does the cache do, and what TTL do you set if revocation must take effect within five minutes?
3. `kms:Decrypt` is allowed in the identity policy. Decrypt still fails cross-account. What else is required?
4. The function logs `event["headers"]` for debugging. Name the header that makes this a credential leak.
5. Two functions share one role that can read both tables. Why does that fail least privilege when one function is compromised?

## Answers

1. They can read every bucket the role's account can read, and any object the resource policies also allow. Restrict the ARN to the one prefix, and use a condition such as `s3:prefix` tied to the tenant, or `dynamodb:LeadingKeys` in the DynamoDB version of this bug.
2. The authorizer keeps returning the cached allow until the TTL ends. Set the TTL at or under 300 seconds, and accept the extra authorizer invocations. A 0 TTL checks every call and costs more.
3. The key policy in the key's account must allow this role. KMS does not care that the caller's own account allowed `kms:Decrypt` if the key policy never mentions them.
4. `Authorization`, and often `Cookie`. Also the body if you logged that. Log the request id instead.
5. The attacker who can run one function can read both tables. Split the roles. A compromise should be one table, one prefix, one queue.
