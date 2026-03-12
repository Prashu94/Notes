# 08 — Failure Scenarios & Mitigation

## System: Photo Sharing Service (Instagram-Scale)

---

## Failure 1: CDN Outage / Major PoP Failure

### Detection
- Cloud Monitoring: CDN cache hit rate drops from 95% → < 50%
- Synthetic monitoring (Cloud Monitoring Uptime Checks) from 10 global probes → failures in specific regions
- P99 photo load latency spikes from 100ms → > 2000ms
- Alert: PagerDuty → on-call SRE within 2 minutes

### Impact
| What breaks | What still works |
|-------------|-----------------|
| Photo rendering across affected region | Feed fetching (content IDs still load) |
| Avatar images | Post creation (upload goes to GCS directly) |
| Video playback | Likes, comments, follows |
| CDN-served static assets (JS/CSS for web) | Native apps (cached assets) |

### Mitigation
1. **Immediate**: CDN automatically routes requests to nearest healthy PoP (Cloud CDN's Anycast routing handles this transparently)
2. **Traffic shift**: Update Cloud Load Balancer backend policy to serve media directly from GCS origin for affected region
3. **Cache-Control headers**: Photos already have long TTLs cached on clients (7-day cache header) — most users unaffected
4. **Origin shield**: If origin load spikes, enable Cloud CDN origin shield to aggregate origin requests

### Prevention
- Multi-CDN strategy: CloudFlare as secondary CDN for failover (in roadmap)
- Client-side retry with exponential backoff for failed image loads
- Lazy loading: feed content loads text-first, images deferred

### RTO / RPO
- **RTO**: 2 minutes (automatic PoP rerouting by Cloud CDN)
- **RPO**: N/A — CDN is stateless; no data loss

---

## Failure 2: Primary Database (Cloud SQL) Failure

### Detection
- Cloud SQL internal health check → automatic failover trigger
- App-level: connection errors in posts/comments service
- SLO breach: error rate > 0.1% on POST /posts → PagerDuty alert

### Impact
| What breaks | What still works |
|-------------|-----------------|
| New post creation | Feed reading (Redis cache serves all reads) |
| Comment writes (new) | Like/unlike (Bigtable + Redis) |
| Profile edits | Follow/unfollow (Cloud Spanner separate) |
| User registration | Content viewing (CDN + Redis) |

### Mitigation
1. **Automatic HA failover**: Cloud SQL HA instance promotes standby in same region in ~60 seconds
2. **Read replicas**: Read traffic automatically routes to regional replicas; no action needed
3. **Connection pooling (pgBouncer)**: Prevents connection storm during failover; pool exhaustion avoided
4. **Application retry**: Services implement retry with 3× exponential backoff for `connection_refused` errors
5. **Circuit breaker**: Envoy sidecar trips after 5 consecutive failures → stops hammering dead primary → directs write traffic to queue (Cloud Tasks) for delayed retry

### Prevention
- Cloud SQL HA with automatic failover configured
- Regular failover drills (quarterly chaos engineering)
- Database connection pool pre-warming to avoid cold start

### RTO / RPO
- **RTO**: 60–90 seconds (automatic Cloud SQL HA failover)
- **RPO**: < 5 seconds (synchronous replication to standby in same zone)

---

## Failure 3: Redis (Feed Cache) Failure / Eviction Storm

### Detection
- Memorystore monitoring: memory usage > 90% → eviction rate spikes
- App-level: Feed service cache miss rate spikes from 5% → 80%
- Feed service p99 latency: 200ms → 3000ms (fallback to on-read generation)
- Alert: "Cache miss rate > 50% for 5 minutes" → PagerDuty

### Impact
| What breaks | What still works |
|-------------|-----------------|
| Fast feed serving (100M cache hits/day affected) | Feed is still served (falls back to on-read) |
| Like count reads (stale for all users) | Post creation, uploads |
| Session cache (users must re-authenticate) | Follow, comments |

### Mitigation
1. **Redis HA (Memorystore Standard)**: Automatic failover to replica in < 30 seconds; minimal impact
2. **Cache stampede prevention**: Use probabilistic early expiration + Redis SETNX locks to prevent thundering herd on cold start
3. **Graceful degradation**: Feed service has code path for on-read fan-out when Redis miss ratio > 60% — serve correct feeds, just with higher latency
4. **LRU eviction policy**: Redis configured with `allkeys-lru` — most stale caches evicted first
5. **Feed cache warm-up job**: On Redis restart, a Cloud Run job pre-warms feed caches for top-1000 most active users

### Prevention
- Memorystore Standard HA with automatic replica promotion
- Redis memory allocated at 125% of expected working set (do not over-pack)
- Key expiry spread via random jitter (prevent synchronized expiry waves)
- Monitor keyspace hits/misses via Memorystore metrics dashboard

### RTO / RPO
- **RTO**: 30 seconds (Memorystore HA failover)
- **RPO**: Up to 30 seconds of like counter increments lost → reconciled from Bigtable on recovery

---

## Failure 4: Media Processing Worker Backlog (Upload Spike)

### Detection
- Pub/Sub `media.uploaded` topic: undelivered message count > 10,000
- Media workers (Cloud Run): concurrency maxed at 500 instances
- User-facing: Post creation stuck in "processing" state > 2 minutes
- Alert: "Pub/Sub backlog > 5,000 messages for > 2 minutes"

### Impact
| What breaks | What still works |
|-------------|-----------------|
| New posts not becoming visible (stuck "processing") | Photo uploads succeed (GCS write succeeds) |
| Explore/feed showing fewer new posts | All reads: feed, comments, likes |
| CDN cache not populated for new media | Follow, user management |

### Mitigation
1. **Cloud Run autoscaling cap increase**: Temporarily raise max instances 500 → 1000 (Cloud Run concurrency is the limit, not compute)
2. **Priority queue**: High-priority topic for regular users, low-priority for bulk/backfill operations
3. **Message TTL**: Pub/Sub messages expire after 1 hour; if processing takes longer, the upload is considered failed and user is notified to retry
4. **Client polling**: Mobile app polls `GET /v1/media/{id}/status` every 5s — user sees progress; doesn't perceive total failure
5. **Partial visibility**: Post caption and location are indexed immediately; only photo not visible → "Photo processing..." placeholder shown

### Prevention
- Pre-warm 50 Cloud Run instances during predicted high-traffic events (Super Bowl, major holidays)
- Horizontal scaling: Cloud Run scales to 1000 instances by default; increase quota with GCP support
- Autoscaling trigger: scale out when Pub/Sub backlog > 1,000 messages

### RTO / RPO
- **RTO**: 5 minutes (Cloud Run scale-out + backlog drain)
- **RPO**: No data loss — GCS upload succeeded; just processing delayed

---

## Failure 5: Cloud Spanner Follow Graph Latency Spike

### Detection
- Cloud Spanner metrics: p99 latency > 100ms (normal < 10ms)
- Fan-out Worker: feed generation taking > 2 seconds
- Alert: "Spanner p99 > 50ms for 5 minutes"

### Impact
| What breaks | What still works |
|-------------|-----------------|
| Feed generation for cold cache users (slower) | Feed for users with warm Redis cache (~95%) |
| New-follow feed backfill (delayed) | All reads from feed cache |
| Like/comment access control (private accounts slower) | Public post viewing |

### Mitigation
1. **Read replicas**: Cloud Spanner automatically routes read-only queries to nearest replica — check if stale reads are enabled
2. **Enable stale reads**: For non-access-control queries (e.g., fan-out for feed), use `read_timestamp = now() - 15s` — dramatically reduces latency
3. **Follow list cache**: Cache follower lists in Redis for 5 minutes for the fan-out worker (TTL-based invalidation on follow/unfollow)
4. **Rate-limit fan-out**: If Spanner is degraded, slow down fan-out worker (process at 50% normal rate) — feed update just delayed

### Prevention
- Cloud Spanner node count: 10 nodes provides ~10,000 reads/sec; add nodes if sustained > 70% utilization
- Use `partitionRead` for large follower list scans (bulk operations)
- Separate node pools for OLTP (follow checks) vs OLAP (analytics fan-out reads)

### RTO / RPO
- **RTO**: Automatic — Spanner self-heals; SRE adds nodes if sustained
- **RPO**: N/A — Spanner is always consistent; no data loss scenario

---

## Failure 6: Like Counter Divergence (Redis ↔ PostgreSQL Desync)

### Detection
- Reconciliation job (runs every 6 hours): compares Redis count vs Bigtable actual likes
- Discrepancy > 5% → alert
- Example: Redis says post has 1,000 likes; Bigtable has 1,050 actual like records

### Impact
- Like counts shown to users are incorrect (off by small margin)
- No functional failure — just data quality issue

### Mitigation
1. **Reconciliation Job** (Cloud Scheduler, every 6h):
   ```
   For each post with dirty counter:
     actual_count = COUNT(*) FROM bigtable WHERE post_id=X AND action='like'
     redis.set(likes:count:{post_id}, actual_count)
     UPDATE posts SET like_count = actual_count WHERE id = X
   ```
2. **Redis crash recovery**: On startup, seed Redis counters from PostgreSQL `like_count` column
3. **Write-through for high-value posts**: Top 1% of posts (> 100K likes) get synchronous write-through to PostgreSQL on every like

### Prevention
- Bigtable-first writes: Bigtable write is the primary; Redis is always derived
- Periodic audit log: daily BigQuery job compares all three stores' like counts

### RTO / RPO
- **RTO**: Immediate — like counts may be slightly wrong but system functions
- **RPO**: 30 seconds of counter drift maximum; Bigtable row history is the ground truth

---

## Failure 7: Media Upload Abuse / DDoS via Presigned URLs

### Detection
- GCS bucket monitoring: unusual ingress spike from single IP range
- Cloud Armor: rate limit triggers at 10K requests/IP/min
- Presigned URL issuance rate per user: > 10/hour → block

### Impact
- Storage cost spike (100TB uploaded in minutes)
- Media processing worker overload

### Mitigation
1. **GCS Object Lifecycle**: Objects not converted to posts within 1 hour → automatically deleted
2. **Per-user upload quota**: Max 10 presigned URLs per hour enforced server-side
3. **File size cap**: GCS signed URL content-length-range header: {min: 1, max: 20971520} (20MB)
4. **Cloud Armor rate limiting**: Block source IPs issuing > 100 upload requests/min
5. **Async CSAM scan**: Malicious content detected and purged within 90 seconds

### Prevention
- Presigned URL includes `x-goog-user-id` custom metadata → audit trail
- GCS bucket does NOT have public `requester-pays` — all costs borne by account
- Firebase App Check to verify legitimate app clients before URL issuance

---

## Disaster Recovery Plan

| Scenario | RTO | RPO | Recovery Steps |
|----------|-----|-----|----------------|
| Single AZ failure | < 1 min | 0 | GCP auto-reroutes; no action needed |
| Regional failure | < 5 min | < 30s | GCLB failover to secondary region |
| GCS bucket corruption | < 1 hr | 0 | Object versioning; restore from version history |
| Cloud SQL regional loss | < 5 min | < 30s | Promote cross-region read replica to primary |
| Full region loss (us-central1) | < 15 min | < 1 min | Promote EU region; update DNS |
| Security breach (DB access) | < 1 hr | 0 | Rotate credentials via Secret Manager; audit logs |

---

## Chaos Engineering Runbook

| Test | Frequency | Expected Behavior |
|------|-----------|-------------------|
| Kill all Feed Service pods in us-central1 | Monthly | GKE restarts pods in < 60s; EU region absorbs traffic |
| Flush Redis feed cache entirely | Quarterly | Feed service falls back to on-read; latency degrades gracefully |
| Cloud SQL failover simulation | Quarterly | HA promotes in < 90s; error rate stays < 0.1% |
| Media processing workers killed mid-batch | Monthly | Pub/Sub re-delivers; no duplicate posts |
| Spike 10× upload traffic | Quarterly | Cloud Run scales out; GCS handles surge; backlog clears in < 5 min |
