# Security services: Security Hub, GuardDuty, Inspector, Macie, Detective

SAA 1.2. SAP 1.2 and 3.2. DVA does not administer these. A developer still reads a finding that names their role.

Official:

- https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html
- https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html
- https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html
- https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html
- https://docs.aws.amazon.com/detective/latest/userguide/what-is-detective.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html

## Do not swap them

| Service | It watches | It does not |
| --- | --- | --- |
| GuardDuty | CloudTrail, VPC flow, DNS, S3 data events, EKS audit, malware on volumes. Findings are behavior | Patch the CVE. That is Inspector |
| Inspector | CVEs on EC2, ECR images, Lambda. Continuous | Tell you an instance is mining bitcoin. That is GuardDuty |
| Macie | Sensitive data in S3. PII discovery | Stop a DDoS |
| Security Hub | A place findings land. Standards such as FSBP. A score | Replace the detectors |
| Detective | A graph of who talked to whom after a finding | The detector itself |
| Access Analyzer | Resources shared outside the zone of trust. Unused access. Policy generation | Runtime malware |
| Config | Whether a resource drifted from a rule | The attacker behavior |
| Firewall Manager | Push WAF, Shield Advanced, security groups, Network Firewall across the org | Detect a mined credential |
| Audit Manager | Evidence for an audit | Block an API |
| Artifact | AWS's own compliance reports | Make you compliant |

Organization pattern: delegated administrator in the security account, auto-enable in new accounts, EventBridge rule to a ticket or to chat, an SCP that denies disabling the detector.

```bash
aws guardduty create-detector --enable
aws guardduty enable-organization-admin-account --admin-account-id 222233334444
aws inspector2 enable --resource-types EC2 ECR LAMBDA
aws macie2 enable-macie
aws securityhub enable-security-hub --enable-default-standards
```

Suppression rules are for findings you have accepted. They are not the remediation. Remediation is a tighter role, a closed security group, a patched image, or a disabled key.

GuardDuty S3 protection and malware protection are features you turn on. "We enabled GuardDuty" does not mean every protection is on. Read the finding type. `Recon:EC2/PortProbeUnprotectedPort` is not the same action as `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration`.

## Exercises

1. The stem says "find buckets that contain card numbers." Which service, and which service is the trap?
2. ECR images must fail a pipeline when a critical CVE appears. Which service produces the finding, and where does the build learn about it?
3. Forty accounts, one security team, findings in forty consoles. What do you change?
4. A finding says a role was used from an unusual country. You need the API calls that role made in the following hour. GuardDuty or Detective or CloudTrail?

## Answers

1. Macie. GuardDuty is the trap. GuardDuty can watch S3 API behavior. It does not classify the object contents the way Macie does.
2. Inspector (enhanced scanning). CodeBuild or the pipeline reads the finding and exits non-zero. Security Hub can aggregate it. The build still has to fail on purpose.
3. Delegated admin and Security Hub aggregation. An SCP so members cannot disable GuardDuty.
4. CloudTrail has the API record. Detective helps you pivot across resources if it is enabled. GuardDuty raised the finding and does not replace the trail.

## What each service sees

| Service | It watches | It does not |
| --- | --- | --- |
| GuardDuty | CloudTrail management events, VPC flow logs, DNS logs, and the protections you enabled (S3 data events, EKS, malware, RDS login). It produces a finding when the behavior looks like recon, credential theft, or cryptomining | It does not read the bytes of an object and say "this is a passport." It does not scan a container image for CVEs |
| Macie | S3 object contents and bucket configuration, looking for sensitive data | It does not tell you an instance is mining. It is not cheap to point at every object in a huge bucket. Scope the buckets |
| Inspector | CVEs and network reachability on EC2, Lambda, and ECR images. Enhanced scanning is the ECR path | It does not aggregate the other tools. A pipeline has to read the finding and fail |
| Security Hub | Findings from the others, plus standards such as Foundational Security Best Practices and CIS. One inbox | It is not a detector. Turning it on without GuardDuty and Inspector leaves an empty inbox |
| Detective | A graph of behavior after a finding, so you can pivot from a role to the instances and the API calls | It does not raise the original finding. It has to be enabled before the incident if you want the history |
| Config | Whether a resource still matches a rule. Drift. Optional remediation through SSM | It is not an IDS. A rule that fires an hour later is detective, not preventive |
| Access Analyzer | A resource policy that shares with the outside, unused access, a generated policy | It is not Macie and it is not GuardDuty |
| CloudTrail | The API call, the principal, the source IP, the error code | Not packet payloads. Not "is this CVE present" |

"We turned GuardDuty on" means a detector in that Region. Detectors are Regional. An organization delegated administrator in the security account, with auto-enable for new accounts and new Regions, is the Professional answer. The management account is the wrong place to operate the detector, and a workload account is the wrong place because the workload admin can be the attacker. An SCP that denies `guardduty:DeleteDetector` and the disable APIs stops a member admin from turning it off. The same pattern fits Security Hub and Config.

Findings that nobody reads are not a control. EventBridge on the finding, filtered by severity, to a ticket or to SNS. A chat channel that receives every low finding is how the high finding is missed. Security Hub custom actions and automation rules are the at-scale version.

## How a finding becomes an action

GuardDuty finding `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration` means credentials from an instance were used from outside AWS. The response is: revoke the session, scope the role down, turn on IMDSv2 if it was v1, and read CloudTrail for what the credentials did. Quarantining the instance before you snapshot it for forensics is a runbook, not a product. Detective helps the pivot if it was already enabled. Macie is the wrong tool.

Inspector finding on an ECR image: the pipeline's job is to fail the promotion. Scanning in the account after the image is already in production is late. Scan on push, and block the deploy on critical.

Macie finding on a bucket: the bucket should not have been public, and the data should have been encrypted, and the prefix should have been limited. Macie is how you discovered it. Block Public Access and the bucket policy are how you stop the next one. A Config rule can catch the public setting faster than a content scan.

Config plus SSM remediation is "detective and then corrective." It is slower than an SCP. Use it for "versioning must be on," where a remediation can enable versioning. Use an SCP for "this API is forbidden."

## Multi-account

Delegated admin: GuardDuty, Security Hub, Inspector, Detective, Macie. The security account. Member accounts are enrolled automatically. Findings aggregate to Security Hub in that account, or to a finding aggregator Region. CloudTrail is an organization trail into the log-archive account, which is a different account from the security account so the people who investigate are not the people who can delete the log. That split is the landing-zone answer.

Firewall Manager is the related control when the problem is "forty accounts, forty different WAF web ACLs." It is not a detective product. It pushes a policy.

## More exercises

5. GuardDuty is enabled in `us-east-1`. The suspicious call was in `eu-west-1`. Why is the console empty?
6. A member admin disables GuardDuty. Which control would have made that API fail?
7. The pipeline must fail on a critical image CVE. Inspector is enabled. The image still deploys. What did the pipeline not do?
8. Config reports an unencrypted volume an hour after it was created. The stem says unencrypted volumes must be impossible. Config or an account setting?
9. You need the principal that called `DeleteTrail`. Which of these four is the source: GuardDuty, Macie, Flow Logs, CloudTrail?

## Answers

5. The detector in `eu-west-1` was never turned on, or the organization auto-enable did not include that Region. Findings do not cross Regions by themselves. Enable the detector there, or fix the organization configuration.
6. An SCP on the member OU denying the GuardDuty disable and delete actions. The delegated admin in the security account can still manage it. `AdministratorAccess` in the member account does not beat the SCP.
7. It never read the Inspector finding. Enabling the scanner does not change the deploy step. The build has to query the finding and exit non-zero, or a pipeline stage has to block promotion.
8. The account setting "encrypt EBS volumes by default," plus a customer managed or AWS managed key. Config told you after the fact. The setting stops the next volume. Existing volumes are still a snapshot-and-copy job.
9. CloudTrail. GuardDuty might raise a related finding later. Macie does not see the control-plane call. Flow logs do not have a principal. The trail has to exist, ideally in another account, or the deletion of the trail is the last event you will ever see in that account.
