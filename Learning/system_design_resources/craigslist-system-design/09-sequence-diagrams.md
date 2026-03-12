# 9. Sequence Diagrams & Request Flows

---

## 9.1 User Registration Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client as Client (Browser/App)
    participant Apigee as Apigee Gateway
    participant UserSvc as User Service
    participant Firebase as Firebase Auth
    participant DB as Cloud SQL
    participant Tasks as Cloud Tasks
    participant Email as Email Provider

    User->>Client: Fill registration form
    Client->>Apigee: POST /api/v1/auth/register
    Apigee->>Apigee: Rate limit check (10 req/15min per IP)
    Apigee->>UserSvc: Forward request
    UserSvc->>DB: SELECT * FROM users WHERE email = ?
    DB-->>UserSvc: [] (no existing user)
    UserSvc->>Firebase: createUser(email, password)
    Firebase-->>UserSvc: { firebase_uid }
    UserSvc->>DB: INSERT INTO users (...)
    DB-->>UserSvc: { user_id }
    UserSvc->>Tasks: Enqueue: send verification email
    Tasks-->>UserSvc: OK
    UserSvc-->>Client: 201 { user_id, verification_sent: true }
    Tasks->>Email: Send verification email
    Email->>User: 📧 Verification email
```

---

## 9.2 Create Listing Flow

```mermaid
sequenceDiagram
    autonumber
    actor Owner
    participant Client
    participant Apigee as Apigee Gateway
    participant ListingSvc as Listing Service
    participant ModSvc as Moderation Service
    participant Redis as Memorystore (Redis)
    participant DB as Cloud SQL (PostgreSQL)
    participant PubSub as Cloud Pub/Sub
    participant SearchSvc as Search Service
    participant ES as Elasticsearch

    Owner->>Client: Fill listing form + images
    Client->>Apigee: POST /api/v1/listings\n(Idempotency-Key: uuid123)
    Apigee->>Apigee: Validate JWT token
    Apigee->>ListingSvc: Forward request
    
    ListingSvc->>Redis: GET idempotency:uuid123
    Redis-->>ListingSvc: nil (first request)

    ListingSvc->>Redis: INCR ratelimit:post:account:{user_id}
    Redis-->>ListingSvc: 2 (under limit of 5)

    ListingSvc->>ModSvc: POST /check-spam (title, description, ip)
    ModSvc-->>ListingSvc: { spam_score: 0.1, action: "allow" }

    ListingSvc->>DB: INSERT INTO listings (...)\nWHERE idempotency_key = uuid123
    DB-->>ListingSvc: { listing_id: "lst_01" }

    ListingSvc->>Redis: SET idempotency:uuid123 → "lst_01" TTL=24h

    ListingSvc->>PubSub: Publish listing.created event\n{ listing_id, title, location, category }
    PubSub-->>ListingSvc: messageId

    ListingSvc-->>Client: 201 { listing_id, url, expires_at }

    Note over PubSub, ES: Async — happens within 30 seconds
    PubSub->>SearchSvc: Deliver listing.created message
    SearchSvc->>ES: PUT /listings/_doc/{listing_id}
    ES-->>SearchSvc: indexed OK
    SearchSvc->>PubSub: ACK message
```

---

## 9.3 Search Listing Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client
    participant Apigee
    participant SearchSvc as Search Service
    participant Redis as Memorystore (Redis)
    participant ES as Elasticsearch
    participant PubSub as Cloud Pub/Sub
    participant BQ as BigQuery

    User->>Client: Search "apartment SF $2500 max"
    Client->>Apigee: GET /api/v1/listings/search\n?q=apartment&city=SF&max_price=2500
    Apigee->>Apigee: Rate limit check (100/min per IP)
    Apigee->>SearchSvc: Forward request

    SearchSvc->>SearchSvc: Build cache key\nSHA256(query params) = "abc123"
    SearchSvc->>Redis: GET search:abc123
    
    alt Cache HIT
        Redis-->>SearchSvc: Cached JSON results
        SearchSvc-->>Client: 200 { results, from_cache: true }
    else Cache MISS
        Redis-->>SearchSvc: nil
        SearchSvc->>ES: POST /listings/_search\n(bool query + geo filter + price filter)
        ES-->>SearchSvc: { hits, aggregations, total }
        SearchSvc->>SearchSvc: Enrich results\n(add thumbnail URLs)
        SearchSvc->>Redis: SET search:abc123 → results TTL=5min
        SearchSvc-->>Client: 200 { results, facets, next_cursor }
    end

    Note over SearchSvc, BQ: Async analytics
    SearchSvc->>PubSub: Publish search.executed event
    PubSub->>BQ: Stream to BigQuery search_events table
```

---

## 9.4 Image Upload Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client
    participant Apigee
    participant ImageSvc as Image Service
    participant DB as Cloud SQL
    participant GCS as Cloud Storage
    participant CloudFn as Cloud Function\n(Image Processor)
    participant CDN as Cloud CDN

    User->>Client: Select photo to upload
    Client->>Apigee: POST /api/v1/images/upload-url\n{ filename, content_type, file_size }
    Apigee->>ImageSvc: Forward request
    ImageSvc->>DB: INSERT INTO images (status='pending')
    DB-->>ImageSvc: { image_id }
    ImageSvc->>GCS: Generate signed upload URL\n(PUT, TTL=15min, max-size=10MB)
    GCS-->>ImageSvc: signed_url
    ImageSvc-->>Client: { image_id, upload_url }

    Client->>GCS: PUT <signed_url> (image bytes directly)
    Note right of GCS: Image lands in gs://craigslist-uploads/
    GCS-->>Client: 200 OK

    Note over GCS, CDN: Async processing triggered by GCS event
    GCS->>CloudFn: Trigger: object.finalize event
    CloudFn->>GCS: Download original image
    CloudFn->>CloudFn: Strip EXIF (remove GPS data)
    CloudFn->>CloudFn: Resize → thumbnail/medium/large (WebP)
    CloudFn->>GCS: Upload variants to gs://craigslist-processed/
    CloudFn->>DB: UPDATE images SET\nstatus='ready',\nthumbnail_url=..., medium_url=..., large_url=...

    Note over CDN: Subsequent image requests served from CDN
    User->>CDN: GET https://cdn.craigslist.com/img_01_thumb.webp
    CDN-->>User: Image (cached at edge)
```

---

## 9.5 Contact Poster Flow (Anonymous Email Relay)

```mermaid
sequenceDiagram
    autonumber
    actor Buyer
    participant Client
    participant Apigee
    participant ListingSvc as Listing Service
    participant ModSvc as Moderation Service
    participant PubSub as Cloud Pub/Sub
    participant NotifSvc as Notification Service
    participant Tasks as Cloud Tasks
    participant Email as Email Provider
    actor Poster

    Buyer->>Client: Type message, click "Send"
    Client->>Apigee: POST /api/v1/listings/{id}/contact\n{ message, reply_to_email }
    Apigee->>ListingSvc: Forward request
    
    ListingSvc->>ListingSvc: Rate limit check\n(20 contacts/hr per user)
    ListingSvc->>ModSvc: Score message for spam
    ModSvc-->>ListingSvc: { spam_score: 0.05 }
    
    ListingSvc->>ListingSvc: Generate anonymous relay token\nToken = HMAC(listing_id + buyer_email + timestamp)
    ListingSvc->>PubSub: Publish listing.contact event\n{ listing_id, relay_token, message_text, poster_user_id }
    PubSub-->>ListingSvc: OK
    ListingSvc-->>Client: 202 { message_id, status: "queued" }

    Note over PubSub, Poster: Async email relay
    PubSub->>NotifSvc: Deliver listing.contact message
    NotifSvc->>NotifSvc: Lookup poster email from user_id
    NotifSvc->>NotifSvc: Build relay email:\n From: reply-<token>@mail.craigslist.com\n To: poster@example.com\n Reply-To: reply-<token>@mail.craigslist.com
    NotifSvc->>Tasks: Enqueue email send
    Tasks->>Email: Send via SendGrid API
    Email->>Poster: 📧 "Someone is interested in your listing..."
    
    Note over Poster, Buyer: Poster replies to email
    Poster->>Email: Reply to relay address
    Email->>NotifSvc: Inbound webhook (reply received)
    NotifSvc->>NotifSvc: Lookup buyer email from relay token
    NotifSvc->>Email: Forward to buyer's real email
    Email->>Buyer: 📧 Reply from poster
```

---

## 9.6 Listing Expiry Flow

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Cloud Scheduler\n(Hourly cron)
    participant Tasks as Cloud Tasks
    participant Worker as Expiry Worker (GKE Job)
    participant DB as Cloud SQL
    participant PubSub as Cloud Pub/Sub
    participant SearchSvc as Search Service
    participant ES as Elasticsearch
    participant NotifSvc as Notification Service
    participant Email as Email Provider
    actor Owner

    Scheduler->>Tasks: Trigger: run-expiry-job
    Tasks->>Worker: Execute expiry job
    
    Worker->>DB: SELECT id, user_id FROM listings\nWHERE status='active'\nAND expires_at < NOW()\nLIMIT 10000

    loop For each expired listing
        Worker->>DB: UPDATE listings\nSET status='expired'\nWHERE id = ?
        Worker->>PubSub: Publish listing.expired\n{ listing_id, user_id }
    end

    Note over PubSub: Fan-out to subscribers
    PubSub->>SearchSvc: listing.expired event
    SearchSvc->>ES: DELETE /listings/_doc/{listing_id}
    ES-->>SearchSvc: OK
    SearchSvc->>PubSub: ACK

    PubSub->>NotifSvc: listing.expired event
    NotifSvc->>Email: Send "Your listing expired" email
    Email->>Owner: 📧 "Renew your listing?"
```

---

## 9.7 Saved Search Alert Flow

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Cloud Scheduler\n(Daily 8am)
    participant AlertWorker as Alert Worker
    participant DB as Cloud SQL
    participant SearchSvc as Search Service
    participant ES as Elasticsearch
    participant NotifSvc as Notification Service
    participant Email as Email Provider
    actor User

    Scheduler->>AlertWorker: Trigger: process-daily-alerts
    AlertWorker->>DB: SELECT * FROM saved_searches\nWHERE notify=true\nAND notify_frequency='daily'\nAND (last_notified_at < NOW() - INTERVAL '24h'\n     OR last_notified_at IS NULL)

    loop For each saved search
        AlertWorker->>SearchSvc: Execute saved search\n(posted_after: last_notified_at)
        SearchSvc->>ES: Query for new matching listings
        ES-->>SearchSvc: { new_listings }
        
        alt New listings found
            SearchSvc-->>AlertWorker: { results }
            AlertWorker->>NotifSvc: Send alert email\n{ user_id, search_name, results }
            NotifSvc->>Email: Render digest email template
            Email->>User: 📧 "5 new listings matching 'SF Apartments'"
            AlertWorker->>DB: UPDATE saved_searches\nSET last_notified_at = NOW()
        else No new listings
            SearchSvc-->>AlertWorker: []
            Note over AlertWorker: Skip - no email sent
        end
    end
```

---

## 9.8 Write Path + GCP Services Diagram

```mermaid
flowchart TD
    Client([Client]) -->|HTTPS| Armor[Cloud Armor\nWAF/DDoS]
    Armor --> GLB[Cloud Load Balancer\nGlobal HTTPS LB]
    GLB --> Apigee[Apigee\nAPI Gateway\nRate Limit / Auth]
    Apigee --> Firebase[Firebase Auth\nJWT Verification]
    Apigee --> ListingSvc[Listing Service\nGKE Pod]
    
    ListingSvc -->|Rate limit check| Redis[(Memorystore\nRedis)]
    ListingSvc -->|Spam check| ModSvc[Moderation Service\nGKE Pod]
    ListingSvc -->|Write listing| CloudSQL[(Cloud SQL\nPostgreSQL\nPrimary)]
    ListingSvc -->|Publish event| PubSub[Cloud Pub/Sub\nlistings-events]
    
    PubSub -->|listing.created| SearchConsumer[Search Consumer\nGKE Pod]
    PubSub -->|listing.created| Analytics[Analytics Consumer]
    
    SearchConsumer -->|Index document| ES[(Elasticsearch\non GCE)]
    Analytics -->|Stream| BQ[(BigQuery)]
    
    Client -->|Pre-signed URL upload| GCS[(Cloud Storage\nImages Bucket)]
    GCS -->|object.finalize trigger| CloudFn[Cloud Function\nImage Processor]
    CloudFn -->|Resize + upload variants| GCS
    CloudFn -->|Update status| CloudSQL

    style Armor fill:#ff6b6b,color:#fff
    style Redis fill:#ff4444,color:#fff
    style CloudSQL fill:#4285f4,color:#fff
    style ES fill:#f5a623,color:#fff
    style GCS fill:#34a853,color:#fff
    style PubSub fill:#fbbc05,color:#000
    style BQ fill:#4285f4,color:#fff
```

---

## 9.9 Key Request Flows Summary

| Flow | Key Services | SLA Target |
|------|-------------|-----------|
| User registration | User Service → Firebase → Cloud SQL → Cloud Tasks | < 500ms |
| Create listing | Listing Service → Moderation → Cloud SQL → Pub/Sub | < 300ms |
| Browse listings | Listing Service → Redis (cache) → Cloud SQL | < 100ms (cache) / 300ms (DB) |
| Search listings | Search Service → Redis → Elasticsearch | < 150ms (cache) / 300ms (ES) |
| Image upload URL | Image Service → Cloud SQL → GCS | < 200ms |
| Contact poster | Listing Service → Moderation → Pub/Sub | < 200ms (async email) |
| Listing expiry | Scheduler → Cloud Tasks → Worker → Cloud SQL + ES | Background, hourly |
| Saved search alert | Scheduler → Worker → ES → Email | Background, daily |
