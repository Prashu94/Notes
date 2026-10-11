# Exam traps

Each line is a wrong answer that looks neighboring. If you missed it once, it goes on your own card. This list is the ones the practice exams already used.

## Identity

- An SCP is not a grant. An allow in an SCP does nothing without an allow in an identity policy.
- SCPs do not apply to the management account. Putting the workload there to "get around" an SCP is the failure.
- A permissions boundary does not grant the action. It only limits the role.
- A resource policy can allow a principal in another account. The principal's identity policy still has to allow the call, except for the anonymous cases you are not enabling.
- `AdministratorAccess` on a role in a sandbox OU still loses to a deny SCP on that OU.
- IAM users for staff are the old answer. Identity Center is the current one.
- Access keys in a repo, a Lambda environment, or a container image are the defect. The role is the fix.
- `AKIA` is a long-lived key. `ASIA` is a session. `ExpiredToken` means the cache outlived `Expiration`.
- IMDSv1 plus a wide instance role is the SSRF item. IMDSv2 (`http-tokens required`) and a narrow role are the fix. Hop limit 2 only when a container on the instance must reach IMDS.
- Trusting a tenant id from the JSON body when the token has a different tenant is the authorization bug.

## Network

- A security group is stateful. A NACL is not. Ephemeral ports belong on the NACL.
- Default NACL allows all. Default security group does not allow the world.
- Peering is not transitive. A to B and B to C does not give A to C.
- Peering refuses overlapping CIDRs.
- A gateway endpoint exists for S3 and DynamoDB. It does not exist for Secrets Manager, STS, KMS, or SQS. Those are interface endpoints.
- One NAT gateway in one AZ is an AZ outage for every private subnet that uses it. One NAT per AZ is the resilient answer and the more expensive one.
- A public subnet is "has a route to an IGW," not "has a public IP" by itself, and not "is called public."
- Multi-AZ is not a second Region.
- CloudFront certificates for custom domains live in us-east-1, even when the origin is elsewhere.
- WAF attaches to CloudFront, ALB, API Gateway, and AppSync. It does not attach to an NLB.
- Shield Standard is already on CloudFront and Route 53. Shield Advanced is the paid response and cost-protection answer.
- Global Accelerator is not a cache. CloudFront is not an anycast IP for UDP.

## Data

- A DynamoDB filter does not reduce read capacity. The read already happened.
- A scan of one hot partition key is how you throttle a table that looks idle in CloudWatch at the table level.
- `begins_with` is for the sort key.
- A read replica does not fail over. You promote it. Multi-AZ fails over.
- DynamoDB global tables accept writes in each Region. Aurora Global Database has one writer unless write forwarding is on.
- SSE-S3 is a managed key you do not administer. SSE-KMS is the key policy. Client-side means AWS stores ciphertext only.
- Cross-account `s3:GetObject` still fails without `kms:Decrypt` and a key policy allow.
- Versioning without a noncurrent expiration keeps every overwrite forever.
- STANDARD_IA wants objects to stay at least 30 days. A lifecycle transition on day 1 is rejected.
- Object Lock compliance cannot be shortened, including by root. You do not enable it on a lab bucket.
- S3 public access block at the account level beats a bucket policy someone adds later.
- RDS encryption must be on at creation. You do not flip it on a live unencrypted instance. You snapshot, copy encrypted, and restore.

## Compute and integration

- Lambda retries an async invoke twice, then the on-failure destination. A queue has its own redrive policy. Destinations are not the SQS DLQ.
- SQS is at-least-once. The write is idempotent, or you will double-charge.
- Deleting the SQS message before the write commits loses the work when the write fails.
- Without partial batch failure, one bad record fails the batch.
- Visibility timeout shorter than the function timeout redelivers a message the function is still processing.
- A Lambda global is reused on a warm environment. It is not a session store.
- Reserved concurrency of 0 turns the function off and removes that concurrency from the account pool. Any reservation removes its number from the pool.
- `$LATEST` and the image tag `latest` both move when someone deploys. Production points at a version, an alias, or a digest.
- API Gateway's integration timeout is about 29 seconds. A two-minute job is a queue and a 202, not a longer Lambda timeout.
- Returning HTTP 200 with an error in the body makes the client, and the alarm, think the call worked.
- Step Functions is orchestration. EventBridge is choreography. SNS fanout is not a workflow.
- Amazon MQ is for the protocol you already have. It is not the default queue.

## Delivery and operations

- A CloudFormation change set is how you see a replacement before it happens. A stack policy is how you refuse the replacement. `DeletionPolicy: Retain` is how a stack delete leaves the data.
- Drift is a console edit. The next deploy will fight it.
- A budget alarm does not stop spend.
- Cost Explorer and a tag are how you see the bill. An SCP or a smaller instance is how you change it.
- CloudTrail answers who called the API. VPC Flow Logs answer who talked to whom on the network. Logs Insights answers what the application printed. X-Ray answers where the time went. GuardDuty answers what looked malicious.
- A DLQ with no alarm is a bin.
- Readiness fails when the dependency is down. Liveness fails when the process is dead. Using one check for both restarts every task during a database blip.
- CodeDeploy canary plus an alarm is the rollback. Deleting the function is not.
- CDK is out of scope on the SAA guide. CloudFormation is the SAA answer. CDK and SAM are in scope on DVA.
- App Mesh is in maintenance. New service-to-service designs on these exams are ECS Service Connect or VPC Lattice.

## The new exams, without inventing a guide

- SAP-C03 and DVA-C03 task sentences are not public until 27 October 2026. Do not treat a blog bullet as a scored weight.
- Bedrock on DVA-C03 is about access, privacy, logging, and tool permissions. It is not about which model to pick, how to chunk a corpus, or a governance program. Those are out of scope for Developer.
- A model that asked for `dynamodb:DeleteItem` does not get a role that can delete the table. The role allows the one action the workflow already approved.
- Post-quantum KMS key specs (ML-DSA, ML-KEM) are named for SAP-C03. Confirm the CLI `key-spec` values in `aws kms create-key help` before you memorize a flag. The exam point is "the key spec changed," not a memorized enum from a blog.
- Prompt engineering as a craft is not a Developer item. Redacting the prompt in a log line is.
