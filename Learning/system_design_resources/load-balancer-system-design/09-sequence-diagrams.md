# 09 — Sequence Diagrams

---

## Diagram 1: Normal Request Flow (L7 HTTP/HTTPS)

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant CA as Cloud Armor<br/>(WAF/DDoS)
    participant CDN as Cloud CDN
    participant GCLB as GCP Global LB<br/>(Anycast)
    participant ILB as Internal LB<br/>(Regional)
    participant LB as LB Node<br/>(Envoy)
    participant Redis as Memorystore<br/>Redis
    participant Backend as Backend Server

    Client->>CA: HTTPS GET /api/products (TCP SYN + TLS ClientHello)
    Note over CA: WAF rules check<br/>IP reputation check
    CA->>CDN: Forward (rules passed)
    CDN->>CDN: Cache lookup
    alt Cache HIT
        CDN-->>Client: 200 OK (cached response)
    else Cache MISS
        CDN->>GCLB: Forward to origin
        GCLB->>GCLB: Geo-route: pick us-central1 backend group
        GCLB->>ILB: Route to regional internal LB
        ILB->>LB: Round-robin to LB Node #7

        Note over LB: TLS termination<br/>Certificate from Secret Manager
        LB->>LB: Evaluate routing rules (in-memory)<br/>Match: host=api.company.com, path=/api/*

        LB->>Redis: GET lb:session:{session_cookie} (sticky session check)
        Redis-->>LB: backend_id = "be-f9e8d7c6"

        LB->>Redis: GET lb:health:be-f9e8d7c6
        Redis-->>LB: status = HEALTHY

        alt Rate limit check
            LB->>Redis: EVAL token_bucket_lua (INCR + check)
            Redis-->>LB: allowed=true, remaining=847
        end

        LB->>Redis: INCR lb:conns:be-f9e8d7c6
        Redis-->>LB: new_count = 88

        LB->>Backend: HTTP GET /api/products<br/>Headers: X-Forwarded-For: {client_ip}<br/>         X-Request-ID: req_01HXYZ...

        Backend-->>LB: HTTP 200 OK + JSON body (50KB)

        LB->>Redis: DECR lb:conns:be-f9e8d7c6
        LB-->>Client: HTTPS 200 OK + body
        Note over LB: Async: log to Cloud Logging
    end
```

---

## Diagram 2: Backend Failure Detection & Failover

```mermaid
sequenceDiagram
    autonumber
    participant HC as Health Check Engine
    participant Redis as Redis<br/>(Health State)
    participant PS as Cloud Pub/Sub<br/>(health-events)
    participant CM as Config Manager<br/>(xDS Server)
    participant LB as LB Node<br/>(Envoy)
    participant Backend as Backend Server<br/>(10.0.1.88)
    participant Mon as Cloud Monitoring

    Note over Backend: Backend starts failing<br/>(OOM, crash, etc.)

    HC->>Backend: HTTP HEAD /healthz (probe #1)
    Backend-->>HC: Connection refused / timeout

    HC->>Redis: HMSET lb:health:be-c5b4a3b2<br/>consecutive_fail=1, last_fail_reason="connection refused"

    Note over LB: Passive path (concurrent):
    LB->>Backend: HTTP GET /api/data (real user request)
    Backend-->>LB: TCP RST (connection refused)
    Note over LB: Envoy outlier detection:<br/>consecutive_5xx++ (passive eject threshold)
    LB->>LB: Eject be-c5b4a3b2 from cluster<br/>(local, temporary — 30s ejection interval)

    HC->>Backend: HTTP HEAD /healthz (probe #2 at T+5s)
    Backend-->>HC: Timeout after 2s

    HC->>Redis: HMSET lb:health:be-c5b4a3b2<br/>consecutive_fail=2

    HC->>Backend: HTTP HEAD /healthz (probe #3 at T+10s)
    Backend-->>HC: Timeout after 2s

    HC->>Redis: HMSET lb:health:be-c5b4a3b2<br/>status=UNHEALTHY, consecutive_fail=3

    HC->>PS: Publish {event: BACKEND_DOWN, backend_id: be-c5b4a3b2}

    PS->>CM: Deliver BACKEND_DOWN event
    CM->>Redis: GET lb:health:be-c5b4a3b2 (confirm)
    Redis-->>CM: status=UNHEALTHY

    CM->>LB: xDS EDS update: remove be-c5b4a3b2 from cluster
    Note over LB: Endpoint removed from routing table<br/>No more requests sent to 10.0.1.88

    HC->>Mon: Emit metric: unhealthy_backend_count{pool}++
    Mon->>Mon: Alert: unhealthy_backends > threshold → PagerDuty
```

---

## Diagram 3: New Backend Registration & Config Propagation

```mermaid
sequenceDiagram
    autonumber
    actor Operator
    participant API as Control Plane API<br/>(Cloud Run)
    participant SQL as Cloud SQL<br/>(PostgreSQL)
    participant PS as Cloud Pub/Sub
    participant CM as Config Manager<br/>(xDS)
    participant HC as Health Check Engine
    participant Redis as Redis
    participant LB1 as LB Node 1
    participant LB2 as LB Node 2
    participant Backend as New Backend<br/>(10.0.1.100)

    Operator->>API: POST /v1/pools/pool-a1b2c3d4/backends<br/>{"address":"10.0.1.100","port":8080,"weight":100}

    API->>API: Validate request (auth + schema)
    API->>SQL: INSERT INTO backends<br/>(pool_id, address, port, weight, state=ACTIVE)
    SQL-->>API: backend_id = "be-new123"

    API->>PS: Publish {event: BACKEND_ADDED,<br/>pool_id: pool-a1b2c3d4,<br/>backend_id: be-new123}

    API-->>Operator: 201 Created {backend_id: be-new123, health_status: UNKNOWN}

    Note over PS: Async processing begins

    PS->>CM: Deliver BACKEND_ADDED event
    CM->>SQL: SELECT backend config for be-new123
    SQL-->>CM: {address:10.0.1.100, port:8080, weight:100}

    Note over CM: Backend NOT added to xDS yet<br/>Must wait for first successful health check

    PS->>HC: Deliver BACKEND_ADDED event
    HC->>Redis: HMSET lb:health:be-new123<br/>status=UNKNOWN, consecutive_ok=0

    HC->>Backend: HTTP HEAD /healthz (probe #1)
    Backend-->>HC: 200 OK

    HC->>Redis: HMSET lb:health:be-new123<br/>consecutive_ok=1

    HC->>Backend: HTTP HEAD /healthz (probe #2 at T+5s)
    Backend-->>HC: 200 OK

    Note over HC: healthy_threshold=2 reached!
    HC->>Redis: HMSET lb:health:be-new123 status=HEALTHY
    HC->>PS: Publish {event: BACKEND_HEALTHY, backend_id: be-new123}

    PS->>CM: Deliver BACKEND_HEALTHY event
    CM->>LB1: xDS EDS DeltaDiscoveryResponse:<br/>add endpoint 10.0.1.100:8080 to cluster pool-a1b2c3d4
    CM->>LB2: xDS EDS DeltaDiscoveryResponse (same)

    LB1-->>CM: EDS ACK
    LB2-->>CM: EDS ACK

    Note over LB1,LB2: New backend 10.0.1.100<br/>now receives traffic!
```

---

## Diagram 4: Rate Limit — Request Rejected

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client (IP: 203.0.113.42)
    participant LB as LB Node<br/>(Envoy)
    participant Redis as Redis<br/>(Rate Limiter)

    Note over Client: Sending 1001st request<br/>in the last 60 seconds

    Client->>LB: HTTP GET /api/data

    LB->>LB: Extract client IP: 203.0.113.42
    LB->>LB: Identify rate limit policy: per-ip-global-1000rpm

    LB->>Redis: EVAL token_bucket_lua {<br/>  key: lb:rl:policy-1:203.0.113.42,<br/>  rate: 16.67 tokens/sec,<br/>  burst: 2000,<br/>  now: 1741776000123<br/>}

    Note over Redis: Lua script (atomic):<br/>tokens = 0 (bucket empty)<br/>return {0, retry_after=58ms}

    Redis-->>LB: {allowed: 0, retry_after_ms: 58}

    LB-->>Client: HTTP 429 Too Many Requests<br/>Retry-After: 1<br/>X-RateLimit-Limit: 1000<br/>X-RateLimit-Remaining: 0<br/>X-RateLimit-Reset: 2026-03-12T10:01:00Z<br/><br/>{"error": {"code": "RATE_LIMITED",<br/>  "message": "Too many requests. Retry in 58ms."}}

    Note over LB: Access log written:<br/>rate_limited=true
```

---

## Diagram 5: Graceful Backend Drain (Rolling Deployment)

```mermaid
sequenceDiagram
    autonumber
    actor DevOps
    participant API as Control Plane API
    participant SQL as Cloud SQL
    participant PS as Cloud Pub/Sub
    participant CM as Config Manager
    participant LB as LB Node<br/>(Envoy)
    participant Redis as Redis
    participant Backend as Backend<br/>(be-xyz789)<br/>10.0.1.42:8080

    Note over DevOps: Starting rolling deployment<br/>of new version v2.4.0

    DevOps->>API: PUT /v1/pools/pool-a1b2c3d4/backends/be-xyz789/drain<br/>{"drain_timeout_seconds": 30}

    API->>SQL: UPDATE backends SET state=DRAINING<br/>WHERE backend_id=be-xyz789
    API->>PS: Publish {event: BACKEND_DRAINING, backend_id: be-xyz789}

    API-->>DevOps: 200 OK {state: DRAINING,<br/>drain_deadline: T+30s,<br/>active_connections: 142}

    PS->>CM: Deliver BACKEND_DRAINING event

    CM->>LB: xDS EDS update:<br/>set endpoint 10.0.1.42:8080 weight=0<br/>(stop new requests, drain inflight)

    Note over LB: Weight=0 → no new requests routed<br/>In-flight 142 requests continue to completion

    loop Every 5 seconds during drain
        LB->>Redis: GET lb:conns:be-xyz789
        Redis-->>LB: active_connections = 142 → 87 → 31 → 0
    end

    Note over LB: All connections drained (T+18s)

    LB->>CM: Signal: endpoint drained (via metrics)
    CM->>PS: Publish {event: BACKEND_DRAINED, backend_id: be-xyz789}
    PS->>API: Deliver BACKEND_DRAINED

    API->>SQL: UPDATE backends SET state=DELETED<br/>WHERE backend_id=be-xyz789

    CM->>LB: xDS EDS update:<br/>remove endpoint 10.0.1.42:8080 from cluster

    Note over DevOps: Safe to deploy new version to 10.0.1.42<br/>Then re-register as new backend
```

---

## Diagram 6: SSL Certificate Rotation

```mermaid
sequenceDiagram
    autonumber
    participant CM_CERT as GCP Certificate Manager
    participant SM as Secret Manager
    participant PS as Cloud Pub/Sub
    participant CFG as Config Manager
    participant LB1 as LB Node 1
    participant LB2 as LB Node 2

    Note over CM_CERT: Certificate expiry in 30 days<br/>Auto-renewal triggered

    CM_CERT->>CM_CERT: Generate new certificate<br/>via ACME (Let's Encrypt) or CA
    CM_CERT->>SM: Store new cert + private key<br/>as new Secret version (v42)

    SM->>PS: Publish {event: SECRET_VERSION_ADDED,<br/>secret: tls-cert-wildcard,<br/>version: 42}

    PS->>CFG: Deliver SECRET_VERSION_ADDED
    CFG->>SM: GetSecretVersion tls-cert-wildcard/v42
    SM-->>CFG: {certificate: ..., private_key: ...}

    CFG->>LB1: xDS LDS update:<br/>new TLS context with cert v42
    CFG->>LB2: xDS LDS update:<br/>new TLS context with cert v42

    LB1->>LB1: Hot-swap TLS context<br/>(no connections dropped!)
    LB2->>LB2: Hot-swap TLS context

    LB1-->>CFG: LDS ACK (v42 active)
    LB2-->>CFG: LDS ACK (v42 active)

    Note over LB1,LB2: New TLS certificate active<br/>Old cert accepted during overlap period<br/>(clients with existing TLS sessions unaffected)

    CFG->>SM: Destroy old secret version v41<br/>(after 48h grace period)
```

---

## Diagram 7: Circuit Breaker — Open/Half-Open/Close Transitions

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant LB as LB Node<br/>(Envoy)
    participant Redis as Redis<br/>(Circuit Breaker State)
    participant Backend as Backend Pool<br/>(pool-a1b2c3d4)

    Note over Backend: Backend error rate spikes<br/>above 50% threshold

    Client->>LB: Request #1
    LB->>Redis: Check lb:cb:pool-a1b2c3d4 → CLOSED
    LB->>Backend: Forward request
    Backend-->>LB: HTTP 500 Error

    LB->>Redis: INCR error_count (now 52/100 = 52%)
    Note over Redis: Error rate 52% > threshold 50%<br/>Circuit opened!
    Redis->>Redis: SET lb:cb:pool-a1b2c3d4 OPEN<br/>EXPIRE 30  (open_duration=30s)

    Client->>LB: Request #2
    LB->>Redis: Check lb:cb:pool-a1b2c3d4 → OPEN
    LB-->>Client: 503 Service Unavailable<br/>Retry-After: 30<br/>(fail fast, no backend hit)

    Note over Redis: 30 seconds pass (circuit open)

    Redis->>Redis: Key expires → state becomes HALF_OPEN<br/>(LB checks on next request)

    Client->>LB: Request #3
    LB->>Redis: Check lb:cb:pool-a1b2c3d4 → missing key (HALF_OPEN)
    Note over LB: Probe one request through

    LB->>Backend: Forward probe request (single request)
    alt Backend recovered
        Backend-->>LB: HTTP 200 OK
        LB->>Redis: SET lb:cb:pool-a1b2c3d4 CLOSED<br/>RESET counters
        LB-->>Client: 200 OK
        Note over LB,Backend: Circuit CLOSED — normal operation resumes
    else Backend still failing
        Backend-->>LB: HTTP 500 Error
        LB->>Redis: SET lb:cb:pool-a1b2c3d4 OPEN<br/>EXPIRE 60  (backoff: 2× duration)
        LB-->>Client: 503 Service Unavailable
    end
```
