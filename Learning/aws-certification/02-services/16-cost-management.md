# Cost management

SAA domain 4. SAP tasks 1.5, 2.6, and 3.5.

Official:

- https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html
- https://docs.aws.amazon.com/cur/latest/userguide/what-is-cur.html
- https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- https://docs.aws.amazon.com/compute-optimizer/latest/ug/what-is-compute-optimizer.html
- https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/Welcome.html

## Which tool answers which question

| Question | Tool |
| --- | --- |
| What will this design cost before we launch? | Pricing Calculator. It does not see your bill |
| What did we spend, and what is the forecast? | Cost Explorer |
| Give me every line item in S3 so finance can build chargeback | Cost and Usage Report, often queried with Athena |
| Email me at 80% of the monthly forecast | Budgets. It does not stop resources unless you add an action you wrote |
| Which instance is oversized? | Compute Optimizer |
| Which buckets have incomplete multipart uploads and which class is the data in? | S3 Storage Lens |
| Which idle load balancers and open security groups exist? | Trusted Advisor. Some checks need Business Support or higher |
| Did the tag we invented show up in the bill? | Only after you activate it as a cost allocation tag |

## Purchasing, one page

Compute Savings Plans: a dollar-per-hour commit across EC2, Fargate, and Lambda. EC2 Instance Savings Plans: cheaper, stuck to a family and Region. Reserved Instances and reserved nodes: still the discount for RDS, ElastiCache, Redshift, OpenSearch, and DynamoDB reserved capacity. Spot: interruptible. Dedicated Hosts: licenses. A Savings Plan does not make a Spot interruption impossible, and Spot does not belong under the only database.

## The transfers that dominate Professional answers

NAT data processing, cross-AZ, cross-Region, and internet egress. Gateway endpoints remove S3 and DynamoDB from the NAT line. CloudFront can reduce origin bytes. A second hot Region is a cost decision disguised as resilience. If the RTO is a day, stop paying for warm standby.

Public IPv4, idle NAT gateways, idle load balancers, unattached EBS, and old snapshots are the cleanup list. gp3 replaces gp2 volumes that were grown to buy IOPS.

## Tags

`owner`, `environment`, `cost-center`, `application`. Enforce with a tag policy or an SCP once you have tested it. Activate the keys in billing. Untagged spend shows up as unallocated. That is a data problem, not a pricing-model problem.

## Commands

```bash
aws ce get-cost-and-usage --time-period Start=2026-09-01,End=2026-10-01 --granularity MONTHLY \
  --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE
aws budgets describe-budgets --account-id "$ACCOUNT"
aws compute-optimizer get-ec2-instance-recommendations
aws cur describe-report-definitions
```

## Exercises

1. The CUR is empty and Cost Explorer works. What did nobody create?
2. A Standard RI for `m5.xlarge` stopped matching after a move to `m7g`. What purchase would have followed the fleet?
3. A budget action is not configured. The alarm fired. Why are instances still launching?
4. Storage Lens shows a bucket of objects untouched for a year in Standard. Which S3 change, if retrieval within hours is acceptable and the pattern is now known?

## Answers

1. A Cost and Usage Report definition. Cost Explorer does not require the CUR. The line-item export does.
2. A Compute Savings Plan. It applies across families. A Convertible RI could be exchanged and is more work.
3. The budget notified. It did not deny `RunInstances`. An SCP or a custom action does that.
4. A lifecycle rule to Glacier Flexible Retrieval or Deep Archive, or Intelligent-Tiering if they still do not trust the pattern. Known and cold is a lifecycle. Unknown is Intelligent-Tiering.

## What shows the bill, and what changes it

| Tool | It does | It does not |
| --- | --- | --- |
| Cost Explorer | Interactive cost, by service, account, tag, for the last months | A line-item export. It does not stop spend |
| Cost and Usage Report | The line items, in S3, hourly if you ask, including resource ids | Appear by magic. Someone creates the report definition. It does not backfill a tag that was not activated |
| Budgets | An email or a notification at an amount or a forecast. Optional budget actions | Deny `RunInstances` unless you attached an action that does. The alarm alone is a letter |
| Cost allocation tags | A dimension in the bill, after you activate them in the payer account | Retroactive history. Activate, then wait |
| Compute Optimizer | Rightsizing recommendations after it has metrics | Delete the instance. You apply the change |
| Trusted Advisor | Idle load balancers, idle addresses, underused volumes, service limits | A design. It is a checklist of waste that already exists |
| S3 Storage Lens | Bucket-level access and cost patterns | Move the objects. A lifecycle does that |
| Pricing Calculator | A before-the-move estimate | The bill. The CUR is the bill |
| Savings Plans and Reservations | A lower rate on a commitment | Apply to the wrong service. A Compute Savings Plan does not discount RDS the way an RDS reservation does |

The payer account sees member spend. A member account sees its own, unless a billing view was shared. The CUR should land in a bucket finance and the platform team can read, not only in a console screenshot. An organization trail of the billing console is not a CUR.

Activate tags before you promise a per-team report. User-defined tags and AWS-generated tags both need activation. A tag on the resource and a tag that is activated are two steps. Teams that tag faithfully and still cannot split the bill skipped the second step.

## Commitments

Compute Savings Plans commit to a dollar-per-hour rate and apply across EC2, Fargate, and Lambda, across instance families. That is the "one commitment, the fleet will change shape" answer. EC2 Instance Savings Plans are cheaper and stuck to a family in a Region. Standard Reserved Instances are the least flexible and match attributes. Convertible Reserved Instances can be exchanged. RDS, ElastiCache, Redshift, and OpenSearch have their own reservations. A Compute Savings Plan will not quiet those lines.

Spot is not a commitment. It is a discount you can lose. Use it for the interruptible share. A zonal Reserved Instance that is not shared with the organization discounts one AZ in one account. An organization can share discounts. If the stem says the reservation was bought in the wrong account and sharing is off, that is why production is still On-Demand.

## The lines that surprise people

NAT Gateway hours plus data processing. Public IPv4 hours. Cross-AZ data. Cross-Region replication. Idle Elastic IPs. Unattached EBS. Snapshots of deleted test instances. Log groups with no retention. DynamoDB provisioned capacity on a table that is idle all night, when on-demand would have been nothing. A second Region running full size for an RTO of two days. Interface endpoints in three AZs for an API called daily.

Budgets do not see all of this in time to matter if the granularity is a monthly surprise. A daily budget on the sandbox account, plus an SCP that denies the expensive instance families, is the control. The budget is the signal. The SCP is the brake.

## More exercises

5. Finance wants last quarter split by `CostCenter`. The tags were applied in January and activated in March. What does the January bill show?
6. The NAT line is larger than EC2. The workload is S3 and DynamoDB. What architecture change, not what commitment?
7. A Savings Plan was bought for the RDS fleet. The RDS line did not drop. Why?
8. Trusted Advisor says an Elastic IP is idle. What are you paying for, and what do you delete?
9. Dev runs all weekend on On-Demand, the same size as production. Name two changes that are not a Savings Plan.

## Answers

5. Nothing for `CostCenter` in January and February. Activation does not backfill. March onward can split. Recreating the tags does not fix the past.
6. Gateway endpoints for S3 and DynamoDB. A Savings Plan does not discount NAT data processing. Direct Connect does not either, for this path.
7. Compute Savings Plans cover EC2, Fargate, and Lambda. RDS needs an RDS Reserved Instance or its own reservation product. The purchase was the wrong product.
8. The public IPv4 address hourly charge, whether or not it is attached, in the current pricing. Release the address. If it was attached to a stopped instance you still need, you are also paying for that instance's EBS.
9. Stop the instances outside working hours, and shrink them. Dev does not need production's Multi-AZ or its size unless the stem said developers cannot work during a failure. A schedule beats a commitment for a fleet that should be off.
