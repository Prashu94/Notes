# DVA-C03 transition

Source: AWS Training and Certification blog, 1 September 2026.

https://aws.amazon.com/blogs/training-and-certification/september-2026-new-offerings/

The exam page repeats the dates:

https://aws.amazon.com/certification/certified-developer-associate/

The task-by-task guide is published when registration opens on 27 October 2026. This file uses only what that blog stated. It does not invent skill sentences AWS has not printed.

## Dates and format

| Item | Fact from AWS |
| --- | --- |
| Registration opens | 27 October 2026, all languages the exam already supports |
| Last day of DVA-C02 | 30 November 2026 |
| First day of DVA-C03 delivery | 1 December 2026 |
| Duration | 130 minutes |
| Questions | 65 (50 scored, 15 unscored) |
| Price | 150 USD |
| Passing score | 720 / 1000 |
| Delivery | Pearson VUE, test center or online |
| Experience AWS recommends | 1+ year developing on AWS, one high-level language, AI-assisted development, application lifecycle and CI/CD |

A DVA-C02 pass stays valid through its original expiration.

## Domains AWS published, with weights

The four-domain shape stays. The names and weights move.

| DVA-C02 | Weight | DVA-C03 | Weight |
| --- | --- | --- | --- |
| Development with AWS Services | 32% | Development with AWS Services | 30% |
| Security | 26% | Security | 26% |
| Deployment | 24% | Testing and Deployment | 22% |
| Troubleshooting and Optimization | 18% | Troubleshooting and Optimization | 22% |

Testing is called out in the domain name. Troubleshooting and optimization gain four points. Development drops two. Security stays the second-heaviest domain.

## What AWS says is new

### New Task 2.3 — AI security (5 skills)

AWS named the five themes:

1. Access management for AI services.
2. Data privacy controls: VPC endpoints, and making sure inputs and outputs are not used to train the provider's models.
3. Content filtering and prompt-injection protection.
4. AI agent interaction security: tool-use authorization, session isolation, human-in-the-loop approval.
5. Protecting sensitive content so it does not land in monitoring logs.

Taught in `05-dva/10-dva-c03-new-skills.md` and `02-services/17-generative-ai-bedrock-q-kiro.md`.

### AI-assisted development across every domain

| Domain | What you are now expected to do with the tools |
| --- | --- |
| 1 Development | Code generation and automated review |
| 3 Testing and Deployment | Test automation, regression testing, CI/CD help including automated deployment approvals |
| 4 Troubleshooting | Error analysis and troubleshooting suggestions, performance recommendations |

Amazon Q Developer is already a scored DVA-C02 skill (1.1.11 and 3.3.6). DVA-C03 expands that from "you can use the assistant" to "you can use it safely in each phase." Kiro is named as a new in-scope tool for spec-driven development.

### Containers

Building and managing images in Amazon ECR. Deploying with ECS, EKS, and Fargate. DVA-C02 already lists ECR, ECS, and EKS. DVA-C03 makes image build and Fargate deployment first-class. Taught in `02-services/03-containers-ecs-eks-fargate-ecr.md`.

### New in-scope services AWS named

- Amazon Bedrock
- Amazon Bedrock AgentCore
- Amazon Q
- Kiro
- Amazon Data Firehose
- AWS PrivateLink

Firehose and PrivateLink were already things a careful DVA-C02 candidate met inside Kinesis and VPC. They are now named.

## What AWS says was consolidated

The blog describes merges. It does not print the replacement skill sentences. When the guide lands, diff it. Until then, study the current skills. A merge does not delete the knowledge.

| Area | What the blog says happened |
| --- | --- |
| DynamoDB | 4 skills become 1 comprehensive skill |
| Encryption and sensitive data | 13 skills across 2 tasks become 7 skills in 1 task |
| Testing | 11 skills across 2 tasks become 5 skills in 1 task |
| Observability | 8 skills become 5 |
| Optimization | 9 skills become 6 |

## Explicitly out of scope on DVA-C03

The blog lists these as out of scope for the developer exam:

- Prompt engineering as a discipline
- RAG design
- AI model selection
- Amazon SageMaker AI
- AI governance framework design

Those belong to the architect and to the ML engineer exams. A developer item can still ask you to call Bedrock with a role, a VPC endpoint, a guardrail, and a log filter. It should not ask you to choose a foundation model family or design the chunking strategy for a knowledge base. If a practice question turns into model selection, it is testing the wrong exam.

## What to do on 27 October 2026

1. Open the DVA-C03 guide from the exam page.
2. Confirm the weights in the table above. They came from the September blog. If the guide disagrees, the guide wins.
3. Diff in-scope services against `02-services/20-full-product-catalog.md`.
4. Write one scenario per new AI-security skill into `05-dva/10-dva-c03-new-skills.md` using the guide's wording as the requirement, in your own explanation.
5. If you are already scoring well on the DVA-C02 practice exam and you can sit before 30 November, book C02. The credential does not expire early.

## Study order if you are waiting for C03

Finish every DVA-C02 skill in `05-dva/`. Then add, in this order:

1. ECR build, scan, and a deploy to Fargate.
2. PrivateLink from a Lambda in a VPC to the AWS API you call, including Bedrock if you call it.
3. The five AI-security controls, with a log redaction exercise.
4. Q Developer or Kiro used to draft a test, then a human review of that test for mocked-out assertions and leaked secrets.
