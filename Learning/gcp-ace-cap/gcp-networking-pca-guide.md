# Google Cloud Networking Guide for PCA Certification

This guide covers advanced networking architectures, hybrid connectivity, and security patterns required for the **Professional Cloud Architect (PCA)** exam.

## 1. Network Architectures

### 1.1 Shared VPC vs. VPC Peering

| Feature | Shared VPC | VPC Peering |
| :--- | :--- | :--- |
| **Model** | Centralized Administration | Decentralized / Collaborative |
| **Transitivity** | **Yes** (Implicit). VMs in different service projects in the same Shared VPC can talk to each other. | **No**. If A peers with B, and B peers with C, A cannot talk to C. |
| **Administration** | Host Project Admin manages network; Service Project Admins manage VMs. | Each VPC owner manages their own network and peering settings. |
| **Use Case** | Multiple teams/projects within the *same organization* needing centralized control. | Connecting independent organizations (SaaS) or distinct administrative domains. |
| **Limits** | Hard limits on number of service projects. | Limits on number of peered networks (25 per VPC). |

### 1.2 Hub-and-Spoke Topology

A common pattern where a central "Hub" VPC connects to multiple "Spoke" VPCs.

*   **Implementation**:
    *   **Via Peering**: Requires a "Transitive" workaround (e.g., NVA/Proxy in Hub) if Spokes need to talk to each other, because Peering is non-transitive.
    *   **Via VPN**: Spokes connect to Hub via VPN. Supports transitivity if routes are advertised.
*   **Use Case**: Centralized egress (NAT), centralized security inspection (IDS/IPS), or shared services (DNS, Active Directory).

## 2. Hybrid Connectivity

Connecting on-premises data centers to Google Cloud.

### 2.1 Cloud VPN
*   **HA VPN (High Availability)**:
    *   **SLA**: 99.99% availability.
    *   **Requirement**: Two public IPs on-prem, two tunnels (active/active or active/passive).
    *   **Routing**: Must use **Dynamic Routing (BGP)**.
*   **Classic VPN**: Deprecated for new deployments. 99.9% SLA.
*   **Use Case**: Low to medium bandwidth requirements, encrypted traffic over public internet.

### 2.2 Cloud Interconnect
*   **Dedicated Interconnect**:
    *   **Physical Link**: Direct physical cable between your network and Google.
    *   **Bandwidth**: 10 Gbps or 100 Gbps increments.
    *   **SLA**: 99.9% (2 links) or 99.99% (4 links in 2 metros).
    *   **Use Case**: High bandwidth, low latency, data residency requirements.
*   **Partner Interconnect**:
    *   **Physical Link**: Connect via a service provider.
    *   **Bandwidth**: 50 Mbps to 10 Gbps.
    *   **Use Case**: You don't have a presence in a Google PoP, or need lower bandwidth than Dedicated.

### 2.3 Direct Peering vs. Carrier Peering
*   *Not* for private VPC access. These connect to Google *public* IPs (Workspace, YouTube, APIs).
*   **Direct Peering**: Direct physical link to Google's edge.
*   **Carrier Peering**: Via a provider.

## 3. Cloud DNS Architectures

### 3.1 Private Zones
*   Resolve internal hostnames for VMs within a VPC.
*   Not accessible from the internet.

### 3.2 Split-Horizon DNS
*   Using the same domain name (e.g., `example.com`) for both internal and external resolution.
*   **Internal Clients**: Resolve to private IPs (via Private Zone).
*   **External Clients**: Resolve to public IPs (via Public Zone).

### 3.3 DNS Forwarding & Peering
*   **Outbound Forwarding Zone**: Forwards DNS queries from VPC to on-prem DNS servers (via VPN/Interconnect).
*   **Inbound Forwarding Policy**: Allows on-prem systems to query Cloud DNS (via a proxy IP).
*   **DNS Peering**: Allows one VPC to resolve names defined in another VPC's Private Zone (essential for Hub-and-Spoke).

## 4. Advanced Security Patterns

### 4.1 Packet Mirroring
*   **Purpose**: Clones traffic from specific VMs/Subnets/Tags and forwards it to a collector (Internal Load Balancer).
*   **Use Case**: Intrusion Detection Systems (IDS), Application Performance Monitoring (APM), Compliance auditing.
*   **Key Constraint**: Collector must be in the same region.

### 4.2 Hierarchical Firewall Policies
*   Define firewall rules at the **Organization** or **Folder** level.
*   **Inheritance**: Rules are inherited by all projects under the node.
*   **Enforcement**: Can create "deny" rules that project admins *cannot* override.
*   **Use Case**: Enforcing global security standards (e.g., "Deny SSH from internet everywhere").

### 4.3 Private Service Connect (PSC)
*   **Consumer**: Access a managed service (in another VPC/Project) via a private IP in your own VPC.
*   **Producer**: Publish a service behind a Load Balancer.
*   **Benefit**: No VPC Peering required. No IP overlap issues. Unidirectional access.

## 5. Routing & Global Load Balancing

### 5.1 Dynamic Routing Mode
*   **Regional**: Cloud Router only learns/advertises routes in the region where it is deployed.
*   **Global**: Cloud Router learns/advertises routes from *all* regions.
*   **Impact**: Required for global access to on-prem resources via a single VPN/Interconnect attachment.

### 5.2 Global Load Balancing with Cloud CDN
*   **External HTTP(S) Load Balancer**: Anycast IP (single global IP).
*   **Cloud CDN**: Caches content at the edge.
*   **Backend Buckets**: Serve static content directly from GCS.
*   **Backend Services**: Serve dynamic content from Instance Groups or NEGs (Network Endpoint Groups).
