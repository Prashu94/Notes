# Lab 02 — VPC, gateway endpoint, and the expensive designs you do not build

SAA tasks 1.2, 3.4, and 4.4. You will create a VPC and an S3 gateway endpoint, because those have no hourly charge. You will not create a NAT gateway, an interface endpoint, or a Transit Gateway attachment unless you set `RUN_PAID=1` and you know you will delete them within the hour.

Official: https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html

## Cost line

| Object | Charge |
| --- | --- |
| VPC, subnet, route table, security group | No hourly charge |
| Gateway endpoint (S3, DynamoDB) | No hourly charge |
| NAT gateway | Hourly plus data. This is the lab people forget |
| Interface endpoint | Hourly per AZ plus data |
| Transit Gateway attachment | Hourly per attachment |
| Public IPv4 address | Hourly |

## Part A — the VPC and the free endpoint

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
AZ1=$(aws ec2 describe-availability-zones --query 'AvailabilityZones[0].ZoneName' --output text)
AZ2=$(aws ec2 describe-availability-zones --query 'AvailabilityZones[1].ZoneName' --output text)

VPC=$(aws ec2 create-vpc --cidr-block 10.40.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=lab02}]' \
  --query Vpc.VpcId --output text)
aws ec2 modify-vpc-attribute --vpc-id "$VPC" --enable-dns-support
aws ec2 modify-vpc-attribute --vpc-id "$VPC" --enable-dns-hostnames

SUB_A=$(aws ec2 create-subnet --vpc-id "$VPC" --cidr-block 10.40.1.0/24 \
  --availability-zone "$AZ1" --query Subnet.SubnetId --output text)
SUB_B=$(aws ec2 create-subnet --vpc-id "$VPC" --cidr-block 10.40.2.0/24 \
  --availability-zone "$AZ2" --query Subnet.SubnetId --output text)

RT=$(aws ec2 create-route-table --vpc-id "$VPC" --query RouteTable.RouteTableId --output text)
aws ec2 associate-route-table --route-table-id "$RT" --subnet-id "$SUB_A"
aws ec2 associate-route-table --route-table-id "$RT" --subnet-id "$SUB_B"

EP=$(aws ec2 create-vpc-endpoint --vpc-id "$VPC" \
  --service-name "com.amazonaws.${AWS_DEFAULT_REGION}.s3" \
  --vpc-endpoint-type Gateway \
  --route-table-ids "$RT" \
  --query VpcEndpoint.VpcEndpointId --output text)

aws ec2 describe-route-tables --route-table-ids "$RT" \
  --query 'RouteTables[0].Routes'
```

The route you added is a prefix-list target, not a `0.0.0.0/0`. That is the exam picture of a gateway endpoint: S3 traffic from the private subnets goes to the endpoint, and there is still no path to the internet.

There is no IGW and no NAT. A private instance in this VPC could reach S3 and could not reach Secrets Manager, STS, or the public internet. That is the "Lambda in a VPC times out on Secrets Manager" item. The fix on the exam is an interface endpoint or a NAT, and the cheap fix in this account is the interface endpoint only if you accept the hourly charge.

## Part B — say the design out loud

Draw this and do not create it:

```text
On-premises -- DX primary, VPN backup
        |
   TGW in the network account (RAM share)
        |
 prod VPC     shared-services VPC     egress VPC (one NAT per AZ)
 each VPC: gateway endpoints for S3 and DynamoDB
 Resolver inbound + outbound for hybrid DNS
```

| Stem | You pick | You refuse |
| --- | --- | --- |
| Two VPCs, no growth | Peering | TGW |
| Many VPCs and on-premises, transitive | TGW | A mesh of peering |
| One API, databases stay unroutable | PrivateLink | Peering the whole VPC |
| HTTP between accounts, IAM on the call | VPC Lattice | Peering plus a wide security group |
| Overlapping CIDRs | Private NAT | Peering |
| S3 from a private subnet, no other AWS API | Gateway endpoint | NAT, and not an interface endpoint |
| KMS, SQS, Secrets Manager, Bedrock from a private subnet | Interface endpoint, private DNS on | A gateway endpoint. Those services do not have one |

Security group versus NACL, because this lab's empty VPC is where people forget: a security group is stateful, so the return traffic is allowed. A NACL is stateless, so the ephemeral ports (1024–65535) must be allowed back in. Default NACL allows all. Default security group allows inbound only from itself.

## Part C — paid objects, only with the flag

Do not run this block on a first pass.

```bash
if [ "$RUN_PAID" = "1" ]; then
  echo "You are about to pay for a NAT gateway and an interface endpoint. Delete them in cleanup."
  # IGW + public subnet + NAT is the usual path. Prefer the console wizard only if you
  # already know which resources you will delete. Hourly charges start at create time.
fi
```

## Cleanup

Gateway endpoints and subnets must go before the VPC.

```bash
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids "$EP"
aws ec2 delete-subnet --subnet-id "$SUB_A"
aws ec2 delete-subnet --subnet-id "$SUB_B"
# Disassociate the explicit associations, then delete the route table.
ASSOC=$(aws ec2 describe-route-tables --route-table-ids "$RT" \
  --query 'RouteTables[0].Associations[?Main==`false`].RouteTableAssociationId' --output text)
for A in $ASSOC; do aws ec2 disassociate-route-table --association-id "$A"; done
aws ec2 delete-route-table --route-table-id "$RT"
aws ec2 delete-vpc --vpc-id "$VPC"
```

If `delete-vpc` says there are dependencies, you left an endpoint, a security group you created, or a NAT. `describe-vpc-endpoints`, `describe-nat-gateways`, and `describe-internet-gateways` filtered by this VPC are the three commands that find the bill.
