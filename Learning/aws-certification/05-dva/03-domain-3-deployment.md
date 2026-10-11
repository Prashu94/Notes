# DVA Domain 3 — Testing and deployment (24%)

Skills 3.1 through 3.4. You do not design the pipeline. You do commit code that a pipeline can build, and you do pick the strategy.

## Artifacts

Dependencies inside the zip, the image, or a layer. A layer is shared code, not a junk drawer. The handler path matches the file. Memory and timeout come from a measurement. AppConfig or a stage variable changes a flag without a new zip.

ECR for images. Immutable tags. Scan on push. The execution role pulls. The task role calls AWS.

## Tests

`sam local invoke -e events/apigw.json` for a unit-level invoke. A separate account or a stage named `test` for integration. Do not point tests at production. Mock the SDK in unit tests. Do not mock the function you claim to test. EventBridge tests use an event with a source your dev rule matches.

Q Developer may draft the test. You check the assertions.

## Strategies

| Change | Mechanism |
| --- | --- |
| Lambda 10% then 100% | Version, alias, CodeDeploy canary, alarm |
| ECS new tasks then the listener | Blue/green |
| EC2 a batch at a time | Rolling, preferably with an extra batch |
| Instant undo | Keep the old version or the old task set and point back |
| Dev versus prod code path | Stage variable or alias, not a forked template |
| Flag | AppConfig with bake time |

`latest` as the production image tag is the wrong answer. `$LATEST` as the production Lambda target is the wrong answer.

## Pipeline facts you will be shown

A push starts the pipeline. CodeBuild runs the buildspec. The deploy stage assumes a role. A failed hook or a CloudWatch alarm rolls back. CloudFormation change sets show a replacement before you execute it. Two stages of one API are not two unrelated APIs unless you created two.

## Exercise

Prod is alias `live` on version 14. The pipeline publishes version 15 and shifts 10% for five minutes. Errors breach the alarm. What should traffic be on when rollback finishes, and what is still deployed?

Answer: `live` points at 14 again, or 100% of traffic is on 14. Version 15 still exists. You do not delete it to roll back. You move the alias. The bad version is available for the postmortem.

## What you are responsible for

You do not design the company's pipeline product. You do commit an artifact a pipeline can build, you do pick the deployment strategy that matches the blast radius, and you do wire the alarm that rolls it back. The out-of-scope line on the exam guide is "designing a CI/CD pipeline" as an architecture exercise. The in-scope line is every skill under domain 3: artifacts, tests, infrastructure as code for the application, and the strategy. If the stem shows a buildspec, a task definition, or an alias, you are in scope.

## Artifacts

Dependencies are in the zip, the image, or a Lambda layer. A layer is shared code you version, not a place to dump a one-off script. The handler string matches the file and the function name. `handler.handler` means `handler.py` and `def handler`. A wrong string is a runtime error that looks like a permissions error if you only read the API Gateway 502.

Memory and timeout come from a measurement of `Duration`, not from the template default of 128 MB and 3 seconds. A timeout that is shorter than the downstream's p99 is an outage you deployed on purpose.

Configuration that changes between environments is a stage variable, an AppConfig profile, or a parameter. It is not a second copy of the code. AppConfig has an application, an environment, a configuration profile, and a deployment strategy with a bake time. The bake time is how a bad flag rolls back. A feature flag with no bake and no alarm is a global variable you edit in production.

Containers: the image is in ECR, the tag is immutable or you deploy a digest, scan on push fails the pipeline on a critical finding, the execution role can pull, the task role can call AWS. `latest` means the next push from anyone who can push changes production the next time a task starts. That is the bug.

## Tests

Unit tests mock the SDK and assert the parameters. They do not mock the function you claim to test. They do not call production. A fixture event for API Gateway, one for SQS, and one for S3 cover the three shapes people mix up. `sam local invoke -e events/apigw.json` runs the function in a container. It does not prove IAM. An integration test in a separate account or a `test` stage proves IAM, the queue, and the table. Contract tests for an event: the producer and the consumer agree on `source` and `detail-type`. A test that only checks the HTTP status and not the row in DynamoDB misses the bug where you return 201 and forget the put.

Q Developer may draft the test. You check that the assertion can fail. A test with no assertion, or an assertion on a constant, is not a test. C03's Kiro drafts the same way. You still run it.

Load tests belong against the test stage with a ceiling on concurrency, so you do not discover the account's Lambda quota in production. The metric you watch is the downstream (database connections, throttles), not only the function's duration.

## Strategies

| Change | What has to already exist |
| --- | --- |
| Lambda, 10 percent then 100 percent | A published version, an alias, a CodeDeploy deployment group using that alias, an alarm on errors or latency |
| Lambda, instant rollback | Move the alias back to the previous version. The bad version stays |
| ECS | A new task definition revision. The service's minimum healthy percent and maximum percent decide whether you have spare capacity. Blue/green needs a second target group and a listener rule |
| EC2 | Rolling, preferably with an extra batch so capacity does not dip. The health check must be the load balancer's, or a bad AMI stays in service |
| Instant undo of a container | The previous task definition revision is still registered. You roll the service back to it |
| Dev versus prod code path | A stage variable or an alias. Not a forked repository |
| A flag | AppConfig, bake time, an alarm |
| A schema | Expand and contract. The old code and the new code run at the same time during the canary. A drop-column migration cannot be canaried |

`$LATEST` moves when you update the code. An alias does not move until you point it. API Gateway, event source mappings, and the CLI should call the alias. Calling `$LATEST` means the canary never happened, because you already replaced the only target.

CloudFormation change sets show a replacement. Replacing a table or a bucket is a data migration, not a deploy. If the logical id changes, CloudFormation thinks it is a new resource. Stable logical ids are part of writing the template. `DeletionPolicy: Retain` on the table means a stack delete leaves the data. SAM and CDK generate these templates. You still read the change set.

## Pipeline facts the snippet will show

A push to the branch starts the pipeline. CodeBuild runs `buildspec.yml`. The build role can read the repo and write the artifact. It cannot administer IAM in the management account. The deploy stage assumes a role in the application account. A test stage fails the pipeline before deploy. A manual approval sits in front of production. A CloudWatch alarm on the canary fails the deployment and rolls it back. A hook script that returns a non-zero code fails the deployment. Two stages of one API are two configuration surfaces of one API, not two unrelated products, unless you created two APIs.

GitHub Actions uses OIDC. The trust policy's `sub` claim pins the repository and the branch. A token from another repository fails the condition. There is no access key in the repo secrets. If the stem shows `AWS_ACCESS_KEY_ID` in the pipeline variables, that is the defect.

CodeArtifact is the private package store so the build does not pull untrusted public packages for the production deploy. A lockfile is the application-side version of that control.

## Environments

Dev can be a smaller table and a shared NAT. Prod cannot be the same account with a different stage variable if the stem says a blast radius or a compliance boundary. Separate accounts, the pipeline promoting the same artifact, not a rebuild that might produce a different zip. Rebuilding in prod "to pick up a patch" is how prod runs code nobody tested. Promote the artifact. Patch by rebuilding in the pipeline and promoting again.

## Exercises

1. Prod is alias `live` on version 14. Version 15 shifts 10 percent. The alarm fires. Where does traffic go, and is version 15 deleted?
2. Why is deploying the image tag `latest` a different bug from deploying a digest?
3. The change set says the DynamoDB table will be replaced. What do you do before execute?
4. A unit test mocks `handler` and asserts it was called. What have you proved?
5. Dev works and prod fails with `AccessDenied` on KMS. The code is the same artifact. Name two configuration causes that are not "the code is wrong."

## Answers

1. The alias goes back to version 14. Version 15 remains so you can read its logs. Deleting it is not the rollback.
2. `latest` moves when anyone pushes. The service will eventually start tasks on a new image you did not deploy on purpose. A digest is immutable. You change tasks only when you change the digest in the task definition.
3. You stop. A replacement is a new table. Rename nothing. Add an update policy or a deletion policy, and change the template so the update is in place. If you needed a new key schema, that is a migration to a new table you copy into, not an accidental replacement.
4. That the mock framework works. The handler's behavior was replaced. Assert on the SDK call or on the return value of the real handler with the SDK mocked.
5. The prod role is missing `kms:Decrypt`, or the prod key policy does not allow the prod role, or the environment variable points at a different key. An SCP in prod that denies `kms:*` outside a path is a third. The zip being identical is why you look at IAM and configuration next, not at a rebuild.
