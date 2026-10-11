# Global infrastructure and the Well-Architected Framework

SAA all four domains. SAP every domain. DVA only where a function's Region, quota, or timeout shows up in code.

Official:

- https://docs.aws.amazon.com/whitepapers/latest/aws-overview/global-infrastructure.html
- https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
- https://aws.amazon.com/compliance/shared-responsibility-model/
- https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html

## The map

| Unit | What it is | What fails inside it | Exam consequence |
| --- | --- | --- | --- |
| Region | A cluster of AZs with its own API endpoints, IAM is global, most data is regional | A Regional service impairment | Multi-AZ does not save you. You need a second Region for that sentence |
| Availability Zone | One or more data centers with independent power and networking, connected by low-latency links inside the Region | An AZ outage | Put subnets, NAT, and instances in at least two AZs |
| Local Zone | An extension of a Region placed near a city | The parent Region can still be required for the control plane | Single-digit millisecond to users in that city. Not a DR Region |
| Wavelength | AWS compute in a carrier 5G network | Carrier-specific | Ultra-low latency to mobile devices. SAP and SAA both list it |
| Outposts | AWS racks in your building | You operate the facility power | Same APIs, data stays on premises. Not the cheap option |
| Edge location | CloudFront, Route 53, WAF, Global Accelerator points of presence | An edge pop | Caching and anycast. Not a place you launch an RDS instance |
| Partition | `aws`, `aws-cn`, `aws-us-gov` | IAM and ARNs do not cross partitions | GovCloud and China are separate. Artifact and compliance stems mention GovCloud. You do not "peer" a commercial account to GovCloud with a normal VPC peering |

AZs have names that differ per account (`us-east-1a` in your account is not the same building as `us-east-1a` in a customer's account). Use AZ IDs (`use1-az1`) when you place resources across accounts so they land in the same physical zone and you avoid a cross-AZ charge you did not expect.

## Global, regional, AZ-scoped

| Scope | Examples | Trap |
| --- | --- | --- |
| Global | IAM, CloudFront, Route 53 public hosted zones, WAF classic global for CloudFront, Global Accelerator, Organizations | An S3 bucket name is global. The bucket itself lives in a Region |
| Regional | VPC, ALB, RDS, Lambda, KMS keys (unless multi-Region), Secrets Manager secrets, API Gateway regional APIs | A snapshot copy to another Region is a copy, not a live replica |
| AZ | EBS volume, NAT Gateway, subnet, instance store | One NAT in one AZ is a single point of failure for every private subnet that uses it |
| Multi-AZ by service design | S3 Standard, DynamoDB, SQS, Aurora storage | You do not "enable Multi-AZ" on S3 Standard. It is already |

## Shared responsibility

| AWS | You, always | You, on EC2 | AWS, on Lambda / DynamoDB / S3 |
| --- | --- | --- | --- |
| Buildings, power, hypervisor, network hardware | Data classification, IAM, encryption choices, application code | Guest OS patches, security groups, AMIs | Runtime patching of the platform, storage durability of the service |
| Managed service availability targets | Backups you can restore, because a service snapshot you never tested is a hope | The process health check | The API availability |

A stem that says "AWS handles patching, so we are compliant" is wrong for EC2 and right for the Lambda runtime. Read the compute.

## The six pillars, as decision rules

Use the pillar that matches the last sentence of the question. When two pillars conflict, the stem's adjective picks the winner: "most cost-effective" loses to an RTO only if the cheap design misses the RTO.

### Operational excellence

Runbooks, IaC, small reversible changes, observability, and a way to practice failure.

| They do this | You recommend |
| --- | --- |
| SSH and a wiki | Session Manager, Patch Manager, a CloudFormation change set |
| One giant Friday deploy | Pipeline, canary or blue/green, alarm-based rollback |
| Nobody has failed over | A DRS drill, a Backup restore test, or a Fault Injection Service experiment on SAP-C03 |

### Security

Identity, detective controls, infrastructure protection, data protection, incident response.

Least privilege is an identity policy plus a resource policy plus, in an organization, an SCP that sets the ceiling. Encryption is KMS when you must turn the key off. Logging is CloudTrail for the API and CloudWatch for the workload. GuardDuty is findings. Inspector is vulnerabilities. Macie is sensitive data in S3. They are three different sentences.

### Reliability

Quotas, network topology, workload architecture that sheds load, change management, and failure management.

| Sentence | Reliability move |
| --- | --- |
| Survive an instance | ASG across AZs, ELB health checks, stateless app |
| Survive an AZ | Multi-AZ data store, NAT per AZ, subnet per AZ |
| Survive a Region | A DR pattern from the RTO/RPO table in `04-sap/06-disaster-recovery-design.md` |
| Survive a dependency | Queue, retry with jitter, timeout, fallback |
| Survive success | Service Quotas raised before launch. Partition keys with high cardinality |

### Performance efficiency

Pick the service that does the access pattern, then measure, then right-size. Caching, partitioning, and edge are the three tools. A bigger instance is the tool when the bottleneck is that instance and the workload cannot be split.

### Cost optimization

Right-size, price model, data transfer, storage class, and managed services that delete idle operational work. A budget alarm does not stop spend. It sends an email. Stopping spend is a deletion, a Service Catalog constraint, or an action you built.

### Sustainability

Use less. Graviton, scale to zero, lifecycle to cold storage, and a Region close to users so you do not carry bytes across the planet. The Associate exam rarely leads with this pillar. The framework still includes it. When a stem says "reduce environmental impact" with no other constraint, pick the option that scales to zero or moves cold data out of hot storage.

## Service quotas

Quotas are per Region unless the page says global. They fail launches in quiet ways: "you cannot create a VPC", Lambda throttles at the account concurrency, a Kinesis shard ceiling, an EIP limit.

```bash
aws service-quotas list-service-quotas --service-code vpc \
  --query 'Quotas[?contains(QuotaName, `VPC`)].{Name:QuotaName,Value:Value}' --output table
aws service-quotas get-aws-default-service-quota --service-code lambda \
  --quota-code L-B99A9384
aws service-quotas request-service-quota-increase --service-code vpc \
  --quota-code L-F678F1CE --desired-value 10
```

Quota codes change. If `get-aws-default-service-quota` returns `NoSuchResourceException`, list the quotas and read the code from the output. Do not memorize codes. Memorize that you request the increase before the launch window, and that a standby Region needs its own increase because quotas are regional.

Trusted Advisor and Service Quotas are how you see the wall. CloudWatch is how you see you are about to hit it (Lambda `Throttles`, `ConcurrentExecutions`).

## Health

AWS Health Dashboard (and the older Personal Health Dashboard name) tells you about events on your resources. AWS Health API in an organization account rolls events up. A public status page (`health.aws.amazon.com`) is the general service view and does not know about your instance.

## Exercises

1. A payments API must keep serving when one data center loses power. Users are in one country. RTO if the whole Region fails is 24 hours. Which scope do you design for the serving path, and which scope do you design for the 24-hour case?
2. A team enables Multi-AZ on RDS and S3 Cross-Region Replication and claims both protect against a Region failure. Which one does?
3. `us-east-1a` in the production account and `us-east-1a` in the log-archive account must share a placement so that a Transit Gateway attachment and its inspection appliance are in the same building. What identifier do you use?
4. A CloudWatch alarm emails finance when the bill crosses 1,000 USD. The stem says "prevent further spend." What does the alarm fail to do?
5. Name the pillar for each change: Session Manager instead of SSH; Aurora readers for a read-heavy catalog; S3 Intelligent-Tiering; two AZs; a canary deploy.

## Answers

1. Serving path: at least two AZs in one Region. The 24-hour Regional case: backup and restore into a second Region, not a warm standby. The RTO allows it, and warm standby would spend money the RTO does not require.
2. S3 CRR copies objects to another Region. RDS Multi-AZ stays inside one Region. Regional survival of the database needs a cross-Region replica, Aurora Global Database, or a copy of snapshots plus a restore runbook.
3. The AZ ID, not the AZ name.
4. It notifies. It does not stop instances, close an API, or apply a deny. You still need a human or an automation you wrote.
5. Operational excellence; performance efficiency; cost optimization; reliability; operational excellence.

## Regions, AZs, and what a name hides

A Region is a group of Availability Zones. An AZ is one or more data centers with independent power and networking. `us-east-1a` in your account is not `us-east-1a` in another account. The AZ ID (`use1-az1`) is the physical name. Use the ID when two accounts must land in the same building, such as a Transit Gateway attachment and the inspection appliance.

Edge locations are CloudFront and Global Accelerator, not a place you launch EC2. Local Zones are a city-level extension of a Region for a latency target the Region cannot meet. Wavelength is the 5G edge. Outposts is a rack in a building you control. None of them is a second Region for disaster recovery.

Global services that are not Regional: IAM, Organizations, Route 53 public zones, CloudFront, WAFs in the CloudFront scope. A Region-deny SCP that forgets them breaks the console. STS and some IAM calls can be Regional endpoints. The exam point is "do not treat IAM as living inside the VPC."

## Well-Architected, as a way to reject an option

| Pillar | The option loses when |
| --- | --- |
| Operational excellence | The change is an SSH session, a Friday script, or a runbook nobody has run |
| Security | The change opens a port, shares a key, or puts the workload in the management account |
| Reliability | The change is one AZ, one NAT, or a backup nobody has restored |
| Performance efficiency | The change is a bigger instance while the metric says the tier is waiting on something else |
| Cost optimization | The change is a second hot Region for an RTO of two days, or a commitment that does not cover the service |
| Sustainability | The change leaves idle capacity running. This pillar is real and it is rarely the only sentence in the stem |

The review is not a product you buy. The Well-Architected Tool records it. The exam wants the pillar that matches the change, and a design that does not violate a second pillar to satisfy the first.

## Quotas

Quotas are Regional. A standby Region does not inherit the primary's Lambda concurrency or EIP limit. Request the increase before the failover test. Trusted Advisor and Service Quotas show the wall. A budget alarm does not raise it and does not stop spend.

## More exercises

6. Users in one city need single-digit milliseconds. The nearest Region is 40 ms away. What do you look for, and what is it not?
7. A team puts production in the management account so an SCP will not block them. Which pillar did they break, and what is the fix?
8. CloudFront and an EC2 fleet are both "global" in a slide. Which one runs in a Region you pick?
9. `us-east-1a` in account A and account B. Why might a low-latency requirement between them fail?
10. Sustainability versus cost: idle dev instances all weekend. Which change satisfies both?

## Answers

6. A Local Zone in that city, if one exists, or Outposts if the workload must sit in their building. It is not a second full Region, and it is not a CloudFront cache if the traffic is not cacheable HTTP.
7. Security, and reliability of the guardrail model. Move the workload to a member account. SCPs do not apply to the management account, which is why they wanted to be there, and which is why they must not be there.
8. The EC2 fleet. You pick its Region and its AZs. CloudFront runs at the edge. The origin is still in a Region.
9. The AZ names are not physical. Account A's `us-east-1a` can be a different building from account B's. Use AZ IDs if they must be the same place.
10. Stop them. You stop paying and you stop burning the capacity. A Savings Plan on instances that should be off satisfies neither.
