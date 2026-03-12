# Load Balancer for Web Servers — System Design

> **Scale:** 1M RPS peak | **Geography:** Global (US + EU) | **Protocol:** L7 HTTP/HTTPS | **Cloud:** GCP  
> **Purpose:** Interview prep + production architecture reference

---

## Quick Summary

A globally distributed **Layer 7 load balancer** built on GCP that distributes HTTP/HTTPS traffic across backend web server pools. Uses **Envoy Proxy** as the data plane (configured via xDS), **GCP Cloud Load Balancing** for global Anycast ingress, and a custom **control plane** for health checking, configuration management, and observability.

---

## Design Files

| # | File | Description |
|---|------|-------------|
| 01 | [01-requirements.md](01-requirements.md) | Functional & Non-Functional Requirements, Priority Matrix |
| 02 | [02-traffic-estimation.md](02-traffic-estimation.md) | Traffic, Storage, Bandwidth, Node Sizing |
| 03 | [03-api-design.md](03-api-design.md) | Control Plane REST API — Pools, Backends, Rules, Rate Limits, Metrics |
| 04 | [04-database-design.md](04-database-design.md) | PostgreSQL schema, Redis key design, BigQuery logs, Data lifecycle |
| 05 | [05-high-level-architecture.md](05-high-level-architecture.md) | Mermaid architecture diagram, GCP services, Request flow |
| 06 | [06-detailed-components.md](06-detailed-components.md) | Envoy internals, Health Check Engine, Config Manager, Rate Limiter, Session Affinity |
| 07 | [07-tradeoffs.md](07-tradeoffs.md) | 9 major design decisions with comparison tables and verdicts |
| 08 | [08-failure-scenarios.md](08-failure-scenarios.md) | 7 failure scenarios with RTO/RPO, detection, and mitigation |
| 09 | [09-sequence-diagrams.md](09-sequence-diagrams.md) | 7 Mermaid sequence diagrams for all key flows |

---

## Key Numbers at a Glance

| Metric | Value |
|--------|-------|
| Peak RPS | **1,000,000 RPS** |
| P99 Added Latency | **< 5 ms** |
| Availability | **99.999%** (< 5.3 min/year downtime) |
| Failover Time | **< 30 seconds** (regional), **< 5 seconds** (single backend) |
| LB Nodes | **20 × n2-standard-32** per region (2 regions = 40 nodes) |
| Max Concurrent Connections | **10 million** |
| Daily Log Volume | **~1.15 TB** (compressed) |
| Config Propagation | **< 1 second** (xDS streaming push) |

---

## Architecture at a Glance

```
Internet
    │
    ▼
[Cloud Armor]  ← WAF + DDoS
    │
[Cloud CDN]    ← Static asset cache (~40% cache hit rate)
    │
[GCP Global HTTPS LB]  ← Anycast IP, geo-routing
    │
    ├──────────────────┐
    ▼                  ▼
[US Region]        [EU Region]
[Internal LB]      [Internal LB]
    │                  │
[Envoy Pool]       [Envoy Pool]    ← 20 nodes each, xDS-configured
[×20 nodes]        [×20 nodes]
    │                  │
[Redis]            [Redis]         ← Health state, sessions, rate limits
    │                  │
[Backends]         [Backends]      ← 10,000 backend web servers total

Control Plane (GKE, us-central1):
  ├─ Control Plane API (Cloud Run)
  ├─ Config Manager (xDS server, GKE Deployment)
  ├─ Health Check Engine (GKE DaemonSet)
  ├─ Cloud SQL (config source of truth)
  └─ Cloud Pub/Sub (event bus)
```

---

## Core Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Data plane** | Envoy Proxy | Battle-tested, xDS support, L7-aware |
| **Default LB algorithm** | Least Connections | Self-adjusts to slow backends; better than RR |
| **Health checking** | Centralized active + Envoy passive outlier detection | Fast (passive) + accurate (active) |
| **Config delivery** | xDS push (Aggregated DS) | Sub-second propagation for canary/circuit breaker |
| **Session affinity** | Cookie-based (Redis-backed) | Works behind NAT, survives IP changes |
| **Rate limiting** | Redis Lua atomic token bucket | Accurate, race-condition-free |
| **SSL termination** | At LB; cert from Certificate Manager | Central management, backends stay plain HTTP |
| **Control plane failure** | Fail open (LB continues with last config) | Data plane availability > config freshness |

---

## Key Flows (Covered in Sequence Diagrams)

1. **Normal request** — Client → Cloud Armor → CDN → GCLB → ILB → LB Node → Backend
2. **Backend failure detection** — Active health check + Envoy passive outlier detection
3. **New backend registration** — API → SQL → Pub/Sub → Config Manager → xDS → Envoy
4. **Rate limit rejection** — Redis Lua token bucket → 429 response
5. **Graceful drain** — Weight=0 → drain in-flight → remove endpoint → safe deploy
6. **SSL rotation** — Certificate Manager → Secret Manager → xDS LDS → hot-swap
7. **Circuit breaker** — CLOSED → OPEN (50% errors) → HALF_OPEN (30s) → CLOSED

---

## Interview Cheat Sheet

**"How does the LB handle a backend going down?"**
> Envoy passive outlier detection ejects it within 1-3 failed requests. Active health checks confirm UNHEALTHY in ~15s. Redis updated, all LB nodes notified via redis read on next request, or proactively via xDS EDS update.

**"How do sticky sessions work?"**
> Cookie `LB_AFFINITY` injected on first request. Subsequent requests: LB reads cookie, does `Redis GET lb:session:{id}` → gets pinned backend_id → routes there (if healthy, else fall back).

**"How does rate limiting work correctly across 20 LB nodes?"**
> Shared Redis instance. Lua script is atomic (single operation, no race conditions). All 20 LB nodes write to the same key per client IP.

**"What happens if Redis goes down?"**
> Fail open: sessions fall back to IP hash, rate limiting temporarily disabled, routing continues with last in-memory health snapshot. Memorystore HA auto-recovers in < 30s.

**"How is config pushed to all Envoy nodes without restart?"**
> xDS Aggregated Discovery Service (ADS). Config Manager maintains a persistent gRPC stream to each Envoy node. Config changes are pushed as incremental deltas (EDS/CDS) and acknowledged by Envoy. Zero restarts, zero dropped connections.
