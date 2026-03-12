# 01 — Requirements: Load Balancer for Web Servers

## Functional Requirements

### MVP (Phase 1)

| # | Requirement | Priority |
|---|-------------|----------|
| F1 | **Traffic Distribution**: Distribute incoming HTTP/HTTPS requests across a pool of backend web servers | P0 |
| F2 | **Load Balancing Algorithms**: Round Robin, Weighted Round Robin, Least Connections, IP Hash, Consistent Hashing | P0 |
| F3 | **Active Health Checks**: Periodic HTTP/TCP probes to each backend; configurable interval, timeout, thresholds | P0 |
| F4 | **Passive Health Checks**: Detect failures from live traffic errors (5xx, connection refused) | P0 |
| F5 | **SSL/TLS Termination**: Terminate TLS at the LB; forward plain HTTP to backends | P0 |
| F6 | **Sticky Sessions**: Pin a client to a specific backend via cookie injection or IP hash | P0 |
| F7 | **Dynamic Backend Management**: Add, remove, and drain backends without traffic loss | P0 |
| F8 | **Path/Host-Based Routing**: Route requests by URL path prefix, hostname, HTTP method | P0 |
| F9 | **Connection Draining**: Allow in-flight requests to complete before removing a backend | P0 |

### Phase 2

| # | Requirement | Priority |
|---|-------------|----------|
| F10 | **Rate Limiting**: Per-IP / per-API-key / per-path limits using the token bucket algorithm | P1 |
| F11 | **Circuit Breaker**: Automatically open circuit when backend error rate exceeds threshold | P1 |
| F12 | **WebSocket & HTTP/2 Support**: Long-lived and multiplexed connections | P1 |
| F13 | **Canary / A/B Routing**: Route X% of traffic to a canary backend pool | P1 |
| F14 | **Geo-Based Routing**: Route users to the nearest healthy regional cluster | P1 |
| F15 | **Header Injection / Rewriting**: Inject `X-Forwarded-For`, custom headers; rewrite paths | P1 |
| F16 | **mTLS**: Client certificate authentication between LB and backends | P2 |
| F17 | **GRPC Load Balancing**: gRPC-aware L7 load balancing with trailers support | P2 |

---

## Non-Functional Requirements

| Attribute | Target | Notes |
|-----------|--------|-------|
| **Peak Throughput** | 1,000,000 RPS globally | Across all regions |
| **P50 Added Latency** | < 0.5 ms | LB processing overhead only |
| **P99 Added Latency** | < 5 ms | Including SSL resumption |
| **P999 Added Latency** | < 20 ms | Tail latency budget |
| **Availability** | 99.999% | < 5.3 min downtime/year |
| **Failure Detection Time** | < 2 seconds | Active health check detection |
| **Failover Time** | < 5 seconds | Time to stop routing to failed backend |
| **Max Backends per Pool** | 10,000 servers | |
| **Max Concurrent Connections** | 10,000,000 | Client-side keep-alive |
| **Config Propagation Latency** | < 30 seconds | Globally consistent config |
| **SSL Session Resumption** | > 90% hit rate | TLS 1.3 session tickets |
| **Horizontal Scalability** | Linear | Adding LB nodes increases throughput linearly |
| **Observability** | Per-backend P99 latency, RPS, error rate | Real-time and historical |

---

## Capacity Assumptions

- Backend servers are stateless (or session-offloaded to Redis/Memcached)
- Clients support HTTP/1.1 and HTTP/2; HTTP/3 (QUIC) is a future consideration
- Average request payload: **2 KB**; average response payload: **50 KB**
- Average backend processing time: **50 ms**
- Geographic distribution: **US** (primary) + **EU** (secondary), expanding to 5 regions

---

## Out of Scope

- **Layer 4 (TCP/UDP) raw load balancing** — handled by GCP Cloud Load Balancing primitives
- **DNS infrastructure** — handled by Cloud DNS / Anycast
- **Backend application logic** — black box to the LB
- **Service mesh (Envoy/Istio)** — covered in separate design
- **Content caching** — handled by Cloud CDN upstream of the LB
- **API gateway features** (auth, transformation) — handled by Apigee upstream

---

## Priority Matrix

```
╔══════════════════════════════════════════════════════╗
║              PRIORITY MATRIX                         ║
╠═══════════════════════╦══════════════════════════════╣
║  MVP (Ship Day 1)     ║  Phase 2 (Next Quarter)      ║
╠═══════════════════════╬══════════════════════════════╣
║ Round Robin           ║ Rate Limiting                ║
║ Weighted RR           ║ Circuit Breaker              ║
║ Least Connections     ║ WebSocket/HTTP2              ║
║ IP Hash               ║ Canary Routing               ║
║ Active Health Checks  ║ Geo Routing                  ║
║ Passive Health Checks ║ Header Rewriting             ║
║ SSL Termination       ║                              ║
║ Sticky Sessions       ║  Phase 3 (Future)            ║
║ Connection Draining   ║ mTLS                         ║
║ Path/Host Routing     ║ gRPC LB                      ║
║ Dynamic Backend Mgmt  ║ HTTP/3 (QUIC)                ║
╚═══════════════════════╩══════════════════════════════╝
```
