# 02 — Traffic & Capacity Estimation

## System: Photo Sharing Service (Instagram-Scale)

---

## Key Scale Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Monthly Active Users (MAU) | 500M | Assumption |
| Daily Active Users (DAU) | 100M | 20% of MAU |
| Peak multiplier | 3× average | Standard rule of thumb |
| Photo:Video ratio | 70:30 | Assumption |
| Read:Write ratio | 100:1 | Typical social media |

---

## 1. Write Traffic (Uploads)

### Photos

```
Uploads per user per day   = 2 (avg across all DAU)
Total photo+video uploads  = 100M DAU × 2 = 200M uploads/day

Photo uploads (70%)        = 140M photos/day
Video uploads (30%)        = 60M videos/day

Photo uploads/sec (avg)    = 140M / 86,400 ≈ 1,620 uploads/sec
Photo uploads/sec (peak)   = 1,620 × 3 ≈ 4,860 uploads/sec

Video uploads/sec (avg)    = 60M / 86,400 ≈ 695 uploads/sec
Video uploads/sec (peak)   = 695 × 3 ≈ 2,085 uploads/sec

Total upload RPS (peak)    ≈ 7,000 uploads/sec
```

### Other Writes

```
Likes per user per day     = 20
Total likes/day            = 100M × 20 = 2B likes/day
Likes/sec (avg)            = 2B / 86,400 ≈ 23,150 likes/sec
Likes/sec (peak)           = 23,150 × 3 ≈ 70,000 likes/sec

Comments per user per day  = 3
Total comments/day         = 100M × 3 = 300M comments/day
Comments/sec (avg)         = 300M / 86,400 ≈ 3,470/sec
Comments/sec (peak)        ≈ 10,400/sec

Follows per user per day   = 2
Total follows/day          = 100M × 2 = 200M/day
Follows/sec (avg)          ≈ 2,315/sec
Follows/sec (peak)         ≈ 7,000/sec
```

---

## 2. Read Traffic

### Feed Requests

```
Feed refreshes per user per day = 10
Total feed requests/day     = 100M × 10 = 1B/day
Feed RPS (avg)              = 1B / 86,400 ≈ 11,600/sec
Feed RPS (peak)             = 11,600 × 3 ≈ 35,000/sec
```

### Photo Views

```
Photo views per user per day = 50
Total photo views/day       = 100M × 50 = 5B views/day
Photo views/sec (avg)       = 5B / 86,400 ≈ 57,900/sec
Photo views/sec (peak)      = 57,900 × 3 ≈ 174,000/sec

Note: ~95% served from CDN cache (CDN hit ratio: 95%)
Origin photo requests/sec   = 174,000 × 0.05 ≈ 8,700/sec
```

### Profile & Search

```
Profile views/day           = 100M × 5 = 500M/day   →  5,800/sec avg
Search requests/day         = 100M × 3 = 300M/day   →  3,470/sec avg
```

---

## 3. Storage Estimation

### Per-Photo Storage (3 variants generated server-side)

| Variant | Resolution | Size | Purpose |
|---------|-----------|------|---------|
| Thumbnail | 150×150 | 15KB | Grid view, notifications |
| Medium | 640×640 | 150KB | Mobile feed |
| HD | 1080×1080 | 600KB | Desktop feed / full view |
| Original | variable | 3MB | Download, backup |

```
Storage per photo (all variants) = 15KB + 150KB + 600KB + 3MB ≈ 3.75MB

Photos per day          = 140M
Storage per day (photos) = 140M × 3.75MB ≈ 525 TB/day
```

### Per-Video Storage

```
Average video (60s, compressed) = 50MB
Processed variants (3 bitrates) ≈ 75MB total per video

Videos per day          = 60M
Storage per day (videos) = 60M × 75MB ≈ 4.5 PB/day
```

### Total Media Storage

```
Photos/day              = 525 TB/day
Videos/day              = 4,500 TB/day (4.5 PB/day)
Total media/day         ≈ 5 PB/day

Annual media storage    = 5 PB × 365 ≈ 1,825 PB ≈ 1.8 EB/year

With 3× replication (GCS multi-region):
Actual storage needed   = 1.8 EB × 3 ≈ 5.4 EB/year

Note: GCS handles this natively with multi-region buckets.
Hot tier (< 30 days): ~150 PB
Warm tier (30d–1yr):  ~400 PB
Cold tier (> 1yr):    Nearline/Coldline on GCS
```

### Database Storage

```
Users table:
  - 500M users × 500 bytes/row ≈ 250 GB

Posts table:
  - 200M new posts/day × 365 days × 200 bytes/row = ~14.6 TB/year

Likes table:
  - 2B likes/day × 365 days × 50 bytes/row = ~36.5 TB/year

Comments table:
  - 300M comments/day × 365 × 300 bytes = ~32.9 TB/year

Follow graph:
  - 500M users × 300 follows average × 16 bytes = ~2.4 TB

Feed cache (Redis):
  - 100M DAU × 100 post IDs × 8 bytes = ~80 GB hot key cache
```

---

## 4. Bandwidth Estimation

### Upload Bandwidth

```
Photo uploads at peak: 4,860/sec × 3MB = 14.6 GB/s inbound
Video uploads at peak: 2,085/sec × 50MB = 104 GB/s inbound

Total upload bandwidth (peak) ≈ 120 GB/s inbound
```

### Download Bandwidth (Origin, post-CDN)

```
CDN hit ratio = 95%
Origin photo requests at peak = 8,700/sec × 0.6MB (HD avg) = 5.2 GB/s
Origin video requests (est.)  ≈ 30 GB/s

Total origin egress ≈ 35 GB/s
```

### CDN Bandwidth

```
CDN serves: 174,000 photo views/sec × 0.5MB (avg) = 87 GB/s
CDN video:  est. 50 GB/s

Total CDN egress ≈ 137 GB/s globally
```

---

## 5. Summary Table

| Metric | Average | Peak |
|--------|---------|------|
| Total uploads (photos + videos) | ~2,315/sec | ~7,000/sec |
| Feed requests | ~11,600/sec | ~35,000/sec |
| Photo views | ~57,900/sec | ~174,000/sec |
| Likes | ~23,150/sec | ~70,000/sec |
| Comments | ~3,470/sec | ~10,400/sec |
| Upload bandwidth | ~40 GB/s | ~120 GB/s |
| CDN egress | ~46 GB/s | ~137 GB/s |
| New media storage/day | ~5 PB | — |
| Total storage/year (3× replicated) | ~5.4 EB | — |

---

## 6. Infrastructure Sizing (GCP)

### GKE Services (Autopilot — auto-scales)

| Service | Avg Pods | Peak Pods | vCPU/pod | Memory/pod |
|---------|----------|-----------|----------|------------|
| Media Upload Service | 50 | 200 | 2 | 4GB |
| Feed Service | 100 | 400 | 4 | 8GB |
| Like/Comment Service | 80 | 320 | 2 | 4GB |
| User/Auth Service | 30 | 120 | 2 | 4GB |
| Notification Service | 40 | 160 | 2 | 4GB |
| Search Service | 20 | 80 | 4 | 16GB |

### Database Sizing

| Store | Size | Instance |
|-------|------|----------|
| Cloud SQL (PostgreSQL) — Users, Posts, Comments | ~50 TB | db-custom-64-262144 (HA) |
| Cloud Bigtable — Likes, Media metadata | ~100 TB | 50-node cluster |
| Memorystore Redis — Feed cache | ~500 GB | Standard HA, 3 replicas |
| Cloud Spanner — Follow graph | ~3 TB | 10-node regional |
| Elasticsearch (GCE) — Search | ~10 TB | 20-node cluster |
| Cloud Storage (GCS) — Media | Multi-exabyte | Multi-region bucket |
