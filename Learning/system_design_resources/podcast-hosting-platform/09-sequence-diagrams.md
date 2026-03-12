# Sequence Diagrams — Podcast Hosting Platform

> All diagrams use Mermaid `sequenceDiagram` syntax.
> `autonumber` labels each step for reference.

---

## Diagram 1: Episode Upload Flow (Full End-to-End)

```mermaid
sequenceDiagram
    autonumber
    actor Creator as Creator (Browser)
    participant API as Upload Service (GKE)
    participant Auth as Firebase Auth
    participant Spanner as Cloud Spanner
    participant GCS as Cloud Storage (GCS)
    participant Tasks as Cloud Tasks
    participant Worker as Transcode Worker (GKE Job)
    participant CDN as Cloud CDN
    participant PubSub as Cloud Pub/Sub

    Creator->>API: POST /v1/podcasts/{id}/episodes/upload-url
    Note over Creator,API: {filename, content_type, file_size, checksum_sha256}

    API->>Auth: Validate JWT token
    Auth-->>API: Token valid, user_id = "usr_xyz"

    API->>Spanner: Verify user owns podcast
    Spanner-->>API: Creator confirmed

    API->>GCS: Initiate resumable upload session
    GCS-->>API: Upload session URI

    API->>Spanner: INSERT episode (status=draft, upload_id=upl_xxx)
    Spanner-->>API: episode_id = "ep_abc"

    API-->>Creator: 202 Accepted {upload_id, signed_url, expires_at}

    loop Chunked Upload (10MB chunks)
        Creator->>GCS: PUT {signed_url} Content-Range: bytes X-Y/Total
        GCS-->>Creator: 308 Resume Incomplete (Range: bytes 0-Y)
    end

    Creator->>GCS: PUT final chunk
    GCS-->>Creator: 200 OK (upload complete)

    GCS->>PubSub: Object finalize notification (object=raw/ep_abc.mp3)

    Creator->>API: POST /v1/podcasts/{id}/episodes
    Note over Creator,API: {upload_id, title, description, chapters, publish_at}

    API->>Spanner: UPDATE episode (title, description, status=processing)
    API->>Tasks: Enqueue transcode job (episode_id=ep_abc, priority=normal)
    API->>PubSub: Publish episode.processing event
    API-->>Creator: 201 Created {episode_id, status=processing}

    Tasks->>Worker: Dispatch transcode job

    Worker->>GCS: Fetch raw audio (raw/ep_abc.mp3)
    GCS-->>Worker: Audio stream

    Note over Worker: FFmpeg encode to 4 bitrates (parallel)<br/>32 / 64 / 128 / 192 kbps → HLS segments

    Worker->>GCS: Write HLS segments (episodes/ep_abc/128k/*.aac, ...)
    Worker->>GCS: Write HLS manifests (episodes/ep_abc/128k/playlist.m3u8, adaptive.m3u8)

    Worker->>Spanner: UPDATE episode (status=ready, audio_url_base, duration_ms)
    Worker->>PubSub: Publish episode.transcoded event

    Note over API,PubSub: At scheduled publish time (or immediately if publish_at is now)

    API->>Spanner: UPDATE episode (status=published, published_at=now())
    API->>PubSub: Publish episode.published event

    PubSub->>API: RSS Service subscribes to episode.published
    API->>GCS: Regenerate RSS XML
    Note over API: DELETE Redis rss:feed:{podcast_id}<br/>Rebuild XML, SET Redis rss:feed:{podcast_id} EX 300

    Creator->>API: GET /v1/episodes/ep_abc (poll status)
    API-->>Creator: {status: "published", audio_url: "https://cdn.../adaptive.m3u8"}
```

---

## Diagram 2: On-Demand Streaming Flow

```mermaid
sequenceDiagram
    autonumber
    actor Listener as Listener (iOS App)
    participant Apigee as Apigee API Gateway
    participant StreamSvc as Streaming Service (GKE)
    participant Redis as Memorystore Redis
    participant Spanner as Cloud Spanner
    participant CDN as Cloud CDN
    participant GCS as Cloud Storage (GCS)
    participant PubSub as Cloud Pub/Sub
    participant AnalSvc as Analytics Service

    Listener->>Apigee: GET /v1/episodes/ep_abc/stream
    Note over Listener,Apigee: Authorization: Bearer {jwt}

    Apigee->>StreamSvc: Route request

    StreamSvc->>Redis: GET ep:meta:ep_abc
    alt Cache HIT
        Redis-->>StreamSvc: Episode metadata (JSON)
    else Cache MISS
        StreamSvc->>Spanner: SELECT episode WHERE id='ep_abc'
        Spanner-->>StreamSvc: Episode row
        StreamSvc->>Redis: SET ep:meta:ep_abc {json} EX 600
    end

    alt Episode is_premium = true
        StreamSvc->>Redis: GET sub:{user_id}:{creator_id}
        alt Subscription cached
            Redis-->>StreamSvc: Active subscription
        else Not cached
            StreamSvc->>Spanner: SELECT subscription WHERE subscriber=user AND status=active
            Spanner-->>StreamSvc: Subscription record
            StreamSvc->>Redis: SET sub:{uid}:{cid} "active" EX 3600
        end

        alt No active subscription
            StreamSvc-->>Listener: 403 Forbidden {error: SUBSCRIPTION_REQUIRED}
        end
    end

    StreamSvc->>Redis: GET pos:{user_id}:ep_abc
    Redis-->>StreamSvc: position_ms = 924000 (resume point)

    Note over StreamSvc: Generate Cloud CDN signed URL<br/>HMAC-SHA256(signing_key, path + expiry)

    StreamSvc-->>Listener: 200 OK<br/>{manifest_url (signed, 2hr TTL), resume_position_ms: 924000,<br/>tracks: [{192k, url}, {128k, url}, {64k, url}, {32k, url}],<br/>ad_break_positions_ms: [0, 900000, 1800000]}

    Listener->>CDN: GET adaptive.m3u8 (with signature)
    alt CDN Cache HIT (95%)
        CDN-->>Listener: Adaptive master manifest
    else CDN Cache MISS (5%)
        CDN->>GCS: Fetch adaptive.m3u8
        GCS-->>CDN: Manifest content
        CDN-->>Listener: Adaptive master manifest
    end

    Listener->>CDN: GET 128k/playlist.m3u8 (selected bitrate)
    CDN-->>Listener: Variant playlist (list of .aac segment files)

    loop HLS Segment Download (every 10 seconds)
        Listener->>CDN: GET 128k/045.aac
        CDN-->>Listener: Audio segment (10s, 160KB)
    end

    loop Playback position heartbeat (every 30 seconds)
        Listener->>StreamSvc: POST /v1/episodes/ep_abc/playback-position
        Note over Listener,StreamSvc: {position_ms: 1230000, session_id: sess_xyz}
        StreamSvc->>Redis: SET pos:{uid}:ep_abc 1230000 EX 2592000
        StreamSvc-->>Listener: 204 No Content
    end

    loop Analytics events (batched every 30s)
        Listener->>AnalSvc: POST /v1/analytics/events
        Note over Listener,AnalSvc: [{play_start}, {heartbeat×N}, ...]
        AnalSvc->>PubSub: Publish batch to raw-play-events
        AnalSvc-->>Listener: 202 Accepted {ingested: 12}
    end
```

---

## Diagram 3: Live Streaming Flow

```mermaid
sequenceDiagram
    autonumber
    actor Creator as Creator (Browser / OBS)
    actor Listener as Listener
    participant LiveSvc as Live Stream Service (GKE)
    participant RTMP as RTMP Media Server (GKE)
    participant Segmenter as HLS-LL Segmenter (FFmpeg)
    participant GCS as GCS: podcast-live bucket
    participant CDN as Cloud CDN
    participant FS as Cloud Firestore
    participant PubSub as Cloud Pub/Sub
    participant RecWorker as Recording Worker

    Creator->>LiveSvc: POST /v1/live-streams
    Note over Creator,LiveSvc: {podcast_id, title, enable_chat: true, auto_save_as_episode: true}

    LiveSvc->>FS: Create document streams/{stream_id} {status: waiting}
    LiveSvc-->>Creator: 201 Created<br/>{stream_id, rtmp_url, stream_key, playback_hls_url, chat_channel}

    Note over Creator,RTMP: Creator goes live — starts RTMP push

    Creator->>RTMP: RTMPS connect + authenticate stream_key
    RTMP->>FS: UPDATE streams/{stream_id} {status: live, started_at: now()}
    RTMP->>PubSub: Publish stream.started event

    Note over RTMP,Segmenter: Media pipeline starts

    loop Continuous stream (every 2 seconds)
        RTMP->>Segmenter: Raw audio/video frames
        Segmenter->>GCS: Write partial segment (HLS-LL: .aac + .m3u8 update)
        GCS->>CDN: CDN picks up new segments (origin pull)
    end

    Listener->>CDN: GET /live/stream_id/index.m3u8 (polls every 2s for HLS-LL)
    CDN-->>Listener: Master manifest

    loop HLS-LL polling (every 2s with blocking playlist request)
        Listener->>CDN: GET /live/stream_id/playlist.m3u8?_HLS_msn=45&_HLS_part=2
        Note over CDN: HLS-LL blocking: CDN holds request until segment 45 part 2 is available
        CDN-->>Listener: Updated playlist with new partial segments
        Listener->>CDN: GET partial segment (*.aac)
        CDN-->>Listener: 2-second audio chunk
    end

    Listener->>FS: Listen to streams/{stream_id} real-time updates
    Note over Listener,FS: WebSocket / SSE via Firestore SDK

    Listener->>FS: Create chat message in streams/{stream_id}/messages
    FS-->>Creator: Real-time new message notification

    alt Creator disconnects
        RTMP->>FS: UPDATE streams/{stream_id} {status: interrupted}
        Note over RTMP: Hold "live edge" for 30 seconds
        FS-->>Listener: Real-time push: status=interrupted → UI shows "Reconnecting..."

        alt Creator reconnects within 30s
            Creator->>RTMP: RTMPS reconnect with same stream_key
            RTMP->>FS: UPDATE {status: live}
            Note over RTMP,Segmenter: Stream continues seamlessly
        else 30s timeout
            RTMP->>FS: UPDATE {status: ended, ended_at: now()}
            RTMP->>PubSub: Publish stream.ended event
        end
    end

    Creator->>LiveSvc: POST /v1/live-streams/{stream_id}/end
    LiveSvc->>FS: UPDATE {status: ended}
    LiveSvc->>PubSub: Publish stream.ended event

    PubSub->>RecWorker: Consume stream.ended event
    RecWorker->>GCS: Read all live segments (rolling window)
    RecWorker->>GCS: Stitch into full episode MP3 (FFmpeg concat)
    RecWorker->>PubSub: Publish episode.uploaded event
    Note over RecWorker: Full transcode + RSS pipeline runs automatically
```

---

## Diagram 4: RSS Feed Update on Episode Publish

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Cloud Scheduler
    participant EpSvc as Episode Service (GKE)
    participant PubSub as Cloud Pub/Sub
    participant RssSvc as RSS Service (GKE)
    participant Redis as Memorystore Redis
    participant Spanner as Cloud Spanner
    participant CDN as Cloud CDN
    actor PodApp as Podcast App (Spotify / Apple)

    Note over Scheduler,EpSvc: At scheduled publish time for episode

    Scheduler->>EpSvc: Cloud Tasks trigger: publish_episode:{ep_id}
    EpSvc->>Spanner: UPDATE episodes SET status='published', published_at=now()
    Spanner-->>EpSvc: Success

    EpSvc->>PubSub: Publish message to topic: episode-published
    Note over EpSvc,PubSub: {episode_id: "ep_abc", podcast_id: "pod_xyz", published_at: ...}

    PubSub->>RssSvc: Push subscription delivers message
    RssSvc->>Redis: DEL rss:feed:pod_xyz (invalidate cache)

    Note over RssSvc: Proactively warm the cache

    RssSvc->>Spanner: SELECT podcast WHERE id='pod_xyz'
    RssSvc->>Spanner: SELECT episodes WHERE podcast_id='pod_xyz' AND status='published' ORDER BY published_at DESC LIMIT 50
    Spanner-->>RssSvc: Podcast + episode rows

    RssSvc->>RssSvc: Generate RSS 2.0 XML (iTunes namespace)
    RssSvc->>Redis: SET rss:feed:pod_xyz {xml} EX 300
    Note over RssSvc,Redis: Cache warm — next poll served instantly

    loop RSS polling (every 4-8 hours per app)
        PodApp->>CDN: GET https://feeds.podcastplatform.com/pod_xyz/rss
        Note over PodApp,CDN: If-None-Match: "old-etag"

        CDN->>RssSvc: Cache MISS → forward to RSS Service
        RssSvc->>Redis: GET rss:feed:pod_xyz
        Redis-->>RssSvc: RSS XML (from warm cache)
        RssSvc-->>CDN: 200 OK + ETag: "new-etag" + Cache-Control: max-age=300

        CDN-->>PodApp: RSS XML (new episode included)
        Note over PodApp: App detects new episode enclosure URL → alerts subscriber
    end
```

---

## Diagram 5: Creator Subscription & Premium Episode Access

```mermaid
sequenceDiagram
    autonumber
    actor Listener as Listener
    participant API as Monetization Service (GKE)
    participant Stripe as Stripe API
    participant PG as Cloud SQL PostgreSQL
    participant Redis as Memorystore Redis
    participant StreamSvc as Streaming Service
    participant PubSub as Cloud Pub/Sub
    participant NotifSvc as Notification Service

    Listener->>API: POST /v1/monetization/creator-subscriptions
    Note over Listener,API: {creator_id, tier_id, payment_method_id}

    API->>Stripe: Create Stripe Subscription
    Note over API,Stripe: Idempotency-Key: sub-req-{uuid}

    Stripe-->>API: Subscription created {stripe_sub_id, status: active}

    API->>PG: INSERT creator_subscriptions {subscriber_id, creator_id, tier_id, status=active, stripe_sub_id}
    API->>Redis: SET sub:{listener_id}:{creator_id} "active" EX 3600
    API-->>Listener: 201 Created {subscription_id, status: active, current_period_end}

    Note over Listener: Listener navigates to premium episode

    Listener->>StreamSvc: GET /v1/episodes/ep_premium/stream

    StreamSvc->>Redis: GET sub:{listener_id}:{creator_id}
    Redis-->>StreamSvc: "active" (cached hit — no DB query needed)

    StreamSvc-->>Listener: 200 OK {signed manifest URL, ...}

    Note over Stripe: Monthly renewal attempt

    Stripe->>API: Webhook: invoice.paid
    API->>PG: UPDATE creator_subscriptions SET current_period_end = next_month
    API->>Redis: SETEX sub:{listener_id}:{creator_id} "active" 3600
    API->>PubSub: Publish subscription.renewed event
    PubSub->>NotifSvc: Notify creator of renewal revenue

    alt Payment fails
        Stripe->>API: Webhook: invoice.payment_failed
        API->>PG: UPDATE creator_subscriptions SET status='past_due'
        Note over API: Grace period: do NOT revoke access immediately
        Note over API: Stripe retries for 4 days

        Stripe->>API: Webhook: invoice.payment_failed (final)
        API->>PG: UPDATE creator_subscriptions SET status='canceled', canceled_at=now()
        API->>Redis: DEL sub:{listener_id}:{creator_id}
        API->>PubSub: Publish subscription.canceled event
        PubSub->>NotifSvc: Notify listener: subscription ended
    end
```

---

## Diagram 6: Analytics Event → Creator Dashboard

```mermaid
sequenceDiagram
    autonumber
    actor Listener as Listener (iOS)
    participant AnalAPI as Analytics Service (GKE)
    participant PubSub as Cloud Pub/Sub
    participant Dataflow as Cloud Dataflow (Streaming Job)
    participant BQ as BigQuery
    participant DashAPI as Analytics Dashboard API
    actor Creator as Creator Dashboard

    loop Every 30 seconds while playing
        Listener->>AnalAPI: POST /v1/analytics/events
        Note over Listener,AnalAPI: Batch: [{play_start}, {heartbeat×N}, {play_pause}...]

        AnalAPI->>AnalAPI: Validate schema + authenticate session
        AnalAPI->>PubSub: Publish 12 messages to raw-play-events topic
        Note over AnalAPI,PubSub: Messages include: episode_id, session_id, position_ms, country, device
        AnalAPI-->>Listener: 202 Accepted {ingested: 12}
    end

    Note over PubSub,Dataflow: Streaming pipeline (continuous)

    PubSub->>Dataflow: Pull messages (auto-scaled workers)

    Dataflow->>Dataflow: Stage 1: Deduplicate on (session_id, event_type, position_ms) in 10s window
    Dataflow->>Dataflow: Stage 2: Enrich (IP → country via MaxMind, add podcast_id from episode)
    Dataflow->>BQ: Stream insert to play_events (partitioned by date)
    Dataflow->>BQ: 5-minute windowed aggregate → daily_episode_stats (MERGE/UPDATE)

    Note over BQ: BigQuery materialized view refreshes every 5 min

    Creator->>DashAPI: GET /v1/analytics/podcasts/pod_xyz/overview?from=2026-03-01&to=2026-03-12
    DashAPI->>BQ: SELECT total_plays, unique_listeners, revenue FROM daily_episode_stats...
    BQ-->>DashAPI: Aggregated results
    DashAPI-->>Creator: 200 OK {totals, timeseries, geography, top_episodes}

    Creator->>DashAPI: GET /v1/analytics/episodes/ep_abc/retention
    DashAPI->>BQ: SELECT minute_mark, listeners_at_minute FROM daily_retention_curves WHERE episode_id='ep_abc'
    BQ-->>DashAPI: Retention curve data
    DashAPI-->>Creator: 200 OK {retention_curve: [{position_seconds: 0, pct: 100.0}, ...]}
```

---

## Diagram 7: Transcription Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant PubSub as Cloud Pub/Sub
    participant TransOrch as Transcription Orchestrator (GKE)
    participant Tasks as Cloud Tasks
    participant Worker as Transcription Worker (Cloud Run)
    participant GCS as Cloud Storage (GCS)
    participant SpeechAPI as GCP Speech-to-Text API
    participant ES as Elasticsearch
    participant Spanner as Cloud Spanner

    Note over PubSub: episode.transcoded event published after audio processing

    PubSub->>TransOrch: Consume episode.transcoded event
    Note over TransOrch: Check if transcription already exists (idempotent)
    TransOrch->>Spanner: SELECT transcript_url FROM episodes WHERE id='ep_abc'
    Spanner-->>TransOrch: transcript_url IS NULL (not yet done)

    TransOrch->>Tasks: Enqueue transcription job (episode_id=ep_abc, priority=low)
    TransOrch->>Spanner: UPDATE episodes SET transcription_status='queued'

    Tasks->>Worker: Dispatch job (Cloud Run cold start: ~2s)

    Worker->>GCS: Stream 128k MP3 audio file
    GCS-->>Worker: Audio bytes

    Note over Worker: Split into 5-min chunks (API max 60 min, we use 5 min for parallelism)

    par Parallel API calls (45min episode → 9 chunks in parallel)
        Worker->>SpeechAPI: RecognizeAsync chunk 1 (SPEAKER_DIARIZATION + WORD_TIME_OFFSETS)
        SpeechAPI-->>Worker: Words + timestamps for chunk 1
    and
        Worker->>SpeechAPI: RecognizeAsync chunk 2
        SpeechAPI-->>Worker: Words + timestamps for chunk 2
    and
        Worker->>SpeechAPI: RecognizeAsync chunks 3-9...
        SpeechAPI-->>Worker: Words + timestamps
    end

    Worker->>Worker: Merge chunks, align timestamps, detect chapter boundaries
    Note over Worker: Chapter detection: silence >5s + semantic shift (TF-IDF topic change)

    Worker->>GCS: Write transcripts/ep_abc/words.json
    Worker->>GCS: Write transcripts/ep_abc/transcript.srt
    Worker->>GCS: Write transcripts/ep_abc/transcript.txt

    Worker->>Spanner: UPDATE episodes SET transcript_url=..., chapters_json=..., transcription_status=done

    Worker->>ES: Index document {episode_id, podcast_id, title, transcript_text (first 50KB)}
    Note over Worker,ES: Transcript text indexed for full-text search

    Worker->>PubSub: Publish episode.transcribed event

    Note over PubSub: Notification service consumes episode.transcribed
    PubSub->>TransOrch: episode.transcribed consumed by notification worker
    TransOrch->>TransOrch: Push notification to creator: "Transcript ready for Episode 42"
```

---

## Diagram 8: Comment + Notification Flow

```mermaid
sequenceDiagram
    autonumber
    actor Commenter as Listener A (Commenter)
    actor EpOwner as Creator (Podcast Owner)
    participant SocSvc as Social Service (GKE)
    participant PG as Cloud SQL PostgreSQL
    participant Redis as Memorystore Redis
    participant PubSub as Cloud Pub/Sub
    participant NotifSvc as Notification Service (GKE)
    participant FCM as Firebase Cloud Messaging

    Commenter->>SocSvc: POST /v1/episodes/ep_abc/comments
    Note over Commenter,SocSvc: {content: "This was amazing!", parent_comment_id: null}

    SocSvc->>PG: INSERT INTO comments (episode_id='ep_abc', user_id=commenter, content=..., depth=0)
    PG-->>SocSvc: comment_id = cmt_xyz

    SocSvc->>Redis: INCR comment_count:ep_abc
    SocSvc->>PubSub: Publish comment.created event
    Note over SocSvc,PubSub: {comment_id, episode_id, podcast_id, commenter_id, content_preview}
    SocSvc-->>Commenter: 201 Created {comment object}

    PubSub->>NotifSvc: Consume comment.created

    NotifSvc->>PG: SELECT creator_id FROM podcasts JOIN episodes WHERE episode_id='ep_abc'
    PG-->>NotifSvc: creator_id = usr_CreatorXxx

    NotifSvc->>Redis: GET user:device_tokens:usr_CreatorXxx
    Redis-->>NotifSvc: [device_token_1, device_token_2]

    NotifSvc->>FCM: Send push notification
    Note over NotifSvc,FCM: {title: "New comment on Episode 42", body: "This was amazing!", data: {episode_id, comment_id}}
    FCM-->>EpOwner: Push notification delivered

    EpOwner->>SocSvc: GET /v1/episodes/ep_abc/comments?sort=new&limit=20
    SocSvc->>PG: SELECT top-level comments + 2 levels replies (recursive CTE)
    PG-->>SocSvc: Comment tree

    SocSvc-->>EpOwner: 200 OK {paginated comment thread}

    EpOwner->>SocSvc: POST /v1/episodes/ep_abc/comments
    Note over EpOwner,SocSvc: {content: "Thanks! Glad you enjoyed it.", parent_comment_id: cmt_xyz}

    SocSvc->>PG: INSERT comment (depth=1, parent_comment_id=cmt_xyz)
    SocSvc->>PubSub: Publish comment.created (reply to commenter)
    PubSub->>NotifSvc: Notify Commenter: "Creator replied to your comment"
    NotifSvc->>FCM: Push to Commenter's device
    FCM-->>Commenter: "Creator replied: Thanks! Glad you enjoyed it."
```
