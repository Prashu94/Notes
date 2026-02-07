# Google Cloud Armor - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Cloud Armor Architecture](#cloud-armor-architecture)
3. [Security Policies](#security-policies)
4. [WAF Rules](#waf-rules)
5. [DDoS Protection](#ddos-protection)
6. [Rate Limiting](#rate-limiting)
7. [Bot Management](#bot-management)
8. [Adaptive Protection](#adaptive-protection)
9. [Edge Security Policies](#edge-security-policies)
10. [Integration with Load Balancers](#integration-with-load-balancers)
11. [Logging and Monitoring](#logging-and-monitoring)
12. [Best Practices](#best-practices)
13. [ACE Exam Focus](#ace-exam-focus)
14. [PCA Exam Focus](#pca-exam-focus)

---

## Overview

### What is Cloud Armor?

Google Cloud Armor is a distributed denial-of-service (DDoS) defense and web application firewall (WAF) service that protects your applications and services from attacks. It works with HTTP(S) Load Balancing to provide defense at the edge of Google's network.

**Key Features:**
- **DDoS Protection**: Volumetric and protocol attacks
- **WAF**: OWASP Top 10 protection
- **Rate Limiting**: Control request rates
- **Bot Management**: reCAPTCHA Enterprise integration
- **Adaptive Protection**: ML-based attack detection
- **IP/Geo Blocking**: Allowlist and denylist by IP or region
- **Named IP Lists**: Google-managed threat intelligence lists

### Cloud Armor Tiers

| Tier | Features | Use Case |
|------|----------|----------|
| **Standard** | Basic WAF rules, IP blocking, rate limiting | Basic protection |
| **Managed Protection Plus** | Adaptive Protection, advanced WAF, DDoS response team | Enterprise protection |

### Supported Load Balancers

Cloud Armor works with:
- **Global External HTTP(S) Load Balancer** (Classic and new)
- **Global External HTTP(S) Load Balancer (Classic)**
- **External TCP/UDP Network Load Balancer** (limited)
- **Cloud CDN**

---

## Cloud Armor Architecture

### Traffic Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLOUD ARMOR ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐                                                       │
│   │   Client    │                                                       │
│   │   Request   │                                                       │
│   └──────┬──────┘                                                       │
│          │                                                               │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │                    GOOGLE'S EDGE NETWORK                     │      │
│   │  ┌─────────────────────────────────────────────────────┐    │      │
│   │  │                 CLOUD ARMOR                          │    │      │
│   │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │    │      │
│   │  │  │  DDoS   │  │   WAF   │  │  Rate   │            │    │      │
│   │  │  │ Defense │  │  Rules  │  │ Limiting│            │    │      │
│   │  │  └────┬────┘  └────┬────┘  └────┬────┘            │    │      │
│   │  │       └────────────┼────────────┘                  │    │      │
│   │  └───────────────────┬┴──────────────────────────────┘    │      │
│   │                      │                                      │      │
│   │  ┌───────────────────▼──────────────────────────────┐      │      │
│   │  │            HTTP(S) LOAD BALANCER                  │      │      │
│   │  └───────────────────┬──────────────────────────────┘      │      │
│   └──────────────────────┼──────────────────────────────────────┘      │
│                          │                                               │
│          ┌───────────────┼───────────────┐                              │
│          │               │               │                              │
│          ▼               ▼               ▼                              │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐                          │
│   │ Backend  │   │ Backend  │   │ Backend  │                          │
│   │ Service 1│   │ Service 2│   │ Bucket   │                          │
│   └──────────┘   └──────────┘   └──────────┘                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Security Policy** | Container for rules attached to backend services |
| **Rules** | Individual allow/deny conditions with priorities |
| **Match Conditions** | IP ranges, regions, expressions |
| **Actions** | Allow, deny, rate-limit, redirect, throttle |

---

## Security Policies

### Creating Security Policies

```bash
# Create a security policy
gcloud compute security-policies create my-security-policy \
    --description="Production security policy"

# List security policies
gcloud compute security-policies list

# Describe a policy
gcloud compute security-policies describe my-security-policy
```

### Attaching Policies to Backend Services

```bash
# Attach policy to backend service
gcloud compute backend-services update my-backend-service \
    --security-policy=my-security-policy \
    --global

# Remove policy from backend service
gcloud compute backend-services update my-backend-service \
    --security-policy="" \
    --global
```

### Policy Types

#### Backend Security Policies
Applied to backend services:

```bash
# Create backend policy
gcloud compute security-policies create backend-policy \
    --type=CLOUD_ARMOR

# Attach to backend
gcloud compute backend-services update web-backend \
    --security-policy=backend-policy \
    --global
```

#### Edge Security Policies
Applied at Google's edge for Cloud CDN:

```bash
# Create edge policy
gcloud compute security-policies create edge-policy \
    --type=CLOUD_ARMOR_EDGE

# Attach to backend bucket
gcloud compute backend-buckets update cdn-bucket \
    --edge-security-policy=edge-policy
```

---

## WAF Rules

### Rule Structure

```bash
# Add a rule to security policy
gcloud compute security-policies rules create PRIORITY \
    --security-policy=POLICY_NAME \
    --expression="EXPRESSION" \
    --action="ACTION" \
    --description="DESCRIPTION"
```

**Priority**: Lower numbers = higher priority (evaluated first)
- 0-999: Custom rules
- 2147483647: Default rule

### IP-Based Rules

```bash
# Block specific IP addresses
gcloud compute security-policies rules create 1000 \
    --security-policy=my-policy \
    --src-ip-ranges="192.0.2.0/24,198.51.100.0/24" \
    --action=deny-403 \
    --description="Block malicious IPs"

# Allow only specific IPs (allowlist)
gcloud compute security-policies rules create 1000 \
    --security-policy=my-policy \
    --src-ip-ranges="203.0.113.0/24" \
    --action=allow \
    --description="Allow corporate network"

# Block all others (deny by default)
gcloud compute security-policies rules update 2147483647 \
    --security-policy=my-policy \
    --action=deny-403
```

### Geo-Based Rules

```bash
# Block traffic from specific countries
gcloud compute security-policies rules create 2000 \
    --security-policy=my-policy \
    --expression="origin.region_code == 'CN' || origin.region_code == 'RU'" \
    --action=deny-403 \
    --description="Block traffic from China and Russia"

# Allow only specific regions
gcloud compute security-policies rules create 2000 \
    --security-policy=my-policy \
    --expression="origin.region_code == 'US' || origin.region_code == 'CA'" \
    --action=allow \
    --description="Allow North American traffic only"
```

### Custom Expression Rules (CEL)

Cloud Armor uses Common Expression Language (CEL) for custom rules:

```bash
# Block requests with specific headers
gcloud compute security-policies rules create 3000 \
    --security-policy=my-policy \
    --expression="request.headers['user-agent'].contains('BadBot')" \
    --action=deny-403

# Block large request bodies
gcloud compute security-policies rules create 3001 \
    --security-policy=my-policy \
    --expression="int(request.headers['content-length']) > 10000000" \
    --action=deny-413

# Block specific paths
gcloud compute security-policies rules create 3002 \
    --security-policy=my-policy \
    --expression="request.path.matches('/admin/.*')" \
    --action=deny-403

# Complex condition
gcloud compute security-policies rules create 3003 \
    --security-policy=my-policy \
    --expression="request.method == 'POST' && !request.path.startsWith('/api/')" \
    --action=deny-403
```

### Pre-configured WAF Rules (OWASP)

```bash
# Enable SQL injection protection
gcloud compute security-policies rules create 4000 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('sqli-stable')" \
    --action=deny-403 \
    --description="SQL injection protection"

# Enable XSS protection
gcloud compute security-policies rules create 4001 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('xss-stable')" \
    --action=deny-403 \
    --description="Cross-site scripting protection"

# Enable Local File Inclusion protection
gcloud compute security-policies rules create 4002 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('lfi-stable')" \
    --action=deny-403 \
    --description="Local file inclusion protection"

# Enable Remote File Inclusion protection
gcloud compute security-policies rules create 4003 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('rfi-stable')" \
    --action=deny-403 \
    --description="Remote file inclusion protection"

# Enable Remote Code Execution protection
gcloud compute security-policies rules create 4004 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('rce-stable')" \
    --action=deny-403 \
    --description="Remote code execution protection"

# Enable protocol attack protection
gcloud compute security-policies rules create 4005 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('protocolattack-stable')" \
    --action=deny-403

# Enable session fixation protection
gcloud compute security-policies rules create 4006 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('sessionfixation-stable')" \
    --action=deny-403

# Enable scanner detection
gcloud compute security-policies rules create 4007 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('scannerdetection-stable')" \
    --action=deny-403
```

### Available Pre-configured Rules

| Rule Set | Description |
|----------|-------------|
| `sqli-stable` / `sqli-canary` | SQL Injection |
| `xss-stable` / `xss-canary` | Cross-Site Scripting |
| `lfi-stable` / `lfi-canary` | Local File Inclusion |
| `rfi-stable` / `rfi-canary` | Remote File Inclusion |
| `rce-stable` / `rce-canary` | Remote Code Execution |
| `methodenforcement-stable` | Method Enforcement |
| `scannerdetection-stable` | Scanner Detection |
| `protocolattack-stable` | Protocol Attacks |
| `php-stable` | PHP Injection |
| `sessionfixation-stable` | Session Fixation |
| `cve-canary` | Known CVE exploits |

---

## DDoS Protection

### Built-in Protection

Cloud Armor provides always-on DDoS protection for:
- **Layer 3/4 attacks**: Volumetric attacks (UDP floods, SYN floods)
- **Layer 7 attacks**: Application-layer attacks (HTTP floods)

```bash
# DDoS protection is automatic with HTTP(S) Load Balancer
# No additional configuration required for basic protection

# View DDoS mitigation events
gcloud logging read 'resource.type="http_load_balancer" AND jsonPayload.@type="type.googleapis.com/google.cloud.loadbalancing.type.LoadBalancerLogEntry"' \
    --limit=100
```

### Advanced DDoS Protection (Managed Protection Plus)

```bash
# Enable Managed Protection Plus (requires subscription)
gcloud compute security-policies update my-policy \
    --enable-layer7-ddos-defense

# Configure adaptive protection
gcloud compute security-policies update my-policy \
    --layer7-ddos-defense-rule-visibility=STANDARD
```

### Network DDoS Protection

For TCP/UDP Network Load Balancers:

```bash
# Enable network edge security policy
gcloud compute security-policies create network-edge-policy \
    --type=CLOUD_ARMOR_NETWORK

# Attach to forwarding rule
gcloud compute forwarding-rules update my-forwarding-rule \
    --network-edge-security-policy=network-edge-policy
```

---

## Rate Limiting

### Throttle-Based Rate Limiting

```bash
# Create rate limiting rule
gcloud compute security-policies rules create 5000 \
    --security-policy=my-policy \
    --expression="true" \
    --action=throttle \
    --rate-limit-threshold-count=100 \
    --rate-limit-threshold-interval-sec=60 \
    --conform-action=allow \
    --exceed-action=deny-429 \
    --enforce-on-key=IP \
    --description="Rate limit: 100 requests per minute per IP"
```

### Rate Limit by Different Keys

```bash
# Rate limit by IP
--enforce-on-key=IP

# Rate limit by all traffic
--enforce-on-key=ALL

# Rate limit by HTTP header
--enforce-on-key=HTTP-HEADER \
--enforce-on-key-name=X-API-Key

# Rate limit by XFF IP (behind proxy)
--enforce-on-key=XFF-IP

# Rate limit by HTTP cookie
--enforce-on-key=HTTP-COOKIE \
--enforce-on-key-name=session_id

# Rate limit by SNI
--enforce-on-key=SNI
```

### Advanced Rate Limiting Examples

```bash
# Rate limit API endpoints
gcloud compute security-policies rules create 5001 \
    --security-policy=my-policy \
    --expression="request.path.startsWith('/api/')" \
    --action=rate-based-ban \
    --rate-limit-threshold-count=1000 \
    --rate-limit-threshold-interval-sec=60 \
    --ban-duration-sec=600 \
    --conform-action=allow \
    --exceed-action=deny-429 \
    --enforce-on-key=IP \
    --description="API rate limit with 10-min ban"

# Different limits for different paths
gcloud compute security-policies rules create 5002 \
    --security-policy=my-policy \
    --expression="request.path.startsWith('/login')" \
    --action=throttle \
    --rate-limit-threshold-count=10 \
    --rate-limit-threshold-interval-sec=60 \
    --conform-action=allow \
    --exceed-action=deny-429 \
    --enforce-on-key=IP \
    --description="Login rate limit: 10/minute"
```

### Rate Limiting Actions

| Action | Description |
|--------|-------------|
| `throttle` | Limit requests but don't ban |
| `rate-based-ban` | Ban IP after exceeding threshold |

---

## Bot Management

### reCAPTCHA Enterprise Integration

```bash
# Create security policy with reCAPTCHA
gcloud compute security-policies create bot-policy \
    --recaptcha-redirect-site-key=SITE_KEY

# Add reCAPTCHA rule
gcloud compute security-policies rules create 6000 \
    --security-policy=bot-policy \
    --expression="request.path.matches('/sensitive/.*')" \
    --action=redirect \
    --redirect-type=GOOGLE_RECAPTCHA \
    --description="Challenge bots on sensitive paths"
```

### Bot Detection Rules

```bash
# Block known bad bots
gcloud compute security-policies rules create 6001 \
    --security-policy=my-policy \
    --expression="request.headers['user-agent'].contains('BadBot') || request.headers['user-agent'].contains('Scanner')" \
    --action=deny-403

# Challenge suspicious requests
gcloud compute security-policies rules create 6002 \
    --security-policy=bot-policy \
    --expression="!has(request.headers['accept-language'])" \
    --action=redirect \
    --redirect-type=GOOGLE_RECAPTCHA
```

---

## Adaptive Protection

### Overview

Adaptive Protection uses machine learning to detect and mitigate application-layer (L7) DDoS attacks.

**Features:**
- Automatic attack detection
- Attack signatures
- Suggested rules
- Alert integration

### Enabling Adaptive Protection

```bash
# Enable adaptive protection
gcloud compute security-policies update my-policy \
    --enable-layer7-ddos-defense

# Set alerting mode (STANDARD or VERBOSE)
gcloud compute security-policies update my-policy \
    --layer7-ddos-defense-rule-visibility=STANDARD
```

### Responding to Alerts

```python
# Example: Automatically apply suggested rules from Adaptive Protection
from google.cloud import compute_v1

def apply_adaptive_protection_rule(project, policy_name, alert):
    """Apply suggested rule from Adaptive Protection alert."""
    client = compute_v1.SecurityPoliciesClient()
    
    rule = compute_v1.SecurityPolicyRule()
    rule.priority = 10000  # High priority
    rule.match = compute_v1.SecurityPolicyRuleMatcher()
    rule.match.expr = compute_v1.Expr()
    rule.match.expr.expression = alert.suggested_rule_expression
    rule.action = "deny(403)"
    rule.description = f"Adaptive Protection: {alert.attack_type}"
    
    client.add_rule(
        project=project,
        security_policy=policy_name,
        security_policy_rule_resource=rule
    )
```

---

## Edge Security Policies

### For Cloud CDN

Edge security policies filter traffic before it reaches Cloud CDN caches:

```bash
# Create edge security policy
gcloud compute security-policies create cdn-edge-policy \
    --type=CLOUD_ARMOR_EDGE \
    --description="Edge policy for CDN"

# Add rules
gcloud compute security-policies rules create 1000 \
    --security-policy=cdn-edge-policy \
    --src-ip-ranges="192.0.2.0/24" \
    --action=deny-403

# Attach to backend bucket
gcloud compute backend-buckets update my-cdn-bucket \
    --edge-security-policy=cdn-edge-policy

# Attach to backend service (with CDN enabled)
gcloud compute backend-services update my-cdn-service \
    --edge-security-policy=cdn-edge-policy \
    --global
```

### Differences from Backend Policies

| Feature | Backend Policy | Edge Policy |
|---------|----------------|-------------|
| **Evaluation Point** | After CDN cache | Before CDN cache |
| **WAF Rules** | Full support | Limited |
| **Rate Limiting** | Supported | Limited |
| **Use Case** | Origin protection | Cache protection |

---

## Integration with Load Balancers

### External HTTP(S) Load Balancer

```bash
# Create load balancer infrastructure
# 1. Create backend service
gcloud compute backend-services create web-backend \
    --protocol=HTTP \
    --port-name=http \
    --health-checks=http-health-check \
    --global

# 2. Create security policy
gcloud compute security-policies create web-policy

# 3. Attach policy to backend
gcloud compute backend-services update web-backend \
    --security-policy=web-policy \
    --global

# 4. Create URL map
gcloud compute url-maps create web-map \
    --default-service=web-backend

# 5. Create target proxy
gcloud compute target-http-proxies create web-proxy \
    --url-map=web-map

# 6. Create forwarding rule
gcloud compute forwarding-rules create web-rule \
    --global \
    --target-http-proxy=web-proxy \
    --ports=80
```

### Per-Backend Policies

Different backends can have different policies:

```bash
# API backend with strict rules
gcloud compute backend-services update api-backend \
    --security-policy=strict-api-policy \
    --global

# Static content with basic rules
gcloud compute backend-services update static-backend \
    --security-policy=basic-policy \
    --global
```

---

## Logging and Monitoring

### Cloud Armor Logging

```bash
# Enable verbose logging
gcloud compute security-policies update my-policy \
    --log-level=VERBOSE

# Log levels:
# - NORMAL: Blocked requests only
# - VERBOSE: All requests
```

### Log Query Examples

```bash
# View all blocked requests
gcloud logging read '
  resource.type="http_load_balancer"
  jsonPayload.enforcedSecurityPolicy.outcome="DENY"
' --limit=100

# View requests blocked by specific rule
gcloud logging read '
  resource.type="http_load_balancer"
  jsonPayload.enforcedSecurityPolicy.matchedRuleName="my-rule"
  jsonPayload.enforcedSecurityPolicy.outcome="DENY"
' --limit=100

# View rate limited requests
gcloud logging read '
  resource.type="http_load_balancer"
  jsonPayload.enforcedSecurityPolicy.outcome="THROTTLE"
' --limit=100

# View Adaptive Protection events
gcloud logging read '
  resource.type="security_policy"
  jsonPayload.adaptiveProtection.autoDeployAlertId!=""
' --limit=100
```

### Monitoring Metrics

```bash
# Create alerting policy for blocked requests
gcloud alpha monitoring policies create \
    --display-name="High Block Rate Alert" \
    --condition-display-name="Block rate > 1000/min" \
    --condition-filter='
      resource.type="https_lb_rule"
      metric.type="loadbalancing.googleapis.com/https/request_count"
      metric.labels.response_code_class="400"
    ' \
    --duration="60s" \
    --comparison="COMPARISON_GT" \
    --threshold-value="1000"
```

### Key Metrics

| Metric | Description |
|--------|-------------|
| `request_count` | Total requests processed |
| `backend_request_count` | Requests reaching backends |
| `request_bytes_count` | Request size |
| `response_bytes_count` | Response size |
| `total_latencies` | Request latency |

---

## Best Practices

### Security Policy Design

1. **Default Deny** (for sensitive applications):
```bash
# Set default rule to deny
gcloud compute security-policies rules update 2147483647 \
    --security-policy=my-policy \
    --action=deny-403

# Then add allow rules for legitimate traffic
gcloud compute security-policies rules create 1000 \
    --security-policy=my-policy \
    --src-ip-ranges="KNOWN_GOOD_IPS" \
    --action=allow
```

2. **Defense in Depth**:
```bash
# Layer 1: IP allowlist/denylist
gcloud compute security-policies rules create 1000 \
    --security-policy=my-policy \
    --src-ip-ranges="BLOCKED_IPS" \
    --action=deny-403

# Layer 2: Geo-blocking
gcloud compute security-policies rules create 2000 \
    --security-policy=my-policy \
    --expression="origin.region_code != 'US'" \
    --action=deny-403

# Layer 3: WAF rules
gcloud compute security-policies rules create 3000 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('sqli-stable')" \
    --action=deny-403

# Layer 4: Rate limiting
gcloud compute security-policies rules create 4000 \
    --security-policy=my-policy \
    --expression="true" \
    --action=throttle \
    --rate-limit-threshold-count=1000 \
    --rate-limit-threshold-interval-sec=60 \
    --conform-action=allow \
    --exceed-action=deny-429 \
    --enforce-on-key=IP
```

3. **Use Named IP Lists**:
```bash
# Block known malicious IPs (Google-managed list)
gcloud compute security-policies rules create 500 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('sourceiplist-fastly')" \
    --action=allow

# Create custom named IP list
gcloud compute security-policies add-user-defined-field my-policy \
    --user-defined-field-name="blocked-ips" \
    --base=SRC_IPS_V1
```

### Testing Security Policies

```bash
# Preview mode - log but don't enforce
gcloud compute security-policies rules create 9999 \
    --security-policy=my-policy \
    --expression="evaluatePreconfiguredExpr('sqli-stable')" \
    --action=deny-403 \
    --preview  # Enable preview mode

# Check logs for what would be blocked
gcloud logging read '
  resource.type="http_load_balancer"
  jsonPayload.enforcedSecurityPolicy.preview="true"
'

# Remove preview mode after testing
gcloud compute security-policies rules update 9999 \
    --security-policy=my-policy \
    --no-preview
```

---

## ACE Exam Focus

### Key Concepts for ACE

1. **Security Policy Basics**: Create and attach policies to backend services
2. **IP Blocking**: Allow/deny by IP ranges
3. **Geo-blocking**: Block by region codes
4. **Pre-configured WAF Rules**: Enable OWASP protection
5. **Basic Rate Limiting**: Configure throttling

### Sample ACE Questions

**Q1:** How do you protect a web application from SQL injection attacks using Cloud Armor?
- **A:** Create a security policy with a pre-configured WAF rule:
  ```bash
  gcloud compute security-policies rules create 1000 \
      --security-policy=my-policy \
      --expression="evaluatePreconfiguredExpr('sqli-stable')" \
      --action=deny-403
  ```

**Q2:** A company wants to allow traffic only from US IP addresses. What Cloud Armor configuration is needed?
- **A:** 
  1. Create a rule allowing US traffic: `origin.region_code == 'US'` → allow
  2. Set default rule to deny-403

**Q3:** Which load balancer types support Cloud Armor?
- **A:** Global External HTTP(S) Load Balancer (required for full Cloud Armor features)

### ACE gcloud Commands

```bash
# Create security policy
gcloud compute security-policies create POLICY_NAME

# Add rule
gcloud compute security-policies rules create PRIORITY \
    --security-policy=POLICY_NAME \
    --src-ip-ranges="IP_RANGES" \
    --action=allow|deny-403|deny-404|deny-502

# Attach to backend
gcloud compute backend-services update BACKEND_NAME \
    --security-policy=POLICY_NAME \
    --global

# List policies
gcloud compute security-policies list

# Describe policy
gcloud compute security-policies describe POLICY_NAME
```

---

## PCA Exam Focus

### Architecture Decision Framework

#### When to Use Cloud Armor

| Scenario | Cloud Armor Feature |
|----------|---------------------|
| DDoS protection | Built-in + Adaptive Protection |
| WAF for OWASP Top 10 | Pre-configured rules |
| Geo-compliance | Region-based rules |
| API rate limiting | Rate limiting rules |
| Bot protection | reCAPTCHA integration |

#### Cloud Armor vs Other Security Solutions

| Solution | Use Case |
|----------|----------|
| **Cloud Armor** | L7 protection at edge |
| **VPC Firewall** | L3/L4 internal traffic |
| **IAP** | Identity-based access |
| **reCAPTCHA** | Bot detection |

### Sample PCA Questions

**Q1:** Design a security architecture for a global e-commerce platform that needs DDoS protection, WAF capabilities, and rate limiting for API endpoints.

**A:**
- **Global LB**: Deploy External HTTP(S) Load Balancer
- **Cloud Armor Policy**:
  - Rule 1: Pre-configured WAF rules (SQLi, XSS, RCE)
  - Rule 2: Geo-blocking for sanctioned regions
  - Rule 3: Rate limiting for `/api/*` paths
  - Rule 4: reCAPTCHA for `/checkout` path
- **Adaptive Protection**: Enable for ML-based attack detection
- **Logging**: Enable verbose logging for security analysis

**Q2:** A financial services company requires 99.99% availability and must protect against sophisticated L7 attacks. What Cloud Armor configuration should they use?

**A:**
- **Managed Protection Plus**: Subscribe for enterprise features
- **Adaptive Protection**: Enable with VERBOSE alerting
- **DDoS Response Team**: Engage for attack support
- **Multi-layer rules**:
  1. Named IP lists for known threats
  2. Custom WAF rules for financial APIs
  3. Strict rate limiting
  4. Default deny policy

**Q3:** How would you protect a CDN-served static website from attacks while minimizing cache miss rates?

**A:**
- **Edge Security Policy**: Apply at CDN edge before cache
- **Rules**:
  - IP blocking for known bad actors
  - Geo-restrictions if applicable
  - Basic rate limiting
- **Why Edge**: Blocks malicious traffic before cache lookup, reducing origin load

### Multi-Region Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GLOBAL SECURITY ARCHITECTURE              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Internet Traffic                                          │
│         │                                                    │
│         ▼                                                    │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              CLOUD ARMOR POLICY                      │  │
│   │   • DDoS Protection (Always on)                     │  │
│   │   • WAF Rules (OWASP Top 10)                       │  │
│   │   • Geo-blocking                                    │  │
│   │   • Rate Limiting                                   │  │
│   │   • Adaptive Protection                            │  │
│   └─────────────────────────────────────────────────────┘  │
│                          │                                   │
│         ┌────────────────┼────────────────┐                │
│         │                │                │                │
│         ▼                ▼                ▼                │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│   │ us-east1 │    │ europe   │    │ asia     │           │
│   │ backends │    │ backends │    │ backends │           │
│   └──────────┘    └──────────┘    └──────────┘           │
│                                                              │
│   Additional Layers:                                        │
│   • VPC Firewall (internal traffic)                        │
│   • IAP (admin access)                                     │
│   • VPC Service Controls (data exfiltration)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

### Cloud Armor Features by Tier

| Feature | Standard | Managed Protection Plus |
|---------|----------|------------------------|
| DDoS Protection | ✅ | ✅ |
| Pre-configured WAF | ✅ | ✅ |
| IP/Geo Rules | ✅ | ✅ |
| Rate Limiting | ✅ | ✅ |
| Custom Rules (CEL) | ✅ | ✅ |
| Edge Policies | ✅ | ✅ |
| Adaptive Protection | ❌ | ✅ |
| Named IP Lists | ❌ | ✅ |
| DDoS Response Team | ❌ | ✅ |
| Advanced WAF | ❌ | ✅ |

### Key Takeaways

| Topic | ACE Focus | PCA Focus |
|-------|-----------|-----------|
| Policy Creation | Basic commands | Architecture decisions |
| WAF Rules | Enable pre-configured | Custom rule design |
| Rate Limiting | Basic throttle | Advanced patterns |
| Adaptive Protection | Awareness | Full implementation |
| Integration | Attach to backend | Multi-layer design |
