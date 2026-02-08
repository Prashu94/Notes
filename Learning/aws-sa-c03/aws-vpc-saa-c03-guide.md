# AWS VPC (Virtual Private Cloud) - SAA-C03 Certification Guide

## Table of Contents
1. [VPC Fundamentals](#vpc-fundamentals)
2. [VPC Components](#vpc-components)
3. [VPC Connectivity](#vpc-connectivity)
4. [Advanced VPC Features](#advanced-vpc-features)
5. [VPC Security](#vpc-security)
6. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
7. [AWS CLI Commands Reference](#aws-cli-commands-reference)
8. [Exam Tips and Common Scenarios](#exam-tips-and-common-scenarios)

---

## VPC Fundamentals

### What is Amazon VPC?

Amazon Virtual Private Cloud (VPC) is a service that allows you to launch AWS resources in a logically isolated virtual network. You have complete control over your virtual networking environment, including:

- Selection of IP address range
- Creation of subnets
- Configuration of route tables and network gateways
- Security settings using security groups and NACLs

### Key VPC Concepts

#### CIDR Blocks (Classless Inter-Domain Routing)

**Primary CIDR Block:**
- Each VPC must have a primary CIDR block (e.g., 10.0.0.0/16)
- Minimum size: /28 (16 IP addresses)
- Maximum size: /16 (65,536 IP addresses)
- Cannot be changed after VPC creation

**Secondary CIDR Blocks:**
- Up to 4 additional CIDR blocks can be associated
- Must not overlap with existing CIDR blocks
- Useful for expanding IP address space

**Reserved IP Addresses:**
In each subnet, AWS reserves 5 IP addresses:
- Network address (e.g., 10.0.0.0)
- VPC router (e.g., 10.0.0.1)
- DNS server (e.g., 10.0.0.2)
- Future use (e.g., 10.0.0.3)
- Broadcast address (e.g., 10.0.0.255)

### Subnets

#### Public Subnets
- Have a route to an Internet Gateway
- Resources can have public IP addresses
- Used for web servers, load balancers, bastion hosts

#### Private Subnets
- No direct route to Internet Gateway
- Resources typically use NAT Gateway/Instance for outbound internet access
- Used for application servers, databases

#### Subnet Sizing Best Practices
```
Example VPC: 10.0.0.0/16 (65,536 IPs)

Public Subnets:
- 10.0.1.0/24 (AZ-a) - 256 IPs
- 10.0.2.0/24 (AZ-b) - 256 IPs
- 10.0.3.0/24 (AZ-c) - 256 IPs

Private Subnets:
- 10.0.11.0/24 (AZ-a) - 256 IPs
- 10.0.12.0/24 (AZ-b) - 256 IPs
- 10.0.13.0/24 (AZ-c) - 256 IPs

Database Subnets:
- 10.0.21.0/24 (AZ-a) - 256 IPs
- 10.0.22.0/24 (AZ-b) - 256 IPs
- 10.0.23.0/24 (AZ-c) - 256 IPs
```

### Availability Zones and Multi-AZ Deployments

#### Best Practices:
- Distribute subnets across multiple AZs for high availability
- Each AZ should have at least one public and one private subnet
- Use at least 2 AZs for production workloads
- Consider using 3 AZs for critical applications

---

## VPC Components

### Internet Gateway (IGW)

**Characteristics:**
- Horizontally scaled, redundant, and highly available
- One IGW per VPC
- No bandwidth constraints
- Supports IPv4 and IPv6

**Functions:**
- Provides internet connectivity for public subnets
- Performs NAT for instances with public IP addresses
- Route target for internet-bound traffic

### NAT Gateway

**Use Cases:**
- Enable private subnet instances to access the internet
- Software updates, patches, and downloads
- Outbound API calls

**Characteristics:**
- Managed service (AWS handles scaling, patching)
- Deployed in public subnet
- Requires Elastic IP address
- Supports up to 45 Gbps bandwidth
- Charged per hour and data processed

**High Availability:**
- Deploy one NAT Gateway per AZ for redundancy
- Cross-AZ failover not automatic

### NAT Instance

**When to Use:**
- Cost optimization for low traffic scenarios
- Need for custom configurations
- Port forwarding requirements

**Limitations:**
- Single point of failure
- Manual scaling required
- Security group management needed

### Route Tables

**Types:**
- **Main Route Table:** Default for all subnets not explicitly associated
- **Custom Route Tables:** Created for specific routing requirements

**Route Priority:**
1. Most specific route (longest prefix match)
2. Local routes always take priority
3. Static routes over propagated routes

**Common Routes:**
```
Destination         Target
10.0.0.0/16        Local
0.0.0.0/0          igw-xxxxx (Internet Gateway)
0.0.0.0/0          nat-xxxxx (NAT Gateway)
```

### Security Groups

**Characteristics:**
- Stateful firewall (return traffic automatically allowed)
- Default deny all inbound, allow all outbound
- Only allow rules (no deny rules)
- Can reference other security groups
- Applied at instance level

**Best Practices:**
- Use descriptive names and descriptions
- Follow principle of least privilege
- Create separate security groups for different tiers
- Use security group references instead of IP addresses

**Example Security Group Rules:**
```
Web Server Security Group:
Inbound:
- HTTP (80) from 0.0.0.0/0
- HTTPS (443) from 0.0.0.0/0
- SSH (22) from Bastion-SG

Application Server Security Group:
Inbound:
- Port 8080 from Web-Server-SG
- SSH (22) from Bastion-SG

Database Security Group:
Inbound:
- MySQL (3306) from App-Server-SG
```

### Network ACLs (NACLs)

**Characteristics:**
- Stateless firewall (must configure both inbound and outbound rules)
- Default NACL allows all traffic
- Custom NACLs deny all traffic by default
- Rules processed in numerical order
- Applied at subnet level

**Key Differences from Security Groups:**
| Feature | Security Groups | NACLs |
|---------|----------------|--------|
| Scope | Instance level | Subnet level |
| State | Stateful | Stateless |
| Rules | Allow only | Allow and Deny |
| Rule Processing | All rules evaluated | Processed in order |

---

## VPC Connectivity

### VPC Peering

**Use Cases:**
- Connect VPCs within same or different AWS accounts
- Cross-region connectivity
- Resource sharing between environments

**Limitations:**
- No transitive peering
- No overlapping CIDR blocks
- Maximum 125 peering connections per VPC

**Configuration Requirements:**
- Accept peering connection
- Update route tables
- Configure security groups/NACLs

### Transit Gateway

**Benefits:**
- Simplifies network connectivity
- Supports transitive routing
- Central hub for multiple VPCs
- Cross-region peering support

**Key Features:**
- Up to 5,000 VPCs per Transit Gateway
- Multicast support
- Direct Connect Gateway integration
- VPN connection support

**Route Tables:**
- Default propagation and association
- Custom route tables for segmentation
- Blackhole routes for traffic blocking

### AWS Direct Connect

**Use Cases:**
- Dedicated network connection to AWS
- Lower bandwidth costs for high data transfer
- More consistent network performance
- Compliance requirements

**Virtual Interfaces (VIFs):**
- **Private VIF:** Access VPC resources
- **Public VIF:** Access public AWS services
- **Transit VIF:** Connect to Transit Gateway

### VPN Connections

#### Site-to-Site VPN
- IPSec VPN connection
- Two tunnels for redundancy
- Static or dynamic (BGP) routing

#### Client VPN
- Managed client-based VPN service
- OpenVPN-based
- Integrates with Active Directory

---

## Advanced VPC Features

### VPC Endpoints

#### Interface Endpoints (PrivateLink)
**Characteristics:**
- Elastic Network Interface with private IP
- DNS names for service access
- Security group support
- Charges per hour and data processed

**Supported Services:**
- S3, DynamoDB, Lambda, SNS, SQS
- EC2, CloudFormation, Systems Manager
- Third-party services via PrivateLink

#### Gateway Endpoints
**Characteristics:**
- Route table entry (not ENI)
- No additional charges
- Only supports S3 and DynamoDB

**Configuration:**
```
Route Table Entry:
Destination: pl-xxxxx (S3 prefix list)
Target: vpce-xxxxx (VPC Endpoint)
```

### VPC Flow Logs

**Log Destinations:**
- CloudWatch Logs
- S3 bucket
- Kinesis Data Firehose

**Capture Levels:**
- VPC level
- Subnet level  
- Network Interface level

**Use Cases:**
- Security monitoring
- Troubleshooting connectivity
- Network analytics
- Compliance auditing

### DNS Resolution

**DNS Attributes:**
- **enableDnsHostnames:** Assigns public DNS hostnames
- **enableDnsSupport:** Enables DNS resolution

**Route 53 Resolver:**
- Hybrid DNS resolution
- Conditional forwarding rules
- Integration with on-premises DNS

### Elastic Network Interfaces (ENIs)

**Use Cases:**
- Multiple IP addresses per instance
- Network interface failover
- Licensing based on MAC addresses

**Characteristics:**
- Can be attached/detached from instances
- Retain private IP and MAC address
- Security group associations

---

## VPC Security

### Defense in Depth Strategy

#### Network Level Security
1. **NACLs:** Subnet-level filtering
2. **Security Groups:** Instance-level filtering
3. **Route Tables:** Traffic direction control

#### Application Level Security
1. **WAF:** Web application firewall
2. **Shield:** DDoS protection
3. **GuardDuty:** Threat detection

### Security Groups vs NACLs Comparison

#### When to Use Security Groups:
- Instance-specific rules
- Application-tier security
- Dynamic environments
- Rule simplicity preferred

#### When to Use NACLs:
- Subnet-wide protection
- Compliance requirements
- Deny rules needed
- Additional security layer

### Bastion Host Architecture

**Best Practices:**
- Deploy in public subnet
- Minimize attack surface
- Use IAM roles instead of keys when possible
- Implement session logging
- Regular security updates

**Alternative Solutions:**
- AWS Systems Manager Session Manager
- AWS Client VPN
- Direct Connect with private connectivity

### Network Segmentation

**Micro-segmentation Strategies:**
```
Three-Tier Architecture:
├── Public Subnet (Web Tier)
│   ├── Application Load Balancer
│   └── Bastion Hosts
├── Private Subnet (App Tier)
│   ├── Web Servers
│   └── Application Servers
└── Private Subnet (Data Tier)
    ├── RDS Instances
    └── ElastiCache Clusters
```

---

## Monitoring and Troubleshooting

### VPC Flow Logs Analysis

**Log Format:**
```
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes windowstart windowend action flowlogstatus
```

**Common Analysis Patterns:**
- **REJECT actions:** Security group/NACL blocking
- **High packet counts:** Potential DDoS
- **Unusual source IPs:** Security investigation needed

### CloudWatch Metrics

**Network-Related Metrics:**
- NetworkIn/NetworkOut
- NetworkPacketsIn/NetworkPacketsOut
- NetworkLatency (for some services)

### Common Connectivity Issues

#### Instance Cannot Access Internet
**Troubleshooting Steps:**
1. Check if subnet has route to IGW/NAT Gateway
2. Verify security group outbound rules
3. Check NACL rules
4. Confirm instance has public IP (for direct internet access)

#### Cannot Connect to Instance
**Troubleshooting Steps:**
1. Verify security group inbound rules
2. Check NACL inbound rules
3. Confirm route table configuration
4. Check instance status and security

#### High Data Transfer Costs
**Optimization Strategies:**
1. Use VPC Endpoints for AWS services
2. Implement caching strategies
3. Optimize cross-AZ traffic
4. Consider Direct Connect for high volume

### VPC Reachability Analyzer

**Use Cases:**
- Path analysis between source and destination
- Troubleshoot connectivity issues
- Validate network configuration changes
- Security posture assessment

---

## AWS CLI Commands Reference

### VPC Management

#### Create and Delete VPC
```bash
# Create a VPC
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MyVPC}]'

# Create VPC with IPv6 CIDR block
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --amazon-provided-ipv6-cidr-block

# Describe VPCs
aws ec2 describe-vpcs

# Describe specific VPC
aws ec2 describe-vpcs --vpc-ids vpc-0123456789abcdef0

# Describe VPCs with filters
aws ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=MyVPC"

# Add secondary CIDR block to VPC
aws ec2 associate-vpc-cidr-block \
    --vpc-id vpc-0123456789abcdef0 \
    --cidr-block 10.1.0.0/16

# Remove secondary CIDR block
aws ec2 disassociate-vpc-cidr-block \
    --association-id vpc-cidr-assoc-0123456789abcdef0

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id vpc-0123456789abcdef0 \
    --enable-dns-hostnames

# Enable DNS support
aws ec2 modify-vpc-attribute \
    --vpc-id vpc-0123456789abcdef0 \
    --enable-dns-support

# Delete VPC
aws ec2 delete-vpc --vpc-id vpc-0123456789abcdef0
```

### Subnet Management

#### Create and Manage Subnets
```bash
# Create a subnet
aws ec2 create-subnet \
    --vpc-id vpc-0123456789abcdef0 \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=PublicSubnet1}]'

# Create subnet with IPv6
aws ec2 create-subnet \
    --vpc-id vpc-0123456789abcdef0 \
    --cidr-block 10.0.2.0/24 \
    --ipv6-cidr-block 2600:1f13:fe3:5c00::/64 \
    --availability-zone us-east-1b

# Describe subnets
aws ec2 describe-subnets

# Describe subnets in a specific VPC
aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0"

# Describe specific subnet
aws ec2 describe-subnets --subnet-ids subnet-0123456789abcdef0

# Enable auto-assign public IPv4
aws ec2 modify-subnet-attribute \
    --subnet-id subnet-0123456789abcdef0 \
    --map-public-ip-on-launch

# Disable auto-assign public IPv4
aws ec2 modify-subnet-attribute \
    --subnet-id subnet-0123456789abcdef0 \
    --no-map-public-ip-on-launch

# Enable auto-assign IPv6
aws ec2 modify-subnet-attribute \
    --subnet-id subnet-0123456789abcdef0 \
    --assign-ipv6-address-on-creation

# Delete subnet
aws ec2 delete-subnet --subnet-id subnet-0123456789abcdef0
```

### Internet Gateway Operations

#### Create and Attach Internet Gateway
```bash
# Create Internet Gateway
aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=MyIGW}]'

# Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id igw-0123456789abcdef0 \
    --vpc-id vpc-0123456789abcdef0

# Describe Internet Gateways
aws ec2 describe-internet-gateways

# Describe specific Internet Gateway
aws ec2 describe-internet-gateways \
    --internet-gateway-ids igw-0123456789abcdef0

# Describe Internet Gateways attached to a VPC
aws ec2 describe-internet-gateways \
    --filters "Name=attachment.vpc-id,Values=vpc-0123456789abcdef0"

# Detach Internet Gateway from VPC
aws ec2 detach-internet-gateway \
    --internet-gateway-id igw-0123456789abcdef0 \
    --vpc-id vpc-0123456789abcdef0

# Delete Internet Gateway
aws ec2 delete-internet-gateway \
    --internet-gateway-id igw-0123456789abcdef0
```

### NAT Gateway Operations

#### Create and Manage NAT Gateway
```bash
# Create NAT Gateway (requires Elastic IP)
aws ec2 create-nat-gateway \
    --subnet-id subnet-0123456789abcdef0 \
    --allocation-id eipalloc-0123456789abcdef0 \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=MyNATGateway}]'

# Describe NAT Gateways
aws ec2 describe-nat-gateways

# Describe specific NAT Gateway
aws ec2 describe-nat-gateways \
    --nat-gateway-ids nat-0123456789abcdef0

# Describe NAT Gateways in a specific VPC
aws ec2 describe-nat-gateways \
    --filter "Name=vpc-id,Values=vpc-0123456789abcdef0"

# Describe NAT Gateways by state
aws ec2 describe-nat-gateways \
    --filter "Name=state,Values=available"

# Delete NAT Gateway
aws ec2 delete-nat-gateway \
    --nat-gateway-id nat-0123456789abcdef0
```

### Route Table Management

#### Create and Manage Route Tables
```bash
# Create route table
aws ec2 create-route-table \
    --vpc-id vpc-0123456789abcdef0 \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=PublicRouteTable}]'

# Describe route tables
aws ec2 describe-route-tables

# Describe route tables in a specific VPC
aws ec2 describe-route-tables \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0"

# Describe specific route table
aws ec2 describe-route-tables \
    --route-table-ids rtb-0123456789abcdef0

# Create route to Internet Gateway
aws ec2 create-route \
    --route-table-id rtb-0123456789abcdef0 \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id igw-0123456789abcdef0

# Create route to NAT Gateway
aws ec2 create-route \
    --route-table-id rtb-0123456789abcdef0 \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id nat-0123456789abcdef0

# Create route to VPC Peering Connection
aws ec2 create-route \
    --route-table-id rtb-0123456789abcdef0 \
    --destination-cidr-block 10.1.0.0/16 \
    --vpc-peering-connection-id pcx-0123456789abcdef0

# Create route to Transit Gateway
aws ec2 create-route \
    --route-table-id rtb-0123456789abcdef0 \
    --destination-cidr-block 10.2.0.0/16 \
    --transit-gateway-id tgw-0123456789abcdef0

# Delete route
aws ec2 delete-route \
    --route-table-id rtb-0123456789abcdef0 \
    --destination-cidr-block 0.0.0.0/0

# Associate route table with subnet
aws ec2 associate-route-table \
    --route-table-id rtb-0123456789abcdef0 \
    --subnet-id subnet-0123456789abcdef0

# Disassociate route table from subnet
aws ec2 disassociate-route-table \
    --association-id rtbassoc-0123456789abcdef0

# Replace route table association
aws ec2 replace-route-table-association \
    --association-id rtbassoc-0123456789abcdef0 \
    --route-table-id rtb-0fedcba9876543210

# Delete route table
aws ec2 delete-route-table \
    --route-table-id rtb-0123456789abcdef0
```

### Security Group Operations

#### Create and Manage Security Groups
```bash
# Create security group
aws ec2 create-security-group \
    --group-name MySecurityGroup \
    --description "Security group for web servers" \
    --vpc-id vpc-0123456789abcdef0 \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=WebServerSG}]'

# Describe security groups
aws ec2 describe-security-groups

# Describe security groups in a specific VPC
aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0"

# Describe specific security group
aws ec2 describe-security-groups \
    --group-ids sg-0123456789abcdef0

# Add inbound rule (SSH from specific IP)
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 22 \
    --cidr 203.0.113.0/24

# Add inbound rule (HTTP from anywhere)
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Add inbound rule (HTTPS from anywhere)
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Add inbound rule from another security group
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 3306 \
    --source-group sg-0fedcba9876543210

# Add multiple rules at once using JSON
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --ip-permissions '[{"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}, {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]'

# Remove inbound rule
aws ec2 revoke-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Add outbound rule
aws ec2 authorize-security-group-egress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Remove outbound rule
aws ec2 revoke-security-group-egress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Update security group description
aws ec2 update-security-group-rule-descriptions-ingress \
    --group-id sg-0123456789abcdef0 \
    --ip-permissions '[{"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "203.0.113.0/24", "Description": "SSH from office"}]}]'

# Delete security group
aws ec2 delete-security-group \
    --group-id sg-0123456789abcdef0
```

### Network ACL Operations

#### Create and Manage Network ACLs
```bash
# Create network ACL
aws ec2 create-network-acl \
    --vpc-id vpc-0123456789abcdef0 \
    --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=MyNACL}]'

# Describe network ACLs
aws ec2 describe-network-acls

# Describe network ACLs in a specific VPC
aws ec2 describe-network-acls \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0"

# Describe specific network ACL
aws ec2 describe-network-acls \
    --network-acl-ids acl-0123456789abcdef0

# Create inbound rule (allow HTTP)
aws ec2 create-network-acl-entry \
    --network-acl-id acl-0123456789abcdef0 \
    --rule-number 100 \
    --protocol tcp \
    --port-range From=80,To=80 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --ingress

# Create inbound rule (allow HTTPS)
aws ec2 create-network-acl-entry \
    --network-acl-id acl-0123456789abcdef0 \
    --rule-number 110 \
    --protocol tcp \
    --port-range From=443,To=443 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --ingress

# Create inbound rule (allow ephemeral ports)
aws ec2 create-network-acl-entry \
    --network-acl-id acl-0123456789abcdef0 \
    --rule-number 120 \
    --protocol tcp \
    --port-range From=1024,To=65535 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --ingress

# Create outbound rule (allow all)
aws ec2 create-network-acl-entry \
    --network-acl-id acl-0123456789abcdef0 \
    --rule-number 100 \
    --protocol -1 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --egress

# Create rule to deny specific IP
aws ec2 create-network-acl-entry \
    --network-acl-id acl-0123456789abcdef0 \
    --rule-number 50 \
    --protocol -1 \
    --cidr-block 203.0.113.100/32 \
    --rule-action deny \
    --ingress

# Delete network ACL entry
aws ec2 delete-network-acl-entry \
    --network-acl-id acl-0123456789abcdef0 \
    --rule-number 100 \
    --ingress

# Replace network ACL entry
aws ec2 replace-network-acl-entry \
    --network-acl-id acl-0123456789abcdef0 \
    --rule-number 100 \
    --protocol tcp \
    --port-range From=80,To=80 \
    --cidr-block 10.0.0.0/16 \
    --rule-action allow \
    --ingress

# Associate network ACL with subnet
aws ec2 replace-network-acl-association \
    --association-id aclassoc-0123456789abcdef0 \
    --network-acl-id acl-0123456789abcdef0

# Delete network ACL
aws ec2 delete-network-acl \
    --network-acl-id acl-0123456789abcdef0
```

### VPC Peering Operations

#### Create and Manage VPC Peering Connections
```bash
# Create VPC peering connection
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-0123456789abcdef0 \
    --peer-vpc-id vpc-0fedcba9876543210 \
    --peer-region us-west-2 \
    --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=VPCPeering}]'

# Create VPC peering connection to another account
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-0123456789abcdef0 \
    --peer-vpc-id vpc-0fedcba9876543210 \
    --peer-owner-id 123456789012 \
    --peer-region us-west-2

# Accept VPC peering connection
aws ec2 accept-vpc-peering-connection \
    --vpc-peering-connection-id pcx-0123456789abcdef0

# Reject VPC peering connection
aws ec2 reject-vpc-peering-connection \
    --vpc-peering-connection-id pcx-0123456789abcdef0

# Describe VPC peering connections
aws ec2 describe-vpc-peering-connections

# Describe specific VPC peering connection
aws ec2 describe-vpc-peering-connections \
    --vpc-peering-connection-ids pcx-0123456789abcdef0

# Describe VPC peering connections for a VPC
aws ec2 describe-vpc-peering-connections \
    --filters "Name=requester-vpc-info.vpc-id,Values=vpc-0123456789abcdef0"

# Modify VPC peering connection options (requester side)
aws ec2 modify-vpc-peering-connection-options \
    --vpc-peering-connection-id pcx-0123456789abcdef0 \
    --requester-peering-connection-options AllowDnsResolutionFromRemoteVpc=true

# Modify VPC peering connection options (accepter side)
aws ec2 modify-vpc-peering-connection-options \
    --vpc-peering-connection-id pcx-0123456789abcdef0 \
    --accepter-peering-connection-options AllowDnsResolutionFromRemoteVpc=true

# Delete VPC peering connection
aws ec2 delete-vpc-peering-connection \
    --vpc-peering-connection-id pcx-0123456789abcdef0
```

### VPC Endpoint Operations

#### Create and Manage VPC Endpoints
```bash
# Create Gateway VPC Endpoint (S3)
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --service-name com.amazonaws.us-east-1.s3 \
    --route-table-ids rtb-0123456789abcdef0 \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=S3Endpoint}]'

# Create Gateway VPC Endpoint (DynamoDB)
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --service-name com.amazonaws.us-east-1.dynamodb \
    --route-table-ids rtb-0123456789abcdef0

# Create Interface VPC Endpoint (EC2)
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.ec2 \
    --subnet-ids subnet-0123456789abcdef0 subnet-0fedcba9876543210 \
    --security-group-ids sg-0123456789abcdef0 \
    --private-dns-enabled

# Create Interface VPC Endpoint (Systems Manager)
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0123456789abcdef0 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.ssm \
    --subnet-ids subnet-0123456789abcdef0 \
    --security-group-ids sg-0123456789abcdef0

# Describe VPC endpoints
aws ec2 describe-vpc-endpoints

# Describe VPC endpoints in a specific VPC
aws ec2 describe-vpc-endpoints \
    --filters "Name=vpc-id,Values=vpc-0123456789abcdef0"

# Describe specific VPC endpoint
aws ec2 describe-vpc-endpoints \
    --vpc-endpoint-ids vpce-0123456789abcdef0

# Describe available VPC endpoint services
aws ec2 describe-vpc-endpoint-services

# Describe VPC endpoint services by name
aws ec2 describe-vpc-endpoint-services \
    --filters "Name=service-name,Values=com.amazonaws.us-east-1.s3"

# Modify VPC endpoint (add route table)
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --add-route-table-ids rtb-0fedcba9876543210

# Modify VPC endpoint (remove route table)
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --remove-route-table-ids rtb-0123456789abcdef0

# Modify VPC endpoint (add subnet)
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --add-subnet-ids subnet-0fedcba9876543210

# Modify VPC endpoint (add security group)
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --add-security-group-ids sg-0fedcba9876543210

# Enable private DNS for VPC endpoint
aws ec2 modify-vpc-endpoint \
    --vpc-endpoint-id vpce-0123456789abcdef0 \
    --private-dns-enabled

# Delete VPC endpoint
aws ec2 delete-vpc-endpoints \
    --vpc-endpoint-ids vpce-0123456789abcdef0
```

### Elastic IP Operations

#### Allocate and Manage Elastic IPs
```bash
# Allocate Elastic IP for VPC
aws ec2 allocate-address \
    --domain vpc \
    --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=MyEIP}]'

# Describe Elastic IPs
aws ec2 describe-addresses

# Describe specific Elastic IP
aws ec2 describe-addresses \
    --allocation-ids eipalloc-0123456789abcdef0

# Describe Elastic IPs by filter
aws ec2 describe-addresses \
    --filters "Name=domain,Values=vpc"

# Associate Elastic IP with instance
aws ec2 associate-address \
    --instance-id i-0123456789abcdef0 \
    --allocation-id eipalloc-0123456789abcdef0

# Associate Elastic IP with network interface
aws ec2 associate-address \
    --network-interface-id eni-0123456789abcdef0 \
    --allocation-id eipalloc-0123456789abcdef0

# Associate Elastic IP with private IP address
aws ec2 associate-address \
    --instance-id i-0123456789abcdef0 \
    --allocation-id eipalloc-0123456789abcdef0 \
    --private-ip-address 10.0.1.100

# Disassociate Elastic IP
aws ec2 disassociate-address \
    --association-id eipassoc-0123456789abcdef0

# Release Elastic IP
aws ec2 release-address \
    --allocation-id eipalloc-0123456789abcdef0

# Move Elastic IP to another account (Step 1: Enable transfer)
aws ec2 enable-address-transfer \
    --allocation-id eipalloc-0123456789abcdef0 \
    --transfer-account-id 123456789012

# Move Elastic IP to another account (Step 2: Accept transfer)
aws ec2 accept-address-transfer \
    --address eipalloc-0123456789abcdef0
```

### VPC Flow Logs

#### Create and Manage VPC Flow Logs
```bash
# Create VPC Flow Logs to CloudWatch Logs
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flowlogs \
    --deliver-logs-permission-arn arn:aws:iam::123456789012:role/flowlogsRole \
    --tag-specifications 'ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=VPCFlowLogs}]'

# Create VPC Flow Logs to S3
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type s3 \
    --log-destination arn:aws:s3:::my-flow-logs-bucket/vpc-flow-logs/

# Create Flow Logs for subnet
aws ec2 create-flow-logs \
    --resource-type Subnet \
    --resource-ids subnet-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flowlogs

# Create Flow Logs for network interface
aws ec2 create-flow-logs \
    --resource-type NetworkInterface \
    --resource-ids eni-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flowlogs

# Create Flow Logs with custom format
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type s3 \
    --log-destination arn:aws:s3:::my-flow-logs-bucket/ \
    --log-format '${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${bytes} ${action}'

# Create Flow Logs for ACCEPT traffic only
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type ACCEPT \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flowlogs-accept

# Create Flow Logs for REJECT traffic only
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type REJECT \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flowlogs-reject

# Describe Flow Logs
aws ec2 describe-flow-logs

# Describe Flow Logs for specific VPC
aws ec2 describe-flow-logs \
    --filter "Name=resource-id,Values=vpc-0123456789abcdef0"

# Describe specific Flow Log
aws ec2 describe-flow-logs \
    --flow-log-ids fl-0123456789abcdef0

# Delete Flow Logs
aws ec2 delete-flow-logs \
    --flow-log-ids fl-0123456789abcdef0
```

### Network Interface Operations

#### Create and Manage Network Interfaces (ENIs)
```bash
# Create network interface
aws ec2 create-network-interface \
    --subnet-id subnet-0123456789abcdef0 \
    --description "Primary network interface" \
    --groups sg-0123456789abcdef0 \
    --private-ip-address 10.0.1.100 \
    --tag-specifications 'ResourceType=network-interface,Tags=[{Key=Name,Value=MyENI}]'

# Create network interface with secondary private IPs
aws ec2 create-network-interface \
    --subnet-id subnet-0123456789abcdef0 \
    --groups sg-0123456789abcdef0 \
    --secondary-private-ip-address-count 2

# Describe network interfaces
aws ec2 describe-network-interfaces

# Describe network interfaces in a subnet
aws ec2 describe-network-interfaces \
    --filters "Name=subnet-id,Values=subnet-0123456789abcdef0"

# Describe specific network interface
aws ec2 describe-network-interfaces \
    --network-interface-ids eni-0123456789abcdef0

# Attach network interface to instance
aws ec2 attach-network-interface \
    --network-interface-id eni-0123456789abcdef0 \
    --instance-id i-0123456789abcdef0 \
    --device-index 1

# Detach network interface
aws ec2 detach-network-interface \
    --attachment-id eni-attach-0123456789abcdef0 \
    --force

# Modify network interface attribute (description)
aws ec2 modify-network-interface-attribute \
    --network-interface-id eni-0123456789abcdef0 \
    --description "Updated description"

# Modify network interface attribute (security groups)
aws ec2 modify-network-interface-attribute \
    --network-interface-id eni-0123456789abcdef0 \
    --groups sg-0123456789abcdef0 sg-0fedcba9876543210

# Modify network interface attribute (source/dest check)
aws ec2 modify-network-interface-attribute \
    --network-interface-id eni-0123456789abcdef0 \
    --no-source-dest-check

# Assign private IP addresses
aws ec2 assign-private-ip-addresses \
    --network-interface-id eni-0123456789abcdef0 \
    --private-ip-addresses 10.0.1.101 10.0.1.102

# Assign private IP addresses (let AWS choose)
aws ec2 assign-private-ip-addresses \
    --network-interface-id eni-0123456789abcdef0 \
    --secondary-private-ip-address-count 2

# Unassign private IP addresses
aws ec2 unassign-private-ip-addresses \
    --network-interface-id eni-0123456789abcdef0 \
    --private-ip-addresses 10.0.1.101

# Assign IPv6 addresses
aws ec2 assign-ipv6-addresses \
    --network-interface-id eni-0123456789abcdef0 \
    --ipv6-address-count 1

# Unassign IPv6 addresses
aws ec2 unassign-ipv6-addresses \
    --network-interface-id eni-0123456789abcdef0 \
    --ipv6-addresses 2001:db8:1234:1a00::123

# Delete network interface
aws ec2 delete-network-interface \
    --network-interface-id eni-0123456789abcdef0
```

### Transit Gateway Operations

#### Create and Manage Transit Gateway
```bash
# Create Transit Gateway
aws ec2 create-transit-gateway \
    --description "My Transit Gateway" \
    --options AmazonSideAsn=64512,AutoAcceptSharedAttachments=enable,DefaultRouteTableAssociation=enable,DefaultRouteTablePropagation=enable \
    --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=MyTGW}]'

# Describe Transit Gateways
aws ec2 describe-transit-gateways

# Describe specific Transit Gateway
aws ec2 describe-transit-gateways \
    --transit-gateway-ids tgw-0123456789abcdef0

# Create Transit Gateway VPC attachment
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id tgw-0123456789abcdef0 \
    --vpc-id vpc-0123456789abcdef0 \
    --subnet-ids subnet-0123456789abcdef0 subnet-0fedcba9876543210 \
    --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=VPCAttachment}]'

# Describe Transit Gateway attachments
aws ec2 describe-transit-gateway-attachments

# Describe Transit Gateway VPC attachments
aws ec2 describe-transit-gateway-vpc-attachments

# Accept Transit Gateway VPC attachment
aws ec2 accept-transit-gateway-vpc-attachment \
    --transit-gateway-attachment-id tgw-attach-0123456789abcdef0

# Delete Transit Gateway VPC attachment
aws ec2 delete-transit-gateway-vpc-attachment \
    --transit-gateway-attachment-id tgw-attach-0123456789abcdef0

# Delete Transit Gateway
aws ec2 delete-transit-gateway \
    --transit-gateway-id tgw-0123456789abcdef0
```

### VPN Connection Operations

#### Create and Manage VPN Connections
```bash
# Create Customer Gateway
aws ec2 create-customer-gateway \
    --type ipsec.1 \
    --public-ip 203.0.113.12 \
    --bgp-asn 65000 \
    --tag-specifications 'ResourceType=customer-gateway,Tags=[{Key=Name,Value=MyCGW}]'

# Create Virtual Private Gateway
aws ec2 create-vpn-gateway \
    --type ipsec.1 \
    --amazon-side-asn 64512 \
    --tag-specifications 'ResourceType=vpn-gateway,Tags=[{Key=Name,Value=MyVGW}]'

# Attach Virtual Private Gateway to VPC
aws ec2 attach-vpn-gateway \
    --vpn-gateway-id vgw-0123456789abcdef0 \
    --vpc-id vpc-0123456789abcdef0

# Create VPN Connection
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id cgw-0123456789abcdef0 \
    --vpn-gateway-id vgw-0123456789abcdef0 \
    --tag-specifications 'ResourceType=vpn-connection,Tags=[{Key=Name,Value=MyVPN}]'

# Create VPN Connection with static routing
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id cgw-0123456789abcdef0 \
    --vpn-gateway-id vgw-0123456789abcdef0 \
    --options StaticRoutesOnly=true

# Describe Customer Gateways
aws ec2 describe-customer-gateways

# Describe Virtual Private Gateways
aws ec2 describe-vpn-gateways

# Describe VPN Connections
aws ec2 describe-vpn-connections

# Describe specific VPN Connection
aws ec2 describe-vpn-connections \
    --vpn-connection-ids vpn-0123456789abcdef0

# Create static route for VPN connection
aws ec2 create-vpn-connection-route \
    --vpn-connection-id vpn-0123456789abcdef0 \
    --destination-cidr-block 192.168.0.0/16

# Delete static route
aws ec2 delete-vpn-connection-route \
    --vpn-connection-id vpn-0123456789abcdef0 \
    --destination-cidr-block 192.168.0.0/16

# Enable route propagation
aws ec2 enable-vgw-route-propagation \
    --route-table-id rtb-0123456789abcdef0 \
    --gateway-id vgw-0123456789abcdef0

# Disable route propagation
aws ec2 disable-vgw-route-propagation \
    --route-table-id rtb-0123456789abcdef0 \
    --gateway-id vgw-0123456789abcdef0

# Delete VPN Connection
aws ec2 delete-vpn-connection \
    --vpn-connection-id vpn-0123456789abcdef0

# Detach Virtual Private Gateway
aws ec2 detach-vpn-gateway \
    --vpn-gateway-id vgw-0123456789abcdef0 \
    --vpc-id vpc-0123456789abcdef0

# Delete Virtual Private Gateway
aws ec2 delete-vpn-gateway \
    --vpn-gateway-id vgw-0123456789abcdef0

# Delete Customer Gateway
aws ec2 delete-customer-gateway \
    --customer-gateway-id cgw-0123456789abcdef0
```

### DHCP Options

#### Create and Manage DHCP Options Sets
```bash
# Create DHCP options set
aws ec2 create-dhcp-options \
    --dhcp-configuration \
        "Key=domain-name,Values=example.com" \
        "Key=domain-name-servers,Values=10.0.0.2,AmazonProvidedDNS" \
    --tag-specifications 'ResourceType=dhcp-options,Tags=[{Key=Name,Value=MyDHCPOptions}]'

# Describe DHCP options
aws ec2 describe-dhcp-options

# Describe specific DHCP options
aws ec2 describe-dhcp-options \
    --dhcp-options-ids dopt-0123456789abcdef0

# Associate DHCP options with VPC
aws ec2 associate-dhcp-options \
    --dhcp-options-id dopt-0123456789abcdef0 \
    --vpc-id vpc-0123456789abcdef0

# Associate default DHCP options with VPC
aws ec2 associate-dhcp-options \
    --dhcp-options-id default \
    --vpc-id vpc-0123456789abcdef0

# Delete DHCP options
aws ec2 delete-dhcp-options \
    --dhcp-options-id dopt-0123456789abcdef0
```

### Prefix Lists

#### Create and Manage Prefix Lists
```bash
# Create managed prefix list
aws ec2 create-managed-prefix-list \
    --prefix-list-name my-prefix-list \
    --address-family IPv4 \
    --max-entries 10 \
    --entries Cidr=10.0.0.0/16,Description="VPC CIDR" \
    --tag-specifications 'ResourceType=prefix-list,Tags=[{Key=Name,Value=MyPrefixList}]'

# Describe managed prefix lists
aws ec2 describe-managed-prefix-lists

# Describe specific prefix list
aws ec2 describe-managed-prefix-lists \
    --prefix-list-ids pl-0123456789abcdef0

# Get prefix list entries
aws ec2 get-managed-prefix-list-entries \
    --prefix-list-id pl-0123456789abcdef0

# Modify prefix list (add entries)
aws ec2 modify-managed-prefix-list \
    --prefix-list-id pl-0123456789abcdef0 \
    --add-entries Cidr=10.1.0.0/16,Description="Additional CIDR"

# Modify prefix list (remove entries)
aws ec2 modify-managed-prefix-list \
    --prefix-list-id pl-0123456789abcdef0 \
    --remove-entries Cidr=10.1.0.0/16

# Delete managed prefix list
aws ec2 delete-managed-prefix-list \
    --prefix-list-id pl-0123456789abcdef0
```

---

## Exam Tips and Common Scenarios

### SAA-C03 Exam Focus Areas

#### High-Priority Topics:
1. **Subnet design and CIDR planning**
2. **Security Groups vs NACLs**
3. **NAT Gateway vs NAT Instance**
4. **VPC Peering limitations**
5. **VPC Endpoints benefits and use cases**
6. **Transit Gateway scenarios**

#### Common Exam Scenarios:

**Scenario 1: Multi-Tier Application Architecture**
*Question: Design a VPC for a three-tier web application with high availability requirements.*

**Solution Approach:**
- Use multiple AZs (minimum 2, preferably 3)
- Public subnets for load balancers
- Private subnets for application servers
- Database subnets for RDS with Multi-AZ
- NAT Gateways in each AZ for redundancy

**Scenario 2: Hybrid Cloud Connectivity**
*Question: Connect on-premises data center to AWS VPC with consistent performance.*

**Solution Options:**
- **Direct Connect:** Best for consistent performance and high bandwidth
- **Site-to-Site VPN:** Cost-effective for variable or lower bandwidth needs
- **Direct Connect + VPN:** Backup connectivity option

**Scenario 3: Cost Optimization**
*Question: Reduce data transfer costs for applications accessing S3 frequently.*

**Solution:**
- Implement VPC Endpoint for S3 (Gateway Endpoint)
- Eliminates data transfer charges for S3 access
- Traffic remains within AWS network

**Scenario 4: Security Compliance**
*Question: Implement additional network security layer beyond security groups.*

**Solution:**
- Use Network ACLs as additional subnet-level protection
- Implement VPC Flow Logs for monitoring
- Consider AWS WAF for application-layer protection

### Exam Tips

#### Question Analysis Strategy:
1. **Identify key requirements:** Performance, cost, security, availability
2. **Look for keywords:** "cost-effective," "high availability," "secure," "consistent performance"
3. **Consider scale:** Current and future requirements
4. **Eliminate impossible options:** Overlapping CIDRs, unsupported configurations

#### Common Distractors:
- **Transitive VPC Peering:** Not supported natively
- **Multiple IGWs per VPC:** Only one IGW allowed
- **Cross-region security group references:** Not possible
- **NACL statefulness:** NACLs are stateless, not stateful

#### Best Practices for Exam:
1. **Always consider multiple AZs** for high availability
2. **Use least privilege** for security configurations
3. **Choose managed services** when available (NAT Gateway vs NAT Instance)
4. **Consider cost implications** of architectural decisions
5. **Think about scalability** and future growth

### Quick Reference

#### CIDR Block Sizes:
- /16 = 65,536 IPs
- /20 = 4,096 IPs
- /24 = 256 IPs
- /28 = 16 IPs (minimum VPC size)

#### Key Service Limits:
- VPCs per region: 5 (soft limit)
- Subnets per VPC: 200
- Route tables per VPC: 200
- Routes per route table: 50
- Security groups per VPC: 2,500
- Rules per security group: 60

#### Cost Considerations:
- **NAT Gateway:** $0.045/hour + $0.045/GB processed
- **VPC Endpoints:** $0.01/hour + $0.01/GB processed (Interface Endpoints)
- **Data Transfer:** Cross-AZ charges apply
- **Elastic IPs:** Charged when not associated with running instance

---

This comprehensive guide covers all major VPC concepts and scenarios relevant to the AWS SAA-C03 certification exam. Focus on understanding the practical applications and decision factors for each service and feature, as the exam emphasizes real-world architectural scenarios rather than memorization of facts.