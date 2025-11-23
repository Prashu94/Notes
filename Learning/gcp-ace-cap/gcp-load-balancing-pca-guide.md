# Google Cloud Load Balancing & Security Guide for PCA Certification

This guide covers architectural decisions for Load Balancing, Autoscaling, and Edge Security required for the **Professional Cloud Architect (PCA)** exam.

## 1. Choosing the Right Load Balancer

The most common PCA question involves selecting the correct load balancer based on requirements.

### 1.1 Decision Matrix

| Requirement | Recommended Load Balancer | Key Features |
| :--- | :--- | :--- |
| **HTTP(S) + Global** | **Global External Application LB** | Anycast IP, CDN, WAF (Armor), Cross-region failover. |
| **HTTP(S) + Regional** | **Regional External Application LB** | Data residency compliance (traffic stays in region). |
| **TCP/UDP + Global** | **Global External Proxy Network LB** | TCP with SSL offload, Anycast IP. |
| **TCP/UDP + Regional** | **Regional External Proxy Network LB** | TCP/UDP, Proxy-based. |
| **Preserve Client IP** | **External Passthrough Network LB** | L4, Regional, DSR (Direct Server Return), supports UDP/ESP/ICMP. |
| **Internal HTTP(S)** | **Internal Application LB** | L7, Envoy-based, Regional (but accessible globally via Global Access). |
| **Internal TCP/UDP** | **Internal Passthrough Network LB** | L4, Andromeda-based, Low latency. |

### 1.2 Key Differentiators
*   **Proxy vs. Passthrough**:
    *   **Proxy (ALB, Proxy NLB)**: Terminates connection. Client IP is lost (seen in `X-Forwarded-For`).
    *   **Passthrough (Passthrough NLB)**: Preserves Client IP. Backend sees the original source IP.
*   **Global vs. Regional**:
    *   **Global**: Single IP worldwide. Traffic enters Google network at closest PoP (Premium Tier).
    *   **Regional**: IP is specific to a region. Good for compliance/sovereignty.

## 2. Advanced Load Balancing Features

### 2.1 Session Affinity (Sticky Sessions)
*   **Client IP Affinity**: Best effort. Breaks if client IP changes (e.g., mobile networks). Supported by Network LBs.
*   **Generated Cookie Affinity**: LB sets a cookie (`GCLB`). Supported by HTTP(S) LB.
*   **Header Field Affinity**: Routes based on specific HTTP header.

### 2.2 Container-Native Load Balancing
*   **Network Endpoint Groups (NEGs)**:
    *   LB sends traffic directly to **Pod IPs** (bypassing NodePort/Kube-Proxy).
    *   **Benefits**: Lower latency, better visibility, native Pod health checks.
    *   **Requirement**: VPC-native GKE cluster.

### 2.3 Capacity Management
*   **Balancing Mode**:
    *   **UTILIZATION**: CPU utilization of backend.
    *   **RATE**: Requests per second (RPS) per instance.
*   **Capacity Scaler**: Can temporarily reduce traffic to a backend service (e.g., set to `0` for maintenance) without removing instances.

## 3. Cloud CDN (Content Delivery Network)

Accelerates content delivery by caching at Google's edge.

*   **Integration**: Works *only* with **Global External Application LB**.
*   **Cache Keys**: By default, includes Protocol, Host, and Path. Can be customized to include/exclude query parameters.
*   **Security**:
    *   **Signed URLs/Cookies**: Restrict access to paid/private content.
    *   **Cache Invalidation**: Manually purge content (expensive/rate-limited).

## 4. Cloud Armor (Web Application Firewall)

Protects applications at the edge (before traffic hits the backend).

*   **Targets**: Global External Application LB, External Proxy NLB.
*   **Capabilities**:
    *   **IP Allow/Deny Lists**: Block specific CIDRs or countries (Geo-blocking).
    *   **Preconfigured Rules**: OWASP Top 10 (SQLi, XSS, LFI).
    *   **Rate Limiting**: Throttle requests from a single IP (prevent brute force).
    *   **Adaptive Protection**: ML-based detection of anomalies (DDoS).

## 5. Autoscaling Architectures

### 5.1 Scaling Policies
*   **CPU Utilization**: Scale out when CPU > 60%.
*   **Load Balancing Capacity**: Scale out when RPS > 100.
*   **Custom Metrics**: Scale based on Stackdriver metric (e.g., Queue Depth).
*   **Schedules**: Scale out proactively before a known event (e.g., 9 AM login spike).

### 5.2 Predictive Autoscaling
*   Uses machine learning to forecast demand based on history.
*   Scales out *ahead* of the load.
*   Best for predictable daily/weekly patterns.

### 5.3 Cool-down Period
*   Time to wait after a scale-out event before collecting metrics again.
*   Prevents "flapping" (rapid scale out/in).
*   Should match the application startup time.
