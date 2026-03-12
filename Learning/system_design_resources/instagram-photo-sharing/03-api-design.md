# 03 — API Design

## System: Photo Sharing Service (Instagram-Scale)

---

## API Conventions

- **Base URL**: `https://api.photoshare.io/v1`
- **Protocol**: HTTPS only (TLS 1.3)
- **Format**: JSON request/response bodies
- **Authentication**: Bearer JWT (Firebase Auth) in `Authorization` header
- **Versioning**: URI path versioning (`/v1/`, `/v2/`)
- **Pagination**: Cursor-based (not offset-based) for stable pagination at scale
- **Idempotency**: Write endpoints accept `Idempotency-Key` header (UUID v4)
- **Compression**: Gzip on responses > 1KB

### Standard Error Format

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Post with id 'abc123' not found",
    "request_id": "req_7f3k2m9x",
    "timestamp": "2026-03-12T10:30:00Z"
  }
}
```

### Standard Pagination (Cursor-based)

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNH0=",
    "has_more": true,
    "count": 20
  }
}
```

---

## Rate Limits

| Endpoint Group | Limit | Window | Scope |
|----------------|-------|--------|-------|
| Media upload | 10 uploads | 1 hour | Per user |
| Post creation | 10 posts | 1 hour | Per user |
| Like/unlike | 500 | 1 hour | Per user |
| Comments | 60 | 1 hour | Per user |
| Feed fetch | 300 | 1 hour | Per user |
| Follow/unfollow | 200 | 1 hour | Per user |
| Search | 100 | 1 hour | Per user |
| Unauthenticated | 60 | 1 hour | Per IP |

Rate limit headers returned on all responses:
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 247
X-RateLimit-Reset: 1710242400
```

---

## Endpoints

### 1. Media Upload (Two-Phase)

#### Step 1 — Request Presigned URL

> Client requests a signed URL directly to GCS. This offloads upload bandwidth from app servers.

**POST** `/v1/media/upload-url`

Request:
```json
{
  "file_name": "sunset_beach.jpg",
  "content_type": "image/jpeg",
  "file_size_bytes": 3145728,
  "checksum_md5": "d41d8cd98f00b204e9800998ecf8427e"
}
```

Response `201 Created`:
```json
{
  "upload_id": "upl_9x3km2f7",
  "presigned_url": "https://storage.googleapis.com/photoshare-uploads/...",
  "expires_at": "2026-03-12T11:00:00Z",
  "media_id": "med_5z7q1p4n"
}
```

> Client then PUTs the binary directly to `presigned_url`. After upload completes, proceed to Step 2.

#### Step 2 — Create Post

**POST** `/v1/posts`

Headers:
```
Authorization: Bearer <jwt>
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

Request:
```json
{
  "media_ids": ["med_5z7q1p4n"],
  "caption": "Beautiful sunset at Santa Monica #beach #sunset",
  "location": {
    "name": "Santa Monica Beach",
    "lat": 34.0195,
    "lng": -118.4912
  },
  "tagged_user_ids": ["usr_abc123", "usr_def456"],
  "alt_text": "Orange sunset sky over calm ocean waters"
}
```

Response `201 Created`:
```json
{
  "post": {
    "id": "pst_7t3n8z2k",
    "author": {
      "id": "usr_me123",
      "username": "prashant",
      "avatar_url": "https://cdn.photoshare.io/avatars/prashant_thumb.webp"
    },
    "media": [
      {
        "id": "med_5z7q1p4n",
        "url_thumb": "https://cdn.photoshare.io/photos/xxx_thumb.webp",
        "url_medium": "https://cdn.photoshare.io/photos/xxx_medium.webp",
        "url_hd": "https://cdn.photoshare.io/photos/xxx_hd.webp",
        "width": 1080,
        "height": 1080,
        "type": "photo"
      }
    ],
    "caption": "Beautiful sunset at Santa Monica #beach #sunset",
    "hashtags": ["beach", "sunset"],
    "location": {
      "name": "Santa Monica Beach",
      "lat": 34.0195,
      "lng": -118.4912
    },
    "like_count": 0,
    "comment_count": 0,
    "created_at": "2026-03-12T10:30:00Z"
  }
}
```

---

### 2. Feed

**GET** `/v1/feed`

Query Parameters:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `cursor` | string | null | Pagination cursor from previous response |
| `limit` | int | 20 | Items per page (max: 50) |
| `type` | string | `ranked` | `ranked` or `chronological` |

Response `200 OK`:
```json
{
  "posts": [
    {
      "id": "pst_7t3n8z2k",
      "author": {
        "id": "usr_xyz789",
        "username": "jane_doe",
        "avatar_url": "https://cdn.photoshare.io/avatars/jane_thumb.webp",
        "is_verified": true
      },
      "media": [...],
      "caption": "Morning run! #fitness",
      "like_count": 1243,
      "comment_count": 87,
      "is_liked_by_me": true,
      "created_at": "2026-03-12T06:15:00Z",
      "feed_score": 0.94
    }
  ],
  "pagination": {
    "next_cursor": "eyJsYXN0X2lkIjoicHN0XzdmM3oifQ==",
    "has_more": true,
    "count": 20
  }
}
```

---

### 3. Like / Unlike a Post

**PUT** `/v1/posts/{postId}/like`

Request:
```json
{
  "action": "like"
}
```

`action` is either `"like"` or `"unlike"` — idempotent.

Response `200 OK`:
```json
{
  "post_id": "pst_7t3n8z2k",
  "like_count": 1244,
  "is_liked_by_me": true
}
```

---

### 4. Comments

**GET** `/v1/posts/{postId}/comments`

Query: `cursor`, `limit=20`

Response `200 OK`:
```json
{
  "comments": [
    {
      "id": "cmt_9k2m1p",
      "author": {
        "id": "usr_abc",
        "username": "alex",
        "avatar_url": "..."
      },
      "text": "Amazing shot 🌅",
      "like_count": 12,
      "replies": [
        {
          "id": "cmt_reply_x1",
          "author": { "id": "usr_xyz", "username": "jane_doe" },
          "text": "@alex Thank you! 😊",
          "like_count": 3,
          "created_at": "2026-03-12T07:00:00Z"
        }
      ],
      "created_at": "2026-03-12T06:45:00Z"
    }
  ],
  "pagination": { "next_cursor": "...", "has_more": false, "count": 5 }
}
```

**POST** `/v1/posts/{postId}/comments`

Request:
```json
{
  "text": "Incredible colors! 🌅",
  "reply_to_comment_id": null
}
```

Response `201 Created`:
```json
{
  "id": "cmt_newxyz",
  "author": { "id": "usr_me", "username": "prashant" },
  "text": "Incredible colors! 🌅",
  "like_count": 0,
  "created_at": "2026-03-12T10:31:00Z"
}
```

**DELETE** `/v1/posts/{postId}/comments/{commentId}` → `204 No Content`

---

### 5. Follow / Unfollow

**PUT** `/v1/users/{userId}/follow`

Request:
```json
{
  "action": "follow"
}
```

`action` is either `"follow"` or `"unfollow"` — idempotent.

Response `200 OK`:
```json
{
  "target_user_id": "usr_xyz789",
  "relationship": {
    "is_following": true,
    "is_follower": false,
    "is_pending": false
  },
  "follower_count": 10241
}
```

> For private accounts, `is_following: false` and `is_pending: true` until approved.

---

### 6. User Profile

**GET** `/v1/users/{userId}/profile`

Response `200 OK`:
```json
{
  "user": {
    "id": "usr_xyz789",
    "username": "jane_doe",
    "display_name": "Jane Doe",
    "bio": "Photographer & traveler ✈️",
    "avatar_url": "https://cdn.photoshare.io/avatars/jane_hd.webp",
    "website": "https://janedoe.com",
    "is_verified": true,
    "is_private": false,
    "post_count": 347,
    "follower_count": 125000,
    "following_count": 512,
    "is_following_me": false,
    "am_i_following": true,
    "created_at": "2021-06-15T00:00:00Z"
  },
  "recent_posts": [...]
}
```

---

### 7. Search

**GET** `/v1/search`

Query Parameters:
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search query (required) |
| `type` | string | `users`, `hashtags`, `locations`, or `all` |
| `cursor` | string | Pagination cursor |
| `limit` | int | Max 30 |

Response `200 OK`:
```json
{
  "users": [
    {
      "id": "usr_xyz789",
      "username": "jane_doe",
      "display_name": "Jane Doe",
      "avatar_url": "...",
      "follower_count": 125000,
      "is_verified": true
    }
  ],
  "hashtags": [
    {
      "tag": "beach",
      "post_count": 45200000,
      "preview_urls": ["https://cdn.photoshare.io/...", "..."]
    }
  ],
  "locations": [
    {
      "id": "loc_sm001",
      "name": "Santa Monica Beach",
      "post_count": 1230000,
      "preview_url": "https://cdn.photoshare.io/..."
    }
  ],
  "pagination": { "next_cursor": "...", "has_more": true, "count": 10 }
}
```

---

### 8. Notifications

**GET** `/v1/notifications`

Query: `cursor`, `limit=20`, `unread_only=false`

Response `200 OK`:
```json
{
  "notifications": [
    {
      "id": "ntf_abc123",
      "type": "like",
      "actor": {
        "id": "usr_abc",
        "username": "alex",
        "avatar_url": "..."
      },
      "target": {
        "type": "post",
        "id": "pst_7t3n8z2k",
        "preview_url": "https://cdn.photoshare.io/..."
      },
      "text": "alex liked your photo",
      "is_read": false,
      "created_at": "2026-03-12T10:25:00Z"
    }
  ],
  "unread_count": 7,
  "pagination": { "next_cursor": "...", "has_more": true }
}
```

**POST** `/v1/notifications/mark-read`

Request:
```json
{
  "notification_ids": ["ntf_abc123", "ntf_def456"]
}
```

Response `200 OK`: `{ "marked_read": 2 }`

---

## API Gateway Configuration (Apigee)

| Policy | Config |
|--------|--------|
| Authentication | Firebase JWT validation on all authenticated routes |
| Rate limiting | Quota policy per user tier (regular / verified / partner) |
| Request size limit | 10MB max body |
| Response caching | Cache-Control: max-age=60 for feed; public for profile |
| CORS | Whitelist origins: `*.photoshare.io`, `photoshare.io` |
| Request logging | All requests logged to Cloud Logging with `request_id` |
| DDoS protection | Cloud Armor threat intelligence + geo-blocking |
