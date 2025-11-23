# Google Cloud Firestore - Professional Cloud Architect (PCA) Comprehensive Guide

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Design Decisions & Trade-offs](#design-decisions--trade-offs)
3. [Advanced Data Modeling](#advanced-data-modeling)
4. [Performance Optimization](#performance-optimization)
5. [Scalability Patterns](#scalability-patterns)
6. [Security Architecture](#security-architecture)
7. [Multi-Region Strategy](#multi-region-strategy)
8. [Cost Optimization](#cost-optimization)
9. [Enterprise Integration Patterns](#enterprise-integration-patterns)
10. [Migration Strategies](#migration-strategies)
11. [PCA Exam Tips](#pca-exam-tips)

---

## Architectural Overview

Cloud Firestore is a horizontally-scalable, distributed NoSQL document database built on Google's Colossus storage system and Spanner's consistency model. For the Professional Cloud Architect exam, you must design Firestore architectures that optimize for scalability, consistency, cost, and user experience.

### Distributed Architecture

```
Global Firestore Database
├── Region A (Multi-region configuration)
│   ├── Zone A1 (Replicas)
│   ├── Zone A2 (Replicas)
│   └── Zone A3 (Replicas)
├── Region B
│   └── Zones (3x with replicas)
└── Region C
    └── Zones (3x with replicas)
```

**Key Components:**
- **Colossus:** Distributed storage system (Google's next-gen GFS)
- **Megastore:** Provides ACID transactions across datacenter
- **Bigtable-style sharding:** Automatic data distribution
- **Paxos replication:** Strong consistency within regions

### Consistency Model

**Single-Document Operations:**
- **Strong consistency** for reads/writes within a document
- Linearizable (externally consistent)
- Read-your-writes guarantee

**Transactions:**
- **Optimistic concurrency control** (OCC)
- Retries on conflicts
- Max 500 documents per transaction

**Queries:**
- **Eventually consistent** across indexes (typically milliseconds)
- Can be strongly consistent with explicit transactions

---

## Design Decisions & Trade-offs

### Firestore vs Other NoSQL Databases

| Database | Consistency | Scalability | Latency | Cost | Use Case |
|----------|-------------|-------------|---------|------|----------|
| **Firestore** | Strong (single doc) | Horizontal (unlimited) | 5-50ms | Medium | Mobile/web, real-time apps |
| **Datastore** | Strong | Horizontal | 10-100ms | Low | Server apps, App Engine |
| **Bigtable** | Eventual | Horizontal (petabytes) | <10ms | High | Analytics, time-series |
| **MongoDB Atlas** | Strong (tunable) | Horizontal | 10-100ms | High | General-purpose NoSQL |
| **DynamoDB** | Eventual/Strong | Horizontal | <10ms | Medium | AWS-native NoSQL |

### Native Mode vs Datastore Mode

| Aspect | Native Mode | Datastore Mode |
|--------|-------------|----------------|
| **Real-time** | Yes (onSnapshot) | No |
| **Offline** | Yes (mobile SDKs) | No |
| **Client SDKs** | Mobile, Web | Server only |
| **Entity Groups** | No | Yes (strongly consistent) |
| **Transactions** | Optimistic | Pessimistic |
| **Migration** | Cannot → Datastore | Can → Native (one-way) |
| **Use Case** | Mobile/web apps | App Engine, server apps |

**Decision Matrix:**
```
Mobile/Web App? → Yes → Native Mode
Real-time sync needed? → Yes → Native Mode
App Engine app? → Yes → Datastore Mode
Server-only app? → No preference → Native Mode (recommended)
```

### Regional vs Multi-Region

| Configuration | Latency | Availability | Cost | Use Case |
|---------------|---------|--------------|------|----------|
| **Regional** | <10ms local | 99.9% | Baseline | Regional apps |
| **Multi-Region** | 50-300ms cross-region | 99.99% | 2-3x | Global apps |

**Multi-Region Configurations:**
- `nam5` - US multi-region
- `eur3` - Europe multi-region
- Not available in all regions (unlike Spanner)

---

## Advanced Data Modeling

### Document Design Patterns

#### Pattern 1: Flat Documents (Recommended)

```javascript
// ✅ GOOD: Flat structure, easy to query
{
  "orderId": "order123",
  "userId": "user456",
  "status": "shipped",
  "total": 99.99,
  "customerName": "Alice",
  "customerEmail": "alice@example.com",
  "shippingCity": "San Francisco",
  "shippingState": "CA",
  "createdAt": "2024-11-20T10:30:00Z"
}
```

**Advantages:**
- Simple queries: `where('shippingState', '==', 'CA')`
- All data in one read
- Lower latency

**Disadvantages:**
- Data duplication
- Harder to maintain consistency

#### Pattern 2: Normalized with References

```javascript
// orders/order123
{
  "orderId": "order123",
  "userRef": db.collection('users').doc('user456'),  // Reference
  "status": "shipped",
  "total": 99.99,
  "createdAt": "2024-11-20T10:30:00Z"
}

// users/user456
{
  "name": "Alice",
  "email": "alice@example.com"
}
```

**Advantages:**
- No data duplication
- Single source of truth
- Easier to update user data

**Disadvantages:**
- Multiple reads required
- Higher latency (2+ reads)
- More complex client code

#### Pattern 3: Hybrid (Denormalization)

```javascript
// ✅ BEST: Denormalize frequently accessed fields
{
  "orderId": "order123",
  "userId": "user456",
  "userName": "Alice",  // Denormalized
  "userEmail": "alice@example.com",  // Denormalized
  "status": "shipped",
  "total": 99.99,
  "createdAt": "2024-11-20T10:30:00Z"
}
```

**When to Denormalize:**
- Read-heavy fields (user name, email)
- Rarely changing data
- Query performance critical

**When to Normalize:**
- Write-heavy fields
- Frequently changing data
- Large nested objects (>100 KB)

### Subcollection vs Array

**Use Arrays (<100 items):**
```javascript
{
  "postId": "post123",
  "title": "My Post",
  "tags": ["firebase", "nosql", "database"],  // Array
  "likes": 42
}

// Query
db.collection('posts').where('tags', 'array-contains', 'firebase')
```

**Use Subcollections (>100 items):**
```javascript
// posts/post123
{
  "postId": "post123",
  "title": "My Post"
}

// posts/post123/comments (subcollection)
// comments/comment456
{
  "commentId": "comment456",
  "text": "Great post!",
  "author": "Bob"
}
```

### Collection Group Queries

**Scenario:** Query all comments across all posts

```javascript
// Traditional approach (inefficient)
const posts = await db.collection('posts').get();
for (const post of posts.docs) {
  const comments = await db.collection('posts').doc(post.id)
    .collection('comments').get();
  // Process comments
}

// ✅ Collection Group Query (efficient)
const allComments = await db.collectionGroup('comments')
  .where('author', '==', 'Bob')
  .orderBy('createdAt', 'desc')
  .limit(50)
  .get();
```

**Index Required:**
- Collection group queries require special indexes
- Create in console or via automatic suggestion

### Root-Level Collections vs Subcollections

**Root-Level Collections:**
```
/users/{userId}
/posts/{postId}
/comments/{commentId}
```

**Advantages:**
- Easier to query all documents
- Collection group queries work
- Simpler structure

**Subcollections:**
```
/users/{userId}/posts/{postId}/comments/{commentId}
```

**Advantages:**
- Hierarchical organization
- Clear ownership (user → posts → comments)
- Can delete parent without subcollections (manual cleanup)

**Decision:**
- Use root-level for independent entities (users, products)
- Use subcollections for hierarchical data (user orders, post comments)

---

## Performance Optimization

### Query Optimization

#### Minimize Read Operations

**❌ Bad: Read entire collection, filter in client**
```javascript
const snapshot = await db.collection('products').get();
const expensive = snapshot.docs.filter(doc => doc.data().price > 100);
// Cost: N reads (all products)
```

**✅ Good: Server-side filtering**
```javascript
const snapshot = await db.collection('products')
  .where('price', '>', 100)
  .get();
// Cost: M reads (only matching products)
```

#### Use Cursors for Pagination

**❌ Bad: Offset-based pagination**
```javascript
const page2 = await db.collection('products')
  .orderBy('name')
  .limit(25)
  .offset(25)  // Skips 25 docs (still charged!)
  .get();
// Cost: 50 reads (25 skipped + 25 returned)
```

**✅ Good: Cursor-based pagination**
```javascript
// Page 1
const page1 = await db.collection('products')
  .orderBy('name')
  .limit(25)
  .get();
const lastDoc = page1.docs[page1.docs.length - 1];

// Page 2
const page2 = await db.collection('products')
  .orderBy('name')
  .startAfter(lastDoc)
  .limit(25)
  .get();
// Cost: 25 reads (only page 2)
```

#### Index Design

**Single-Field Indexes:**
- Automatically created for every field
- Support simple queries (`where`, `orderBy`)

**Composite Indexes:**
- Required for queries with multiple filters or order clauses
- Must be created manually

**Covering Queries (Index-Only):**
```javascript
// Query uses only indexed fields (no document read)
const snapshot = await db.collection('users')
  .where('city', '==', 'San Francisco')
  .select('name', 'email')  // Only return these fields
  .get();
// Cheaper: Index read only (no full document read)
```

**Index Exemptions:**
- `!=` and `not-in` require exemption to avoid excessive indexes
- Managed in console under Firestore > Index Exemptions

### Batching Operations

**Batch Writes (up to 500 operations):**
```javascript
const batch = db.batch();

// Add multiple operations
batch.set(db.collection('users').doc('user1'), { name: 'Alice' });
batch.update(db.collection('users').doc('user2'), { age: 30 });
batch.delete(db.collection('users').doc('user3'));

// Commit atomically
await batch.commit();
// Cost: 3 writes (atomic, all-or-nothing)
```

**When to Use Batches:**
- Multiple related writes
- Need atomicity (all succeed or all fail)
- Reduce round trips

### Caching Strategies

**Client-Side Caching:**
```javascript
// Enable offline persistence (web)
firebase.firestore().enablePersistence()
  .then(() => {
    // Reads from cache when available
    const doc = await db.collection('users').doc('user123')
      .get({ source: 'cache' });  // Try cache first
  });
```

**Application-Level Caching (Cloud Functions):**
```javascript
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600 });

exports.getProduct = functions.https.onRequest(async (req, res) => {
  const productId = req.query.id;
  
  // Check cache
  let product = cache.get(productId);
  if (!product) {
    // Cache miss, read from Firestore
    const doc = await db.collection('products').doc(productId).get();
    product = doc.data();
    cache.set(productId, product);
  }
  
  res.json(product);
});
```

**CDN Caching (Static Data):**
```javascript
// Set cache-control headers for Cloud Functions
res.set('Cache-Control', 'public, max-age=300, s-maxage=600');
res.json(data);
```

### Hot Spotting Prevention

**Problem: Sequential Document IDs**
```javascript
// ❌ Bad: Sequential IDs create hot spots
for (let i = 0; i < 10000; i++) {
  await db.collection('logs').doc(`log-${i}`).set({
    timestamp: Date.now(),
    message: `Log ${i}`
  });
}
// All writes go to same shard (hot spot)
```

**Solution: Random/UUID Document IDs**
```javascript
// ✅ Good: Random IDs distribute writes
for (let i = 0; i < 10000; i++) {
  await db.collection('logs').add({  // Auto-generated ID
    timestamp: Date.now(),
    message: `Log ${i}`
  });
}
// Writes distributed across shards
```

---

## Scalability Patterns

### Sharding Strategies

**Automatic Sharding:**
- Firestore automatically shards collections based on document IDs
- Each shard handles ~500 writes/second
- Scales horizontally as needed

**Manual Sharding (for extreme scale):**
```javascript
// Shard counter across multiple documents
const shardId = Math.floor(Math.random() * 10);  // 10 shards
await db.collection('stats').doc(`counter_${shardId}`).update({
  count: firebase.firestore.FieldValue.increment(1)
});

// Read total across shards
const snapshot = await db.collection('stats')
  .where(firebase.firestore.FieldPath.documentId(), '>=', 'counter_0')
  .where(firebase.firestore.FieldPath.documentId(), '<=', 'counter_9')
  .get();
const total = snapshot.docs.reduce((sum, doc) => sum + doc.data().count, 0);
```

### Fan-Out Pattern (for real-time feeds)

**Scenario:** User posts update, notify all followers

**❌ Bad: Read-Time Fan-Out (doesn't scale)**
```javascript
// When user opens feed
const following = await db.collection('users').doc(userId)
  .collection('following').get();

for (const follow of following.docs) {
  const posts = await db.collection('users').doc(follow.id)
    .collection('posts').limit(10).get();
  // Merge into feed
}
// Problem: N+1 reads per user (expensive!)
```

**✅ Good: Write-Time Fan-Out (scalable)**
```javascript
// When user creates post (via Cloud Function)
exports.onPostCreated = functions.firestore
  .document('posts/{postId}')
  .onCreate(async (snap, context) => {
    const post = snap.data();
    
    // Get all followers
    const followers = await db.collection('users').doc(post.authorId)
      .collection('followers').get();
    
    // Fan-out to each follower's feed
    const batch = db.batch();
    followers.forEach(follower => {
      const feedRef = db.collection('users').doc(follower.id)
        .collection('feed').doc(context.params.postId);
      batch.set(feedRef, post);
    });
    
    await batch.commit();
  });

// When user opens feed (fast!)
const feed = await db.collection('users').doc(userId)
  .collection('feed')
  .orderBy('createdAt', 'desc')
  .limit(50)
  .get();
// Cost: 1 query (50 reads)
```

### Aggregation Pattern (for counters)

**❌ Bad: Real-Time Aggregation**
```javascript
// Count total likes (expensive!)
const snapshot = await db.collection('posts').doc(postId)
  .collection('likes').get();
const totalLikes = snapshot.size;
// Cost: N reads (all likes)
```

**✅ Good: Counter Field (updated transactionally)**
```javascript
// posts/post123
{
  "title": "My Post",
  "likeCount": 42,  // Maintained counter
  "createdAt": "2024-11-20T10:30:00Z"
}

// When user likes post
await db.runTransaction(async (transaction) => {
  const postRef = db.collection('posts').doc(postId);
  const post = await transaction.get(postRef);
  
  transaction.update(postRef, {
    likeCount: post.data().likeCount + 1
  });
  
  transaction.set(
    db.collection('posts').doc(postId).collection('likes').doc(userId),
    { likedAt: firebase.firestore.FieldValue.serverTimestamp() }
  );
});
// Cost: 2 reads + 2 writes
```

**For High-Frequency Updates (Distributed Counter):**
```javascript
// Shard counter to handle >1 write/second
const numShards = 10;
const shardId = Math.floor(Math.random() * numShards);

await db.collection('posts').doc(postId)
  .collection('likesShards').doc(`shard_${shardId}`)
  .update({
    count: firebase.firestore.FieldValue.increment(1)
  });

// Read total (background job)
const shards = await db.collection('posts').doc(postId)
  .collection('likesShards').get();
const total = shards.docs.reduce((sum, doc) => sum + doc.data().count, 0);

// Update main counter
await db.collection('posts').doc(postId).update({ likeCount: total });
```

---

## Security Architecture

### Defense-in-Depth Strategy

**Layer 1: Security Rules (Client SDKs)**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isOwner(userId) {
      return request.auth.uid == userId;
    }
    
    function isValidUser(data) {
      return data.keys().hasAll(['name', 'email', 'createdAt'])
        && data.name is string
        && data.name.size() >= 2
        && data.email.matches('.*@.*\\..*');
    }
    
    // User documents
    match /users/{userId} {
      allow read: if isAuthenticated();
      allow create: if isOwner(userId) && isValidUser(request.resource.data);
      allow update: if isOwner(userId);
      allow delete: if false;  // Never allow delete
    }
    
    // Private user data
    match /users/{userId}/private/{document=**} {
      allow read, write: if isOwner(userId);
    }
    
    // Posts
    match /posts/{postId} {
      allow read: if resource.data.visibility == 'public' 
                  || isOwner(resource.data.authorId);
      allow create: if isAuthenticated() 
                    && request.resource.data.authorId == request.auth.uid;
      allow update, delete: if isOwner(resource.data.authorId);
    }
  }
}
```

**Layer 2: IAM (Server SDKs)**
```bash
# Grant Cloud Function access to Firestore
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=serviceAccount:function-sa@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/datastore.user
```

**Layer 3: VPC Service Controls (Enterprise)**
```bash
# Create perimeter for Firestore
gcloud access-context-manager perimeters create firestore-perimeter \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=firestore.googleapis.com \
    --policy=POLICY_ID
```

### Advanced Security Rules

**Role-Based Access Control (RBAC):**
```javascript
// users/user123
{
  "name": "Alice",
  "role": "admin"  // or "editor", "viewer"
}

// Security Rules
match /documents/{documentId} {
  function getUserRole() {
    return get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role;
  }
  
  allow read: if getUserRole() in ['admin', 'editor', 'viewer'];
  allow write: if getUserRole() in ['admin', 'editor'];
  allow delete: if getUserRole() == 'admin';
}
```

**Attribute-Based Access Control (ABAC):**
```javascript
match /documents/{documentId} {
  allow read: if request.auth.token.email_verified == true;
  allow write: if request.auth.token.email.matches('.*@company\\.com$');
}
```

**Rate Limiting:**
```javascript
match /posts/{postId}/likes/{likeId} {
  // Limit to 1 like per user per post per hour
  allow create: if !exists(/databases/$(database)/documents/posts/$(postId)/likes/$(request.auth.uid))
                && request.time > resource.data.get('lastLikeTime', timestamp.value(0, 0)) 
                   + duration.value(1, 'h');
}
```

### Sensitive Data Protection

**Client-Side Encryption (before writing):**
```javascript
const crypto = require('crypto');

function encrypt(text, key) {
  const cipher = crypto.createCipher('aes-256-cbc', key);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

// Encrypt before writing
await db.collection('users').doc(userId).set({
  name: 'Alice',
  ssn: encrypt(ssn, encryptionKey),  // Encrypted field
  email: 'alice@example.com'
});
```

**Use Secret Manager for Keys:**
```javascript
const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');
const client = new SecretManagerServiceClient();

async function getEncryptionKey() {
  const [version] = await client.accessSecretVersion({
    name: 'projects/PROJECT_ID/secrets/firestore-encryption-key/versions/latest'
  });
  return version.payload.data.toString();
}
```

---

## Multi-Region Strategy

### Configuration Selection

**Regional (nam5, eur3):**
```
Database Location: nam5 (US multi-region)
├── us-central1 (Iowa)
├── us-east1 (Virginia)
└── us-west1 (Oregon)
```

**Advantages:**
- 99.99% SLA
- <50ms latency within continent
- Automatic replication across regions
- Lower cost than global

**Multi-Region with Read Replicas:**
- Not directly supported (unlike Spanner)
- Use Firebase Hosting + CDN for static content caching

### Cross-Region Data Access Patterns

**Pattern 1: Geo-Partitioned Data**
```javascript
// Separate databases per region
const db = region === 'US' 
  ? firebase.firestore(usApp)
  : firebase.firestore(euApp);

await db.collection('users').doc(userId).set(data);
```

**Pattern 2: Centralized Database with Client Routing**
```javascript
// Single multi-region database, smart client routing
const db = firebase.firestore();
db.settings({
  ignoreUndefinedProperties: true,
  merge: true
});

// Writes go to nearest replica automatically
await db.collection('users').doc(userId).set(data);
```

---

## Cost Optimization

### Cost Model

**Operations:**
- Document reads: $0.06 per 100,000
- Document writes: $0.18 per 100,000
- Document deletes: $0.02 per 100,000
- **Regional:** Baseline
- **Multi-region:** 2x operations cost

**Storage:**
- $0.18/GB/month (regional)
- $0.36/GB/month (multi-region)

**Network:**
- Egress: Standard GCP rates

### Optimization Strategies

**1. Minimize Reads with Offline Persistence**
```javascript
// Enable persistence (mobile/web)
firebase.firestore().enablePersistence();

// Reads from cache (free!)
const doc = await db.collection('users').doc(userId).get();
// If cached, cost = $0; if not cached, cost = 1 read
```

**2. Use Transactions Wisely**
```javascript
// ❌ Bad: Unnecessary transaction
const doc = await db.collection('users').doc(userId).get();  // 1 read
await db.collection('users').doc(userId).update({ age: 30 });  // 1 write
// Cost: 1 read + 1 write

// ✅ Good: Direct update (no read needed)
await db.collection('users').doc(userId).update({ age: 30 });
// Cost: 1 write
```

**3. Bulk Operations with Batching**
```javascript
// Write 500 documents in single batch
const batch = db.batch();
for (let i = 0; i < 500; i++) {
  const ref = db.collection('items').doc();
  batch.set(ref, { name: `Item ${i}` });
}
await batch.commit();
// Cost: 500 writes (same as individual, but 1 round trip)
```

**4. Delete Old Data (Storage Costs)**
```javascript
// Schedule Cloud Function to delete old logs
exports.deleteOldLogs = functions.pubsub
  .schedule('every 24 hours')
  .onRun(async (context) => {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - 30);  // 30 days ago
    
    const snapshot = await db.collection('logs')
      .where('createdAt', '<', cutoff)
      .limit(500)
      .get();
    
    const batch = db.batch();
    snapshot.docs.forEach(doc => batch.delete(doc.ref));
    await batch.commit();
    
    return null;
  });
```

**5. Optimize Queries (Reduce Read Count)**
```javascript
// ❌ Bad: Read all, filter client-side
const all = await db.collection('products').get();  // 10,000 reads
const active = all.docs.filter(d => d.data().active);

// ✅ Good: Filter server-side
const active = await db.collection('products')
  .where('active', '==', true)
  .get();  // 1,000 reads
```

**6. Use Regional for Cost Savings**
- Multi-region: 2x read/write costs, 2x storage
- Use regional unless global distribution required

---

## Enterprise Integration Patterns

### Event-Driven Architecture with Cloud Functions

**Firestore Triggers:**
```javascript
// On document create
exports.onUserCreate = functions.firestore
  .document('users/{userId}')
  .onCreate(async (snap, context) => {
    const user = snap.data();
    
    // Send welcome email
    await sendEmail(user.email, 'Welcome!');
    
    // Initialize user profile
    await snap.ref.collection('profile').doc('settings').set({
      theme: 'light',
      notifications: true
    });
  });

// On document update
exports.onOrderUpdate = functions.firestore
  .document('orders/{orderId}')
  .onUpdate(async (change, context) => {
    const before = change.before.data();
    const after = change.after.data();
    
    if (before.status !== 'shipped' && after.status === 'shipped') {
      // Send shipping notification
      await sendShippingNotification(after);
    }
  });

// On document delete
exports.onUserDelete = functions.firestore
  .document('users/{userId}')
  .onDelete(async (snap, context) => {
    const userId = context.params.userId;
    
    // Clean up related data
    const batch = db.batch();
    const posts = await db.collection('posts')
      .where('authorId', '==', userId)
      .get();
    posts.forEach(doc => batch.delete(doc.ref));
    await batch.commit();
  });
```

### Integration with BigQuery (Analytics)

**Export to BigQuery (Scheduled):**
```bash
# Enable Firestore BigQuery export extension
firebase ext:install firestore-bigquery-export

# Configure
# - Collection path: users
# - BigQuery dataset: firestore_export
# - BigQuery table: users
```

**Query in BigQuery:**
```sql
-- Analyze user growth
SELECT 
  DATE(timestamp) as date,
  COUNT(*) as new_users
FROM `project.firestore_export.users`
WHERE operation = 'INSERT'
GROUP BY date
ORDER BY date DESC;
```

### Integration with Cloud Pub/Sub

```javascript
const { PubSub } = require('@google-cloud/pubsub');
const pubsub = new PubSub();

exports.onNewOrder = functions.firestore
  .document('orders/{orderId}')
  .onCreate(async (snap, context) => {
    const order = snap.data();
    
    // Publish to Pub/Sub for downstream processing
    const topic = pubsub.topic('new-orders');
    await topic.publishJSON({
      orderId: context.params.orderId,
      userId: order.userId,
      total: order.total,
      timestamp: Date.now()
    });
  });
```

---

## Migration Strategies

### Migrating from MongoDB

**Schema Differences:**
- MongoDB: Collections → Documents → Fields
- Firestore: Collections → Documents → Fields (similar!)

**Migration Steps:**
1. Export MongoDB data to JSON
2. Transform data format
3. Import to Firestore using Admin SDK

**Example Migration Script:**
```javascript
const admin = require('firebase-admin');
const MongoClient = require('mongodb').MongoClient;

admin.initializeApp();
const db = admin.firestore();

async function migrateUsers() {
  const mongoClient = await MongoClient.connect('mongodb://localhost:27017');
  const mongoDb = mongoClient.db('myapp');
  const users = await mongoDb.collection('users').find().toArray();
  
  const batch = db.batch();
  let count = 0;
  
  for (const user of users) {
    const docRef = db.collection('users').doc(user._id.toString());
    const firestoreUser = {
      name: user.name,
      email: user.email,
      createdAt: admin.firestore.Timestamp.fromDate(user.createdAt)
    };
    batch.set(docRef, firestoreUser);
    
    count++;
    if (count % 500 === 0) {
      await batch.commit();
      console.log(`Migrated ${count} users`);
    }
  }
  
  await batch.commit();
  console.log(`Migration complete: ${count} users`);
}
```

### Migrating from SQL Databases

**Challenges:**
- Relational → Document model
- Joins → Denormalization or multiple reads
- Transactions → Limited to 500 documents

**Strategy:**
1. **Identify entity relationships**
2. **Denormalize where appropriate**
3. **Use subcollections for one-to-many**
4. **Migrate in phases** (test with subset)

**Example: Orders System**
```sql
-- SQL Schema
CREATE TABLE users (id, name, email);
CREATE TABLE orders (id, user_id, total, created_at);
CREATE TABLE order_items (id, order_id, product_id, quantity);
```

**Firestore Schema:**
```javascript
// Denormalized approach (fast reads)
// users/user123
{
  "name": "Alice",
  "email": "alice@example.com"
}

// orders/order456
{
  "userId": "user123",
  "userName": "Alice",  // Denormalized
  "userEmail": "alice@example.com",  // Denormalized
  "total": 99.99,
  "items": [
    { "productId": "prod1", "quantity": 2 },
    { "productId": "prod2", "quantity": 1 }
  ],
  "createdAt": "2024-11-20T10:30:00Z"
}
```

---

## PCA Exam Tips

### Key Architectural Patterns

1. **Firestore Selection:**
   - Mobile/web + real-time → Firestore Native
   - Server-only + App Engine → Firestore Datastore mode
   - Need SQL → Cloud SQL or Spanner

2. **Data Modeling:**
   - **Denormalize** for read performance (duplicate frequently accessed fields)
   - **Normalize** for write consistency (use references for infrequently accessed data)
   - **Arrays** for small lists (<100), **subcollections** for large lists

3. **Scalability:**
   - Avoid sequential IDs (use auto-generated UUIDs)
   - Use fan-out pattern for real-time feeds (write-time, not read-time)
   - Shard counters for high-frequency updates (>1/sec)

4. **Performance:**
   - Enable offline persistence (reduces reads)
   - Use cursor pagination (not offset)
   - Create composite indexes for complex queries
   - Cache data at application/CDN level

5. **Security:**
   - Security Rules for client SDKs (mobile, web)
   - IAM for server SDKs (Cloud Functions, Compute Engine)
   - Never trust client data (validate in Security Rules)

6. **Cost Optimization:**
   - Minimize reads (use caching, offline persistence)
   - Use batches for bulk operations
   - Delete old data to reduce storage costs
   - Use regional (not multi-region) unless global required

7. **Multi-Region:**
   - Multi-region: 2x operation costs, 99.99% SLA
   - Regional: Lower cost, 99.9% SLA
   - Choose location close to users

### Common Exam Scenarios

**Scenario 1:** Mobile app with offline support and real-time sync
- **Answer:** Cloud Firestore (Native mode) with offline persistence

**Scenario 2:** Social media app, need real-time feed for 1M users
- **Answer:** Firestore with write-time fan-out pattern (Cloud Functions)

**Scenario 3:** High write rate causing hot spots
- **Answer:** Use auto-generated document IDs (not sequential)

**Scenario 4:** Need to restrict users to only their own data
- **Answer:** Security Rules with `request.auth.uid == userId`

**Scenario 5:** Analytics on Firestore data (millions of documents)
- **Answer:** Export to BigQuery for analysis (not direct Firestore queries)

**Scenario 6:** Migrating from MongoDB to Firestore
- **Answer:** Export JSON, transform, bulk import via Admin SDK

**Scenario 7:** Need ACID transactions across >500 documents
- **Answer:** Use Cloud Spanner (Firestore limited to 500 docs/transaction)

### Decision Trees

**Database Selection:**
```
Mobile/Web app? → Yes → Firestore Native
Real-time sync needed? → Yes → Firestore Native
App Engine (legacy)? → Yes → Firestore Datastore mode
SQL required? → Yes → Cloud SQL or Spanner
High-throughput analytics? → Yes → Bigtable
```

**Data Modeling:**
```
Small list (<100 items)? → Yes → Use array
Large list (>100 items)? → Yes → Use subcollection
Frequently read together? → Yes → Denormalize
Frequently updated? → Yes → Normalize (use reference)
```

---

## Additional Resources

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Data Model Guide](https://firebase.google.com/docs/firestore/data-model)
- [Security Rules Reference](https://firebase.google.com/docs/firestore/security/rules-structure)
- [Best Practices](https://firebase.google.com/docs/firestore/best-practices)
- [Pricing Calculator](https://firebase.google.com/pricing)
- [Solutions for Common Use Cases](https://firebase.google.com/docs/firestore/solutions)

---

**Last Updated:** November 2025  
**Exam:** Google Professional Cloud Architect (PCA)
