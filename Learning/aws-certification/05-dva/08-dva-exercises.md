# DVA exercises

## Questions

1. A handler stores the user id in a global variable set from the first event. The second user on a warm environment sees the first user's data. Why, and where does the session go?
2. `list_objects_v2` once, no loop. What is the bug?
3. SQS consumer deletes the message, then the conditional put fails because the item exists. Is that a bug or a correct idempotent outcome? What if the put failed for `ProvisionedThroughputExceededException` after the delete?
4. API returns 200 and the body says `"error": "db down"`. What should the status code be, and who set 200?
5. JWT signature is not checked. The code base64-decodes the payload and reads `tenant`. What is the attack?
6. Environment variable `DB_PASSWORD` on the function. Anyone with `lambda:GetFunctionConfiguration` can see it. Where do you move it, and which IAM action does the role gain?
7. Cross-account bucket, SSE-KMS, `s3:GetObject` allowed, decrypt fails. What is missing?
8. Canary shifted 10% to version 9. The alarm fired. Where should the alias point?
9. `latest` is the image tag in the ECS service. A developer pushes a broken build. Why did production move?
10. Logs contain the full API Gateway event. Name the field that must be removed before you log.
11. Reserved concurrency 0. The function "disappeared." What did 0 mean?
12. A cache key at API Gateway does not include the user. What do users see?
13. Lambda in a VPC can reach RDS and times out on Secrets Manager. What endpoint do you add?
14. GitHub Actions has an access key in a secret. Replace the identity mechanism.
15. DVA-C03: the agent tool can call `dynamodb:DeleteItem` on the whole table because the model said so. What do you change in IAM and in the workflow?

## Answers

1. The environment is reused. A global is not per request. Keep the user id in a local variable. Put durable session state in DynamoDB or ElastiCache.
2. Only the first page is processed. Paginator or `NextContinuationToken`.
3. If the item exists, the duplicate delivery is the success case. If the delete happened before a throttle, the message is gone and the write never landed. Delete only after a successful write, and treat "already exists" as success.
4. 503 or 500. The handler returned `statusCode: 200` out of habit. API Gateway proxy trusts that field.
5. Anyone can forge the payload. Verify the signature, issuer, audience, and expiry. Take the tenant from the verified claim.
6. Secrets Manager. `secretsmanager:GetSecretValue` on that secret, and `kms:Decrypt` if the secret uses a customer managed key.
7. `kms:Decrypt` in the role and an allow in the key policy for that role.
8. The previous version. The alias moves back. Version 9 can stay in the account.
9. The service tracks the tag. A new push of `latest` is a new image under the name production pulls. Pin a digest or an immutable tag.
10. `body`, and `authorization` headers. Log the request id and the route.
11. It throttles every invoke. Reserved concurrency is a cap. Zero means the function cannot run.
12. One user's response served to another, if the method is cached. Remove the cache or include a user dimension and accept a low hit rate.
13. An interface endpoint for Secrets Manager with private DNS. RDS was already private. Secrets Manager was a public API the VPC could not reach without NAT or an endpoint.
14. GitHub OIDC and `AssumeRoleWithWebIdentity`. Delete the access key.
15. The tool role allows delete only on the one item key the workflow already authorized, or it does not allow delete at all. A Step Functions approval sits in front of the delete. The model output is not an IAM decision.
