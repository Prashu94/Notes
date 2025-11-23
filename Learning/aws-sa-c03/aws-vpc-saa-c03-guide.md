# AWS VPC (Virtual Private Cloud) - SAA-C03 Certification Guide

## Table of Contents
1. [VPC Fundamentals](#vpc-fundamentals)
2. [VPC Components](#vpc-components)
3. [VPC Connectivity](#vpc-connectivity)
4. [Advanced VPC Features](#advanced-vpc-features)
5. [VPC Security](#vpc-security)
6. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
7. [Exam Tips and Common Scenarios](#exam-tips-and-common-scenarios)

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