# Traffic Estimation — Podcast Hosting Platform

> All estimates are for **Spotify-scale (500M MAU / 200M DAU)**.
> Show your math — that's what interviewers want to see.

---

## Baseline Assumptions

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| MAU | 500M | Spotify comparable |
| DAU | 200M | 40% of MAU (Spotify actual: 236M/602M ≈ 39%) |
| Avg listening time / DAU | **45 min/day** | Edison Research podcast listener survey |
| Avg episode duration | **45 min** | Industry average |
| Episodes played / user / day | **~2** | 45 min / ~22.5 min avg play session |
| New episodes uploaded / day | **1,000,000** | 5M active podcasts × 0.2 episodes/week |
| Total podcasts | 5,000,000 | |
| Total episodes in corpus | 50,000,000 | 10 avg per podcast |
| Audio bitrate (streaming) | **128 kbps** | Standard high-quality MP3 |
| Audio bitrate (live streaming) | **256 kbps** | Higher quality for live |
| CDN cache hit ratio | **95%** | Audio is immutable after publish |
| Peak multiplier | **3×** | Evening hours 8–11pm local time |
| Read : Write ratio | **1000:1** | Streaming platform is extremely read-heavy |

---

## 1. Streaming Traffic

### 1.1 Stream Start Requests/sec

```
Daily stream starts = 200M DAU × 2 episodes = 400M streams/day

Average RPS = 400,000,000 / 86,400 s/day    = 4,630 stream starts/sec
Peak RPS    = 4,630 × 3 (peak multiplier)   ≈ 14,000 stream starts/sec
```

### 1.2 Concurrent Listeners

```
Total listening seconds/day = 200M DAU × 45 min × 60 s = 540,000,000,000 s

Average concurrent listeners = 540B seconds / 86,400 s/day  = 6,250,000
Peak concurrent listeners    = 6.25M × 3                     ≈ 18,750,000
```

### 1.3 Streaming Bandwidth

```
Audio bitrate = 128 kbps = 16 KB/s per stream

Average bandwidth = 6.25M  × 16 KB/s = 100,000,000 KB/s = 100 GB/s = 800 Gbps
Peak bandwidth    = 18.75M × 16 KB/s = 300,000,000 KB/s = 300 GB/s = 2.4 Tbps

CDN handles: 95% cache hit
Origin (GCS) traffic:
  Average: 800 Gbps × 5%  = 40 Gbps
  Peak:    2.4 Tbps × 5%  = 120 Gbps
```

> **Key number: 2.4 Tbps peak bandwidth** — this is why CDN is non-negotiable.

### 1.4 Live Streaming

```
Assumption: 1% of DAU are live listeners at any peak moment
Peak live listeners = 200M × 1% = 2,000,000

Assumption: 0.01% of 5M podcasters broadcast live simultaneously (peak event)
Peak live streams  = 5M × 0.01% = 500 concurrent live streams (avg)
                                 = 2,000 during a "SuperBowl moment"

Ingest bandwidth  (creator → platform): 2,000 × 256 kbps = 512 Mbps
Delivery bandwidth (platform → listeners): 2M × 256 kbps  = 512 Gbps
```

---

## 2. Upload Traffic

### 2.1 Upload Rate

```
1,000,000 new episodes / 86,400 s     = 11.6 uploads/sec avg
Peak (3×)                              ≈ 35 uploads/sec
```

### 2.2 Episode File Sizes

```
Raw WAV uploaded (creator source):
  45 min × 16-bit stereo 44.1 kHz     ≈ 45 × 10 MB/min = 450 MB

Post-encoding per bitrate:
  192 kbps: 45 × 60 × 192,000 / 8    = 64.8 MB
  128 kbps: 45 × 60 × 128,000 / 8    = 43.2 MB
   64 kbps: 45 × 60 ×  64,000 / 8    = 21.6 MB
   32 kbps: 45 × 60 ×  32,000 / 8    = 10.8 MB
Total per episode (all bitrates)       ≈ 140 MB
```

### 2.3 Upload Bandwidth

```
Average: 11.6 uploads/sec × 450 MB (raw) = 5.2 GB/s = 42 Gbps
Peak:    35   uploads/sec × 450 MB       = 15.8 GB/s = 126 Gbps

Note: Creators upload raw/original once; platform transcodes internally.
Transcoded output stored in GCS (internal transfer, not internet egress).
```

### 2.4 Transcoding Workers Required

```
Processing time per episode (FFmpeg, cloud GPU/CPU):
  ~0.5× real-time per bitrate pass
  45 min episode × 0.5 = 22.5 min per bitrate
  4 bitrates in parallel per worker = 22.5 min per episode

Workers for steady state: 11.6 uploads/sec × 22.5 min / 60 = 4.4 ≈ 5 workers
Workers for peak + buffer: 35 × 22.5 / 60 × 3 safety factor ≈ 50 workers

GKE auto-scales transcoding jobs via Cloud Tasks queue depth signal.
```

---

## 3. Storage Requirements

### 3.1 Audio Storage Growth

```
Daily new audio (4 bitrates):
  1,000,000 episodes/day × 140 MB     = 140 TB/day = 140,000 GB/day

Annual new audio:
  140 TB/day × 365                    ≈ 51 PB/year

Existing corpus (50M episodes):
  50M × 140 MB                        = 7,000,000,000 MB = 7 PB
```

### 3.2 Non-Audio Storage

| Data Type | Size | Calculation |
|-----------|------|-------------|
| Podcast artwork | ~10 TB | 5M × 2 MB (3000×3000 JPEG) |
| Episode thumbnails | ~50 TB | 50M × ~1 MB short clips |
| Transcripts (full text) | ~4 TB existing + 29 TB/yr | 50M × 80 KB avg |
| Live stream recordings | ~5 TB/day | 2,000 streams × ~4 GB/hr × 2 hr avg |
| Database (Spanner) | ~5 TB | Metadata rows, small vs audio |
| Search index (ES) | ~500 GB | 50M doc titles/descriptions |
| Redis hot working set | ~50 GB | Sessions, hot episode cache |

### 3.3 Analytics Data

```
Raw play events: 4B events/day × 200 bytes = 800 GB/day

Pub/Sub retention (7 days): 800 GB × 7    = 5.6 TB (in-flight buffer)

BigQuery (analytics DW), compressed:
  800 GB / 5× compression               = 160 GB ingested/day
  Annual accumulation                    ≈ 58 TB/year cumulative

Cloud Logging (ops):                      ~10 TB/year
```

### 3.4 Total Storage Summary

| Category | Year 1 Total | YoY Growth |
|----------|-------------|------------|
| Audio files (all bitrates) | **58 PB** (7 PB existing + 51 PB new) | 51 PB/yr |
| Live stream recordings | ~1.8 PB | 1.8 PB/yr |
| Transcripts | ~33 TB | 29 TB/yr |
| Artwork / thumbnails | ~60 TB | 18 TB/yr |
| Analytics (BigQuery) | ~58 TB | 58 TB/yr |
| Logs + misc | ~10 TB | 10 TB/yr |
| Database (Spanner + PG) | ~10 TB | ~2 TB/yr |
| **Grand Total** | **~60 PB** | **~53 PB/yr** |

> **Dominant cost driver**: Audio file storage. Use GCS **Nearline** for episodes older than 90 days ($0.01/GB vs $0.02/GB standard). Saves ~$26M/year at scale.

---

## 4. RSS Feed Traffic

```
5M podcasts × avg 500 RSS subscribers × 3 different apps per subscriber
= 7.5B active RSS feed subscriptions

Apps poll every 4–8 hours (let's use 6h average):
RSS polls/day = 7.5B / 6 = 1.25B polls/day

Average RSS polls/sec = 1.25B / 86,400       = 14,468/sec
Peak RSS polls/sec (3×)                       ≈ 43,400/sec

Redis cache hit: 99%+ (feeds change at most once per publish event)
Actual RSS backend hits: 43,400 × 1%         ≈ 434 computations/sec
```

---

## 5. Analytics Event Traffic

```
Events per stream session:
  - play_start, play_pause × N, play_resume × N, play_end = ~10 avg
  - Position heartbeat every 30s: 45min episode / 0.5min = ~90 heartbeats

Let's use 10 explicit events + 90 heartbeats = ~100 events per session
(Heartbeats batch-sent every 5 min = 10 batches × 9 positions = 90 events)

Total events/day = 400M streams × 100 events = 40B events/day

Average events/sec = 40B / 86,400             = 462,963/sec
Peak events/sec (3×)                           = 1,388,889/sec

BUT: clients batch events into 30-second bundles before sending
Effective API calls for analytics/sec (peak) = ~140,000/sec
(400M streams × 3 peak × (100 events / 30 events per batch) / 86,400)
```

---

## 6. Database Load

### 6.1 Read QPS (with Caching)

```
Peak API RPS: 140,000
Average DB reads per API request: 5 (mix of hot and cold paths)
Theoretical DB reads/sec: 140,000 × 5 = 700,000

Redis cache hit rate: 85%
Actual persistent DB reads/sec: 700,000 × 15% = 105,000

Breakdown:
  Cloud Spanner (podcast/episode metadata): ~80,000 reads/sec
  Cloud SQL PostgreSQL (social, subscriptions): ~25,000 reads/sec
  Elasticsearch (search queries): ~1,400/sec
  Memorystore Redis (from app side): ~500,000 operations/sec
```

### 6.2 Write QPS

```
Playback position updates:
  6.25M concurrent × 1 write per 30s to Redis    = 208,333 Redis writes/sec
  Async flush to Spanner every 5 min              = 6.25M / 300 = 20,833 writes/sec

Social writes (comments, ratings, follows):        ~5,000 writes/sec
Upload metadata writes:                            ~35 writes/sec
Analytics (to Pub/Sub, not DB directly):           140,000 messages/sec
Payment / subscription writes:                     <100 writes/sec

Total persistent DB writes:                        ~26,000 writes/sec
  Spanner: ~21,000 (position + metadata)
  PostgreSQL: ~5,000 (social + subscriptions)
```

---

## 7. Summary: Numbers to Memorize

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| Peak concurrent streams | **18.75M** | Sizing streaming infra |
| Peak CDN bandwidth | **2.4 Tbps** | CDN is non-negotiable |
| Average origin bandwidth | **40 Gbps** | GCS egress cost driver |
| Daily new audio storage | **140 TB** | Storage cost planning |
| Year 1 total storage | **~60 PB** | Nearline tier decision |
| Audio corpus day-1 (50M eps) | **7 PB** | Migration planning |
| Peak analytics events/sec | **1.4M raw → 140K batched** | Pub/Sub sizing |
| Peak API RPS | **140,000** | Apigee + GKE sizing |
| Peak RSS polls/sec | **43,400** | Redis cache is critical |
| Peak live listeners | **2M** | Live stream CDN cap |
| Transcoding workers (peak) | **50** | Cloud Tasks queue depth |
