# Lab 09 — Multi-account design, and an SCP you might attach

SAP task 1.4. Most of this lab is a design you can defend on a whiteboard. The JSON at the bottom is real. Attach it only in an organization you created for practice, and only to a sandbox OU that does not contain the management account.

An SCP does not grant access. It is a ceiling. The management account is not affected by SCPs. A deny in an SCP wins against an allow in an identity policy. There is no SCP that can block the management account, which is why the management account does not run workloads.

## The accounts

| Account | What lives there | What must not |
| --- | --- | --- |
| Management | Organizations, billing, the root of the OU tree | Workloads, pipelines, buckets of data |
| Security | CloudTrail organization trail, GuardDuty delegated admin, Security Hub, Config aggregator | Application deploys |
| Log archive | The trail bucket, Object Lock if a regulator asked | Application roles that can delete objects |
| Network | Transit Gateway, RAM shares, egress VPC, Resolver | Application data |
| Shared services | Pipeline, ECR, golden AMIs, Identity Center delegated admin if you moved it | The organization root |
| Workload prod, workload dev | The application stacks | IAM users for staff. Humans come from Identity Center |

Control Tower is the product that builds this landing zone. You do not click through Control Tower for practice. You do need to know Account Factory is how a new account arrives with the baseline, and that an SCP on the OU still applies after Account Factory is done.

## Read-only checks

These are safe in any account. `describe-organization` fails if the account is not in an organization. That failure means you stop before the attach step and you still finish the design section.

```bash
export AWS_PROFILE=sandbox
aws organizations describe-organization
aws organizations list-roots
aws organizations list-policies --filter SERVICE_CONTROL_POLICY
```

## The region-deny SCP

Denies every action outside three Regions, with the exceptions AWS itself needs so that global services keep working. Confirm the condition keys against the current Organizations SCP examples before you attach this in an account you care about. The exam answer is the shape: `aws:RequestedRegion` plus a deny, and an exemption for the services that are global.

```bash
cat > /tmp/lab09-region-deny.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideApprovedRegions",
    "Effect": "Deny",
    "NotAction": [
      "iam:*",
      "organizations:*",
      "support:*",
      "sts:*",
      "route53:*",
      "cloudfront:*",
      "budgets:*",
      "ce:*"
    ],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": ["us-east-1", "us-west-2", "eu-west-1"]
      }
    }
  }]
}
EOF
```

CloudFront and IAM are global. A region deny that forgets them breaks the console. That is a Professional trap.

## The sandbox GPU deny

Attach this only to the sandbox OU. Production can still launch the instances it was allowed to launch. The sandbox OU cannot, even if someone attaches `AdministratorAccess` to a role there.

```bash
cat > /tmp/lab09-gpu-deny.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyGpuFamiliesInSandbox",
    "Effect": "Deny",
    "Action": "ec2:RunInstances",
    "Resource": "arn:aws:ec2:*:*:instance/*",
    "Condition": {
      "StringLike": {"ec2:InstanceType": ["p*", "g*", "inf*"]}
    }
  }]
}
EOF
```

## Attach, only if this is a sandbox organization

```bash
# STOP if the organization contains production.
ROOT=$(aws organizations list-roots --query 'Roots[0].Id' --output text)
# Create a sandbox OU if you do not already have one.
SANDBOX_OU=$(aws organizations create-organizational-unit \
  --parent-id "$ROOT" --name lab09-sandbox \
  --query OrganizationalUnit.Id --output text)

POL=$(aws organizations create-policy --name lab09-region-deny \
  --type SERVICE_CONTROL_POLICY \
  --content file:///tmp/lab09-region-deny.json \
  --query Policy.PolicySummary.Id --output text)

aws organizations attach-policy --policy-id "$POL" --target-id "$SANDBOX_OU"
```

Move a member account into that OU and try `aws ec2 describe-instances --region ap-southeast-2` with credentials from that member. The management account will still succeed. That contrast is the whole lab.

## Cleanup

```bash
aws organizations detach-policy --policy-id "$POL" --target-id "$SANDBOX_OU"
aws organizations delete-policy --policy-id "$POL"
aws organizations delete-organizational-unit --organizational-unit-id "$SANDBOX_OU"
rm -f /tmp/lab09-region-deny.json /tmp/lab09-gpu-deny.json
```

Delete the OU only after it contains no accounts. If you moved a member in, move it back to the root first.
