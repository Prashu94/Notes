# 02 — Traffic & Capacity Estimation

## Scale Assumptions

| Parameter | Value |
|-----------|-------|
| Peak RPS (global) | 1,000,000 RPS |
| Average RPS | ~333,000 RPS (peak = 3× average) |
| Daily requests | 333K × 86,400 = **~28.8 billion/day** |
| Average request size (payload) | 2 KB |
| Average response size (payload) | 50 KB |
| Average backend processing time | 50 ms |
| Geographic regions | 2 (US-Central, EU-West), scaling to 5 |
| Backends per pool | up to 10,000 |

---

## Bandwidth

### Inbound (Client → Load Balancer)

```
Peak bandwidth in = RPS × avg_request_size
                  = 1,000,000 × 2 KB
                  = 2,000,000 KB/s
                  ≈ 2 GB/s inbound
```

### Outbound (Load Balancer → Client)

```
Peak bandwidth out = RPS × avg_response_size
                   = 1,000,000 × 50 KB
                   = 50,000,000 KB/s
                   ≈ 50 GB/s outbound
```

### Backend Traffic (Load Balancer ↔ Backend)

```
Same order of magnitude as client traffic:
  ~2 GB/s to backends (requests)
  ~50 GB/s from backends (responses)
Total: ~52 GB/s per region at peak
```

**Per region (2 regions active-active):**
- US region handles ~60% of traffic → ~31 GB/s
- EU region handles ~40% of traffic → ~21 GB/s

---

## Concurrent Connections

```
Using Little's Law:  N = λ × W
  λ = arrival rate (RPS) = 1,000,000
  W = avg time in system = 50ms = 0.05s

Active backend connections = 1,000,000 × 0.05 = 50,000

With HTTP keep-alive (clients reuse connections, multiplex ratio 10×):
  Client-side connections = 1,000,000 / 10 = 100,000 persistent client connections per second
  
Accumulated idle keep-alive connections (timeout 60s):
  ~100,000 × 60 = ~6,000,000 open client sockets

Target design capacity:  10,000,000 concurrent connections
```

---

## Health Check Traffic

```
Backends: 10,000 servers (across both regions)
Health check interval: 5 seconds
Health check payload: 200 bytes (HTTP HEAD /health)

Health check RPS = 10,000 / 5 = 2,000 RPS
Health check bandwidth = 2,000 × 200 bytes = 400 KB/s  ← negligible

From N LB nodes (20 per region), each checking all backends in its region:
  Per-LB check rate = 5,000 backends / 5s = 1,000 probes/sec per node
```

---

## Log Storage

```
Log entry fields:
  timestamp(8) + src_ip(16) + method(4) + path(128) + status(2)
  + latency_ms(4) + backend_id(16) + request_bytes(4) + response_bytes(4)
  + rule_id(16) + session_id(16) + edge_region(8)
  = ~400 bytes per request (uncompressed)

Daily log volume (uncompressed):
  = 28.8B × 400 bytes = 11.52 TB/day

With LZ4 compression (10:1 ratio):
  = ~1.15 TB/day

Monthly compressed: ~34.5 TB  (BigQuery hot tier)
Annual compressed:  ~420 TB   (GCS Coldline archive)
```

---

## In-Memory State (per Load Balancer node)

```
Backend routing table:
  Per backend: 256 bytes (IP + port + weight + health + conn_count + rps + p95)
  10,000 backends × 256 bytes = 2.56 MB  ← trivially small

Connection state table (TCP connections):
  Per connection: 512 bytes (src/dst IP+port, state, timestamps, backend_ptr)
  500,000 connections per node × 512 bytes = 256 MB RAM per node

Ring buffer for passive health check tracking:
  Per backend: 100-entry sliding window × 1 byte = 100 bytes
  10,000 backends × 100 bytes = 1 MB
```

---

## Shared State (Redis / Memorystore)

```
Sticky session mappings:
  session_id (16 bytes) → backend_id (8 bytes) + TTL metadata (8 bytes)
  50M active sessions × 32 bytes = 1.6 GB Redis RAM

Rate limit counters (token bucket):
  Per IP counter: key(16) + tokens(4) + last_refill(8) = 28 bytes
  1M unique active IPs × 28 bytes = 28 MB Redis RAM

Total Redis memory required: ~1.63 GB (with 2× headroom: 4 GB Memorystore instance)
```

---

## Load Balancer Node Capacity

```
Single LB node capability (32 vCPU, 64 GB RAM, 25 Gbps NIC):
  - User-space networking (DPDK/io_uring): ~100,000 RPS
  - Connection limit: 500,000 concurrent sockets
  - Bandwidth: ~12.5 GB/s (half-duplex)

Nodes needed for 500,000 RPS per region (US 60% of 1M RPS):
  = 500,000 / 100,000 = 5 nodes minimum
  
With 4× redundancy headroom: 20 nodes per region
With 2 active regions: 40 nodes total

In GCP: n2-standard-32 instances in a GKE Autopilot node pool
```

---

## Sizing Summary

| Metric | Value |
|--------|-------|
| **Peak RPS (global)** | 1,000,000 |
| **Daily Requests** | ~28.8 billion |
| **Peak Outbound Bandwidth** | ~50 GB/s |
| **Max Concurrent Connections** | ~10 million |
| **LB Nodes per Region** | 20 × n2-standard-32 |
| **Total LB Nodes** | 40 (2 regions) |
| **Daily Log Volume (compressed)** | ~1.15 TB |
| **Redis RAM (sessions + rate limits)** | ~4 GB (Memorystore M2) |
| **Health check overhead** | ~400 KB/s (negligible) |
| **Backend routing table** | 2.56 MB per node |
