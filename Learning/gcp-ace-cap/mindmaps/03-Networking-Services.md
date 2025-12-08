# GCP Networking Services - Detailed Mindmap & Design

## 1. Virtual Private Cloud (VPC)
*   **Network Architecture**
    *   **Global Resource**: VPCs span all regions.
    *   **Subnets**: Regional resources. Define IP ranges.
    *   **Modes**:
        *   *Auto Mode*: One subnet per region automatically. Fixed CIDR (/20). Good for POC.
        *   *Custom Mode*: No subnets initially. You define ranges. Production best practice.
*   **IP Addressing**
    *   *Internal IPs*: RFC 1918 (10.x, 172.16.x, 192.168.x). Communication within VPC.
    *   *External IPs*: Internet routable. Ephemeral (Dynamic) or Static (Reserved).
    *   *Alias IPs*: Secondary ranges for subnets (used by GKE Pods).
*   **Firewall Rules**
    *   **Stateful**: Return traffic automatically allowed.
    *   **Components**: Priority (0-65535), Action (Allow/Deny), Direction (Ingress/Egress), Target (Tags/SA/All), Source/Dest.
    *   **Implied Rules**: Deny all Ingress, Allow all Egress.
    *   **Hierarchical Policies**: Org/Folder level policies (e.g., "Always block port 22").
*   **Routes**
    *   **System Routes**: Default internet route, Subnet routes.
    *   **Custom Routes**: Static (Next hop: VPN, Instance) or Dynamic (BGP).
    *   **Order**: Most specific prefix wins. If equal, highest priority wins.

## 2. VPC Connectivity
*   **VPC Peering**
    *   Connect two VPCs (same or different project/org).
    *   **Non-transitive**: A<->B and B<->C does NOT mean A<->C.
    *   Private communication (Internal IPs).
    *   No subnet overlap allowed.
*   **Shared VPC**
    *   **Host Project**: Owns the network/subnets. Centralized admin.
    *   **Service Project**: Attaches to Host. Uses subnets. Decentralized app teams.
    *   *Use Case*: Centralized network management, distributed resource creation.
*   **Serverless VPC Access**
    *   Connector for Cloud Run/Functions/App Engine to access VPC resources (Redis, SQL) via private IP.

## 3. Load Balancing
*   **Global Load Balancers** (Anycast IP, Cross-region)
    *   **HTTP(S) Load Balancer** (Layer 7)
        *   Traffic: HTTP/HTTPS, HTTP/2.
        *   Backends: Instance Groups, NEGs (Zonal/Internet/Serverless), Buckets.
        *   Features: URL Maps, SSL Offload, Cloud CDN, Cloud Armor (WAF).
    *   **SSL Proxy Load Balancer** (Layer 4)
        *   Traffic: SSL/TCP (Non-HTTP).
        *   Features: SSL Offload, Intelligent Routing.
    *   **TCP Proxy Load Balancer** (Layer 4)
        *   Traffic: TCP (Non-HTTP, No SSL offload needed).
*   **Regional Load Balancers**
    *   **Network Load Balancer** (Layer 4 - External Passthrough)
        *   Traffic: TCP/UDP.
        *   Features: Preserves Client IP. High performance.
    *   **Internal HTTP(S) Load Balancer** (Layer 7)
        *   Traffic: HTTP/HTTPS inside VPC.
        *   Envoy-based proxy.
    *   **Internal TCP/UDP Load Balancer** (Layer 4)
        *   Traffic: TCP/UDP inside VPC.
        *   Andromeda-based (SDN).

## 4. Hybrid Connectivity
*   **Cloud VPN** (IPSec over Internet)
    *   **HA VPN**:
        *   99.99% SLA.
        *   2 Interfaces, 2 External IPs.
        *   Requires Dynamic Routing (BGP).
    *   **Classic VPN**: Legacy. 99.9% SLA. Static routing supported.
*   **Cloud Interconnect** (Physical Link)
    *   **Dedicated Interconnect**:
        *   Direct physical cable to Google.
        *   10 Gbps or 100 Gbps.
        *   High bandwidth, low latency.
    *   **Partner Interconnect**:
        *   Connect via Service Provider.
        *   50 Mbps to 50 Gbps.
        *   SLA depends on provider.
*   **Cloud Router**
    *   Global routing control plane (regional resource).
    *   Uses BGP to exchange routes between VPC and On-prem.
    *   Required for HA VPN and Interconnect.

## 5. Network Services
*   **Cloud DNS**
    *   Managed authoritative DNS.
    *   *Public Zones*: Internet visible.
    *   *Private Zones*: VPC visible only.
    *   *Forwarding Zones*: Hybrid DNS (resolve on-prem names).
*   **Cloud NAT**
    *   Outbound internet access for private VMs.
    *   No inbound connections allowed.
    *   Regional resource.
*   **Private Google Access**
    *   Allow VMs with *only* internal IPs to reach Google APIs (Storage, BigQuery, etc.) via public IPs.
    *   Enabled at Subnet level.

---

## 🧠 Design Decision Guide: Networking

### Load Balancer Selection Flowchart
1.  **Internal or External?**
    *   **Internal**:
        *   HTTP/HTTPS? -> **Internal HTTP(S) LB**
        *   TCP/UDP? -> **Internal TCP/UDP LB**
    *   **External**:
        *   HTTP/HTTPS? -> **Global HTTP(S) LB**
        *   TCP/UDP?
            *   Global / SSL Offload / Proxy? -> **SSL/TCP Proxy**
            *   Regional / Preserve Client IP / UDP? -> **Network LB**

### Hybrid Connectivity Choice
1.  **Bandwidth Needs?**
    *   **Low (< 3 Gbps)** -> **Cloud VPN** (Cheap, Fast setup).
    *   **High (> 10 Gbps)** -> **Dedicated Interconnect**.
    *   **Medium / No Google PoP nearby** -> **Partner Interconnect**.
2.  **SLA Needs?**
    *   **Mission Critical** -> HA VPN or Redundant Interconnect (99.99%).
    *   **Standard** -> Classic VPN (99.9%).

### 🔑 Key Exam Rules
1.  **"Preserve Client IP"** -> **Network Load Balancer** (External Passthrough).
2.  **"WAF" or "DDoS"** -> **Cloud Armor** (Requires HTTP(S) LB).
3.  **"Private Access to APIs"** -> **Private Google Access**.
4.  **"Connect VPCs"** -> **VPC Peering**.
5.  **"Centralized Network Admin"** -> **Shared VPC**.
6.  **"UDP Traffic"** -> **Network LB** (External) or **Internal TCP/UDP LB**.
