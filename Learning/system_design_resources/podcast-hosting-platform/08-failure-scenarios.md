# Failure Scenarios — Podcast Hosting Platform

> For each scenario: **Detection → Impact → Mitigation → Prevention → RTO/RPO**

---

## Failure 1: CDN Outage (Cloud CDN Partial or Full)

### Description
Cloud CDN nodes in one or more regions stop serving requests. This is the most impactful failure given that 95% of audio traffic flows through CDN.

### Detection
- **Cloud Monitoring alert**: CDN cache hit ratio drops below 80% for any region
- **Synthetic monitoring**: Canary client tries to fetch a known audio segment every 30 seconds from US, EU, APAC PoPs
- **User-visible errors**: Stream start failures spike >2% (alert on error rate, not absolute count)
- **Mean time to detect**: <2 minutes

### Impact Assessment
| Component | Impact |
|-----------|--------|
| Audio streaming | ❌ Critical — 18.75M concurrent listeners lose playback |
| API calls | ✅ Unaffected — API routes through Cloud LB, not CDN |
| RSS feeds | ⚠️ Degraded — RSS served from CDN cache misses → RSS Service directly |
| Uploads | ✅ Unaffected |
| Live streaming | ❌ Degraded — live HLS manifests served from CDN |

### Mitigation (Immediate Actions)
1. **Auto-failover**: Cloud LB with backup origin pool. If CDN is misconfigured, GCS presigned URLs can be served directly (at much higher egress cost).
2. **Circuit breaker**: Streaming Service detects CDN failures; switches to direct GCS signed URL serving for new streams (bypasses CDN)
3. **Client retry**: Mobile clients retry with exponential backoff (up to 5 attempts) before surfacing an error
4. **Incident response**: Page on-call SRE via PagerDuty; GCP support ticket for CDN incident

### Prevention
- **Multi-CDN strategy**: Use Cloud CDN as primary + Fastly/Akamai as secondary (automatic failover via Traffic Director)
- **Health checks**: CDN origin health checks configured; Cloud Armor policy stays active on backup path
- **Regular DR drills**: Quarterly CDN failover drill to validate backup path works

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO (streaming restored) | < 5 minutes (auto-failover to backup CDN or direct origin) |
| RPO | Zero — no data loss in a CDN failure |

---

## Failure 2: Cloud Spanner Overload / Unavailability

### Description
Cloud Spanner (podcast + episode metadata) experiences high latency or becomes unavailable due to hotspot, misconfiguration, or regional fault.

### Detection
- **Spanner metrics**: Latency p99 > 50ms fires alert (normal is <10ms)
- **Spanner metrics**: CPU utilization > 65% on any node
- **Application error rate**: 5xx errors spike on any endpoint that reads episode metadata
- **Cloud Monitoring**: Spanner instance availability < 100%

### Impact Assessment
| Component | Impact |
|-----------|--------|
| Streaming (episode metadata) | ❌ Cannot validate premium access → fail open or fail closed? |
| RSS Service | ❌ Cannot regenerate feeds on cache miss |
| Upload Service | ❌ Cannot write new episodes |
| Analytics | ✅ Pub/Sub based — unaffected |
| Social / Payment | ✅ PostgreSQL based — unaffected |

### Mitigation
1. **Fail open for streaming** (not fail closed): If Spanner is unavailable, allow streaming for non-premium episodes to preserve listener experience. Premium check: serve cached access token from Redis for up to 1 hour.
2. **Read replica**: Use Spanner read pool. Long-tail queries use stale reads (up to 15-second staleness) to avoid contention.
3. **Redis fallback**: Most episode metadata is cached in Redis. On Spanner hiccup, Redis serves all reads for up to 10 minutes.
4. **Upload queue**: Episode creates queue in Cloud Tasks. If Spanner write fails, Task retries with exponential backoff for 1 hour.

### Prevention
- **Key design**: UUID primary keys (no sequential IDs → no hotspots)
- **Interleaved tables**: Episodes interleaved under Podcasts — query fan-out minimized
- **Load test**: Chaos engineering runs quarterly to simulate Spanner latency injection
- **Capacity**: Maintain 50% CPU headroom; scale up proactively at 65% utilization

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO (reads) | ~0 — Redis cache serves for 10 min without Spanner |
| RTO (writes) | < 60 min — Cloud Tasks retries episode creates |
| RPO | Zero — Spanner is synchronously replicated; no data loss |

---

## Failure 3: Upload Service Failure

### Description
The Upload Service pods crash or become unresponsive. Creators cannot upload new episodes.

### Detection
- **Kubernetes**: Pod crash-loop alerts via Cloud Monitoring
- **Apigee**: 5xx error rate on `/v1/podcasts/*/episodes/upload-url` > 1%
- **Synthetic test**: Canary upload probe runs every 5 minutes

### Impact Assessment
| Component | Impact |
|-----------|--------|
| New episode uploads | ❌ Creators cannot start new uploads |
| Existing in-progress uploads | ⚠️ GCS resumable sessions survive — clients can resume when service restores |
| Streaming / Listening | ✅ Completely unaffected |
| Analytics / Social | ✅ Unaffected |

### Mitigation
1. **GKE auto-restart**: Kubernetes restarts crashed pods; health checks route traffic only to ready pods
2. **Pre-signed URL durability**: Once a GCS signed URL is issued, the upload can complete even if the Upload Service crashes. Clients upload directly to GCS.
3. **Graceful degradation message**: If upload-url endpoint fails, return a friendly error message with retry-after header (not a bare 503)
4. **Scale-up**: HPA (Horizontal Pod Autoscaler) scales Upload Service pods based on CPU + request rate

### Prevention
- **Stateless design**: Upload Service is fully stateless (state in GCS + Spanner)
- **Rolling deployments**: K8s rolling updates; never take all pods down simultaneously
- **Bulkhead**: Upload Service is isolated from Streaming Service in separate GKE deployments; a crash in Upload doesn't affect streaming

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO | < 2 minutes (Kubernetes auto-restart) |
| RPO | Zero — uploads are to GCS directly; no data in the pod |

---

## Failure 4: Analytics Pipeline Lag

### Description
Pub/Sub → Dataflow → BigQuery pipeline experiences lag. Dashboards show stale data.

### Detection
- **Pub/Sub**: Message age (oldest unacknowledged message) > 10 minutes fires alert
- **Dataflow**: Pipeline latency metric > 10 minutes
- **BigQuery ingestion lag**: Streaming buffer last-updated > 10 minutes
- **Dashboard**: Creator sees "Data as of Xm ago" banner when last_updated > 5 min

### Impact Assessment
| Component | Impact |
|-----------|--------|
| Creator analytics dashboards | ⚠️ Stale data (explicitly in SLO: 5 min lag acceptable) |
| Audio streaming | ✅ Fully unaffected |
| Ad impression counting | ⚠️ Delayed (but idempotent — not lost) |
| RSS feeds | ✅ Unaffected |
| Payments | ✅ Revenue calculations run weekly — short-term lag irrelevant |

### Mitigation
1. **Pub/Sub replay**: Events are retained for 7 days. Once Dataflow recovers, it replays from last committed offset — no data loss.
2. **Dataflow auto-scale**: Dataflow automatically adds workers when parallelism backlog grows. Alert fires at 10 min lag; auto-scale resolves within 5 min.
3. **Dead-letter queue**: Malformed events that fail to parse are routed to `play-events-dlq` Pub/Sub topic for investigation, not dropped.
4. **Dashboard freshness indicator**: UI always shows "Last updated: X minutes ago" so creators know data lag.

### Prevention
- **Dataflow backpressure**: Pipelines configured with max parallelism = 500 workers
- **Pub/Sub throughput**: Pre-provisioned topic throughput at 200,000 msg/sec (3× expected peak)
- **Schema registry**: Analytics events schema validated server-side before publishing to Pub/Sub; malformed events rejected at ingest

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO (dashboard data current) | < 15 minutes after Dataflow restarts |
| RPO | Zero — 7-day Pub/Sub replay buffer |

---

## Failure 5: Live Stream Interruption (Creator Side)

### Description
Creator's RTMP/WebRTC connection drops mid-stream. Thousands of listeners are actively listening.

### Detection
- **Media server**: No RTMP data received for 3 seconds → stream considered interrupted
- **Firestore**: Stream status updated to `interrupted` (real-time push to listeners)
- **HLS manifest**: No new segments added for 5 seconds → players detect stall

### Impact Assessment
| Component | Impact |
|-----------|--------|
| Active live listeners | ❌ Stream stalls; client shows reconnecting... |
| Future listeners (VOD) | ✅ Recording up to dropout point is saved |
| Creator | ⚠️ 30-second grace window to reconnect |

### Mitigation
1. **30-second reconnect buffer**: Media server holds last segment and waits for up to 30 seconds for creator to reconnect with same stream key. Listeners see "Reconnecting..." UI via Firestore real-time update.
2. **Seamless recovery**: If creator reconnects within 30s, stream resumes without audience gap. HLS manifest stitches segments seamlessly.
3. **Graceful end**: If no reconnect within 30s, live stream ends. Recording finalizes and transcript job is queued.
4. **Listener fallback**: Listeners are offered to listen from beginning (VOD) if they missed content.

### Prevention
- **WebRTC TURN relay**: Ensures creator connection works even behind strict firewalls/NAT
- **Client-side preflight**: Creator's browser runs pre-stream connectivity test (bandwidth, latency, microphone) before going live
- **Redundant ingest**: Support dual RTMP push to two media servers; failover if primary drops

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO (seamless recovery) | < 1 second if reconnect within 30s |
| RTO (stream end) | 30 seconds after connection loss |
| RPO (recording) | Loss of at most 30s at end of interrupted stream |

---

## Failure 6: Payment Service Failure (Stripe Outage)

### Description
Stripe API is unavailable or returns errors. Subscription renewals and tips fail.

### Detection
- **Stripe webhook**: No events received for >10 minutes (expected ~1000/min at scale) fires alert
- **Outbound Stripe calls**: P99 latency > 10s or error rate > 1% fires alert
- **Stripe status page**: Monitor via Stripe's operational status API

### Impact Assessment
| Component | Impact |
|-----------|--------|
| New subscriptions | ❌ Cannot process |
| Existing subscriptions (renewal) | ⚠️ Stripe retries automatically; grace period applies |
| Tips | ❌ Cannot process new tips |
| Episode access (paywall) | ✅ Active subscriptions validated from PostgreSQL — NOT re-checked via Stripe on every request |
| Creator payouts | ⚠️ Delayed — queued; Stripe Connect transfers processed when restored |

### Mitigation
1. **Stripe's own retries**: Stripe automatically retries failed payments for up to 4 days for subscriptions.
2. **Grace period**: Do NOT immediately revoke access on first payment failure. Allow 3-day grace period (Stripe's default dunning). Subscriber retains access.
3. **Queue tips**: If Stripe is down, queue tip requests in Cloud Tasks with 24-hour retry window. Show "Your tip is processing" in UI.
4. **Idempotency keys**: All Stripe API calls include `Idempotency-Key: {tip_id}` or `{subscription_id}` — safe to retry without double charging.

### Prevention
- **Stripe webhook reliability**: Stripe retries webhooks for 72 hours. Webhook handler is idempotent.
- **PostgreSQL as source of truth**: Subscription status stored in PostgreSQL. Stripe is the billing system, not the access control system. Access check never calls Stripe in real-time.
- **Circuit breaker**: Stripe API client has circuit breaker. Open after 5 consecutive failures; half-open after 60 seconds.

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO (listener access) | Zero — managed by PostgreSQL grace period |
| RTO (new payments) | 0–4 hours typically (Stripe resolves) |
| RPO | Zero — no financial data loss; Stripe stores all records |

---

## Failure 7: Redis Cache Cluster Failure

### Description
Memorystore Redis cluster becomes unavailable. RSS feed cache, playback positions, and session cache are affected.

### Detection
- **Cloud Monitoring**: Redis connection refusals > 0/sec fires alert
- **Application errors**: Cache miss rate spikes to 100%
- **RSS Service**: Response times spike from <10ms to >500ms (DB queries)

### Impact Assessment
| Component | Impact |
|-----------|--------|
| RSS feeds | ⚠️ Served from Spanner (much slower, high load) |
| Playback positions | ⚠️ Position sync delayed; resumes from Spanner cold reads |
| Episode metadata cache | ⚠️ All requests go to Spanner |
| User sessions | ❌ Sessions invalidated; users logged out |
| Live viewer counts | ❌ Counter lost |

### Mitigation
1. **Redis HA cluster**: Memorystore deployed as Redis HA Cluster (primary + replica per shard). Automatic failover in <60 seconds.
2. **Soft degradation**: RSS Service falls back to Spanner direct with rate limiting (1,000 RPS max to protect Spanner)
3. **Session fallback**: JWT tokens are stateless (Firebase-signed). Session data in Redis is a cache; token itself is the session. Users don't get logged out.
4. **Write-through for positions**: On Redis failure, Streaming Service writes position directly to Spanner synchronously (slower but durable).

### Prevention
- **Redis persistence**: Enable AOF (Append-Only File) on Memorystore for position data recovery
- **Circuit breaker**: Application has Redis circuit breaker — on open state, bypass cache entirely
- **Warm-up**: After Redis recovery, warm cache by replaying top 1000 podcast feeds and hot episodes

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO | < 60 seconds (Redis HA automatic failover) |
| RPO | Up to 1 second of Redis AOF lag (position data), zero for session (JWT-based) |

---

## Failure 8: Elasticsearch Index Corruption / Unavailability

### Description
Elasticsearch cluster has shard failures or index becomes corrupted.

### Detection
- **ES cluster health**: Turns RED (unassigned primary shards) — alert immediately
- **Search API error rate**: > 5% fires alert
- **Index lag**: Episode published >60s but not searchable fires alert

### Impact Assessment
| Component | Impact |
|-----------|--------|
| Search | ❌ Return empty results or 503 |
| Transcript search | ❌ Unavailable |
| Core streaming, upload, payments | ✅ Fully unaffected |

### Mitigation
1. **Graceful degradation**: Search endpoint returns HTTP 503 with a clear message. Podcast discovery falls back to "trending" list from BigQuery ← pre-computed, unaffected by ES.
2. **Shard replication**: ES configured with 1 primary + 2 replicas per shard. Single-node failure doesn't cause RED status.
3. **Reindex from Spanner**: If corruption is severe, Dataflow job re-indexes all 50M episodes from Spanner source of truth within ~4 hours.

### Prevention
- **Regular snapshots**: Daily ES snapshots to GCS. Can restore within 1 hour.
- **Rolling upgrades**: ES version upgrades done rolling (1 node at a time)

### RTO / RPO
| Metric | Target |
|--------|--------|
| RTO (soft degradation) | < 2 minutes (circuit breaker to fallback) |
| RTO (full restore from snapshot) | < 1 hour |
| RPO | Up to 1 day of search index updates (snapshot period) |

---

## Failure Summary Matrix

| Failure | User Impact | Detection Time | Auto-Recovery? | RTO |
|---------|-------------|---------------|---------------|-----|
| CDN outage | Critical (no audio) | <2 min | ✅ Failover CDN | <5 min |
| Spanner overload | High (metadata fails) | <1 min | ✅ Redis cache | <2 min |
| Upload service crash | Low (new uploads only) | <1 min | ✅ K8s restart | <2 min |
| Analytics lag | Minimal (dashboard stale) | <10 min | ✅ Pub/Sub replay | <15 min |
| Live stream drop | High (live listeners) | <3 sec | ✅ Creator reconnect | <30 sec |
| Stripe outage | Medium (new payments) | <10 min | ✅ Stripe's retries | <4 hr |
| Redis failure | Medium (cache miss perf) | <1 min | ✅ HA failover | <60 sec |
| Elasticsearch down | Low (search only) | <1 min | ✅ Graceful degrade | <2 min |
