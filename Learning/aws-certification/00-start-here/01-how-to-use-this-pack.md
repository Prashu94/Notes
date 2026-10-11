# How to use this pack

Read this once. Then follow the study plan in `09-study-plan.md`. The pack is built so one person can sit Associate, Professional, and Developer without relearning S3 three times. Shared mechanics live in `01-foundations/` and `02-services/`. Exam-specific judgment lives in `03-saa/`, `04-sap/`, and `05-dva/`.

SAA-C03 is not optional background. It is a scored exam in this pack, with its own blueprint, domain chapters, exercises, and practice exam. Professional chapters assume you can already make the Associate choice, then they add the constraint that makes that choice wrong.

## What each file is for

Every service file in `02-services/` has the same shape:

1. **Exam weight.** Which SAP-C02 tasks and which DVA-C02 skills the service supports, and whether SAP-C03 or DVA-C03 raises the weight.
2. **When you choose it.** The requirement language that points at this service, and the nearby service that the stem is trying to tempt you with.
3. **How it actually works.** Enough mechanism that a scenario with a constraint (RPO of seconds, 10 accounts, no public internet, 50 TB, PCI, burst to zero) has one defensible answer.
4. **Commands.** AWS CLI v2 unless the tool is SAM, CDK, or the SDK. Flags that change often are called out. If a flag is uncertain, the note says to run `aws <service> help` and to read the current API reference.
5. **Exercises.** Do them before you scroll to the answers. Answers are at the bottom of the same file under `## Answers`.
6. **Official references.** Deep links into docs.aws.amazon.com, whitepapers, and decision guides.

Domain files in `03-saa/`, `04-sap/`, and `05-dva/` are the scored job. They assume you have read the related service files. They teach how to combine services under constraints. A domain file that only restates a service page is a waste of your time, so those files are scenario-first.

Labs in `05-labs/` are the proof. If you cannot make the CLI succeed, you do not know the service yet.

## Two exams, one cloud

Professional questions ask **which design meets the constraint**. They rarely ask you to write a policy document from memory, but they do expect you to recognize a broken policy, a missing SCP, a wrong endpoint type, or a DR pattern whose RPO is too loose.

Developer questions ask **which code, API, or configuration makes the application correct**. They rarely ask you to design a VPC from scratch. The DVA-C02 guide lists architecture design, pipeline design, IAM administration, OS administration, and network design as out of scope. You still must *use* IAM roles, VPC-attached Lambda, and API Gateway stages, because those are application tasks.

SAP-C03 pulls the architect toward implementation of cloud-native and AI designs. DVA-C03 pulls the developer toward containers and AI security. The overlap grows. Study the shared chapters once.

## How to read a scenario

Use the same pass on every question, in this order:

1. **Constraint.** Write down the numbers and the hard words: RTO, RPO, milliseconds, exactly once, no internet, least privilege, already using, must not change the application, 15 minutes, cross-account, PCI, retain for 7 years, cheapest, most operationally efficient.
2. **Verb.** “Most cost-effective” eliminates the design that is merely correct. “Least operational overhead” eliminates the design you would build from EC2 and cron. “Most secure” eliminates a broader IAM action that also works.
3. **Reject.** Cross out answers that violate a constraint even if the service is famous. NAT Gateway does not encrypt. A read replica is not a failover. S3 Cross-Region Replication is not a database. CloudFront does not fail over a write path by itself.
4. **Commit.** Pick the remaining answer that satisfies every constraint with the managed service AWS would rather you use.

Multiple-response items require every correct option. A half-right selection scores zero. There is no partial credit and no penalty for guessing, so on a single-answer item an educated guess beats a blank.

Unscored questions are mixed in. You cannot see which they are. Treat every question as scored. On SAP-C02, emerging AI questions are pretest and do not affect the score. On SAP-C03 those topics become part of the job. Study them either way.

## How to use the command blocks

Commands assume:

- AWS CLI version 2 (`aws --version`).
- A named profile, shown as `--profile sandbox` when the account matters. Drop the flag if you only have `default`.
- Region `us-east-1` unless the lab says otherwise. Set `AWS_DEFAULT_REGION` or pass `--region`.
- `jq` installed for the filters. On macOS, `brew install jq`.
- Placeholders in `ALL_CAPS` that you replace: `ACCOUNT_ID`, `BUCKET`, `ROLE_ARN`, `VPC_ID`.

A block you should be able to paste after substitution looks like this:

```bash
aws sts get-caller-identity --profile sandbox
aws configure get region
```

A block that is a template, not a paste, says so in the sentence above it.

## How to do the exercises

Write the answer on paper or in a scratch file. Then compare with `## Answers`. If you were wrong, write one sentence on which constraint you missed. That sentence is the study note. Re-read the service section that owns the constraint. Do not highlight the whole page.

For developer exercises, run the code. A mental model of `boto3` pagination is weaker than a script that paginates.

## What to skip

Skip a section only when the catalog file marks it **out of scope for both exams** and you are inside two weeks of a booked seat. Even then, skim the one-line “why it is out of scope” so a distractor does not lure you. Game tech (Amazon GameLift) is the only category the SAP-C02 guide explicitly parks out of scope. DVA-C02 also parks QuickSight, Chime, Connect, WorkMail, AppStream, WorkSpaces, Polly, Rekognition, Managed Services, Elastic Transcoder, Application Discovery Service, Application Migration Service, Shield Standard, Shield Advanced, Snow Family, and Storage Gateway. Those services can still appear as wrong answers. Know what they are in one sentence.

## Companion SAA-C03 folder

`../aws-sa-c03/` is a service-by-service Associate pack: IAM, VPC, S3, EC2, RDS, Aurora, DynamoDB, and the rest, plus seven practice tests. Use it when a Professional or Developer chapter assumes a mechanism you cannot explain yet (for example, security group versus network ACL state, or S3 storage classes). This pack repeats the mechanism when the Professional or Developer exam tests a harder version of it. It does not paste that folder.

## A week that works

Five days of 90 minutes beat a Sunday of eight hours.

| Day | Block |
| --- | --- |
| 1 | One foundation or service chapter. Do the exercises closed-book. |
| 2 | The lab that matches that chapter, or the design lab if the service costs money. |
| 3 | Next chapter. |
| 4 | Next chapter, plus 10 review cards from earlier traps. |
| 5 | Domain scenario set from `03-saa/`, `04-sap/`, or `05-dva/`. |
| 6 | Weak objective from the map. One page of commands from `06-reference/command-index.md`. |
| 7 | Off, or a timed 20-question slice. |

In the last 10 days, stop adding new services. Run the practice exam in this pack timed, then the official AWS practice exam, then repair only the objectives you missed.

## Tools to install before week 1

```bash
aws --version          # expect aws-cli/2.x
sam --version          # AWS SAM CLI
python3 --version      # 3.11 or newer is comfortable
node --version         # current LTS if you do the JavaScript SDK exercises
jq --version
docker --version       # SAM local and container labs
git --version
```

Optional, for the CDK lab:

```bash
npm install -g aws-cdk
cdk --version
```

Configure a sandbox profile:

```bash
aws configure --profile sandbox
# AWS Access Key ID, secret, region, output json
aws sts get-caller-identity --profile sandbox
```

Prefer IAM Identity Center (`aws configure sso`) for any account you will keep. Long-lived access keys are a lab convenience and a production defect. The developer security chapter shows both, and it shows why the key pair loses.

## Files to open on exam morning

- `06-reference/decision-trees.md`
- `06-reference/exam-traps.md`
- The one-page logistics table in the root `README.md`
- Your own list of missed constraints from the practice exams

Leave the long service chapters closed. If you are still reading Kinesis internals on exam morning, you are not ready, and reading more will not fix that in an hour.
