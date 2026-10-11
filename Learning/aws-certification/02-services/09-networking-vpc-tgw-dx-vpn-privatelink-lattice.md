# Networking: VPC, Transit Gateway, Direct Connect, VPN, PrivateLink, Lattice

SAA 3.4 and 4.4. SAP 1.1. Foundations are in `01-foundations/05-networking-foundations-for-architects.md`. This file is the decision and the commands.

Official:

- https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html
- https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html
- https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html
- https://docs.aws.amazon.com/vpc-lattice/latest/ug/what-is-vpc-lattice.html
- https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html

## Choose the path

| Need | Service |
| --- | --- |
| Two VPCs, no third party, no overlap | Peering. Not transitive. You write the routes |
| Many VPCs, on-premises, shared services | Transit Gateway. Separate route tables for prod, non-prod, and inspection |
| A segmented global WAN | Cloud WAN |
| Publish one service | PrivateLink. You run an NLB. They get an interface endpoint. Their route tables do not learn your VPC |
| Service-to-service HTTP, IAM, across accounts and clusters | VPC Lattice. SAP-C03 weights this. It is already the green-field answer |
| Encrypted over the internet, days not months | Site-to-Site VPN. About 1.25 Gbps per tunnel is the planning number people use. Use several tunnels or DX when the stem is multi-gigabit |
| Steady high bandwidth, stable latency | Direct Connect. A hosted connection, a dedicated connection, a private VIF, a public VIF, or a transit VIF onto a Transit Gateway |
| DX down | A second DX location, or a VPN backup. One cross-connect is a single point of failure |
| Encryption on DX that an auditor can name | MACsec where the port supports it, or VPN over the DX VIF |
| People, not sites | Client VPN, or Verified Access when the stem is an application without a full network tunnel |
| Overlap | Private NAT. Do not keep trying to peer |

Inspection: an egress VPC with Network Firewall or Gateway Load Balancer endpoints, and the Transit Gateway route tables send spoke traffic there instead of straight to the internet. "Central egress" is this picture.

## Commands you can run without buying a circuit

```bash
aws ec2 create-transit-gateway --description hub --options AmazonSideAsn=64512,AutoAcceptSharedAttachments=enable,DefaultRouteTableAssociation=enable,DefaultRouteTablePropagation=enable
aws ec2 create-transit-gateway-vpc-attachment --transit-gateway-id tgw-xxxx --vpc-id "$VPC" --subnet-ids "$PRIV_A" "$PRIV_B"
aws ec2 create-vpc-peering-connection --vpc-id "$A" --peer-vpc-id "$B" --peer-region us-east-1
aws ec2 create-vpn-connection --type ipsec.1 --customer-gateway-id cgw-xxxx --transit-gateway-id tgw-xxxx
aws ec2 create-vpc-endpoint --vpc-id "$VPC" --service-name com.amazonaws.us-east-1.sqs --vpc-endpoint-type Interface --subnet-ids "$PRIV_A" "$PRIV_B" --security-group-ids "$SG" --private-dns-enabled
aws ec2 describe-flow-logs
```

Direct Connect is a design exercise unless you already pay for a port. Know the words: virtual interface, Direct Connect gateway, transit VIF, LAG, and the fact that DX is not encrypted by default.

## Lattice and Service Connect

ECS Service Connect names tasks inside ECS and adds a proxy. VPC Lattice is the broader service network: HTTP services, IAM auth, across VPCs, accounts, and including Lambda. Pick Lattice when the caller is not another ECS service. Do not start a new App Mesh.

## DNS

Private hosted zones associate to VPCs. They do not automatically cross a peering connection unless you associate the zone. Hybrid: Resolver inbound and outbound, rules shared with RAM. A conditional forwarder on-premises points at the inbound endpoint IPs.

## Cost and failure

Gateway endpoints for S3 and DynamoDB. NAT per AZ for what remains. Cross-AZ traffic is a bill and a reason to be careful with chatty tiers. Flow logs answer "who connected." Reachability Analyzer answers "which rule stopped it."

## Exercises

1. A vendor must call one HTTPS API and must not get a route to your databases. PrivateLink or peering?
2. Prod and dev must not route to each other, but both must reach shared services and the internet through inspection. How many Transit Gateway route tables?
3. DX is ordered and will take eight weeks. The migration starts in two. What runs until DX is up, and what remains after as the backup?

## Answers

1. PrivateLink. Peering is a network. You would then have to filter it. An endpoint attached to an NLB in front of the API is the narrow path.
2. At least three. One that dev uses, one that prod uses, one for shared services and inspection. Dev's table has no route to prod's attachment.
3. Site-to-Site VPN now. Keep the VPN or a second DX location after the primary circuit exists. One circuit is not the resilient design.

## Transit Gateway, the route tables are the design

A Transit Gateway is a Regional hub. Attachments are VPCs, VPN connections, Direct Connect gateways, and peering to a Transit Gateway in another Region. Each attachment is associated with one route table. Routes point at an attachment. Propagation can add routes from an attachment into a table automatically. Static routes are how you pin a default to the inspection VPC.

The exam picture for a company that wants isolation:

| Route table | Associated attachments | Routes |
| --- | --- | --- |
| Prod | Production VPCs | Shared services, the inspection or egress VPC. No route to the dev attachment |
| Non-prod | Developer VPCs | Shared services, inspection. No route to prod |
| Shared | The shared-services VPC, often the inspection VPC | Back to the spokes that are allowed to use it |

A shared services VPC that hosts endpoints or Active Directory is on the tables that need it. An egress VPC holds NAT Gateways and, when they asked for inspection, AWS Network Firewall or a Gateway Load Balancer and the appliance fleet. Spoke private subnets default-route to the Transit Gateway, not to a NAT of their own. The Transit Gateway default route sends `0.0.0.0/0` at the egress attachment. East-west traffic can be sent through inspection too, with a more specific design, when the stem says prod must not talk to dev without being inspected. If you leave the default route table and default propagation on, everything talks to everything. That is the failure mode of the CLI flag `DefaultRouteTableAssociation=enable` copied from a blog into a bank.

The appliance mode on an attachment keeps a flow on the same AZ appliance. Without it, a stateful firewall sees one direction and not the return, and it drops the flow. The stem is "the firewall is up and established connections still fail."

RAM shares the Transit Gateway from the network account. Workload accounts create the VPC attachment. An SCP can still stop them. Sharing does not put routes in. You still edit the route tables.

Transit Gateway Connect and peering across Regions exist. Cloud WAN is the next step up when the stem is a global segmented WAN rather than one Region plus a data center. Two VPCs in one Region do not need Cloud WAN, and they often do not need a Transit Gateway either. Peering is cheaper and simpler until the third network shows up.

Overlapping CIDRs will not peer and will not route on one Transit Gateway domain as if they were unique. Private NAT translates one side. Renumbering is cleaner and slower. The acquisition stem is private NAT.

## Direct Connect and VPN

A Direct Connect connection lands at a location. A dedicated connection is your port. A hosted connection is a partner handing you a piece of theirs. A link aggregation group bundles dedicated connections. None of that is encryption, and none of it is a second building.

Virtual interfaces:

| VIF | It reaches |
| --- | --- |
| Private | A virtual private gateway on a VPC, the older one-VPC design |
| Transit | A Direct Connect gateway associated with a Transit Gateway. This is the many-VPC design |
| Public | AWS public services over the circuit, such as S3, without using the internet |

A Direct Connect gateway is the indirection between VIFs and one or more gateways. You do not order a new physical connection per VPC.

BGP is how failover works. Static routes are how a human fails over badly. A second location, or a Site-to-Site VPN with BGP of a worse preference, is the resilient design. One cross-connect is one maintenance event away from an outage.

Encryption an auditor can name: MACsec on ports that support it, or a VPN over the Direct Connect private path. "It is a private circuit" is not "it is encrypted."

Site-to-Site VPN is IPsec over the internet. Two tunnels per connection is the normal configuration. Throughput on the order of 1.25 Gbps per tunnel is the planning number. Multi-gigabit steady traffic is Direct Connect. VPN is what you turn up this week, and what you keep as the backup after the circuit exists. The customer gateway is the on-premises device. The AWS side is a virtual private gateway or, in this chapter's designs, the Transit Gateway.

Client VPN is people on laptops into the VPC. It is not a site-to-site replacement. Verified Access is application access without giving the laptop a route to the whole VPC. That is the "do not put users on the network" answer when the stem allows it.

## PrivateLink, step by step

The provider runs the service behind a Network Load Balancer in their VPC. They create a VPC endpoint service and allow the consumer's account. The consumer creates an interface endpoint in their subnets, with a security group, and enables private DNS if the provider offered a private DNS name. The consumer's applications call that name. Their route tables never learn the provider's CIDR. The provider's databases stay unroutable. That is the whole point.

Interface endpoints for AWS services (Secrets Manager, KMS, SQS, CloudWatch Logs) are the same object with AWS as the provider. Private DNS makes the SDK's normal hostname resolve to the endpoint inside the VPC. Without it, the SDK still uses the public name and you need a NAT or a custom endpoint URL. The endpoint has a security group. The application's security group must be allowed to it. A timeout means the network. `AccessDenied` means IAM, and it comes back quickly.

Gateway endpoints for S3 and DynamoDB are route-table prefix lists. They do not have security groups. They do not have an hourly charge. They are not PrivateLink, even though people say "the S3 endpoint" for both. There is an S3 interface endpoint. It costs money. The cost and "no internet" answer for S3 is the gateway endpoint unless the stem needs the interface endpoint's features from another VPC or from on-premises.

Gateway Load Balancer is the third endpoint story: you are inserting a fleet of appliances. GENEVE. The consumer's route sends the traffic at the endpoint. This is inspection, not an application API.

## Lattice and Service Connect

ECS Service Connect gives ECS services names and a proxy inside the cluster. It is the ECS-to-ECS answer. VPC Lattice is a service network for HTTP services across VPCs, accounts, and compute types, including Lambda, with IAM authentication on the call. Pick Lattice when the caller is not "another task in this ECS cluster." App Mesh is in maintenance. A new design that starts with App Mesh is the wrong answer. Security groups still exist underneath. Lattice does not replace a Transit Gateway for arbitrary TCP between databases. It is HTTP with identity.

## DNS that crosses the network

A private hosted zone is associated with VPCs. Peering does not associate it. You associate the zone, or you share Resolver rules. On-premises names from a VPC: Resolver outbound endpoint in two AZs, a forwarding rule, RAM if other VPCs need the rule. Private names from the office: Resolver inbound endpoint in two AZs, and the corporate DNS forwards to those IPs. One AZ for the Resolver is the outage when that AZ dies and "DNS is down" while the instances are fine.

## Cost and the failures that look like routing bugs

NAT data processing on S3 and DynamoDB is a missing gateway endpoint. Cross-AZ charges inside a chatty tier are real and do not justify collapsing a Multi-AZ design the stem required. Interface endpoints have an hourly charge per AZ. One endpoint for a once-a-day call is waste. One endpoint for Secrets Manager on a private fleet with no NAT is the design. Idle public IPv4 addresses are a bill. An ALB replaces an address per instance.

Flow logs tell you accepted and rejected flows, not payloads and not the IAM principal. Reachability Analyzer tells you which security group, NACL, or route stopped a path. The Transit Gateway route analyzer does that across attachments. Traffic Mirroring copies packets to an appliance and is the heavy tool.

## More exercises

4. Default association and default propagation are enabled. Prod can open a TCP session to a developer database. What do you change, without building a second Transit Gateway?
5. The firewall in the egress VPC sees the SYN and not the SYN-ACK. Which attachment setting?
6. PrivateLink is up. The consumer times out. The provider's NLB is healthy. Name the two security groups you check.
7. S3 traffic from a private subnet must not use the NAT. You create an interface endpoint because "PrivateLink is the private path." What did you pay for that you did not need, and what do you create instead?
8. Office laptops resolve `db.prod.internal` only when they are on the Client VPN. The VPC resolves it. What is missing for the office DNS servers?
9. A hosted Direct Connect connection is in one building. The stem says the data center link must survive that building. What do you add, and what routing protocol makes the failover automatic?

## Answers

4. Separate Transit Gateway route tables. Associate prod attachments with a table that has no route to the dev attachment, and the reverse. Turn off the flat default propagation that made one table for everyone. Shared services get a route from both tables.
5. Appliance mode on the firewall's attachment, so forward and return stay on the same appliance. A stateful firewall dropping the return path is the symptom.
6. The endpoint's security group in the consumer VPC must allow the consumer application. The NLB target's security group in the provider VPC must allow the NLB. Private DNS should be checked third: if it is off, the client may be trying the public name and timing out for a different reason.
7. You pay the hourly interface endpoint charge. Create a gateway endpoint and associate it with the route tables. Keep an interface endpoint only if you have a requirement the gateway endpoint cannot meet.
8. An inbound Resolver endpoint, and a forwarder on the office DNS that points `prod.internal` at those endpoint IPs. Client VPN works because the laptop is using the VPC's resolver. The office DNS is not. Peering or a VPN for the site does not create this forwarder by itself.
9. A second Direct Connect location, or a Site-to-Site VPN backup with a worse BGP preference. BGP withdraws the dead path. A static route waits for a human. One hosted connection is one location.
