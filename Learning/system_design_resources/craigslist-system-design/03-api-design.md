# 3. API Design

---

## 3.1 API Design Principles

- **RESTful** with JSON payloads
- **Versioned** under `/api/v1/`
- **JWT Bearer Token** authentication via Firebase Auth
- Standard HTTP status codes
- Pagination via `cursor` (keyset) for listings, `offset/limit` for admin
- Rate limiting headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- All timestamps in **ISO 8601 UTC** format
- **Idempotency-Key** header on mutating requests to prevent duplicates

---

## 3.2 Authentication APIs

### POST /api/v1/auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "display_name": "John Doe",
  "phone": "+14155552671"
}
```
**Response `201 Created`:**
```json
{
  "user_id": "usr_01HQ2K8XYZABC",
  "email": "user@example.com",
  "display_name": "John Doe",
  "verification_sent": true,
  "created_at": "2026-03-12T10:00:00Z"
}
```

---

### POST /api/v1/auth/login
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}
```
**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

---

### POST /api/v1/auth/refresh
Rotate access token using refresh token.

### POST /api/v1/auth/logout
Invalidate current session.

### POST /api/v1/auth/verify-email
**Request:** `{ "token": "<email-verification-token>" }`

### POST /api/v1/auth/forgot-password
**Request:** `{ "email": "user@example.com" }`

---

## 3.3 Listing APIs

### POST /api/v1/listings — Create Listing
`Authorization: Bearer <token>` | `Idempotency-Key: <uuid>`

**Request:**
```json
{
  "title": "2BR Apartment for Rent - Downtown SF",
  "description": "Spacious 2 bedroom, 1 bath apartment...",
  "category_id": "cat_housing_rentals",
  "subcategory_id": "subcat_apartments",
  "price": 2500.00,
  "price_type": "monthly",
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "zip": "94105",
    "lat": 37.7749,
    "lng": -122.4194,
    "neighborhood": "SoMa"
  },
  "contact": {
    "method": "email",
    "show_phone": false
  },
  "tags": ["pet-friendly", "laundry-in-unit", "parking"],
  "images": ["img_01", "img_02", "img_03"],
  "status": "active"
}
```

**Response `201 Created`:**
```json
{
  "listing_id": "lst_01HQ2K8XYZDEF",
  "url": "https://craigslist.com/sf/apa/lst_01HQ2K8XYZDEF",
  "status": "active",
  "expires_at": "2026-04-11T10:00:00Z",
  "created_at": "2026-03-12T10:00:00Z"
}
```

---

### GET /api/v1/listings/:id — Get Listing Detail

**Response `200 OK`:**
```json
{
  "listing_id": "lst_01HQ2K8XYZDEF",
  "title": "2BR Apartment for Rent - Downtown SF",
  "description": "Spacious 2 bedroom, 1 bath apartment...",
  "category": {
    "id": "cat_housing_rentals",
    "name": "Housing > Apts/Housing For Rent"
  },
  "price": 2500.00,
  "price_type": "monthly",
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "neighborhood": "SoMa",
    "lat": 37.7749,
    "lng": -122.4194
  },
  "images": [
    {
      "image_id": "img_01",
      "thumbnail_url": "https://cdn.craigslist.com/img_01_thumb.jpg",
      "medium_url": "https://cdn.craigslist.com/img_01_med.jpg",
      "large_url": "https://cdn.craigslist.com/img_01_lg.jpg"
    }
  ],
  "views": 142,
  "status": "active",
  "poster": {
    "display_name": "John D.",
    "member_since": "2022-01-01"
  },
  "expires_at": "2026-04-11T10:00:00Z",
  "created_at": "2026-03-12T10:00:00Z",
  "updated_at": "2026-03-12T10:00:00Z"
}
```

---

### PUT /api/v1/listings/:id — Update Listing
`Authorization: Bearer <token>` (owner only)

**Request:** Partial update — only fields to change.
```json
{
  "price": 2400.00,
  "description": "Updated description..."
}
```
**Response `200 OK`:** Updated listing object.

---

### DELETE /api/v1/listings/:id — Delete Listing
`Authorization: Bearer <token>` (owner only)
**Response `204 No Content`**

---

### POST /api/v1/listings/:id/renew — Renew Listing
Resets expiration timer.
**Response `200 OK`:** `{ "expires_at": "2026-05-12T10:00:00Z" }`

---

### GET /api/v1/users/me/listings — My Listings
**Query Params:** `status=active|expired|sold&cursor=<cursor>&limit=25`

**Response `200 OK`:**
```json
{
  "listings": [ ... ],
  "next_cursor": "eyJpZCI6Imxzd...",
  "total": 12
}
```

---

## 3.4 Search APIs

### GET /api/v1/listings/search — Search Listings

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Full-text search query |
| `category_id` | string | Filter by category |
| `city` | string | City name |
| `state` | string | State code |
| `lat` | float | Latitude (for geo search) |
| `lng` | float | Longitude |
| `radius_miles` | int | Radius from lat/lng (default: 25) |
| `min_price` | float | Minimum price |
| `max_price` | float | Maximum price |
| `has_image` | bool | Only listings with images |
| `posted_after` | ISO 8601 | Posted after date |
| `sort` | string | `date_desc`, `date_asc`, `price_asc`, `price_desc`, `relevance` |
| `cursor` | string | Pagination cursor |
| `limit` | int | Results per page (max 100, default 25) |

**Example:** `GET /api/v1/listings/search?q=apartment&city=San+Francisco&state=CA&min_price=1500&max_price=3000&has_image=true&sort=date_desc&limit=25`

**Response `200 OK`:**
```json
{
  "query": "apartment",
  "total_results": 2847,
  "results": [
    {
      "listing_id": "lst_01HQ2K8XYZDEF",
      "title": "2BR Apartment for Rent - Downtown SF",
      "price": 2500.00,
      "price_type": "monthly",
      "thumbnail_url": "https://cdn.craigslist.com/img_01_thumb.jpg",
      "location": { "city": "San Francisco", "neighborhood": "SoMa" },
      "posted_at": "2026-03-12T10:00:00Z",
      "distance_miles": 1.2
    }
  ],
  "next_cursor": "eyJpZCI6Imxzd...",
  "facets": {
    "categories": [
      { "id": "cat_housing_rentals", "name": "Apartments", "count": 1843 }
    ],
    "price_ranges": [
      { "range": "1500-2000", "count": 921 },
      { "range": "2000-2500", "count": 673 }
    ]
  }
}
```

---

## 3.5 Image Upload APIs

### POST /api/v1/images/upload-url — Get Pre-signed Upload URL
`Authorization: Bearer <token>`

**Request:**
```json
{
  "filename": "apartment_photo.jpg",
  "content_type": "image/jpeg",
  "file_size_bytes": 2457600
}
```

**Response `200 OK`:**
```json
{
  "image_id": "img_01HQ2K8XYZGHI",
  "upload_url": "https://storage.googleapis.com/craigslist-images/...",
  "upload_expires_at": "2026-03-12T10:15:00Z",
  "max_file_size_bytes": 10485760
}
```

> Client uploads directly to GCS using the pre-signed URL. No image bytes pass through the API server.

---

### GET /api/v1/images/:id/status — Check Processing Status
```json
{
  "image_id": "img_01",
  "status": "ready",
  "variants": {
    "thumbnail": "https://cdn.craigslist.com/img_01_thumb.jpg",
    "medium": "https://cdn.craigslist.com/img_01_med.jpg",
    "large": "https://cdn.craigslist.com/img_01_lg.jpg"
  }
}
```

---

## 3.6 Communication APIs

### POST /api/v1/listings/:id/contact — Contact Poster

**Request:**
```json
{
  "message": "Hi, is this apartment still available? I'd like to schedule a viewing.",
  "reply_to_email": "buyer@example.com"
}
```

**Response `202 Accepted`:**
```json
{
  "message_id": "msg_01HQ",
  "status": "queued",
  "note": "Your message will be relayed to the poster via anonymous email."
}
```

---

## 3.7 Flag/Report APIs

### POST /api/v1/listings/:id/flag

**Request:**
```json
{
  "reason": "spam",
  "details": "This listing appears multiple times"
}
```
_Reason options: `spam`, `wrong_category`, `prohibited`, `scam`, `offensive`, `already_sold`_

**Response `202 Accepted`:** `{ "flag_id": "flg_01", "status": "received" }`

---

## 3.8 Saved Search APIs

### POST /api/v1/saved-searches — Save a Search
**Request:**
```json
{
  "name": "SF Apartments under $2500",
  "search_params": {
    "q": "apartment",
    "category_id": "cat_housing_rentals",
    "city": "San Francisco",
    "max_price": 2500
  },
  "notify": true,
  "notify_frequency": "daily"
}
```

### GET /api/v1/saved-searches — List My Saved Searches
### DELETE /api/v1/saved-searches/:id — Delete Saved Search

---

## 3.9 Categories APIs

### GET /api/v1/categories — List All Categories
```json
{
  "categories": [
    {
      "id": "cat_housing",
      "name": "Housing",
      "subcategories": [
        { "id": "subcat_apts", "name": "Apts/Housing For Rent" },
        { "id": "subcat_housing_sale", "name": "Housing For Sale" }
      ]
    },
    {
      "id": "cat_jobs",
      "name": "Jobs",
      "subcategories": [ ... ]
    }
  ]
}
```

---

## 3.10 Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "LISTING_NOT_FOUND",
    "message": "The requested listing does not exist or has expired.",
    "status": 404,
    "request_id": "req_01HQ2K8XYZJKL"
  }
}
```

| HTTP Status | Error Code | Meaning |
|-------------|------------|---------|
| 400 | `VALIDATION_ERROR` | Invalid request body |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Not listing owner |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 409 | `DUPLICATE_REQUEST` | Idempotency key conflict |
| 422 | `UNPROCESSABLE_ENTITY` | Business rule violation |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Temporary outage |

---

## 3.11 Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /listings | 5 per account | 24 hours |
| POST /listings | 1 per IP | 1 hour |
| GET /listings/search | 100 requests | 1 minute |
| POST /images/upload-url | 50 requests | 1 hour |
| POST /listings/:id/contact | 20 requests | 1 hour |
| Auth endpoints | 10 attempts | 15 minutes |
