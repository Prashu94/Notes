# 07 — Trade-offs

---

## 1. Load Balancing Algorithm Selection

| Dimension | Round Robin | Weighted Round Robin | Least Connections | Consistent Hash |
|-----------|------------|---------------------|-------------------|----------------|
| **Implementation Complexity** | Trivial (counter mod N) | Low (weight array) | Medium (atomic counters in Redis) | High (CH ring with vnodes) |
| **Fairness** | Equal distribution | Proportional to weight | Proportional to capacity | Not uniform (skew possible) |
| **Backend Heterogeneity** | Poor (ignores different capacities) | Good | Best (self-adjusting) | Poor |
| **Latency Sensitivity** | Doesn't account for slow backends | Doesn't account | Naturally avoids slow backends | Doesn't account |
| **Session Affinity** | Not inherent | Not inherent | Not inherent | **Built-in** |
| **Operational Cost** | Zero Redis calls | Zero Redis calls | 2 Redis ops/request | Zero Redis calls |
| **Rebalance on Change** | Immediate, even | Needs reweight | Automatic | ~1/N traffic shifted |
| **Verdict** | Good default for homogeneous pools | Use when backends have different capacities | **Best for variable workloads** | Use when session affinity needed without cookie overhead |

**Decision: Default to Least Connections for dynamic web workloads. Allow per-pool override.**

---

## 2. Centralized vs. Distributed Health Checking

| Dimension | Centralized (one global HC service) | Distributed (each LB node checks all backends) |
|-----------|-------------------------------------|-----------------------------------------------|
| **Probe Volume** | N probes per interval | LB_nodes × N probes per interval |
| **Single Point of Failure** | Yes — HC service failure = stale health data | No — every node checks independently |
| **Consistency** | Strongly consistent (one source of truth) | Eventually consistent (nodes may disagree momentarily) |
| **Network Fan-out** | One source → N backends | Many sources → N backends (thundering herd risk) |
| **Detection Latency** | Higher (one probe per interval) | Lower (multiple confirmations faster) |
| **Complexity** | Low | High (coordination, deduplication) |

**Decision: Centralized health check service (one per region), sharded by backend subset. Passive health detection in Envoy (outlier detection) provides local fast-path failure detection within 1-2 requests.**

---

## 3. Redis for Hot State vs. In-Process Memory

| Dimension | Redis (Memorystore) | In-Process Memory (per node) |
|-----------|--------------------|-----------------------------|
| **Consistency** | Strongly consistent across all LB nodes | Eventually consistent (stale between nodes) |
| **Latency per Request** | +0.1–0.3 ms round-trip | 0 ms (in-process) |
| **Scalability** | Single Redis shard handles ~100K ops/sec | Scales with LB node count |
| **Least Connections accuracy** | Exact across all nodes | Each node only sees its own connections |
| **Session Affinity** | Works across all nodes | Node-local: client must hit same LB node |
| **Operational complexity** | One more dependency | Simpler |
| **Failure Impact** | Redis failure breaks sessions + rate limits | No dependency |

**Decision: Use Redis for session affinity (correctness required across nodes) and rate limiting (global enforcement required). Use in-process counters for Least Connections with Redis as eventual sync (acceptable slight inaccuracy for performance).**

---

## 4. xDS (Dynamic Config) vs. File-Based Config

| Dimension | xDS Control Plane (dynamic) | Static File Config + Reload |
|-----------|---------------------------|----------------------------|
| **Config Change Latency** | < 1 second (streaming push) | 5–30 seconds (reload + health check) |
| **Zero-Downtime Updates** | Yes (incremental delta) | Partial (graceful reload) |
| **Complexity** | High (implement gRPC streaming server) | Low |
| **Failure Risk** | Config manager outage → stale but working config | File system / reload failure possible |
| **Scale** | Handles 10K backends with delta updates | Full reload cost grows with backend count |

**Decision: Use Envoy with xDS (ADS) for production. Complexity is justified at scale. Config Manager failure is handled gracefully — Envoy continues with last-known-good config.**

---

## 5. L4 vs. L7 Load Balancing

| Dimension | L4 (TCP/UDP) | L7 (HTTP/HTTPS) |
|-----------|-------------|----------------|
| **Visibility** | IP + port only | URL, headers, cookies, body |
| **Routing Sophistication** | Simple (hash, RR) | Path-based, host-based, header-based, canary |
| **SSL Termination** | No (pass-through) | Yes |
| **Added Latency** | < 0.1 ms | 0.5–2 ms (SSL + HTTP parsing) |
| **CPU Cost** | Minimal | Higher (TLS, HTTP parsing) |
| **Use Cases** | Any TCP app (DB, SMTP, non-HTTP) | Web servers, APIs, microservices |

**Decision: L7 for all web server traffic. L4 handled implicitly by GCP GCLB beneath our Envoy layer. Latency cost is acceptable given routing intelligence gained.**

---

## 6. Session Affinity: Cookie vs. IP Hash

| Dimension | Cookie-Based | IP Hash |
|-----------|-------------|---------|
| **Accuracy** | Exact — unique per session | Imprecise — entire /24 subnet maps to same backend |
| **NAT Friendliness** | Works behind NAT (cookie is per-browser) | Broken — all users behind corporate NAT same backend |
| **Redis Cost** | Yes — GET + SET per session | No — deterministic hash |
| **Cookie Theft Risk** | Possible (mitigated with HttpOnly + Secure) | N/A |
| **Mobile / Network Changes** | Preserved (cookie follows device) | Broken — IP changes = different backend |
| **Complexity** | Medium | Low |

**Decision: Default to Cookie-based sticky sessions. Use IP hash ONLY for non-browser clients (mobile apps, APIs) where cookie support is uncertain.**

---

## 7. Active vs. Passive Health Checks

| Dimension | Active (periodic probes) | Passive (from live traffic) |
|-----------|------------------------|--------------------------|
| **Detection Speed** | Bounded: up to `interval_secs` (5s) | Immediate — detects on first failed request |
| **Accuracy** | High — dedicated probe, controlled conditions | Can have false positives (slow request ≠ failure) |
| **Backend Load** | Small extra probe traffic | Zero overhead |
| **Works for idle backends** | Yes | No — no traffic = no detection |
| **Avoids false DOWN** | Less likely (ignores user traffic noise) | More likely (single slow req = eject?) |

**Decision: Both. Active probes detect failures within 10-15 seconds (3 failures × 5s interval). Passive outlier detection in Envoy catches them within 1-3 requests. Combined gives < 5s end-to-end failover.**

---

## 8. Consistency vs. Availability (CAP Analysis)

The load balancer system chooses **Availability over Consistency** in partition scenarios:

| Scenario | Behavior |
|---------|---------|
| Redis unavailable | LB continues routing (without session affinity, rate limiting temporarily disabled) |
| Config Manager unavailable | LB continues with last-known-good config (stale but functional) |
| Health check engine down | LB uses last-known health state from Redis (may route to dead backends transiently) |
| Cloud SQL unavailable | New config changes blocked; all existing LBs continue working from in-memory cache |

**Principle: The data plane (request forwarding) MUST stay up even if the control plane is completely down. Design for control plane failures being invisible to end clients.**

---

## 9. Pull vs. Push Config Propagation

| Dimension | Push (Config Manager → Envoy) | Pull (Envoy polls Config Manager) |
|-----------|------------------------------|----------------------------------|
| **Propagation Latency** | < 1 second (streaming) | Poll interval (e.g., 30s) |
| **Connection overhead** | Persistent gRPC stream per node | Polling HTTP requests |
| **Config Manager load** | One push per change regardless of node count | N requests per poll cycle |
| **Ordering guarantees** | Strong (streaming, sequential) | Weak (nodes may see different versions) |
| **Failure handling** | Stream reconnect with ACK/NACK | Graceful — just retry next poll |

**Decision: Push via xDS streaming (ADS). Envoy has built-in support. Push gives sub-second config propagation which is required for canary deployments and circuit breaker state.**

---

## Design Decision Summary

| Decision | Choice | Key Reason |
|----------|--------|-----------|
| LB Algorithm default | Least Connections | Self-adjusts to backend speed differences |
| Health checking | Centralized + passive Envoy outlier detection | Reduce probe fan-out; fast passive path |
| Hot state storage | Redis (shared) | Session affinity correctness across nodes |
| Config delivery | xDS push (ADS) | Sub-second propagation for canary/CB |
| Protocol | L7 (HTTP) | Path/host routing, TLS termination required |
| Session affinity | Cookie > IP hash | NAT friendliness, mobile client support |
| Health check strategy | Active + Passive | Balance idle detection with fast failover |
| Control plane failure | Fail open | Data plane availability > config freshness |
