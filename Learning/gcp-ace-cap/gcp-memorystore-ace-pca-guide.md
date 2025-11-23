# Google Cloud Memorystore - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Memorystore for Redis](#memorystore-for-redis)
3. [Memorystore for Memcached](#memorystore-for-memcached)
4. [When to Use Memorystore](#when-to-use-memorystore)
5. [Architecture Patterns](#architecture-patterns)
6. [Performance Optimization](#performance-optimization)
7. [High Availability](#high-availability)
8. [Security](#security)
9. [Monitoring](#monitoring)
10. [Best Practices](#best-practices)
11. [Exam Tips](#exam-tips)

---

## Overview

Memorystore is Google Cloud's fully managed in-memory data store service, offering Redis and Memcached.

**What is Memorystore?**
- Fully managed Redis and Memcached
- Sub-millisecond latency
- High availability and automatic failover
- Scalable (up to 300 GB for Redis)
- Compatible with open-source Redis/Memcached

**Use Cases:**
- **Caching:** Database query results, API responses
- **Session Management:** User sessions in web applications
- **Leaderboards:** Gaming, real-time rankings
- **Pub/Sub:** Real-time messaging
- **Rate Limiting:** API throttling

---

## Memorystore for Redis

### What is Redis?

Redis is an in-memory data structure store supporting:
- Strings, lists, sets, sorted sets, hashes
- Pub/Sub messaging
- Transactions
- TTL (Time-To-Live) for keys
- Persistence (optional)

### Instance Tiers

**1. Basic Tier:**
- Single zone
- No replication
- Lower cost
- 99.9% SLA
- **Use for:** Dev/test, caching (acceptable to lose)

**2. Standard Tier:**
- Multi-zone with automatic failover
- Read replicas (optional)
- Higher availability
- 99.9% SLA
- **Use for:** Production, session storage

### Create Redis Instance

**Via Console:**
1. **Memorystore** → **Redis** → **Create Instance**
2. **Instance ID:** `my-redis-instance`
3. **Tier:** Basic or Standard
4. **Region:** `us-central1`
5. **Zone:** `us-central1-a` (Basic) or select zones (Standard)
6. **Capacity:** 1-300 GB
7. **Redis Version:** 6.x or 7.x
8. **Network:** VPC network
9. **Create**

**Via gcloud:**

**Basic Tier:**
```bash
gcloud redis instances create my-redis-instance \
  --size=5 \
  --region=us-central1 \
  --zone=us-central1-a \
  --redis-version=redis_6_x \
  --network=default \
  --tier=basic
```

**Standard Tier (HA):**
```bash
gcloud redis instances create my-redis-ha \
  --size=5 \
  --region=us-central1 \
  --alternative-zone=us-central1-b \
  --redis-version=redis_6_x \
  --network=default \
  --tier=standard
```

**With Read Replicas:**
```bash
gcloud redis instances create my-redis-replicas \
  --size=10 \
  --region=us-central1 \
  --redis-version=redis_7_x \
  --network=default \
  --tier=standard \
  --replica-count=2 \
  --read-replicas-mode=READ_REPLICAS_ENABLED
```

### Connect to Redis

**Get Connection Info:**
```bash
gcloud redis instances describe my-redis-instance --region=us-central1
```

**Output includes:**
- `host`: IP address
- `port`: 6379 (default)

**Connect from Compute Engine:**
```bash
# Install redis-cli
sudo apt-get install redis-tools

# Connect
redis-cli -h REDIS_IP_ADDRESS

# Test connection
127.0.0.1:6379> PING
PONG
```

**Connect from Application (Python):**
```python
import redis

# Create connection
client = redis.Redis(
    host='10.0.0.3',  # Redis instance IP
    port=6379,
    decode_responses=True
)

# Set key
client.set('user:1000', 'John Doe')

# Get key
value = client.get('user:1000')
print(value)  # John Doe

# Set with expiration (TTL)
client.setex('session:abc123', 3600, 'user_data')

# Hash operations
client.hset('user:1000', mapping={'name': 'John', 'email': 'john@example.com'})
user = client.hgetall('user:1000')
print(user)  # {'name': 'John', 'email': 'john@example.com'}
```

**Connect from Node.js:**
```javascript
const redis = require('redis');

const client = redis.createClient({
  socket: {
    host: '10.0.0.3',
    port: 6379
  }
});

await client.connect();

// Set key
await client.set('user:1000', 'John Doe');

// Get key
const value = await client.get('user:1000');
console.log(value);

// Set with expiration
await client.setEx('session:abc123', 3600, 'user_data');
```

### Redis Operations

**Common Commands:**
```redis
# Strings
SET key value
GET key
DEL key
INCR counter
EXPIRE key 3600

# Lists
LPUSH mylist "item1"
RPUSH mylist "item2"
LRANGE mylist 0 -1

# Sets
SADD myset "member1"
SMEMBERS myset
SISMEMBER myset "member1"

# Sorted Sets (Leaderboards)
ZADD leaderboard 100 "player1"
ZADD leaderboard 200 "player2"
ZRANGE leaderboard 0 -1 WITHSCORES
ZREVRANGE leaderboard 0 9  # Top 10

# Hashes
HSET user:1000 name "John" email "john@example.com"
HGET user:1000 name
HGETALL user:1000

# Pub/Sub
SUBSCRIBE channel1
PUBLISH channel1 "message"
```

### Scaling Redis

**Vertical Scaling (Resize):**
```bash
# Increase capacity
gcloud redis instances update my-redis-instance \
  --region=us-central1 \
  --size=10

# Note: May cause brief unavailability (~1 minute)
```

**Read Replicas (Standard Tier):**
```bash
# Add read replicas
gcloud redis instances update my-redis-ha \
  --region=us-central1 \
  --replica-count=3 \
  --read-replicas-mode=READ_REPLICAS_ENABLED
```

**Benefits:**
- Offload read traffic from primary
- Reduce latency (geographically distributed)
- Higher read throughput

### Redis Persistence

**RDB (Redis Database Backup):**
- Point-in-time snapshots
- Automatic backups
- Configurable frequency

**Enable Backups:**
```bash
gcloud redis instances update my-redis-instance \
  --region=us-central1 \
  --persistence-mode=RDB
```

**AOF (Append-Only File):**
- Logs every write operation
- Better durability
- Slightly lower performance

---

## Memorystore for Memcached

### What is Memcached?

Memcached is a simple, distributed memory caching system.

**Characteristics:**
- Simple key-value store
- No data structures (only strings)
- No persistence
- Horizontal scaling
- LRU (Least Recently Used) eviction

**Memcached vs Redis:**

| Feature | Memcached | Redis |
|---------|-----------|-------|
| Data Structures | Strings only | Strings, lists, sets, hashes, etc. |
| Persistence | No | Yes (RDB, AOF) |
| Replication | No | Yes |
| Pub/Sub | No | Yes |
| Transactions | No | Yes |
| Scaling | Horizontal (sharding) | Vertical + read replicas |
| Use Case | Simple caching | Complex caching, sessions, queues |

### Create Memcached Instance

**Via Console:**
1. **Memorystore** → **Memcached** → **Create Instance**
2. **Instance ID:** `my-memcached`
3. **Node count:** 3 (minimum)
4. **Node CPU:** 1-32 vCPUs per node
5. **Node memory:** 1-256 GB per node
6. **Region/Zones:** Select zones
7. **Network:** VPC network
8. **Create**

**Via gcloud:**
```bash
gcloud memcache instances create my-memcached \
  --node-count=3 \
  --node-cpu=1 \
  --node-memory=1GB \
  --region=us-central1 \
  --zones=us-central1-a,us-central1-b,us-central1-c \
  --network=default
```

### Connect to Memcached

**Get Discovery Endpoint:**
```bash
gcloud memcache instances describe my-memcached --region=us-central1
```

**Output:**
- `discoveryEndpoint`: IP:port

**Connect from Python:**
```python
import memcache

# Create client with auto-discovery
client = memcache.Client(
    ['10.0.0.5:11211'],
    server_max_value_length=1024*1024
)

# Set key
client.set('user:1000', 'John Doe', time=3600)

# Get key
value = client.get('user:1000')
print(value)

# Delete key
client.delete('user:1000')
```

**Connect from Node.js:**
```javascript
const Memcached = require('memcached');

const memcached = new Memcached('10.0.0.5:11211');

// Set key
memcached.set('user:1000', 'John Doe', 3600, (err) => {
  if (err) console.error(err);
});

// Get key
memcached.get('user:1000', (err, data) => {
  console.log(data);
});
```

### Scaling Memcached

**Add Nodes:**
```bash
gcloud memcache instances update my-memcached \
  --region=us-central1 \
  --node-count=5
```

**Update Node Resources:**
```bash
gcloud memcache instances apply-parameters my-memcached \
  --region=us-central1 \
  --parameters="max-item-size=2097152"  # 2 MB
```

---

## When to Use Memorystore

### Use Redis When:

**✅ Good Fit:**
- Complex data structures needed (lists, sets, sorted sets)
- Pub/Sub messaging required
- Data persistence required
- Transactions needed
- Session storage (with persistence)
- Leaderboards, real-time analytics
- Rate limiting with precision

**Example: Session Storage**
```python
# Store user session
session_data = {
    'user_id': '12345',
    'username': 'john_doe',
    'login_time': '2024-01-15T10:30:00'
}
redis_client.hset(f'session:{session_id}', mapping=session_data)
redis_client.expire(f'session:{session_id}', 3600)  # 1 hour TTL
```

**Example: Leaderboard**
```python
# Add score
redis_client.zadd('game:leaderboard', {
    'player1': 1500,
    'player2': 1200,
    'player3': 1800
})

# Get top 10
top_players = redis_client.zrevrange('game:leaderboard', 0, 9, withscores=True)
```

### Use Memcached When:

**✅ Good Fit:**
- Simple key-value caching
- Database query result caching
- No persistence needed
- Horizontal scaling required
- Large cache size (multi-node)
- High throughput caching

**Example: Database Query Caching**
```python
import memcache
import mysql.connector

cache = memcache.Client(['10.0.0.5:11211'])
db = mysql.connector.connect(host='...', user='...', password='...', database='...')

def get_user(user_id):
    # Check cache first
    cache_key = f'user:{user_id}'
    user_data = cache.get(cache_key)
    
    if user_data:
        return user_data  # Cache hit
    
    # Cache miss - query database
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    
    # Store in cache (1 hour)
    cache.set(cache_key, user_data, time=3600)
    
    return user_data
```

### Don't Use Memorystore When:

**❌ Not a Good Fit:**
- Primary data store (use Cloud SQL, Firestore instead)
- Complex queries (use BigQuery instead)
- Large object storage (use Cloud Storage instead)
- Small traffic (overhead not worth it)

---

## Architecture Patterns

### Pattern 1: Database Caching

```
Application
    ↓
    ├─→ Memorystore/Redis (Cache Layer)
    │       ↓ (Cache Hit)
    │   Return Data
    │
    ├─→ Cloud SQL (Cache Miss)
        ↓
    Query Database
        ↓
    Update Cache
        ↓
    Return Data
```

**Implementation:**
```python
def get_product(product_id):
    cache_key = f'product:{product_id}'
    
    # Try cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Query database
    product = db.query('SELECT * FROM products WHERE id = ?', product_id)
    
    # Store in cache (5 minutes)
    redis_client.setex(cache_key, 300, json.dumps(product))
    
    return product
```

### Pattern 2: Session Store

```
Load Balancer
    ↓
Application Instances (Stateless)
    ↓
Memorystore/Redis (Centralized Sessions)
```

**Implementation:**
```python
# Flask example
from flask import Flask, session
from flask_session import Session
import redis

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(host='10.0.0.3', port=6379)
Session(app)

@app.route('/login', methods=['POST'])
def login():
    session['user_id'] = '12345'
    session['username'] = 'john_doe'
    return 'Logged in'
```

### Pattern 3: Rate Limiting

```python
def check_rate_limit(user_id, limit=100, window=60):
    """
    Allow 100 requests per minute
    """
    key = f'rate_limit:{user_id}'
    
    # Increment counter
    current = redis_client.incr(key)
    
    if current == 1:
        # First request, set expiration
        redis_client.expire(key, window)
    
    if current > limit:
        return False  # Rate limit exceeded
    
    return True  # OK
```

### Pattern 4: Pub/Sub Messaging

```python
import redis

# Publisher
def send_notification(channel, message):
    redis_client.publish(channel, message)

# Subscriber
def listen_notifications():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('notifications')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Received: {message['data']}")
```

---

## Performance Optimization

### 1. Connection Pooling

**Python:**
```python
from redis import ConnectionPool, Redis

# Create connection pool
pool = ConnectionPool(
    host='10.0.0.3',
    port=6379,
    max_connections=50,
    socket_keepalive=True,
    socket_connect_timeout=5,
    health_check_interval=30
)

# Use pool
redis_client = Redis(connection_pool=pool)
```

**Node.js:**
```javascript
const redis = require('redis');

const client = redis.createClient({
  socket: {
    host: '10.0.0.3',
    port: 6379,
    reconnectStrategy: (retries) => Math.min(retries * 50, 500)
  },
  poolSize: 50
});
```

### 2. Pipeline Operations

**Batch Multiple Commands:**
```python
# Without pipeline (3 round trips)
redis_client.set('key1', 'value1')
redis_client.set('key2', 'value2')
redis_client.set('key3', 'value3')

# With pipeline (1 round trip)
pipe = redis_client.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.set('key3', 'value3')
pipe.execute()
```

### 3. Optimize Key Names

**Use Short, Consistent Names:**
```python
# Bad (long keys waste memory)
redis_client.set('user_profile_information_for_user_id_12345', 'data')

# Good (short, structured)
redis_client.set('u:12345', 'data')
```

### 4. Set Appropriate TTLs

**Prevent Memory Bloat:**
```python
# Always set expiration for cache entries
redis_client.setex('cache:query:123', 300, 'result')  # 5 minutes

# For temporary data
redis_client.setex('temp:token:abc', 3600, 'token_data')  # 1 hour
```

---

## High Availability

### Redis Standard Tier

**Automatic Failover:**
```
Primary (us-central1-a)
    ↓ (Replication)
Replica (us-central1-b)

# If primary fails:
Replica promoted to primary (automatic)
Downtime: < 60 seconds
```

**Read Replicas:**
```
Primary (Read + Write)
    ↓
Replica 1 (Read Only)
    ↓
Replica 2 (Read Only)
```

**Application Pattern:**
```python
import redis

# Primary for writes
primary = redis.Redis(host='10.0.0.3', port=6379)

# Replicas for reads
replica1 = redis.Redis(host='10.0.0.4', port=6379)
replica2 = redis.Redis(host='10.0.0.5', port=6379)

# Write to primary
primary.set('key', 'value')

# Read from replica
value = replica1.get('key')
```

### Monitoring Health

**Check Instance Status:**
```bash
gcloud redis instances describe my-redis-instance \
  --region=us-central1 \
  --format="value(state)"
```

**Cloud Monitoring Metrics:**
- `redis.googleapis.com/stats/connections/total`
- `redis.googleapis.com/stats/cpu_utilization`
- `redis.googleapis.com/stats/memory/usage_ratio`
- `redis.googleapis.com/stats/cache_hit_ratio`

---

## Security

### VPC Networking

**Private IP Only:**
- Memorystore instances only have private IPs
- Must access from same VPC
- Use VPN/Interconnect for on-premises access

**VPC Peering:**
```bash
# Memorystore in VPC A can be accessed from VPC B via peering
gcloud compute networks peerings create peer-vpc-b \
  --network=vpc-a \
  --peer-network=vpc-b \
  --auto-create-routes
```

### IAM Roles

| Role | Permissions |
|------|------------|
| `roles/redis.admin` | Full control |
| `roles/redis.editor` | Create/modify instances |
| `roles/redis.viewer` | View instances |

**Grant Access:**
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=user:developer@example.com \
  --role=roles/redis.editor
```

### Auth (Redis)

**Enable AUTH:**
```bash
gcloud redis instances update my-redis-instance \
  --region=us-central1 \
  --auth-enabled
```

**Connect with AUTH:**
```python
redis_client = redis.Redis(
    host='10.0.0.3',
    port=6379,
    password='YOUR_AUTH_STRING'
)
```

### Encryption

**In-Transit:**
- TLS encryption available
- Enable during instance creation

```bash
gcloud redis instances create my-redis-secure \
  --size=5 \
  --region=us-central1 \
  --tier=standard \
  --transit-encryption-mode=SERVER_AUTHENTICATION
```

**At-Rest:**
- Automatic encryption (Google-managed keys)
- Optional: CMEK (Customer-managed encryption keys)

---

## Monitoring

### Key Metrics

**1. Hit Ratio:**
```
Hit Ratio = Cache Hits / (Cache Hits + Cache Misses)
Target: > 90%
```

**Low hit ratio? → Review caching strategy**

**2. Memory Usage:**
```
Target: < 80% of allocated memory
Alert at: 90%
```

**High memory → Increase size or add eviction policy**

**3. CPU Utilization:**
```
Target: < 70%
Alert at: 90%
```

**4. Connections:**
```
Monitor active connections
Alert on sudden spikes
```

### Create Alerts

```bash
# Alert on high memory usage
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Redis High Memory" \
  --condition-threshold-value=0.9 \
  --condition-threshold-duration=300s \
  --condition-display-name="Memory > 90%"
```

---

## Best Practices

### 1. Right-Size Instances

**Monitor Usage:**
- Start small, scale up
- Monitor memory and CPU
- Add read replicas for read-heavy workloads

### 2. Set Appropriate TTLs

**All Cache Keys Should Expire:**
```python
# Good
redis_client.setex('cache:data', 3600, 'value')

# Bad (memory leak)
redis_client.set('cache:data', 'value')  # Never expires
```

### 3. Handle Cache Failures Gracefully

```python
def get_data_with_fallback(key):
    try:
        # Try cache
        data = redis_client.get(key)
        if data:
            return data
    except redis.ConnectionError:
        # Cache unavailable, go to database
        pass
    
    # Fallback to database
    return query_database(key)
```

### 4. Use Connection Pooling

- Reuse connections
- Set max connection limits
- Enable keepalive

### 5. Monitor and Alert

-Set up Cloud Monitoring alerts
- Monitor hit ratio, memory, CPU
- Alert on anomalies

### 6. Separate Dev and Prod

- Use separate instances for environments
- Basic tier for dev/test
- Standard tier for production

---

## Exam Tips

### ACE Exam Focus

**1. When to Use:**
- **Redis:** Session storage, complex caching, pub/sub
- **Memcached:** Simple caching, large distributed cache

**2. Tiers:**
- **Basic:** Single zone, dev/test
- **Standard:** Multi-zone, production

**3. Basic Commands:**
```bash
# Create Redis instance
gcloud redis instances create NAME --size=SIZE --region=REGION

# List instances
gcloud redis instances list --region=REGION

# Delete instance
gcloud redis instances delete NAME --region=REGION
```

**4. Connectivity:**
- Private IP only
- Must be in same VPC
- VPN/Interconnect for on-premises

### PCA Exam Focus

**1. Architecture Decisions:**

**Use Memorystore When:**
- Sub-millisecond latency needed
- Database query caching
- Session management
- Real-time leaderboards

**Don't Use When:**
- Primary data store
- Complex queries
- Long-term storage

**2. HA Strategy:**
- Standard tier for production
- Read replicas for read-heavy
- Automatic failover

**3. Scaling:**
- **Redis:** Vertical scaling + read replicas
- **Memcached:** Horizontal scaling (add nodes)

**4. Cost Optimization:**
- Basic tier for non-critical
- Right-size memory allocation
- Set appropriate TTLs

### Exam Scenarios

**Scenario:** "Web app needs to store user sessions across multiple instances"
**Solution:** Memorystore for Redis with Standard tier

**Scenario:** "Cache database query results for high-traffic API"
**Solution:** Memorystore for Memcached or Redis

**Scenario:** "Real-time leaderboard for gaming application"
**Solution:** Memorystore for Redis (sorted sets)

**Scenario:** "Reduce Cloud SQL read load"
**Solution:** Implement caching layer with Memorystore

---

## Quick Reference

```bash
# Redis
gcloud redis instances create NAME --size=5 --region=REGION --tier=standard
gcloud redis instances list --region=REGION
gcloud redis instances describe NAME --region=REGION
gcloud redis instances update NAME --region=REGION --size=10

# Memcached
gcloud memcache instances create NAME --node-count=3 --region=REGION
gcloud memcache instances list --region=REGION
gcloud memcache instances describe NAME --region=REGION
```

---

**End of Guide** - Cache like a pro with Memorystore! ⚡
