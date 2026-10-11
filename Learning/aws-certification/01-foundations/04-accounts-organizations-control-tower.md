# Accounts, Organizations, and Control Tower

SAA 1.1. SAP 1.4, and every stem that says "the company has many accounts." DVA does not administer this. A developer still deploys into an account that already has an SCP, and the deploy fails until someone reads the deny.

Official:

- https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html
- https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html
- https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/organizing-your-aws-environment.html
- https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html
- https://docs.aws.amazon.com/ram/latest/userguide/what-is.html

## Why more than one account

An account is a hard boundary for privileges, blast radius, and the bill. One account for the whole company fails when a lab user can touch production, when a compromised app role can read every bucket, or when finance cannot tell which product spent the money.

| Account | What is inside | Who can log in |
| --- | --- | --- |
| Management | Organizations, consolidated billing, SCPs. Almost no workloads | Break-glass only |
| Log archive | CloudTrail, Config history, flow logs. Bucket policy denies delete | Security, and even they should not delete |
| Security tooling | GuardDuty, Security Hub, Detective, Inspector, delegated admin | Security |
| Network | Transit Gateway, RAM shares, egress VPC, Route 53 Resolver | Network team |
| Shared services | CI/CD, golden AMIs, Private CA, Directory | Platform team |
| Workload prod / test / dev | The application, one environment per account when you can | The team that owns it, through Identity Center |
| Sandbox | Experiments. SCP denies expensive Regions and large instances | Everyone, with a budget |

Consolidated billing: one payer, volume discounts across member accounts, Cost Explorer at the org. It does not by itself tag the spend. Activate cost allocation tags and deliver a Cost and Usage Report to the log or finance account.

## Organizations objects

| Object | Use |
| --- | --- |
| Root | The top. One. SCPs attached here hit every member |
| OU | A folder of accounts. Nest them. SCPs inherit down |
| Account | A member. Created by Organizations or invited |
| SCP | A policy that sets the maximum API surface |
| Tag policy | Required tag keys and allowed values |
| Backup policy | A backup plan applied across accounts |
| AI services opt-out policy | Stops content from being used to improve AWS AI services. Relevant to the DVA-C03 privacy skill and to SAP-C03 |

```bash
aws organizations describe-organization
aws organizations list-roots
aws organizations list-organizational-units-for-parent --parent-id r-xxxx
aws organizations list-accounts
aws organizations create-account --email new-prod@example.com --account-name prod-orders
aws organizations enable-policy-type --root-id r-xxxx --policy-type SERVICE_CONTROL_POLICY
aws organizations create-policy --name deny-regions --type SERVICE_CONTROL_POLICY --content file://scp.json
aws organizations attach-policy --policy-id p-xxxx --target-id ou-xxxx
```

`create-account` is asynchronous. Poll `describe-create-account-status`. The new account root email must be unique.

An SCP that denies every Region except two:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOtherRegions",
    "Effect": "Deny",
    "NotAction": [
      "iam:*", "organizations:*", "support:*", "sts:*",
      "route53:*", "cloudfront:*", "budgets:*", "ce:*"
    ],
    "Resource": "*",
    "Condition": {"StringNotEquals": {"aws:RequestedRegion": ["us-east-1", "us-east-2"]}}
  }]
}
```

Global services must sit in `NotAction` or you will lock yourself out of IAM. Test an SCP on a single sandbox OU before the root.

## Control Tower

Control Tower is a landing zone on top of Organizations: Account Factory, a dashboard, and guardrails.

| Guardrail | Implementation | What the stem says |
| --- | --- | --- |
| Preventive | SCP | "Must not be able to disable CloudTrail" |
| Detective | AWS Config rule | "Must detect public buckets" |
| Proactive | CloudFormation hook | "Must block a non-compliant stack before it creates resources" |

"Least operational overhead" plus a new multi-account company is Control Tower. "We already have a custom landing zone and a guardrail Control Tower cannot express" is Organizations plus your own SCPs and Config rules. Do not rip out a working landing zone because Control Tower exists.

Account Factory vends accounts into an OU with the guardrails of that OU. Customizations use Customizations for Control Tower (CfCT) or Account Factory for Terraform. You do not hand-create forty accounts in the console.

## Delegated administrator

The management account should not run GuardDuty. You delegate:

```bash
aws organizations enable-aws-service-access --service-principal guardduty.amazonaws.com
aws guardduty enable-organization-admin-account --admin-account-id 222233334444
```

The same pattern exists for Security Hub, Inspector, Macie, Config, CloudTrail (organization trail is configured from a delegated admin in current accounts), Firewall Manager, and IAM Identity Center. The exam phrase is "delegated administrator in the security account."

## Organization trail and central logs

One trail, all Regions, all accounts, log file validation, KMS encryption, delivered to the log-archive bucket. The bucket policy allows the CloudTrail service principal with `aws:SourceArn` bound to the trail. Member accounts cannot delete the trail if the SCP denies `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail`.

Config aggregator in the security account sees resource compliance across the org. Config itself records history. It does not block an API call. An SCP blocks. A Config rule plus an SSM Automation document remediates after the fact.

## Break-glass

A role in the management account, long session discouraged, MFA, the credentials offline, CloudWatch alarm on `AssumeRole` for that role name. You use it when Identity Center is down. You do not use it to deploy the application.

## Exercises

1. A member account administrator cannot create a CloudTrail. The identity policy is `AdministratorAccess`. Where do you look first?
2. Finance wants one bill and per-team cost. Name the two features beyond "we have Organizations."
3. Security wants GuardDuty in every new account without anyone logging into the management account to read findings. What do you configure?
4. A sandbox OU must be unable to launch GPU instances. SCP or IAM policy in each account?
5. Control Tower detective guardrail versus preventive. A public S3 bucket already exists. Which guardrail type notices it, and which type would have blocked `s3:PutBucketPolicy` if you had written it that way?

## Answers

1. SCPs on the account and its parent OUs, then a permissions boundary on the role. `AdministratorAccess` does not beat an SCP.
2. Consolidated billing is already there. Add activated cost allocation tags and a Cost and Usage Report.
3. Enable GuardDuty organization-wide and set the security account as the delegated administrator.
4. An SCP on the sandbox OU. An IAM policy in each account depends on someone remembering to attach it. The SCP is the ceiling.
5. A Config rule (detective) sees the existing bucket. An SCP (preventive) would have denied the API if the action was in the deny. Detective controls do not travel backward and undo a bucket that is already public unless you add a remediation action.

## The accounts, by job

| Account | What lives there | What must not |
| --- | --- | --- |
| Management | Organizations, billing, the root of the OU tree | Workloads, pipelines, data buckets. SCPs do not apply here |
| Security | Delegated admin for GuardDuty, Security Hub, Inspector, Detective, Macie. Config aggregator | Application deploys |
| Log archive | The organization trail bucket, Object Lock or a deny-delete policy | Roles from workload accounts that can delete objects |
| Network | Transit Gateway, RAM shares, Direct Connect, the egress VPC | Application data |
| Shared services | Pipeline, ECR, golden AMIs | The organization root |
| Workloads | The stacks, split by prod and non-prod OUs | IAM users for staff |

Control Tower builds this landing zone. Account Factory enrolls a new account into the OUs and the baselines. If a landing zone already exists and expresses a guardrail Control Tower cannot, extend it. Replacing it for sport is the trap.

The default `FullAWSAccess` SCP allows everything. A deny-list adds specific denies and is how most zones start. An allow-list (detach FullAWSAccess, allow only named services) is tighter and can lock every member account, including the one you would use to fix it. The management account still works. That is your recovery path.

Region deny SCPs need `NotAction` exemptions for global services (`iam`, `sts`, `route53`, `cloudfront`, `organizations`, support, billing) or the console breaks. GPU denies belong on the sandbox OU, not on the root, if production is allowed to run those families.

Delegated administrators keep the security team out of the management account. Findings and the trail are not the same account: investigators should not be the people who can delete the log.

## More exercises

6. A pipeline in the management account uses an administrator role. Why does an SCP that denies `iam:CreateUser` not stop it?
7. Account Factory creates an account in the prod OU. GuardDuty is missing. What was not turned on?
8. You detach `FullAWSAccess` and attach an SCP that allows only S3. What happens to member accounts, and where can you still sign in to fix it?
9. Cost allocation tags exist on resources. Finance cannot group the CUR. What was skipped?
10. Break-glass is used every Friday to deploy. What is wrong with that, beyond the missing alarm?

## Answers

6. SCPs do not apply to the management account. Move the pipeline to a member account. The SCP then applies to the deploy role there.
7. Organization GuardDuty with auto-enable, and the security account as delegated administrator. Account Factory enrolls the account. It does not replace a detector you never enabled for the organization.
8. Member accounts can call S3 and almost nothing else, including the APIs you need to put the SCP back, if you are in a member. Sign in to the management account, which SCPs do not affect, and restore `FullAWSAccess` before you try a narrower allow-list again.
9. Activation in the payer account's billing console. Tags on resources do not become cost dimensions until then, and they do not backfill earlier months.
10. Break-glass is for when Identity Center is down. A weekly deploy means the normal permission set is missing and the offline credential is now a shared admin password. Give the deploy role a pipeline. Alarm the break-glass role. If it fires every Friday, the design is wrong.
