# DVA practice exam

20 original questions. The real exam is 65 questions and 130 minutes. Answers in `09-dva-practice-exam-answers.md`.

1. A Lambda global holds a shopping cart. Two users hit a warm environment. What happens?
   A. Each user gets an isolated global
   B. They can see each other's data if the code stored it in the global
   C. Lambda serializes all users in the account onto one environment
   D. Globals are cleared after every invoke

2. Which SQS consumer behavior survives a second delivery?
   A. Insert the order and assume the queue is exactly-once
   B. A conditional put that treats "item exists" as success
   C. Delete the message, then write the database
   D. Store the cart in a Lambda global

3. `list_objects_v2` returns 1,000 keys and `IsTruncated` is true. The code stops. What did it ignore?
   A. The Region
   B. `NextContinuationToken`
   C. The object ACL
   D. The KMS key spec

4. API Gateway integration timeout is about 29 seconds. The job takes two minutes. What should the handler do?
   A. Set the Lambda timeout to 15 minutes and leave the client waiting
   B. Enqueue the job and return 202
   C. Switch to a bigger memory setting so two minutes fit in 29 seconds
   D. Enable caching

5. A user-pool JWT arrives in `Authorization`. The code decodes it and does not check the signature. What is required?
   A. Trust the payload if it is valid JSON
   B. Verify signature, issuer, audience, and expiry
   C. Store the JWT in S3
   D. Turn the method auth to NONE

6. A function in a VPC reaches RDS and cannot reach Secrets Manager. There is no NAT. What do you add?
   A. A public IP on RDS
   B. An interface VPC endpoint for Secrets Manager
   C. A gateway endpoint for Secrets Manager
   D. An Internet Gateway on the data subnet

7. SSE-KMS object, cross-account role, `s3:GetObject` allowed, decrypt fails.
   A. Add `kms:Decrypt` on the role and allow the role in the key policy
   B. Make the bucket public
   C. Disable rotation
   D. Switch the function to a larger memory size

8. Where should a rotating database password live?
   A. A Lambda environment variable committed in git
   B. Secrets Manager
   C. A tag on the function
   D. The function name

9. Production Lambda traffic moves 10% to a new version, then an alarm fires. What rolls back?
   A. Delete the function
   B. Point the alias back at the previous version
   C. Change the memory
   D. Disable CloudTrail

10. Which image tag is safe for an ECS production service?
    A. `latest`
    B. An immutable tag or a digest you deployed on purpose
    C. Whatever the developer pushed last
    D. The Dockerfile `FROM` line

11. Partial batch failure is off. One SQS message in a batch of ten throws. What happens?
    A. Only that message retries
    B. The batch fails and the other nine can be processed again
    C. The queue deletes all ten
    D. Lambda Destinations run because this is an SQS mapping

12. Which metric dimension is the expensive one?
    A. A status code
    B. A unique user id on every metric
    C. The function name
    D. The stage name

13. Readiness and liveness use the same check, which fails when the database fails. What happens to the tasks?
    A. They stop receiving traffic and stay up
    B. They are restarted because liveness fails, which can take the whole service down during a database blip
    C. Nothing. ECS ignores health checks
    D. The database fails over to Lambda

14. GitHub must deploy with no long-lived AWS key.
    A. `AssumeRoleWithWebIdentity` via OIDC
    B. An access key in the repo
    C. The root account password in a secret
    D. `GetSessionToken` with a user key stored in the workflow

15. A filter expression on a DynamoDB scan returns one item and consumes a large number of RCUs. Why?
    A. Filters reduce the read before it happens
    B. The scan already read the items. The filter only hides them
    C. RCUs are not charged for scans
    D. The partition key was too unique

16. Which client construction matches the exam's preferred credential story on Lambda?
    A. `boto3.client("s3", aws_access_key_id="AKIA...", aws_secret_access_key="...")`
    B. `boto3.client("s3")` and an execution role
    C. Keys in an environment variable named `AWS_SECRET_ACCESS_KEY` set in the template
    D. The root key in Parameter Store as a `String`

17. Stage variables exist so that:
    A. Dev and prod can target different Lambda aliases without a second code package
    B. The VPC CIDR changes at runtime
    C. IAM users get MFA
    D. S3 versioning turns on

18. CloudWatch Logs Insights is the tool you open when:
    A. You need the principal who called `DeleteTrail`
    B. You need the log lines for one `aws_request_id`
    C. You need to buy a Savings Plan
    D. You need a VPC peering connection

19. DVA-C03. Prompts from a private subnet must not use the internet, and must not be used to train models. Which two controls?
    A. A Bedrock interface endpoint, and the data-use opt-out
    B. A public function URL and a longer prompt
    C. `Action: *` on the function role
    D. Logging the full prompt and the full completion to a shared log group

20. An alarm on DLQ depth is missing. Messages sit in the DLQ for a week. What did the application lose?
    A. Nothing. A DLQ is a successful archive
    B. The failed work, unless something pages a person or a consumer repairs the DLQ
    C. The IAM role
    D. The Route 53 zone
