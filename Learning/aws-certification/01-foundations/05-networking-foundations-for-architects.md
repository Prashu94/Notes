# Networking foundations for architects

SAA 1.2, 2.2, 3.4, 4.4. SAP 1.1. DVA only needs the Lambda-in-a-VPC slice at the end.

Official:

- https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html
- https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html
- https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html
- https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/welcome.html

## A VPC you can draw

```text
10.0.0.0/16
  public  10.0.0.0/24   AZ a   0.0.0.0/0 -> IGW
  public  10.0.1.0/24   AZ b   0.0.0.0/0 -> IGW
  private 10.0.10.0/24  AZ a   0.0.0.0/0 -> NAT in AZ a
  private 10.0.11.0/24  AZ b   0.0.0.0/0 -> NAT in AZ b
  data    10.0.20.0/24  AZ a   no default route
  data    10.0.21.0/24  AZ b   no default route
```

| Piece | Behavior the exam uses |
| --- | --- |
| Internet Gateway | One is enough. It is a horizontally scaled VPC component. A second IGW is not an HA design |
| NAT Gateway | Lives in one AZ. Production puts one in each AZ and points that AZ's private route table at it. A single shared NAT is cheaper and dies with the AZ |
| NAT instance | A self-managed AMI. Cheaper at tiny scale, worse availability, you patch it. Loses "least operational overhead" |
| Egress-only IGW | IPv6 outbound. NAT Gateway is the IPv4 outbound tool |
| Route table | Longest prefix match. Local route for the VPC CIDR cannot be removed |
| Elastic IP | A public IPv4 you keep. Charged when it is not attached to a running instance, and public IPv4 has its own charge. ALB removes the need for one public IP per instance |

```bash
VPC=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query Vpc.VpcId --output text)
aws ec2 modify-vpc-attribute --vpc-id "$VPC" --enable-dns-support
aws ec2 modify-vpc-attribute --vpc-id "$VPC" --enable-dns-hostnames
aws ec2 create-internet-gateway
# then attach-internet-gateway, create-subnet, create-route-table, create-route, associate-route-table
aws ec2 create-nat-gateway --subnet-id "$PUB_A" --allocation-id "$EIP_ALLOC"
```

DNS hostnames must be on or public and private DNS names for instances do not exist. Interface endpoints need DNS hostnames and DNS support.

## Security groups and network ACLs

| | Security group | Network ACL |
| --- | --- | --- |
| Attached to | ENI (instance, ALB, RDS, Lambda, task) | Subnet |
| State | Stateful. Return traffic is allowed | Stateless. You must allow the return ephemeral ports |
| Rules | Allow only | Allow and deny, numbered, first match wins |
| Default | Default SG allows all inbound from itself | Default NACL allows all. A custom NACL starts with deny-all |
| Use | The normal control | A blunt subnet deny of a CIDR, or a compliance rule that demands a deny list |

Ephemeral ports: Linux often 1024–65535, Windows often 49152–65535. If a NACL allows inbound 443 and you forget the outbound ephemeral range, clients cannot complete TLS. Security groups do not have this bug because they are stateful.

Reference a security group id as the source. `sg-alb` inbound 443 from `0.0.0.0/0`. `sg-app` inbound 8080 from `sg-alb`. `sg-db` inbound 5432 from `sg-app`. Do not open 5432 to the VPC CIDR "to make it work."

## Endpoints

| Type | Services | Route | Price shape | Stem |
| --- | --- | --- | --- | --- |
| Gateway endpoint | S3, DynamoDB | Prefix list in the route table | No hourly charge, no data processing charge | Private subnet reaches S3 without NAT |
| Interface endpoint | Most other AWS APIs, and endpoint services | ENI in your subnet, private DNS | Hourly per AZ plus data processing | Private subnet reaches SQS, Secrets Manager, KMS, CloudWatch, Bedrock |
| Gateway Load Balancer endpoint | Inspection appliances | Next hop in the route table | The inspection pattern | Traffic must pass a firewall fleet |

An endpoint policy is a ceiling, like an SCP for that path. Private DNS on an interface endpoint makes the public service name resolve to the private ENI. Without it, the SDK still tries the public name and you need a custom endpoint URL.

```bash
aws ec2 create-vpc-endpoint --vpc-id "$VPC" --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway --route-table-ids "$RTB"
aws ec2 create-vpc-endpoint --vpc-id "$VPC" --service-name com.amazonaws.us-east-1.secretsmanager \
  --vpc-endpoint-type Interface --subnet-ids "$PRIV_A" "$PRIV_B" \
  --security-group-ids "$SG" --private-dns-enabled
```

## Connecting VPCs and data centers

| Need | Choice |
| --- | --- |
| Two VPCs, same or different Region, no third hop, no overlap | VPC peering. Not transitive. Routes are manual |
| Many VPCs, on-premises, shared services, transitive | Transit Gateway. Share it with RAM |
| A very large multi-Region WAN with segmentation | AWS Cloud WAN |
| One service exposed, not the whole VPC | PrivateLink. You publish an NLB. The consumer creates an interface endpoint |
| HTTP between services across VPCs and accounts, with auth | VPC Lattice. Heavier on SAP-C03. Already the right new design |
| Encrypted over the internet this week | Site-to-Site VPN |
| Steady multi-gigabit, consistent latency | Direct Connect. A VIF into a VGW or, more often now, a transit VIF onto a Transit Gateway |
| DX plus encryption the security team can name | VPN over DX, or MACsec where the port supports it |
| DX fails | A backup VPN, or a second DX location. One DX is a single point of failure |
| People, not networks | Client VPN, or IAM Identity Center plus Verified Access for applications without a full tunnel |
| Overlapping RFC1918 during migration | You cannot peer overlapping CIDRs. Private NAT, or re-address, or a transit account that NATs |

Hybrid DNS:

| Direction | Route 53 Resolver feature |
| --- | --- |
| VPC needs to resolve `corp.example.com` | Outbound endpoint plus a forwarding rule |
| On-premises needs to resolve a private hosted zone | Inbound endpoint. On-prem DNS forwards to the inbound IP |
| Share the rule with many VPCs | RAM |

## Seeing the traffic

| Tool | You get |
| --- | --- |
| VPC Flow Logs | Accepted and rejected flows to CloudWatch Logs or S3. Not packet payloads |
| Traffic Mirroring | A copy of packets to a security appliance. Heavier |
| Reachability Analyzer | "Can A reach B, and which rule stops it?" |
| Network Access Analyzer | Unintended paths, such as an internet gateway reaching a data subnet |
| Transit Gateway route analyzer | Routes across attachments |

Flow logs do not include traffic to the Amazon DNS resolver in the same way people expect, and they do not capture traffic dropped by a security group before it is a full connection in every case you might imagine. For the exam: rejected flows in the log mean a security group or NACL deny. Use them when the stem says "investigate who connected."

## Lambda, ECS, and RDS in the VPC

| Compute | What "in the VPC" means |
| --- | --- |
| Lambda | The function's ENIs are in the subnets you name. The security group must reach the database. To call S3, add a gateway endpoint or a NAT. Default Lambda (no VPC) has internet and public AWS APIs and cannot reach a private RDS |
| ECS on Fargate | `awsvpc` mode. The task has its own ENI and security group. Same NAT and endpoint rules |
| RDS | Lives in data subnets. `PubliclyAccessible=false`. The subnet group covers at least two AZs for Multi-AZ |
| ALB | Needs at least two subnets in two AZs. Internal ALBs go in private subnets and are reached through peering, TGW, or a VPN |

## Exercises

1. Private instances download patches from the internet and read from S3. NAT data-processing charges dominate the bill. What do you add, and what traffic still needs the NAT?
2. A NACL allows inbound TCP 443 and outbound TCP 443. Users time out. Why, and which control would not have this bug?
3. Three VPCs must talk, and next quarter a fourth VPC and a data center join. Peering or Transit Gateway?
4. A vendor must call one API you host. They must not route to your databases. PrivateLink or peering?
5. Lambda in a VPC times out calling Secrets Manager and times out calling RDS. You add a NAT Gateway and both succeed. The security team wants the AWS API off the NAT. What do you add, and does RDS still need the NAT?

## Answers

1. A gateway endpoint for S3. Patch downloads and other public internet still use the NAT. DynamoDB, if they use it, gets a gateway endpoint too.
2. Return traffic uses ephemeral ports, and NACLs are stateless. Allow the ephemeral range outbound (and the matching direction for your flow). A security group is stateful and would not require that rule.
3. Transit Gateway. Peering is a mesh and does not give you the data center attachment or transitivity.
4. PrivateLink. Peering gives a network path you then have to filter. PrivateLink gives an endpoint to the NLB in front of the API.
5. An interface endpoint for Secrets Manager with private DNS. RDS uses a private IP in the VPC. It never needed the NAT. The NAT was only covering Secrets Manager and any other public AWS API.

## Subnets, routes, and the two firewalls

A public subnet is a route table with `0.0.0.0/0` to an Internet Gateway. A public IP without that route does not create a public subnet. A private subnet that needs the internet points `0.0.0.0/0` at a NAT Gateway in a public subnet. The NAT has an Elastic IP. The private instances do not. One Internet Gateway per VPC is enough. It is not a zonal device. A NAT Gateway is zonal. One NAT for a Multi-AZ private fleet dies with that AZ.

Security groups are stateful and allow-only. Reference another security group, not a CIDR that will change when the Auto Scaling group replaces an instance. The database allows the app security group on the database port. The app allows the load balancer security group on the app port. NACLs are stateless, numbered, and can deny. A custom NACL starts by denying until you add rules. Inbound 443 without outbound ephemeral ports (1024–65535) times out. The default NACL allows all. The default security group allows inbound only from itself.

| Path from a private subnet | What you add |
| --- | --- |
| S3 or DynamoDB | Gateway endpoint on the route table. No hourly charge. No security group |
| Any other AWS API | Interface endpoint, private DNS, a security group the app can reach |
| A service another account published | PrivateLink. Their NLB, your interface endpoint. You do not learn their CIDR |
| The public internet | NAT, or do not |

CIDR planning: do not overlap, because peering and Transit Gateway routing will not sort it out for you. `/16` for the VPC and `/24` per subnet is the classroom layout. Leave space. A second Region is a second VPC, not a stretch of the first.

## More exercises

6. An instance in a "private" subnet has a public IP and no default route to an IGW. Can it receive a connection from the internet?
7. The app security group allows inbound 8080 from `10.0.0.0/16`. The ASG replaces the instances. Why is a security-group reference better?
8. Two AZs, one NAT, private route tables in both AZs point at it. What fails, and what do you add if outbound must survive an AZ?
9. You need to deny a CIDR to an entire subnet even if a security group is wrong. Which control?
10. Flow logs show REJECT. Reachability Analyzer says the NACL. Which one do you edit, and why was the security group not the answer?

## Answers

6. No. The route to the IGW is what makes the subnet public. A public IP without that route does not complete the path. Remove the public IP anyway so the next route edit does not expose it.
7. The `/16` allows every future subnet in the VPC, including a data subnet you did not mean to include, and it does not track the load balancer. A source security group id allows only ENIs that have that group.
8. The AZ that holds the NAT takes outbound internet away from both AZs, and the other AZ pays cross-AZ data charges to reach it. Add a NAT in each AZ and point each private route table at its own. Add gateway endpoints so S3 never needed the NAT.
9. A NACL. Security groups cannot deny.
10. The NACL. Reachability Analyzer already named the rule. Flow logs confirm the traffic was rejected. Opening the security group would not fix a NACL deny, because both must allow.
