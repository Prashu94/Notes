# IAM, STS, Identity Center, and RAM

SAA 1.1. SAP 1.2 and 2.3. DVA 2.1. This is the chapter people fail when they memorize service names and then cannot explain why an allow did nothing.

Official:

- https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html
- https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html
- https://docs.aws.amazon.com/ram/latest/userguide/what-is.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html

## Principals

| Principal | Lives where | Give it |
| --- | --- | --- |
| Root user | One per account | MFA, no access keys, no daily use. It can close the account and change the support plan. SCPs do not apply to it in the management account |
| IAM user | One account | A password or a key. Legacy. The exam's "best practice" answer replaces humans with Identity Center |
| IAM group | A bag of users | Policies. Groups are not principals. You cannot put a group in a trust policy |
| IAM role | Assumed by a principal or a service | A trust policy and permissions. No long-term key |
| Identity Center user | The organization identity store or an external IdP | A permission set, which becomes a role in each assigned account |
| Federated user | Corporate IdP, Cognito, SAML, OIDC | Temporary credentials from STS |

## The evaluation order that answers "why was I denied"

AWS evaluates, in short form:

1. Explicit deny anywhere that applies wins. SCP, permission boundary, session policy, identity policy, resource policy.
2. If an SCP or a permissions boundary or a session policy is present, it must allow the action. These are ceilings. They grant nothing by themselves.
3. Then an allow must exist. Same-account: the identity policy is enough for most resources. Cross-account: the identity policy in the caller account and the resource policy in the owner account both allow.
4. Resource-based policies can allow a principal directly for some services (S3, KMS key policies, Lambda, SQS, SNS, secrets).

| Policy type | Attached to | Grants access? | Typical stem |
| --- | --- | --- | --- |
| Identity-based | User, group, role | Yes | "Allow this role to read this bucket" |
| Resource-based | Bucket, key, queue, secret, function | Yes, to the principal it names | Cross-account, or a service principal writing a log |
| Permissions boundary | User or role | No. Maximum | A developer can create roles and must not create an admin |
| SCP | OU or account | No. Maximum for the whole account | "Even administrators must not leave this Region" |
| Session policy | An STS session | No. Maximum for that session | AssumeRole with a narrower policy than the role |
| VPC endpoint policy | The endpoint | No. Maximum for traffic through that endpoint | Private S3 access limited to one bucket |
| Service control is not a resource policy |  |  | Do not mix these rows on exam day |

An SCP deny of `ec2:RunInstances` blocks every principal in the member account, including roles the member thinks are admin. It does not block the management account. It does not block service-linked roles in the cases AWS documents as exceptions. Read the current SCP evaluation page if a stem hinges on a service-linked role.

## A role you can actually use

Trust policy (who can assume it). EC2 example:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

Permissions (what the role can do):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::orders-BUCKET/incoming/*"
  }]
}
```

Cross-account trust with an external id, which blocks a confused deputy:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111122223333:root"},
    "Action": "sts:AssumeRole",
    "Condition": {"StringEquals": {"sts:ExternalId": "a-shared-secret-from-the-partner"}}
  }]
}
```

Trusting `:root` means "any principal in that account whom that account allows to assume this role." It does not by itself let every user in that account in. Their identity policy still needs `sts:AssumeRole`.

Commands:

```bash
aws iam create-role --role-name app-read --assume-role-policy-document file://trust.json
aws iam put-role-policy --role-name app-read --policy-name read --policy-document file://perm.json
aws iam create-instance-profile --instance-profile-name app-read
aws iam add-role-to-instance-profile --instance-profile-name app-read --role-name app-read
aws iam attach-role-policy --role-name app-read --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
aws sts assume-role --role-arn arn:aws:iam::ACCOUNT:role/app-read --role-session-name lab --external-id a-shared-secret-from-the-partner
aws sts get-caller-identity
```

`ReadOnlyAccess` loses a least-privilege stem. It wins a "let the auditor look, least operational overhead, nothing sensitive was specified" stem only if you accept how wide it is. Prefer a custom policy when the stem lists the APIs.

## STS APIs

| API | When |
| --- | --- |
| `AssumeRole` | You know the role ARN. Cross-account, service, break-glass |
| `AssumeRoleWithWebIdentity` | OIDC: Cognito, GitHub Actions, EKS IRSA. No long-term AWS key on the far side |
| `AssumeRoleWithSAML` | A SAML IdP |
| `GetSessionToken` | An IAM user adds MFA to a session. Not how EC2 gets credentials |
| `GetFederationToken` | A custom identity broker. Older pattern. Identity Center replaced it for workforce |
| `DecodeAuthorizationMessage` | Turn an encoded deny into the policy that caused it. Needs its own permission |

Temporary credentials have `AccessKeyId`, `SecretAccessKey`, `SessionToken`, and an expiration. All three fields are required on the call. Missing `SessionToken` looks like a bad key.

## Identity Center

Use it for humans in more than one account, and for humans in one account if you are starting now.

| Piece | Job |
| --- | --- |
| Identity source | Identity Center directory, Active Directory, or an external IdP (Okta, Entra ID) |
| Permission set | A template that becomes an IAM role in each account you assign |
| Assignment | A user or group, a permission set, an account |
| CLI | `aws configure sso` then `aws sso login --profile sandbox` |

Permission sets support a managed policy, a custom policy, and a permissions boundary. Session duration is on the permission set. MFA is on the identity source.

Directory Service (AWS Managed Microsoft AD) is the answer when a Windows workload must join a domain: FSx for Windows, RDS for SQL Server Windows auth, EC2 joined to AD. It is not the answer for "employees need the console." That is Identity Center federated to the existing AD.

## RAM

Resource Access Manager shares a resource into another account without copying it.

Shareable things that show up on exams: Transit Gateway and its attachments, VPC subnets (so a central network account owns the VPC and a workload account launches into it), Route 53 Resolver rules, License Manager configurations, Aurora or RDS clusters where the feature is supported, Capacity Reservations.

```bash
aws ram create-resource-share --name net-tgw --resource-arns "$TGW_ARN" \
  --principals 444455556666 --permission-arns arn:aws:ram::aws:permission/AWSRAMDefaultPermissionTransitGateway
aws ram get-resource-shares --resource-owner SELF
```

The consumer account accepts the share unless the organization has sharing enabled inside the org, in which case acceptance can be automatic. An SCP can still block the use of the shared resource.

## Access Analyzer

| Use | What it finds |
| --- | --- |
| External access | Buckets, roles, KMS keys, and other resources shared outside the zone of trust (the account or the organization) |
| Unused access | Roles and permissions nobody has used. Feed this into a least-privilege cleanup |
| Policy generation | A policy from CloudTrail activity. The starting point, then you review it |
| Policy validation | Syntax and findings before you attach it |

"Detect buckets that became public" is Access Analyzer or the S3 Block Public Access plus a Config rule. GuardDuty is for the API call that looks like an attacker after the fact. Macie is for the sensitive data inside the object.

## Conditions you will see

| Key | Meaning |
| --- | --- |
| `aws:SourceIp` | The caller's IP. Useless for traffic that comes through a service |
| `aws:SourceVpce` | The VPC endpoint id. Locks a bucket to a private path |
| `aws:SourceAccount` / `aws:SourceArn` | The service that is calling you is doing so on behalf of this account or resource. Required on confused-deputy fixes for SNS, S3 event notifications, CloudTrail |
| `aws:PrincipalOrgID` | Any account in this organization. Easier than listing accounts, dangerous if the org is broad |
| `aws:MultiFactorAuthPresent` | The STS session used MFA. Does not evaluate the way people expect on Identity Center users |
| `s3:prefix` | Limits `ListBucket` |
| `dynamodb:LeadingKeys` | Limits items a principal can touch to keys that start with their tenant id |

## Exercises

1. An SCP allows only `us-east-1` and `us-east-2`. A role in a member account has `AdministratorAccess`. Can that role create a bucket in `eu-west-1`?
2. A bucket policy allows account B's role to `s3:GetObject`. The role in B has no S3 permissions. Can the role read the object?
3. A partner account must assume your role. You are worried they will use the role ARN inside a different product of theirs that you did not approve. Which condition do you add?
4. Developers must create IAM roles for their apps and must be unable to create a role with more power than they have. Which feature?
5. Fifty accounts, one AD, users need CLI access for three hours. Which service, and which CLI command starts the session?
6. The network team owns a Transit Gateway. Twenty workload accounts must attach. Which service shares it, and why is peering each VPC to a network VPC the weaker answer at this scale?

## Answers

1. No. The SCP deny or the missing allow for that Region is a ceiling. `AdministratorAccess` cannot exceed it. The management account is the exception, and this role is in a member account.
2. Same-account resource policies can be enough. Cross-account, both sides allow. Account B's role needs an identity policy that allows `s3:GetObject` on that ARN as well as the bucket policy. KMS adds a third allow if the object is SSE-KMS with a customer key.
3. `sts:ExternalId`.
4. A permissions boundary on the roles they create, plus an identity policy that lets them create roles only if the boundary is attached (`iam:PermissionsBoundary`).
5. IAM Identity Center. `aws configure sso` and `aws sso login`.
6. RAM. A peering mesh does not scale, is not transitive, and puts route tables in every VPC. A shared Transit Gateway is the hub.

## Policies you should be able to read cold

An identity policy grants. This one lets a role read one prefix and nothing else. `s3:ListBucket` is an action on the bucket ARN, not the object ARN. People attach `GetObject` on the bucket ARN and then cannot list, or they attach `ListBucket` on the object ARN and the list still fails.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::orders-prod",
      "Condition": {"StringLike": {"s3:prefix": ["incoming/*"]}}
    },
    {
      "Sid": "ReadObjects",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::orders-prod/incoming/*"
    }
  ]
}
```

A trust policy is a resource policy on the role. It does not grant S3. It grants `sts:AssumeRole` to the principal who may call it. For EC2 the principal is the service `ec2.amazonaws.com`. For a human in another account the principal is that account or, better, that role ARN. For GitHub Actions the principal is the OIDC provider, and the condition pins `sub` to the repository and the branch.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111122223333:role/partner-copy"},
    "Action": "sts:AssumeRole",
    "Condition": {"StringEquals": {"sts:ExternalId": "a-long-unlisted-value"}}
  }]
}
```

Trusting `arn:aws:iam::111122223333:root` means any principal in that account whose own admin allows `sts:AssumeRole` can call you. The external id stops a confused deputy: a different product in the partner account cannot reuse the role ARN unless it also knows the id. It does not stop the partner's administrator. If the stem says "only this one role," name that role, not `:root`.

A permissions boundary is attached to the role. It does not grant. If the identity policy allows `s3:*` and the boundary allows only `s3:GetObject`, the effective permission is `GetObject`. The boundary is how a delegated admin can create roles without being able to create an admin. The creating principal's policy must require `iam:PermissionsBoundary` to equal the boundary ARN, or the developer will create the role and forget the boundary.

An SCP is the same shape of ceiling, attached to an OU or a member account. It does not apply to the management account. A deny of `ec2:RunInstances` for `p*` and `g*` on the sandbox OU still denies a role that has `AdministratorAccess`. Moving the workload into the management account to escape the SCP is the failure the item is testing.

Session policies are a third ceiling, passed to `AssumeRole`. A broker can hand a role to a process and pass a session policy that is narrower than the role. The session cannot exceed it. Useful when one role serves many tenants and the session should see one prefix.

## STS calls, and which credential comes back

| API | Who calls it | What you get |
| --- | --- | --- |
| `AssumeRole` | An IAM principal that is allowed to, calling a role | Temporary `ASIA` keys and a session token. Duration is from 15 minutes up to the role maximum, which caps at 12 hours. The default is 1 hour |
| `AssumeRoleWithWebIdentity` | A holder of an OIDC token: GitHub Actions, EKS IRSA, a mobile IdP | Same shape of temporary credentials. No AWS access key was involved |
| `AssumeRoleWithSAML` | A holder of a SAML assertion from a corporate IdP | Same. Identity Center has largely replaced hand-built SAML for humans. You still recognize the API |
| `GetSessionToken` | An IAM user, often to attach MFA | Temporary credentials for that user. This is not a role. You cannot call it with root in the way people hope, and you should not be building on IAM users |
| `GetFederationToken` | An IAM user minting a restricted session | Older federation. Identity Center and `AssumeRole` are the answers now |

`AKIA` prefixes are long-lived access keys. `ASIA` prefixes are session keys. `ExpiredToken` means the cache outlived `Expiration`. Refresh by calling `AssumeRole` again. Do not fix it by writing a long-lived key into the environment.

The credential chain the SDK walks, in the order that matters on the exam: explicit keys in the constructor (the one you avoid), environment variables, a web identity token file, the shared config file including `role_arn` and SSO, ECS container credentials, then EC2 instance metadata. The first hit wins. A stale key in the environment hides the instance role and is the "it works on my laptop and not on the instance" bug, or the reverse.

IMDSv2 is `http-tokens required`. A hop limit of 1 keeps the metadata on the instance. A hop limit of 2 is for a container on that instance that must reach IMDS. The role behind IMDS is still least privilege. IMDSv2 does not shrink a wide role. It stops the easy SSRF that used IMDSv1.

## Identity Center, the human path

One organization. One identity source: the built-in directory, an external SAML or OIDC IdP, or Active Directory via the connector. People and groups live there. Permission sets are templates. Assigning a permission set to a group for an account creates a role in that account. You do not hand-build that role per account. MFA is configured on the identity source. Disabling the user in the IdP ends access, bounded by the session that is already issued. Session duration on the permission set is the leftover-credential control.

CLI access is `aws configure sso` and `aws sso login`. The profile in `~/.aws/config` points at the start URL and the account. There is no access key to rotate. A pipeline is not a person: it uses `AssumeRole` or `AssumeRoleWithWebIdentity`, not an SSO login prompt.

Identity Center is not Managed Microsoft AD. AD is for workloads that must join a domain (Windows, FSx for Windows, RDS SQL Server Windows authentication). Humans can be federated from that AD into Identity Center. Standing up Managed AD only so people can click the console is the extra directory.

Permission sets can carry a permissions boundary and a session duration. A production assignment that is `AdministratorAccess` "because the SCP will save us" is empty if the only SCP on the OU is `FullAWSAccess`. Write the deny.

## Cross-account, the three allows

Account A reads an SSE-KMS object in account B.

1. The role in A has `s3:GetObject` and `kms:Decrypt` on the object ARN and the key ARN.
2. The bucket policy in B allows that role `s3:GetObject`.
3. The key policy in B allows that role `kms:Decrypt` and `kms:GenerateDataKey` as needed.

Miss any one and the error is often just `AccessDenied` from S3. CloudTrail on the key shows the `Decrypt` denial. AWS-managed keys (`aws/s3`) are a poor cross-account choice because you do not own the key policy the way you own a customer managed key. The stem "another account must decrypt" wants a customer managed key.

Service principals need a source condition. A bucket policy that allows `cloudtrail.amazonaws.com` with no `aws:SourceArn` lets a trail you do not own write, or confuse the bucket. The same pattern applies to SNS, EventBridge, and S3 event notifications into SQS. The condition is the exam fix for confused deputy when the caller is an AWS service rather than a partner account. The partner-account version is `sts:ExternalId`.

KMS key policies are special. If the key policy does not trust the account, IAM policies inside the account cannot grant use of the key. Leave an admin statement for a role you control, or you can lock the ciphertext away from yourself. Disabling the key is reversible and is the incident control. Scheduling deletion has a waiting period of 7 to 30 days and then the data is gone.

## RAM, what is actually shared

RAM shares a resource. It does not copy it. The owner pays for the resource. The consumer needs an identity policy that allows use, and an SCP in the consumer account can still block it. Shares inside an organization can auto-accept. Shares outside require an accept step.

What you share on these exams: a Transit Gateway, a subnet (the network account owns the VPC, the application account launches into it), Resolver rules, a License Manager configuration, an Aurora cluster so another account can attach. You do not share a thing the service cannot share and then invent a snapshot copy as "RAM." Snapshot copy is a copy. RAM is a share.

Sharing with the organization when only one OU needed it is the over-share Access Analyzer will flag. Share with the OU or the account.

## What each exam wants from this chapter

| Exam | The item |
| --- | --- |
| SAA | Identity Center versus IAM users, a role on the compute, SCP as a ceiling, cross-account role plus resource policy, ExternalId, Block Public Access rather than a public principal |
| SAP | Permission sets per OU, delegated admin, RAM for the network, SCP exceptions for global services, the log-archive key policy, a pipeline role that cannot edit the trail |
| DVA | The execution role versus a key in the code, `AssumeRoleWithWebIdentity`, `LeadingKeys`, not logging the token, session expiry |

## More exercises

7. A role policy allows `s3:*` on one bucket. A permissions boundary on the role allows only `s3:GetObject`. Can the role delete an object?
8. GitHub Actions has `AWS_ACCESS_KEY_ID` in the repository secrets. Replace the mechanism. What goes in the trust policy?
9. `GetSessionToken` versus `AssumeRole`. Which one do you call from a Lambda function that must write to a bucket in another account?
10. The key policy allows the account root, and the role's identity policy allows `kms:Decrypt`. Decrypt works in-account and fails from a role in another account that has the same identity policy. What is missing?
11. A developer can create roles. They create one without a boundary and attach `AdministratorAccess`. Which two controls would have stopped that?
12. Flow logs show an accepted connection. The question is which IAM role made the API call an hour later. Which log answers the second question?

## Answers

7. No. The boundary is a ceiling. Delete is not in the boundary, so it is denied even though the identity policy allows `s3:*`.
8. An IAM OIDC provider for `token.actions.githubusercontent.com` and a role whose trust policy allows `sts:AssumeRoleWithWebIdentity` with a condition on `aud` and on `sub` for that repository and branch. Delete the access key.
9. `AssumeRole` on a role in the other account, if the trust allows this function's role. `GetSessionToken` does not change which account you are. It wraps the current user. Lambda should not be an IAM user in the first place.
10. The key policy must name the other account's role, or the other account must be trusted and that role's admin must be allowed to use the key. An identity policy in the other account cannot grant a key it does not own. KMS will not follow "I allowed myself."
11. An identity policy that denies `iam:CreateRole` and `iam:AttachRolePolicy` unless `iam:PermissionsBoundary` equals the approved boundary ARN. An SCP that denies `iam:AttachRolePolicy` of `AdministratorAccess` would also stop it and is coarser. Either control works. Neither exists in the stem, which is why the developer succeeded.
12. CloudTrail, not VPC Flow Logs. Flow logs have IPs and ports. CloudTrail has the principal and the API.
