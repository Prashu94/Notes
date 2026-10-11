# Identity: Cognito, Directory Service, Verified Permissions

SAA 1.1 and 1.2. DVA 2.1. SAP uses Identity Center and Directory Service in migrations. Workforce identity is in `01-foundations/02-iam-sts-identity-center-ram.md`. This file is application identity.

Official:

- https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html
- https://docs.aws.amazon.com/directoryservice/latest/admin-guide/what_is.html
- https://docs.aws.amazon.com/verifiedpermissions/latest/userguide/what-is-avp.html

## Three different directories

| Need | Service |
| --- | --- |
| App users, sign-up, social login, SAML or OIDC, JWT for your API | Cognito user pool |
| Those users must also call AWS APIs with temporary credentials | Cognito identity pool, exchanging a user-pool token for a role |
| Employees into the AWS console and CLI | IAM Identity Center. Not a user pool |
| Windows instances, FSx for Windows, RDS SQL Server Windows auth | AWS Managed Microsoft AD, or AD Connector if the domain stays on-premises |
| Fine-grained authorization in the application, "can this user edit this document" | Verified Permissions (Cedar), or your own checks plus a tenant key. IAM is the wrong tool for per-row app rules unless you are vending credentials per tenant |

## Tokens

| Token | Use |
| --- | --- |
| ID token | The app learns who the user is. Claims. Not an AWS credential |
| Access token | Call your API. Scopes and groups |
| Refresh token | New tokens. Longer lived. Store it carefully |

API Gateway validates a user-pool token with a Cognito authorizer, or any JWT with the HTTP API JWT authorizer. A Lambda authorizer is the escape hatch. Verify issuer, audience, expiry, and signature. Decoding the middle of the JWT and trusting it is not validation.

Hosted UI is the least code for sign-up and federated login. You still set the callback URLs. A wildcard callback is a bug.

## Identity pools

Authenticated role and unauthenticated role. The unauthenticated role is a public credential. Keep it empty of data permissions. The authenticated role can be narrowed with principal tags and `dynamodb:LeadingKeys` so a tenant only sees their items. That is DVA skill 2.1.7 and 2.3.6.

## Directory Service

| Option | Use |
| --- | --- |
| Managed Microsoft AD | You want AWS to run the domain controllers |
| AD Connector | Proxy to your existing AD. The domain stays where it is |
| Simple AD | Small, Samba-based. Rarely the exam answer now |

Trusts between forests show up when a migration must keep an on-premises domain and a cloud domain. Identity Center can use Managed AD or an external IdP as its identity source. That does not replace the domain join for a Windows file server.

## Verified Permissions

A policy store, a schema, Cedar policies, an `IsAuthorized` call from the application. Use it when the stem says application authorization that changes with the resource, and they do not want that logic scattered in every service. It does not replace IAM for calling `s3:GetObject`. The app checks Verified Permissions, then the app's role calls AWS.

## Commands

```bash
aws cognito-idp create-user-pool --pool-name orders
aws cognito-idp create-user-pool-client --user-pool-id "$POOL" --client-name web --no-generate-secret
aws ds describe-directories
```

## Exercises

1. A mobile app has users. The API is API Gateway. Nobody should get an IAM user. Which Cognito feature, and which authorizer?
2. The same app must upload to a prefix named after the user id. User pool only, or an identity pool as well?
3. A file server on EC2 must join a domain AWS runs. Identity Center or Managed Microsoft AD?
4. "Only the author may publish" is a rule that changes per document. IAM policy on the bucket, or Verified Permissions in the app?

## Answers

1. A user pool, and a Cognito authorizer or a JWT authorizer on the API. IAM auth on the method would mean AWS credentials, which they said they do not want for users.
2. An identity pool if the mobile client receives AWS credentials and writes to S3 itself. If the API uploads on the user's behalf, the API's role writes to S3 and the user pool is enough. Read who holds the SDK.
3. Managed Microsoft AD. Identity Center does not join a server to a domain.
4. Verified Permissions or a check in the application. A bucket policy cannot express "author of this document" unless you have built a very specific prefix scheme and you accept its limits.

## Cognito, the two products

A user pool is your user directory for the application. It signs users up, stores them or federates them to Google, Apple, SAML, or OIDC, and issues tokens. The ID token is the identity the API trusts after it verifies the signature. The access token is for calling APIs. The refresh token gets a new pair without another password prompt. A JWT authorizer on API Gateway checks the issuer, the audience, and the signature. Decoding the payload without the signature check is the bug.

The hosted UI is the login pages Cognito serves. Lambda triggers fire on sign-up, sign-in, and token generation when you must add a claim or block a user. A pre-token-generation trigger is how a tenant id gets into the token. Putting the tenant id in a form field the client sends later is how a user picks a different tenant.

An identity pool trades a user-pool token, a social token, or an anonymous session for temporary AWS credentials. Use it when the mobile client itself must call S3 or DynamoDB. The authenticated role must be scoped: a prefix per user, or `dynamodb:LeadingKeys`, not `s3:*`. The unauthenticated role is the tutorial footgun. Disable it if anonymous AWS access is not a requirement. If your API uploads on the user's behalf, you do not need an identity pool. The API's role writes to S3. The user pool is enough. Read who holds the SDK.

MFA and compromised-credential protection are user-pool features. They are not IAM MFA. IAM MFA is for IAM users, which this chapter is trying not to create.

## Directory Service

| Directory | Use |
| --- | --- |
| AWS Managed Microsoft AD | A real AD that EC2, FSx for Windows, and RDS SQL Server can join. Trusts to an on-premises forest when you need them |
| AD Connector | A proxy to an on-premises AD so AWS can authenticate against it without hosting the domain |
| Simple AD | A small Samba-compatible directory. Rare on these exams. Not the answer for a Windows estate |

Identity Center is the human console path and can use AD as its identity source. It does not join a file server to a domain. Managed AD does. You often run both: Identity Center for people, Managed AD for Windows workloads. Standing up Managed AD only so administrators can click the console is the extra directory.

## Verified Permissions

Cedar policies decide "can this principal do this action on this resource" inside the application. The user pool tells you who the user is. Verified Permissions tells you whether that user may publish this document. IAM decides whether the application's role may call DynamoDB. Those are three layers. Collapsing "only the author may publish" into a bucket policy fails as soon as the rule is per document rather than per prefix.

Cache the authorization decision only as long as a revocation can wait. A one-hour cache on a removed author is the same bug as a one-hour Lambda authorizer cache.

## More exercises

5. The ID token is decoded in the browser and the API trusts the body the browser posts. What did the API skip?
6. An identity pool's authenticated role allows `s3:GetObject` on `*`. What can any signed-in user do?
7. FSx for Windows must join a domain, and staff must use SSO for the console. Which two services?
8. A pre-token trigger adds `custom:tenant`. The code still reads the tenant from the JSON body. Does the trigger help?
9. Simple AD is proposed for a company that already has a forest and needs SQL Server Windows auth. What do you run instead?

## Answers

5. Signature, issuer, audience, and expiry checks against the user pool. The browser can post any JSON. The API must validate the token itself or sit behind a JWT authorizer that does.
6. Read every object in the account that resource policies also allow, not just their prefix. Scope the role to the user's prefix or stop vending credentials and upload through the API.
7. Managed Microsoft AD for the file system. Identity Center, often federated to that AD or to the corporate IdP, for the console. One of them does not do the other's job.
8. No. The claim is on the token and the code ignores it. Read the tenant from the verified claim and do not accept a different value from the body.
9. Managed Microsoft AD, with a trust to the existing forest if the users must stay there. Simple AD does not replace a forest and is the wrong place for SQL Server Windows authentication at that scale. AD Connector if AWS should not host the domain and the on-premises AD is reachable.
