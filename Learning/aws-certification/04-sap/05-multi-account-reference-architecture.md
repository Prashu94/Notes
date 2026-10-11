# Multi-account reference architecture

SAP task 1.4. This is the picture you draw from memory.

Official: https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/organizing-your-aws-environment.html

```text
Management account
  Organizations, SCPs, billing, break-glass only
  OU Security
    Security tooling     delegated admin: GuardDuty, Security Hub, Inspector, Macie, Detective
    Log archive          org trail, Config, flow logs, Object Lock or a deny-delete bucket
  OU Infrastructure
    Network              Transit Gateway, RAM, Resolver, egress VPC, Network Firewall
    Shared services      CI/CD, golden AMIs, Private CA, Directory if Windows needs it
  OU Workloads
    Prod / Staging / Dev one account per application per environment when blast radius matters
  OU Sandbox             SCP denies expensive Regions, GPU, and leaving the allowed Regions
  OU Suspended           accounts being closed
```

## What is shared, and what is not

| Resource | Where it lives | How others use it |
| --- | --- | --- |
| Transit Gateway | Network account | RAM share. Workload accounts attach |
| Subnets for a shared VPC pattern | Network account | RAM share of subnets. Workloads launch ENIs into them |
| Resolver rules | Network account | RAM |
| GuardDuty | Security account as admin | Organization auto-enable |
| CloudTrail | Log archive bucket | Organization trail. Member accounts cannot delete it |
| Permission sets | Identity Center, usually in the management account or a delegated admin | Assigned to groups per account |
| CI/CD deploy role | Each workload account | The pipeline account is trusted to assume it. The pipeline does not use keys |
| KMS keys for logs | Log archive | Key policy allows the CloudTrail service and denies member admins `kms:DisableKey` |

Do not copy a Transit Gateway into every account. Do not put the application in the management account. Do not let the security account be the same account developers use for experiments.

## SCPs worth attaching on day one

- Deny leaving the allowed Regions, with `NotAction` for global services (`iam`, `organizations`, `route53`, `cloudfront`, `support`, `sts`).
- Deny disabling CloudTrail, GuardDuty, Config, and Access Analyzer.
- Deny root user access keys.
- Deny actions unless a required tag is present, if the organization is ready to enforce tags. A bad tag SCP locks account creation. Test it on the sandbox OU first.
- Sandbox: deny large instance families and non-approved Regions.

```bash
aws organizations attach-policy --policy-id p-xxxx --target-id ou-sandbox
aws cloudtrail create-trail --name org --s3-bucket-name log-archive-BUCKET \
  --is-organization-trail --is-multi-region-trail --enable-log-file-validation \
  --kms-key-id alias/org-trail
aws cloudtrail start-logging --name org
```

## Break-glass

A role in the management account. MFA. Credentials offline. An alarm on `AssumeRole` for that role name. Used when Identity Center is down. Not used to deploy.

## When Control Tower is the answer

New organization, least operational overhead, Account Factory, preventive and detective guardrails. When they already run a custom landing zone that expresses a guardrail Control Tower cannot, keep the landing zone and add the missing SCP. "Replace everything with Control Tower" is the trap in that stem.

## Exercise

A developer in a sandbox account launches `p5.48xlarge` in `eu-west-3`. The company standard is `us-east-1` and `us-east-2`, and sandboxes must not run GPU instances. Which two SCPs, attached where, stop this without affecting production GPU jobs in an approved Region?

Answer: a Region-deny SCP on the sandbox OU (or on the root if production is also Region-locked and the GPU jobs are already in `us-east-1` or `us-east-2`). A separate SCP that denies the GPU instance families, attached only to the sandbox OU, so production in an approved Region can still launch them. Attaching the GPU deny at the root would block production. An IAM policy in the sandbox account is weaker because an administrator in that account can detach it.

## What each account is for

Management holds Organizations and the payer bill. It does not hold workloads, because SCPs do not apply to it. Security holds delegated GuardDuty, Security Hub, Inspector, and the Config aggregator. Log archive holds the organization trail: all Regions, log file validation, a customer managed key the workload accounts cannot disable, a bucket policy that denies delete. Network holds the Transit Gateway, shares it with RAM, and owns the egress VPC where inspection and NAT live. Shared services holds the pipeline and ECR. Workload OUs split prod from sandbox so a GPU deny and a Region deny can hit one and not the other.

Identity Center permission sets are how a human gets a different role in prod than in the sandbox. The pipeline assumes a deploy role in the workload account. It does not run in the management account.

A Region-deny SCP uses `NotAction` so IAM, STS, Route 53, CloudFront, and Organizations still work. A GPU deny on `ec2:RunInstances` with a condition on `ec2:InstanceType` belongs on the sandbox OU only.

Control Tower is the answer when the organization is new and they want Account Factory and guardrails with the least operational overhead. An existing landing zone that already has the guardrail gets an SCP added. It does not get ripped out.

## More exercises

2. The trail bucket is in the application account. The application role can `s3:DeleteObject`. What is the landing-zone fix?
3. Developers have `AdministratorAccess` in every account via one permission set. How do you narrow production without creating IAM users?
4. The network account shares the Transit Gateway with the organization. Sandbox VPCs start attaching and routing to prod. What did the share and the route tables get wrong?
5. GuardDuty findings go to the management account. Why is that the wrong delegated admin?

## Answers

2. Move the bucket to the log-archive account. Deny delete in the bucket policy. Deny `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail` with an SCP on workload OUs. The application role should not be in the log account at all.
3. A second permission set that is read-only or a narrow role, assigned to the production accounts. Keep a broader set on the sandbox OU. Permission sets are the assignment. You do not need a user per account.
4. The share was too wide. Share with the workload OUs that should attach, or accept attachments and then associate them with route tables that do not propagate sandbox routes into prod. A share is not a route. A flat default route table is how the routes became the problem.
5. The management account is the org root, not the place analysts work, and it is exempt from SCPs. Delegate to the security account so a compromise of a workload does not own the detector and so analysts are not logging into the payer.
