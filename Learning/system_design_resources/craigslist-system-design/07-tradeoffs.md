# 7. Trade-off Discussion

---

## 7.1 Architecture Trade-offs

### Microservices vs Monolith

| Dimension | Microservices (Chosen) | Monolith |
|-----------|----------------------|----------|
| Scalability | Scale per service independently | Scale whole app together |
| Deployment | Deploy individual services | Single deployment unit |
| Complexity | Higher — service mesh, network calls | Lower — in-process calls |
| Fault isolation | Failure in one service doesn't cascade | One bug can bring down all |
| Team ownership | Clear service boundaries | Shared codebase |
| Latency | Added network hops between services | In-process, < 1ms |
| **Verdict** | ✅ Better for Craigslist scale (50M MAU) | Good for early-stage only |

**Decision rationale:** At 50M MAU with wildly different scaling needs (Search: 350 RPS vs Notification: 58/sec), independent scaling per service saves compute cost and allows different languages/stacks per team.

---

### PostgreSQL (Cloud SQL) vs NoSQL (Firestore / Bigtable)

| Dimension | PostgreSQL (Chosen) | Firestore/NoSQL |
|-----------|--------------------|--------------------|
| Data model | Relational — strong FK constraints | Document / Key-value |
| Query flexibility | Ad-hoc SQL, complex joins | Limited queries |
| ACID compliance | Full ACID per transaction | Limited transactions |
| Schema evolution | Requires migrations | Schema-free |
| Scaling | Vertical + read replicas | Horizontal, near-infinite |
| Geo search | PostGIS extension (excellent) | Limited |
| **Verdict** | ✅ Suitable for listings and users | Consider for user sessions only |

**Decision rationale:** Listing data is inherently relational (listing → user, listing → images, listing → flags). PostgreSQL with partitioning handles our 220 GB dataset efficiently. Cloud Spanner added for global distribution.

---

### Cloud Spanner vs PostgreSQL Sharding

| Dimension | Cloud Spanner (Chosen for global) | Manual Sharding |
|-----------|----------------------------------|-----------------|
| Operational overhead | Managed — zero ops | High — shard management |
| Global strong consistency | ✅ TrueTime-based | ❌ Complex to achieve |
| Cost | Expensive (~$0.90/node/hour) | Cheaper compute |
| Query language | Standard SQL | Standard SQL |
| Latency | < 10ms same region, ~100ms global | < 5ms same region |
| **Verdict** | ✅ For global listing reads | Overkill for single-region |

**Decision rationale:** Craigslist operates in 700+ cities including non-US cities. Cloud Spanner multi-region (nam6) allows low-latency reads from both US coasts while maintaining strong consistency for listing mutations.

---

### Elasticsearch vs Algolia vs Cloud Search

| Dimension | Elasticsearch (Chosen) | Algolia | Cloud Search |
|-----------|----------------------|---------|--------------|
| Full-text quality | Excellent | Excellent | Good |
| Geo search | ✅ Native, powerful | ✅ Good | Limited |
| Faceted search | ✅ Aggregations | ✅ | Limited |
| Cost | Self-managed GCE cost | Very expensive at scale | Moderate |
| Control | Full DSL control | Limited customization | Limited |
| Operational burden | Medium (manage nodes) | Zero | Low |
| At 45M docs | ~$800-1500/month | ~$10,000+/month | ~$3,000/month |
| **Verdict** | ✅ Best cost/features at this scale | Too expensive | Insufficient geo |

---

### Synchronous vs Asynchronous Search Indexing

| Dimension | Async (Chosen via Pub/Sub) | Sync (in-request indexing) |
|-----------|--------------------------|---------------------------|
| Listing create latency | Fast (< 200ms — no ES wait) | Slow (+ 500ms ES indexing) |
| Search freshness | Up to 30s delay | Immediate |
| Resilience | ES outage doesn't block creates | ES outage blocks all posts |
| Complexity | Higher (Pub/Sub consumer) | Simpler |
| **Verdict** | ✅ Acceptable for classifieds | Unnecessary coupling |

**Decision rationale:** A 30-second search indexing delay is completely acceptable for a classifieds platform. Users won't notice. The benefit — decoupling listing creation from search — prevents cascading failures.

---

### Cache Strategy: Cache-Aside vs Write-Through

| Dimension | Cache-Aside (Chosen) | Write-Through |
|-----------|---------------------|---------------|
| Cache management | App manages cache population | Cache auto-populated on writes |
| Cache miss penalty | First read hits DB (cold start) | No cold start |
| Stale data risk | Higher (TTL-based expiry) | Lower |
| Simplicity | Moderate | Simple |
| Flexibility | Write only what's needed | All writes go to cache |
| **Verdict** | ✅ Better for read-heavy listings | Wastes cache space |

**Chosen TTLs:**
- Hot listing: 10 minutes (accept slight staleness)
- Category tree: 1 hour (rarely changes)
- Search results: 5 minutes (accept eventual freshness)
- Sessions: 1 hour sliding

---

## 7.2 Data Consistency Trade-offs

### CAP Theorem Position

```
Craigslist is a classifieds platform — not a bank.
We choose: Availability + Partition Tolerance (AP)

  Listings:
    - Strong consistency on CREATE (idempotency key prevents duplicates)
    - Eventual consistency on SEARCH (30s delay acceptable)
    - Read-your-writes for listing owner (cache with userId key)

  Search:
    - Eventual consistency acceptable
    - Users expect search to be "close enough"
    - CAP: Availability over Consistency

  User Auth:
    - Strong consistency required (can't login with deleted account)
    - CAP: Consistency over Availability here
```

---

## 7.3 Scalability Trade-offs

### Read Replica Strategy for PostgreSQL

```
Option A: Single Primary (rejected — SPOF, can't scale reads)
Option B: Primary + 2 Read Replicas (chosen)
  └── Listing Service reads from read replica
  └── Writes to primary only
  └── Replication lag: < 100ms (acceptable)
  └── Cost: 3× Cloud SQL instance

Option C: Cloud Spanner (for global scale)
  └── Used for global listing distribution
  └── Higher cost but eliminates replica management
```

---

## 7.4 Image Storage Trade-offs

### Direct Upload vs Proxy Upload

| Dimension | Client → GCS Direct (Chosen) | Client → API → GCS |
|-----------|------------------------------|-------------------|
| API server bandwidth | Zero — images bypass API | All images through API |
| API server load | Low | High (I/O bound) |
| Security | Pre-signed URL limits scope | API can validate each upload |
| Complexity | Moderately complex | Simple |
| Cost | Lower (no API egress) | Higher (API bandwidth) |
| **Verdict** | ✅ Scales to 15 TB/day without changing APIs | Would saturate API servers |

---

## 7.5 Rate Limiting Trade-offs

### Per-IP vs Per-Account Rate Limiting

```
Per-IP only (rejected):
  ❌ Shared IPs (offices, universities) block legitimate users
  ❌ VPN/proxy bypass

Per-Account only (rejected):
  ❌ New accounts created to bypass limits
  ❌ Anonymous browsing not rate-limited

Both (chosen):
  ✅ Per-account: 5 posts/day (hard limit)
  ✅ Per-IP: 1 post/hour (soft limit — catch bots)
  ✅ CAPTCHA on first post from new account
  ✅ Phone verification for categories prone to spam (jobs, housing)
```

---

## 7.6 Summary of Key Decisions

| Decision | Choice | Alternative Considered | Reason |
|----------|--------|----------------------|--------|
| Architecture | Microservices | Monolith | Scale, fault isolation |
| Primary DB | PostgreSQL | MongoDB, Firestore | ACID, relational data |
| Global DB | Cloud Spanner | Sharded Postgres | Managed, strong consistency |
| Search | Elasticsearch | Algolia | Cost at scale, geo power |
| Cache | Redis (Memorystore) | Memcached | Richer data structures |
| Message bus | Cloud Pub/Sub | Kafka | Managed, GCP native |
| Auth | Firebase Auth | Custom JWT | Managed, OAuth support |
| Image storage | Cloud Storage (GCS) | GCE block storage | Object store, CDN integration |
| Indexing | Async (Pub/Sub) | Sync in-request | Resilience, latency |
| Upload | Pre-signed URL (GCS direct) | Proxy through API | Bandwidth cost |
