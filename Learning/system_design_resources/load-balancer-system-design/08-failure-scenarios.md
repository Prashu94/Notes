# 08 — Failure Scenarios

---

## Failure Scenario 1: Single Backend Server Goes Down

**Trigger:** A backend web server crashes (OOM, hardware fault, kernel panic) or becomes unresponsive.

### Detection

| Method | Detection Time | Trigger |
|--------|--------------|---------|
| Active health check | ≤ 15 seconds | 3 consecutive failures × 5s interval |
| Passive (Envoy outlier detection) | < 3 seconds | 3 consecutive 5xx or connection refused errors from real traffic |

The passive path is faster and takes effect within seconds of the first failure on a loaded backend.

### Impact

- New requests: continue being routed (Envoy outlier detection ejects backend from cluster within seconds)
- In-flight requests to the failed backend: receive TCP RST or TCP timeout → client gets 502/504
- Requests per second absorbed by remaining healthy backends

### Mitigation

```
T+0s:   Backend starts failing
T+1s:   Envoy passive detection: 3 consecutive 5xx → mark backend EJECTED (local)
T+5s:   Active health check probe #1 fails
T+10s:  Active health check probe #2 fails
T+15s:  Active health check probe #3 fails → status=UNHEALTHY in Redis
T+15s:  Pub/Sub health-events emits BACKEND_DOWN event
T+15s:  All LB nodes read updated Redis health state → stop routing
T+15s:  PagerDuty alert fired via Cloud Monitoring
```

### Prevention

- **Redundancy:** Minimum 3 backends per pool; LB never routes more than `max_connections` per backend
- **Circuit breaker:** Prevents cascading by opening circuit when error rate > 50%
- **Connection draining:** Graceful removal drains connections before backend is removed

### RTO / RPO

| | Value |
|-|-------|
| **RTO** | < 15 seconds (no manual intervention required) |
| **RPO** | 0 (LB has no data; only routes requests) |

---

## Failure Scenario 2: Redis (Memorystore) Unavailable

**Trigger:** Redis instance fails (node failure, network partition, maintenance).

### Detection

- LB nodes detect Redis connection errors within 100ms (connection timeout)
- Cloud Monitoring alert: Redis connection error rate > 1% → PagerDuty

### Impact

| Feature | Impact without Redis |
|---------|---------------------|
| Session affinity (cookie) | Broken — sessions may be routed to wrong backend |
| Rate limiting | **Disabled** — requests pass through without rate checks |
| Least connections (exact) | Falls back to round robin (local connection count used) |
| Circuit breaker state | Falls back to last in-process cached state |
| Health state | Falls back to last in-memory health snapshot (up to 10s stale) |

### Mitigation

```
1. LB nodes switch to degraded mode:
   - Session affinity: fallback to IP hash (deterministic, no Redis)
   - Rate limiting: log warning, allow all traffic (fail-open)
   - LB algorithm: use local connection count approximation

2. Config Manager publishes REDIS_DEGRADED event to all nodes

3. Memorystore HA setup (primary + read replica) auto-promotes replica in < 60 seconds
   (Memorystore Standard Tier with HA: < 30s failover)

4. After Redis recovery: session state is lost — sessions rebuild naturally over TTL
```

### Prevention

- **Memorystore Standard Tier with HA** (automatic failover < 30s)
- **Redis Sentinel / Cluster** for additional redundancy
- **Graceful degradation:** Rate limiting fail-open (availability > strict enforcement)
- **Local rate limit fallback:** Per-LB-node token bucket (less accurate, avoids 0% rate limiting)

### RTO / RPO

| | Value |
|-|-------|
| **RTO** | < 30 seconds (HA auto-failover) |
| **RPO** | Session mappings within last 30s (best effort; sessions re-pinned after reconnect) |

---

## Failure Scenario 3: LB Node Crashes

**Trigger:** An Envoy node crashes (OOM, bug, kernel panic) or is evicted from GKE.

### Detection

- GCP Internal LB health check detects unhealthy LB node within 5 seconds
- GKE auto-replaces pod within 30 seconds
- Cloud Monitoring: unhealthy backend count on internal LB → alert

### Impact

- Active connections on that node: terminated (TCP RST to clients)
- New connections: immediately rerouted to remaining 19 nodes
- Capacity: 5% reduction per node crash (1/20 nodes); 19 nodes handle 1M RPS with headroom

### Mitigation

```
T+0s:   LB node crash
T+5s:   Internal GCP LB detects unhealthy backend → stops routing to it
T+5s:   Remaining 19 nodes absorb the load
T+30s:  GKE restarts the pod on a healthy host
T+60s:  New pod passes startup health check
T+65s:  Internal GCP LB adds pod back to rotation
T+65s:  Full capacity restored
```

### Prevention

- **GKE Pod Disruption Budget (PDB):** At most 2 LB pods down simultaneously
- **Pod anti-affinity:** LB pods spread across availability zones (no two pods on same VM)
- **HPA (Horizontal Pod Autoscaler):** Scale up if avg CPU > 70%
- **Memory limits:** `OOMKilled` restarts quickly vs. gradual slowdown

### RTO / RPO

| | Value |
|-|-------|
| **RTO** | < 5 seconds (routing around failed node) + 65s for full restore |
| **RPO** | 0 (no data stored on LB nodes; Redis holds state) |

---

## Failure Scenario 4: Entire Regional Cluster Failure (US Region Down)

**Trigger:** GCP us-central1 regional outage, VPC issue, or all LB nodes crash simultaneously.

### Detection

- GCP Global HTTPS LB health checks detect US backend group unhealthy within 30 seconds
- Cloud Monitoring: 500-error rate spike → P0 alert → PagerDuty

### Impact

- US users: experience errors for up to 30 seconds during detection
- Global throughput: EU region must absorb 100% of traffic (previously ~40%)
- EU region capacity: 20 nodes × 100K RPS = 2M RPS headroom (current 1M RPS fits)

### Mitigation

```
T+0s:    US region becomes unavailable
T+30s:   GCP GCLB detects US backend group unhealthy (≥2 consecutive checks fail)
T+30s:   GCLB automatically routes all traffic to EU backend group
T+30s:   EU LB nodes: CPU jumps from ~40% to ~80% (still within capacity)
T+35s:   GKE HPA in EU triggers scale-out (target CPU 70% exceeded)
T+5min:  EU scaled to 40 nodes, CPU back to ~40%

Recovery (US region comes back):
T+0s:   US region healthy
T+5min: GCP GCLB detects US backend group healthy (2 consecutive successes)
T+5min: GCLB gradually shifts traffic back to US (canary percentage)
T+15min: Normal geo-distribution restored
```

### Prevention

- **Multi-region active-active:** Both US and EU always serving traffic (not active-standby)
- **Capacity headroom:** Each region sized for 100% of peak traffic (not 60%/40%)
- **Zero-downtime deployments:** Blue-green per region to avoid self-inflicted outages
- **Chaos engineering:** Regular regional failover drills

### RTO / RPO

| | Value |
|-|-------|
| **RTO** | < 30 seconds (GCLB auto-fails over) |
| **RPO** | 0 (no persistent data in LB nodes) |

---

## Failure Scenario 5: Config Manager Unavailable

**Trigger:** Config Manager pods all crash; no xDS updates can be pushed to Envoy nodes.

### Detection

- Envoy ADS stream disconnects (all nodes detect within 10 seconds)
- Cloud Monitoring: xDS stream errors → alert

### Impact

- **Existing traffic:** Unaffected. Envoy continues with last-known-good config.
- **Config changes:** Blocked. New backend additions, pool changes don't take effect.
- **Health state:** Envoy continues with stale health snapshot + its own passive outlier detection.

### Mitigation

```
T+0s:   Config Manager pods crash
T+10s:  Envoy nodes detect ADS stream disconnect
T+10s:  Envoy holds last-known-good config in memory
T+30s:  GKE restarts Config Manager pods
T+60s:  Config Manager reconnects to Cloud SQL + Redis
T+90s:  Config Manager pushes full xDS snapshot to all reconnecting Envoy nodes
T+90s:  All nodes updated to latest config
```

Config Manager shutdown is a **"fail open"** scenario — the system remains operational without it, just config-frozen.

### Prevention

- **Multi-replica Config Manager:** 3 replicas with leader election (via Kubernetes lease)
- **Health check on ADS stream:** LB nodes alert if no config update in 120s

### RTO / RPO

| | Value |
|-|-------|
| **RTO** | < 90 seconds (config resync after recovery) |
| **RPO** | Config changes queued in Pub/Sub; applied after recovery |

---

## Failure Scenario 6: SSL Certificate Expiry / Rotation Failure

**Trigger:** TLS certificate approaches expiry; auto-renewal fails silently.

### Detection

- Certificate Manager (GCP) monitors expiry; auto-renews 30 days before expiry
- Cloud Monitoring custom alert: cert expiry < 14 days → warning; < 7 days → P1 alert
- LB nodes log SSL handshake failures if expired cert is served

### Impact

- All HTTPS clients get `ERR_CERT_DATE_INVALID`
- Complete service outage for browser clients if cert expires

### Mitigation

```
Prevention workflow:
  Day -30: Certificate Manager triggers auto-renewal
  Day -14: Cloud Monitoring P2 alert if not renewed
  Day -7:  P1 alert + manual intervention required
  Day 0:   Certificate Manager replaces cert; pushes to Secret Manager
  Day 0:   LB nodes pick up new TLS context via Secret Manager watch (< 30s)
  
Emergency manual rotation:
  1. Upload new certificate to Certificate Manager
  2. Certificate Manager updates Secret Manager version
  3. Config Manager detects new secret version → pushes updated TLS config via xDS
  4. Envoy hot-reloads TLS context (no connection drops)
```

### Prevention

- **GCP Certificate Manager:** Fully managed auto-renewal (eliminates manual process)
- **Multi-level alerting:** 30-day, 14-day, 7-day alerts
- **Cert pinning avoided:** Allows seamless rotation
- **OCSP stapling:** Hides revocation latency during emergency rotation

### RTO / RPO

| | Value |
|-|-------|
| **RTO** | < 5 minutes (emergency rotation) |
| **RPO** | N/A (no data loss; TLS is stateless) |

---

## Failure Scenario 7: DDoS Attack (Volumetric)

**Trigger:** Attacker sends 10M+ RPS of garbage traffic to the LB's Anycast IP.

### Detection

- Cloud Armor: Rate of new connections per source IP spikes
- Cloud Monitoring: Bytes per second on GCLB exceeds 98th percentile → immediate alert
- Cloud Armor Adaptive Protection: ML-based L7 DDoS detection within 60 seconds

### Impact

- Without mitigation: $100K+ in egress costs; legitimate traffic dropped (LB saturated)
- With Cloud Armor: Malicious traffic blocked at GCP PoP (never reaches LB nodes)

### Mitigation

```
Cloud Armor adaptive protection (automatic):
  T+0s:   Attack begins
  T+60s:  Cloud Armor Adaptive Protection detects anomaly, issues auto-rule recommendation
  T+120s: Operator approves rule (or auto-approve if confidence > 95%)
  T+120s: Cloud Armor blocks attacking IPs at edge (GCP PoP level)
  
Manual rules already in place:
  - Max 10,000 RPS per source IP (Cloud Armor WAF rule)
  - Geographic blocking of unexpected source regions
  - Rate limit: 1,000 RPS per /24 CIDR block
  - HTTP flood protection (slowloris, fragmented requests)
```

### Prevention

- **Cloud Armor Standard** always-on: OWASP Top 10 rules, IP reputation lists
- **Cloud Armor Enterprise**: Adaptive Protection (ML-based) + DDoS response team
- **Anycast advantage:** Attack traffic is absorbed across ALL GCP PoPs globally
- **Rate limiting at LB:** Even traffic that reaches LB nodes is rate-limited per IP

### RTO / RPO

| | Value |
|-|-------|
| **RTO** | < 2 minutes (Cloud Armor adaptive rule activation) |
| **RPO** | 0 |

---

## Failure Summary Matrix

| Scenario | Detection Time | Failover Time | Impact Severity | Automated Recovery |
|---------|--------------|--------------|----------------|--------------------|
| Single backend crash | < 15s | < 15s | Low (1 of N backends) | ✅ Yes |
| Redis unavailable | < 1s | < 30s (HA failover) | Medium (degraded sessions/rate limits) | ✅ Yes |
| LB node crash | < 5s | < 5s | Low (1 of 20 nodes) | ✅ Yes |
| Regional outage | < 30s | < 30s | High (all regional traffic) | ✅ Yes |
| Config Manager down | < 10s | Stale config (functional) | None to traffic | ✅ Yes (graceful) |
| SSL cert expiry | Day -30 warning | < 5min manual | Critical (if expired) | ✅ Yes (auto-renew) |
| DDoS attack | < 60s | < 120s | Medium → Low with Cloud Armor | ✅ Partial (human approval) |
