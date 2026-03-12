# 4. Database Design

---

## 4.1 Database Technology Choices

| Store | Technology | Why |
|-------|-----------|-----|
| Primary RDBMS | **Cloud SQL (PostgreSQL 15)** | ACID transactions, relational data (users, listings, flags) |
| Global distribution | **Cloud Spanner** | Horizontally scalable SQL for global listing reads |
| Search | **Elasticsearch 8** | Full-text search + geo queries, complex facets |
| Cache | **Memorystore (Redis 7)** | Session data, hot listings, rate limit counters |
| Object Storage | **Google Cloud Storage** | Images, attachments |
| Analytics | **BigQuery** | Event logs, search analytics, BI reporting |
| Time-series | **Cloud Monitoring** | System metrics (not application data) |

---

## 4.2 Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    users    │1     N│     listings      │N     N│  categories │
│─────────────│───────│──────────────────│───────│─────────────│
│ id (PK)     │       │ id (PK)          │       │ id (PK)     │
│ email       │       │ user_id (FK)     │       │ name        │
│ display_name│       │ category_id (FK) │       │ parent_id   │
│ phone_hash  │       │ title            │       │ slug        │
│ password_hash       │ description      │       └─────────────┘
│ status      │       │ price            │
│ email_verified      │ price_type       │       ┌─────────────┐
│ created_at  │       │ status           │1     N│listing_images│
│ updated_at  │       │ location_id (FK) │───────│─────────────│
└─────────────┘       │ expires_at       │       │ id (PK)     │
                      │ view_count       │       │ listing_id  │
                      │ is_promoted      │       │ image_id    │
                      │ created_at       │       │ sort_order  │
                      │ updated_at       │       └─────────────┘
                      └──────────────────┘
                               │1
                               │N
                      ┌────────────────┐      ┌──────────────────┐
                      │     flags      │      │  saved_searches  │
                      │────────────────│      │──────────────────│
                      │ id (PK)        │      │ id (PK)          │
                      │ listing_id (FK)│      │ user_id (FK)     │
                      │ reporter_id    │      │ name             │
                      │ reason         │      │ search_params    │
                      │ details        │      │ notify           │
                      │ status         │      │ last_notified_at │
                      │ created_at     │      │ created_at       │
                      └────────────────┘      └──────────────────┘

                      ┌────────────────┐      ┌──────────────────┐
                      │   locations    │      │     messages     │
                      │────────────────│      │──────────────────│
                      │ id (PK)        │      │ id (PK)          │
                      │ city           │      │ listing_id (FK)  │
                      │ state          │      │ sender_email_hash│
                      │ country        │      │ message_text     │
                      │ zip            │      │ status           │
                      │ lat            │      │ created_at       │
                      │ lng            │      └──────────────────┘
                      │ neighborhood   │
                      └────────────────┘
```

---

## 4.3 PostgreSQL Schema (DDL)

### Users Table
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    email_verified  BOOLEAN DEFAULT FALSE,
    display_name    VARCHAR(100) NOT NULL,
    phone_hash      VARCHAR(64),                     -- SHA-256 of phone, NOT plaintext
    password_hash   VARCHAR(255),                    -- bcrypt, NULL for OAuth users
    oauth_provider  VARCHAR(50),                     -- 'google', 'facebook', NULL
    oauth_sub       VARCHAR(255),                    -- OAuth subject identifier
    status          VARCHAR(20) DEFAULT 'active'     -- active, suspended, deleted
                    CHECK (status IN ('active','suspended','deleted')),
    post_count      INT DEFAULT 0,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status) WHERE status != 'deleted';
```

---

### Categories Table
```sql
CREATE TABLE categories (
    id          VARCHAR(50) PRIMARY KEY,             -- e.g., 'cat_housing_rentals'
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    parent_id   VARCHAR(50) REFERENCES categories(id),
    icon_url    TEXT,
    sort_order  INT DEFAULT 0,
    is_active   BOOLEAN DEFAULT TRUE
);

-- Seed data example
INSERT INTO categories VALUES
  ('cat_housing', 'Housing', 'housing', NULL, NULL, 1, TRUE),
  ('subcat_apts', 'Apts/Housing For Rent', 'apts', 'cat_housing', NULL, 1, TRUE),
  ('cat_jobs', 'Jobs', 'jobs', NULL, NULL, 2, TRUE),
  ('cat_forsale', 'For Sale', 'for-sale', NULL, NULL, 3, TRUE);
```

---

### Locations Table
```sql
CREATE TABLE locations (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city          VARCHAR(100) NOT NULL,
    state         VARCHAR(50),
    country       VARCHAR(2) NOT NULL DEFAULT 'US',
    zip           VARCHAR(20),
    neighborhood  VARCHAR(100),
    lat           DECIMAL(9,6) NOT NULL,
    lng           DECIMAL(9,6) NOT NULL,
    geo_point     GEOGRAPHY(POINT, 4326) GENERATED ALWAYS AS
                  (ST_SetSRID(ST_MakePoint(lng, lat), 4326)) STORED
);

CREATE INDEX idx_locations_geo ON locations USING GIST(geo_point);
CREATE INDEX idx_locations_city_state ON locations(city, state);
```

---

### Listings Table
```sql
CREATE TABLE listings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    category_id     VARCHAR(50) NOT NULL REFERENCES categories(id),
    location_id     UUID NOT NULL REFERENCES locations(id),

    title           VARCHAR(300) NOT NULL,
    description     TEXT NOT NULL,
    price           DECIMAL(12,2),
    price_type      VARCHAR(20)                       -- 'fixed', 'negotiable', 'free', 'monthly'
                    CHECK (price_type IN ('fixed','negotiable','free','monthly','hourly')),

    status          VARCHAR(20) DEFAULT 'active'
                    CHECK (status IN ('active','expired','sold','deleted','draft','ghost')),

    contact_method  VARCHAR(20) DEFAULT 'email'
                    CHECK (contact_method IN ('email','phone','both')),
    show_phone      BOOLEAN DEFAULT FALSE,

    tags            TEXT[],                           -- searchable tags array
    is_promoted     BOOLEAN DEFAULT FALSE,
    promoted_until  TIMESTAMPTZ,

    view_count      BIGINT DEFAULT 0,
    flag_count      INT DEFAULT 0,

    thumbnail_image_id  UUID,
    image_count     SMALLINT DEFAULT 0,

    idempotency_key UUID UNIQUE,                      -- prevent duplicate posts
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ                       -- soft delete
);

-- Indexes
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_category ON listings(category_id);
CREATE INDEX idx_listings_location ON listings(location_id);
CREATE INDEX idx_listings_status ON listings(status) WHERE status = 'active';
CREATE INDEX idx_listings_expires_at ON listings(expires_at) WHERE status = 'active';
CREATE INDEX idx_listings_created_at ON listings(created_at DESC);
CREATE INDEX idx_listings_price ON listings(price) WHERE price IS NOT NULL;
CREATE INDEX idx_listings_tags ON listings USING GIN(tags);

-- Composite index for common query pattern
CREATE INDEX idx_listings_category_location_created
    ON listings(category_id, location_id, created_at DESC)
    WHERE status = 'active';
```

---

### Images Table
```sql
CREATE TABLE images (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id      UUID REFERENCES listings(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id),

    original_path   TEXT NOT NULL,                   -- GCS path
    thumbnail_url   TEXT,
    medium_url      TEXT,
    large_url       TEXT,

    width           INT,
    height          INT,
    file_size_bytes BIGINT,
    content_type    VARCHAR(50),

    processing_status VARCHAR(20) DEFAULT 'pending'
                    CHECK (processing_status IN ('pending','processing','ready','failed')),
    sort_order      SMALLINT DEFAULT 0,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_images_listing_id ON images(listing_id);
CREATE INDEX idx_images_status ON images(processing_status) WHERE processing_status != 'ready';
```

---

### Flags Table
```sql
CREATE TABLE flags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id      UUID NOT NULL REFERENCES listings(id),
    reporter_id     UUID REFERENCES users(id),        -- NULL for anonymous reports
    reporter_ip     INET,

    reason          VARCHAR(30) NOT NULL
                    CHECK (reason IN ('spam','wrong_category','prohibited','scam','offensive','already_sold','other')),
    details         TEXT,
    status          VARCHAR(20) DEFAULT 'pending'
                    CHECK (status IN ('pending','reviewed','dismissed','actioned')),
    reviewed_by     UUID REFERENCES users(id),        -- admin user
    reviewed_at     TIMESTAMPTZ,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_flags_listing_id ON flags(listing_id);
CREATE INDEX idx_flags_status ON flags(status) WHERE status = 'pending';
```

---

### Saved Searches Table
```sql
CREATE TABLE saved_searches (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    name            VARCHAR(200),
    search_params   JSONB NOT NULL,                   -- stores all search criteria
    notify          BOOLEAN DEFAULT TRUE,
    notify_frequency VARCHAR(20) DEFAULT 'daily'
                    CHECK (notify_frequency IN ('instant','daily','weekly')),
    last_notified_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX idx_saved_searches_notify ON saved_searches(notify, notify_frequency)
    WHERE notify = TRUE;
```

---

### Messages Table (Contact Relay)
```sql
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id      UUID NOT NULL REFERENCES listings(id),
    sender_email_hash VARCHAR(64) NOT NULL,           -- SHA-256 of sender email
    message_hash    VARCHAR(64),                      -- dedup check
    status          VARCHAR(20) DEFAULT 'queued'
                    CHECK (status IN ('queued','sent','failed','spam')),
    spam_score      DECIMAL(3,2),
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_listing_id ON messages(listing_id);
```

---

## 4.4 Elasticsearch Index Schema

### listings_index mapping
```json
{
  "mappings": {
    "properties": {
      "listing_id":    { "type": "keyword" },
      "title":         { "type": "text", "analyzer": "english",
                         "fields": { "raw": { "type": "keyword" } }},
      "description":   { "type": "text", "analyzer": "english" },
      "category_id":   { "type": "keyword" },
      "category_name": { "type": "keyword" },
      "price":         { "type": "double" },
      "price_type":    { "type": "keyword" },
      "status":        { "type": "keyword" },
      "tags":          { "type": "keyword" },
      "has_image":     { "type": "boolean" },
      "is_promoted":   { "type": "boolean" },
      "view_count":    { "type": "integer" },
      "thumbnail_url": { "type": "keyword", "index": false },
      "location": {
        "properties": {
          "city":         { "type": "keyword" },
          "state":        { "type": "keyword" },
          "neighborhood": { "type": "keyword" },
          "zip":          { "type": "keyword" },
          "geo_point":    { "type": "geo_point" }
        }
      },
      "created_at":    { "type": "date" },
      "expires_at":    { "type": "date" }
    }
  },
  "settings": {
    "number_of_shards": 6,
    "number_of_replicas": 1,
    "index.refresh_interval": "30s"
  }
}
```

---

## 4.5 Redis Key Design (Memorystore)

```
# Hot listing cache (TTL: 10 min)
listing:{listing_id}                        → JSON blob of listing

# User session (TTL: 1 hour, sliding)
session:{session_id}                        → { user_id, email, roles }

# Rate limiting counters
ratelimit:post:account:{user_id}            → count (TTL: 24h)
ratelimit:post:ip:{ip_addr}                 → count (TTL: 1h)
ratelimit:contact:{user_id}                 → count (TTL: 1h)
ratelimit:search:{ip_addr}                  → count (TTL: 1min)

# Search result cache (TTL: 5 min for top queries)
search:{hash_of_params}                     → JSON results

# Category tree cache (TTL: 1 hour)
categories:all                              → JSON category tree

# Trending listings per city (TTL: 30 min)
trending:{city_slug}:{category_id}          → [listing_id, listing_id, ...]

# View count accumulator (flushed to Postgres every 5 min)
view_count:{listing_id}                     → integer
```

---

## 4.6 Data Partitioning Strategy

### PostgreSQL Partitioning
```sql
-- Partition listings by created_at (monthly partitions)
CREATE TABLE listings (
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE listings_2026_03 PARTITION OF listings
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

CREATE TABLE listings_2026_04 PARTITION OF listings
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
```

### Elasticsearch Sharding
- 6 primary shards across data nodes
- Shard routing by `location.state` to co-locate geo queries
- Monthly index rollover for archival (via ILM policy)

### Cloud Spanner
- Listing data distributed globally by `city_region` interleave key
- Eliminates hot spots on sequential listing IDs

---

## 4.7 Data Lifecycle & Retention

| Data Type | Retention | Action After |
|-----------|-----------|-------------|
| Active listings | Per category (7–45 days) | Auto-expire → status='expired' |
| Expired listings (data) | 90 days | Soft delete, removed from search |
| Deleted listings (data) | 30 days | Hard delete from DB |
| Images (originals) | 90 days post-expiry | GCS lifecycle → delete |
| Images (thumbnails) | 30 days post-expiry | GCS lifecycle → delete |
| Messages | 90 days | Archived to BigQuery |
| Flags | 1 year | Archived to BigQuery |
| User accounts | Until deletion request | GDPR: delete within 30 days of request |
| Analytics events | 2 years | BigQuery, partitioned by month |
