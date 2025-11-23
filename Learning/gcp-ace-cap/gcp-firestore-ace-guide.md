# Google Cloud Firestore - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Data Model](#data-model)
4. [Database Creation & Configuration](#database-creation--configuration)
5. [CRUD Operations](#crud-operations)
6. [Queries & Indexing](#queries--indexing)
7. [Security Rules](#security-rules)
8. [Offline Support & Real-time Listeners](#offline-support--real-time-listeners)
9. [Backup & Recovery](#backup--recovery)
10. [Monitoring & Quotas](#monitoring--quotas)
11. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

**Cloud Firestore** is a fully managed, serverless, NoSQL document database for mobile, web, and server development. It provides:
- **Real-time synchronization** across clients
- **Offline support** with automatic sync
- **Flexible, hierarchical data structures**
- **Powerful querying** capabilities
- **Automatic scaling** to handle any workload

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Type** | Document-oriented NoSQL database |
| **Consistency** | Strong consistency for single-document operations |
| **Scalability** | Automatic, unlimited horizontal scaling |
| **Pricing Model** | Pay per operation (reads, writes, deletes) + storage |
| **Global Distribution** | Multi-region replication available |
| **Offline Support** | Built-in client SDKs with offline caching |

### Firestore Editions

**Native Mode (Default):**
- Optimized for mobile and web apps
- Real-time synchronization
- Offline support
- Firebase integration

**Datastore Mode:**
- Server-side applications
- Compatible with legacy Datastore API
- No real-time sync or offline support
- Ideal for App Engine applications

### When to Use Firestore

**Best For:**
- Mobile and web applications
- Real-time collaboration apps (chat, gaming)
- User-generated content platforms
- Applications requiring offline support
- Hierarchical data structures

**Consider Alternatives:**
- **Cloud Spanner:** Relational data, strong consistency, SQL
- **Cloud SQL:** Traditional RDBMS, complex joins
- **Bigtable:** High-throughput analytics, time-series data
- **BigQuery:** Data warehousing, analytics

---

## Core Concepts

### Architecture Components

```
Project
└── Firestore Database
    └── Collections (e.g., "users")
        └── Documents (e.g., "user123")
            ├── Fields (name: "Alice", age: 30)
            └── Subcollections (e.g., "orders")
                └── Documents (e.g., "order456")
```

### Document

A **document** is a lightweight record containing fields with values:
- Similar to JSON objects
- Can contain nested objects and arrays
- Maximum size: 1 MiB
- Identified by unique ID within collection

**Example Document:**
```json
{
  "userId": "user123",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "age": 30,
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA"
  },
  "interests": ["reading", "hiking", "photography"],
  "createdAt": "2024-01-15T10:30:00Z",
  "isActive": true
}
```

### Collection

A **collection** is a container for documents:
- Collections don't exist until they contain at least one document
- Collection names must be odd-length path segments
- Documents in a collection can have different fields
- No schema enforcement

**Path Examples:**
```
/users                           # Collection
/users/user123                   # Document
/users/user123/orders            # Subcollection
/users/user123/orders/order456   # Document in subcollection
```

### Subcollections

**Subcollections** organize data hierarchically:
- Each document can have subcollections
- Subcollections can have their own subcollections
- Deleting parent document doesn't auto-delete subcollections

**Example Hierarchy:**
```
users (collection)
└── alice (document)
    ├── name: "Alice"
    ├── email: "alice@example.com"
    └── orders (subcollection)
        ├── order1 (document)
        │   └── total: 99.99
        └── order2 (document)
            └── total: 149.99
```

---

## Data Model

### Supported Data Types

| Type | Example | Description |
|------|---------|-------------|
| **String** | `"Hello World"` | UTF-8 text, max 1 MiB |
| **Number** | `42`, `3.14` | 64-bit integer or double |
| **Boolean** | `true`, `false` | True or false |
| **Map** | `{city: "SF", zip: 94105}` | Nested object |
| **Array** | `["apple", "banana"]` | Ordered list of values |
| **Null** | `null` | Null value |
| **Timestamp** | `Timestamp(2024, 1, 15)` | Date and time |
| **Geopoint** | `GeoPoint(37.7749, -122.4194)` | Geographic coordinates |
| **Reference** | `db.collection("users").doc("user123")` | Reference to another document |
| **Bytes** | `Bytes([1, 2, 3])` | Binary data (up to 1 MiB) |

### Document Structure Best Practices

**✅ Good Structure:**
```javascript
// Flat structure for simple queries
{
  "userId": "user123",
  "name": "Alice",
  "email": "alice@example.com",
  "city": "San Francisco",
  "state": "CA",
  "country": "USA"
}
```

**✅ Nested Objects for Grouping:**
```javascript
{
  "userId": "user123",
  "name": "Alice",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA"
  }
}
```

**❌ Avoid Deep Nesting:**
```javascript
// Bad: Hard to query, inefficient
{
  "level1": {
    "level2": {
      "level3": {
        "level4": {
          "data": "too deep"
        }
      }
    }
  }
}
```

### Arrays vs Subcollections

**Use Arrays When:**
- Small, bounded lists (<100 items)
- Order matters
- Need to query "contains" operations

```javascript
{
  "userId": "user123",
  "interests": ["reading", "hiking", "photography"]
}
```

**Use Subcollections When:**
- Large or unbounded lists
- Each item is complex (multiple fields)
- Need to query items independently

```javascript
// users/user123 (document)
{
  "name": "Alice"
}

// users/user123/orders (subcollection)
// orders/order1 (document)
{
  "orderId": "order1",
  "total": 99.99,
  "items": [...]
}
```

---

## Database Creation & Configuration

### Creating a Database

**Console:**
1. Navigate to **Firestore** in Cloud Console
2. Click **Create Database**
3. Choose mode:
   - **Native mode** (recommended for new apps)
   - **Datastore mode** (for App Engine compatibility)
4. Select location (e.g., `us-central`)
5. Click **Create Database**

**gcloud:**
```bash
# Create Firestore database in native mode
gcloud firestore databases create \
    --location=us-central \
    --type=firestore-native

# Create in Datastore mode
gcloud firestore databases create \
    --location=us-central \
    --type=datastore-mode
```

### Location Types

| Location Type | Regions | Use Case |
|---------------|---------|----------|
| **Regional** | Single region (e.g., `us-central1`) | Lower cost, regional app |
| **Multi-Region** | Multiple regions (e.g., `nam5`) | Global app, high availability |

**Regional Locations:**
- `us-central1` (Iowa)
- `us-east1` (Virginia)
- `europe-west1` (Belgium)
- `asia-south1` (Mumbai)

**Multi-Region Locations:**
- `nam5` (US multi-region)
- `eur3` (Europe multi-region)

---

## CRUD Operations

### Creating Documents

**Auto-Generated ID:**
```javascript
// JavaScript SDK
const docRef = await db.collection('users').add({
  name: 'Alice',
  email: 'alice@example.com',
  createdAt: firebase.firestore.FieldValue.serverTimestamp()
});
console.log('Document ID:', docRef.id);
```

**Custom ID:**
```javascript
await db.collection('users').doc('user123').set({
  name: 'Alice',
  email: 'alice@example.com'
});
```

**gcloud (REST API):**
```bash
# Create document with auto-generated ID
gcloud firestore documents create \
    --collection-ids=users \
    --fields='name=Alice,email=alice@example.com'
```

### Reading Documents

**Get Single Document:**
```javascript
const docRef = db.collection('users').doc('user123');
const doc = await docRef.get();

if (doc.exists) {
  console.log('Document data:', doc.data());
} else {
  console.log('No such document!');
}
```

**Get Multiple Documents (Query):**
```javascript
const snapshot = await db.collection('users')
  .where('city', '==', 'San Francisco')
  .get();

snapshot.forEach(doc => {
  console.log(doc.id, '=>', doc.data());
});
```

**gcloud:**
```bash
# Get document
gcloud firestore documents describe \
    "projects/PROJECT_ID/databases/(default)/documents/users/user123"
```

### Updating Documents

**Update Specific Fields:**
```javascript
await db.collection('users').doc('user123').update({
  email: 'newemail@example.com',
  'address.city': 'New York'  // Nested field
});
```

**Set with Merge (Upsert):**
```javascript
// Creates document if it doesn't exist, updates if it does
await db.collection('users').doc('user123').set({
  email: 'alice@example.com',
  lastLogin: firebase.firestore.FieldValue.serverTimestamp()
}, { merge: true });
```

**Atomic Operations:**
```javascript
// Increment counter
await db.collection('posts').doc('post123').update({
  likes: firebase.firestore.FieldValue.increment(1)
});

// Add to array
await db.collection('users').doc('user123').update({
  interests: firebase.firestore.FieldValue.arrayUnion('cooking')
});

// Remove from array
await db.collection('users').doc('user123').update({
  interests: firebase.firestore.FieldValue.arrayRemove('hiking')
});
```

### Deleting Documents

**Delete Document:**
```javascript
await db.collection('users').doc('user123').delete();
```

**Delete Field:**
```javascript
await db.collection('users').doc('user123').update({
  email: firebase.firestore.FieldValue.delete()
});
```

**Batch Delete (in client):**
```javascript
const batch = db.batch();
const snapshot = await db.collection('users').where('age', '<', 18).get();

snapshot.forEach(doc => {
  batch.delete(doc.ref);
});

await batch.commit();
```

---

## Queries & Indexing

### Simple Queries

**Equality:**
```javascript
const query = db.collection('users').where('city', '==', 'San Francisco');
```

**Comparison:**
```javascript
const query = db.collection('users').where('age', '>', 25);
```

**Multiple Conditions (AND):**
```javascript
const query = db.collection('users')
  .where('city', '==', 'San Francisco')
  .where('age', '>', 25);
```

**Array Contains:**
```javascript
const query = db.collection('users')
  .where('interests', 'array-contains', 'hiking');
```

**IN Queries (OR):**
```javascript
const query = db.collection('users')
  .where('city', 'in', ['San Francisco', 'New York', 'Seattle']);
```

### Ordering and Limiting

**Order By:**
```javascript
const query = db.collection('users')
  .orderBy('age', 'desc')
  .limit(10);
```

**Pagination (Cursors):**
```javascript
// First page
const first = db.collection('users')
  .orderBy('name')
  .limit(25);

const snapshot = await first.get();
const lastDoc = snapshot.docs[snapshot.docs.length - 1];

// Next page
const next = db.collection('users')
  .orderBy('name')
  .startAfter(lastDoc)
  .limit(25);
```

### Composite Queries

**Multiple Filters and Order:**
```javascript
const query = db.collection('products')
  .where('category', '==', 'electronics')
  .where('price', '<', 500)
  .orderBy('price', 'asc')
  .limit(20);
```

**Note:** Composite queries require indexes!

### Indexes

**Single-Field Indexes:**
- Created automatically for each field
- Support simple queries

**Composite Indexes:**
- Required for complex queries (multiple fields, order by + filter)
- Must be created manually or automatically suggested

**Create Index via Console:**
1. Navigate to **Firestore** > **Indexes**
2. Click **Create Index**
3. Configure:
   - Collection: `products`
   - Fields: `category` (Ascending), `price` (Ascending)
   - Query scope: Collection
4. Click **Create**

**Create Index via gcloud:**
```bash
gcloud firestore indexes composite create \
    --collection-group=products \
    --field-config=field-path=category,order=ascending \
    --field-config=field-path=price,order=ascending
```

**Automatic Index Creation:**
When you run a query that requires an index, Firestore provides an error with a link to create the index automatically.

### Query Limitations

**Cannot Combine:**
- Range filters (`<`, `>`) on multiple fields
- `!=` with other operators (except `orderBy`)
- `array-contains` with `array-contains-any`

**Example (Not Allowed):**
```javascript
// ❌ Cannot use range filters on multiple fields
const query = db.collection('users')
  .where('age', '>', 25)
  .where('score', '<', 100);  // Error!
```

---

## Security Rules

### Overview

**Security Rules** control access to Firestore data:
- Applied to all client SDK access (mobile, web)
- Server SDKs bypass security rules (use IAM)
- Written in a domain-specific language

### Basic Rule Structure

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Rules go here
  }
}
```

### Common Rules Patterns

**Allow All (Development Only):**
```javascript
match /{document=**} {
  allow read, write: if true;
}
```

**Deny All:**
```javascript
match /{document=**} {
  allow read, write: if false;
}
```

**Authenticated Users Only:**
```javascript
match /{document=**} {
  allow read, write: if request.auth != null;
}
```

**User-Specific Data:**
```javascript
// Users can only read/write their own document
match /users/{userId} {
  allow read, write: if request.auth.uid == userId;
}

// Users can only read/write their own orders
match /users/{userId}/orders/{orderId} {
  allow read, write: if request.auth.uid == userId;
}
```

**Content-Based Access:**
```javascript
// Only allow writes if email is verified
match /posts/{postId} {
  allow read: if true;
  allow create: if request.auth != null 
                && request.auth.token.email_verified == true;
  allow update, delete: if request.auth.uid == resource.data.authorId;
}
```

**Field Validation:**
```javascript
match /users/{userId} {
  allow create: if request.auth.uid == userId
                && request.resource.data.keys().hasAll(['name', 'email'])
                && request.resource.data.name is string
                && request.resource.data.name.size() >= 2;
}
```

**Rate Limiting:**
```javascript
match /posts/{postId} {
  allow read: if true;
  allow create: if request.auth != null 
                && request.time > resource.data.lastPost + duration.value(1, 'h');
}
```

### Testing Rules

**Console:**
1. Navigate to **Firestore** > **Rules**
2. Click **Rules Playground**
3. Configure:
   - Location: Collection path
   - Auth: Authenticated/Unauthenticated
   - Action: Read/Write
4. Click **Run**

**Local Testing (Firebase Emulator):**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init firestore

# Start emulator
firebase emulators:start
```

---

## Offline Support & Real-time Listeners

### Offline Persistence

**Enable Offline Support:**
```javascript
// Web
firebase.firestore().enablePersistence()
  .catch((err) => {
    if (err.code == 'failed-precondition') {
      // Multiple tabs open
    } else if (err.code == 'unimplemented') {
      // Browser doesn't support
    }
  });

// Android
FirebaseFirestore.getInstance().setPersistenceEnabled(true);

// iOS
let settings = Firestore.firestore().settings
settings.isPersistenceEnabled = true
Firestore.firestore().settings = settings
```

**How it Works:**
1. Client reads/writes to local cache first
2. Changes sync to server when online
3. Server changes sync to client automatically
4. Conflicts resolved automatically (last write wins)

### Real-time Listeners

**Listen to Document:**
```javascript
const unsubscribe = db.collection('users').doc('user123')
  .onSnapshot((doc) => {
    console.log('Current data:', doc.data());
  }, (error) => {
    console.error('Error:', error);
  });

// Stop listening
unsubscribe();
```

**Listen to Collection:**
```javascript
const unsubscribe = db.collection('posts')
  .where('status', '==', 'published')
  .onSnapshot((snapshot) => {
    snapshot.docChanges().forEach((change) => {
      if (change.type === 'added') {
        console.log('New post:', change.doc.data());
      }
      if (change.type === 'modified') {
        console.log('Modified post:', change.doc.data());
      }
      if (change.type === 'removed') {
        console.log('Removed post:', change.doc.data());
      }
    });
  });
```

**Detach Listener:**
```javascript
// Detach when component unmounts
useEffect(() => {
  const unsubscribe = db.collection('messages').onSnapshot(snapshot => {
    // Handle updates
  });
  
  return () => unsubscribe();  // Cleanup
}, []);
```

---

## Backup & Recovery

### Managed Backups

**Enable Backups (Console):**
1. Navigate to **Firestore** > **Backups**
2. Click **Enable Backups**
3. Configure schedule (daily/weekly)
4. Set retention period

**gcloud:**
```bash
# Create backup
gcloud firestore backups schedules create \
    --database='(default)' \
    --recurrence=daily \
    --retention=7d
```

### Export/Import

**Export Data:**
```bash
# Export all collections
gcloud firestore export gs://my-bucket/firestore-export

# Export specific collections
gcloud firestore export gs://my-bucket/firestore-export \
    --collection-ids=users,posts
```

**Import Data:**
```bash
gcloud firestore import gs://my-bucket/firestore-export
```

### Point-in-Time Recovery (PITR)

**Available in Enterprise Edition:**
- Restore to any point within retention window (up to 7 days)
- No performance impact on production database

```bash
# Restore to specific time (Enterprise only)
gcloud firestore databases restore \
    --source-database='(default)' \
    --destination-database='restored-db' \
    --snapshot-time='2024-11-20T10:30:00Z'
```

---

## Monitoring & Quotas

### Key Metrics

**Cloud Monitoring:**
- Document reads/writes/deletes
- Storage usage
- Connection count
- Error rate

**View Metrics (Console):**
1. Navigate to **Firestore** > **Usage**
2. View read/write operations and storage

### Quotas and Limits

| Resource | Free Tier | Limit |
|----------|-----------|-------|
| **Document Reads** | 50,000/day | No hard limit |
| **Document Writes** | 20,000/day | No hard limit |
| **Document Deletes** | 20,000/day | No hard limit |
| **Storage** | 1 GiB | No hard limit |
| **Document Size** | N/A | 1 MiB |
| **Max Write Rate** | N/A | 10,000/sec per database |
| **Max Indexes** | N/A | 200 composite indexes |

**Important Limits:**
- **Document size:** Max 1 MiB
- **Collection depth:** No limit (but avoid deep nesting)
- **Transaction size:** Max 500 documents
- **Batch size:** Max 500 operations

### Cost Optimization

**Minimize Reads:**
```javascript
// ❌ Bad: Reads entire document for small update
const doc = await db.collection('users').doc('user123').get();
// Process and write back

// ✅ Good: Update directly
await db.collection('users').doc('user123').update({
  lastLogin: firebase.firestore.FieldValue.serverTimestamp()
});
```

**Use Offline Persistence:**
- Reduces redundant reads from cache
- Improves app performance

**Optimize Queries:**
```javascript
// ❌ Bad: Fetches all documents, filters in client
const snapshot = await db.collection('posts').get();
const published = snapshot.docs.filter(doc => doc.data().status === 'published');

// ✅ Good: Filter on server
const snapshot = await db.collection('posts')
  .where('status', '==', 'published')
  .get();
```

---

## ACE Exam Tips

### Key Concepts to Remember

1. **Firestore vs Datastore:**
   - Native mode: Mobile/web, real-time sync, offline support
   - Datastore mode: Server apps, App Engine compatibility, no real-time

2. **Document Structure:**
   - Max size: 1 MiB per document
   - Use subcollections for large datasets (not arrays)
   - Avoid deep nesting (>3 levels)

3. **Queries:**
   - Composite indexes required for complex queries
   - Cannot combine range filters on multiple fields
   - Use `limit()` to control read costs

4. **Security Rules:**
   - Apply to client SDKs only (mobile, web)
   - Server SDKs use IAM instead
   - Test rules in console before deploying

5. **Real-time:**
   - `onSnapshot()` for real-time listeners
   - Offline persistence for mobile apps
   - Detach listeners to avoid memory leaks

6. **Pricing:**
   - Charged per operation (read, write, delete)
   - Storage charged per GiB
   - Minimize reads with offline cache

7. **Backups:**
   - Managed backups (daily/weekly)
   - Export to Cloud Storage for long-term retention
   - PITR available in Enterprise edition

### Common Exam Scenarios

**Scenario 1:** Mobile app needs offline support and real-time sync
- **Answer:** Cloud Firestore (Native mode)

**Scenario 2:** App Engine app needs NoSQL database
- **Answer:** Cloud Firestore (Datastore mode) or legacy Datastore

**Scenario 3:** Query failing with "requires an index"
- **Answer:** Create composite index for the query

**Scenario 4:** Need to control access to user-specific data
- **Answer:** Use Security Rules with `request.auth.uid`

**Scenario 5:** High read costs from mobile app
- **Answer:** Enable offline persistence to cache data locally

**Scenario 6:** Need to export data for analysis
- **Answer:** Use `gcloud firestore export` to Cloud Storage

### Essential Commands

```bash
# Create database
gcloud firestore databases create --location=us-central

# Export data
gcloud firestore export gs://my-bucket/export

# Import data
gcloud firestore import gs://my-bucket/export

# Create composite index
gcloud firestore indexes composite create \
    --collection-group=posts \
    --field-config=field-path=category,order=ascending \
    --field-config=field-path=date,order=descending

# View database info
gcloud firestore databases describe --database='(default)'
```

---

## Additional Resources

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Data Model Guide](https://firebase.google.com/docs/firestore/data-model)
- [Security Rules Guide](https://firebase.google.com/docs/firestore/security/get-started)
- [Query Best Practices](https://firebase.google.com/docs/firestore/query-data/queries)
- [Pricing Calculator](https://firebase.google.com/pricing)

---

**Last Updated:** November 2025  
**Exam:** Google Associate Cloud Engineer (ACE)
