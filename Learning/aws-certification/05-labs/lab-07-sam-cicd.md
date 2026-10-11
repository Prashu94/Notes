# Lab 07 — SAM, a local invoke, a deploy, a pipeline shape

DVA skills 3.1 through 3.4. You build an artifact, invoke it with a fixture, deploy it, and write the pipeline file a build service would run. You do not need a CodePipeline in this account for the exam point to land.

Install SAM CLI before you start. `sam --version`. Docker is required for `sam local`.

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
cd "$HOME"
sam init --name lab07 --runtime python3.12 --app-template hello-world \
  --dependency-manager pip --no-interactive
cd lab07
```

## 1. A fixture and a local invoke

`events/event.json` from the template is an API Gateway proxy event. Add an assertion you can see:

```bash
sam build
sam local invoke HelloWorldFunction --event events/event.json
```

The function runs in a container. It does not call your AWS account unless the code does. A unit test that only checks this output, with boto3 mocked, is skill 3.2. A test that hits the production alias is the failure mode.

## 2. Deploy

```bash
sam deploy --guided
```

Accept the defaults except: stack name `lab07`, region from your environment, confirm changes, allow SAM CLI IAM role creation, do not save the config into git if it contains an account id you would rather not commit. `samconfig.toml` is local.

When it finishes:

```bash
aws cloudformation describe-stacks --stack-name lab07 \
  --query 'Stacks[0].Outputs'
aws cloudformation describe-stack-resources --stack-name lab07 \
  --query 'StackResources[].{type:ResourceType,status:ResourceStatus,id:PhysicalResourceId}'
```

You have a stack, a function, and an API. That is CloudFormation, which SAM generated. CDK would have generated CloudFormation too. On SAA you answer CloudFormation. On DVA, SAM and CDK are both in scope.

## 3. The buildspec you would commit

Save this as `buildspec.yml` next to `template.yaml`. Do not create a CodeBuild project unless you want another thing to delete.

```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      python: 3.12
    commands:
      - pip install aws-sam-cli
  build:
    commands:
      - sam build
      - sam validate
  post_build:
    commands:
      - sam deploy --no-confirm-changeset --no-fail-on-empty-changeset --stack-name lab07
```

The deploy stage's role is not an admin role in the management account. It is a deploy role in the workload account, assumed by the pipeline. A manual approval sits in front of production. A CloudWatch alarm rolls the alias back. Those three sentences are the Professional and Developer deploy items. The YAML above is only the build.

## 4. GitHub OIDC, the trust you do not have to attach

If the runner is GitHub Actions, there is no access key in the repo. The trust policy on the deploy role looks like this. Replace the account and the repo. Do not attach it to an admin role.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:ref:refs/heads/main"
      }
    }
  }]
}
```

The action is `AssumeRoleWithWebIdentity`. The subject pins the repo and the branch. A token from another repo fails the condition. That is the item.

## 5. Canary, on paper

Publishing a version and moving an alias is the Lambda rollback. From the deployed function:

```bash
FN=$(aws cloudformation describe-stack-resource --stack-name lab07 \
  --logical-resource-id HelloWorldFunction --query StackResourceDetail.PhysicalResourceId --output text)
aws lambda publish-version --function-name "$FN" --query Version --output text
aws lambda create-alias --function-name "$FN" --name live --function-version 1
```

A CodeDeploy canary shifts `live` from the previous version to the new one, ten percent, then the rest, and an alarm sends it back. You do not have to create the deployment group to answer the item. You do have to be able to say the alias is what moves.

## Cleanup

```bash
sam delete --stack-name lab07 --no-prompts
```

Confirm `aws cloudformation describe-stacks --stack-name lab07` says the stack does not exist. Then delete the local folder if you do not want the sample app: `rm -rf "$HOME/lab07"`.
