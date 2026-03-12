# Trade-offs — Podcast Hosting Platform

> Every major design decision explained with alternatives, pros/cons, and a clear verdict.

---

## Trade-off 1: Geographic Deployment Strategy

This was explicitly requested — full analysis of all three options.

### Single Region (`us-central1`) vs Multi-Region vs Global Active-Active

| Dimension | Single Region | Multi-Region (US+EU) | Global Active-Active (4 regions) |
|-----------|:---:|:---:|:---:|
| API Latency (US users) | ✅ <20ms | ✅ <20ms | ✅ <20ms |
| API Latency (EU users) | ❌ 150-200ms | ✅ <30ms | ✅ <20ms |
| API Latency (APAC users) | ❌ 200-300ms | ❌ 150ms | ✅ <50ms |
| Audio Latency (all) | ✅ <2s via CDN | ✅ <2s via CDN | ✅ <2s via CDN |
| Availability | ❌ Region failure = full outage | ✅ Region failure = degraded | ✅✅ N-2 failure tolerance |
| Infrastructure Cost (relative) | $1x | $2x | $4-5x |
| GDPR Data Residency | ❌ Hard to comply | ✅ EU instance for EU users | ✅ Full compliance |
| Operational Complexity | ✅ Minimal | ☑️ Medium | ❌ Very high |
| Write Consistency | ✅ Strong | ☑️ Eventual (replication lag) | ✅ Strong (Spanner quorum) |
| Cross-region Write Latency | ✅ N/A | ☑️ N/A (writes go to leader) | ❌ ~100ms (2PC quorum) |
| Time to Market | ✅ Fastest | ☑️ Medium | ❌ Months of extra engineering |

**Key Insight — CDN Equalizer**: Audio streaming latency is CDN-bound, NOT compute-bound. Cloud CDN has 200+ PoPs globally. A single-region `us-central1` compute setup still delivers audio in <2s to APAC users via CDN. The only thing that degrades for non-US users in single-region is **API calls** (metadata fetches, login, progress syncs).

**GDPR Detail**: With multi-region, EU users' data is stored in `europe-west1`. With single-region, EU user data is stored in the US, requiring Standard Contractual Clauses (SCCs) and potentially conflicting with GDPR Chapter V transfer rules.

**Verdict**: 
- **MVP Launch**: Single Region (`us-central1`) — ship fast, validate product
- **50M+ MAU / EU users**: Multi-Region (US + EU) — GDPR compliance + EU latency
- **300M+ MAU / Spotify-scale**: Global Active-Active — 4 regions required

---

## Trade-off 2: HLS vs DASH for Audio Streaming

| Dimension | HLS (HTTP Live Streaming) | DASH (Dynamic Adaptive Streaming over HTTP) |
|-----------|--------------------------|---------------------------------------------|
| Browser support | ✅ Safari native; others via MSE | ✅ All modern browsers via MSE |
| iOS support | ✅ Native (required for App Store) | ❌ Requires 3rd-party library |
| Protocol | MPEG-TS or fMP4 segments | fMP4 segments only |
| Segment duration | ✅ Flexible (2–10s) | ✅ Flexible |
| DRM support | ✅ FairPlay (Apple) | ✅ Widevine (Google), PlayReady (Microsoft) |
| Low latency | ✅ HLS-LL (<10s) | ✅ DASH-LL (<10s) |
| CDN compatibility | ✅ Universal | ✅ Universal |
| Adaptive bitrate | ✅ Yes | ✅ Yes |
| Podcast industry standard | ✅ Dominant choice | ❌ Rarely used for podcasts |

**Verdict**: **HLS is primary, DASH is secondary**. iOS App Store rules require HLS for streaming >10 minutes. Podcast ecosystem (Apple Podcasts, Spotify) uses HLS. Provide DASH as a secondary option for Android/web clients where slightly better codec support matters.

---

## Trade-off 3: Server-Side Ad Stitching (SSAI) vs Client-Side VAST

| Dimension | Client-Side VAST | Server-Side Ad Stitching (SSAI) |
|-----------|-----------------|--------------------------------|
| Ad blocker bypass | ❌ Blocked by most ad blockers | ✅ Stitched into audio stream, unblockable |
| Implementation complexity | ✅ Simple (return VAST URL, client handles) | ❌ Complex (proxy all audio, stitch in real-time) |
| Transcoding cost | ✅ None | ❌ High — re-encode audio per-listener |
| Ad skip detection | ❌ Clients can skip trivially | ✅ Cannot skip stitched audio |
| Dynamic ad insertion | ✅ Yes | ✅ Yes |
| Personalization | ✅ Easy | ✅ Requires per-request stitching |
| Audio continuity | N/A | ✅ Seamless playback |
| Infrastructure cost | $ | $$$$  (audio proxy at scale = 18.75M concurrent) |
| Advertiser measurement | ☑️ JavaScript pixels | ✅ Server-confirmed impressions |
| Time to implement | ✅ Days | ❌ Months |

**Verdict**: **Client-Side VAST for MVP/Phase 2**. SSAI requires proxying 2.4 Tbps of audio through servers — at Spotify scale, this adds ~$10M/month in infrastructure and introduces a massive latency-sensitive proxy in the critical streaming path. SSAI is Phase 3 for top-tier monetization. Client-side VAST is standard in the industry (Spotify, Anchor, Buzzsprout all started this way).

---

## Trade-off 4: Push vs Pull RSS Feed Regeneration

| Dimension | Pull (Regenerate on Every Request) | Push (Regenerate on Episode Publish Event) |
|-----------|-----------------------------------|-------------------------------------------|
| Feed freshness | ✅ Always fresh | ☑️ Up to 5-min stale (per SLO) |
| Database read load | ❌ 43,400 req/sec × DB reads = huge | ✅ ~1 regeneration/publish event |
| Latency | ❌ High (DB query on every request) | ✅ Served from Redis cache <1ms |
| Cache complexity | ✅ Simple (just TTL-invalidate) | ☑️ Requires event-driven invalidation |
| Feed consistency | ✅ Perfect consistency | ☑️ Up to 5-min lag (within SLO) |
| CDN caching | ✅ Possible with short TTL | ✅ Natural fit |
| Cost | ❌ DB costs dominate | ✅ Near zero DB cost |

**Verdict**: **Event-driven (push) with Redis cache**. 5-minute feed staleness is explicitly in our SLO and acceptable for podcasts (listeners aren't checking the feed every minute). This reduces RSS-related DB load from 43,400 reads/sec to ~1-2 writes/sec (regenerations).

---

## Trade-off 5: Cloud Spanner vs PostgreSQL for Podcast Metadata

| Dimension | Cloud Spanner | Cloud SQL (PostgreSQL) |
|-----------|:---:|:---:|
| Horizontal scaling | ✅ Automatic, unlimited | ❌ Manual sharding or read replicas |
| Global distribution | ✅ Multi-region with strong consistency | ❌ Cross-region = replication lag |
| ACID transactions | ✅ Serializable | ✅ Serializable |
| SQL support | ☑️ Spanner SQL (not full PG compat) | ✅ Full PostgreSQL |
| Joins | ☑️ Supported, but prefer denormalization | ✅ Efficient with foreign keys |
| Cost | ❌ ~$0.90/node/hr, 10× PostgreSQL | ✅ ~$0.09/hr for db-custom-8-16384 |
| Interleaved tables | ✅ Co-located parent-child rows | ❌ N/A |
| ORM support | ☑️ Limited (custom adapters) | ✅ Excellent (SQLAlchemy, etc.) |
| Hotspot prevention | ✅ UUID keys auto-distribute | ❌ Sequential IDs create hotspots |
| Max rows per table | ✅ Billions, petabytes | ❌ ~1-5B rows before sharding needed |

**Verdict**: **Spanner for podcast/episode metadata, PostgreSQL for social/monetization**.
- Podcasts + Episodes: 50M+ episodes growing at 1M/day → Spanner is right choice
- Social graph (follows, comments): <1B rows, complex SQL queries → PostgreSQL is right choice
- The 10× cost difference is justified only where scale demands it

---

## Trade-off 6: Synchronous vs Asynchronous Transcription

| Dimension | Sync (Transcribe Before Episode Available) | Async (Transcribe After, Episode Playable Immediately) |
|-----------|:---:|:---:|
| User experience (creator) | ❌ 2+ hour wait to publish | ✅ Episode published instantly |
| User experience (listener) | ✅ Transcript ready at publish | ☑️ Transcript arrives up to 2h later |
| Infrastructure | ❌ Transcription blocks publish pipeline | ✅ Decoupled, independent scaling |
| Cost | Same | ✅ Can batch off-peak (cheaper) |
| Failure handling | ❌ Transcription failure delays publish | ✅ Transcription failure doesn't affect playback |
| Scalability | ❌ Publish throughput = transcription throughput | ✅ Independent scaling |

**Verdict**: **Async transcription always**. Blocking episode availability on a 2-hour API call is unacceptable UX. Display "Transcript coming soon" on the episode page. Notify creator via push when transcript is ready. This decouples two expensive operations entirely.

---

## Trade-off 7: Redis vs Persistent DB for Playback Positions

| Dimension | Redis Only | PostgreSQL/Spanner Only | Redis (hot) + Spanner (flush) |
|-----------|:---:|:---:|:---:|
| Write latency | ✅ Sub-millisecond | ❌ 5-50ms | ✅ Sub-millisecond |
| Durability | ❌ Memory, can lose data on restart | ✅ Durable | ✅ Eventual durability (5-min lag) |
| Consistency | ✅ Strong per-user | ✅ Strong | ☑️ 5-min eventual |
| Scale (6.25M concurrent writes) | ✅ handled | ❌ 208,333 writes/sec = kills Spanner | ✅ Only 20,833 writes/sec to Spanner |
| Cost | $ | $$$ | $$ |
| Cross-device sync | ✅ Yes (if shared key) | ✅ Yes | ✅ Yes (with flush delay) |

**Verdict**: **Redis for hot path, async flush to Spanner every 5 minutes**. 
208,333 writes/sec directly to Spanner would cost ~$2M/month in write units alone and introduce unacceptable latency. Redis handles this trivially. A 5-minute sync delay for playback position is imperceptible to users.

---

## Trade-off 8: Fan-out on Write vs Fan-out on Read (Activity Feed)

| Dimension | Fan-out on Write | Fan-out on Read |
|-----------|:---:|:---:|
| Feed read latency | ✅ O(1) — pre-computed | ❌ O(follows) — computed on request |
| Write amplification | ❌ 1 episode publish → 1M Redis writes if creator has 1M followers | ✅ 1 write to DB |
| Storage | ❌ N users × M activities = huge | ✅ Only store activities once |
| Celebrity problem (1M+ followers) | ❌ Critical bottleneck | ✅ Handles transparently |
| Stale feed risk | ✅ No (written at event time) | ☑️ Read join must be fast |
| Implementation complexity | ✅ Simple Redis lists | ☑️ Requires sorted merge on read |

**Verdict**: **Hybrid** — Fan-out on write for creators <100K followers (most creators). Fan-out on read for large creators (celebrities). This cuts Redis storage cost by 80% while still serving most users with O(1) feed reads.

---

## Trade-off 9: WebRTC vs RTMP for Live Stream Ingest

| Dimension | RTMP | WebRTC |
|-----------|:---:|:---:|
| Latency | ❌ 3-5 second ingest buffer | ✅ Sub-second |
| Browser support | ❌ Requires OBS/3rd party software | ✅ Native in Chrome, Firefox, Edge |
| Mobile support | ❌ Requires separate app/SDK | ✅ Native on iOS 15+, Android |
| Reliability | ✅ TCP-based, stable over bad networks | ❌ UDP-based, can drop under severe loss |
| Quality (audio bitrate) | ✅ Up to 320 kbps | ✅ Up to 256 kbps (Opus) |
| Server complexity | ✅ Nginx-RTMP is well-understood | ❌ Requires SFU (mediasoup/Janus) |
| Industry adoption | ✅ YouTube Live, Twitch ingest | ✅ Growing (Clubhouse, Twitter Spaces) |
| Firewall friendly | ❌ Port 1935 often blocked | ✅ Uses 443/UDP, TURN fallback |

**Verdict**: **Support both, prefer WebRTC for browser/mobile creators, RTMP for OBS/professional setups**. Most creator workflows start on browser → WebRTC is critical for adoption. RTMP for power users with OBS. Both ingest into the same HLS-LL segmenter pipeline.

---

## Trade-off 10: Monolith vs Microservices

| Dimension | Monolith | Microservices |
|-----------|:---:|:---:|
| Development velocity (early) | ✅ Fast | ❌ Slow (service boilerplate) |
| Team scalability (>50 engineers) | ❌ Merge conflicts, coupling | ✅ Independent team ownership |
| Deployment complexity | ✅ One deploy | ❌ 12+ services, Helm charts, pipelines |
| Operational complexity | ✅ One thing to monitor | ❌ Distributed tracing required |
| Independent scaling | ❌ Scale everything uniformly | ✅ Scale Streaming without scaling Social |
| Fault isolation | ❌ Analytics bug crashes uploads | ✅ Analytics failure is isolated |
| Technology heterogeneity | ❌ One language/framework | ✅ Best tool per service |
| Latency (inter-service calls) | ✅ In-process | ❌ Network + serialization overhead |

**Verdict**: **Microservices are correct for Spotify-scale** with 500+ engineers. However, start with a **modular monolith** (separate modules, single deployment) and extract services only when scale demands it — typically: Upload, Analytics, and Live Streaming are extracted first because they have radically different scaling profiles. Social and RSS can stay as modules longer.

---

## Trade-off 11: Cloud Pub/Sub vs Kafka for Analytics Event Bus

| Dimension | Cloud Pub/Sub | Kafka on GKE |
|-----------|:---:|:---:|
| Operational overhead | ✅ Fully managed, serverless | ❌ Large ops burden (ZooKeeper/KRaft, disks) |
| Throughput | ✅ ~10B messages/day | ✅ Nearly unlimited |
| Latency | ☑️ ~10-100ms | ✅ <10ms |
| Replay / retention | ✅ 7 days built-in | ✅ Configurable (unlimited) |
| Exactly-once delivery | ❌ At-least-once (dedup in Dataflow) | ✅ Native exactly-once (Kafka Streams) |
| Ordering guarantees | ☑️ Per-message-key (ordering key) | ✅ Per-partition ordering |
| Cost | ✅ Pay-per-message | ❌ Always-on cluster |
| Dataflow integration | ✅ Native connector | ☑️ Kafka IO connector, more config |

**Verdict**: **Cloud Pub/Sub**. At 140,000 messages/sec (~12B/day), Pub/Sub handles this reliably. The operational savings vs self-managed Kafka on GKE are enormous. Deduplication (at-least-once → effectively-once) is handled in the Dataflow pipeline stage. Only switch to Kafka if sub-10ms event latency becomes a hard requirement.

---

## Trade-off 12: CAP Theorem Application

| Component | CAP Choice | Reason |
|-----------|-----------|--------|
| Episode metadata (Spanner) | **CP** (Consistency + Partition tolerance) | Stale episode data = incorrect paywall check |
| Playback positions (Redis) | **AP** (Availability + Partition tolerance) | Small position drift acceptable |
| Social graph (PostgreSQL) | **CP** with eventual | Follow counts can lag 5s |
| Analytics (BigQuery) | **AP** | Eventual dashboards explicitly OK |
| Live stream state (Firestore) | **AP** | Real-time viewer count can be approximate |
| Payments (Stripe + PostgreSQL) | **CP** | No double charges ever |
| RSS feed (Redis cache) | **AP** | 5-min stale feed is in SLO |
