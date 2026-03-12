# 1. Functional & Non-Functional Requirements

---

## 1.1 Problem Statement

Design a **Craigslist-like classified advertisements platform** that allows users to post, browse, and search for listings across hundreds of categories and cities worldwide. The system must handle high read traffic, geographic targeting, and image uploads while remaining simple and performant.

---

## 1.2 Clarifying Questions (Interview Style)

Before diving in, these are key clarifying questions to ask:

| Question | Assumption |
|----------|------------|
| How many monthly active users? | ~50 million MAU |
| How many cities/regions? | ~700+ cities globally |
| Do users need accounts to browse? | No — browsing is anonymous |
| Do users need accounts to post? | Yes — email verification required |
| Do we support real-time chat between buyer/seller? | Basic contact via masked email |
| Do we support paid/promoted listings? | Yes (basic tier) |
| What categories do we support? | Housing, Jobs, For Sale, Services, Community |
| Do we need mobile apps? | Yes — iOS, Android, Web |
| Image uploads per listing? | Up to 24 images |
| Listing expiration? | 7–45 days depending on category |

---

## 1.3 Functional Requirements

### Core User Features

#### 1.3.1 User Management
- [ ] **Register** via email or OAuth (Google, Facebook)
- [ ] **Login / Logout** with session management
- [ ] **Profile management** (display name, phone, location)
- [ ] **Account verification** via email
- [ ] **Password reset** flow

#### 1.3.2 Listing Management
- [ ] **Create a listing** with title, description, category, price, location, and up to 24 images
- [ ] **Edit a listing** (owner only)
- [ ] **Delete / Deactivate** a listing
- [ ] **Renew / Repost** an expired listing
- [ ] **Mark as sold / fulfilled**
- [ ] **Draft saving** — save listing without publishing
- [ ] Listings auto-expire after **7–45 days** by category

#### 1.3.3 Search & Browse
- [ ] **Browse by category** and **city/region**
- [ ] **Full-text search** with keyword matching across title and description
- [ ] **Geo-aware search** — filter by city, neighborhood, radius (miles/km)
- [ ] **Filter listings** by price range, date posted, has image
- [ ] **Sort** by date, price (asc/desc), relevance
- [ ] **Saved searches** — receive alerts for new matching listings
- [ ] **Pagination** of results (25 per page)

#### 1.3.4 Communication
- [ ] **Contact poster** via anonymized/masked email relay
- [ ] **Flag/report** a listing for abuse, spam, or scams
- [ ] **Block a user**
- [ ] Email notifications for:
  - New replies to your listing
  - Saved search alerts
  - Listing expiry reminders

#### 1.3.5 Moderation
- [ ] Admin can **remove flagged listings**
- [ ] Automatic spam detection on listing creation
- [ ] **Ghost posting** — post appears to creator but is hidden from others (spam mitigation)
- [ ] IP-based and account-based rate limiting for posts

#### 1.3.6 Images
- [ ] Upload up to 24 images per listing
- [ ] Auto-resize to multiple resolutions (thumbnail, medium, large)
- [ ] CDN delivery for fast image loading

---

## 1.4 Non-Functional Requirements

### Performance
| Metric | Target |
|--------|--------|
| Search response time (p99) | < 300ms |
| Listing page load time | < 500ms |
| Image upload response | < 2s |
| API response time (p95) | < 200ms |

### Availability & Reliability
| Metric | Target |
|--------|--------|
| Overall system availability | 99.99% (< 52 min downtime/year) |
| Search service availability | 99.9% |
| Data durability | 99.999999999% (11 nines) |
| RPO (Recovery Point Objective) | < 1 minute |
| RTO (Recovery Time Objective) | < 5 minutes |

### Scalability
| Metric | Target |
|--------|--------|
| Monthly Active Users | 50M |
| Daily Active Users | 10M |
| New listings per day | 1M |
| Peak concurrent users | 500K |
| Read:Write ratio | 100:1 |

### Security
- HTTPS/TLS 1.3 everywhere
- Email masking for user privacy
- Input sanitization (XSS, SQL injection prevention)
- Rate limiting on posting (5 posts/day per account, 1 per hour per IP)
- CAPTCHA on account creation and posting
- PII data encryption at rest

### Consistency
- **Eventual consistency** acceptable for search index updates (up to 30s delay)
- **Strong consistency** required for listing creation/deletion
- **Read-your-writes** consistency for listing owner

### Compliance
- GDPR compliant (right to delete, data portability)
- CAN-SPAM Act compliant for email notifications
- COPPA compliant (no users under 18 for certain categories)

---

## 1.5 Out of Scope

- Real-time chat/messaging (would require separate design)
- Payment processing / escrow
- Mobile app architecture (backend API design only)
- ML-based recommendation engine (mentioned but not detailed)
- i18n / multilingual support

---

## 1.6 System Constraints

```
- Single post must be idempotent (no accidental duplicate listings)
- Images stored separately from listing metadata
- Search results must be geographically scoped by default
- Anonymous browsing must not require authentication
- Listing URLs must be shareable and stable (no token-based URLs)
```

---

## 1.7 Feature Priority Matrix

```
Priority 1 (MVP):
  ✅ User auth
  ✅ Create/edit/delete listings
  ✅ Browse by category + city
  ✅ Basic search
  ✅ Image upload
  ✅ Contact poster via email

Priority 2 (Core Product):
  ✅ Full-text + geo search
  ✅ Saved searches + alerts
  ✅ Listing expiry + renewal
  ✅ Spam detection
  ✅ Flagging system

Priority 3 (Growth):
  ✅ Promoted listings
  ✅ Analytics dashboard
  ✅ Advanced filters
  ✅ Mobile push notifications
```
