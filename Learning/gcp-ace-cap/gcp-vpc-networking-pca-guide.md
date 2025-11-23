# Google Cloud VPC & Networking - Professional Cloud Architect (PCA) Comprehensive Guide

## Table of Contents
1. [Network Architecture Design](#network-architecture-design)
2. [VPC Design Patterns](#vpc-design-patterns)
3. [Hybrid Connectivity Architecture](#hybrid-connectivity-architecture)
4. [Network Security Architecture](#network-security-architecture)
5. [Load Balancing Architecture](#load-balancing-architecture)
6. [Network Performance & Optimization](#network-performance--optimization)
7. [Multi-Region & Global Networking](#multi-region--global-networking)
8. [Network Topology Patterns](#network-topology-patterns)
9. [Cost Optimization Strategies](#cost-optimization-strategies)
10. [PCA Exam Tips](#pca-exam-tips)

---

## Network Architecture Design

### Network Design Principles

**1. Isolation & Segmentation:**
```
Organization
├── Host Project (Shared VPC Network)
│   ├── DMZ Subnet (Public-facing services)
│   ├── Application Subnet (Business logic)
│   ├── Database Subnet (Data tier)
│   └── Management Subnet (Admin access)
└── Service Projects
    ├── Production Project
    ├── Staging Project
    └── Development Project
```

**2. Defense in Depth:**
- VPC isolation (project/network boundaries)
- Firewall rules (network-level filtering)
- IAM policies (identity-based access)
- VPC Service Controls (data exfiltration prevention)
- Cloud Armor (DDoS protection)

**3. High Availability:**
- Multi-region deployment
- Redundant VPN tunnels (HA VPN)
- Multiple Cloud Interconnect connections
- Global load balancing

**4. Scalability:**
- Subnet expansion capability
- IP address planning (reserve space)
- Cloud NAT for outbound scaling
- Global VPC spanning regions

### IP Address Planning

**Enterprise IP Address Scheme:**

```yaml
Organization CIDR: 10.0.0.0/8

# By Environment
Production:  10.0.0.0/12   (10.0.0.0 - 10.15.255.255)
Staging:     10.16.0.0/12  (10.16.0.0 - 10.31.255.255)
Development: 10.32.0.0/12  (10.32.0.0 - 10.47.255.255)
Shared:      10.48.0.0/12  (10.48.0.0 - 10.63.255.255)

# By Region (within Production)
us-central1: 10.0.0.0/16
us-east1:    10.1.0.0/16
us-west1:    10.2.0.0/16
europe-west1: 10.3.0.0/16
asia-east1:  10.4.0.0/16

# By Function (within us-central1)
Web Tier:      10.0.1.0/24
App Tier:      10.0.2.0/24
Database Tier: 10.0.3.0/24
Management:    10.0.4.0/24
GKE Pods:      10.0.16.0/20 (secondary range)
GKE Services:  10.0.32.0/20 (secondary range)
```

**Key Considerations:**
- Reserve space for growth (use /16 per region)
- Plan for VPN/Interconnect (on-prem ranges)
- Avoid overlap with on-premises networks
- Consider future mergers/acquisitions
- Plan secondary ranges for GKE

### Subnet Design Strategy

**Pattern 1: Functional Subnets**
```
Production VPC (us-central1)
├── frontend-subnet (10.0.1.0/24)     - Load balancer backends
├── app-subnet (10.0.2.0/24)          - Application servers
├── data-subnet (10.0.3.0/24)         - Databases (no external IP)
├── gke-subnet (10.0.4.0/22)          - GKE node IPs
│   ├── Secondary: pods (10.0.16.0/20)
│   └── Secondary: services (10.0.32.0/20)
└── mgmt-subnet (10.0.8.0/24)         - Bastion, monitoring
```

**Pattern 2: Regional Expansion**
```
Multi-Region VPC
├── us-central1
│   ├── web-us-central1 (10.0.1.0/24)
│   └── app-us-central1 (10.0.2.0/24)
├── europe-west1
│   ├── web-europe-west1 (10.1.1.0/24)
│   └── app-europe-west1 (10.1.2.0/24)
└── asia-east1
    ├── web-asia-east1 (10.2.1.0/24)
    └── app-asia-east1 (10.2.2.0/24)
```

---

## VPC Design Patterns

### Pattern 1: Hub-and-Spoke (Shared VPC)

**Architecture:**
```
                    ┌─────────────────┐
                    │   Host Project   │
                    │   (Hub VPC)      │
                    │                  │
                    │  ┌───────────┐   │
                    │  │Cloud VPN/ │   │
                    │  │Interconnect│  │
                    │  └─────┬─────┘   │
                    └────────┼──────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
    │  Service   │      │  Service   │      │  Service   │
    │ Project A  │      │ Project B  │      │ Project C  │
    │ (Spoke)    │      │ (Spoke)    │      │ (Spoke)    │
    └────────────┘      └────────────┘      └────────────┘
```

**Benefits:**
- Centralized network management
- Single point for hybrid connectivity
- Centralized security controls
- Cost-effective (single VPN/Interconnect)

**Implementation:**
```bash
# Enable host project
gcloud compute shared-vpc enable host-project-id

# Create hub VPC with regional subnets
gcloud compute networks create hub-vpc \
  --subnet-mode=custom

# Create subnets per region
for REGION in us-central1 us-east1 europe-west1; do
  gcloud compute networks subnets create $REGION-subnet \
    --network=hub-vpc \
    --region=$REGION \
    --range=10.$((INDEX++)).0.0/16
done

# Attach service projects
gcloud compute shared-vpc associated-projects add project-a \
  --host-project=host-project-id
```

### Pattern 2: Multi-VPC with VPC Peering

**Architecture:**
```
┌──────────────┐        ┌──────────────┐
│  VPC: Prod   │◄──────►│  VPC: Shared │
│              │ Peering │   Services   │
│  Web + App   │        │   Logging    │
│  Tier        │        │   Monitoring │
└──────────────┘        └──────┬───────┘
                               │ Peering
                               │
                        ┌──────▼───────┐
                        │  VPC: Dev    │
                        │              │
                        │  Development │
                        │  Environment │
                        └──────────────┘
```

**Use Case:** Separate production and development environments

**Implementation:**
```bash
# Create peering from prod to shared services
gcloud compute networks peerings create prod-to-shared \
  --network=prod-vpc \
  --peer-project=shared-project \
  --peer-network=shared-vpc \
  --auto-create-routes \
  --import-custom-routes \
  --export-custom-routes

# Create reciprocal peering
gcloud compute networks peerings create shared-to-prod \
  --network=shared-vpc \
  --peer-project=prod-project \
  --peer-network=prod-vpc \
  --auto-create-routes \
  --import-custom-routes \
  --export-custom-routes
```

### Pattern 3: Three-Tier Architecture

**Architecture:**
```
Internet
   ↓
External Load Balancer (Layer 7)
   ↓
[DMZ Subnet: 10.0.1.0/24]
   ├─ Web Server 1 (10.0.1.10)
   ├─ Web Server 2 (10.0.1.11)
   └─ Web Server 3 (10.0.1.12)
   ↓
Internal Load Balancer (Layer 7)
   ↓
[App Subnet: 10.0.2.0/24]
   ├─ App Server 1 (10.0.2.10)
   ├─ App Server 2 (10.0.2.11)
   └─ App Server 3 (10.0.2.12)
   ↓
[Data Subnet: 10.0.3.0/24] (No external IP)
   ├─ Cloud SQL (10.0.3.10)
   └─ Memorystore (10.0.3.11)
```

**Firewall Rules:**
```bash
# Allow HTTP/HTTPS from internet to web tier
gcloud compute firewall-rules create allow-web-external \
  --network=production-vpc \
  --allow=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

# Allow app tier from web tier only
gcloud compute firewall-rules create allow-app-from-web \
  --network=production-vpc \
  --allow=tcp:8080 \
  --source-tags=web-server \
  --target-tags=app-server

# Allow database access from app tier only
gcloud compute firewall-rules create allow-db-from-app \
  --network=production-vpc \
  --allow=tcp:3306,tcp:5432 \
  --source-tags=app-server \
  --target-tags=database
```

### Pattern 4: GKE Private Cluster with Shared VPC

**Architecture:**
```
Host Project (Shared VPC)
├── gke-subnet (10.0.4.0/22)
│   ├── Primary: Node IPs
│   ├── Secondary: Pod IPs (10.0.16.0/20)
│   └── Secondary: Service IPs (10.0.32.0/20)
└── Firewall Rules (Managed by GKE)

Service Project (GKE Cluster)
└── Private GKE Cluster
    ├── Private endpoint (10.0.4.100)
    ├── Master authorized networks
    └── Workload Identity enabled
```

**Implementation:**
```bash
# Create GKE subnet with secondary ranges
gcloud compute networks subnets create gke-subnet \
  --network=hub-vpc \
  --region=us-central1 \
  --range=10.0.4.0/22 \
  --secondary-range pods=10.0.16.0/20,services=10.0.32.0/20 \
  --enable-private-ip-google-access

# Grant Network User role to service project GKE SA
gcloud compute networks subnets add-iam-policy-binding gke-subnet \
  --region=us-central1 \
  --member=serviceAccount:service-PROJECT_NUMBER@container-engine-robot.iam.gserviceaccount.com \
  --role=roles/compute.networkUser

# Create private GKE cluster in service project
gcloud container clusters create private-cluster \
  --enable-ip-alias \
  --network=projects/HOST_PROJECT/global/networks/hub-vpc \
  --subnetwork=projects/HOST_PROJECT/regions/us-central1/subnetworks/gke-subnet \
  --cluster-secondary-range-name=pods \
  --services-secondary-range-name=services \
  --enable-private-nodes \
  --enable-private-endpoint \
  --master-ipv4-cidr=172.16.0.0/28 \
  --enable-master-authorized-networks \
  --master-authorized-networks=10.0.8.0/24 \
  --region=us-central1
```

---

## Hybrid Connectivity Architecture

### Pattern 1: HA VPN for Multi-Site Connectivity

**Architecture:**
```
          ┌─────────────────────────────────┐
          │      GCP VPC Network            │
          │                                  │
          │  ┌──────────────────────────┐   │
          │  │  HA VPN Gateway          │   │
          │  │  Interface 0: 35.x.x.1   │   │
          │  │  Interface 1: 35.x.x.2   │   │
          │  └───┬──────────────────┬───┘   │
          └──────┼──────────────────┼────────┘
                 │                  │
                 │ IPsec Tunnel 1   │ IPsec Tunnel 2
                 │                  │
          ┌──────▼──────────────────▼────────┐
          │   On-Premises Network            │
          │                                  │
          │  ┌──────────────────────────┐   │
          │  │  On-Prem VPN Gateway 1   │   │
          │  │  Interface: 203.0.113.1  │   │
          │  └──────────────────────────┘   │
          │  ┌──────────────────────────┐   │
          │  │  On-Prem VPN Gateway 2   │   │
          │  │  Interface: 203.0.113.2  │   │
          │  └──────────────────────────┘   │
          └──────────────────────────────────┘
```

**Configuration for 99.99% SLA:**
```bash
# Create HA VPN gateway
gcloud compute vpn-gateways create ha-vpn-gw \
  --network=production-vpc \
  --region=us-central1

# Create external VPN gateway resource (2 interfaces)
gcloud compute external-vpn-gateways create on-prem-gw \
  --interfaces 0=203.0.113.1,1=203.0.113.2

# Create Cloud Router with high-priority ASN
gcloud compute routers create cloud-router \
  --network=production-vpc \
  --region=us-central1 \
  --asn=65001

# Create VPN tunnels (4 total for maximum redundancy)
# Tunnel 1: Interface 0 → On-Prem Gateway 1
gcloud compute vpn-tunnels create tunnel-0-to-gw1 \
  --peer-external-gateway=on-prem-gw \
  --peer-external-gateway-interface=0 \
  --region=us-central1 \
  --ike-version=2 \
  --shared-secret=SECRET_1 \
  --router=cloud-router \
  --vpn-gateway=ha-vpn-gw \
  --interface=0

# Tunnel 2: Interface 0 → On-Prem Gateway 2
gcloud compute vpn-tunnels create tunnel-0-to-gw2 \
  --peer-external-gateway=on-prem-gw \
  --peer-external-gateway-interface=1 \
  --region=us-central1 \
  --ike-version=2 \
  --shared-secret=SECRET_2 \
  --router=cloud-router \
  --vpn-gateway=ha-vpn-gw \
  --interface=0

# Tunnel 3: Interface 1 → On-Prem Gateway 1
gcloud compute vpn-tunnels create tunnel-1-to-gw1 \
  --peer-external-gateway=on-prem-gw \
  --peer-external-gateway-interface=0 \
  --region=us-central1 \
  --ike-version=2 \
  --shared-secret=SECRET_3 \
  --router=cloud-router \
  --vpn-gateway=ha-vpn-gw \
  --interface=1

# Tunnel 4: Interface 1 → On-Prem Gateway 2
gcloud compute vpn-tunnels create tunnel-1-to-gw2 \
  --peer-external-gateway=on-prem-gw \
  --peer-external-gateway-interface=1 \
  --region=us-central1 \
  --ike-version=2 \
  --shared-secret=SECRET_4 \
  --router=cloud-router \
  --vpn-gateway=ha-vpn-gw \
  --interface=1

# Configure BGP sessions with different priorities
# Primary path (higher preference)
gcloud compute routers add-bgp-peer cloud-router \
  --peer-name=bgp-peer-tunnel-0 \
  --interface=if-tunnel-0 \
  --peer-ip-address=169.254.0.2 \
  --peer-asn=65002 \
  --advertised-route-priority=100 \
  --region=us-central1

# Backup path (lower preference)
gcloud compute routers add-bgp-peer cloud-router \
  --peer-name=bgp-peer-tunnel-1 \
  --interface=if-tunnel-1 \
  --peer-ip-address=169.254.1.2 \
  --peer-asn=65002 \
  --advertised-route-priority=200 \
  --region=us-central1
```

### Pattern 2: Cloud Interconnect for Enterprise

**Architecture:**
```
                        ┌────────────────────────┐
                        │   GCP Region           │
                        │                        │
                        │  ┌──────────────────┐  │
                        │  │  VPC Network     │  │
                        │  │  10.0.0.0/16     │  │
                        │  └────────┬─────────┘  │
                        │           │            │
                        │  ┌────────▼─────────┐  │
                        │  │  Cloud Router    │  │
                        │  │  BGP: AS 65001   │  │
                        │  └────────┬─────────┘  │
                        │           │            │
                        │  ┌────────▼─────────┐  │
                        │  │  VLAN Attachment │  │
                        │  │  VLAN 100        │  │
                        │  └────────┬─────────┘  │
                        └───────────┼────────────┘
                                    │
                                    │ 10 Gbps
                                    │
                 ┌──────────────────┼──────────────────┐
                 │  Google Edge PoP (Colocation)       │
                 │                                     │
                 │  ┌──────────────┼──────────────┐   │
                 │  │  Interconnect Connection     │   │
                 │  │  (Dedicated or Partner)      │   │
                 │  └──────────────┬──────────────┘   │
                 └─────────────────┼──────────────────┘
                                   │
                        ┌──────────▼─────────┐
                        │  Enterprise Router  │
                        │  BGP: AS 65002      │
                        │  On-Premises Network│
                        │  192.168.0.0/16     │
                        └─────────────────────┘
```

**Dedicated Interconnect Configuration:**
```bash
# Create Cloud Router
gcloud compute routers create interconnect-router \
  --network=production-vpc \
  --region=us-central1 \
  --asn=65001

# Create VLAN attachment (after Interconnect provisioned)
gcloud compute interconnects attachments dedicated create vlan-attachment-1 \
  --region=us-central1 \
  --router=interconnect-router \
  --interconnect=my-interconnect \
  --vlan=100 \
  --candidate-subnets=169.254.0.0/29

# Configure BGP session
gcloud compute routers add-interface interconnect-router \
  --interface-name=interconnect-if \
  --ip-address=169.254.0.1 \
  --mask-length=29 \
  --interconnect-attachment=vlan-attachment-1 \
  --region=us-central1

gcloud compute routers add-bgp-peer interconnect-router \
  --peer-name=on-prem-peer \
  --interface=interconnect-if \
  --peer-ip-address=169.254.0.2 \
  --peer-asn=65002 \
  --region=us-central1
```

### Pattern 3: Hybrid Architecture with Multiple Connectivity Options

**Architecture (Active-Active):**
```
                    ┌──────────────────────────┐
                    │    GCP VPC Network       │
                    │                          │
                    │  ┌──────┐   ┌─────────┐ │
                    │  │Cloud │   │ Cloud   │ │
                    │  │Router│   │ Router  │ │
                    │  │  VPN │   │Interconn│ │
                    │  └───┬──┘   └────┬────┘ │
                    └──────┼───────────┼───────┘
                           │           │
                    VPN    │           │ Interconnect
                  (Backup) │           │ (Primary)
                           │           │
                    ┌──────▼───────────▼───────┐
                    │  On-Premises Network     │
                    └──────────────────────────┘
```

**Use Case:** High availability with cost optimization
- **Primary:** Interconnect (low latency, high bandwidth, cost-effective for large traffic)
- **Backup:** HA VPN (automatic failover, lower bandwidth acceptable)

**BGP Route Priority Configuration:**
```bash
# Interconnect: Higher priority (lower MED)
gcloud compute routers add-bgp-peer interconnect-router \
  --peer-name=on-prem-interconnect \
  --advertised-route-priority=100 \
  --region=us-central1

# VPN: Lower priority (higher MED)
gcloud compute routers add-bgp-peer vpn-router \
  --peer-name=on-prem-vpn \
  --advertised-route-priority=200 \
  --region=us-central1
```

### Pattern 4: Multi-Region Hybrid Connectivity

**Architecture:**
```
On-Premises Network
        ↓
        │
   ┌────┴────┐
   │         │
   ↓         ↓
GCP us-central1    GCP europe-west1
   (Primary)          (Secondary)
   │                  │
   ├─ VPC Network ────┤
   │  (Global VPC)    │
   │                  │
   └──────────────────┘
```

**Dynamic Routing Mode:**
```bash
# Set to GLOBAL for multi-region route propagation
gcloud compute networks update production-vpc \
  --bgp-routing-mode=GLOBAL
```

**Benefits:**
- Routes learned in one region propagated to all regions
- Automatic failover between regions
- Regional Cloud Routers share routes

---

## Network Security Architecture

### Defense in Depth Layers

**Layer 1: Network Isolation**
```
Organization
├── Production VPC (Strict firewall rules)
├── Development VPC (Separate, no access to prod)
└── Shared Services VPC (Peered to prod with limited access)
```

**Layer 2: VPC Service Controls**

**Perimeter Configuration:**
```bash
# Create access policy
gcloud access-context-manager policies create \
  --organization=ORGANIZATION_ID \
  --title="Production Access Policy"

# Create service perimeter
gcloud access-context-manager perimeters create prod-perimeter \
  --title="Production Perimeter" \
  --resources=projects/PROJECT_NUMBER \
  --restricted-services=storage.googleapis.com,bigquery.googleapis.com \
  --access-levels=corp_network \
  --policy=POLICY_ID \
  --perimeter-type=regular
```

**Use Case:** Prevent data exfiltration from Cloud Storage/BigQuery

**Layer 3: Hierarchical Firewall Policies**

**Organization-Level Deny Rules:**
```bash
# Deny all external SSH except from corporate IPs
gcloud compute firewall-policies create org-deny-policy \
  --organization=ORGANIZATION_ID

gcloud compute firewall-policies rules create 1000 \
  --firewall-policy=org-deny-policy \
  --action=deny \
  --direction=ingress \
  --src-ip-ranges=0.0.0.0/0 \
  --layer4-configs=tcp:22 \
  --organization=ORGANIZATION_ID

gcloud compute firewall-policies rules create 900 \
  --firewall-policy=org-deny-policy \
  --action=allow \
  --direction=ingress \
  --src-ip-ranges=203.0.113.0/24 \
  --layer4-configs=tcp:22 \
  --organization=ORGANIZATION_ID
```

**Layer 4: VPC Firewall Rules (Project-Level)**

**Micro-Segmentation:**
```bash
# Default deny all ingress
gcloud compute firewall-rules create deny-all-ingress \
  --network=production-vpc \
  --action=DENY \
  --direction=INGRESS \
  --rules=all \
  --source-ranges=0.0.0.0/0 \
  --priority=65534

# Allow web tier from load balancer only
gcloud compute firewall-rules create allow-lb-to-web \
  --network=production-vpc \
  --allow=tcp:8080 \
  --source-ranges=35.191.0.0/16,130.211.0.0/22 \
  --target-service-accounts=web-sa@project.iam.gserviceaccount.com \
  --priority=1000

# Allow app tier from web tier only
gcloud compute firewall-rules create allow-web-to-app \
  --network=production-vpc \
  --allow=tcp:8080 \
  --source-service-accounts=web-sa@project.iam.gserviceaccount.com \
  --target-service-accounts=app-sa@project.iam.gserviceaccount.com \
  --priority=1000

# Allow database from app tier only
gcloud compute firewall-rules create allow-app-to-db \
  --network=production-vpc \
  --allow=tcp:5432 \
  --source-service-accounts=app-sa@project.iam.gserviceaccount.com \
  --target-service-accounts=db-sa@project.iam.gserviceaccount.com \
  --priority=1000
```

### Pattern: Private Service Connect

**Architecture:**
```
Consumer VPC                Producer VPC
(Your Project)              (Service Provider)
                            
[Your App] ──────┐          ┌─────[Backend Service]
                 │          │
                 ↓          ↑
          [PSC Endpoint]───→[Service Attachment]
          10.1.0.100        (Published Service)
```

**Use Case:** Private access to managed services or partner services

**Consumer Side:**
```bash
# Create Private Service Connect endpoint
gcloud compute addresses create psc-endpoint \
  --region=us-central1 \
  --subnet=consumer-subnet \
  --addresses=10.1.0.100

gcloud compute forwarding-rules create psc-forwarding-rule \
  --region=us-central1 \
  --network=consumer-vpc \
  --address=psc-endpoint \
  --target-service-attachment=projects/SERVICE_PROJECT/regions/us-central1/serviceAttachments/SERVICE_NAME
```

---

## Load Balancing Architecture

### Pattern 1: Global External Application Load Balancer

**Architecture:**
```
                     Internet
                         ↓
              [Cloud Armor - DDoS Protection]
                         ↓
          [External Application Load Balancer]
                  (Global Anycast IP)
                         ↓
        ┌────────────────┼────────────────┐
        │                │                │
 [Backend: us-central1]  │  [Backend: europe-west1]
        │                │                │
   [MIG: 3 instances]    │  [MIG: 3 instances]
        │                │                │
   Cloud CDN enabled     │  Cloud CDN enabled
```

**Benefits:**
- Single global IP address
- Automatic routing to nearest region
- Cloud CDN integration
- SSL/TLS termination
- Cloud Armor protection

**Implementation:**
```bash
# Reserve global static IP
gcloud compute addresses create lb-ipv4 \
  --ip-version=IPV4 \
  --global

# Create health check
gcloud compute health-checks create http http-health-check \
  --port=80 \
  --request-path=/health

# Create backend service
gcloud compute backend-services create web-backend \
  --protocol=HTTP \
  --health-checks=http-health-check \
  --global \
  --enable-cdn \
  --cache-mode=CACHE_ALL_STATIC

# Add backends (MIGs in multiple regions)
gcloud compute backend-services add-backend web-backend \
  --instance-group=us-central1-mig \
  --instance-group-region=us-central1 \
  --balancing-mode=UTILIZATION \
  --max-utilization=0.8 \
  --capacity-scaler=1.0 \
  --global

gcloud compute backend-services add-backend web-backend \
  --instance-group=europe-west1-mig \
  --instance-group-region=europe-west1 \
  --balancing-mode=UTILIZATION \
  --max-utilization=0.8 \
  --capacity-scaler=1.0 \
  --global

# Create URL map
gcloud compute url-maps create web-map \
  --default-service=web-backend

# Create target HTTP proxy
gcloud compute target-http-proxies create http-lb-proxy \
  --url-map=web-map

# Create global forwarding rule
gcloud compute forwarding-rules create http-content-rule \
  --address=lb-ipv4 \
  --global \
  --target-http-proxy=http-lb-proxy \
  --ports=80
```

### Pattern 2: Internal Application Load Balancer (Shared VPC)

**Architecture:**
```
Host Project (Shared VPC)
└── Internal Load Balancer (10.0.0.100)
        ↓
Service Project A        Service Project B
[MIG: App Servers]      [MIG: App Servers]
```

**Use Case:** Private load balancing across service projects

**Implementation:**
```bash
# In host project, create internal load balancer
gcloud compute backend-services create internal-app-backend \
  --protocol=HTTP \
  --health-checks=internal-health-check \
  --region=us-central1 \
  --load-balancing-scheme=INTERNAL_MANAGED

# Add backends from service projects
gcloud compute backend-services add-backend internal-app-backend \
  --instance-group=projects/SERVICE_PROJECT_A/zones/us-central1-a/instanceGroups/mig-a \
  --region=us-central1

# Create forwarding rule with subnet from host project
gcloud compute forwarding-rules create internal-http-rule \
  --load-balancing-scheme=INTERNAL_MANAGED \
  --network=projects/HOST_PROJECT/global/networks/shared-vpc \
  --subnet=projects/HOST_PROJECT/regions/us-central1/subnetworks/app-subnet \
  --address=10.0.0.100 \
  --ports=80 \
  --region=us-central1 \
  --target-http-proxy=internal-http-proxy
```

### Pattern 3: Multi-Tier with Internal and External Load Balancers

**Architecture:**
```
Internet
   ↓
External ALB (35.x.x.x)
   ↓
Frontend Tier (10.0.1.0/24)
   ↓
Internal ALB (10.0.2.100)
   ↓
Backend Tier (10.0.2.0/24)
   ↓
Internal TCP/UDP LB (10.0.3.100)
   ↓
Database Tier (10.0.3.0/24)
```

---

## Network Performance & Optimization

### Bandwidth Optimization

**1. Premium vs Standard Tier:**

**Premium Tier (Default):**
- Enters Google network at closest PoP to user
- Global load balancing
- Lower latency
- Higher cost

**Standard Tier:**
- Routes over public internet
- Regional load balancing only
- Higher latency
- Lower cost

```bash
# Set VM to Standard Tier
gcloud compute instances create my-instance \
  --zone=us-central1-a \
  --network-tier=STANDARD
```

**2. VPC Flow Logs for Analysis:**

```bash
# Enable VPC Flow Logs on subnet
gcloud compute networks subnets update my-subnet \
  --region=us-central1 \
  --enable-flow-logs \
  --logging-aggregation-interval=interval-5-sec \
  --logging-flow-sampling=0.5 \
  --logging-metadata=include-all
```

**3. Packet Mirroring for Troubleshooting:**

```bash
# Create packet mirroring policy
gcloud compute packet-mirrorings create my-mirroring \
  --region=us-central1 \
  --network=production-vpc \
  --mirrored-subnets=my-subnet \
  --collector-ilb=INTERNAL_LB_FORWARDING_RULE
```

### Latency Optimization

**1. Placement Policies:**

```bash
# Compact placement for low latency
gcloud compute resource-policies create group-placement compact-policy \
  --region=us-central1 \
  --collocation=COLLOCATED

# Use in MIG template
gcloud compute instance-templates create low-latency-template \
  --region=us-central1 \
  --resource-policies=compact-policy
```

**2. Regional vs Zonal Resources:**
- Use **regional** MIGs for HA
- Use **zonal** MIGs for lowest latency (same-zone communication)

---

## Multi-Region & Global Networking

### Global VPC with Regional Workloads

**Architecture:**
```yaml
Global VPC: production-vpc

Regions:
  us-central1:
    - app-us-central1 subnet (10.0.1.0/24)
    - Regional MIG with 10 instances
    - Regional Internal LB
    
  europe-west1:
    - app-europe-west1 subnet (10.1.1.0/24)
    - Regional MIG with 10 instances
    - Regional Internal LB
    
  asia-east1:
    - app-asia-east1 subnet (10.2.1.0/24)
    - Regional MIG with 10 instances
    - Regional Internal LB

Frontend:
  - Global External Application Load Balancer
  - Cloud CDN enabled
  - Single Anycast IP
  - Automatic regional routing
```

### Cross-Region Private Connectivity

**All regions share the same VPC:**
- Instances can communicate using internal IPs
- Subject to firewall rules
- No need for VPN or peering
- Egress charged between regions

---

## Network Topology Patterns

### Pattern 1: Disaster Recovery (Active-Passive)

**Architecture:**
```
Primary Region (us-central1)      DR Region (us-east1)
[Active Workload]                 [Standby]
        │                              │
        └──────── VPC Network ─────────┘
        
Primary: Normal traffic
DR: Standby with periodic snapshots
Failover: Manual or automated DNS/LB switch
```

### Pattern 2: Active-Active Multi-Region

**Architecture:**
```
Global Load Balancer (Anycast IP)
        │
   ┌────┴────┐
   │         │
Region A   Region B
(Active)   (Active)
   │         │
Both handle traffic simultaneously
```

---

## Cost Optimization Strategies

### 1. Ingress vs Egress

**Free:**
- Ingress from internet to GCP
- Within same zone (same VPC)
- Between GCP services in same region (some exceptions)

**Paid:**
- Egress to internet
- Between regions
- Between zones (lower cost)
- To on-premises (via Interconnect cheaper than VPN)

### 2. Use Cloud NAT Instead of External IPs

```bash
# Cloud NAT: $0.045/hour + $0.045/GB
# External IP: Static = $0.010/hour, Ephemeral = Free (but egress costs same)
# Savings: Reduced IP costs for many instances
```

### 3. Private Google Access

```bash
# Avoid egress charges to Google APIs
gcloud compute networks subnets update my-subnet \
  --region=us-central1 \
  --enable-private-ip-google-access
```

### 4. Cloud CDN

```bash
# Reduce origin egress by caching at edge
# CDN egress typically cheaper than origin egress
--enable-cdn
```

---

## PCA Exam Tips

### 1. Hybrid Connectivity Decision Matrix

| Requirement | Solution |
|------------|----------|
| < 3 Gbps bandwidth | HA VPN |
| > 3 Gbps bandwidth | Cloud Interconnect |
| Low latency critical | Interconnect (does not traverse internet) |
| Quick setup | HA VPN (hours vs weeks for Interconnect) |
| Cost-sensitive, low traffic | HA VPN |
| High traffic volume | Interconnect (cheaper per GB) |
| 99.99% SLA | HA VPN (with proper config) or redundant Interconnect |
| Encrypted | HA VPN (IPsec native) or HA VPN over Interconnect |

### 2. VPC Design Decisions

**Shared VPC vs VPC Peering:**
- **Shared VPC:** Centralized admin, single network, IAM integration
- **VPC Peering:** Separate networks, separate admin, no transitive routing

**Auto vs Custom Mode:**
- **Auto:** Quick start, limited control
- **Custom:** Production recommended, full control, planned IP ranges

### 3. Load Balancer Selection

| Load Balancer | Scope | Use Case |
|--------------|-------|----------|
| External ALB | Global | HTTP(S), multi-region web apps, SSL offload, Cloud CDN |
| Internal ALB | Regional | HTTP(S) internal services, microservices |
| External Network LB (Passthrough) | Regional | TCP/UDP, preserve client IP, non-HTTP |
| Internal Network LB (Passthrough) | Regional | TCP/UDP internal, low latency |
| External Network LB (Proxy) | Global | TCP with SSL offload, global anycast |
| Internal Network LB (Proxy) | Regional | TCP with SSL offload, internal |

### 4. Firewall Best Practices

- Use **service accounts** (not network tags) for production
- **Hierarchical policies** at organization level for enforce deny rules
- **Least privilege:** Deny by default, allow specific
- Enable **firewall logging** for security audit
- Use **Firewall Insights** to identify unused rules

### 5. Security Architecture

**Principle:** Defense in Depth
1. **VPC isolation** (project/network boundaries)
2. **Firewall rules** (network-level filtering)
3. **IAM policies** (identity-based)
4. **VPC Service Controls** (data exfiltration prevention)
5. **Private Google Access** (no external IPs)
6. **Cloud Armor** (DDoS, WAF)

### 6. Common Exam Scenarios

**Scenario:** "Need private connectivity between GCP and on-prem with > 10 Gbps"
- **Answer:** Dedicated Interconnect (10 or 100 Gbps)

**Scenario:** "Multiple projects need to share network, centralized firewall management"
- **Answer:** Shared VPC (not VPC peering)

**Scenario:** "Global web application, SSL termination, DDoS protection"
- **Answer:** External Application Load Balancer + Cloud Armor + Cloud CDN

**Scenario:** "Instances need to access Google APIs without external IPs"
- **Answer:** Private Google Access (enable on subnet)

**Scenario:** "Separate prod and dev environments but share logging/monitoring"
- **Answer:** Multiple VPCs with VPC peering to shared services VPC

**Scenario:** "High availability VPN with 99.99% SLA"
- **Answer:** HA VPN with 2 tunnels to 2 on-prem gateways

**Scenario:** "Prevent data exfiltration from Cloud Storage/BigQuery"
- **Answer:** VPC Service Controls perimeter

**Scenario:** "Cost optimization for multi-region deployment"
- **Answer:** Premium tier for latency-sensitive, Standard tier for cost-sensitive

### 7. IP Address Planning Red Flags

- Overlapping IP ranges (can't peer/VPN)
- Not reserving space for growth
- Using default network in production
- /30 or /29 subnets (too small, only 0-2 usable IPs)

### 8. BGP and Dynamic Routing

- **Regional mode:** Routes learned in one region stay in that region
- **Global mode:** Routes propagated to all regions (recommended for multi-region)
- **MED (Multi-Exit Discriminator):** Lower value = higher priority (use for primary/backup paths)
- **AS path prepending:** Make path look longer to de-prefer it

### 9. Performance Optimization

- **Placement policies:** Compact for low latency (HPC, gaming)
- **Network tier:** Premium for global apps, Standard for cost savings
- **VPC Flow Logs:** Sampling 0.5 for troubleshooting, lower for cost
- **Cloud CDN:** Enable for static content (images, JS, CSS)

### 10. Shared VPC Permissions

- **Shared VPC Admin:** `compute.xpnAdmin` + `resourcemanager.projectIamAdmin`
- **Network Admin:** `compute.networkAdmin` (manage networks, routes)
- **Security Admin:** `compute.securityAdmin` (manage firewall rules)
- **Service Project Admin:** `compute.networkUser` (use subnets)
