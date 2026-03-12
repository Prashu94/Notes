# 04 — Database Design

The load balancer system uses **three storage tiers** with different access patterns:

| Tier | Technology | Purpose |
|------|-----------|---------|
| **Config Store** | Cloud SQL (PostgreSQL 15) | Persistent pool/backend/rule configuration |
| **Hot State** | Memorystore (Redis 7) | Health state, sticky sessions, rate limit counters |
| **Analytics** | BigQuery | Access logs, metrics history, capacity planning |

---

## Cloud SQL (PostgreSQL) — Configuration Database

### Schema

#### `pools` table

```sql
CREATE TABLE pools (
    pool_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    algorithm       VARCHAR(50)  NOT NULL CHECK (algorithm IN (
                        'ROUND_ROBIN', 'WEIGHTED_ROUND_ROBIN',
                        'LEAST_CONNECTIONS', 'IP_HASH', 'CONSISTENT_HASH'
                    )),
    status          VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE'
                        CHECK (status IN ('ACTIVE', 'DISABLED', 'DELETED')),
    draining_timeout_seconds  INT NOT NULL DEFAULT 30,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pools_status ON pools(status) WHERE status = 'ACTIVE';
```

#### `health_check_configs` table

```sql
CREATE TABLE health_check_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id         UUID NOT NULL REFERENCES pools(pool_id) ON DELETE CASCADE,
    protocol        VARCHAR(10) NOT NULL CHECK (protocol IN ('HTTP', 'HTTPS', 'TCP')),
    path            VARCHAR(512) DEFAULT '/healthz',
    port            INT,                   -- NULL means use backend's port
    interval_secs   INT NOT NULL DEFAULT 5,
    timeout_secs    INT NOT NULL DEFAULT 2,
    healthy_thresh  INT NOT NULL DEFAULT 2,
    unhealthy_thresh INT NOT NULL DEFAULT 3,
    expected_codes  INT[] NOT NULL DEFAULT '{200}',
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (pool_id)
);
```

#### `session_affinity_configs` table

```sql
CREATE TABLE session_affinity_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id         UUID NOT NULL REFERENCES pools(pool_id) ON DELETE CASCADE,
    affinity_type   VARCHAR(20) NOT NULL CHECK (affinity_type IN ('NONE', 'COOKIE', 'IP_HASH')),
    cookie_name     VARCHAR(128),
    ttl_seconds     INT NOT NULL DEFAULT 3600,
    UNIQUE (pool_id)
);
```

#### `circuit_breaker_configs` table

```sql
CREATE TABLE circuit_breaker_configs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id                 UUID NOT NULL REFERENCES pools(pool_id) ON DELETE CASCADE,
    enabled                 BOOLEAN NOT NULL DEFAULT TRUE,
    error_rate_threshold    NUMERIC(4,3) NOT NULL DEFAULT 0.5,  -- 0.0–1.0
    min_request_volume      INT NOT NULL DEFAULT 100,
    window_seconds          INT NOT NULL DEFAULT 10,
    open_duration_seconds   INT NOT NULL DEFAULT 30,
    UNIQUE (pool_id)
);
```

#### `backends` table

```sql
CREATE TABLE backends (
    backend_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id         UUID NOT NULL REFERENCES pools(pool_id) ON DELETE CASCADE,
    address         INET NOT NULL,
    port            INT NOT NULL CHECK (port BETWEEN 1 AND 65535),
    weight          INT NOT NULL DEFAULT 100 CHECK (weight BETWEEN 0 AND 10000),
    max_connections INT NOT NULL DEFAULT 10000,
    state           VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
                        CHECK (state IN ('ACTIVE', 'DRAINING', 'DISABLED', 'DELETED')),
    zone            VARCHAR(64),
    version_label   VARCHAR(64),
    instance_id     VARCHAR(256),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (pool_id, address, port)
);

CREATE INDEX idx_backends_pool_active ON backends(pool_id, state)
    WHERE state = 'ACTIVE';

CREATE INDEX idx_backends_pool_id ON backends(pool_id);
```

#### `routing_rules` table

```sql
CREATE TABLE routing_rules (
    rule_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    priority        INT NOT NULL,
    match_host      VARCHAR(255),
    match_path_prefix VARCHAR(512),
    match_methods   TEXT[],
    match_headers   JSONB,               -- { "header_name": "value" }
    action_type     VARCHAR(30) NOT NULL CHECK (action_type IN (
                        'FORWARD', 'WEIGHTED_FORWARD', 'REDIRECT', 'REJECT'
                    )),
    action_config   JSONB NOT NULL,      -- pool targets with weights, redirect config, etc.
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_routing_rules_priority ON routing_rules(priority ASC)
    WHERE status = 'ACTIVE';
CREATE INDEX idx_routing_rules_match_host ON routing_rules(match_host)
    WHERE status = 'ACTIVE';
```

#### `rate_limit_policies` table

```sql
CREATE TABLE rate_limit_policies (
    policy_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    scope           VARCHAR(20) NOT NULL CHECK (scope IN ('SOURCE_IP', 'API_KEY', 'GLOBAL')),
    algorithm       VARCHAR(20) NOT NULL DEFAULT 'TOKEN_BUCKET',
    rate_per_minute INT NOT NULL,
    burst_size      INT NOT NULL,
    action          VARCHAR(20) NOT NULL DEFAULT 'REJECT',
    reject_code     INT NOT NULL DEFAULT 429,
    pool_id         UUID REFERENCES pools(pool_id) ON DELETE CASCADE,
    path_prefix     VARCHAR(512) DEFAULT '/',
    enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `ssl_certificates` table

```sql
CREATE TABLE ssl_certificates (
    cert_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    provider        VARCHAR(20) NOT NULL DEFAULT 'GCP_CERTIFICATE_MANAGER',
    gcp_cert_id     VARCHAR(512),        -- GCP Certificate Manager resource name
    domains         TEXT[] NOT NULL,
    expires_at      TIMESTAMPTZ,
    auto_renew      BOOLEAN NOT NULL DEFAULT TRUE,
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### ER Diagram

```
┌─────────────────────┐
│       pools         │
│─────────────────────│
│ pool_id (PK)        │
│ name                │──────────────────────────────┐
│ algorithm           │                              │
│ status              │                              │
└─────────────────────┘                              │
        │  1                                         │
        │                                            │
   ─────┼─────────────────────────────────           │
   │    │    │           │          │                │
   │    │    │           │          │                │
   ▼    ▼    ▼           ▼          ▼                ▼
┌──────┐ ┌─────────────┐ ┌────────────┐  ┌──────────────────┐
│health│ │session_affin│ │circuit_br. │  │    backends      │
│_check│ │ity_configs  │ │_configs    │  │──────────────────│
│_conf │ └─────────────┘ └────────────┘  │ backend_id (PK)  │
└──────┘                                 │ pool_id (FK)     │
                                         │ address          │
                                         │ port             │
                                         │ weight           │
                                         │ state            │
                                         └──────────────────┘
```

---

## Memorystore (Redis) — Hot State

All Redis keys follow the namespace pattern: `lb:{entity}:{id}:{field}`

### Health State

```
Key:    lb:health:{backend_id}
Type:   Hash
TTL:    None (updated by health check loop)
Fields:
  status          → "HEALTHY" | "UNHEALTHY" | "UNKNOWN"
  consecutive_ok  → integer
  consecutive_fail → integer
  last_check_ts   → unix_ms timestamp
  last_fail_reason → string (last failure message)
  active_conns    → integer (updated in real-time)
  rps             → integer (rolling 10s window)
```

### Circuit Breaker State

```
Key:    lb:cb:{pool_id}
Type:   Hash
TTL:    open_duration_seconds (auto-expires to HALF_OPEN)
Fields:
  state         → "CLOSED" | "OPEN" | "HALF_OPEN"
  opened_at     → unix_ms
  error_count   → counter in current window
  total_count   → counter in current window
```

### Sticky Session Mappings

```
Key:    lb:session:{session_id}
Type:   String → backend_id
TTL:    ttl_seconds from session affinity config (e.g., 3600s)
```

### Rate Limit Counters (Token Bucket)

```
Key:    lb:rl:{policy_id}:{scope_key}
Type:   Hash
TTL:    window_seconds × 2 (sliding expiry)
Fields:
  tokens        → current token count (float, stored as integer × 1000)
  last_refill   → unix_ms of last token refill
```

### Backend Connection Counter

```
Key:    lb:conns:{backend_id}
Type:   String (atomic integer)
TTL:    None
Operations: INCR on accept, DECR on close
Used for LEAST_CONNECTIONS algorithm
```

---

## BigQuery — Access Logs & Analytics

### `lb_access_logs` table (partitioned by day)

```sql
CREATE TABLE lb_access_logs (
    req_timestamp       TIMESTAMP   NOT NULL,   -- Partition column
    request_id          STRING,
    src_ip              STRING,
    src_port            INT64,
    edge_region         STRING,                 -- "us-central1", "eu-west1"
    http_method         STRING,
    host                STRING,
    path                STRING,
    query_string        STRING,
    http_version        STRING,
    tls_version         STRING,
    request_bytes       INT64,
    response_status     INT64,
    response_bytes      INT64,
    backend_id          STRING,
    backend_address     STRING,
    pool_id             STRING,
    rule_id             STRING,
    lb_latency_ms       FLOAT64,               -- Time spent in LB (not backend)
    total_latency_ms    FLOAT64,               -- End-to-end
    backend_latency_ms  FLOAT64,
    session_id          STRING,
    rate_limited        BOOL,
    circuit_opened      BOOL
)
PARTITION BY DATE(req_timestamp)
CLUSTER BY edge_region, pool_id, response_status;
```

**Retention Policy:**
- Hot (BigQuery standard): 30 days
- Cold (GCS Coldline): 12 months
- Archive (GCS Archive): 7 years (compliance)

---

## Data Lifecycle

```
Config data (Cloud SQL):
  - Soft-deleted (status = 'DELETED') for 30 days
  - Hard-purge after 30 days via Cloud Scheduler job

Redis hot state:
  - Health state: no TTL, overwritten by health loop every 5s
  - Session affinity: TTL per policy (default 3600s)
  - Rate limit counters: TTL = window × 2
  - Stale backend keys: cleaned up within 60s of backend deletion via pub/sub event

BigQuery logs:
  - Streamed in real-time via Cloud Pub/Sub → Dataflow → BigQuery
  - 30-day partition expiry on hot table
  - Partitions moved to GCS after 30 days via scheduled export
```

---

## Caching Strategy

| Data | Cache Layer | TTL | Invalidation |
|------|------------|-----|-------------|
| Pool + backend config | In-process memory (LRU, per LB node) | 30s | Pub/Sub config change event |
| Routing rules | In-process memory (sorted by priority) | 30s | Pub/Sub rule change event |
| Health status | Redis | No TTL (live) | Written every 5s by health checker |
| SSL cert handles | In-process (OpenSSL ctx) | Until cert rotation | Certificate rotation event |
| Rate limit state | Redis | window × 2 | Natural expiry |
| Sticky sessions | Redis | Per-policy TTL | Natural expiry or explicit DELETE |
