# Deployment: CloudFormation, CDK, SAM, CI/CD

SAA answers CloudFormation and refuses to make you design CodePipeline. CDK is out of scope on the SAA guide and in scope on DVA. SAP task 2.1 and DVA domain 3 both live here. SAP-C03 adds image scanning and multi-account pipelines.

Official:

- https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html
- https://docs.aws.amazon.com/cdk/v2/guide/home.html
- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html
- https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html
- https://docs.aws.amazon.com/codedeploy/latest/userguide/welcome.html

## What you are choosing

| Tool | You write | It produces |
| --- | --- | --- |
| CloudFormation | YAML or JSON | A stack. Drift detection. Change sets. Stack policies. StackSets across accounts |
| CDK | TypeScript, Python, Java, Go, C# | A CloudFormation template. `cdk diff` before you deploy |
| SAM | A short template for functions, APIs, tables | A CloudFormation stack, plus `sam build` and `sam local` |
| Elastic Beanstalk | The app and option settings | The ASG, the load balancer, the platform |
| Console clicks | Nothing repeatable | A snowflake. The exam rejects this when they say "repeatable" |

StackSets with service-managed permissions deploy into OUs. That is the Professional "every new account gets a baseline" tool, next to Control Tower.

A change set shows the replacement of a database before you execute it. A stack policy can prevent an update from replacing the table. Deletion policy `Retain` keeps the bucket when the stack goes away. `DeletionPolicy: Snapshot` on RDS is the difference between a mistake and a resume-generating event.

Drift is the console edit somebody made. Detect it. Do not ignore it and then wonder why the next deploy fails.

## Pipeline shape

Source (GitHub, GitLab, CodeCommit if it is already there) to CodeBuild to a deploy stage. The pipeline role in a shared account assumes a deploy role in the workload account. OIDC from GitHub Actions is the same idea without a long-lived key. A manual approval stage sits in front of production. An alarm rolls the deploy back.

CodeBuild `buildspec.yml` installs, tests, and synthesizes. Fail the build when Inspector or a dependency scan reports a critical finding. That is the SAP-C03 and DVA-C03 pipeline-scanning skill.

CodeArtifact holds the language packages so the build does not pull untrusted public packages at random during the production deploy.

## CodeDeploy strategies

| Strategy | Where it fits | Rollback |
| --- | --- | --- |
| All-at-once | Dev | Redeploy the old revision |
| Rolling | A fleet that can be mixed for a while | Stop and redeploy |
| Blue/green | ECS, Lambda, EC2 behind a load balancer. Two copies, then the listener moves | Send the listener back. The old copy is still there |
| Canary | A slice, then the rest, with an alarm | Automatic when the alarm fires |
| Linear | Even steps of traffic | Same |

Lambda: publish a version, point an alias, shift traffic on the alias. `$LATEST` is not a production target.

## AppConfig

Application, environment, configuration profile, deployment strategy with a bake time. Change a flag without a new artifact. DVA skill 3.1.5. A bad flag still needs a rollback strategy. Bake time is that strategy.

## Commands

```bash
aws cloudformation deploy --template-file template.yaml --stack-name orders --capabilities CAPABILITY_IAM --parameter-overrides Env=prod
aws cloudformation create-change-set --stack-name orders --change-set-name review --template-body file://template.yaml
aws cloudformation describe-stack-events --stack-name orders
sam build && sam deploy --config-env prod
cdk diff && cdk deploy
```

`CAPABILITY_NAMED_IAM` when the template names a role. `--no-execute-changeset` when you want to look first.

## Multi-account

The pipeline does not live in the management account. It lives in shared services. It cannot use `AdministratorAccess`. The deploy role allows `cloudformation:*` on the application stacks and nothing else. SCPs still apply. A deploy that worked in dev and fails in prod is often an SCP or a missing KMS grant, not a bad template.

## Exercises

1. A template update would replace the production Aurora cluster. What do you look at before you execute, and what policy stops a careless update later?
2. GitHub must deploy without an access key in the repo. What identity flow?
3. Half the Lambda traffic should move to the new version for ten minutes. Which two Lambda objects, and which service shifts the weight?
4. Why is CDK listed out of scope for SAA and in scope for DVA, and what do you answer on SAA when the options are CDK and CloudFormation?

## Answers

1. A change set. Then a stack policy that denies replacement of the cluster, and `DeletionPolicy: Retain` or snapshot so a stack delete is not a data delete.
2. GitHub OIDC to `AssumeRoleWithWebIdentity`, or a CodePipeline source connection. No static key.
3. A published version and an alias. CodeDeploy canary on that alias, with a CloudWatch alarm.
4. The SAA guide lists CDK out of scope. The DVA guide lists it in scope. On SAA you pick CloudFormation. On DVA, CDK is acceptable because it deploys CloudFormation and the developer wrote it.

## CloudFormation, the objects that prevent a bad update

A stack is a set of resources with a template. Parameters take input. Mappings are static lookups. Conditions include or skip resources. Outputs publish names other stacks read. `Fn::GetAtt` and `Ref` are how resources point at each other. A change to a property that cannot be updated in place causes replacement: CloudFormation creates the new resource, swaps, and deletes the old. For a database or a bucket, replacement is data loss unless `DeletionPolicy` is `Retain` or `Snapshot` and you meant to migrate.

A change set shows that replacement before you execute. A stack policy can deny updates to the database resource so a careless template cannot replace it. Drift is a console edit the template does not know about. Detect it. The next update will fight it or silently adopt a difference you did not intend. `CAPABILITY_IAM` and `CAPABILITY_NAMED_IAM` are required when the template creates roles. They are not a security control. They are an acknowledgement.

StackSets deploy the same template into many accounts and Regions. Service-managed permissions target an OU, so a new account receives the baseline. The pipeline's own admin role is not what StackSets use in the workload account. A deploy role is.

## CDK and SAM

CDK code synthesizes a CloudFormation template. `cdk diff` is the review. The bootstrap stack in the account holds the assets bucket and the deploy roles. Constructs are the libraries. The exam does not ask you to write a construct. It asks you to know that CDK is CloudFormation plus a language, that it is out of scope on the SAA guide, and that a diff still happens before deploy.

SAM is a CloudFormation transform for functions, APIs, and tables. `sam build` produces the artifact. `sam local invoke` runs a fixture. `sam deploy` creates or updates the stack. A `Globals` section sets the runtime once. Policies in the template should name actions, not `*`. The generated function name and the alias are what the pipeline promotes.

## The pipeline

Source, build, test, approve, deploy. CodePipeline orchestrates. CodeBuild runs `buildspec.yml`: install, test, synthesize, fail on a critical scan. CodeDeploy shifts traffic: all-at-once, rolling, blue/green, canary, linear. Lambda and ECS have deployment configurations that understand aliases and target groups. A hook that returns non-zero fails the deployment. An alarm can fail it and roll it back.

The build role can read the repo and write artifacts. The deploy role in the workload account can update the application stacks. Neither is `AdministratorAccess` in the management account. GitHub Actions uses OIDC: the trust policy allows `AssumeRoleWithWebIdentity` and the `sub` claim pins the repository and the branch. A long-lived key in the repo is the defect. CodeArtifact holds language packages so production builds do not pull untrusted public versions at random. A lockfile is the application-side version of that.

AppConfig deploys a configuration change with a bake time, separate from the artifact. A bad flag rolls back during the bake. A feature flag edited by hand in production has no bake.

Promote the same artifact from test to prod. Rebuilding in prod "to pick up a patch" produces a zip nobody tested. Patch by rebuilding in the pipeline and promoting again.

## More exercises

5. The change set says `Replace` on `AWS::RDS::DBInstance`. The template only changed a tag. What do you suspect, and what do you do?
6. A StackSet targets the workload OU. A new account is created later. What has to be true for the baseline to appear without a human?
7. CodeDeploy canary moves 10 percent, the alarm fires, and the old tasks are already gone. Which deployment configuration did you actually use?
8. The buildspec runs `npm install` against the public registry during the production deploy. What do you put in the account so the packages are known?
9. SAA stem: "repeatable infrastructure, least manual work," and the options include CDK and CloudFormation. Which do you pick?

## Answers

5. A property that forces replacement changed, or the logical id was renamed, which CloudFormation treats as delete plus create. Revert the logical id. Do not execute. Confirm `DeletionPolicy` before any future replacement you actually intend.
6. Service-managed permissions and automatic deployment enabled for the OU. A self-managed StackSet that lists account ids will not notice the new account until someone adds the id.
7. A configuration that terminated the old tasks before the canary finished, or an all-at-once deploy you called a canary. A real canary keeps the old version until the bake succeeds. On Lambda that means the previous version still has the alias weight available to shift back.
8. CodeArtifact, and a build that installs from it. The public registry remains the upstream you vet, not the URL production resolves on every deploy.
9. CloudFormation. CDK is listed out of scope on the SAA guide even though it deploys CloudFormation. On DVA and on SAP, CDK is a normal answer when the team writes it and the pipeline shows the diff.
