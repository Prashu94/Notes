# DVA practice exam answers

16 of 20 is 80% on this drill.

| # | Answer | Why |
| --- | --- | --- |
| 1 | B | A warm environment reuses globals. They are not per user and they are not cleared for you |
| 2 | B | At-least-once delivery. The write has to be safe the second time. Deleting first loses the message if the write fails |
| 3 | B | Truncation means another page. The token is how you ask for it |
| 4 | B | The integration will not wait two minutes. Accept the work and process it from a queue |
| 5 | B | An unverified JWT is attacker-controlled JSON |
| 6 | B | Secrets Manager is an AWS API. From a private subnet with no NAT you need the interface endpoint. It is not a gateway endpoint. Those are S3 and DynamoDB |
| 7 | A | The key policy and `kms:Decrypt`. Public buckets and memory size do not decrypt |
| 8 | B | Rotation is the product. An environment variable in git is not |
| 9 | B | The alias is the traffic pointer. Deleting the function is not a rollback |
| 10 | B | `latest` moves when someone pushes. Pin the tag or the digest |
| 11 | B | Without partial batch response, one failure fails the batch. Destinations are not the SQS retry mechanism |
| 12 | B | One metric per user is a cardinality bill. A status code is a small set |
| 13 | B | Liveness restarts the task. A dependency check belongs on readiness so traffic stops and the process stays up |
| 14 | A | OIDC web identity. Keys in the repo and root passwords are the failures |
| 15 | B | Filters do not reduce read capacity. Design the key so the query does not scan |
| 16 | B | The execution role is the credential. Hard-coded keys and plaintext parameters are the defects |
| 17 | A | Stage variables are runtime configuration for the stage, including which alias a method calls |
| 18 | B | Insights queries logs. CloudTrail answers who deleted the trail. Savings Plans and peering are not log queries |
| 19 | A | PrivateLink for the API, and an opt-out so the prompts are not training data. Logging the full prompt fails the sensitive-content skill. `Action: *` fails least privilege |
| 20 | B | A DLQ holds failures. Without an alarm or a consumer, nobody repairs them |
