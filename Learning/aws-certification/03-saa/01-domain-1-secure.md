# SAA-C03 Domain 1 — Design secure architectures (30%)

This is the heaviest domain. About 15 of the 50 scored items live here. A secure answer that misses the availability or cost sentence in the stem is still wrong. A cheap answer that leaves a bucket public is wrong on this domain.

Official task list and the in-scope service names: `00-start-here/04-saa-c03-exam-blueprint.md`. Mechanics: `01-foundations/02-iam-sts-identity-center-ram.md`, `04-accounts-organizations-control-tower.md`, `05-networking-foundations-for-architects.md`, `06-encryption-kms-certificates-secrets.md`, plus the security and edge chapters in `02-services/`.

Read a stem by naming the caller, the resource, and the thing that must be impossible. The option that only "works" and does not make that thing impossible loses.

## How an allow actually happens

AWS evaluates every applicable policy. One explicit deny anywhere beats every allow. After that, something must allow the call. Nothing is allowed by default except a few service-linked cases you do not design.

Order you can defend out loud:

1. Explicit deny in an SCP, a permissions boundary, a session policy, an identity policy, or a resource policy. Deny wins.
2. If the account is a member of an organization, an SCP must not block the action. SCPs do not apply to the management account. An SCP never grants. It only filters.
3. If the principal has a permissions boundary, the boundary must allow the action. A boundary does not grant either. It caps the identity policies.
4. If the caller passed a session policy to `AssumeRole`, the session policy must allow the action. It also only caps.
5. Then an allow has to exist. Same account: an identity policy or a resource policy can allow, and you still write both when the stem says "only this role." Cross account: the identity policy in the caller account and the resource policy in the owner account both have to allow. KMS adds a third: the key policy.

That is why "I added `s3:GetObject` on the role" still fails on an SSE-KMS object in another account. The bucket policy or the key policy said no, or `kms:Decrypt` was missing.

| Policy | Grants? | Typical job |
| --- | --- | --- |
| Identity policy on a user, group, or role | Yes | What this principal may do |
| Resource policy (bucket, key, queue, function, secret) | Yes | Who may touch this resource, including another account |
| SCP | No | Ceiling on a member account or an OU |
| Permissions boundary | No | Ceiling on one principal, so a delegated admin cannot create a role wider than the boundary |
| Session policy | No | Ceiling on one `AssumeRole` session |
| Service control on the management account | Does not apply | Why the management account does not run workloads |

A group is not a principal. You cannot put a group in a trust policy or a bucket principal. You attach the identity policy to the group, and the users in the group receive it.

## Task 1.1 — Who is allowed in

### People

Employees do not get an IAM user in every account. They get a permission set in IAM Identity Center, assigned to an account or an OU, mapped to a group in the corporate identity provider. MFA is turned on at that identity source. Disabling the person in the IdP is how a leaver loses access. Rotating thirty access keys is the trap.

Identity Center still creates an IAM role in the target account behind the permission set. You do not hand-build that role per account. You also do not confuse it with IAM Identity Center's older name, AWS SSO. The CLI family is still `aws sso` and `aws identitystore` in many accounts.

Use AWS Managed Microsoft AD or AD Connector when a Windows workload must join a domain: FSx for Windows File Server, RDS for SQL Server Windows auth, EC2 joined to the domain. That is a different job from "humans need the console." Humans use Identity Center federated to the existing AD or to an external SAML or OIDC IdP. Picking Managed AD for the console and nothing else is the extra directory you did not need.

An IAM user is the legacy answer. It survives only when the stem is a break-glass path you have already locked, or a system that cannot assume a role and the stem is honest about that. An access key on that user fails every "best practice" and "no long-lived credentials" stem.

### Root

The root user of an account can close the account, change the support plan, and do a few things no IAM policy can. Lock it. Hardware MFA. No access keys. No daily work. No pipeline.

In the organization management account, root is worse: SCPs do not apply to that account. A pipeline running as root there, or as an admin user there, can do things you thought the SCP had forbidden. Workloads and pipelines live in member accounts.

`aws:MultiFactorAuthPresent` is the condition on an IAM-user STS session. It is the wrong control to paste onto an Identity Center permission set and call done. Identity Center MFA is configured on the identity source.

### Applications

EC2 uses an instance profile, which is the wrapper that attaches a role. Lambda uses an execution role. ECS splits them: the execution role pulls the image and writes logs, the task role calls S3, DynamoDB, and SQS. EKS pods use a role via IRSA (`AssumeRoleWithWebIdentity`). The exam sentence is the same in every case: the compute has a role, and the AMI, the user data, the environment variable, and the repository do not contain keys.

IMDSv2 (`http-tokens required`) is the answer when the stem is SSRF against instance metadata. A hop limit of 2 is only there so a container on the instance can still reach IMDS. The role that metadata returns must still be narrow. IMDSv2 does not fix a role that can `s3:*`.

### Another account

Account A wants an object in account B.

- A role in B whose trust policy allows A, and an identity policy on the caller in A that allows `sts:AssumeRole`. This is the usual answer. Credentials stay temporary.
- Or a bucket policy in B that names the role ARN in A, and an identity policy on that role that allows `s3:GetObject`. Both sides.

If the object is SSE-KMS with a customer managed key, add `kms:Decrypt` on the caller and an allow in the key policy for that caller. AWS managed keys (`aws/s3`) are often the wrong key for cross-account, because you do not control the key policy the same way. The stem that says "another account must decrypt" wants a customer managed key.

A partner that assumes your role gets `sts:ExternalId` in the trust policy. Without it, anyone in the partner account who learns the role ARN can ask their own admin to assume it. The external id is a secret the partner sends and your trust policy requires. It is not MFA. It is not a permissions boundary.

Service-to-service writes (CloudTrail to a bucket, SNS to SQS, EventBridge to a queue) use the service principal plus `aws:SourceArn` and `aws:SourceAccount`. A bucket policy that allows `cloudtrail.amazonaws.com` with no source condition lets a trail in another account you do not own write, or worse, confuse the bucket. The condition is the exam fix.

### Many accounts

| Stem | Design |
| --- | --- |
| New company, many accounts, guardrails, least operational overhead | Control Tower. Account Factory enrolls a new account into the OUs and the baselines |
| They already have a landing zone | Extend it. Do not rip it out to install Control Tower for sport |
| Nobody in these member accounts may leave `us-east-1` and `eu-west-1` | An SCP with `aws:RequestedRegion`, attached to the OU. Exempt the global services the console needs (`iam`, `sts`, `route53`, `cloudfront`, `organizations`, billing) or you will lock the console |
| Nobody may stop CloudTrail | SCP deny on `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail`, attached to the member OUs. The trail itself should be an organization trail landing in a log-archive account |
| A team may create roles but must not create an admin role | Permissions boundary they are required to attach, plus an SCP or a condition that denies `iam:CreateRole` unless the boundary is present |
| Share a subnet, a Transit Gateway, or a license configuration with another account in the org | Resource Access Manager. RAM shares the resource. It does not copy it into the other account |

SCP example you should be able to read. It denies everything outside two Regions except the global services:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideApprovedRegions",
    "Effect": "Deny",
    "NotAction": ["iam:*", "organizations:*", "sts:*", "route53:*", "cloudfront:*", "support:*"],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": ["us-east-1", "eu-west-1"]
      }
    }
  }]
}
```

`NotAction` means "this deny applies to every action except these." Forgetting `iam:*` and `route53:*` is how a region SCP breaks the console. Attaching the SCP to the management account does nothing, because SCPs do not apply there.

### Shared responsibility, the version that answers items

| You are looking at | AWS operates | You still own |
| --- | --- | --- |
| EC2 | Hardware, hypervisor, host patching of the virtualization layer | Guest OS patches, security groups, IAM role, data on the volumes |
| Lambda | The runtime platform, the fleet, patching of the environment | Your code, the execution role, the VPC configuration if you added one, the data |
| RDS | The database engine patching if you allow the maintenance window, the Multi-AZ failover machinery | The schema, the master password or the managed secret, the security group, whether encryption was on at creation, the parameter group choices that are yours |
| S3 | Durability of the storage, the encryption capability | The bucket policy, Block Public Access, the key choice, the lifecycle, who you shared with |

"Lambda means AWS patches the OS, so we have no security work" is false. The role and the code are yours. "RDS means we do not patch" is only true for the engine when automated minor versions are on. It is never true for the security group.

## Task 1.2 — The network and the application edge

Draw this before you look at the options.

```text
Users
  -> Route 53
  -> CloudFront (ACM cert in us-east-1, WAF, Shield Standard already on)
  -> public subnet: ALB only, security group 443 from CloudFront prefix list or the internet
  -> private subnet: app, ASG, two AZs, security group allows 8080 only from the ALB security group
       default route to a NAT Gateway in the same AZ, if the app must reach the public internet
  -> data subnet: RDS, security group allows 5432 only from the app security group, no route to an IGW
Gateway endpoint for S3 and DynamoDB on the private route tables
Interface endpoints for Secrets Manager, KMS, SQS, CloudWatch Logs if the private tier must not use NAT for those APIs
```

A public subnet is a subnet whose route table has `0.0.0.0/0` to an Internet Gateway. A public IP on an instance in a private subnet does not make the subnet public, and without a route to the IGW that address still cannot speak to the internet. A private subnet that needs outbound internet gets a route to a NAT Gateway that lives in a public subnet. The NAT needs an Elastic IP. The private instances do not.

One Internet Gateway per VPC is enough. It is a horizontally scaled, highly available component. "Add a second IGW" is not the high-availability answer.

A NAT Gateway is zonal. One NAT for a Multi-AZ private fleet dies with that AZ, and the other AZ pays cross-AZ data charges to reach it. Production that must keep outbound during an AZ failure gets one NAT per AZ. A NAT instance is the old cost hack. It is a single instance you patch, and it loses to NAT Gateway on every availability stem. On a pure cost stem that accepts the operational loss, it can still appear. Prefer deleting the need for NAT (gateway endpoints, no internet) before you pick a NAT instance.

### Security groups and NACLs

Security groups are stateful. You allow inbound. The response leaves without a matching outbound rule for that flow, as long as the outbound rule allows the traffic at all. The default outbound rule allows all, which is why people forget outbound exists. Tighten outbound when the stem says the instance may call only specific endpoints.

Security groups have allow rules only. There is no deny. Reference another security group id, not a wide CIDR, for tier-to-tier traffic. The ALB security group allows 443 from the world or from CloudFront. The app security group allows the app port from the ALB security group id. The database security group allows the database port from the app security group id. A `/32` of a single instance's private IP breaks the moment the ASG replaces the instance.

NACLs are stateless and numbered. The lowest number wins. A custom NACL starts empty, which means deny, because the default final rule is deny. The default NACL of a VPC allows all, which is why a subnet you never touched is not "protected by the NACL." Use a NACL for a subnet-wide deny of a CIDR, or for a compliance rule that says the subnet may not speak to a range even if a security group is wrong. If you allow inbound TCP 443, you must also allow the return traffic to the client ephemeral ports (1024–65535) outbound, and the reverse for traffic the subnet initiates. Forgetting ephemeral ports is the outage.

| | Security group | NACL |
| --- | --- | --- |
| State | Stateful | Stateless |
| Deny rule | No | Yes |
| Attached to | An instance's elastic network interface | A subnet |
| Default | Default SG allows inbound only from itself | Default NACL allows all |
| Exam use | Normal tier isolation | Explicit deny of a CIDR, or a subnet-wide extra belt |

### Endpoints

| Private subnet must reach | Endpoint | Why the other one is wrong |
| --- | --- | --- |
| S3, DynamoDB | Gateway endpoint. Add it to the route tables. No hourly charge. A prefix-list route, not `0.0.0.0/0` | An interface endpoint for S3 exists and costs money. The exam's cost and "no internet" answer for S3 is the gateway endpoint |
| Secrets Manager, KMS, SQS, SNS, CloudWatch Logs, STS, Bedrock | Interface endpoint, private DNS enabled, security group on the endpoint that the app can reach | There is no gateway endpoint for these. A NAT also works and puts the traffic on a bill and, if you are careless, on the internet path |
| A service another team published | PrivateLink. Their NLB, your interface endpoint. You do not peer the VPCs | Peering exposes the whole CIDR |
| HTTP between accounts with IAM on the call | VPC Lattice. More of a Professional answer. Recognize it. Do not pick it for "two EC2 instances in one VPC" | |

Gateway endpoints do not use security groups. Interface endpoints do. Private DNS on the interface endpoint means the SDK's normal public hostname resolves to the endpoint inside the VPC. Without private DNS, the SDK still tries the public name and you need a NAT or a custom endpoint URL in the code.

### Edge and application threats

| Threat | Control | What does not work |
| --- | --- | --- |
| Volumetric DDoS on CloudFront or Route 53 | Shield Standard is already included | Buying Shield Advanced for a single small site with no cost-protection requirement |
| DDoS plus a response team, cost protection, and many accounts | Shield Advanced, often with Firewall Manager to roll the protections out | A security group |
| SQL injection, XSS, bad bots, a rate limit on HTTP | AWS WAF on CloudFront, ALB, API Gateway, or AppSync. Managed rule groups for the common attacks. A rate-based rule for abuse | A NACL, which cannot see the HTTP body. An NLB, which cannot host a WAF |
| WAF on the ALB, but users enter through CloudFront | The WAF never sees cache hits or requests CloudFront does not forward. Attach the web ACL to the distribution | Leaving it only on the ALB |
| Stolen SSH keys, open port 22 | Systems Manager Session Manager. The instance role needs the SSM permissions. No inbound SSH. No bastion | A bastion in a public subnet with port 22 from `0.0.0.0/0` |
| Database password in a config file | Secrets Manager, rotation turned on for RDS. The app role gets `secretsmanager:GetSecretValue` and `kms:Decrypt` if the secret uses a customer managed key | Parameter Store as a `String`. SecureString is acceptable for a secret that does not rotate. Rotation is the Secrets Manager answer |
| Sign-up, social login, a JWT for your API | Cognito user pool | An identity pool. Identity pools vend AWS credentials. Use them only when the browser itself must call S3 or DynamoDB |
| Odd API calls, crypto-mining, a credential used from a new country | GuardDuty. Enable it in every Region you use, or as an organization admin in the security account | Reading CloudTrail by hand |
| Personal data sitting in S3 | Macie | GuardDuty, which is not a data classifier |
| CVEs on EC2, ECR images, Lambda | Inspector | A manual AMI scan you will not repeat |
| One queue of findings | Security Hub, with the standards you need (FSBP is the usual baseline) | Four consoles |
| A resource was shared with the world | IAM Access Analyzer | A bucket ACL check you do once |
| "Is this configuration still true tomorrow" | AWS Config rules. Detective control. It does not stop the change by itself. An SCP or a Service Control plus a preventive IAM deny stops it | Config as a firewall |
| Who called the API | CloudTrail. Management events are the API calls. Data events are `GetObject`, `PutObject`, DynamoDB item calls. A trail of management events does not show who read the object | VPC Flow Logs, which show IPs and ports, not the IAM principal |
| Packets, not API calls | VPC Flow Logs. Traffic Mirroring only when they need the payload. Reachability Analyzer when "why can't A reach B" | CloudTrail |

Network Firewall is the VPC firewall when you need domain filtering, intrusion prevention, or a central egress inspection VPC. A security group cannot filter on a domain name. Professional stems love the inspection VPC. Associate stems mention Network Firewall when the security group and the NACL are clearly not enough.

Firewall Manager pushes WAF rules, security groups, and Shield Advanced across accounts. It is the "we have 40 accounts and the WAF is drifting" answer, not the answer for one distribution.

### Getting in from outside

| Need | Path |
| --- | --- |
| An administrator, no inbound port | Session Manager |
| A person on a laptop into the VPC | Client VPN |
| A site, encrypted, this month, modest bandwidth | Site-to-Site VPN |
| Many gigabits, stable latency, a circuit you can order | Direct Connect. One circuit is still one building. A second location or a VPN backup is the resilient design |
| Encryption on top of Direct Connect | A VPN over the Direct Connect, or MACsec where the port supports it |
| The database must not be reachable from the corporate network at all, only one API | PrivateLink for that API. Do not peer the data VPC to the office |

## Task 1.3 — Data

### Encryption at rest

| Requirement in the stem | Choice |
| --- | --- |
| "Encrypted" and nobody administers a key | SSE-S3 (`AES256`), or the AWS-managed key for that service (`aws/s3`, `aws/ebs`, `aws/rds`) |
| A key policy, a grant, the ability to disable the key, a cross-account decrypt, CloudTrail on key use | Customer managed KMS key, SSE-KMS |
| You bring the key material and AWS must not generate it | A KMS key with imported material. Automatic annual rotation does not apply the same way. You rotate by importing new material on your schedule |
| A regulatory module, FIPS, you manage the HSM | CloudHSM. It is not the default. KMS is the default. CloudHSM is the "we must control the hardware" answer |
| AWS must store ciphertext only | Client-side encryption. You lose AWS-side features that need to read the bytes, and you own the key forever |
| S3, high KMS request cost | A bucket key. It does not change who can decrypt. It changes how many KMS calls S3 makes |
| EBS | Turn encryption on by default in the account. A snapshot of an encrypted volume is encrypted. Sharing the snapshot across accounts means sharing the KMS key too |
| RDS or Aurora | Encryption is chosen at creation. There is no switch you flip on a live unencrypted instance. Snapshot, copy the snapshot with a key, restore a new instance, cut the application over |
| An object that was uploaded with SSE-S3 and must become SSE-KMS | Copy the object onto itself with the new encryption parameters. A bucket default does not rewrite old objects |

Disabling a KMS key is the incident response. Decrypt starts failing, which stops the attacker and also stops the application. Deleting a key has a waiting period (7 to 30 days). Deletion is not the first button. After the waiting period the ciphertext is unrecoverable. Rotation of a customer managed symmetric key creates new key material for new encrypt operations. Old ciphertext still decrypts with the old material. Turning rotation on does not re-encrypt the bucket.

S3 Block Public Access has four switches: block public ACLs, ignore public ACLs, block public policies, restrict public buckets. Set them at the account and on the bucket. A bucket policy with `Principal: "*"` does not make the object public while the account-level block is on. The partner fix is a role, a specific principal, or a presigned URL. Turning the block off is the trap.

Presigned URLs grant a time-limited action with the credentials of the signer. They are the "a customer uploads one object without an AWS account" answer. They are not a substitute for a bucket policy when a partner account will call the API all year.

Object ownership: Bucket owner enforced disables ACLs. New buckets should be there. An exam item about a bucket ACL granting `AllUsers` is the old world. The fix is still Block Public Access plus no public policy, and stop using ACLs.

### Retention and audit

| Stem | Control |
| --- | --- |
| Even root cannot delete this for 7 years | S3 Object Lock, compliance mode, versioning on. It must be enabled at bucket creation. Governance mode lets a principal you have allowed bypass the lock. That fails the "even root" sentence |
| Backups that survive the account being taken over | AWS Backup vault in another account, or a vault lock, or a copy into a locked bucket the application account cannot delete |
| Logs an auditor trusts | Organization CloudTrail, all Regions, log file validation, KMS, object lock or a bucket policy that denies `s3:DeleteObject` to everyone except a break-glass role in the log account |
| The SOC or ISO report | AWS Artifact. It is AWS's report. It does not certify your application |
| A private hostname on an internal ALB | AWS Private CA. Public ACM will not issue `app.corp.internal` |
| TLS on an internet ALB or API Gateway | A public ACM certificate in the same Region as the load balancer. ACM renews it if the DNS validation still works |
| TLS on CloudFront | The certificate must be in `us-east-1`, even when the origin is in `ap-southeast-2` |
| Certificate on a server you manage, not on an AWS front door | ACM Private CA, or a third-party cert you install yourself. Public ACM certificates are for services that integrate with ACM, not for exporting onto a random EC2 nginx in the default case |

Lifecycle belongs to cost as well as security. A retention rule that expires noncurrent versions is how versioning does not keep every secret you overwrote. Do not expire the only copy of an object the regulator said to keep. Object Lock and a lifecycle expiration fight. The lock wins until the retention date, which is what you want, and it is also how a lab bucket becomes undeletable. Do not enable compliance mode on a practice bucket.

## Worked scenarios

**1.** Thirty accounts. Developers have IAM users and access keys. Security wants one disable button and MFA. Identity Center, the corporate IdP, permission sets, MFA on the identity source. Rotating keys is the trap. Creating a new IAM user called `security-admin` in each account is the same trap with a cleaner name.

**2.** A private instance reads S3 through a NAT. The NAT data-processing line is most of the bill. Add an S3 gateway endpoint on that route table. Keep the NAT only if the instance still has to reach the public internet for patches or a SaaS API. "Delete the NAT and add nothing" breaks those calls. "Add an interface endpoint for S3" works and costs more than the gateway endpoint.

**3.** A bucket policy allows `Principal: "*"` and a public ACL, and the object is still not public. Account-level Block Public Access is on. Do not turn it off for a partner. Add the partner role as an explicit principal, or issue a presigned URL.

**4.** CloudFront will not attach a certificate that was requested in `ap-southeast-2`. Request it again in `us-east-1`. The ALB in `ap-southeast-2` keeps its own certificate in `ap-southeast-2`.

**5.** A Lambda role in account A reads SSE-KMS objects in account B and gets `AccessDenied`. Check, in order: the identity policy allows `s3:GetObject` and `kms:Decrypt`, the bucket policy allows that role, the key policy allows that role, and KMS key grants if you used a grant instead of the key policy. The error text is often just `AccessDenied` from S3, which hides the KMS denial. CloudTrail data events on the key show `Decrypt` denied.

**6.** An SCP denies `ec2:RunInstances` for instance types `p*` and `g*` on the sandbox OU. A developer attaches `AdministratorAccess` to a role in a sandbox account and is still denied. That is the SCP working. Moving the workload to the management account to escape the SCP is the failure. The management account is not a workaround.

**7.** Port 22 is open from the office CIDR to a bastion, and the bastion's security group allows SSH onward to the fleet. Session Manager on the instances, delete the bastion, delete port 22. The instance profile needs `AmazonSSMManagedInstanceCore` or a narrower equivalent, and the instances need a path to the SSM endpoints (NAT or interface endpoints).

**8.** The WAF is on the ALB. CloudFront caches the site. Attack traffic that is served from cache never reaches the ALB, and the WAF never sees it. Attach the web ACL to the CloudFront distribution. You can keep a second one on the ALB if origins are also reachable directly. If the origin is reachable directly, put a custom header check or an origin access control so the public cannot skip CloudFront.

**9.** RDS was created without encryption. The auditor wants it encrypted before Friday. You cannot modify the instance in place. Snapshot, copy the snapshot with a customer managed key or the AWS managed RDS key, restore, update the application endpoint, keep the old instance until the cutover is proven. The snapshot copy is the step people skip. A snapshot of an unencrypted instance is unencrypted.

**10.** A regulator says nobody, including the root user, may delete records for seven years, and the records are objects. Object Lock compliance mode. Governance mode fails because a privileged user can bypass it. Versioning is required. Enabling the lock later on an existing bucket is possible for some configurations now, but the exam story is: versioning on, compliance retention, and you cannot shorten it.

**11.** GuardDuty in one Region reports nothing, and the suspicious calls were in another Region. Detectors are Regional. Organization delegated admin plus auto-enable across Regions is the Professional shape. At Associate level, "enable GuardDuty in the Regions you use" is the answer. Security Hub is the aggregator, not the detector.

**12.** A CloudTrail trail writes to a bucket in the same account as the application, and the application role has `s3:DeleteObject` on that bucket. An attacker who steals the role deletes the evidence. Put the trail bucket in a log-archive account, deny delete with a bucket policy, turn on log file validation, and add an SCP so member accounts cannot stop the trail.

**13.** Two applications share an IAM user called `app-user` with one access key. You cannot tell which application made a call, and you cannot rotate one without breaking the other. Two roles. No shared user. CloudTrail then shows the role name.

**14.** The stem says "encryption in transit and at rest" for a public website on an ALB and S3. TLS with ACM on the ALB, and default encryption on the bucket. They did not ask for a customer managed key. SSE-S3 meets "at rest" until the stem says key policy, disable the key, or cross-account decrypt.

**15.** Macie, GuardDuty, Inspector, and Config are all enabled, and nobody reads them. Security Hub plus an EventBridge rule to the ticket system is the operational answer. Turning on a detector is not a control if the finding has nowhere to go.

## Commands

These match lab 01 and lab 03. Run them in a sandbox.

```bash
aws sts get-caller-identity
aws iam get-account-summary
aws iam list-mfa-devices --user-name "$USER"

aws iam create-role --role-name app-s3-read \
  --assume-role-policy-document file://trust.json
aws iam put-role-policy --role-name app-s3-read \
  --policy-name read-one-bucket \
  --policy-document file://permissions.json
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT:role/app-s3-read \
  --action-names s3:GetObject s3:DeleteObject

aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT:role/app-s3-read \
  --role-session-name lab \
  --external-id partner-secret

aws organizations list-policies --filter SERVICE_CONTROL_POLICY

aws ec2 modify-instance-metadata-options --instance-id "$IID" \
  --http-tokens required --http-put-response-hop-limit 2

aws ec2 create-vpc-endpoint --vpc-id "$VPC" \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway --route-table-ids "$RTB"

aws kms create-key --description app
aws kms enable-key-rotation --key-id "$KEY_ID"

aws s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws guardduty create-detector --enable
aws cloudtrail describe-trails
```

EC2 trust policy. The principal is the service, not the instance id. Any instance that is given this role's instance profile can use it, so the identity policy on the role must be narrow.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ec2.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

Cross-account trust with an external id:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::PARTNER_ACCOUNT:root" },
    "Action": "sts:AssumeRole",
    "Condition": { "StringEquals": { "sts:ExternalId": "a-long-random-value" } }
  }]
}
```

Trusting `:root` means "any principal in that account whom their own admin allows to assume this role." The external id stops the confused deputy. It does not stop the partner's admin. If the stem says "only this one role in the partner account," the principal is that role ARN, not the account root.

A minimal key policy statement that lets one role encrypt and decrypt, and lets the account's IAM still administer the key:

```json
{
  "Sid": "AllowUse",
  "Effect": "Allow",
  "Principal": { "AWS": "arn:aws:iam::ACCOUNT:role/app-s3-read" },
  "Action": ["kms:Decrypt", "kms:DescribeKey", "kms:GenerateDataKey"],
  "Resource": "*"
}
```

KMS key policies are the exception people forget: if the key policy does not allow the account root to administer the key, IAM policies in the account cannot grant key use. A key with an empty or broken policy can lock you out of the ciphertext. Always leave an admin statement.

## Exercise set

1. Who can close an account, and why is that principal a bad place to run a pipeline?
2. An SCP denies `cloudtrail:StopLogging`. A member admin has `AdministratorAccess`. Can they stop the organization trail?
3. WAF is on the ALB. Users enter through CloudFront. Where is the WAF blind, and what do you change?
4. A secret is baked into an AMI as an environment file. Name the storage, the IAM change, and the image change.
5. Object Lock governance versus compliance, for a regulator who said nobody can delete the objects for 7 years.
6. A security group allows inbound 443 from `0.0.0.0/0` on the database subnet's instances. The NACL allows all. Is the database safe? What do you change first?
7. Draw the difference between a permissions boundary and an SCP in one sentence each. Which one can stop an administrator in a member account?
8. SSE-S3, SSE-KMS, and client-side. Which one lets you disable decryption during an incident, and which one means AWS cannot read the object to run S3 Select?
9. Why does a CloudFront custom-domain certificate in `eu-west-1` fail, and where do you request it?
10. GuardDuty or Macie or Inspector: crypto-mining on an EC2 instance, a CSV of passport numbers in a bucket, a critical CVE in an ECR image. One service each.
11. The NAT Gateway is in one AZ. The private fleet is in three. What fails when that AZ fails, and what do you add?
12. A partner role has no `ExternalId`. What attack does that allow, in one sentence?
13. Config rule or SCP: you need new public buckets to be impossible, not merely detected.
14. An unencrypted RDS instance must become encrypted. List the steps. "Modify the instance and turn encryption on" is not one of them.
15. Session Manager is deployed and port 22 is still open to the world. Is the migration finished?

## Answers

1. The root user. It can do account-level actions IAM cannot, and in the management account an SCP does not apply. A pipeline assumes a role in a member account.
2. No, if that SCP is attached to the member account or a parent OU. `AdministratorAccess` cannot exceed an SCP. An SCP attached to a different OU does nothing here. The management account is not bound by the SCP, which is another reason the trail bucket should not be writable by the application account.
3. Requests served from the CloudFront cache, and any request CloudFront does not forward, never reach the ALB. Attach the web ACL to the distribution. If the ALB is also a public origin, restrict the origin so callers cannot skip CloudFront.
4. Put the secret in Secrets Manager. Grant the instance role `secretsmanager:GetSecretValue` (and `kms:Decrypt` if you used a customer managed key). Build a new AMI without the file. Terminate the instances that were launched from the old AMI. Deleting the file on a running host and leaving the AMI is how the next scale-out brings the secret back.
5. Compliance mode. Governance mode can be bypassed by a principal you have granted the bypass permission. Compliance mode cannot be shortened, including by root.
6. No. The database is on the internet if those instances have a route to an IGW and a public IP, and even without that the security group is wrong. First, remove the public route and the public IPs if they exist. Then allow the database port only from the application security group. A NACL deny of `0.0.0.0/0` on that port is the extra control, not the first design.
7. A permissions boundary caps one principal and does not grant. An SCP caps a member account or an OU and does not grant. The SCP stops the member administrator. The boundary stops only principals that have the boundary attached. Neither applies as a ceiling inside the management account for SCPs.
8. A customer managed KMS key can be disabled, which stops decrypt. Client-side encryption means AWS stores ciphertext and cannot run features that need plaintext. SSE-S3 encrypts at rest and gives you no key to disable.
9. CloudFront only accepts ACM certificates from `us-east-1`. Request the certificate there. The origin's Region does not matter.
10. GuardDuty for the mining and the suspicious instance behavior. Macie for the passport numbers in S3. Inspector for the CVE in the image.
11. Outbound internet from every private subnet dies, because those route tables point at a NAT in the failed AZ. Add a NAT Gateway in each AZ and point each private route table at the NAT in its own AZ. Also add gateway endpoints so S3 and DynamoDB do not need the NAT at all.
12. A different principal in the partner account can be allowed, by the partner's own admin, to assume your role. Anyone who can trick the partner into reusing the role ARN gets your permissions. `sts:ExternalId` makes the partner present a secret your trust policy checks.
13. The SCP, or an identity deny the admins cannot detach. A Config rule tells you after the bucket exists. Preventive, not detective.
14. Snapshot the instance. Copy the snapshot with encryption enabled and a KMS key. Restore a new instance from the encrypted copy. Point the application at the new endpoint. Keep the old instance until you have verified the new one. You cannot toggle encryption on the existing instance.
15. No. Session Manager removes the need for port 22. Until the security group and the NACL stop allowing it, the old path is still there.
