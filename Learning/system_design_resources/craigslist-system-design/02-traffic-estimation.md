# 2. Traffic Estimation & Data Calculations

---

## 2.1 User Traffic Estimates

### Base Assumptions

| Parameter | Value |
|-----------|-------|
| Monthly Active Users (MAU) | 50,000,000 |
| Daily Active Users (DAU) | ~10,000,000 (20% of MAU) |
| Peak concurrent users | ~500,000 (5% of DAU) |
| Read:Write ratio | 100:1 |

### Requests Per Second (RPS)

```
Daily read requests:
  DAU × avg requests per session = 10M × 15 = 150M reads/day
  150M / 86,400 seconds = ~1,736 reads/sec (avg)
  Peak multiplier (3×) = ~5,200 reads/sec

Daily write requests (listings + updates):
  New listings/day:  1,000,000
  Listing updates:     200,000
  User registrations:   50,000
  Image uploads:     5,000,000 (avg 5 per listing)
  Total writes/day: ~6,250,000
  6.25M / 86,400 = ~72 writes/sec (avg)
  Peak writes/sec:   ~220 writes/sec

Search queries:
  ~10M searches/day
  10M / 86,400 = ~116 searches/sec
  Peak search RPS: ~350/sec

Email sends (notifications):
  ~5M emails/day = ~58 emails/sec
```

---

## 2.2 Storage Estimates

### Listing Storage

```
Per listing metadata (PostgreSQL row):
  id:            8 bytes  (UUID)
  user_id:       8 bytes
  title:       200 bytes  (avg 80 chars)
  description: 4,000 bytes (avg ~1000 chars)
  category:      20 bytes
  price:          8 bytes
  location:      50 bytes
  status:         8 bytes
  created_at:     8 bytes
  expires_at:     8 bytes
  tags:         100 bytes
  ---------------------------
  Total per listing: ~4,420 bytes ≈ ~4.5 KB

Daily new listings: 1,000,000
Daily metadata storage: 1M × 4.5 KB = 4.5 GB/day
Annual metadata storage: 4.5 GB × 365 = ~1.6 TB/year

Active listing pool (45 day max):
  1M × 45 days × 4.5 KB = ~200 GB active at any time
```

### Image Storage

```
Per image sizes:
  Original upload (user submitted): avg 3 MB
  Large (1200px): avg 500 KB
  Medium (600px): avg 150 KB
  Thumbnail (150px): avg 20 KB
  Total stored per image: 3 MB + 500 + 150 + 20 KB ≈ 3.67 MB

Images per listing: avg 5
Storage per listing: 5 × 3.67 MB = 18.35 MB

Daily image storage: 1M listings × 18.35 MB = 18.35 TB/day
Annual image storage: 18.35 TB × 365 ≈ 6.7 PB/year

Note: Images are stored on Cloud Storage (GCS).
      Lifecycle policy: originals deleted after 90 days post-expiry.
      Resized variants retained for active listings only.
```

### Search Index (Elasticsearch)

```
Elasticsearch index size per document: ~10 KB
  (title, description, location, tags, metadata)

Active listings indexed: 45M (45 days × 1M/day)
Total index size: 45M × 10 KB = 450 GB
With Elasticsearch replica (×2): 900 GB
With overhead (1.5×): ~1.35 TB
```

### Cache (Memorystore / Redis)

```
Hot listings cache:
  Top 1% of listings get 80% of traffic
  45M × 1% = 450,000 hot listings
  Per listing cache entry: ~5 KB
  Cache size needed: 450K × 5 KB = ~2.25 GB

Session cache:
  500K concurrent users × 500 bytes = ~250 MB

Search result cache:
  Top 10K queries cached × 10 KB = ~100 MB

Total Redis memory: ~3 GB (active), provision 8 GB
```

---

## 2.3 Bandwidth Estimates

```
Outbound (reads):
  Average response size (listing page): 50 KB (HTML + data, no images)
  Images served via CDN (not counted in API bandwidth)
  API reads/sec: 5,200 peak
  API bandwidth: 5,200 × 50 KB = ~260 MB/sec = ~2 Gbps peak

Image CDN bandwidth:
  Avg 5 images per page view × 150 KB (medium) = 750 KB
  10M page views/day × 750 KB = 7.5 TB/day outbound via CDN

Inbound (writes/uploads):
  Image uploads: 5M/day × 3 MB avg = 15 TB/day inbound
  15 TB / 86,400 sec = ~170 MB/sec = ~1.3 Gbps avg inbound
  Peak inbound: ~4 Gbps
```

---

## 2.4 Database Sizing

```
PostgreSQL (Cloud SQL):
  Users table:         50M rows × 300 bytes = 15 GB
  Listings table:      45M rows × 4.5 KB   = ~200 GB (active)
  Categories table:    ~1,000 rows (negligible)
  Flags/reports table: ~5M rows × 200 bytes = 1 GB
  Sessions table:      500K rows × 500 bytes = 250 MB (Redis preferred)
  Total PostgreSQL:    ~220 GB

Cloud Spanner (global listing distribution):
  Replica of listings for global reads
  Estimate: ~220 GB + overhead = ~300 GB

BigQuery (analytics):
  Event streams, search logs, click data
  ~100M events/day × 500 bytes = 50 GB/day
  Annual: ~18 TB
```

---

## 2.5 Summary of Numbers for Interview

| Resource | Estimate |
|----------|----------|
| Read RPS (peak) | ~5,200 |
| Write RPS (peak) | ~220 |
| Search RPS (peak) | ~350 |
| Storage: Listing metadata/year | ~1.6 TB |
| Storage: Images/year | ~6.7 PB |
| Elasticsearch index | ~1.35 TB |
| Redis cache | ~8 GB |
| CDN bandwidth | ~7.5 TB/day |
| Inbound image bandwidth | ~15 TB/day |
| Emails sent/day | ~5M |

---

## 2.6 GCP Sizing Recommendations

```
GKE Node Pools:
  API services:       8× n2-standard-8  (32 vCPU, 128 GB total)
  Search services:    4× n2-standard-8
  Image processing:   4× n2-standard-4  (burstable)

Cloud SQL (PostgreSQL):
  Instance type: db-n1-standard-16 (16 vCPU, 60 GB RAM)
  Storage: 1 TB SSD with auto-expand
  Read replicas: 2 (for read scaling)

Elasticsearch (self-managed on GCE or managed via Elastic Cloud):
  Master nodes: 3× n2-standard-4
  Data nodes:   6× n2-highmem-16 (for 1.35 TB index)
  Total: 9 nodes

Memorystore (Redis):
  Tier: Standard (HA)
  Size: 16 GB instance

Cloud Storage:
  Multi-regional bucket (US + EU)
  Lifecycle policy: transition to Nearline after 90 days

Cloud Pub/Sub:
  Topics: listings-events, notification-events, search-index-updates
```
