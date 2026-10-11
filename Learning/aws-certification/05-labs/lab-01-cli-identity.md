# Lab 01 — CLI identity

You can name the principal a command used, assume a role, and watch a deny. That is SAA task 1.1 and the start of every later lab.

## 1. See who you are

```bash
aws sts get-caller-identity
aws configure list
aws iam get-account-summary
```

`get-caller-identity` returns the account, the user or role ARN, and the user id. `configure list` shows whether the key came from the environment, a profile, or SSO. If `ACCESS_KEY` in that table is an `AKIA` key and this is an account you will keep, stop and switch to `aws configure sso`. Long-lived keys are the lab convenience the security chapter tells you to delete.

Write down the ARN. The trust policy below must allow it.

## 2. A role that can list buckets and nothing else

```bash
CALLER_ARN=$(aws sts get-caller-identity --query Arn --output text)
# If the ARN is an assumed-role ARN (.../assumed-role/NAME/session),
# the trust principal is the role ARN, not the assumed-role ARN:
# arn:aws:iam::ACCOUNT:role/NAME
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

cat > /tmp/lab01-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "${CALLER_ARN}"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

cat > /tmp/lab01-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["s3:ListAllMyBuckets"], "Resource": "*"},
    {"Effect": "Allow", "Action": ["sts:GetCallerIdentity"], "Resource": "*"}
  ]
}
EOF

aws iam create-policy --policy-name Lab01ListBuckets \
  --policy-document file:///tmp/lab01-policy.json
POLICY_ARN="arn:aws:iam::${ACCOUNT}:policy/Lab01ListBuckets"

aws iam create-role --role-name Lab01Reader \
  --assume-role-policy-document file:///tmp/lab01-trust.json
aws iam attach-role-policy --role-name Lab01Reader --policy-arn "$POLICY_ARN"
```

If `create-role` fails with a malformed principal, your caller is an assumed role. Edit the trust file so `Principal.AWS` is `arn:aws:iam::${ACCOUNT}:role/THE_ROLE_YOU_ALREADY_HAVE`, then:

```bash
aws iam update-assume-role-policy --role-name Lab01Reader \
  --policy-document file:///tmp/lab01-trust.json
```

## 3. Assume it

```bash
CREDS=$(aws sts assume-role \
  --role-arn "arn:aws:iam::${ACCOUNT}:role/Lab01Reader" \
  --role-session-name lab01)
export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | python3 -c 'import json,sys; print(json.load(sys.stdin)["Credentials"]["AccessKeyId"])')
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | python3 -c 'import json,sys; print(json.load(sys.stdin)["Credentials"]["SecretAccessKey"])')
export AWS_SESSION_TOKEN=$(echo "$CREDS" | python3 -c 'import json,sys; print(json.load(sys.stdin)["Credentials"]["SessionToken"])')
unset AWS_PROFILE

aws sts get-caller-identity
aws s3 ls
aws s3api create-bucket --bucket "lab01-should-fail-${ACCOUNT}" --region us-east-1
```

The identity ARN now contains `assumed-role/Lab01Reader`. `s3 ls` works. `create-bucket` returns `AccessDenied`. That deny is the exam: the role is the permission, not the fact that you could log in.

Drop the temporary keys before you delete the role, or the next command runs as Lab01Reader and cannot call IAM:

```bash
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export AWS_PROFILE=sandbox
aws sts get-caller-identity
```

## 4. What the exam is pointing at

| You just did | The item it answers |
| --- | --- |
| `get-caller-identity` after assume-role | Temporary credentials, session name, the role ARN |
| `create-bucket` denied | Least privilege. Adding `s3:*` would have been the wrong fix |
| Trust policy names who may assume | A resource policy on the role. The identity policy on the caller still needs `sts:AssumeRole` if the caller is not an admin |
| Keys were `ASIA`, not `AKIA` | Session keys. They expire. `ExpiredToken` means you cached past `Expiration` |

Optional, still free: see the decision without calling S3.

```bash
aws iam simulate-principal-policy \
  --policy-source-arn "arn:aws:iam::${ACCOUNT}:role/Lab01Reader" \
  --action-names s3:ListAllMyBuckets s3:CreateBucket \
  --query 'EvaluationResults[].{a:EvalActionName,d:EvalDecision}'
```

`allowed` then `implicitDeny` is the result you want.

## Cleanup

```bash
aws iam detach-role-policy --role-name Lab01Reader --policy-arn "$POLICY_ARN"
aws iam delete-role --role-name Lab01Reader
aws iam delete-policy --policy-arn "$POLICY_ARN"
rm -f /tmp/lab01-trust.json /tmp/lab01-policy.json
```
