# SAP-C03 skills that are not in the C02 task list

Source: the 1 September 2026 AWS Training and Certification blog. The task sentences publish on 27 October 2026. Study these as scored material if you sit SAP-C03. On SAP-C02, Guardrails, AgentCore Identity, and human oversight are unscored pretest topics. The rest is the announced delta.

Weights were not published. Do not invent them.

## Generative AI and agents

| Requirement | Design |
| --- | --- |
| Call a foundation model without operating training clusters | Amazon Bedrock |
| Retrieval over company documents | A knowledge base: embeddings, a vector store (OpenSearch, Aurora PostgreSQL, or the store the current Bedrock docs list), and a prompt that includes the retrieved passages. You design the data access and the IAM. You do not train the model |
| Stop the model from answering with PII or a topic the policy forbids | Bedrock Guardrails on the application, not a sentence in the prompt alone |
| An agent that calls tools | Bedrock AgentCore for the runtime. Each tool is an IAM-scoped action. The agent role can only call the tools you named |
| A person must approve a refund, a send, or a delete | Step Functions callback (task token) or a queue a human worker completes. The agent does not get a direct `s3:DeleteBucket` |
| Identity for the agent | AgentCore Identity, or a normal IAM role per tenant. Do not share one admin role across tenants |

Cost: log input and output tokens, set quotas, and cache embeddings. A synchronous giant context on every request is the bill you will be asked to cut. Detail in `02-services/17-generative-ai-bedrock-q-kiro.md`.

## Post-quantum cryptography

KMS ML-KEM for key establishment and ML-DSA for signatures, when the stem says post-quantum or "verify in 15 years." Confirm `--key-spec` in `aws kms create-key help` the week you study. A normal SSE-KMS bucket key remains the answer for "encrypt the objects."

## Resilience engineering

| Tool | Job |
| --- | --- |
| Resilience Hub | Assess an application against an RTO and RPO policy. It recommends. It does not fail over |
| Fault Injection Service | Prove the recommendation. Kill an AZ, pause an API, fill a disk. Run it in a drill account |
| Application Recovery Controller | Routing controls and readiness checks for gray failures and for "is the other Region actually ready" |
| Systems Manager Automation | The runbook the alarm invokes |

## Cloud-native patterns named in the announcement

Serverless data pipeline: S3 event or Kinesis to Firehose or Lambda to a lake, Glue for the batch side, Step Functions when the steps need state. VPC Lattice or ECS Service Connect instead of a new App Mesh. ECR scan on push and a pipeline that fails the build. Multi-tenant: tenant id in the key, a role or a policy condition per tenant, no shared admin credential. Real-time path: Kinesis or MSK. Batch path: Glue or EMR. Do not force one path to do both.

## DevSecOps and observability

Scan images and dependencies in CodeBuild. Deploy through a pipeline account that assumes roles. Do not give the pipeline `AdministratorAccess` in the management account. Container Insights or Managed Prometheus for the cluster. CloudWatch RUM and Synthetics for the user path. Model invocation metrics and guardrail intervention counts for the AI path.

## Data named in the announcement

Lake Formation plus Iceberg tables in S3 for the lakehouse. Athena and EMR read them. Glue catalog. Cross-account sharing of a table, not a copy of the bucket into every account. Clean Rooms when two companies must compute on combined data without exchanging the raw rows.

## Scenario

A bank wants a customer-service agent that can read account notes and draft a fee reversal. Reversals over 200 USD must be approved by a person. Notes contain account numbers that must not appear in logs. The model must not answer questions about account takeover.

Bedrock with a knowledge base limited to the notes the role can read. A guardrail that blocks account-takeover topics and masks account numbers. The agent tool that posts a reversal is a Lambda the workflow calls only after a Step Functions approval task. Logs redact the account number before they are written. VPC endpoints so the prompt does not go over the internet. An SCP or an opt-out policy so prompts are not used to train models.

## What was announced, and what was not

The 1 September 2026 blog names the themes. It does not publish domain weights or the full task sentences. Those arrive with the exam guide when registration opens on 27 October 2026. Study the themes. Do not invent a percentage. On SAP-C02, Guardrails, AgentCore Identity, and human oversight are unscored pretest items. On SAP-C03 they are in the scored story the blog described.

| Theme | The design you should be able to draw |
| --- | --- |
| Agents | Bedrock model, a knowledge base scoped by IAM, a guardrail, AgentCore or a runtime whose tools are separate roles, a Step Functions approval before money or deletion |
| Post-quantum | KMS ML-KEM for key establishment and ML-DSA for signatures. Confirm `key-spec` in `aws kms create-key help` the week you sit. SSE-KMS remains the answer for "encrypt the objects" |
| Resilience engineering | Resilience Hub to assess, FIS to prove, ARC to shift traffic when health checks lie, Systems Manager Automation as the runbook |
| Cloud-native | Lambda and Step Functions, ECS Service Connect or VPC Lattice, not a new App Mesh. ECR scan on push. Tenant id in the key |
| DevSecOps | The pipeline fails the build on a critical scan. It assumes a deploy role. It is not an admin in the management account |
| Observability | Container metrics, synthetics, RUM, model invocation metrics, guardrail intervention counts |
| Data | Lake Formation and Iceberg in S3. Share a table, not a bucket copy. Clean Rooms when the other company must not see the rows |

## More exercises

2. The blog lists eleven generative-AI skills and does not list weights. A practice question asks which SAP-C03 domain is 29 percent. What do you do with that number?
3. A pipeline in the management account has `AdministratorAccess` and deploys to every account. Which announced control does it fail?
4. App Mesh is proposed for a new multi-account HTTP mesh with IAM on each call. What do you propose instead?
5. Two banks want a joint fraud score and neither can receive the other's transactions. Which product from the announcement?
6. You need to verify signatures in 15 years against a quantum-capable adversary. ML-DSA or a larger RSA key you hope lasts?

## Answers

2. Ignore it. Weights were not published. A third-party percentage is not the guide. Re-read the guide on 27 October and correct this file if the weights differ.
3. The pipeline must not be an admin in the management account. Move it to shared services. Give it a deploy role per account. Scan the image and fail the build. SCPs still apply to that role because it is in a member account.
4. VPC Lattice. App Mesh is in maintenance. Service Connect if every caller is an ECS service. Lattice is the cross-account HTTP and IAM answer the announcement named.
5. Clean Rooms. A shared bucket or a shared snapshot gives them the rows. The announcement's sentence is the computation without the raw exchange.
6. ML-DSA, the signature scheme named for this. A larger classical key is not the post-quantum answer. ML-KEM is for establishing a shared secret, not for signing the artifact.
