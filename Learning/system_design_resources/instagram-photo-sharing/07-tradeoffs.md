# 07 — Trade-offs & Design Decisions

## System: Photo Sharing Service (Instagram-Scale)

---

## Decision 1: Feed Generation — Push vs Pull vs Hybrid

### The Problem
How do we populate a user's home feed efficiently at 100M DAU scale?

| Dimension | Fan-out on Write (Push) | Fan-out on Read (Pull) | **Hybrid (Our Choice)** |
|-----------|------------------------|------------------------|------------------------|
| **How it works** | On post creation, push post_id to every follower's feed cache | On feed request, query each followee's recent posts and merge | Push for regular users (<1M followers), pull for celebrities |
| **Read latency** | O(1) — Redis ZRANGE | O(followees) — expensive on read | O(1) for most; O(celebrities) only |
| **Write latency** | O(followers) — slow for celebrities | O(1) — fast write | O(followers) for regular; O(1) for celebrities |
| **Storage** | High — 100 post IDs × 100M users = ~80 GB Redis | Low — no feed precomputation | Moderate |
| **Consistency** | Eventual (~seconds) | Near real-time | Eventual for regular, real-time for celebs |
| **Celebrity problem** | Catastrophic — 400M ZADD operations | Excellent — no fan-out | Solved — celebrities use pull |
| **Inactive users** | Waste — updating feed for users who won't log in | Efficient | Efficient — Redis TTL evicts |
| **Complexity** | Low | Medium | **High** — dual model, threshold management |
| **Verdict** | ❌ Breaks at scale | ❌ High read latency | ✅ **Best of both worlds** |

**Decision**: Use hybrid push-pull. Threshold = 1M followers. This is essentially what Instagram uses in production.

---

## Decision 2: Database Choice — SQL vs NoSQL for Posts

| Dimension | PostgreSQL (Cloud SQL) | Cassandra / Bigtable | **Cloud SQL (Our Choice)** |
|-----------|----------------------|---------------------|---------------------------|
| **Query flexibility** | Full SQL, JOINs, aggregations | Key-value / range scans only | Full SQL |
| **Consistency** | ACID transactions | Eventual consistency | ACID |
| **Write throughput** | ~50K writes/sec (with sharding) | Millions/sec | ~50K writes/sec |
| **Read throughput** | ~100K reads/sec with replicas | 100K+ reads/sec | ~100K reads/sec |
| **Schema flexibility** | Rigid but safe | Flexible | Rigid |
| **Caption search** | Needs full-text index | Not supported | Full-text (offloaded to ES) |
| **Operational cost** | Higher (DBA needed) | Lower (auto-managed) | Higher |
| **Posts/day at our scale** | 200M/day — needs partitioning | Handles natively | Partitioned |

**Decision**: Cloud SQL (PostgreSQL) with monthly partitioning. Posts are relational (have authors, media, locations, hashtags). The 200M posts/day is manageable with table partitioning and read replicas. NoSQL would sacrifice JOIN capability for a write throughput we don't actually need (post creation is not the bottleneck — media upload is).

---

## Decision 3: Like Storage — Redis vs Bigtable vs PostgreSQL

| Dimension | PostgreSQL | Redis Only | **Bigtable + Redis (Our Choice)** |
|-----------|-----------|-----------|----------------------------------|
| **Write throughput** | ~5K writes/sec | 100K+/sec | Bigtable: 1M+/sec |
| **Durability** | ACID | Lost on restart | Bigtable: 99.999% |
| **Read latency** | ~5ms | <1ms | <1ms (Redis cache) |
| **Counter accuracy** | Exact | Exact | Slightly stale (30s sync lag) |
| **Did I like it?** | Indexed query | O(1) | O(1) Redis / O(1) Bigtable |
| **Analytics** | Easy SQL | Hard | Easy via BigQuery connector |
| **Cost at 70K writes/sec** | Very expensive (CPU) | Memory-limited | Cost-effective |

**Decision**: Bigtable for durability + Redis for speed. Redis counters sync to PostgreSQL every 30 seconds. The 30s staleness on like counts is acceptable (users don't notice).

---

## Decision 4: Media Storage — Self-Hosted vs Cloud Object Store

| Dimension | Self-Hosted (Ceph) | **GCS Multi-Region (Our Choice)** |
|-----------|-------------------|----------------------------------|
| **Durability** | 99.9% (with replication) | 99.999999999% (11 nines) |
| **Availability** | 99.5% | 99.95% |
| **CDN integration** | Manual setup | Native Cloud CDN integration |
| **Geo-replication** | Manual config | Automatic multi-region |
| **Ops overhead** | Very high | Very low |
| **Cost** | Lower at extreme scale (>10 EB) | Higher at extreme scale |
| **Bandwidth cost** | Cheaper | CDN egress is costly |

**Decision**: GCS Multi-Region. At Instagram's scale, the engineering cost of self-hosted storage vastly outweighs savings. CDN integration is native, durability is superior, and we can optimize later with CDN caching (95% hit ratio) to reduce egress costs.

---

## Decision 5: Follow Graph — Cloud Spanner vs Neo4j vs PostgreSQL

| Dimension | PostgreSQL | Neo4j | **Cloud Spanner (Our Choice)** |
|-----------|-----------|-------|-------------------------------|
| **Consistency** | Strong (single region) | Eventual (in cluster) | **Strong (globally)** |
| **Scale** | Limited (single master) | Good | **Horizontally unlimited** |
| **Graph traversal** | Slow (N-level JOINs) | Excellent (Cypher) | Moderate (no native graph) |
| **Access patterns** | "Do I follow X?" — index lookup | "Find friends of friends" | "Do I follow X?" — point read |
| **Multi-region** | Read replicas only | Causal clustering | **Native multi-region** |
| **Operational** | Easy | Complex | Moderate |

**Decision**: Cloud Spanner. Our access patterns are NOT deep graph traversals (no "friends of friends" recommendations). We need:
1. "Do I follow X?" → point read (Spanner does this at <10ms globally)
2. "Who do I follow?" → range scan (Spanner handles this)
3. **Strong consistency is critical**: a user unfollowing a private account must immediately lose access to their content

Neo4j would be justified if we needed multi-hop traversals (like LinkedIn's "2nd degree connections"). We don't.

---

## Decision 6: Image Processing — Synchronous vs Asynchronous

| Dimension | Synchronous (inline with upload) | **Asynchronous via Pub/Sub (Our Choice)** |
|-----------|----------------------------------|------------------------------------------|
| **User experience** | Post immediately visible | Post visible after ~3-10 seconds |
| **Upload API latency** | 5-10 seconds (blocked) | < 500ms (fast response) |
| **Server scalability** | Uploads block HTTP connections | Decoupled workers scale independently |
| **Failure handling** | Retry is hard (client timeout) | Pub/Sub retry, dead-letter queue |
| **CSAM safety** | Could skip under load | Guaranteed before visibility |
| **Peak load handling** | API server CPU spikes | Queue absorbs spike |

**Decision**: Asynchronous. A 3-10 second delay before a post is visible is completely acceptable and standard (Instagram, Twitter both work this way). The benefits — decoupled scaling, resilient retry, guaranteed CSAM scanning — far outweigh the minor UX delay.

Implementation: Show "processing..." status on client using polling or WebSocket notification for `media.processed` event.

---

## Decision 7: Notification Push — Firebase FCM vs Direct APNs/FCM

| Dimension | Direct APNs + FCM | **Firebase Cloud Messaging (Our Choice)** |
|-----------|------------------|------------------------------------------|
| **Platform support** | Must maintain 2 SDKs | Single unified SDK |
| **Reliability** | High | High (FCM is Google's own) |
| **Topic-based fan-out** | Manual | Built-in FCM topics |
| **Analytics** | Manual | Firebase Analytics built-in |
| **Ops overhead** | Certificate management (APNs) | Managed by Firebase |
| **Cost** | APNs free, FCM free | Free up to 500M msgs/day |

**Decision**: Firebase Cloud Messaging. Single SDK, managed certificates, built-in analytics, free at our scale.

---

## Decision 8: Consistency for Feed — Strong vs Eventual

| Scenario | Strong Consistency | **Eventual Consistency (Our Choice)** |
|----------|-------------------|--------------------------------------|
| User A posts a photo | Feed updates instantly for all followers | Feed updates within ~30 seconds for followers |
| User blocks someone | They're blocked immediately | **Must be immediate** — CAP exception |
| User likes post | Count updates instantly | Count updates within 30 seconds |
| User deletes post | Disappears from all feeds instantly | Disappears within ~30 seconds |

**Decision**: Eventual consistency for feed with one **exception**: privacy-sensitive operations (block, private account follow removal) MUST be strongly consistent. 

For deleted posts: serve a tombstone from the CDN/cache layer that returns 404/removed content; don't wait for feed cache to expire.

---

## CAP Theorem Position

```
                    C (Consistency)
                         /\
                        /  \
                       /    \
                      / CP   \
                     /  (✓)   \
                    /──────────\
                   / CA  \  AP  \
                  /       \  (✓) \
                 /─────────\─────-\
                P (Partition Tolerance)  ──  A (Availability)

Core user data (Cloud SQL):       CP — prefer consistency
Follow graph (Cloud Spanner):     CP — strong consistency globally
Feed cache (Redis):               AP — prefer availability, eventual
Like counters (Redis+Bigtable):   AP — eventual consistency, always available
Media (GCS):                      CP — durability guaranteed
```

---

## Summary: Key Architectural Bets

| Decision | Choice | Risk | Mitigation |
|----------|--------|------|------------|
| Feed model | Hybrid push-pull | Celebrity threshold tuning complexity | Monitor per-user fan-out time; adjust threshold dynamically |
| Like storage | Redis + Bigtable | Redis data loss → count staleness | Bigtable is source of truth; Redis is cache; periodic reconciliation |
| Follow graph | Cloud Spanner | Cost ($$$) at scale | Evaluate Spanner vs custom consistent KV at >10× scale |
| Media processing | Async (Pub/Sub) | Delayed post visibility | Client polls & shows "processing" status; acceptable UX |
| Image format | WebP | Older client compatibility | Serve JPEG fallback for unsupported clients via CDN routing |
