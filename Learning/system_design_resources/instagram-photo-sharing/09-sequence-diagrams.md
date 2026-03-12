# 09 — Sequence Diagrams

## System: Photo Sharing Service (Instagram-Scale)

---

## Flow 1: Photo Upload & Post Creation

```mermaid
sequenceDiagram
    autonumber
    actor User as 📱 User (Mobile App)
    participant Apigee as Apigee Gateway
    participant MediaSvc as Media Upload Service
    participant GCS as Cloud Storage (GCS)
    participant PubSub as Cloud Pub/Sub
    participant MediaWorker as Media Processing Worker
    participant PostSvc as Post Service
    participant CloudSQL as Cloud SQL (PostgreSQL)
    participant FeedWorker as Feed Fan-out Worker
    participant Redis as Memorystore Redis
    participant CDN as Cloud CDN

    Note over User,CDN: Phase 1 — Request Presigned Upload URL
    User->>+Apigee: POST /v1/media/upload-url<br/>{content_type, file_size, checksum_md5}
    Apigee->>Apigee: Validate JWT (Firebase), rate limit check
    Apigee->>+MediaSvc: Forward request
    MediaSvc->>MediaSvc: Validate content_type, size ≤ 20MB
    MediaSvc->>MediaSvc: Check idempotency (Redis: upload_id exists?)
    MediaSvc->>CloudSQL: INSERT media(status='uploading', owner_id)
    MediaSvc->>GCS: Generate signed PUT URL (15-min expiry)
    MediaSvc-->>-Apigee: 201 {upload_id, presigned_url, media_id}
    Apigee-->>-User: 201 {upload_id, presigned_url, media_id}

    Note over User,CDN: Phase 2 — Direct Binary Upload to GCS
    User->>+GCS: PUT <presigned_url> (binary photo, ~3MB)
    GCS-->>-User: 200 OK (upload complete)
    GCS->>PubSub: Publish: media.uploaded {media_id, owner_id, gcs_path}

    Note over User,CDN: Phase 3 — Post Creation (while processing runs async)
    User->>+Apigee: POST /v1/posts<br/>{media_ids, caption, location, tagged_users}
    Apigee->>+PostSvc: Forward request
    PostSvc->>CloudSQL: INSERT post (status='draft'), INSERT post_media, INSERT post_hashtags
    PostSvc->>PubSub: Publish: post.created {post_id, author_id, follower_count}
    PostSvc-->>-Apigee: 201 {post: {id, status:'processing', ...}}
    Apigee-->>-User: 201 post object (status='processing')

    Note over User,CDN: Phase 4 — Async Media Processing (parallel)
    PubSub->>+MediaWorker: media.uploaded event
    MediaWorker->>GCS: Download original photo (streaming)
    MediaWorker->>MediaWorker: CSAM hash check (PhotoDNA)
    alt CSAM match detected
        MediaWorker->>GCS: Delete original
        MediaWorker->>CloudSQL: UPDATE media SET status='removed'
        MediaWorker->>MediaWorker: Flag account, alert Trust & Safety
    else CSAM check passed
        MediaWorker->>MediaWorker: NSFW score via Vertex AI Vision
        MediaWorker->>MediaWorker: Generate 3 WebP variants (libvips parallel)
        MediaWorker->>GCS: Upload thumb + medium + HD variants
        MediaWorker->>CloudSQL: UPDATE media SET status='ready', cdn_urls=...
        MediaWorker->>PubSub: Publish: media.processed {media_id, post_id}
        MediaWorker-->>-PubSub: ACK
    end

    Note over User,CDN: Phase 5 — Feed Fan-out (async, parallel with Phase 4)
    PubSub->>+FeedWorker: post.created event
    FeedWorker->>CloudSQL: SELECT follower_ids WHERE followee_id=author (paginated 10K)
    loop For each follower batch
        FeedWorker->>Redis: ZADD feed:{follower_id} {score} {post_id} [PIPELINE]
        FeedWorker->>Redis: ZREMRANGEBYRANK feed:{follower_id} 0 -101 (trim to 100)
    end
    FeedWorker-->>-PubSub: ACK

    Note over User,CDN: Phase 6 — Client Polling for Processing Status
    User->>+Apigee: GET /v1/media/{media_id}/status (every 5s)
    Apigee->>+MediaSvc: Forward
    MediaSvc->>CloudSQL: SELECT status FROM media WHERE id=?
    MediaSvc-->>-Apigee: {status: 'ready', cdn_urls: {...}}
    Apigee-->>-User: Post now visible ✅

    Note over User,CDN: CDN pre-warms automatically on first request
    User->>CDN: GET cdn.photoshare.io/photos/{media_id}_medium.webp
    CDN->>GCS: Cache miss → fetch from origin
    GCS-->>CDN: Photo bytes
    CDN-->>User: Photo served (cached for 7 days)
```

---

## Flow 2: Feed Fetch (Warm Cache Path)

```mermaid
sequenceDiagram
    autonumber
    actor User as 📱 User (Mobile App)
    participant Apigee as Apigee Gateway
    participant FeedSvc as Feed Service
    participant Redis as Memorystore Redis
    participant CloudSQL as Cloud SQL
    participant CDN as Cloud CDN

    Note over User,CDN: Happy Path — Feed cached in Redis (95% of requests)

    User->>+Apigee: GET /v1/feed?limit=20&type=ranked
    Note right of Apigee: JWT validation, rate limit check
    Apigee->>+FeedSvc: GET /feed {user_id from JWT}

    FeedSvc->>+Redis: ZRANGE feed:{user_id} 0 19 REV WITHSCORES
    Redis-->>-FeedSvc: [post_id_1: 0.94, post_id_2: 0.87, ...] (20 post IDs)

    Note over FeedSvc,CloudSQL: Hydrate post details (batch query)
    FeedSvc->>+CloudSQL: SELECT p.*, u.username, u.avatar_url, u.is_verified<br/>FROM posts p JOIN users u ON p.author_id=u.id<br/>WHERE p.id = ANY('{post_id_1, post_id_2, ...}')
    CloudSQL-->>-FeedSvc: 20 post rows with author details

    Note over FeedSvc,Redis: Check like status for requesting user
    FeedSvc->>+Redis: MGET likes:user:{user_id}:post_id_1 ... (20 keys in pipeline)
    Redis-->>-FeedSvc: [1, null, 1, null, ...] (liked status per post)

    FeedSvc->>FeedSvc: Merge posts + author info + like status
    FeedSvc->>FeedSvc: Build next_cursor = base64({last_post_id, last_score})

    FeedSvc-->>-Apigee: 200 {posts: [...], pagination: {next_cursor, has_more}}
    Apigee-->>-User: 200 Feed response

    Note over User,CDN: Client renders feed, fetches images from CDN
    loop For each visible post (lazy loading)
        User->>CDN: GET cdn.photoshare.io/photos/{media_id}_medium.webp
        CDN-->>User: Cached photo (< 100ms)
    end
```

---

## Flow 2b: Feed Fetch (Cold Cache / Celebrity Follow Path)

```mermaid
sequenceDiagram
    autonumber
    actor User as 📱 Inactive User (returns after 3 days)
    participant FeedSvc as Feed Service
    participant Redis as Memorystore Redis
    participant Spanner as Cloud Spanner
    participant CloudSQL as Cloud SQL

    User->>+FeedSvc: GET /v1/feed

    FeedSvc->>+Redis: ZRANGE feed:{user_id} 0 19 REV
    Redis-->>-FeedSvc: (empty — cache expired after 24h TTL)

    Note over FeedSvc,CloudSQL: Cache miss — fan-out on read
    FeedSvc->>+Spanner: SELECT followee_id FROM follows<br/>WHERE follower_id={user_id} AND status='active'
    Spanner-->>-FeedSvc: [followee_1, followee_2, ... followee_300]

    FeedSvc->>FeedSvc: Split: regular_users (followees < 1M followers)<br/>vs celebrities (followees >= 1M followers)

    par Regular user followees (push-cached)
        FeedSvc->>+Redis: MGET feed:{followee_R1}, feed:{followee_R2} ... (pipeline)
        Redis-->>-FeedSvc: Post ID lists from each followed user's feed ZSET
    and Celebrity followees (pull on read)
        FeedSvc->>+CloudSQL: SELECT id, created_at, like_count FROM posts<br/>WHERE author_id IN (celeb_1, celeb_2)<br/>AND created_at > NOW()-INTERVAL '7d'<br/>ORDER BY created_at DESC LIMIT 20 PER AUTHOR
        CloudSQL-->>-FeedSvc: Celebrity posts
    end

    FeedSvc->>FeedSvc: Merge all post IDs, deduplicate
    FeedSvc->>FeedSvc: Score each post (recency × 0.4 + engagement × 0.3 + ...)
    FeedSvc->>FeedSvc: Sort by score descending, take top 100

    FeedSvc->>+Redis: ZADD feed:{user_id} {score} {post_id} × 100 (repopulate cache)
    FeedSvc->>Redis: EXPIRE feed:{user_id} 86400
    Redis-->>-FeedSvc: OK

    FeedSvc-->>-User: 200 Top 20 posts (latency: ~800ms vs ~50ms warm)
```

---

## Flow 3: Follow a User

```mermaid
sequenceDiagram
    autonumber
    actor Follower as 📱 Follower (User A)
    participant Apigee as Apigee Gateway
    participant FollowSvc as Follow Service
    participant Spanner as Cloud Spanner
    participant PubSub as Cloud Pub/Sub
    participant FeedWorker as Feed Fan-out Worker
    participant NotifWorker as Notification Worker
    participant Redis as Memorystore Redis

    Follower->>+Apigee: PUT /v1/users/{target_user_id}/follow<br/>{action: "follow"}
    Apigee->>+FollowSvc: Forward request

    FollowSvc->>+Spanner: BEGIN TRANSACTION
    FollowSvc->>Spanner: SELECT is_private FROM users WHERE id={target_id}

    alt Target account is PUBLIC
        FollowSvc->>Spanner: INSERT follows(follower_id=A, followee_id=B,<br/>status='active', created_at=NOW)
        FollowSvc->>Spanner: COMMIT
        Spanner-->>FollowSvc: OK

        FollowSvc->>PubSub: Publish: user.followed<br/>{follower_id: A, followee_id: B, type: 'new_follow'}
        FollowSvc-->>-Apigee: 200 {is_following: true, is_pending: false}

        Note over FollowSvc,Redis: Async: Feed backfill + notification
        PubSub->>+FeedWorker: user.followed event
        FeedWorker->>Spanner: SELECT id FROM posts WHERE author_id=B<br/>ORDER BY created_at DESC LIMIT 20
        FeedWorker->>Redis: ZADD feed:{A} {score} {post_id} × 20
        FeedWorker-->>-PubSub: ACK

        PubSub->>+NotifWorker: user.followed event
        NotifWorker->>NotifWorker: Check B's notification preferences
        NotifWorker->>NotifWorker: FCM push: "A started following you"
        NotifWorker-->>-PubSub: ACK

    else Target account is PRIVATE
        FollowSvc->>Spanner: INSERT follows(follower_id=A, followee_id=B,<br/>status='pending', created_at=NOW)
        FollowSvc->>Spanner: COMMIT
        Spanner-->>FollowSvc: OK

        FollowSvc->>PubSub: Publish: follow.requested<br/>{requester_id: A, target_id: B}
        FollowSvc-->>-Apigee: 200 {is_following: false, is_pending: true}

        PubSub->>+NotifWorker: follow.requested event
        NotifWorker->>NotifWorker: Push to B: "A requested to follow you"
        NotifWorker-->>-PubSub: ACK
    end

    Apigee-->>-Follower: 200 Response
```

---

## Flow 4: Like a Post

```mermaid
sequenceDiagram
    autonumber
    actor User as 📱 User
    participant Apigee as Apigee Gateway
    participant LikeSvc as Like Service
    participant Bigtable as Cloud Bigtable
    participant Redis as Memorystore Redis
    participant PubSub as Cloud Pub/Sub
    participant NotifWorker as Notification Worker

    User->>+Apigee: PUT /v1/posts/{post_id}/like<br/>{action: "like"}
    Apigee->>Apigee: JWT validation, rate limit (500 likes/hr)
    Apigee->>+LikeSvc: Forward request

    Note over LikeSvc,Bigtable: Step 1: Check current like state (deduplication)
    LikeSvc->>+Bigtable: ReadRow(key="{post_id}#{user_id}",<br/>col="like_data:action")
    Bigtable-->>-LikeSvc: null (not yet liked)

    Note over LikeSvc,Redis: Step 2: Write to durable store
    LikeSvc->>+Bigtable: MutateRow(key="{post_id}#{user_id}",<br/>SetCell("like_data","action","like"),<br/>SetCell("like_data","ts", now_micros))
    Bigtable-->>-LikeSvc: OK

    Note over LikeSvc,Redis: Step 3: Increment cache counter (fast read)
    LikeSvc->>+Redis: PIPELINE:<br/>INCR likes:count:{post_id}<br/>SET likes:user:{user_id}:{post_id} "1" EX 3600
    Redis-->>-LikeSvc: [1244, OK]

    LikeSvc->>PubSub: Publish: post.liked<br/>{post_id, liker_id, post_owner_id}

    LikeSvc-->>-Apigee: 200 {like_count: 1244, is_liked_by_me: true}
    Apigee-->>-User: 200 Response

    Note over PubSub,NotifWorker: Async notification (non-blocking for user)
    PubSub->>+NotifWorker: post.liked event
    NotifWorker->>NotifWorker: Check batching window:<br/>Redis GET notif_batch:{post_id}:like:{owner_id}
    alt First like on this post in 30-min window
        NotifWorker->>NotifWorker: FCM push: "@user liked your photo"
        NotifWorker->>Redis: SET notif_batch:{post_id}:like:{owner_id} 1 EX 1800
    else Batch in progress
        NotifWorker->>Redis: INCR notif_batch:{post_id}:like:{owner_id}
        Note right of NotifWorker: Aggregated push sent on TTL expiry:<br/>"@user and 49 others liked your photo"
    end
    NotifWorker-->>-PubSub: ACK
```

---

## Flow 5: Search

```mermaid
sequenceDiagram
    autonumber
    actor User as 📱 User
    participant Apigee as Apigee Gateway
    participant SearchSvc as Search Service
    participant Redis as Redis (Autocomplete Cache)
    participant ES as Elasticsearch

    User->>+Apigee: GET /v1/search?q=beach&type=all&limit=10
    Apigee->>+SearchSvc: Forward request

    Note over SearchSvc,Redis: Check autocomplete cache first
    SearchSvc->>+Redis: GET search:cache:{hash("beach:all")}
    Redis-->>-SearchSvc: null (cache miss)

    Note over SearchSvc,ES: Parallel queries to Elasticsearch
    par Search users by username/display_name
        SearchSvc->>+ES: GET /users/_search<br/>{query: {multi_match: {query: "beach",<br/>fields: ["username^2", "display_name"]}},<br/>size: 5}
        ES-->>-SearchSvc: [{id, username, follower_count, is_verified}, ...]
    and Search hashtags
        SearchSvc->>+ES: GET /hashtags/_search<br/>{query: {prefix: {tag: "beach"}},<br/>sort: [{post_count: desc}], size: 5}
        ES-->>-SearchSvc: [{tag: "beach", post_count: 45.2M}, ...]
    and Search locations
        SearchSvc->>+ES: GET /locations/_search<br/>{query: {match: {name: "beach"}},<br/>sort: [{post_count: desc}], size: 5}
        ES-->>-SearchSvc: [{id, name, post_count}, ...]
    end

    SearchSvc->>SearchSvc: Merge results, sort by relevance score
    SearchSvc->>+Redis: SET search:cache:{hash} <result> EX 300 (5-min cache)
    Redis-->>-SearchSvc: OK

    SearchSvc-->>-Apigee: 200 {users:[...], hashtags:[...], locations:[...]}
    Apigee-->>-User: 200 Search results
```

---

## Flow 6: User Registration

```mermaid
sequenceDiagram
    autonumber
    actor User as 📱 New User
    participant Firebase as Firebase Authentication
    participant Apigee as Apigee Gateway
    participant UserSvc as User Service
    participant CloudSQL as Cloud SQL
    participant ES as Elasticsearch
    participant PubSub as Cloud Pub/Sub

    Note over User,PubSub: Social Login (Google OAuth)
    User->>+Firebase: Sign in with Google
    Firebase->>Firebase: Validate Google ID token
    Firebase->>Firebase: Create Firebase user account
    Firebase-->>-User: Firebase JWT (id_token)

    Note over User,PubSub: Complete profile setup
    User->>+Apigee: POST /v1/users/register<br/>{username, display_name, bio}<br/>Authorization: Bearer <firebase_jwt>
    Apigee->>+Firebase: Verify JWT (public key validation)
    Firebase-->>-Apigee: {uid, email} (decoded claims)
    Apigee->>+UserSvc: Register user with firebase_uid

    UserSvc->>+CloudSQL: SELECT COUNT(*) FROM users WHERE username='chosen_username'
    CloudSQL-->>-UserSvc: 0 (username available)

    UserSvc->>+CloudSQL: INSERT INTO users<br/>(id, firebase_uid, username, email, display_name, ...)
    CloudSQL-->>-UserSvc: OK

    UserSvc->>PubSub: Publish: user.created {user_id, username}

    UserSvc-->>-Apigee: 201 {user: {id, username, ...}}
    Apigee-->>-User: 201 Account created ✅

    Note over PubSub,ES: Async: Index new user in Elasticsearch
    PubSub->>+ES: Index user doc (Search Indexer Worker)
    ES-->>-PubSub: Indexed (user searchable within ~10s)
```
