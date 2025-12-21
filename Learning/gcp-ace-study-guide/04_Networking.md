# 04. Networking (Masterclass Edition)

Networking in Google Cloud is a Global Software-Defined Network (SDN). Google's **Andromeda** is the control plane that orchestrates this globally, providing ~200 Tbps of bandwidth.

---

## 4.1 VPC (Virtual Private Cloud) Architecture

### 4.1.1 The Global Scope
Unlike other clouds where VPCs are regional, **GCP VPCs are Global**.
*   **Subnets**: Are regional resources. A VPC can have subnets in every Google Cloud region.
*   **Routing**: By default, an instance in `us-central1-a` can talk to an instance in `asia-east1-a` via internal IPs without a VPN or peering, provided they are in the same VPC.

```bash
# Create a custom VPC
gcloud compute networks create my-vpc \
    --subnet-mode=custom \
    --bgp-routing-mode=regional

# Create a subnet
gcloud compute networks subnets create my-subnet \
    --network=my-vpc \
    --region=us-central1 \
    --range=10.0.1.0/24 \
    --enable-private-ip-google-access \
    --enable-flow-logs

# Create subnet with secondary ranges (for GKE)
gcloud compute networks subnets create gke-subnet \
    --network=my-vpc \
    --region=us-central1 \
    --range=10.0.0.0/24 \
    --secondary-range=pods=10.1.0.0/16,services=10.2.0.0/20
```

### 4.1.2 VPC Modes

| Mode | Subnet Creation | IP Ranges | Use Case |
|------|-----------------|-----------|----------|
| **Auto Mode** | Auto (one per region) | 10.128.0.0/9 (predefined) | Quick demos, PoC |
| **Custom Mode** | Manual | You define | Production (recommended) |

**Auto to Custom Conversion**: One-way conversion. Cannot go back to auto mode.

```bash
# Convert auto-mode VPC to custom mode
gcloud compute networks update my-auto-vpc --switch-to-custom-subnet-mode
```

### 4.1.3 Shared VPC (Scalable Networking)
Allows an organization to connect resources from multiple projects to a common VPC network.

| Role | Scope | Permissions |
|------|-------|-------------|
| **Shared VPC Admin** | Organization/Folder | Enable/disable host projects, attach service projects |
| **Service Project Admin** | Service Project | Manage resources using shared subnets |
| **Network User** | Subnet | Use subnets from host project |
| **Network Admin** | Host Project | Manage shared VPC resources |

```bash
# Enable Shared VPC on host project
gcloud compute shared-vpc enable HOST_PROJECT_ID

# Associate service project
gcloud compute shared-vpc associated-projects add SERVICE_PROJECT_ID \
    --host-project=HOST_PROJECT_ID

# Grant Network User role to service project developers
gcloud compute networks subnets add-iam-policy-binding my-subnet \
    --region=us-central1 \
    --project=HOST_PROJECT_ID \
    --member="user:developer@example.com" \
    --role="roles/compute.networkUser"
```

#### Shared VPC Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ORGANIZATION                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               HOST PROJECT (Network)                 │    │
│  │  ┌─────────────────────────────────────────────────┐│    │
│  │  │                  SHARED VPC                     ││    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      ││    │
│  │  │  │ Subnet A │  │ Subnet B │  │ Subnet C │      ││    │
│  │  │  │us-central│  │us-east1  │  │europe    │      ││    │
│  │  │  └────┬─────┘  └────┬─────┘  └────┬─────┘      ││    │
│  │  └───────┼─────────────┼─────────────┼────────────┘│    │
│  └──────────┼─────────────┼─────────────┼─────────────┘    │
│             │             │             │                   │
│  ┌──────────▼───┐  ┌──────▼───────┐  ┌──▼────────────┐    │
│  │SERVICE PROJ 1│  │SERVICE PROJ 2│  │SERVICE PROJ 3 │    │
│  │   (Web App)  │  │  (Database)  │  │   (Backend)   │    │
│  └──────────────┘  └──────────────┘  └───────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 4.1.4 VPC Peering & Transitivity

| Feature | VPC Peering | Shared VPC |
|---------|-------------|------------|
| **Scope** | Cross-project, cross-org | Same organization |
| **Subnets** | Separate | Shared |
| **Administration** | Decentralized | Centralized |
| **Transitivity** | ❌ Not transitive | ✅ All service projects can communicate |

**The Transitivity Limit**: If VPC-A peers with VPC-B, and VPC-B peers with VPC-C, **VPC-A cannot reach VPC-C**.

**Solutions**:
1.  Create direct peering (VPC-A ↔ VPC-C)
2.  Use Cloud VPN with BGP
3.  Deploy NVA (Network Virtual Appliance) in hub
4.  Use Private Service Connect

```bash
# Create VPC peering
gcloud compute networks peerings create peer-to-vpc-b \
    --network=vpc-a \
    --peer-network=projects/other-project/global/networks/vpc-b \
    --export-custom-routes \
    --import-custom-routes
```

---

## 4.2 Firewall Rules & Security

### 4.2.1 Firewall Fundamentals
*   **Stateful**: Return traffic is allowed automatically.
*   **Direction**: Ingress (inbound) or Egress (outbound).
*   **Priority Hierarchy**: Lower numbers = higher priority. Range: 0 to 65535.

#### Implied Rules (Cannot be deleted)

| Rule | Priority | Direction | Action |
|------|----------|-----------|--------|
| Allow all egress | 65535 | Egress | Allow |
| Deny all ingress | 65535 | Ingress | Deny |
| Allow internal (default network only) | 65534 | Ingress | Allow |

```bash
# Create allow rule for HTTP
gcloud compute firewall-rules create allow-http \
    --network=my-vpc \
    --direction=INGRESS \
    --priority=1000 \
    --action=ALLOW \
    --rules=tcp:80,tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=web-server

# Create rule using service account (more secure)
gcloud compute firewall-rules create allow-internal-sa \
    --network=my-vpc \
    --direction=INGRESS \
    --priority=1000 \
    --action=ALLOW \
    --rules=tcp:8080 \
    --source-service-accounts=backend-sa@project.iam.gserviceaccount.com \
    --target-service-accounts=frontend-sa@project.iam.gserviceaccount.com

# Create deny rule with logging
gcloud compute firewall-rules create deny-ssh-all \
    --network=my-vpc \
    --direction=INGRESS \
    --priority=900 \
    --action=DENY \
    --rules=tcp:22 \
    --source-ranges=0.0.0.0/0 \
    --enable-logging
```

### 4.2.2 Target Specification Methods

| Method | Security | Flexibility | Use Case |
|--------|----------|-------------|----------|
| **All instances** | ❌ Low | ❌ Low | Rarely recommended |
| **Network Tags** | ⚠️ Medium | ✅ High | Dev/Test, simple setups |
| **Service Accounts** | ✅ High | ✅ High | Production (recommended) |

**Why Service Accounts are more secure**:
*   Tags can be changed by anyone with `compute.instances.setTags`
*   Service Accounts require IAM permissions to modify
*   Provides identity-based security, not just network-based

### 4.2.3 Hierarchical Firewall Policies

Managed at Organization or Folder level. Evaluated **before** VPC firewall rules.

| Scope | Applies To | Management |
|-------|------------|------------|
| Organization | All VPCs in org | Org Admin |
| Folder | All VPCs in folder | Folder Admin |
| VPC | Single VPC | Network Admin |

```bash
# Create organization firewall policy
gcloud compute firewall-policies create \
    --organization=123456789 \
    --short-name=org-security-policy \
    --description="Organization-wide security policy"

# Add rule to policy
gcloud compute firewall-policies rules create 100 \
    --firewall-policy=org-security-policy \
    --organization=123456789 \
    --action=deny \
    --direction=INGRESS \
    --src-ip-ranges=0.0.0.0/0 \
    --layer4-configs=tcp:22 \
    --description="Block SSH from internet"

# Associate policy with folder
gcloud compute firewall-policies associations create \
    --firewall-policy=org-security-policy \
    --organization=123456789 \
    --folder=987654321
```

### 4.2.4 VPC Flow Logs

Capture network flows for security analysis and troubleshooting.

```bash
# Enable flow logs on subnet
gcloud compute networks subnets update my-subnet \
    --region=us-central1 \
    --enable-flow-logs \
    --logging-aggregation-interval=interval-5-sec \
    --logging-flow-sampling=0.5 \
    --logging-metadata=include-all
```

---

## 4.3 Google Cloud Load Balancing (GCLB)

### 4.3.1 Google Front End (GFE)
Traffic enters Google's network at an Edge Point of Presence (PoP) and is routed over Google's private fiber to the GFEs, which handle the load balancing logic.

### 4.3.2 Load Balancer Selection Matrix

| Load Balancer | Scope | Layer | Traffic Type | Use Case |
|---------------|-------|-------|--------------|----------|
| **Global external Application LB** | Global | 7 | HTTP/HTTPS | Web apps, APIs, CDN |
| **Regional external Application LB** | Regional | 7 | HTTP/HTTPS | Regional web apps |
| **Global external proxy Network LB** | Global | 4 | TCP/SSL | Non-HTTP TCP, gaming |
| **Regional external passthrough Network LB** | Regional | 4 | TCP/UDP | Preserve client IP, any protocol |
| **Regional internal Application LB** | Regional | 7 | HTTP/HTTPS | Internal microservices |
| **Regional internal passthrough Network LB** | Regional | 4 | TCP/UDP | Internal TCP/UDP services |
| **Cross-region internal Application LB** | Global | 7 | HTTP/HTTPS | Multi-region internal services |

### 4.3.3 Global External Application Load Balancer (HTTP/S)

The most feature-rich load balancer.

| Feature | Description |
|---------|-------------|
| **URL Maps** | Route based on host, path, headers |
| **Backend Services** | Groups of backends (MIGs, NEGs, buckets) |
| **Health Checks** | HTTP/HTTPS/TCP/SSL/gRPC |
| **Cloud CDN** | Enable caching at edge |
| **Cloud Armor** | WAF and DDoS protection |
| **SSL Policies** | Control TLS versions and ciphers |

```bash
# Create health check
gcloud compute health-checks create http my-health-check \
    --port=80 \
    --request-path=/healthz

# Create backend service
gcloud compute backend-services create my-backend \
    --protocol=HTTP \
    --port-name=http \
    --health-checks=my-health-check \
    --global

# Add MIG to backend
gcloud compute backend-services add-backend my-backend \
    --instance-group=my-mig \
    --instance-group-region=us-central1 \
    --balancing-mode=UTILIZATION \
    --max-utilization=0.8 \
    --global

# Create URL map
gcloud compute url-maps create my-url-map \
    --default-service=my-backend

# Create HTTPS proxy with managed cert
gcloud compute ssl-certificates create my-cert \
    --domains=www.example.com \
    --global

gcloud compute target-https-proxies create my-https-proxy \
    --url-map=my-url-map \
    --ssl-certificates=my-cert

# Create global forwarding rule
gcloud compute forwarding-rules create my-https-rule \
    --global \
    --target-https-proxy=my-https-proxy \
    --ports=443
```

### 4.3.4 URL Mapping Examples

```yaml
# Route based on path
# /api/* -> api-backend
# /static/* -> storage-bucket
# /* -> web-backend

# Route based on header
# Header: X-Environment: canary -> canary-backend
# Default -> production-backend
```

```bash
# Create URL map with path rules
gcloud compute url-maps add-path-matcher my-url-map \
    --path-matcher-name=my-matcher \
    --default-service=web-backend \
    --path-rules="/api/*=api-backend,/static/*=storage-backend"
```

### 4.3.5 Cloud Armor (WAF + DDoS)

| Feature | Description |
|---------|-------------|
| **Preconfigured Rules** | OWASP Top 10 (SQLi, XSS, etc.) |
| **Custom Rules** | CEL-based expressions |
| **Rate Limiting** | Throttle by IP, region, headers |
| **Adaptive Protection** | ML-based anomaly detection |
| **Bot Management** | reCAPTCHA integration |

```bash
# Create security policy
gcloud compute security-policies create my-policy \
    --description="WAF policy"

# Add rule to block SQL injection
gcloud compute security-policies rules create 1000 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredWaf('sqli-v33-stable')" \
    --action=deny-403

# Add rate limiting rule
gcloud compute security-policies rules create 2000 \
    --security-policy=my-policy \
    --expression="true" \
    --action=rate-based-ban \
    --rate-limit-threshold-count=100 \
    --rate-limit-threshold-interval-sec=60 \
    --ban-duration-sec=600

# Attach policy to backend
gcloud compute backend-services update my-backend \
    --security-policy=my-policy \
    --global
```

---

## 4.4 Hybrid Connectivity (On-Prem to Cloud)

### 4.4.1 Connectivity Options Comparison

| Option | Bandwidth | SLA | Setup Time | Cost | Use Case |
|--------|-----------|-----|------------|------|----------|
| **Cloud VPN (HA)** | Up to 3 Gbps | 99.99% | Hours | Low | Dev/test, backup link |
| **Dedicated Interconnect** | 10-200 Gbps | 99.99% | Weeks | High | Large data transfer, low latency |
| **Partner Interconnect** | 50 Mbps-50 Gbps | 99.9-99.99% | Days | Medium | No Google colo nearby |
| **Cross-Cloud Interconnect** | 10-100 Gbps | 99.9% | Days | High | Multi-cloud (AWS, Azure) |

### 4.4.2 HA Cloud VPN

| Component | Description |
|-----------|-------------|
| **VPN Gateway** | Regional resource with 2 interfaces |
| **Tunnels** | IPsec tunnel per interface |
| **Cloud Router** | BGP for dynamic routing |
| **Peer Gateway** | Your on-prem VPN device |

```bash
# Create HA VPN gateway
gcloud compute vpn-gateways create my-vpn-gw \
    --network=my-vpc \
    --region=us-central1

# Create Cloud Router
gcloud compute routers create my-router \
    --network=my-vpc \
    --region=us-central1 \
    --asn=65001

# Create external VPN gateway (peer)
gcloud compute external-vpn-gateways create on-prem-gw \
    --interfaces=0=203.0.113.1,1=203.0.113.2

# Create VPN tunnels (both interfaces for HA)
gcloud compute vpn-tunnels create tunnel-0 \
    --vpn-gateway=my-vpn-gw \
    --interface=0 \
    --peer-external-gateway=on-prem-gw \
    --peer-external-gateway-interface=0 \
    --shared-secret=mysecret \
    --router=my-router \
    --region=us-central1

gcloud compute vpn-tunnels create tunnel-1 \
    --vpn-gateway=my-vpn-gw \
    --interface=1 \
    --peer-external-gateway=on-prem-gw \
    --peer-external-gateway-interface=1 \
    --shared-secret=mysecret \
    --router=my-router \
    --region=us-central1

# Add BGP peer for dynamic routing
gcloud compute routers add-interface my-router \
    --interface-name=bgp-interface-0 \
    --vpn-tunnel=tunnel-0 \
    --ip-address=169.254.0.1 \
    --mask-length=30 \
    --region=us-central1

gcloud compute routers add-bgp-peer my-router \
    --peer-name=on-prem-peer-0 \
    --interface=bgp-interface-0 \
    --peer-ip-address=169.254.0.2 \
    --peer-asn=65002 \
    --region=us-central1
```

### 4.4.3 Cloud Interconnect

#### Dedicated Interconnect
Direct physical connection at Google Edge PoP.

| Capacity | Configuration |
|----------|---------------|
| 10 Gbps | Single circuit |
| 100 Gbps | Single circuit (select locations) |
| 200 Gbps | 2x 100 Gbps link bundle |

#### Partner Interconnect
Connect through a service provider.

| Tier | Speed | SLA |
|------|-------|-----|
| Layer 2 | 50 Mbps - 50 Gbps | Varies |
| Layer 3 | 50 Mbps - 50 Gbps | BGP managed by partner |

```bash
# Create VLAN attachment for Dedicated Interconnect
gcloud compute interconnects attachments dedicated create my-attachment \
    --router=my-router \
    --region=us-central1 \
    --interconnect=my-interconnect \
    --vlan=100 \
    --bandwidth=BPS_1G
```

### 4.4.4 Private Google Access & Private Service Connect

#### Private Google Access
VMs with only internal IPs can reach Google APIs (Cloud Storage, BigQuery, etc.).

| Type | Destination | DNS |
|------|-------------|-----|
| **Private Google Access** | Google APIs | *.googleapis.com |
| **Private Google Access for on-prem** | Google APIs via VPN/Interconnect | Restricted VIP |
| **Private Service Connect** | Specific Google services | Custom endpoint |

```bash
# Enable Private Google Access on subnet
gcloud compute networks subnets update my-subnet \
    --region=us-central1 \
    --enable-private-ip-google-access
```

#### Private Service Connect (PSC)
Create private endpoints for Google services or your own services.

| Use Case | Description |
|----------|-------------|
| **Consumer Endpoint** | Access Google APIs privately |
| **Producer Service** | Expose your service to other VPCs |
| **Published Service** | Access third-party managed services |

```bash
# Create PSC endpoint for Google APIs
gcloud compute addresses create psc-endpoint \
    --global \
    --purpose=PRIVATE_SERVICE_CONNECT \
    --network=my-vpc \
    --addresses=10.0.100.1

gcloud compute forwarding-rules create psc-rule \
    --global \
    --network=my-vpc \
    --address=psc-endpoint \
    --target-google-apis-bundle=all-apis
```

---

## 4.5 Cloud NAT
Enables instances without public IPs to access the internet (for updates/patches) but blocks the internet from reaching the instances.
*   **Managed**: No NAT GW instances to manage.
*   **Scaling**: Highly available and scales automatically per region.

```bash
# Create Cloud Router (required for Cloud NAT)
gcloud compute routers create nat-router \
    --network=my-vpc \
    --region=us-central1

# Create Cloud NAT gateway
gcloud compute routers nats create my-nat \
    --router=nat-router \
    --region=us-central1 \
    --nat-all-subnet-ip-ranges \
    --auto-allocate-nat-external-ips

# Create NAT with specific subnets and manual IPs
gcloud compute addresses create nat-ip --region=us-central1

gcloud compute routers nats create selective-nat \
    --router=nat-router \
    --region=us-central1 \
    --nat-custom-subnet-ip-ranges=my-subnet \
    --nat-external-ip-pool=nat-ip
```

### 4.5.1 Cloud NAT Configuration Options

| Setting | Description |
|---------|-------------|
| **NAT IP Allocation** | Auto (Google manages) or Manual (you provide) |
| **Source Subnetworks** | All subnets or specific subnets |
| **Min Ports Per VM** | Minimum ports allocated per VM (default 64) |
| **Enable Logging** | Log NAT translations for troubleshooting |
| **Endpoint-Independent Mapping** | Required for some protocols |

---

## 4.6 Cloud DNS

Google's managed authoritative DNS service.

### 4.6.1 Zone Types

| Type | Scope | Use Case |
|------|-------|----------|
| **Public** | Internet | External DNS resolution |
| **Private** | VPC | Internal DNS for private resources |
| **Forwarding** | On-prem/other DNS | Hybrid DNS queries |
| **Peering** | Other VPC | Cross-VPC DNS resolution |

```bash
# Create private DNS zone
gcloud dns managed-zones create internal-zone \
    --dns-name=internal.example.com. \
    --visibility=private \
    --networks=my-vpc \
    --description="Internal DNS zone"

# Add A record
gcloud dns record-sets create app.internal.example.com. \
    --zone=internal-zone \
    --type=A \
    --ttl=300 \
    --rrdatas=10.0.1.10

# Create DNS forwarding zone (to on-prem DNS)
gcloud dns managed-zones create forward-zone \
    --dns-name=onprem.example.com. \
    --visibility=private \
    --networks=my-vpc \
    --forwarding-targets=192.168.1.53,192.168.1.54 \
    --description="Forward to on-prem DNS"
```

---

## 4.7 Network Service Tiers

| Tier | Routing | Performance | Cost |
|------|---------|-------------|------|
| **Premium** | Google backbone globally | Lower latency, higher throughput | Higher |
| **Standard** | ISP networks | Variable performance | Lower (~25% less) |

**Premium Tier Features**:
*   Traffic enters Google network at nearest PoP
*   Global load balancing
*   Cloud CDN, Cloud Armor

**Standard Tier Features**:
*   Regional load balancing only
*   Traffic uses public internet longer

```bash
# Reserve Premium tier IP
gcloud compute addresses create premium-ip \
    --network-tier=PREMIUM \
    --region=us-central1

# Reserve Standard tier IP
gcloud compute addresses create standard-ip \
    --network-tier=STANDARD \
    --region=us-central1
```
