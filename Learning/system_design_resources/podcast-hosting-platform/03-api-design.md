# API Design — Podcast Hosting Platform

> **Style**: RESTful JSON over HTTPS
> **Versioning**: URI path versioning (`/v1/`)
> **Auth**: Firebase JWT Bearer token in `Authorization` header
> **Pagination**: Cursor-based (not offset) for all list endpoints
> **Idempotency**: `Idempotency-Key` header on mutation endpoints

---

## Global Conventions

### Authentication Header
```
Authorization: Bearer <firebase_jwt_token>
```

### Standard Error Response
```json
{
  "error": {
    "code": "EPISODE_NOT_FOUND",
    "message": "Episode with id 'ep_abc123' does not exist.",
    "request_id": "req_9kXpQmZy",
    "timestamp": "2026-03-12T14:23:01Z"
  }
}
```

### Standard Pagination (Cursor-Based)
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6ImVwXzEyMyIsInRzIjoxNjk5..."},
    "has_more": true,
    "limit": 20
  }
}
```

### Rate Limits

| Tier | Limit | Window |
|------|-------|--------|
| Anonymous (RSS) | 1,000 req | per minute per IP |
| Authenticated (listener) | 5,000 req | per minute per user |
| Creator (upload/publish) | 100 req | per minute per user |
| Analytics ingest | 10,000 events | per minute per client |
| Admin/internal | Unlimited | — |

Rate limit headers returned on every response:
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4987
X-RateLimit-Reset: 1710252180
```

---

## API 1 — Upload Service

### `POST /v1/podcasts/{podcast_id}/episodes/upload-url`
Request a **pre-signed GCS upload URL** for a new episode. The client uploads directly to GCS — the API server never proxies the file bytes.

**Request**
```json
{
  "filename": "episode-042.mp3",
  "content_type": "audio/mpeg",
  "file_size_bytes": 98765432,
  "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4..."
}
```

**Response `202 Accepted`**
```json
{
  "upload_id": "upl_7Hk2mNpQ",
  "signed_url": "https://storage.googleapis.com/podcast-uploads/...",
  "expires_at": "2026-03-12T15:23:01Z",
  "chunk_size_bytes": 10485760,
  "resume_endpoint": "/v1/uploads/upl_7Hk2mNpQ/resume"
}
```

---

### `POST /v1/podcasts/{podcast_id}/episodes`
Create episode metadata **after** successful audio upload. This triggers transcoding and RSS regeneration.

**Request**
```json
{
  "upload_id": "upl_7Hk2mNpQ",
  "title": "Episode 42: The Future of AI",
  "description": "We dive deep into large language models with Dr. Jane Smith.",
  "season_number": 3,
  "episode_number": 42,
  "explicit": false,
  "tags": ["technology", "AI", "machine-learning"],
  "publish_at": "2026-03-15T09:00:00Z",
  "chapters": [
    { "title": "Intro", "start_ms": 0 },
    { "title": "Interview: Dr. Smith", "start_ms": 180000 },
    { "title": "Listener Q&A", "start_ms": 2700000 }
  ]
}
```

**Response `201 Created`**
```json
{
  "episode": {
    "id": "ep_Xyz9mPqR",
    "podcast_id": "pod_AbcD1234",
    "title": "Episode 42: The Future of AI",
    "status": "processing",
    "transcoding_job_id": "job_Kl8mNoPq",
    "published_at": null,
    "scheduled_for": "2026-03-15T09:00:00Z",
    "audio_url": null,
    "duration_seconds": null,
    "created_at": "2026-03-12T14:23:01Z"
  }
}
```

---

### `GET /v1/podcasts/{podcast_id}/episodes`
List all episodes for a podcast with cursor-based pagination.

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | int | 1–100, default 20 |
| `cursor` | string | Pagination cursor from previous response |
| `status` | enum | `published`, `draft`, `scheduled`, `processing` |
| `sort` | enum | `published_at_desc` (default), `published_at_asc`, `plays_desc` |

**Response `200 OK`**
```json
{
  "data": [
    {
      "id": "ep_Xyz9mPqR",
      "title": "Episode 42: The Future of AI",
      "description": "We dive deep into large language models...",
      "duration_seconds": 2874,
      "audio_url": "https://cdn.podcastplatform.com/episodes/ep_Xyz9mPqR/128k.m3u8",
      "artwork_url": "https://cdn.podcastplatform.com/artwork/pod_AbcD1234.jpg",
      "published_at": "2026-03-15T09:00:00Z",
      "play_count": 142300,
      "is_premium": false,
      "chapters": [...]
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6ImVwX...",
    "has_more": true,
    "limit": 20
  }
}
```

---

## API 2 — Streaming Service

### `GET /v1/episodes/{episode_id}/stream`
Get the HLS manifest URL for an episode. Returns a **time-limited signed CDN URL**.

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `quality` | enum | `auto` (default), `high` (192k), `medium` (128k), `low` (64k), `data_saver` (32k) |
| `position_ms` | int | Resume from position in milliseconds |

**Response `200 OK`**
```json
{
  "manifest_url": "https://cdn.podcastplatform.com/episodes/ep_Xyz9mPqR/adaptive.m3u8?token=eyJ...",
  "manifest_url_expires_at": "2026-03-12T16:23:01Z",
  "tracks": [
    { "bitrate": 192000, "url": "https://cdn.podcastplatform.com/.../192k.m3u8?token=..." },
    { "bitrate": 128000, "url": "https://cdn.podcastplatform.com/.../128k.m3u8?token=..." },
    { "bitrate":  64000, "url": "https://cdn.podcastplatform.com/.../64k.m3u8?token=..."  },
    { "bitrate":  32000, "url": "https://cdn.podcastplatform.com/.../32k.m3u8?token=..."  }
  ],
  "resume_position_ms": 1824000,
  "duration_ms": 2874000,
  "is_premium": false,
  "ad_break_positions_ms": [0, 900000, 1800000]
}
```

---

### `POST /v1/episodes/{episode_id}/playback-position`
Update playback position. Called every 30 seconds by the client. **Idempotent** — safe to retry.

**Request**
```json
{
  "position_ms": 924000,
  "device_id": "dev_iPhoneXR_abc",
  "session_id": "sess_Kl9mNoPq",
  "completed": false
}
```

**Response `204 No Content`**

---

### `POST /v1/analytics/events`
Batch-submit playback analytics events. Clients batch events and send every 30 seconds.

**Request**
```json
{
  "session_id": "sess_Kl9mNoPq",
  "episode_id": "ep_Xyz9mPqR",
  "device_type": "ios",
  "app_version": "4.2.1",
  "events": [
    { "event": "play_start",   "position_ms": 0,       "timestamp": "2026-03-12T14:23:05Z" },
    { "event": "heartbeat",    "position_ms": 30000,   "timestamp": "2026-03-12T14:23:35Z" },
    { "event": "heartbeat",    "position_ms": 60000,   "timestamp": "2026-03-12T14:24:05Z" },
    { "event": "play_pause",   "position_ms": 75000,   "timestamp": "2026-03-12T14:24:20Z" },
    { "event": "play_resume",  "position_ms": 75000,   "timestamp": "2026-03-12T14:24:55Z" }
  ]
}
```

**Response `202 Accepted`**
```json
{ "ingested": 5, "dropped": 0 }
```

---

## API 3 — RSS Service

### `GET /v1/feeds/{podcast_slug}/rss`
Return the iTunes/Spotify-compatible RSS 2.0 XML feed. Served directly from CDN/Redis cache 99% of the time.

**Headers Returned**
```
Content-Type: application/rss+xml; charset=utf-8
Cache-Control: public, max-age=300
ETag: "abc123feed"
Last-Modified: Wed, 11 Mar 2026 09:15:00 GMT
```

**Response `200 OK` (XML)**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
  xmlns:podcast="https://podcastindex.org/namespace/1.0">
  <channel>
    <title>My Awesome Podcast</title>
    <link>https://mypodcast.com</link>
    <description>Weekly deep dives into technology.</description>
    <itunes:author>Jane Smith</itunes:author>
    <itunes:image href="https://cdn.podcastplatform.com/artwork/pod_AbcD1234.jpg"/>
    <itunes:category text="Technology"/>
    <item>
      <title>Episode 42: The Future of AI</title>
      <enclosure url="https://cdn.podcastplatform.com/episodes/ep_Xyz9mPqR/128k.mp3?token=..."
                 length="55296000" type="audio/mpeg"/>
      <guid isPermaLink="false">ep_Xyz9mPqR</guid>
      <pubDate>Sat, 15 Mar 2026 09:00:00 GMT</pubDate>
      <itunes:duration>2874</itunes:duration>
      <itunes:explicit>no</itunes:explicit>
    </item>
  </channel>
</rss>
```

---

## API 4 — Transcription Service

### `GET /v1/episodes/{episode_id}/transcript`
Retrieve the full transcript with optional time-aligned word data.

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | enum | `text` (plain), `srt` (SRT subtitle), `json` (word-level with timestamps) |
| `language` | string | BCP-47 language code. Default: detected language |

**Response `200 OK` (JSON format)**
```json
{
  "episode_id": "ep_Xyz9mPqR",
  "language": "en-US",
  "status": "completed",
  "confidence": 0.97,
  "words": [
    { "word": "Welcome",  "start_ms": 1200,  "end_ms": 1680,  "confidence": 0.99 },
    { "word": "to",       "start_ms": 1690,  "end_ms": 1820,  "confidence": 1.00 },
    { "word": "episode",  "start_ms": 1840,  "end_ms": 2210,  "confidence": 0.98 }
  ],
  "segments": [
    {
      "start_ms": 0,
      "end_ms": 180000,
      "speaker": "HOST",
      "text": "Welcome to episode 42 of My Awesome Podcast..."
    }
  ],
  "chapters": [
    { "title": "Intro",              "start_ms": 0       },
    { "title": "Interview: Dr. Smith","start_ms": 180000 }
  ]
}
```

---

## API 5 — Analytics Dashboard

### `GET /v1/analytics/podcasts/{podcast_id}/overview`
Summary analytics for a podcast. Requires creator auth for the given podcast.

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | ISO8601 | Start of date range |
| `to` | ISO8601 | End of date range (max 365 days) |
| `granularity` | enum | `hour`, `day` (default), `week`, `month` |

**Response `200 OK`**
```json
{
  "podcast_id": "pod_AbcD1234",
  "period": { "from": "2026-02-12", "to": "2026-03-12" },
  "totals": {
    "plays": 1842300,
    "unique_listeners": 432100,
    "hours_listened": 98420,
    "subscribers_gained": 5430,
    "subscribers_lost": 820,
    "net_subscribers": 4610,
    "revenue_usd": 12450.00
  },
  "timeseries": [
    { "date": "2026-03-01", "plays": 58200, "unique_listeners": 14300 },
    { "date": "2026-03-02", "plays": 61400, "unique_listeners": 15100 }
  ],
  "top_episodes": [
    { "episode_id": "ep_Xyz9mPqR", "title": "Episode 42...", "plays": 142300 }
  ],
  "geography": [
    { "country": "US", "plays": 820000, "pct": 44.5 },
    { "country": "GB", "plays": 184000, "pct": 9.99 }
  ],
  "devices": [
    { "type": "iOS",     "pct": 52.3 },
    { "type": "Android", "pct": 31.4 },
    { "type": "Web",     "pct": 16.3 }
  ]
}
```

### `GET /v1/analytics/episodes/{episode_id}/retention`
Listener retention curve — what % of listeners are still playing at each minute.

**Response `200 OK`**
```json
{
  "episode_id": "ep_Xyz9mPqR",
  "duration_seconds": 2874,
  "total_plays": 142300,
  "retention_curve": [
    { "position_seconds": 0,    "retention_pct": 100.0 },
    { "position_seconds": 60,   "retention_pct": 91.2  },
    { "position_seconds": 300,  "retention_pct": 78.4  },
    { "position_seconds": 900,  "retention_pct": 62.1  },
    { "position_seconds": 1800, "retention_pct": 45.8  },
    { "position_seconds": 2700, "retention_pct": 38.2  }
  ],
  "avg_listen_seconds": 1642,
  "completion_rate_pct": 38.2
}
```

---

## API 6 — Monetization Service

### `POST /v1/monetization/creator-subscriptions`
Subscribe to a creator's premium tier.

**Request**
```json
{
  "creator_id": "usr_CreatorXxx",
  "tier_id": "tier_premium_8usd",
  "payment_method_id": "pm_stripe_xxxxx"
}
```

**Response `201 Created`**
```json
{
  "subscription_id": "sub_MnOp5678",
  "creator_id": "usr_CreatorXxx",
  "tier": { "id": "tier_premium_8usd", "name": "Premium", "price_usd": 8.00, "billing_cycle": "monthly" },
  "status": "active",
  "current_period_end": "2026-04-12T14:23:01Z",
  "created_at": "2026-03-12T14:23:01Z"
}
```

### `POST /v1/monetization/tips`
Send a micropayment tip to a creator.

**Request**
```json
{
  "creator_id": "usr_CreatorXxx",
  "amount_usd": 5.00,
  "message": "Loved episode 42!",
  "payment_method_id": "pm_stripe_xxxxx"
}
```

**Response `201 Created`**
```json
{
  "tip_id": "tip_QrSt9012",
  "status": "completed",
  "amount_usd": 5.00,
  "creator_payout_usd": 4.00,
  "platform_fee_usd": 1.00,
  "processed_at": "2026-03-12T14:23:02Z"
}
```

---

## API 7 — Social Service

### `POST /v1/follows`
Follow a podcast or creator.

**Request**
```json
{
  "target_type": "podcast",
  "target_id": "pod_AbcD1234"
}
```

**Response `201 Created`**
```json
{
  "follow_id": "flw_UvWx3456",
  "target_type": "podcast",
  "target_id": "pod_AbcD1234",
  "followed_at": "2026-03-12T14:23:01Z"
}
```

### `GET /v1/episodes/{episode_id}/comments`
Paginated threaded comments for an episode.

**Query Parameters**: `limit` (int), `cursor` (string), `sort` (`top`, `new`)

**Response `200 OK`**
```json
{
  "data": [
    {
      "id": "cmt_Yz012abc",
      "author": { "id": "usr_Jane123", "username": "jane_listens", "avatar_url": "..." },
      "content": "This was such a great episode! Dr. Smith's insights on AI safety were eye-opening.",
      "likes": 142,
      "created_at": "2026-03-15T10:32:00Z",
      "replies": [
        {
          "id": "cmt_Ab345def",
          "author": { "id": "usr_CreatorXxx", "username": "mypodcast_host" },
          "content": "Thanks Jane! Dr. Smith was incredible.",
          "likes": 38,
          "created_at": "2026-03-15T11:00:00Z",
          "replies": []
        }
      ]
    }
  ],
  "pagination": { "next_cursor": "eyJpZCI6ImNtd...", "has_more": true, "limit": 20 }
}
```

### `POST /v1/episodes/{episode_id}/comments`
**Request**
```json
{
  "content": "Mind-blowing episode!",
  "parent_comment_id": null
}
```
**Response `201 Created`** — returns created comment object.

---

## API 8 — Search

### `GET /v1/search`
Full-text search across podcasts, episodes, and transcripts.

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (required) |
| `type` | enum | `all`, `podcast`, `episode`, `transcript` |
| `category` | string | Filter by iTunes category |
| `language` | string | BCP-47 language code |
| `limit` | int | 1–50, default 20 |
| `cursor` | string | Pagination cursor |

**Response `200 OK`**
```json
{
  "query": "AI safety machine learning",
  "total_hits": 8420,
  "data": [
    {
      "type": "episode",
      "score": 0.97,
      "episode": {
        "id": "ep_Xyz9mPqR",
        "title": "Episode 42: The Future of AI",
        "podcast": { "id": "pod_AbcD1234", "title": "My Awesome Podcast" },
        "published_at": "2026-03-15T09:00:00Z",
        "highlight": "...Dr. Smith's insights on <em>AI safety</em> and <em>machine learning</em>..."
      }
    }
  ],
  "pagination": { "next_cursor": "eyJpZCI6InNyY...", "has_more": true }
}
```

---

## API 9 — Live Streaming

### `POST /v1/live-streams`
Start a live stream — returns RTMP/WebRTC ingest credentials.

**Request**
```json
{
  "podcast_id": "pod_AbcD1234",
  "title": "Live Q&A - AI Special",
  "description": "Join me live for listener questions!",
  "enable_chat": true,
  "auto_save_as_episode": true
}
```

**Response `201 Created`**
```json
{
  "stream_id": "live_EfGh7890",
  "rtmp_url": "rtmps://live.podcastplatform.com/publish",
  "stream_key": "sk_live_kXpQmZy9...",
  "webrtc_offer_endpoint": "/v1/live-streams/live_EfGh7890/webrtc-offer",
  "playback_hls_url": "https://cdn.podcastplatform.com/live/live_EfGh7890/index.m3u8",
  "status": "waiting",
  "chat_channel": "live_EfGh7890"
}
```

---

## HTTP Status Code Reference

| Code | Usage |
|------|-------|
| 200 | Successful GET |
| 201 | Resource created |
| 202 | Accepted (async processing, e.g., upload, transcode) |
| 204 | No content (successful update/delete) |
| 400 | Bad request (validation error) |
| 401 | Unauthenticated |
| 403 | Forbidden (authenticated but unauthorized, e.g., accessing another creator's analytics) |
| 404 | Not found |
| 409 | Conflict (duplicate episode GUID on import) |
| 413 | Payload too large (file exceeds 2 GB limit) |
| 422 | Unprocessable entity (valid JSON but semantic error) |
| 429 | Rate limit exceeded |
| 503 | Service unavailable (upstream dependency down) |
