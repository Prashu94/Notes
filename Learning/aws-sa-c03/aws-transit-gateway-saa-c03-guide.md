# AWS Transit Gateway - SAA-C03 Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Architecture and Components](#architecture-and-components)
4. [Route Tables and Routing](#route-tables-and-routing)
5. [Security and Access Control](#security-and-access-control)
6. [Connectivity Options](#connectivity-options)
7. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
8. [Pricing and Cost Optimization](#pricing-and-cost-optimization)
9. [Best Practices](#best-practices)
10. [Common Exam Scenarios](#common-exam-scenarios)
11. [AWS CLI Commands Reference](#aws-cli-commands-reference)
12. [Hands-on Labs](#hands-on-labs)
13. [Exam Tips](#exam-tips)

## Overview

### What is AWS Transit Gateway?
AWS Transit Gateway is a network transit hub that connects Amazon Virtual Private Clouds (VPCs) and on-premises networks through a central hub. It simplifies network connectivity by eliminating the need for complex peering relationships and reducing the number of connections required.

### Key Benefits
- **Simplified Network Architecture**: Centralized connectivity hub
- **Scalability**: Connect thousands of VPCs and on-premises networks
- **Reduced Complexity**: Eliminates mesh networking complexity
- **Cost Optimization**: Reduces data transfer costs
- **Enhanced Security**: Centralized security policy enforcement
- **Multi-Account Support**: Works across AWS accounts and regions

### Use Cases
- Large enterprise networks with multiple VPCs
- Hybrid cloud connectivity
- Multi-region networking
- Network segmentation and isolation
- Centralized internet egress

## Key Concepts

### Transit Gateway
- Regional service that acts as a network hub
- Supports up to 5,000 VPC attachments per Transit Gateway
- Cross-region peering supported
- Highly available and scalable

### Attachments
Types of attachments supported:
- **VPC Attachments**: Connect VPCs to Transit Gateway
- **VPN Attachments**: Connect on-premises via Site-to-Site VPN
- **Direct Connect Gateway**: Connect via AWS Direct Connect
- **Peering Attachments**: Connect to other Transit Gateways
- **Connect Attachments**: Third-party SD-WAN appliances

### Route Tables
- Control traffic routing between attachments
- Default route table created automatically
- Custom route tables for segmentation
- Support for static and propagated routes

### Network Segmentation
- Isolate different environments (dev, test, prod)
- Implement security policies
- Control inter-VPC communication

## Architecture and Components

### Basic Architecture
```
┌─────────────┐    ┌─────────────────────┐    ┌─────────────┐
│    VPC-A    │────│                     │────│    VPC-B    │
└─────────────┘    │   Transit Gateway   │    └─────────────┘
                   │                     │
┌─────────────┐────│                     │────┌─────────────┐
│On-premises  │    │                     │    │    VPC-C    │
│   Network   │    └─────────────────────┘    └─────────────┘
└─────────────┘
```

### Multi-Region Architecture
```
Region A                    Region B
┌─────────────────────┐    ┌─────────────────────┐
│   Transit Gateway   │────│   Transit Gateway   │
│        (TGW-A)      │    │        (TGW-B)      │
└─────────────────────┘    └─────────────────────┘
          │                           │
    ┌─────────────┐              ┌─────────────┐
    │   VPCs in   │              │   VPCs in   │
    │   Region A  │              │   Region B  │
    └─────────────┘              └─────────────┘
```

### Components Deep Dive

#### Transit Gateway Specifications
- **Maximum Bandwidth**: 50 Gbps per VPC attachment
- **Maximum Routes**: 10,000 routes per route table
- **Maximum Attachments**: 5,000 per Transit Gateway
- **Availability**: Multi-AZ by default
- **BGP ASN**: Supports 2-byte and 4-byte ASNs

#### Attachment Types Details

**VPC Attachments**
- Requires subnet in each AZ
- Uses Elastic Network Interfaces (ENIs)
- Supports IPv4 and IPv6
- DNS resolution support

**VPN Attachments**
- Site-to-Site VPN connectivity
- BGP and static routing
- Redundant tunnels for high availability
- Supports up to 1.25 Gbps per tunnel

**Direct Connect Gateway Attachments**
- High-bandwidth dedicated connection
- Private connectivity to AWS
- Consistent network performance
- Multiple VIFs support

## Route Tables and Routing

### Default Route Table
- Automatically created with Transit Gateway
- All attachments associated by default
- Enables full mesh connectivity
- Can be customized or replaced

### Custom Route Tables
```bash
# Example route table configuration
Route Table: Custom-RT-Production
├── VPC-Prod-A (associated)
├── VPC-Prod-B (associated)
└── Routes:
    ├── 10.0.0.0/16 → VPC-Prod-A
    ├── 10.1.0.0/16 → VPC-Prod-B
    └── 0.0.0.0/0 → VPN-Connection
```

### Routing Concepts

#### Route Propagation
- Automatic route advertisement
- Dynamic updates from attachments
- BGP-based for VPN and Direct Connect
- VPC CIDR propagation

#### Route Priority
1. Most specific routes (longest prefix)
2. Static routes over propagated routes
3. VPC routes over VPN routes
4. Direct Connect routes over VPN routes

#### Routing Scenarios

**Scenario 1: Hub and Spoke**
```
Central Services VPC (Hub)
        │
   Transit Gateway
    ├── Spoke VPC 1
    ├── Spoke VPC 2
    └── Spoke VPC 3
```

**Scenario 2: Network Segmentation**
```
Production Route Table     Development Route Table
├── Prod VPC A            ├── Dev VPC A
├── Prod VPC B            ├── Dev VPC B
└── Shared Services       └── Shared Services
```

## Security and Access Control

### Network Access Control
- **Security Groups**: Applied at ENI level
- **NACLs**: Applied at subnet level
- **Route Table Association**: Controls reachability

### Cross-Account Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT-ID:root"
      },
      "Action": [
        "ec2:CreateTransitGatewayVpcAttachment",
        "ec2:DescribeTransitGateways"
      ],
      "Resource": "*"
    }
  ]
}
```

### Resource Sharing
- AWS Resource Access Manager (RAM)
- Share Transit Gateway across accounts
- Granular permission control
- Cross-organizational sharing

### Security Best Practices
1. Use separate route tables for different environments
2. Implement least privilege access
3. Monitor traffic flows
4. Use VPC Flow Logs for visibility
5. Implement network segmentation

## Connectivity Options

### VPC-to-VPC Connectivity
```yaml
Configuration:
  - Transit Gateway in central region
  - VPC attachments in same region
  - Route tables for traffic control
  - Security groups for access control

Benefits:
  - Simplified connectivity
  - Transitive routing
  - Centralized management
  - Cost optimization
```

### Hybrid Connectivity

#### Site-to-Site VPN
```yaml
Setup:
  Customer Gateway: On-premises device
  VPN Connection: AWS-managed tunnels
  Transit Gateway: Central hub
  
Features:
  - BGP routing
  - Redundant tunnels
  - IPSec encryption
  - Up to 1.25 Gbps per tunnel
```

#### Direct Connect
```yaml
Setup:
  Direct Connect Gateway: Regional resource
  Virtual Interfaces: Layer 2/3 connectivity
  Transit Gateway: Attachment point
  
Benefits:
  - Higher bandwidth (up to 100 Gbps)
  - Consistent network performance
  - Reduced data transfer costs
  - Private connectivity
```

### Multi-Region Connectivity

#### Transit Gateway Peering
```bash
# Cross-region peering setup
Region us-east-1:
  Transit Gateway: tgw-12345abcde
  
Region us-west-2:
  Transit Gateway: tgw-67890fghij
  
Peering Connection:
  tgw-12345abcde ←→ tgw-67890fghij
```

#### Benefits and Limitations
**Benefits:**
- Global network connectivity
- Regional fault isolation
- Compliance requirements
- Latency optimization

**Limitations:**
- Additional latency between regions
- Data transfer charges
- No multicast support across regions

## Monitoring and Troubleshooting

### CloudWatch Metrics
```yaml
Key Metrics:
  - BytesIn/BytesOut: Data transfer volume
  - PacketsIn/PacketsOut: Packet counts
  - PacketDropCount: Dropped packets
  - LatencyMetrics: Connection latency

Dimensions:
  - TransitGateway
  - TransitGatewayAttachment
  - TransitGatewayRouteTable
```

### VPC Flow Logs
```json
{
  "version": "5",
  "account-id": "123456789012",
  "interface-id": "eni-1234567890abcdef0",
  "srcaddr": "10.0.1.5",
  "dstaddr": "10.1.2.3",
  "srcport": "443",
  "dstport": "80",
  "protocol": "6",
  "packets": "25",
  "bytes": "2000",
  "action": "ACCEPT",
  "log-status": "OK"
}
```

### Network Insights
- **VPC Reachability Analyzer**: Path analysis
- **Transit Gateway Network Manager**: Global view
- **Route Analyzer**: Route troubleshooting

### Common Issues and Solutions

#### Issue 1: Connectivity Problems
**Symptoms:** Cannot reach resources across attachments
**Diagnosis:**
- Check route table associations
- Verify security group rules
- Check NACL configurations
- Validate CIDR overlaps

**Solution:**
```bash
# Check route table associations
aws ec2 describe-transit-gateway-route-tables
aws ec2 get-associated-transit-gateway-route-table

# Verify routes
aws ec2 search-transit-gateway-routes
```

#### Issue 2: Performance Issues
**Symptoms:** Slow data transfer or high latency
**Diagnosis:**
- Monitor CloudWatch metrics
- Check bandwidth utilization
- Analyze VPC Flow Logs
- Verify placement groups

**Solution:**
- Optimize route paths
- Use placement groups for EC2 instances
- Consider Direct Connect for high bandwidth
- Implement enhanced networking

## Pricing and Cost Optimization

### Pricing Components
1. **Hourly Charges**: Per attachment, per hour
2. **Data Processing**: Per GB processed
3. **Cross-AZ Traffic**: Standard AWS data transfer rates

### Cost Calculation Example
```yaml
Monthly Cost Calculation:
  Transit Gateway: $36.00 (1 gateway × $36/month)
  VPC Attachments: $108.00 (3 attachments × $36/month each)
  Data Processing: $60.00 (300 GB × $0.02/GB)
  Total Monthly Cost: $204.00
```

### Cost Optimization Strategies
1. **Consolidate Attachments**: Reduce number of attachments
2. **Optimize Data Flow**: Minimize unnecessary traffic
3. **Use Local Traffic**: Keep traffic within same AZ when possible
4. **Monitor Usage**: Regular cost analysis
5. **Right-size Connections**: Match bandwidth to requirements

### Cost Comparison: Transit Gateway vs. VPC Peering
```yaml
Scenario: 10 VPCs requiring full mesh connectivity

VPC Peering:
  - Connections needed: 45 (n×(n-1)/2)
  - Management complexity: High
  - Data transfer: Direct path, lower latency
  - Cost: Lower for small deployments

Transit Gateway:
  - Connections needed: 10 (one per VPC)
  - Management complexity: Low
  - Data transfer: Hub-and-spoke, slight latency
  - Cost: Higher per-connection, but scales better
```

## Best Practices

### Design Principles
1. **Plan IP Address Space**: Avoid CIDR overlaps
2. **Implement Segmentation**: Use multiple route tables
3. **Design for Scale**: Consider future growth
4. **Plan for High Availability**: Multi-AZ deployments
5. **Security First**: Implement defense in depth

### Architecture Best Practices

#### Network Segmentation
```yaml
Production Environment:
  Route Table: Production-RT
  Attachments:
    - Production VPCs
    - Shared Services VPC
  Isolation: No access to dev/test

Development Environment:
  Route Table: Development-RT
  Attachments:
    - Development VPCs
    - Shared Services VPC
  Isolation: No access to production
```

#### Multi-Region Design
```yaml
Primary Region (us-east-1):
  - Production workloads
  - Primary Transit Gateway
  - Full mesh connectivity

Secondary Region (us-west-2):
  - DR workloads
  - Secondary Transit Gateway
  - Peering to primary region
```

### Operational Best Practices
1. **Documentation**: Maintain network diagrams
2. **Change Management**: Document route changes
3. **Monitoring**: Implement comprehensive monitoring
4. **Testing**: Regular connectivity testing
5. **Automation**: Use Infrastructure as Code

### Security Best Practices
1. **Principle of Least Privilege**: Minimal required access
2. **Network Segmentation**: Isolate sensitive workloads
3. **Monitoring**: Continuous traffic analysis
4. **Encryption**: Use VPN for sensitive data
5. **Access Control**: Implement proper IAM policies

## Common Exam Scenarios

### Scenario 1: Multi-VPC Connectivity
**Question:** An organization has 15 VPCs that need to communicate with each other. What's the most cost-effective and manageable solution?

**Answer:** AWS Transit Gateway provides a hub-and-spoke model that eliminates the need for 105 VPC peering connections (15×14/2), reducing complexity and management overhead while providing transitive routing.

### Scenario 2: Hybrid Cloud Integration
**Question:** A company needs to connect their on-premises data center to multiple AWS VPCs across different accounts. What solution would you recommend?

**Answer:** Use Transit Gateway with:
- VPN or Direct Connect Gateway attachment for on-premises connectivity
- Resource sharing via AWS RAM for cross-account access
- Custom route tables for network segmentation

### Scenario 3: Network Isolation
**Question:** How can you ensure that development VPCs cannot communicate with production VPCs while still allowing both to access shared services?

**Answer:** Create separate route tables:
- Production route table: Associates production VPCs and shared services
- Development route table: Associates development VPCs and shared services
- Shared services can communicate with both but prod/dev are isolated

### Scenario 4: Multi-Region Disaster Recovery
**Question:** Design a multi-region architecture for disaster recovery with centralized connectivity.

**Answer:** 
- Deploy Transit Gateway in each region
- Create peering connection between Transit Gateways
- Configure route tables to control traffic flow
- Use Direct Connect or VPN for on-premises connectivity in both regions

### Scenario 5: Migration from VPC Peering
**Question:** An organization has complex VPC peering relationships and wants to simplify their network architecture. What's the migration strategy?

**Answer:**
1. Deploy Transit Gateway in target region
2. Create VPC attachments gradually
3. Update route tables to use Transit Gateway routes
4. Remove VPC peering connections once traffic is flowing through Transit Gateway
5. Test connectivity at each step

---

## AWS CLI Commands Reference

### Create Transit Gateway

```bash
# Create a basic Transit Gateway
aws ec2 create-transit-gateway \
    --description "Production Transit Gateway" \
    --options \
        AmazonSideAsn=64512,\
        AutoAcceptSharedAttachments=disable,\
        DefaultRouteTableAssociation=enable,\
        DefaultRouteTablePropagation=enable,\
        VpnEcmpSupport=enable,\
        DnsSupport=enable \
    --tag-specifications \
        'ResourceType=transit-gateway,Tags=[{Key=Name,Value=MyTGW},{Key=Environment,Value=Production}]'

# Create Transit Gateway with multicast support
aws ec2 create-transit-gateway \
    --description "Transit Gateway with Multicast" \
    --options \
        AmazonSideAsn=64513,\
        MulticastSupport=enable,\
        AutoAcceptSharedAttachments=enable,\
        DnsSupport=enable \
    --tag-specifications \
        'ResourceType=transit-gateway,Tags=[{Key=Name,Value=MulticastTGW}]'

# Describe Transit Gateways
aws ec2 describe-transit-gateways

# Describe specific Transit Gateway
aws ec2 describe-transit-gateways \
    --transit-gateway-ids tgw-1234567890abcdef0

# Modify Transit Gateway
aws ec2 modify-transit-gateway \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --options "AutoAcceptSharedAttachments=enable"

# Delete Transit Gateway
aws ec2 delete-transit-gateway \
    --transit-gateway-id tgw-1234567890abcdef0
```

### Create VPC Attachments

```bash
# Create VPC attachment
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --vpc-id vpc-0abcdef1234567890 \
    --subnet-ids subnet-111111111 subnet-222222222 \
    --options \
        DnsSupport=enable,\
        Ipv6Support=disable,\
        ApplianceModeSupport=disable \
    --tag-specifications \
        'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=ProdVPC},{Key=Environment,Value=Production}]'

# Create VPC attachment with appliance mode (for firewall inspection)
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --vpc-id vpc-firewall123456 \
    --subnet-ids subnet-firewall1 subnet-firewall2 \
    --options ApplianceModeSupport=enable

# Describe VPC attachments
aws ec2 describe-transit-gateway-vpc-attachments

# Describe specific attachment
aws ec2 describe-transit-gateway-vpc-attachments \
    --transit-gateway-attachment-ids tgw-attach-0a1b2c3d4e5f6g7h8

# Modify VPC attachment
aws ec2 modify-transit-gateway-vpc-attachment \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8 \
    --options "DnsSupport=disable"

# Add subnets to VPC attachment
aws ec2 modify-transit-gateway-vpc-attachment \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8 \
    --add-subnet-ids subnet-333333333

# Remove subnets from VPC attachment
aws ec2 modify-transit-gateway-vpc-attachment \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8 \
    --remove-subnet-ids subnet-111111111

# Delete VPC attachment
aws ec2 delete-transit-gateway-vpc-attachment \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8
```

### Create VPN Attachments

```bash
# Create Customer Gateway first
aws ec2 create-customer-gateway \
    --type ipsec.1 \
    --public-ip 198.51.100.1 \
    --bgp-asn 65000 \
    --tag-specifications \
        'ResourceType=customer-gateway,Tags=[{Key=Name,Value=OnPremGW}]'

# Create VPN connection attached to Transit Gateway
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id cgw-1234567890abcdef0 \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --options \
        TunnelInsideIpVersion=ipv4,\
        StaticRoutesOnly=false \
    --tag-specifications \
        'ResourceType=vpn-connection,Tags=[{Key=Name,Value=OnPremVPN}]'

# Create VPN with static routes
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id cgw-1234567890abcdef0 \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --options StaticRoutesOnly=true \
    --tag-specifications \
        'ResourceType=vpn-connection,Tags=[{Key=Name,Value=StaticVPN}]'

# Add static route to VPN
aws ec2 create-vpn-connection-route \
    --vpn-connection-id vpn-0a1b2c3d4e5f6g7h8 \
    --destination-cidr-block 10.0.0.0/16

# Describe VPN connections
aws ec2 describe-vpn-connections

# Describe Transit Gateway VPN attachments
aws ec2 describe-transit-gateway-attachments \
    --filters "Name=resource-type,Values=vpn"

# Delete VPN connection route
aws ec2 delete-vpn-connection-route \
    --vpn-connection-id vpn-0a1b2c3d4e5f6g7h8 \
    --destination-cidr-block 10.0.0.0/16
```

### Create Direct Connect Gateway Attachments

```bash
# Create Direct Connect Gateway (if not exists)
aws directconnect create-direct-connect-gateway \
    --direct-connect-gateway-name MyDXGateway \
    --amazon-side-asn 64512

# Associate Direct Connect Gateway with Transit Gateway
aws ec2 create-transit-gateway-connect \
    --transport-transit-gateway-attachment-id tgw-attach-dx123456 \
    --options Protocol=gre \
    --tag-specifications \
        'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=DX-Connect}]'

# Associate Transit Gateway with Direct Connect Gateway
aws directconnect create-direct-connect-gateway-association \
    --direct-connect-gateway-id dcgw-1234567890abcdef \
    --gateway-id tgw-1234567890abcdef0 \
    --add-allowed-prefixes-to-direct-connect-gateway \
        cidr=10.0.0.0/8 cidr=172.16.0.0/12

# Describe Direct Connect Gateway associations
aws directconnect describe-direct-connect-gateway-associations \
    --direct-connect-gateway-id dcgw-1234567890abcdef

# Update allowed prefixes
aws directconnect update-direct-connect-gateway-association \
    --association-id arn:aws:directconnect:us-east-1:123456789012:association/abc123 \
    --add-allowed-prefixes-to-direct-connect-gateway cidr=192.168.0.0/16 \
    --remove-allowed-prefixes-to-direct-connect-gateway cidr=10.0.0.0/8

# Delete Direct Connect Gateway association
aws directconnect delete-direct-connect-gateway-association \
    --association-id arn:aws:directconnect:us-east-1:123456789012:association/abc123
```

### Create Peering Attachments

```bash
# Create Transit Gateway peering attachment (same or different regions)
aws ec2 create-transit-gateway-peering-attachment \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --peer-transit-gateway-id tgw-9876543210fedcba0 \
    --peer-account-id 123456789012 \
    --peer-region us-west-2 \
    --tag-specifications \
        'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=CrossRegionPeering}]'

# Accept Transit Gateway peering attachment (in peer region/account)
aws ec2 accept-transit-gateway-peering-attachment \
    --transit-gateway-attachment-id tgw-attach-peering123 \
    --region us-west-2

# Describe peering attachments
aws ec2 describe-transit-gateway-peering-attachments

# Describe specific peering attachment
aws ec2 describe-transit-gateway-peering-attachments \
    --transit-gateway-attachment-ids tgw-attach-peering123

# Reject peering attachment
aws ec2 reject-transit-gateway-peering-attachment \
    --transit-gateway-attachment-id tgw-attach-peering123

# Delete peering attachment
aws ec2 delete-transit-gateway-peering-attachment \
    --transit-gateway-attachment-id tgw-attach-peering123
```

### Route Tables

```bash
# Create Transit Gateway route table
aws ec2 create-transit-gateway-route-table \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --tag-specifications \
        'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=ProdRouteTable}]'

# Create route table for specific segment
aws ec2 create-transit-gateway-route-table \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --tag-specifications \
        'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=DevRouteTable},{Key=Segment,Value=Development}]'

# Describe route tables
aws ec2 describe-transit-gateway-route-tables

# Describe specific route table
aws ec2 describe-transit-gateway-route-tables \
    --transit-gateway-route-table-ids tgw-rtb-0a1b2c3d4e5f6g7h8

# Search route tables
aws ec2 search-transit-gateway-routes \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --filters "Name=state,Values=active"

# Export route table
aws ec2 export-transit-gateway-routes \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --s3-bucket my-tgw-routes-bucket \
    --filters "Name=state,Values=active"

# Delete route table
aws ec2 delete-transit-gateway-route-table \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8
```

### Route Table Associations and Propagations

```bash
# Associate attachment with route table
aws ec2 associate-transit-gateway-route-table \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8

# Disassociate attachment from route table
aws ec2 disassociate-transit-gateway-route-table \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8

# Enable route propagation
aws ec2 enable-transit-gateway-route-table-propagation \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8

# Disable route propagation
aws ec2 disable-transit-gateway-route-table-propagation \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8

# Get route table associations
aws ec2 get-transit-gateway-route-table-associations \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8

# Get route table propagations
aws ec2 get-transit-gateway-route-table-propagations \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8

# Create static route
aws ec2 create-transit-gateway-route \
    --destination-cidr-block 10.0.0.0/16 \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8

# Create blackhole route
aws ec2 create-transit-gateway-route \
    --destination-cidr-block 192.168.100.0/24 \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --blackhole

# Delete route
aws ec2 delete-transit-gateway-route \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --destination-cidr-block 10.0.0.0/16
```

### Multicast Domains

```bash
# Create multicast domain
aws ec2 create-transit-gateway-multicast-domain \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --options \
        Igmpv2Support=enable,\
        StaticSourcesSupport=disable,\
        AutoAcceptSharedAssociations=disable \
    --tag-specifications \
        'ResourceType=transit-gateway-multicast-domain,Tags=[{Key=Name,Value=MyMulticastDomain}]'

# Associate VPC with multicast domain
aws ec2 associate-transit-gateway-multicast-domain \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8 \
    --subnet-ids subnet-111111111 subnet-222222222

# Register multicast group members
aws ec2 register-transit-gateway-multicast-group-members \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d \
    --group-ip-address 224.0.0.1 \
    --network-interface-ids eni-0a1b2c3d4e5f6g7h8

# Register multicast group sources
aws ec2 register-transit-gateway-multicast-group-sources \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d \
    --group-ip-address 224.0.0.1 \
    --network-interface-ids eni-9876543210fedcba0

# Describe multicast domains
aws ec2 describe-transit-gateway-multicast-domains

# Get multicast group members
aws ec2 search-transit-gateway-multicast-groups \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d \
    --filters "Name=group-ip-address,Values=224.0.0.1"

# Deregister multicast group members
aws ec2 deregister-transit-gateway-multicast-group-members \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d \
    --group-ip-address 224.0.0.1 \
    --network-interface-ids eni-0a1b2c3d4e5f6g7h8

# Deregister multicast group sources
aws ec2 deregister-transit-gateway-multicast-group-sources \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d \
    --group-ip-address 224.0.0.1 \
    --network-interface-ids eni-9876543210fedcba0

# Disassociate VPC from multicast domain
aws ec2 disassociate-transit-gateway-multicast-domain \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8 \
    --subnet-ids subnet-111111111

# Delete multicast domain
aws ec2 delete-transit-gateway-multicast-domain \
    --transit-gateway-multicast-domain-id tgw-mcast-domain-0a1b2c3d
```

### Network Manager

```bash
# Create global network
aws networkmanager create-global-network \
    --description "Global Corporate Network" \
    --tags Key=Name,Value=GlobalNetwork

# Register Transit Gateway to global network
aws networkmanager register-transit-gateway \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8 \
    --transit-gateway-arn arn:aws:ec2:us-east-1:123456789012:transit-gateway/tgw-1234567890abcdef0

# Create site
aws networkmanager create-site \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8 \
    --location \
        Latitude=40.7128,\
        Longitude=-74.0060,\
        Address="New York Office" \
    --description "NY Headquarters" \
    --tags Key=Name,Value=NYOffice

# Create device
aws networkmanager create-device \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8 \
    --site-id site-0a1b2c3d4e5f6g7h8 \
    --description "Core Router" \
    --type "Router" \
    --vendor "Cisco" \
    --model "ASR1000" \
    --tags Key=Name,Value=CoreRouter01

# Create link
aws networkmanager create-link \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8 \
    --site-id site-0a1b2c3d4e5f6g7h8 \
    --bandwidth UploadSpeed=1000,DownloadSpeed=1000 \
    --provider "ISP-Name" \
    --type "Broadband" \
    --description "Primary Internet Connection"

# Get Transit Gateway registrations
aws networkmanager get-transit-gateway-registrations \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8

# Describe global networks
aws networkmanager describe-global-networks

# Get network routes
aws networkmanager get-route-analysis \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8 \
    --source \
        TransitGatewayAttachmentArn=arn:aws:ec2:us-east-1:123456789012:transit-gateway-attachment/tgw-attach-source \
    --destination \
        TransitGatewayAttachmentArn=arn:aws:ec2:us-west-2:123456789012:transit-gateway-attachment/tgw-attach-dest

# Deregister Transit Gateway
aws networkmanager deregister-transit-gateway \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8 \
    --transit-gateway-arn arn:aws:ec2:us-east-1:123456789012:transit-gateway/tgw-1234567890abcdef0

# Delete global network
aws networkmanager delete-global-network \
    --global-network-id global-network-0a1b2c3d4e5f6g7h8
```

### Tags Management

```bash
# Tag Transit Gateway
aws ec2 create-tags \
    --resources tgw-1234567890abcdef0 \
    --tags Key=Environment,Value=Production Key=CostCenter,Value=IT

# Tag Transit Gateway attachment
aws ec2 create-tags \
    --resources tgw-attach-0a1b2c3d4e5f6g7h8 \
    --tags Key=Application,Value=WebApp Key=Backup,Value=Yes

# Tag route table
aws ec2 create-tags \
    --resources tgw-rtb-0a1b2c3d4e5f6g7h8 \
    --tags Key=Segment,Value=Production Key=Team,Value=Network

# Describe tags
aws ec2 describe-tags \
    --filters "Name=resource-id,Values=tgw-1234567890abcdef0"

# Delete tags
aws ec2 delete-tags \
    --resources tgw-1234567890abcdef0 \
    --tags Key=Environment
```

### Monitoring and Troubleshooting

```bash
# Get Transit Gateway attachment state
aws ec2 describe-transit-gateway-attachments \
    --transit-gateway-attachment-ids tgw-attach-0a1b2c3d4e5f6g7h8 \
    --query 'TransitGatewayAttachments[0].State'

# List all attachments for a Transit Gateway
aws ec2 describe-transit-gateway-attachments \
    --filters "Name=transit-gateway-id,Values=tgw-1234567890abcdef0"

# Check route table associations
aws ec2 get-transit-gateway-attachment-propagations \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8

# Get attachment propagations
aws ec2 get-transit-gateway-attachment-propagations \
    --transit-gateway-attachment-id tgw-attach-0a1b2c3d4e5f6g7h8

# Describe prefix list references
aws ec2 describe-transit-gateway-prefix-list-references \
    --transit-gateway-route-table-id tgw-rtb-0a1b2c3d4e5f6g7h8

# Get VPN tunnel status (for VPN attachments)
aws ec2 describe-vpn-connections \
    --vpn-connection-ids vpn-0a1b2c3d4e5f6g7h8 \
    --query 'VpnConnections[0].VgwTelemetry'
```

---

## Hands-on Labs

### Lab 1: Basic Transit Gateway Setup
```bash
# Step 1: Create Transit Gateway
aws ec2 create-transit-gateway \
    --description "My Transit Gateway" \
    --options AmazonSideAsn=64512,AutoAcceptSharedAttachments=enable

# Step 2: Create VPC Attachment
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id tgw-12345abcde \
    --vpc-id vpc-12345abcde \
    --subnet-ids subnet-12345abcde

# Step 3: Create Custom Route Table
aws ec2 create-transit-gateway-route-table \
    --transit-gateway-id tgw-12345abcde \
    --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=Custom-RT}]'
```

### Lab 2: Cross-Region Peering
```bash
# Step 1: Create peering attachment
aws ec2 create-transit-gateway-peering-attachment \
    --transit-gateway-id tgw-us-east-1 \
    --peer-transit-gateway-id tgw-us-west-2 \
    --peer-region us-west-2 \
    --peer-account-id 123456789012

# Step 2: Accept peering (in peer region)
aws ec2 accept-transit-gateway-peering-attachment \
    --transit-gateway-attachment-id tgw-attach-12345abcde \
    --region us-west-2

# Step 3: Add routes
aws ec2 create-route \
    --route-table-id rtb-12345abcde \
    --destination-cidr-block 10.1.0.0/16 \
    --transit-gateway-attachment-id tgw-attach-12345abcde
```

### Lab 3: Site-to-Site VPN Integration
```bash
# Step 1: Create Customer Gateway
aws ec2 create-customer-gateway \
    --type ipsec.1 \
    --public-ip 203.0.113.12 \
    --bgp-asn 65000

# Step 2: Create VPN Connection
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id cgw-12345abcde \
    --transit-gateway-id tgw-12345abcde

# Step 3: Configure route propagation
aws ec2 enable-transit-gateway-route-table-propagation \
    --transit-gateway-route-table-id tgw-rtb-12345abcde \
    --transit-gateway-attachment-id tgw-attach-12345abcde
```

## Exam Tips

### Key Points to Remember
1. **Regional Service**: Transit Gateway is region-specific
2. **No Transitive Peering**: VPC peering doesn't provide transitive routing, Transit Gateway does
3. **Route Table Association**: Each attachment must be associated with a route table
4. **Cross-Region**: Requires peering between Transit Gateways
5. **Bandwidth Limits**: 50 Gbps per VPC attachment

### Common Exam Questions Patterns

#### Pattern 1: Connectivity Requirements
- Multiple VPCs need full mesh connectivity
- Answer: Transit Gateway with default route table

#### Pattern 2: Network Isolation
- Need to isolate different environments
- Answer: Multiple route tables with selective associations

#### Pattern 3: Hybrid Connectivity
- Connect on-premises to multiple VPCs
- Answer: Transit Gateway with VPN or Direct Connect Gateway

#### Pattern 4: Cost Optimization
- Large number of VPCs requiring connectivity
- Answer: Transit Gateway is more cost-effective than VPC peering at scale

#### Pattern 5: Multi-Region Architecture
- Global connectivity requirements
- Answer: Transit Gateway peering between regions

### Comparison Matrix
| Feature | VPC Peering | Transit Gateway | NAT Gateway |
|---------|-------------|----------------|-------------|
| Transitive Routing | ❌ | ✅ | ❌ |
| Cross-Region | ✅ | ✅ (with peering) | ❌ |
| On-premises | ❌ | ✅ | ❌ |
| Scalability | Low | High | Medium |
| Management Complexity | High | Low | Low |
| Cost (small scale) | Lower | Higher | N/A |
| Cost (large scale) | Higher | Lower | N/A |

### Troubleshooting Checklist
1. ✅ Route table associations correct?
2. ✅ Security groups allow traffic?
3. ✅ NACLs permit traffic?
4. ✅ No CIDR overlaps?
5. ✅ Routes properly configured?
6. ✅ DNS resolution enabled?
7. ✅ Cross-account sharing configured?

### Final Exam Preparation
- Understand when to use Transit Gateway vs alternatives
- Know the limits and quotas
- Practice route table configuration scenarios
- Understand pricing model and cost optimization
- Review security and access control mechanisms
- Practice troubleshooting common connectivity issues

---

## Summary

AWS Transit Gateway is a powerful networking service that simplifies connectivity in complex, multi-VPC environments. For the SAA-C03 exam, focus on:

- **When to use**: Large-scale VPC connectivity, hybrid cloud, network segmentation
- **Key features**: Transitive routing, cross-region peering, multiple attachment types
- **Best practices**: Network segmentation, security, cost optimization
- **Common scenarios**: Multi-VPC connectivity, hybrid integration, disaster recovery

Understanding these concepts and practicing hands-on scenarios will help you succeed in both the exam and real-world implementations.