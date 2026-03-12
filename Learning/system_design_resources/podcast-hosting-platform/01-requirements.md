# Requirements — Podcast Hosting Platform (Spotify Scale)

---

## 1. Functional Requirements

### 1.1 Content Upload & Hosting

| ID | Requirement |
|----|-------------|
| FR-01 | Creators upload audio files: MP3, AAC, WAV, FLAC, OGG — up to **2 GB** per episode |
| FR-02 | Support **resumable, chunked uploads** with real-time progress tracking |
| FR-03 | Automatic transcoding to **4 bitrates**: 32 / 64 / 128 / 192 kbps |
| FR-04 | Episode metadata: title, description, season #, episode #, explicit flag, tags, chapter markers |
| FR-05 | Podcast-level metadata: artwork (3000×3000 JPEG/PNG), category, language, author, website |
| FR-06 | Scheduled publishing: set future publish date/time |
| FR-07 | Soft delete (de-list) and permanent delete of episodes |
| FR-08 | Import an existing podcast by supplying an external RSS feed URL |

### 1.2 Streaming

| ID | Requirement |
|----|-------------|
| FR-09 | On-demand streaming via **HLS (HTTP Live Streaming)** with adaptive bitrate |
| FR-10 | DASH streaming as secondary protocol for non-Apple clients |
| FR-11 | Resume playback from last position — synced across all devices for a user |
| FR-12 | **Live podcast streaming** with end-to-end latency < 30 seconds |
| FR-13 | Live stream recording automatically saved as on-demand episode |
| FR-14 | Offline download for premium subscribers (DRM-protected file) |
| FR-15 | 1.5× / 2× speed playback support (server provides raw segments; client controls speed) |

### 1.3 RSS Feed

| ID | Requirement |
|----|-------------|
| FR-16 | Auto-generate an **iTunes/Spotify-compatible RSS 2.0 feed** per podcast |
| FR-17 | Feed includes: artwork, episode enclosures, duration, explicit flag, chapters, transcription link |
| FR-18 | Custom domain RSS URLs (e.g., `feeds.mypodcast.com/rss`) |
| FR-19 | RSS feed reflects new episodes within **5 minutes** of publish |
| FR-20 | Support import of external podcast via RSS URL (ingest episodes into platform) |
| FR-21 | Atom feed support as alternative to RSS 2.0 |

### 1.4 Transcription & Chapters

| ID | Requirement |
|----|-------------|
| FR-22 | Auto-transcribe every episode using speech-to-text — supports 30+ languages |
| FR-23 | Transcripts available as: full text, time-stamped segments (SRT), word-level JSON |
| FR-24 | Automatic chapter detection (silence + topic shift) + manual override |
| FR-25 | Interactive transcript: click a word → seek audio to that timestamp |
| FR-26 | Transcript full-text search across entire platform corpus |
| FR-27 | Transcription turnaround < 2 hours for a 1-hour episode |
| FR-28 | Creators can edit auto-generated transcripts |

### 1.5 Analytics Dashboard

| ID | Requirement |
|----|-------------|
| FR-29 | Real-time listener metrics: plays, unique listeners, completion rate per episode |
| FR-30 | Geographic breakdown: country, city, region |
| FR-31 | Device / platform / app breakdown |
| FR-32 | **Retention curve** per episode: % of listeners still playing at each minute mark |
| FR-33 | Subscriber growth over time with cohort breakdown |
| FR-34 | Episode-to-episode performance comparison |
| FR-35 | Download metrics for external RSS subscribers (IAB v2.1 compliant) |
| FR-36 | Revenue analytics: subscription MRR, ad impressions/RPM, tips total |
| FR-37 | Data export (CSV, JSON) for all analytics |

### 1.6 Monetization

| ID | Requirement |
|----|-------------|
| FR-38 | Creator **subscription tiers** (e.g., $3/mo, $8/mo, $25/mo) with custom perks |
| FR-39 | **Premium episode gating**: subscriber-only episodes |
| FR-40 | **Programmatic ad insertion** (pre-roll, mid-roll, post-roll) via VAST 4.x |
| FR-41 | **Host-read ad campaigns**: CPM-based, targeted by genre/geography/demographics |
| FR-42 | **Listener tips / micropayments** to creators |
| FR-43 | Platform revenue split: 80% creator / 20% platform |
| FR-44 | Creator payout dashboard: earnings, pending, paid, tax documents |
| FR-45 | Stripe integration for payments, subscriptions, and payouts |

### 1.7 Social Features

| ID | Requirement |
|----|-------------|
| FR-46 | Listeners **follow** podcasts and individual creator accounts |
| FR-47 | **Activity feed**: "Creator X published Episode Y", "Friend started following Z" |
| FR-48 | **Episode comments**: threaded, up to 3 levels deep |
| FR-49 | Comment likes, replies, and reporting (DMCA + abuse) |
| FR-50 | **Star ratings** per podcast (1–5 stars; aggregated + recency-weighted) |
| FR-51 | Listener-created **playlists** (public and private) |
| FR-52 | **Shareable episode URLs** with open graph preview + embeddable player |
| FR-53 | Listener profiles: avatar, bio, public listening history, public playlists |
| FR-54 | **Notification system**: push (FCM/APNs), email, in-app for new episodes from followed creators |

---

## 2. Non-Functional Requirements

### 2.1 Scale

| Metric | Target | Notes |
|--------|--------|-------|
| MAU | **500M** | Spotify-comparable |
| DAU | **200M** | ~40% of MAU |
| Peak concurrent streams | **18.75M** | 3× average (200M × 45min / 1440min × 3) |
| New episodes/day | **1,000,000** | |
| Total episodes corpus | **50M+** | Growing at 1M/day |
| Total podcasts | **5M+** | |
| Analytics events/sec (peak) | **140,000** | 4B/day × 3× peak factor |
| API RPS (peak) | **140,000** | 200M DAU × 20 calls / 86,400s × 3 |

### 2.2 Performance SLOs

| Component | Target | Priority |
|-----------|--------|----------|
| Audio stream start latency | < **2s** (p99) | Critical |
| Live stream latency | < **30s** end-to-end | High |
| RSS feed response | < **500ms** (p99) | Critical |
| API response time | < **200ms** (p95) | High |
| Upload throughput (creator) | > **50 MB/s** | High |
| Analytics dashboard load | < **3s** (p95) | Medium |
| Search response | < **500ms** (p95) | High |
| Transcription turnaround | < **2h** for 1-hour episode | Medium |
| Episode publish → feed update | < **5 minutes** | High |

### 2.3 Availability SLAs

| Component | SLA | Justification |
|-----------|-----|---------------|
| Audio streaming (CDN) | **99.99%** | Core product, ~52 min/year downtime |
| RSS Feed Service | **99.99%** | Used by external podcast apps |
| Upload Service | **99.95%** | Degraded OK, creators can retry |
| Live Streaming | **99.9%** | Best-effort live events |
| Analytics | **99.9%** | Lagged dashboards acceptable |
| Social Features | **99.9%** | Eventual consistency acceptable |
| Monetization/Payments | **99.95%** | Financial, needs high SLA |

### 2.4 Durability

| Data Type | Target | Mechanism |
|-----------|--------|-----------|
| Audio files | **99.999999999%** (11 nines) | GCS Multi-Region storage class |
| User data (accounts) | **99.9999999%** (9 nines) | Cloud Spanner multi-region |
| Episode metadata | **99.999%** | Spanner synchronous replication |
| Analytics data | **99.9%** | BigQuery + Pub/Sub replay buffer |
| Live stream recordings | **99.99%** | Async GCS copy on stream end |

### 2.5 Consistency Model

| Operation | Consistency Required | Rationale |
|-----------|---------------------|-----------|
| Episode publish | **Strong** | Creator must see their episode immediately |
| Payment / subscription | **Strong** | Financial integrity |
| Play count display | **Eventual** (up to 5 min lag) | Acceptable for analytics dashboards |
| Comment post | **Eventual** (seconds) | Slight lag unnoticeable to users |
| Follow action | **Eventual** | Feed reordering delay is OK |
| Playback position sync | **Eventual** (< 30s) | User doesn't notice minor drift |
| RSS feed reflect publish | **Eventual** (< 5 min) | Defined SLO, not instant |

### 2.6 Security Requirements

| Requirement | Implementation |
|-------------|---------------|
| All traffic encrypted | TLS 1.3 minimum, HTTPS everywhere |
| Audio file access | **Signed URLs** with TTL (prevents hotlinking, unauthorized downloads) |
| API authentication | OAuth 2.0 + JWT (Firebase Auth) |
| Payment data | PCI-DSS compliant (Stripe handles cardholder data) |
| DDoS protection | Cloud Armor rules + rate limiting via Apigee |
| SQL injection prevention | Parameterized queries only; no raw SQL from API inputs |
| SSRF prevention | Allowlist for external RSS import URLs; no internal IP ranges |
| Secrets management | GCP Secret Manager (no secrets in env vars or code) |

### 2.7 Compliance

| Regulation | Requirement |
|-----------|-------------|
| **GDPR** | User data export (<30 days), right to erasure, data residency (EU region) |
| **CCPA** | California users: opt-out of data sale, data deletion rights |
| **COPPA** | No accounts for users under 13; age verification on signup |
| **DMCA** | Automated takedown pipeline: content hash matching + creator counter-notice flow |
| **IAB Podcast Metrics v2.1** | Download counting methodology compliance for advertisers |
| **PCI-DSS** | Stripe integration keeps platform out of cardholder data scope |

---

## 3. Explicit Assumptions

1. Audio files are stored in GCS; CDN serves 95%+ of streaming traffic from edge cache
2. Transcription is **asynchronous** — not required to complete before episode is playable
3. Live streaming accounts for <5% of total traffic at any time
4. Programmatic ads are served **client-side via VAST URLs** (not server-side audio stitching in MVP)
5. Stripe handles all financial transactions — platform is not PCI in scope
6. RSS feed cache TTL is 5 minutes (regenned event-driven on publish, not on every poll)
7. Full-text search index is asynchronously updated (near-real-time, within 60 seconds)
8. Playback position is written client-side and synced every 30 seconds

---

## 4. Out of Scope (v1)

- Video podcasting (audio-only)
- AI-generated episode summaries / show notes
- Blockchain-based royalty splits
- Native mobile app (API-first; BYO client)
- Multi-tenant white-label hosting for third parties
- Fediverse / ActivityPub federation
- Server-side audio ad stitching (SSAI) — Phase 3

---

## 5. Priority Matrix

| Feature | Priority | Phase | Effort |
|---------|----------|-------|--------|
| Upload + host audio | Critical | **MVP** | L |
| On-demand streaming | Critical | **MVP** | L |
| RSS feed generation | Critical | **MVP** | M |
| User auth + profiles | Critical | **MVP** | M |
| Basic analytics (plays, geography) | High | **MVP** | M |
| Follow + ratings | High | **MVP** | S |
| Transcription (async) | High | **Phase 2** | L |
| Live streaming | High | **Phase 2** | XL |
| Episode comments | Medium | **Phase 2** | M |
| Creator subscriptions + tips | High | **Phase 2** | L |
| Programmatic ads (VAST) | High | **Phase 2** | L |
| Retention curve analytics | Medium | **Phase 3** | M |
| Personalized recommendations | Medium | **Phase 3** | XL |
| Offline downloads (DRM) | Medium | **Phase 3** | L |
| Server-side ad stitching (SSAI) | Low | **Phase 3** | XL |
