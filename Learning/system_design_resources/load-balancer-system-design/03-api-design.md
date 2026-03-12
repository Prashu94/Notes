# 03 — API Design (Control Plane)

The load balancer exposes two surfaces:
1. **Data Plane** — transparent proxying; no explicit API surface, handles live traffic
2. **Control Plane API** — manages pools, backends, routing rules, health config, rate limits

---

## Base URL

```
https://lb-api.internal.company.com/v1
```

---

## Authentication

All endpoints require a **Bearer JWT** issued by Firebase Authentication.  
Service-to-service calls use **GCP Service Account** credentials (OAuth 2.0).

```
Authorization: Bearer <jwt_token>
X-Request-ID: <uuid-v4>   (idempotency key for mutating requests)
```

---

## Rate Limits

| Tier | Limit |
|------|-------|
| GET (read operations) | 1,000 req/min per client |
| POST / PUT (writes) | 100 req/min per client |
| DELETE | 100 req/min per client |
| Bulk / batch operations | 10 req/min per client |

---

## Standard Error Format

```json
{
  "error": {
    "code": "BACKEND_NOT_FOUND",
    "message": "Backend 'be-xyz123' does not exist in pool 'pool-abc456'.",
    "status": 404,
    "request_id": "req_01HXYZ9876ABCDEF",
    "documentation_url": "https://docs.company.com/lb-api/errors#BACKEND_NOT_FOUND"
  }
}
```

| HTTP Status | Error Code | Meaning |
|-------------|-----------|---------|
| 400 | `INVALID_REQUEST` | Malformed JSON or invalid field values |
| 401 | `UNAUTHENTICATED` | Missing or expired JWT |
| 403 | `FORBIDDEN` | Authenticated but lacks permission |
| 404 | `NOT_FOUND` | Pool, backend, or rule not found |
| 409 | `CONFLICT` | Backend already exists in pool |
| 422 | `UNPROCESSABLE` | Semantically invalid (e.g., weight = 0 on only backend) |
| 429 | `RATE_LIMITED` | Exceeded API rate limit |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

---

## Pagination

All collection endpoints use **cursor-based pagination**:

```
GET /v1/pools/{pool_id}/backends?limit=100&cursor=<opaque_b64_cursor>
```

Response envelope:
```json
{
  "data": [ ... ],
  "next_cursor": "eyJpZCI6ImJlLXh5ejEyMyJ9",
  "has_more": true,
  "total_count": 4821
}
```

---

## API Endpoints

---

### 1. Backend Pools

#### `POST /v1/pools` — Create Pool

**Request:**
```json
{
  "name": "web-servers-us-central",
  "algorithm": "LEAST_CONNECTIONS",
  "health_check": {
    "protocol": "HTTP",
    "path": "/healthz",
    "interval_seconds": 5,
    "timeout_seconds": 2,
    "healthy_threshold": 2,
    "unhealthy_threshold": 3,
    "expected_status_codes": [200, 204]
  },
  "session_affinity": {
    "type": "COOKIE",
    "cookie_name": "LB_AFFINITY",
    "ttl_seconds": 3600
  },
  "circuit_breaker": {
    "enabled": true,
    "error_rate_threshold": 0.5,
    "min_request_volume": 100,
    "window_seconds": 10,
    "open_duration_seconds": 30
  },
  "connection_draining_seconds": 30
}
```

**Response `201 Created`:**
```json
{
  "pool_id": "pool-a1b2c3d4",
  "name": "web-servers-us-central",
  "algorithm": "LEAST_CONNECTIONS",
  "status": "ACTIVE",
  "backend_count": 0,
  "created_at": "2026-03-12T10:00:00Z",
  "updated_at": "2026-03-12T10:00:00Z"
}
```

---

#### `GET /v1/pools/{pool_id}` — Get Pool

**Response `200 OK`:**
```json
{
  "pool_id": "pool-a1b2c3d4",
  "name": "web-servers-us-central",
  "algorithm": "LEAST_CONNECTIONS",
  "status": "ACTIVE",
  "backend_count": 18,
  "healthy_count": 17,
  "rps": 48320,
  "p99_latency_ms": 4.7
}
```

---

#### `PUT /v1/pools/{pool_id}` — Update Pool Config

Supports partial update (PATCH semantics). Only provided fields are updated.

```json
{
  "algorithm": "WEIGHTED_ROUND_ROBIN",
  "connection_draining_seconds": 60
}
```

---

#### `DELETE /v1/pools/{pool_id}` — Delete Pool

Returns `409 CONFLICT` if the pool is referenced by active routing rules.

---

### 2. Backends

#### `POST /v1/pools/{pool_id}/backends` — Add Backend

**Request:**
```json
{
  "address": "10.0.1.42",
  "port": 8080,
  "weight": 100,
  "max_connections": 2000,
  "metadata": {
    "zone": "us-central1-a",
    "version": "v2.3.1",
    "instance_id": "gke-node-xyz"
  }
}
```

**Response `201 Created`:**
```json
{
  "backend_id": "be-f9e8d7c6",
  "pool_id": "pool-a1b2c3d4",
  "address": "10.0.1.42",
  "port": 8080,
  "weight": 100,
  "max_connections": 2000,
  "health_status": "UNKNOWN",
  "state": "ACTIVE",
  "active_connections": 0,
  "created_at": "2026-03-12T10:01:00Z"
}
```

`health_status` transitions: `UNKNOWN` → `HEALTHY` | `UNHEALTHY`

---

#### `PUT /v1/pools/{pool_id}/backends/{backend_id}/drain` — Graceful Drain

Stops new requests from being routed to this backend; waits for in-flight requests to complete.

**Request:**
```json
{ "drain_timeout_seconds": 30 }
```

**Response `200 OK`:**
```json
{
  "backend_id": "be-f9e8d7c6",
  "state": "DRAINING",
  "drain_started_at": "2026-03-12T10:05:00Z",
  "drain_deadline": "2026-03-12T10:05:30Z",
  "active_connections": 142
}
```

---

#### `DELETE /v1/pools/{pool_id}/backends/{backend_id}` — Remove Backend

If backend is not in `DRAINING` state, immediate removal (in-flight requests may error).  
Idempotent: returns `204` even if already removed.

**Response `204 No Content`**

---

#### `GET /v1/pools/{pool_id}/health` — Pool Health Status

**Response `200 OK`:**
```json
{
  "pool_id": "pool-a1b2c3d4",
  "summary": {
    "healthy": 17,
    "unhealthy": 2,
    "draining": 1,
    "unknown": 0,
    "total": 20
  },
  "backends": [
    {
      "backend_id": "be-f9e8d7c6",
      "address": "10.0.1.42:8080",
      "health_status": "HEALTHY",
      "state": "ACTIVE",
      "last_probe_at": "2026-03-12T10:09:55Z",
      "consecutive_successes": 24,
      "consecutive_failures": 0,
      "active_connections": 87,
      "rps": 4320,
      "p95_latency_ms": 3.2
    },
    {
      "backend_id": "be-c5b4a3b2",
      "address": "10.0.1.88:8080",
      "health_status": "UNHEALTHY",
      "state": "ACTIVE",
      "last_probe_at": "2026-03-12T10:09:50Z",
      "consecutive_successes": 0,
      "consecutive_failures": 3,
      "failure_reason": "HTTP 503: Service Unavailable",
      "active_connections": 0,
      "rps": 0,
      "p95_latency_ms": null
    }
  ]
}
```

---

### 3. Routing Rules

#### `POST /v1/rules` — Create Routing Rule

**Request:**
```json
{
  "name": "api-v2-canary-10pct",
  "priority": 100,
  "match": {
    "host": "api.company.com",
    "path_prefix": "/api/v2/",
    "methods": ["GET", "POST"],
    "headers": {
      "X-Beta-User": "true"
    }
  },
  "action": {
    "type": "WEIGHTED_FORWARD",
    "targets": [
      { "pool_id": "pool-v2-canary",  "weight": 10 },
      { "pool_id": "pool-v1-stable",  "weight": 90 }
    ]
  }
}
```

**Response `201 Created`:**
```json
{
  "rule_id": "rule-r9s8t7u6",
  "name": "api-v2-canary-10pct",
  "priority": 100,
  "status": "ACTIVE",
  "created_at": "2026-03-12T10:10:00Z"
}
```

Rules are evaluated in ascending **priority** order (lower number = higher priority). First match wins.

---

### 4. Rate Limits

#### `POST /v1/rate-limits` — Configure Rate Limit Policy

**Request:**
```json
{
  "name": "per-ip-global-1000rpm",
  "scope": "SOURCE_IP",
  "algorithm": "TOKEN_BUCKET",
  "rate_per_minute": 1000,
  "burst_size": 2000,
  "action_on_exceed": "REJECT",
  "reject_status_code": 429,
  "reject_message": "Rate limit exceeded. Retry after {retry_after}s.",
  "applies_to": {
    "pool_id": "pool-a1b2c3d4",
    "path_prefix": "/"
  }
}
```

---

### 5. Metrics

#### `GET /v1/pools/{pool_id}/metrics` — Real-Time Metrics

```
GET /v1/pools/pool-a1b2c3d4/metrics?window=60s&granularity=5s
```

**Response `200 OK`:**
```json
{
  "pool_id": "pool-a1b2c3d4",
  "window": "60s",
  "granularity": "5s",
  "aggregated": {
    "rps": 48320,
    "p50_latency_ms": 0.4,
    "p95_latency_ms": 2.1,
    "p99_latency_ms": 8.7,
    "p999_latency_ms": 19.3,
    "error_rate_pct": 0.12,
    "active_connections": 12847,
    "bytes_in_per_sec": 96640000,
    "bytes_out_per_sec": 2416000000
  },
  "timeseries": [
    { "timestamp": "2026-03-12T10:09:00Z", "rps": 47200, "p99_latency_ms": 7.9 },
    { "timestamp": "2026-03-12T10:09:05Z", "rps": 49100, "p99_latency_ms": 9.1 }
  ]
}
```

---

## Idempotency

All `POST` mutating endpoints accept an `X-Request-ID` header.  
Duplicate requests with the same `X-Request-ID` within 24 hours return the original response without creating duplicates.

```
X-Request-ID: 01HXYZ9876ABCDEF0123456789AB
```

---

## Versioning

- Current stable version: `v1`
- Breaking changes introduce a new version prefix (`v2`)
- Old versions deprecated with 12-month sunset window
- `Sunset` header included in responses for deprecated API versions
