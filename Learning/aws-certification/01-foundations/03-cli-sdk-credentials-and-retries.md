# CLI, SDK credentials, retries, and pagination

DVA domain 1 and domain 2. SAA and SAP only need to recognize that a role on the compute beats a key in a file.

Official:

- https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html
- https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html
- https://docs.aws.amazon.com/sdkref/latest/guide/overview.html
- https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
- https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/setting-credentials-node.html

## Install and check

```bash
aws --version
aws configure list
aws sts get-caller-identity
aws configure set region us-east-1 --profile sandbox
```

`configure list` shows which file supplied the key and the region. When a command hits the wrong account, this is the first command you run.

## Credential chain

The SDK and the CLI walk a chain and stop at the first hit. Order worth remembering:

1. Explicit keys in the client constructor. This is the one you avoid in application code.
2. Environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE`, `AWS_DEFAULT_REGION`.
3. Web identity token (`AWS_ROLE_ARN` plus `AWS_WEB_IDENTITY_TOKEN_FILE`). This is EKS IRSA and GitHub Actions OIDC.
4. Shared config `~/.aws/credentials` and `~/.aws/config`, including `source_profile` and `role_arn` for assume-role, and `sso_session` for Identity Center.
5. ECS container credentials (`AWS_CONTAINER_CREDENTIALS_RELATIVE_URI`).
6. EC2 instance metadata (IMDSv2). The hop limit must be 2 if a container on the instance needs the role and you are not using a task role.

Lambda sets the role credentials for you. You do not call `AssumeRole` for the function's own role. You call `AssumeRole` only when the function must hop into a different role.

IMDSv2:

```bash
aws ec2 modify-instance-metadata-options --instance-id "$IID" \
  --http-tokens required --http-put-response-hop-limit 2
```

`http-tokens required` blocks the old IMDSv1 request. A stem about SSRF stealing instance credentials wants IMDSv2 plus a role that can do very little.

## Profiles

```bash
aws configure sso --profile sandbox
aws sso login --profile sandbox
aws s3 ls --profile sandbox
export AWS_PROFILE=sandbox
```

A role profile in `~/.aws/config`:

```ini
[profile sandbox]
region = us-east-1
output = json

[profile prod-read]
role_arn = arn:aws:iam::111122223333:role/ReadOnly
source_profile = sandbox
region = us-east-1
```

## Retries

Default mode in current SDKs is a standard retry with exponential backoff and jitter. Adaptive mode adds client-side rate limiting when it sees throttling.

| Failure | Retry? |
| --- | --- |
| `Throttling`, `RequestLimitExceeded`, 503, timeouts | Yes |
| `AccessDenied`, `ValidationException`, `NoSuchBucket` | No. A retry will fail the same way |
| DynamoDB `ProvisionedThroughputExceededException` | Yes, with backoff. Then fix the capacity or the hot key |
| SQS receive that returns empty | Not an error. Poll again. Long polling (`WaitTimeSeconds` 20) beats a tight loop |

```python
from botocore.config import Config
cfg = Config(retries={"max_attempts": 8, "mode": "adaptive"}, connect_timeout=2, read_timeout=10)
```

Set timeouts. A default socket that waits forever will hold a Lambda invocation until the function timeout, and you will pay for the wait.

## Pagination

List APIs return a page and a token. Using only the first page is a production bug the exam describes as "the script misses resources."

```bash
aws s3api list-objects-v2 --bucket "$BUCKET" --prefix incoming/ --max-keys 1000
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId' --output text
```

The CLI paginates many commands for you. `--no-paginate` turns that off. Boto3 does not paginate unless you use a paginator or follow `NextToken`.

```python
paginator = client.get_paginator("describe_instances")
for page in paginator.paginate(Filters=[{"Name": "instance-state-name", "Values": ["running"]}]):
    for res in page["Reservations"]:
        for inst in res["Instances"]:
            print(inst["InstanceId"])
```

## Idempotency tokens

Some write APIs (`RunInstances`, `PurchaseReservedInstancesOffering`, some SQS and Firehose calls) take a client token. Retries with the same token do not double-create. Generate the token from a stable business id (the order id), not from `uuid4()` on every retry. A new token on every retry creates a new resource.

## Waiters

```python
s3.get_waiter("object_exists").wait(Bucket=b, Key=k)
ec2.get_waiter("instance_running").wait(InstanceIds=[iid])
```

A waiter polls. It is the right tool in a deploy script. It is the wrong tool inside a user-facing Lambda. There, return and let the caller poll, or use an event when the object lands.

## Errors you must distinguish

| Error | Meaning | Fix |
| --- | --- | --- |
| `ExpiredToken` | Session ended | Refresh. Do not cache STS output past `Expiration` |
| `AccessDenied` | Authenticated, not authorized | The policy, the SCP, the boundary, the KMS key, or the bucket policy |
| `InvalidClientTokenId` | The access key id is unknown | Wrong account or a deleted key |
| `SignatureDoesNotMatch` | Secret or clock or region signing bug | Clock skew, wrong secret, or a proxy rewriting the body |
| `AuthorizationHeaderMalformed` | Usually the wrong region for the bucket | Send the request to the bucket's Region |
| `RequestTimeTooSkewed` | Clock | Fix NTP |

## Exercises

1. A Lambda hard-codes an access key so it can write to S3 in the same account. Replace that with the mechanism the exam wants. Which policy do you attach, and where?
2. A pagination bug lists only 1,000 objects and the job reports success. Which API field did the code ignore?
3. GitHub Actions must deploy to a sandbox account. The security team forbids long-lived AWS keys in GitHub secrets. Which STS API does OIDC use?
4. A script retries `AccessDenied` five times. What does the fifth attempt change?
5. IMDSv1 is enabled and a public web app has an SSRF bug. What two changes shrink the blast radius?

## Answers

1. An execution role on the function, with `s3:PutObject` on the bucket prefix. No keys in the package or the environment.
2. `NextContinuationToken` / `IsTruncated` on `ListObjectsV2`, or the absence of a paginator.
3. `AssumeRoleWithWebIdentity`.
4. Nothing. The same deny comes back. Log it once and fix the policy.
5. Require IMDSv2, and replace the instance role's broad policy with the minimum the app needs. A WAF in front helps the SSRF. It does not replace the metadata and IAM fixes.

## The chain, in the order the SDK stops

The first hit wins. A stale key in the environment hides the instance role.

1. Keys passed to the client constructor. This is the one application code should not do.
2. Environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`.
3. Web identity: `AWS_ROLE_ARN` and `AWS_WEB_IDENTITY_TOKEN_FILE`. EKS IRSA and GitHub Actions.
4. Shared config: a profile, `source_profile` plus `role_arn`, or an SSO session.
5. ECS container credentials from the relative URI.
6. EC2 instance metadata. IMDSv2 with a hop limit of 2 only if a container on the instance must reach it.

Lambda injects the execution role. You do not call `AssumeRole` for the function's own role. You call it only to hop into a different role. Refresh before `Expiration`. `ASIA` keys are sessions. `AKIA` keys are long-lived and do not belong in a repository.

Retries: adaptive or standard mode, with jitter, for throttling and transient 500s. Do not retry `AccessDenied`, `ValidationException`, or a conditional check failure you already understand. A paginator follows `NextContinuationToken`, `LastEvaluatedKey`, or the service's next token. One call that returns a page and exits zero is a successful bug.

Waiters belong in deploy scripts. A user-facing Lambda returns and lets the caller poll, or it waits on an event. Sleeping in the handler until a stack is done is how you hit the timeout.

## More exercises

6. `AWS_ACCESS_KEY_ID` is set in the shell and the instance has a role. Which credentials does the CLI use?
7. A loop calls `list_objects_v2` until `IsTruncated` is false and never passes the token. What does it keep returning?
8. The SDK retries a DynamoDB conditional put that failed because the item exists. What should the code do instead?
9. `SignatureDoesNotMatch` started after a proxy was added. What is the proxy doing?
10. SSO works on a laptop. A container in CI has no browser. What replaces `aws sso login`?

## Answers

6. The environment variable. It is earlier in the chain than instance metadata. Unset it if you meant the role.
7. The first page, forever, if the loop condition is wrong, or the same first page each iteration. Pass `ContinuationToken` from the previous response.
8. Treat `ConditionalCheckFailedException` as success when the item existing means the work already happened. Retrying it will fail the same way and burn the attempt budget.
9. Rewriting the body or the headers after the signature was computed. The signature covers the payload. A proxy that "helps" by altering it breaks SigV4. Clock skew is the other cause. Check both.
10. OIDC. The workflow requests an identity token and calls `AssumeRoleWithWebIdentity`. There is no device-code login in the pipeline and no access key in the secrets.
