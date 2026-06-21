# AWS CI/CD and Infrastructure as Code — DVA-C02 Guide

SAM, CloudFormation, CodePipeline, CodeBuild, CodeDeploy — packaging, testing, and deploying AWS applications.

---

## AWS SAM (Serverless Application Model)

SAM extends CloudFormation with simplified syntax for serverless resources.

### Key Resource Types

| SAM Type | Creates |
|----------|---------|
| `AWS::Serverless::Function` | Lambda + IAM role + CloudWatch log group |
| `AWS::Serverless::Api` | API Gateway REST API |
| `AWS::Serverless::SimpleTable` | DynamoDB table |
| `AWS::Serverless::LayerVersion` | Lambda layer |
| `AWS::Serverless::StateMachine` | Step Functions |

### Example Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    Runtime: python3.12
    Environment:
      Variables:
        TABLE_NAME: !Ref OrdersTable

Resources:
  OrdersTable:
    Type: AWS::Serverless::SimpleTable
    Properties:
      PrimaryKey:
        Name: PK
        Type: String

  CreateOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: orders.create
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
      Events:
        Api:
          Type: Api
          Properties:
            Path: /orders
            Method: post
```

### SAM CLI Workflow

```bash
sam build                          # Build artifacts
sam local invoke -e events/e.json  # Local test
sam local start-api                # Local API Gateway
sam deploy --guided                # Deploy to AWS
sam logs -n CreateOrderFunction --tail  # Stream logs
sam delete                         # Tear down stack
```

---

## AWS CloudFormation

- **Stack** — collection of resources defined in template
- **Change set** — preview changes before applying
- **Drift detection** — find manual changes to stack resources
- **StackSets** — deploy stacks across accounts/regions
- **Nested stacks** — modular templates

SAM templates **are** CloudFormation templates (with Transform).

### CDK Awareness

AWS CDK (Cloud Development Kit) generates CloudFormation from TypeScript/Python/Java — developer-friendly IaC. Synthesizes to CloudFormation on deploy.

---

## CodePipeline

```
┌────────┐   ┌───────────┐   ┌────────┐   ┌──────────┐
│ Source │ → │   Build   │ → │ Deploy │ → │  (Test)  │
└────────┘   └───────────┘   └────────┘   └──────────┘
 GitHub       CodeBuild        CloudFormation
 CodeCommit   sam build        CodeDeploy
 S3           npm test         Elastic Beanstalk
```

### Source Providers
- CodeCommit, S3, GitHub (via CodeStar Connections), Bitbucket, ECR

### buildspec.yml (CodeBuild)

```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      python: 3.12
    commands:
      - pip install aws-sam-cli pytest
  pre_build:
    commands:
      - pytest tests/
  build:
    commands:
      - sam build
      - sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
artifacts:
  files:
    - packaged.yaml
```

---

## CodeDeploy

### Deployment Targets

| Target | Strategies |
|--------|-----------|
| **EC2/On-premises** | In-place, blue/green |
| **Lambda** | Canary, linear (via aliases) |
| **ECS** | Blue/green with ALB traffic shifting |

### Lambda Deployment (SAM Integration)

```yaml
CreateOrderFunction:
  Type: AWS::Serverless::Function
  Properties:
    AutoPublishAlias: live
    DeploymentPreference:
      Type: Canary10Percent5Minutes
      Alarms:
        - !Ref AliasErrorAlarm
      Hooks:
        PreTraffic: !Ref PreTrafficHookFunction
        PostTraffic: !Ref PostTrafficHookFunction
```

| Preference type | Behavior |
|----------------|----------|
| `AllAtOnce` | 100% immediately |
| `Canary10Percent5Minutes` | 10% for 5 min, then 100% |
| `Canary10Percent10Minutes` | 10% for 10 min, then 100% |
| `Linear10PercentEvery1Minute` | +10% every minute |
| `Linear10PercentEvery2Minutes` | +10% every 2 minutes |

### Rollback

- **Automatic:** CloudWatch alarm triggers → CodeDeploy rolls back alias
- **Manual:** Update alias to previous version

---

## AWS Elastic Beanstalk (Awareness)

- PaaS for web applications — upload code, Beanstalk handles infrastructure
- Supports Java, .NET, Node.js, Python, Go, Docker
- **Deployment policies:** All at once, rolling, rolling with additional batch, immutable, traffic splitting (canary)
- Less exam focus than SAM/Lambda but know it exists for traditional web apps

---

## Environment Management

| Tool | Purpose |
|------|---------|
| **SAM config (samconfig.toml)** | Per-environment deploy parameters |
| **CloudFormation parameters** | Stack-level configuration |
| **SSM Parameter Store** | Runtime config values |
| **AWS AppConfig** | Dynamic config without redeployment |
| **Lambda aliases** | Environment-specific function versions |

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| IaC for serverless app | AWS SAM or CloudFormation |
| Test Lambda locally before deploy | `sam local invoke` |
| Automate deploy on git push | CodePipeline + CodeBuild |
| Zero-downtime Lambda release | Canary deployment with alias |
| Rollback failed deployment | Revert alias or CodeDeploy auto-rollback |
| Separate dev/prod config | SAM samconfig.toml or CFN parameters |
| Preview infrastructure changes | CloudFormation change set |
| Run tests in CI pipeline | CodeBuild with pytest/npm test in buildspec |

---

## Related Guides

- [Domain 3 — Deployment](domain-03-deployment.md)
- [Lambda Guide](aws-lambda-dva-c02-guide.md)
