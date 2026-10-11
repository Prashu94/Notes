# Labs

Run these in a sandbox account. A budget email at 10 USD does not stop spend. You stop spend by deleting what the lab created.

Set this once:

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
aws sts get-caller-identity
```

If that prints the wrong account, stop.

| Lab | What you prove | Bill if you delete the same day |
| --- | --- | --- |
| `lab-01-cli-identity.md` | Caller identity, a role, assume-role, a denied action | IAM is free |
| `lab-02-vpc-endpoints-tgw.md` | A VPC plus an S3 gateway endpoint. TGW and NAT stay on paper unless you opt in | VPC and gateway endpoints are free. NAT, interface endpoints, and TGW attachments are not |
| `lab-03-s3-encryption-lifecycle.md` | Block public access, default encryption, lifecycle, a deny policy | Pennies if the bucket is empty when you delete it |
| `lab-04-dynamodb-patterns.md` | Query, scan-with-filter, a condition, a GSI | On-demand, a handful of writes |
| `lab-05-lambda-sqs-eventbridge.md` | Queue, function, partial batch failure, an EventBridge rule | Free tier for a few invokes |
| `lab-06-api-gateway-cognito.md` | HTTP API, a user pool, a JWT authorizer | Cognito and HTTP API at this size are inside free tier for one user |
| `lab-07-sam-cicd.md` | `sam build`, `sam local invoke`, deploy, a buildspec, an OIDC trust policy | One small stack. Delete it |
| `lab-08-observability-xray.md` | Active tracing, a Logs Insights query, an alarm | Traces and a few log lines |
| `lab-09-multi-account-design.md` | An SCP you can read. Attach it only inside a sandbox organization | A bad SCP can lock the account. The lab says when to stop |
| `lab-10-disaster-recovery-patterns.md` | The four patterns on paper, plus one Route 53 health check if you want a live object | Do not build Aurora Global, Direct Connect, or Shield Advanced for practice |

Order: 01, 03, 04, 05, 06, 07, 08, then 02, 09, and 10. The last three are where people leave NAT gateways and second Regions running.

Every lab ends with a cleanup block. Run it before you close the laptop.
