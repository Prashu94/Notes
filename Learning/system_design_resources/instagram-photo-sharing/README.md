# Photo Sharing Service — System Design (Instagram-Scale)

## Overview

A production-grade system design for a **global photo and video sharing platform** at Instagram's scale:
- **500M MAU / 100M DAU**
- **7,000 uploads/sec** (peak), **174,000 photo views/sec** (peak)
- **Multi-region**: US · EU · APAC
- **Cloud**: Google Cloud Platform (GCP)
- **Availability**: 99.99% (< 52 min/year downtime)

---

## Design Files

| # | File | What's Inside |
|---|------|--------------|
| 01 | [01-requirements.md](01-requirements.md) | Functional & non-functional requirements, priority matrix, assumptions |
| 02 | [02-traffic-estimation.md](02-traffic-estimation.md) | RPS, storage, bandwidth calculations — with full math |
| 03 | [03-api-design.md](03-api-design.md) | RESTful API — 8 endpoints with full request/response examples, rate limits |
| 04 | [04-database-design.md](04-database-design.md) | SQL DDL, Bigtable schema, Redis structures, Elasticsearch mappings, ER diagram |
| 05 | [05-high-level-architecture.md](05-high-level-architecture.md) | Mermaid architecture diagram, GCP service breakdown, multi-region topology, security |
| 06 | [06-detailed-components.md](06-detailed-components.md) | Deep-dive: Upload service, Media processing, Feed generation, Like service, Notifications, Search, Follow |
| 07 | [07-tradeoffs.md](07-tradeoffs.md) | 8 major design decisions with comparison tables and justifications |
| 08 | [08-failure-scenarios.md](08-failure-scenarios.md) | 7 failure modes with detection, impact, mitigation, prevention, RTO/RPO |
| 09 | [09-sequence-diagrams.md](09-sequence-diagrams.md) | 6 Mermaid sequence diagrams for all major flows |

---

## Key Design Decisions at a Glance

### 1. Hybrid Push-Pull Feed Model
- **Regular users** (< 1M followers): Fan-out **on write** — push post IDs to followers' Redis caches
- **Celebrities** (≥ 1M followers): Fan-out **on read** — pull at request time
- Prevents the "celebrity problem" (400M Redis writes for a Kylie Jenner post)

### 2. Two-Phase Media Upload
```
Client → [Presigned GCS URL] → GCS (direct binary)
                  ↓ (Pub/Sub event)
         Media Processing Worker (Cloud Run)
            → CSAM check → NSFW score → libvips resize → 3 WebP variants
            → CDN-accessible GCS paths
```

### 3. Like Storage
- **Bigtable**: Durable writes (1M+ writes/sec, row key = `{post_id}#{user_id}`)
- **Redis counters**: Fast reads (`INCR likes:count:{post_id}`)
- **30s sync**: Background job syncs Redis → PostgreSQL `like_count`

### 4. Follow Graph on Cloud Spanner
- Globally distributed strong consistency — critical for private account access control
- Stale reads for non-security queries (fan-out) → low latency

---

## Architecture Summary

```
                    Cloud Armor (WAF + DDoS)
                           │
                    Cloud CDN (200+ PoPs)
                           │
              Cloud Load Balancing (Global Anycast)
                           │
                    Apigee API Gateway
                 (JWT · Rate Limits · Routing)
                           │
        ┌──────────────────┼──────────────────┐
        │         GKE Autopilot Services       │
        │  Upload · Feed · Post · Like ·       │
        │  Comment · Follow · Search · Notif   │
        └──────────────────┬──────────────────┘
                           │
              Cloud Pub/Sub Event Bus
                           │
        ┌──────────────────┼──────────────────┐
        │          Async Workers (Cloud Run)   │
        │  Media Processing · Feed Fan-out ·   │
        │  Notifications · Search Indexer      │
        └──────────────────┬──────────────────┘
                           │
    ┌──────────┬───────────┼───────────┬──────────┐
    │          │           │           │          │
  Cloud SQL  Spanner   Bigtable   Memorystore  GCS
 (Posts,    (Follows)  (Likes,    Redis (Feed  (Media
  Users,               Media      Cache,       Files)
  Comments)            Events)    Counters)
```

---

## Traffic Summary

| Metric | Average | Peak |
|--------|---------|------|
| Photo/video uploads | ~2,315/sec | **7,000/sec** |
| Feed requests | ~11,600/sec | **35,000/sec** |
| Photo views | ~57,900/sec | **174,000/sec** |
| Like writes | ~23,150/sec | **70,000/sec** |
| New media storage | — | **~5 PB/day** |

---

## Core APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/media/upload-url` | Request presigned GCS upload URL |
| POST | `/v1/posts` | Create post (after media upload) |
| GET | `/v1/feed` | Get ranked/chronological feed |
| PUT | `/v1/posts/{id}/like` | Like or unlike a post |
| POST | `/v1/posts/{id}/comments` | Add a comment |
| PUT | `/v1/users/{id}/follow` | Follow or unfollow a user |
| GET | `/v1/users/{id}/profile` | Get user profile |
| GET | `/v1/search` | Search users, hashtags, locations |

---

## GCP Services Used

| Category | Service | Purpose |
|----------|---------|---------|
| Edge | Cloud Armor, Cloud CDN | WAF, global media delivery |
| LB | Cloud Load Balancing | Global routing |
| API | Apigee | Rate limiting, JWT validation |
| Auth | Firebase Authentication | User identity, JWT issuance |
| Compute | GKE Autopilot | All microservices |
| Serverless | Cloud Run | Async workers (media, feed, notifs) |
| RDBMS | Cloud SQL (PostgreSQL) | Users, posts, comments |
| Global DB | Cloud Spanner | Follow graph (global consistency) |
| Wide-Column | Cloud Bigtable | Likes, media processing events |
| Cache | Memorystore (Redis) | Feed cache, like counters, sessions |
| Search | Elasticsearch on GCE | Full-text, hashtag, geo search |
| Object Store | Cloud Storage (GCS) | All media files |
| Messaging | Cloud Pub/Sub | Event-driven async pipeline |
| Notifications | Firebase Cloud Messaging | Push notifications (iOS + Android) |
| Analytics | BigQuery + Dataflow | Engagement analytics, ETL |
| ML | Vertex AI | Feed ranking, NSFW detection |
| Observability | Cloud Monitoring, Logging, Trace | Full observability stack |
| Secrets | Secret Manager | DB creds, API keys |

---

## Interview Tip: Key Talking Points

1. **Celebrity problem** → Hybrid push-pull model (most candidates miss this)
2. **Presigned URL for uploads** → Never funnel 120 GB/s through app servers
3. **Eventual consistency for likes** → Justify with UX tradeoff (users don't notice 30s lag)
4. **Cloud Spanner for follows** → Strong consistency required for private account access control
5. **CSAM scanning** → Non-negotiable safety requirement; must be synchronous before post visibility
6. **Feed cache TTL** → 24h with LRU eviction; no waste for inactive users
7. **Notification batching** → Prevents spam; "X and 49 others liked your photo"
8. **libvips over ImageMagick** → 10× faster image processing; critical at 7K uploads/sec
