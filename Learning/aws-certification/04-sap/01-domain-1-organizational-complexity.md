# SAP Domain 1 — Organizational complexity (26%)

Tasks 1.1 through 1.5. Associate already taught one VPC and one role. This domain is many accounts, a data center, and a security team that must see every trail.

Read first: `01-foundations/04-accounts-organizations-control-tower.md`, `01-foundations/05-networking-foundations-for-architects.md`, `02-services/09-networking-vpc-tgw-dx-vpn-privatelink-lattice.md`, `02-services/13-security-hub-guardduty-inspector-macie-detective.md`, `02-services/16-cost-management.md`.

## 1.1 Network connectivity

Draw the network account before you pick a product.

```text
On-premises
  DX (primary) + Site-to-Site VPN (backup)
        |
  Transit Gateway  (network account, shared with RAM)
        |
  prod VPCs, shared-services VPC, egress VPC
  Gateway endpoints for S3 and DynamoDB in each VPC
  Resolver inbound + outbound for hybrid DNS
```

| Constraint | Design |
| --- | --- |
| Two VPCs, no growth, no overlap | Peering |
| Many VPCs plus on-premises, transitive | Transit Gateway |
| Multi-Region segmentation at WAN scale | Cloud WAN |
| One API exposed, databases must stay unroutable | PrivateLink (NLB publisher, interface endpoint consumer) |
| HTTP between accounts and clusters, IAM on the call | VPC Lattice |
| Overlapping CIDRs during migration | Private NAT. Peering will not form |
| 10 Gbps steady, stable latency | Direct Connect. One circuit is still a single point of failure. Second location or a VPN backup |
| Need it this week, encrypted, modest bandwidth | VPN. Not a substitute for DX when the stem names jitter or multi-gigabit |
| See who talked to whom | VPC Flow Logs. Reachability Analyzer for "why can't A reach B". Traffic Mirroring only when they need packets |

Hybrid DNS is where Professional items hide. On-premises names resolved in the VPC: Resolver outbound endpoint plus a forwarding rule, shared with RAM. Private hosted zone names resolved on-premises: Resolver inbound endpoint, and the corporate DNS forwards to it.

Region choice is a network decision. Data residency picks the Region. Latency picks the Region or a Local Zone. A second Region is a DR decision, not a latency decoration.

## 1.2 Security controls

Humans: Identity Center, corporate IdP, permission sets, MFA. No IAM users for staff.

Workloads: roles. Cross-account: `AssumeRole` plus `ExternalId` for a third party. RAM when the resource can be shared instead of copied.

Ceiling: SCPs. They never grant. An explicit deny wins, including against `AdministratorAccess`, except in the management account where SCPs do not apply.

Central detection: organization CloudTrail to the log-archive account, GuardDuty and Security Hub and Inspector delegated to the security account, EventBridge from findings to the ticket system. Access Analyzer for resources shared outside the org. KMS multi-Region keys only when the same ciphertext must decrypt in another Region. Otherwise separate keys, smaller blast radius.

ACM public certs for ALB, CloudFront, API Gateway. Private CA for internal names.

## 1.3 Resilience as an organizational standard

Pick the pattern from RTO and RPO, then make it the standard in the landing zone, not a one-off diagram. The patterns and the service mapping are in `06-disaster-recovery-design.md`. Automatic means a health check and a routing change, not a bridge call. Scale-out is the default. Scale-up is the license or the single-threaded exception.

## 1.4 Account structure

Use the reference in `05-multi-account-reference-architecture.md`. If the stem says new organization and least operational overhead, the answer is Control Tower. If they already have a landing zone, extend it. Do not rip it out to install Control Tower for sport.

Central logging is an organization trail, all Regions, log file validation, KMS, bucket policy denying delete, SCP denying `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail` in member accounts.

## 1.5 Cost visibility

CUR in an account finance can read. Cost allocation tags activated. Budgets per OU or per linked account. Compute Optimizer and S3 Storage Lens for rightsizing. Savings Plans for the steady compute. Reserved nodes for RDS, ElastiCache, Redshift, OpenSearch. Spot for the interruptible share. A budget email does not stop spend.

## Scenarios

1. Forty VPCs, a data center on 10 Gbps, overlapping `10.0.0.0/8` in two acquired companies. Transit Gateway plus private NAT for the overlap. Peering fails the overlap and the scale.
2. A security team must see every API call and must not depend on each account remembering to create a trail. Organization trail, log-archive bucket, SCP that denies stopping the trail.
3. A partner copies data nightly by assuming a role. Last quarter a different product in the partner's account used the same role ARN. Add `sts:ExternalId`.
4. The bill cannot be split by product. Tags exist on resources. They were never activated as cost allocation tags, and there is no CUR.

## How a Professional stem is different from an Associate stem

Associate asks which service. Professional asks which design survives four constraints at once: a company that already has accounts, a data center, a security team that is not you, and a number for RPO or for bandwidth. The option that is "best practice" and ignores one of those constraints is wrong. The option that keeps their landing zone and adds the missing control is usually right. Ripping out a working Transit Gateway to install Cloud WAN because Cloud WAN is newer fails unless the stem is multi-Region WAN segmentation at a scale Transit Gateway is struggling with.

Write the constraints in the margin before you read the options:

- How many accounts, and do they already have Organizations or Control Tower?
- Where is the data center, and is the CIDR overlapping?
- Who must see the logs, and are they allowed to administer production?
- What is already deployed that you are not allowed to replace this quarter?

## Network, at the depth this domain grades

Peering is two VPCs, not transitive, no overlapping CIDRs, no bandwidth device in the middle. It is still the right answer for two VPCs that exchange a little traffic and will stay two. A mesh of fifteen peering connections is how route tables become the outage. Transit Gateway is the hub. It is transitive. You attach VPCs, VPNs, and Direct Connect gateways. You share the gateway with RAM so the network account owns it and the workload accounts attach. Route tables on the Transit Gateway are the segmentation: production does not route to developer VPCs just because both are attached. A shared services VPC (Directory, the pipeline, endpoints) is associated with the route tables that need it. An egress VPC holds the NAT Gateways and, when they asked for inspection, Network Firewall or a Gateway Load Balancer and the appliance fleet. Workload private subnets default-route to the Transit Gateway, not to their own NAT, when central egress is the requirement. That is the bank diagram.

Cloud WAN is the multi-Region version of that hub when the stem is a global network with segments, not one Region plus a data center. Do not answer Cloud WAN for two VPCs in `us-east-1`.

Direct Connect is a circuit. One connection in one location is a single building. The resilient design is a second location, or a Site-to-Site VPN as the backup, with BGP so the failover is not a human editing a static route. A virtual private gateway on one VPC does not scale to forty VPCs. The Direct Connect gateway attaches to the Transit Gateway. Encryption over the circuit is VPN over Direct Connect, or MACsec where the port supports it. "We have Direct Connect, so the traffic is private and encrypted" is only half true. Private, yes, if it is a private VIF. Encrypted, only if you added encryption.

Overlapping `10.0.0.0/8` from an acquisition will not peer and will not attach cleanly to the same routed domain. Private NAT translates one side. Renumbering is cleaner and slower. The exam accepts private NAT when the stem says the overlap cannot be fixed before the migration window.

Hybrid DNS is where otherwise-correct networks fail the item. On-premises names resolved from the VPC: a Resolver outbound endpoint in at least two AZs, a forwarding rule, and RAM if other VPCs must use it. VPC private hosted zone names resolved from on-premises: a Resolver inbound endpoint, and the corporate DNS forwards to those IPs. A private hosted zone associated with the VPC does nothing for a laptop in the office until that forwarding exists. Peering does not automatically share private hosted zones. Association is a separate step, and it still does not help the office.

| Symptom | What is missing |
| --- | --- |
| VPC can reach on-premises IPs and cannot resolve on-premises names | Outbound Resolver and a forwarding rule |
| Office can reach VPC IPs by address and not by the private DNS name | Inbound Resolver, and a forwarder on the corporate DNS |
| Only the VPC that owns the zone can resolve it | Associate the zone with the other VPCs, or share the rules |
| DNS works and a security review fails | The Resolver endpoints are in one AZ. Put them in two |

## Identity and guardrails, at the depth this domain grades

Permission sets are the human path. A permission set is an IAM role template assigned to a group for an account or an OU. Developers get a different permission set in production than in the sandbox, often read-only plus a break-glass that is alarmed. The break-glass role is not the daily role.

SCPs are the ceiling. Common denies that show up as the answer:

- `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail` on member OUs.
- Leaving the approved Regions, with `NotAction` exemptions for global services.
- `ec2:RunInstances` for expensive families in the sandbox OU only.
- Disabling GuardDuty or Security Hub.
- Leaving the organization (`organizations:LeaveOrganization`).

An allow-list SCP (deny `*` then allow a set of services) is tighter and easier to get wrong. A deny-list SCP (allow `*` at the root, then deny specific actions) is how most landing zones start. The root of the organization must not be an empty allow. There is a default FullAWSAccess SCP. If you detach it and attach only a narrow allow, you can lock every member account, including the one you are using to fix it. The management account still works, because SCPs do not apply to it. That is your recovery path, and it is also why workloads do not run there.

Permissions boundaries are for delegated administration inside one account: a developer can create a role only if the boundary is attached, and the boundary is narrower than admin. The boundary does not replace the SCP. The SCP is the org-wide statement. The boundary is the account-local statement.

RAM shares a subnet, a Transit Gateway, an Aurora cluster's subdomain, a License Manager configuration. The share is not a copy. The resource policy and the IAM policy in the consumer account still have to allow use. Sharing a subnet into another account is how a central network account owns the VPC and the application account launches instances into it. That is a real landing-zone pattern. It is also easy to over-share. Share with the OU that needs it, not with the organization, unless the stem says every account.

## Detection that does not depend on the application team

Organization trail, all Regions, log file validation, KMS with a key the application accounts cannot disable, bucket in the log-archive account, Object Lock or a deny-delete bucket policy, SCP so members cannot stop the trail. Data events are expensive. Turn them on for the buckets and tables the stem called sensitive, not for every `GetObject` in the company, unless the stem said that.

GuardDuty, Security Hub, Inspector, and Detective have a delegated administrator. That account should be the security account, not the management account and not a workload account. Auto-enable new accounts. Findings go to EventBridge and then to the ticket system. Access Analyzer on the organization finds resources shared outside the zone. Macie for the buckets that may hold personal data. Config aggregators in the security account so a rule is not something each team remembers to create.

KMS multi-Region keys exist so the same key id can decrypt in another Region. Use them when the stem requires that. Otherwise a key per Region is the smaller blast radius. A key policy that only allows the security account to administer, and the workload role to `Decrypt` and `GenerateDataKey`, is the split. Automatic rotation on for symmetric customer managed keys. Imported material and asymmetric keys are a different rotation story. Disabling the key is the incident control.

## Cost visibility is an organizational control

The payer account sees the bill. A member account does not, unless you gave it a billing view. The CUR delivered to a bucket finance can read is the system of record. Cost allocation tags do nothing until they are activated. Budgets per linked account or per tag catch a sandbox GPU experiment. They do not stop it. The SCP on the sandbox OU stops the instance family. Savings Plans are bought in the payer account and can apply across members. A Savings Plan bought in the wrong account, or a Reserved Instance that is zonal and not shared, is why a steady fleet is still on the On-Demand line. Compute Optimizer and Trusted Advisor at the organization level are how you see idle NAT Gateways in accounts you do not log into every day.

## Scenarios, worked

**1.** Forty VPCs, a data center on 10 Gbps, overlapping `10.0.0.0/8` in two acquired companies. Transit Gateway in the network account, shared with RAM. Direct Connect gateway onto that Transit Gateway, plus a VPN backup. Private NAT for the overlapping ranges. Peering fails the overlap and the scale. A virtual private gateway on each VPC fails the operations sentence.

**2.** The security team must see every API call and must not depend on each account creating a trail. Organization trail into the log-archive bucket, KMS, log file validation, SCP denying stop and delete on the member OUs. Delegated GuardDuty in the security account. A trail inside each application account that the application admin can delete is the design they already have, and it is the one that fails.

**3.** A partner copies data nightly by assuming a role. Last quarter a different product in the partner account used the same role. Add `sts:ExternalId` and, if you can, change the trust principal from the partner account root to the one role ARN they actually use. External id stops the confused deputy. Naming the role stops every other principal in that account.

**4.** The bill cannot be split by product. Tags exist on resources. They were never activated as cost allocation tags, and finance is reading a PDF invoice. Activate the tags. Ship a CUR. Wait until the next billing period for the history to populate. Tagging the resources again does not backfill the months before activation.

**5.** Developers have `AdministratorAccess` in production because "the SCP will protect us." The only SCP is FullAWSAccess. An SCP does not exist until you write the deny. Give production a narrower permission set, and attach the deny SCP. Also stop using the management account as a place developers log into when the sandbox SCP blocks them.

**6.** Private hosted zones work in the production VPC and fail in the new account's VPC and from the office. Associate the zone with the new VPC, or share a Resolver rule. For the office, add an inbound Resolver endpoint and a forwarder. Peering the VPCs does not complete either of those steps.

## Exercise

Write the network and the account names for a bank that wants production isolated from developers, a data center with a circuit, central egress inspection, GuardDuty in one place, and a way to disable one leaver across every account. Then check `05-multi-account-reference-architecture.md`.

A complete answer names at least: management (no workloads), security (delegated GuardDuty, Security Hub, the Config aggregator), log archive (the trail bucket), network (Transit Gateway, Direct Connect gateway, egress VPC with inspection), shared services if the pipeline is central, workload OUs for production and non-production, Identity Center for the leaver, and an SCP that keeps developers from turning the detectors off. If your drawing has one account with a peering mesh, it is an Associate drawing.
