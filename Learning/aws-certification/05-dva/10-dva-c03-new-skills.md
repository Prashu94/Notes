# DVA-C03 skills

The four DVA-C02 domains still exist. Weights move to 30, 26, 22, and 22, and domain 3 is named Testing and Deployment. This file is the delta from the 1 September 2026 blog. Confirm it against the guide on 27 October 2026.

## Task 2.3 — AI security

| Skill theme | What you implement |
| --- | --- |
| Access to AI services | A role with `bedrock:InvokeModel` on one model ARN. Not `bedrock:*` |
| Privacy | Interface VPC endpoint. Organizations AI opt-out or the Bedrock setting that your prompts are not used to train models |
| Content filtering and prompt injection | A Bedrock Guardrail on the call. The tool's IAM still denies anything the model should not do |
| Agent sessions | Separate session per user. Tenant from the token. A human approval in Step Functions before a tool that spends money or deletes |
| Logs | Redact prompts and completions. Do not enable API Gateway full-body logs on that route |

Out of scope for this exam even on C03: prompt-engineering as a craft, RAG architecture, choosing a model, SageMaker AI, and an AI governance framework. If the question is "which model family," you are in the wrong exam. If the question is "the role is too wide and the log has the prompt," you are in this one.

## Containers

Build an image. Push to ECR. Scan on push. Deploy to ECS on Fargate or to EKS. Execution role pulls. Task role calls AWS. Pin the tag. `05-labs` does not include a full cluster build. The commands are in `02-services/03-containers-ecs-eks-fargate-ecr.md`.

## Tools across the lifecycle

Q Developer or Kiro may draft the handler, the test, the review comment, and a guess at a slow query. You accept the draft only after you run the test and you have removed secrets from the prompt. A pipeline approval can be assisted. It still needs an alarm and a person or a policy for production.

## New names on the in-scope list

Bedrock, AgentCore, Amazon Q, Kiro, Data Firehose, PrivateLink. Firehose is the delivery stream. PrivateLink is the VPC endpoint. You already met both in the service chapters. C03 can ask them directly.

## Task 2.3 in code

The role allows `bedrock:InvokeModel` on one model ARN. The function runs in a private subnet and calls Bedrock through an interface endpoint. The account opt-out says prompts are not training data. A guardrail is attached to the call. The tool that can spend money or delete is a separate role, and a Step Functions callback sits in front of it. The tenant comes from the verified token. Logs contain the request id and token counts. They do not contain the prompt.

That is the scored developer skill. Chunking strategy, embedding choice, and "which model" are the architect exam. If a stem asks you to design retrieval, you are in the wrong guide. If it shows a log line with a customer id from the prompt, you redact it.

## Containers and Firehose, the new in-scope names

An image is built, pushed to ECR, scanned on push, and deployed to Fargate or EKS. The execution role pulls. The task role calls AWS. The tag is immutable. A pipeline that deploys `latest` is the defect.

Firehose lands a stream in S3 or OpenSearch when you do not need to replay it yourself. Kinesis Data Streams is still the replayable log. PrivateLink is how the VPC reaches the API without a NAT. You already use it for Secrets Manager. C03 can name Bedrock the same way.

Q Developer and Kiro draft code. You run the test and you keep secrets out of the prompt. The tool is not an approval.

## More exercises

1. The function logs `prompt` and `completion` at INFO. The route is a support bot. What do you change in the log statement and in API Gateway access logs?
2. A task role has `bedrock:*`. The function calls one model. What is the action and the resource?
3. Fargate in a private subnet cannot pull from ECR and there is no NAT. Which endpoints?
4. A practice item asks you to choose an embedding model and a chunk size. Which exam is that?
5. Firehose or Data Streams: the consumer must reprocess yesterday's events after a bad deploy.

## Answers

1. Log the request id only. Drop the prompt and the completion, or run them through a redaction step that removes email, account numbers, and tokens. Turn off full-body logging on that API stage. The access log that prints `$input.body` is the same leak.
2. `bedrock:InvokeModel` on that model ARN. `bedrock:*` includes model management and every model in the account.
3. Interface endpoints for ECR API and ECR DKR, plus an S3 gateway endpoint because layers live in S3, with private DNS on the interface endpoints. The execution role still needs the pull permissions.
4. The architect exam, SAP-C03, if it is scored there. Not DVA-C03. Developer scope is calling and securing the model, not designing the retrieval pipeline.
5. Data Streams, with retention that covers yesterday. Firehose has already delivered. It is not a cursor you rewind. Firehose can still be a consumer that copies the stream to S3.
