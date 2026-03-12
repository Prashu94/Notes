# 01 — Requirements

## System: Photo Sharing Service (Instagram-Scale)

**Scale Assumptions**: 500M MAU · 100M DAU · Global multi-region · GCP

---

## Functional Requirements

### MVP (Phase 1 — Core)

| # | Feature | Description |
|---|---------|-------------|
| F1 | **Photo/Video Upload** | Users can upload photos (JPEG, PNG, WEBP) and short videos (≤ 60s) |
| F2 | **Post Management** | Create, edit caption, delete posts; tag locations and users |
| F3 | **Home Feed** | Chronological + ranked feed from followed users, paginated |
| F4 | **Follow / Unfollow** | Users can follow/unfollow other users; private accounts require approval |
| F5 | **Like / Unlike** | Like or unlike any post; see total like count |
| F6 | **Comments** | Add, edit, delete comments on posts; nested comments (1 level) |
| F7 | **User Profiles** | Public/private profiles with bio, follower/following count, post grid |
| F8 | **Notifications** | Push + in-app notifications for likes, comments, follows, mentions |
| F9 | **Search** | Search users by username, posts by hashtag, locations |
| F10 | **Explore / Discover** | Personalized grid of trending/recommended posts |

### Phase 2 (Future — Out of Scope for this design)

- Stories (24-hour ephemeral content)
- Reels (short-form video feed)
- Direct Messages (DMs)
- Shopping / Product tagging
- Live Streaming
- Collaborative posts

---

## Non-Functional Requirements

### Performance

| Metric | Target |
|--------|--------|
| Photo upload end-to-end | < 2s for 95th percentile (3MB photo) |
| Feed load latency | < 500ms P95, < 200ms P50 |
| Search latency | < 300ms P95 |
| Notification delivery | < 5s for push, < 30s for in-app |
| CDN image serve time | < 100ms P95 globally |

### Scalability

| Metric | Value |
|--------|-------|
| MAU | 500 million |
| DAU | 100 million |
| Peak photo uploads | ~7,000 uploads/sec |
| Peak photo views | ~175,000 views/sec |
| Peak feed requests | ~35,000 req/sec |

### Availability & Reliability

- **Availability**: 99.99% uptime (< 52 min downtime/year)
- **Durability**: 99.999999999% (11 nines) for uploaded media (GCS)
- **RPO**: < 1 minute for user data; 0 for media (replicated at upload)
- **RTO**: < 5 minutes for critical path; < 30 minutes for full recovery

### Consistency

| Data Type | Consistency Model | Rationale |
|-----------|-------------------|-----------|
| Photo upload | **Strong** | Users must see their own uploaded photo immediately |
| Follow/Unfollow | **Strong** | Prevents access control issues with private accounts |
| Like counts | **Eventual** (~1s) | Minor staleness acceptable; high write throughput needed |
| Comment writes | **Strong** | User expects their comment to appear immediately |
| Feed generation | **Eventual** (~30s) | Slight delay acceptable; massive scale requires async fan-out |
| Notifications | **Best-effort** | Occasional miss acceptable |

### Security & Compliance

- All media encrypted at rest (AES-256) and in transit (TLS 1.3)
- GDPR: Data deletion within 30 days of request
- CCPA: Opt-out of data sharing
- CSAM detection pipeline on every uploaded image (PhotoDNA hash matching)
- Rate limiting on all write APIs
- Private account enforcement: followers-only media access

### Geo & Availability Zones

- **Regions**: US (us-central1), EU (europe-west1), APAC (asia-east1)
- **Multi-AZ** within each region for all stateful services
- **CDN PoPs**: 200+ globally via Cloud CDN
- Active-active multi-region with eventual consistency between regions

---

## Explicit Assumptions

1. Average photo size = **3MB** after client-side compression (original can be up to 20MB)
2. Average video size = **50MB** for 60s clip (after mobile compression)
3. **80/20 rule**: 20% of users generate 80% of content (power users / celebrities)
4. Celeb threshold: users with > 1M followers use **pull-based feed** to avoid fan-out storms
5. Regular users (< 1M followers) use **push-based feed** (fan-out on write)
6. Photo:Video upload ratio = **70:30**
7. Read:Write ratio = **100:1** (mostly reads)
8. Average user follows **300** other accounts
9. Average post receives **50 likes** and **5 comments**
10. Client handles image resizing to 3 variants before upload (thumb, medium, original)

---

## Priority Matrix

```
                HIGH IMPACT
                    |
    Notifications   |   Photo Upload
    Following       |   Home Feed
                    |   User Profiles
    ________________|________________
                    |
    Comments        |   Search
    Likes           |   Explore
                    |
                LOW IMPACT
          LOW EFFORT         HIGH EFFORT
```

---

## Out of Scope

- Video transcoding pipeline details (simplified to analogous photo processing)
- Ad serving and monetization platform
- Content moderation dashboard UI
- Stories and ephemeral content
- Real-time collaborative features
- Payment processing
