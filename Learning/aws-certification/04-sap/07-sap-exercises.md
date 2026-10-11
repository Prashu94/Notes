# SAP exercises

Write the answer before you open the key. One service is not enough. Name the constraint it satisfies.

## Questions

1. Sixty accounts. Developers have IAM users. The security team wants one disable button, MFA, and no long-lived keys. The network team wants one Transit Gateway.
2. RPO 30 seconds, RTO 20 minutes, Oracle that must stay Oracle, two Regions. They will not refactor to Aurora this year.
3. A new public API, SQL, spiky, global readers of static images, writes in one Region. Split the design into edge, compute, and data.
4. The NAT bill is the top line. Instances are private. Most bytes are S3. They also patch from the internet. AZ failure must not remove outbound internet.
5. An acquired company uses `10.0.0.0/16`, which you already use. You must connect them this quarter.
6. A pipeline in a shared account deploys to twenty workload accounts. Keys in GitHub are forbidden.
7. Existing Beanstalk rolling deploys have caused outages. The team will not move to EKS. What deploy change do you make?
8. Two hundred TB of files, 200 Mbps link, a month is too long, the share must stay available until cutover.
9. GuardDuty findings exist in each account and nobody looks at them. Least operational overhead.
10. A Region failure drills fails because Lambda in the recovery Region throttles at the default concurrency and the AMI is missing. What did the design forget?
11. Customer managed KMS in one Region. The DR Region cannot decrypt the copied snapshots.
12. The CFO wants chargeback. Tags are on the resources. Cost Explorer has no cost-center dimension.
13. A partner role was used by a different product in the partner account. Which condition, on which policy?
14. Active-active writes, shopping carts, two Regions, no joins.
15. Servers that cannot be refactored, RTO 90 minutes, they already pay for a DR tool discussion and do not want to build AMIs by hand.

## Answers

1. IAM Identity Center with permission sets and MFA. Transit Gateway in a network account, shared with RAM. SCPs for the guardrails. Not sixty IAM users and sixty peerings.
2. DMS CDC into RDS for Oracle in the second Region, or a cross-Region replica if the engine feature fits, plus a promote step inside 20 minutes. Pilot light for compute. Aurora is the trap because they said the engine stays.
3. CloudFront and S3 for the images. API Gateway or an ALB to Lambda or Fargate for the spiky API. Aurora or RDS Multi-AZ in the write Region, readers if the SQL reads are heavy. Do not put the images on the compute.
4. S3 gateway endpoint. One NAT gateway per AZ for the patch traffic that is still the internet.
5. You cannot peer overlapping CIDRs. Private NAT, or re-address one side. A Transit Gateway does not remove an overlap by itself.
6. The pipeline role assumes a deploy role in each workload account via OIDC or a trusted pipeline role. No access keys. StackSets if the infrastructure is CloudFormation.
7. Immutable or blue/green. Keep the old environment until the new one is healthy. Rolling is why users saw the bad version.
8. Snow Family for the bulk, DataSync for the final delta, then cut over the share. DataSync alone misses the window.
9. Delegated administrator in the security account, organization auto-enable, EventBridge rule to the ticket system. Do not ask forty teams to check forty consoles.
10. Service quotas in the recovery Region, and AMI or snapshot copy into that Region. A pilot light that cannot launch is a backup you have not proven.
11. A multi-Region key, or a snapshot copy that re-encrypts with a key that already exists in the DR Region. A single-Region key does not decrypt there.
12. Activate the cost allocation tag. Deliver a CUR if they need line items. Tags that are not activated do not appear.
13. `sts:ExternalId` on the trust policy of your role.
14. DynamoDB global tables.
15. Elastic Disaster Recovery, with a drill. MGN if the goal is migration rather than ongoing DR. Building AMIs by hand fails "not by hand."
