# Domain 3: Deployment (24%) — DVA-C02

Maps to **Task 3.1** (artifacts), **Task 3.2** (testing), **Task 3.3** (automated testing), and **Task 3.4** (CI/CD).

See [CI/CD Guide](aws-cicd-dva-c02-guide.md) for full coverage.

---

## Task 3.1: Prepare Application Artifacts

### Skill 3.1.1 — Manage Dependencies

**Lambda deployment packages:**
- **Zip archive** — code + dependencies (or use Lambda layers)
- **Container image** — up to 10 GB, stored in ECR
- **Layers** — shared dependencies across functions (max 5 layers, 250 MB unzipped total)

```yaml
# SAM — separate dependencies into layer
MyLayer:
  Type: AWS::Serverless::LayerVersion
  Properties:
    ContentUri: layer/
    CompatibleRuntimes:
      - python3.12

MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Layers:
      - !Ref MyLayer
    CodeUri: src/
```

**Environment-specific config:** Use SSM Parameter Store, Secrets Manager, or AppConfig — not hardcoded in artifact.

### Skill 3.1.2 — Directory Structure (SAM)

```
my-app/
├── template.yaml          # SAM/CloudFormation template
├── src/
│   ├── handlers/
│   │   ├── orders.py
│   │   └── users.py
│   └── requirements.txt
├── layer/
│   └── python/
│       └── requirements.txt
├── events/
│   └── order-event.json   # Test events
└── tests/
    └── unit/
```

### Skill 3.1.3 — Code Repositories

- **CodeCommit** — AWS-native Git
- **GitHub / GitLab / Bitbucket** — via CodeStar Connections in CodePipeline
- Branch strategy: `main` → production, `develop` → staging, feature branches

### Skill 3.1.4 — Resource Requirements

| Service | Configurable resources |
|---------|----------------------|
| Lambda | Memory (128–10240 MB), ephemeral storage, timeout |
| ECS/Fargate | CPU, memory in task definition |
| Elastic Beanstalk | Instance type via `.ebextensions` |

### Skill 3.1.5 — AWS AppConfig

- Manage **configuration separately from code**
- Deploy config changes **without redeploying application**
- Validation, deployment strategies (canary, linear), automatic rollback
- Lambda/extension polls AppConfig for updates

---

## Task 3.2: Test in Development Environments

### Skill 3.2.1 — Test Deployed Code

```bash
# Invoke deployed Lambda
aws lambda invoke --function-name MyFunction --payload file://event.json output.json

# SAM local testing
sam local invoke MyFunction -e events/order.json
sam local start-api  # Local API Gateway at localhost:3000
```

### Skill 3.2.3 — API Gateway Stages for Testing

```
API → Stage "dev" → Deployment 1 (latest code)
    → Stage "test" → Deployment 2 (QA approved)
    → Stage "prod" → Deployment 3 (production)
```

Use **stage variables** to point to different Lambda aliases:
- `dev` stage → `$LATEST`
- `prod` stage → Lambda alias `prod` → Version 5

### Skill 3.2.4 — Deploy SAM to Different Environments

```bash
sam deploy --config-env dev     # Uses samconfig.toml [dev] section
sam deploy --config-env prod
```

```toml
# samconfig.toml
[dev.deploy.parameters]
stack_name = "my-app-dev"
parameter_overrides = "Environment=dev"

[prod.deploy.parameters]
stack_name = "my-app-prod"
parameter_overrides = "Environment=prod"
```

### Skill 3.2.5 — Test Event-Driven Applications

- Send test messages to SQS queue manually
- Use `sam local generate-event` for S3, SNS, DynamoDB events
- EventBridge: use `put_events` with test event payload
- Verify DLQ is empty after successful processing

---

## Task 3.3: Automate Deployment Testing

### Skill 3.3.1 — Test Events

```yaml
# SAM template — define test events
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /orders
            Method: post

# events/order.json for sam local invoke
```

### Skill 3.3.4 — Infrastructure as Code

| Tool | What it generates | Best for |
|------|------------------|----------|
| **CloudFormation** | Native CFN templates (JSON/YAML) | All AWS resources |
| **SAM** | CloudFormation (transforms serverless resources) | Serverless apps |
| **CDK** | CloudFormation (via synthesis) | Developers preferring TypeScript/Python/Java |

**SAM transforms:**
```yaml
Transform: AWS::Serverless-2016-10-31
# Enables AWS::Serverless::Function, ::Api, ::SimpleTable, etc.
```

### Skill 3.3.6 — Amazon Q Developer for Tests

- Generate unit tests from function code
- Exam awareness: AI-assisted test generation tool

---

## Task 3.4: CI/CD Deployment

### Skill 3.4.1 — Lambda Packaging Options

| Method | Size limit | Use case |
|--------|-----------|----------|
| Zip upload (direct) | 50 MB zipped | Small functions |
| Zip in S3 | 250 MB unzipped | Larger dependencies |
| Container image (ECR) | 10 GB | Large dependencies, custom runtime |

### Skill 3.4.2 — API Gateway Stages and Custom Domains

- **Stage** = named reference to a deployment + settings (caching, throttling, logging)
- **Custom domain** = `api.example.com` mapped to stage via ACM certificate
- **Base path mapping** = `api.example.com/v1` → prod stage

### Skill 3.4.5–3.4.8 — Deployment Strategies

| Strategy | How | Rollback |
|----------|-----|----------|
| **All-at-once** | Replace all at once | Redeploy previous version/alias |
| **Canary** | Shift traffic gradually (10% → 100%) | Stop shift; route back |
| **Blue/Green** | Two environments; switch DNS/alias | Switch alias back |
| **Linear** | Equal increments over intervals | Reverse traffic shift |
| **In-place** | Update existing instances (CodeDeploy) | Redeploy previous revision |

**Lambda canary with aliases:**
```yaml
AutoPublishAlias: live
DeploymentPreference:
  Type: Canary10Percent5Minutes  # 10% for 5 min, then 100%
  Alarms:
    - !Ref AliasErrorAlarm
```

### Skill 3.4.6–3.4.7 — CodePipeline Workflow

```
Source → Build → Deploy → (Test)
  │        │        │
GitHub  CodeBuild  CloudFormation
        npm test   (SAM deploy)
        sam build
```

**CodeBuild** `buildspec.yml`:
```yaml
version: 0.2
phases:
  install:
    commands:
      - pip install aws-sam-cli
  build:
    commands:
      - sam build
      - sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
artifacts:
  files:
    - template.yaml
```

### Skill 3.4.10 — Dynamic Deployments with Stage Variables

API Gateway stage variable `$stageVariables.lambdaAlias` passed to Lambda integration URI:
```
arn:aws:lambda:region:account:function:MyFunction:${stageVariables.lambdaAlias}
```

---

## CodeDeploy Deployment Types

| Type | Targets | Strategy |
|------|---------|----------|
| **EC2/On-premises** | EC2 instances | In-place or blue/green |
| **Lambda** | Lambda aliases | Canary or linear traffic shift |
| **ECS** | ECS services | Blue/green via ALB |

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Deploy serverless app with IaC | AWS SAM or CloudFormation |
| Zero-downtime Lambda deployment | Publish version + alias + canary |
| Test Lambda locally before deploy | SAM CLI `sam local invoke` |
| Separate config from code | AppConfig or Parameter Store |
| Automate build on git push | CodePipeline + CodeBuild |
| Rollback failed Lambda deploy | Update alias to previous version |

**Next:** [Domain 4 — Troubleshooting](domain-04-troubleshooting-and-optimization.md) | [CI/CD Guide](aws-cicd-dva-c02-guide.md)
