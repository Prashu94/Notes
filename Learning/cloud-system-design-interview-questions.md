# Cloud & System Design Interview Questions

## Comprehensive Guide for Senior Engineers

---

# Part 1: System Design Fundamentals

## 1. What are the key characteristics of a distributed system? Explain CAP theorem.

**Answer:**

**Distributed System Characteristics:**

1. **Scalability**: Ability to handle growing workload
2. **Reliability**: System continues to function despite failures
3. **Availability**: System is operational and accessible
4. **Efficiency**: Response time and throughput optimization
5. **Manageability**: Easy to operate and maintain

**CAP Theorem:**

CAP theorem states that a distributed system can only guarantee two of the following three properties simultaneously:

```
        Consistency
           /\
          /  \
         /    \
        /      \
       /   CA   \
      /          \
     /____________\
    Availability ---- Partition Tolerance
         AP              CP
```

**1. Consistency (C):**
- All nodes see the same data at the same time
- Every read receives the most recent write
- Example: Banking transactions

**2. Availability (A):**
- Every request receives a response (success or failure)
- System remains operational
- Example: Social media feeds

**3. Partition Tolerance (P):**
- System continues to operate despite network partitions
- Messages between nodes can be lost or delayed
- Essential for distributed systems

**CAP Trade-offs:**

| Type | Description | Examples |
|------|-------------|----------|
| **CP** | Consistent + Partition Tolerant | MongoDB, HBase, Redis (cluster) |
| **AP** | Available + Partition Tolerant | Cassandra, DynamoDB, CouchDB |
| **CA** | Consistent + Available | Traditional RDBMS (single node) |

**Real-World Example:**

```
Scenario: E-commerce inventory system

Option 1: CP (Consistency + Partition Tolerance)
- During network partition, system blocks writes
- Users may see "Service temporarily unavailable"
- Inventory count is always accurate
- Good for: Financial systems, inventory management

Option 2: AP (Availability + Partition Tolerance)
- During network partition, both partitions accept writes
- May lead to overselling (inconsistency)
- Users always get a response
- Good for: Social media, content delivery

Resolution: Use eventual consistency with conflict resolution
- Accept writes in both partitions
- Merge/resolve conflicts when partition heals
- "Last write wins" or "merge vectors"
```

**PACELC Theorem (Extension of CAP):**

```
If Partition (P):
    Choose between Availability (A) and Consistency (C)
Else (E) - Normal operation:
    Choose between Latency (L) and Consistency (C)

Examples:
- DynamoDB: PA/EL (Available during partition, Low latency normally)
- MongoDB: PC/EC (Consistent in both cases)
- Cassandra: PA/EL (Tunable consistency)
```

---

## 2. Explain horizontal vs vertical scaling. When would you use each?

**Answer:**

**Vertical Scaling (Scale Up):**

```
┌─────────────────┐     ┌─────────────────────┐
│    Server       │     │      Server         │
│    4 CPU        │ --> │      16 CPU         │
│    16GB RAM     │     │      64GB RAM       │
│    500GB SSD    │     │      2TB SSD        │
└─────────────────┘     └─────────────────────┘
     Before                   After
```

**Horizontal Scaling (Scale Out):**

```
┌──────────┐            ┌──────────┐ ┌──────────┐
│  Server  │            │  Server  │ │  Server  │
│          │    -->     │          │ │          │
└──────────┘            └──────────┘ └──────────┘
                        ┌──────────┐ ┌──────────┐
                        │  Server  │ │  Server  │
                        │          │ │          │
                        └──────────┘ └──────────┘
   Before                      After
```

**Detailed Comparison:**

| Aspect | Vertical Scaling | Horizontal Scaling |
|--------|-----------------|-------------------|
| **Approach** | Add resources to one machine | Add more machines |
| **Complexity** | Simple | Complex |
| **Downtime** | Usually required | Zero downtime |
| **Cost** | Expensive at scale | Cost-effective |
| **Limit** | Hardware limits | Virtually unlimited |
| **Fault Tolerance** | Single point of failure | High availability |
| **Data Consistency** | Easy | Challenging |
| **Session Management** | Simple | Requires sticky sessions/distributed cache |

**When to Use Vertical Scaling:**

```yaml
Use Cases:
  - Early-stage startups
  - Legacy applications (hard to distribute)
  - Relational databases with complex transactions
  - Real-time gaming servers
  - Applications with strong consistency needs

Example Scenario:
  Problem: Database queries are slow
  Solution: Upgrade to larger instance
    - Before: db.m5.large (2 vCPU, 8GB RAM)
    - After: db.m5.4xlarge (16 vCPU, 64GB RAM)
  
  Benefits:
    - No application changes
    - No data sharding complexity
    - Quick implementation
```

**When to Use Horizontal Scaling:**

```yaml
Use Cases:
  - Web applications with stateless design
  - Microservices architecture
  - Read-heavy workloads
  - Big data processing
  - High availability requirements

Example Scenario:
  Problem: Traffic spike during Black Friday
  Solution: Auto-scale application servers
    
    Auto Scaling Configuration:
      min_instances: 5
      max_instances: 50
      scale_up_threshold: CPU > 70%
      scale_down_threshold: CPU < 30%
      cooldown: 300 seconds
```

**Horizontal Scaling Patterns:**

**1. Stateless Services:**
```
                    ┌─────────────┐
                    │ Load Balancer│
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ↓               ↓               ↓
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Server 1 │    │ Server 2 │    │ Server 3 │
    │(Stateless)│   │(Stateless)│   │(Stateless)│
    └──────────┘    └──────────┘    └──────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ↓
                   ┌──────────────┐
                   │Shared State  │
                   │(Redis/DB)    │
                   └──────────────┘
```

**2. Database Sharding:**
```
                    ┌─────────────┐
                    │ Application │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │ Shard Router │
                    └──────┬──────┘
         ┌─────────────────┼─────────────────┐
         ↓                 ↓                 ↓
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │  Shard 1  │    │  Shard 2  │    │  Shard 3  │
   │ Users A-H │    │ Users I-P │    │ Users Q-Z │
   └───────────┘    └───────────┘    └───────────┘
```

**3. Read Replicas:**
```
                    ┌─────────────┐
                    │   Primary   │
                    │  (Writes)   │
                    └──────┬──────┘
         ┌─────────────────┼─────────────────┐
         ↓                 ↓                 ↓
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │ Replica 1 │    │ Replica 2 │    │ Replica 3 │
   │ (Reads)   │    │ (Reads)   │    │ (Reads)   │
   └───────────┘    └───────────┘    └───────────┘
```

**Hybrid Approach:**
```python
# Best practice: Combine both strategies
scaling_strategy = {
    "web_tier": "horizontal",      # Stateless, easy to scale out
    "application_tier": "horizontal",  # Stateless microservices
    "cache_tier": "horizontal",    # Redis Cluster
    "database_tier": {
        "primary": "vertical",     # Scale up for writes
        "read_replicas": "horizontal"  # Scale out for reads
    }
}
```

---

## 3. Explain different load balancing algorithms and when to use each.

**Answer:**

**Load Balancer Architecture:**

```
                 Internet
                    │
            ┌───────┴───────┐
            │ Load Balancer │
            └───────┬───────┘
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
┌───────┐       ┌───────┐       ┌───────┐
│Server1│       │Server2│       │Server3│
│ (3)   │       │ (2)   │       │ (1)   │
└───────┘       └───────┘       └───────┘
```

**Load Balancing Algorithms:**

**1. Round Robin:**
```
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1 (cycle repeats)

Pros:
  - Simple implementation
  - Even distribution
  
Cons:
  - Ignores server capacity
  - Ignores current load
  
Use When:
  - Servers have equal capacity
  - Requests have similar processing time
```

**2. Weighted Round Robin:**
```
Weights: Server1=5, Server2=3, Server3=2

Distribution over 10 requests:
  Server1: 5 requests (50%)
  Server2: 3 requests (30%)
  Server3: 2 requests (20%)

Use When:
  - Servers have different capacities
  - Mixed hardware environment
```

**3. Least Connections:**
```
Current connections:
  Server1: 10 active connections
  Server2: 5 active connections
  Server3: 8 active connections

Next request → Server2 (least connections)

Use When:
  - Long-lived connections (WebSocket, database)
  - Varying request processing times
```

**4. Weighted Least Connections:**
```
Weights: Server1=3, Server2=2, Server3=1
Connections: Server1=9, Server2=4, Server3=3

Ratio = Connections / Weight
  Server1: 9/3 = 3.0
  Server2: 4/2 = 2.0
  Server3: 3/1 = 3.0

Next request → Server2 (lowest ratio)
```

**5. IP Hash (Sticky Sessions):**
```
hash(client_ip) % num_servers = target_server

Client 192.168.1.100:
  hash("192.168.1.100") % 3 = 1 → Server2

Same client always goes to same server

Use When:
  - Session persistence needed
  - Stateful applications
  - Server-side caching per user
```

**6. Least Response Time:**
```
Response times:
  Server1: 50ms average
  Server2: 30ms average  
  Server3: 45ms average

Next request → Server2 (fastest response)

Use When:
  - Performance-critical applications
  - Heterogeneous server performance
```

**7. Random:**
```
Next request → Random(Server1, Server2, Server3)

Use When:
  - Simple stateless applications
  - Servers have equal capacity
  - Testing/development
```

**8. Resource-Based (Adaptive):**
```
Health metrics:
  Server1: CPU 80%, Memory 70%, OK
  Server2: CPU 40%, Memory 50%, OK
  Server3: CPU 90%, Memory 85%, WARNING

Score calculation:
  Server2 has best score → receives next request

Use When:
  - Dynamic workloads
  - Need optimal resource utilization
```

**Layer 4 vs Layer 7 Load Balancing:**

```
┌────────────────────────────────────────────────────────┐
│                    Layer 7 (Application)               │
│  - HTTP/HTTPS aware                                    │
│  - URL-based routing                                   │
│  - Header inspection                                   │
│  - SSL termination                                     │
│  - Content-based routing                               │
│  Examples: AWS ALB, NGINX, HAProxy                     │
└────────────────────────────────────────────────────────┘
                          │
┌────────────────────────────────────────────────────────┐
│                    Layer 4 (Transport)                 │
│  - TCP/UDP level                                       │
│  - Faster (less processing)                            │
│  - IP and port based routing                           │
│  - No content inspection                               │
│  Examples: AWS NLB, LVS, HAProxy (TCP mode)            │
└────────────────────────────────────────────────────────┘
```

**Layer 7 Routing Example:**

```nginx
# NGINX Configuration
upstream api_servers {
    least_conn;
    server api1.example.com:8080 weight=3;
    server api2.example.com:8080 weight=2;
    server api3.example.com:8080 weight=1;
}

upstream static_servers {
    server static1.example.com:80;
    server static2.example.com:80;
}

server {
    listen 80;
    
    # Route based on URL path
    location /api/ {
        proxy_pass http://api_servers;
    }
    
    location /static/ {
        proxy_pass http://static_servers;
    }
    
    # Route based on header
    location / {
        if ($http_x_mobile = "true") {
            proxy_pass http://mobile_servers;
        }
        proxy_pass http://web_servers;
    }
}
```

**Health Checks:**

```yaml
# AWS ALB Health Check Configuration
health_check:
  protocol: HTTP
  port: 8080
  path: /health
  interval: 30 seconds
  timeout: 5 seconds
  healthy_threshold: 2
  unhealthy_threshold: 3
  matcher: "200-299"
```

---

## 4. What is database sharding? Explain different sharding strategies.

**Answer:**

**What is Sharding?**

Sharding is horizontal partitioning of data across multiple database instances, where each instance holds a subset of the total data.

```
┌─────────────────────────────────────────────────────┐
│              Before Sharding                        │
│  ┌─────────────────────────────────────────────┐   │
│  │           Single Database                     │   │
│  │      Users: 100 million records              │   │
│  │      Orders: 500 million records             │   │
│  │      Products: 10 million records            │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              After Sharding                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │  Shard 1  │  │  Shard 2  │  │  Shard 3  │       │
│  │Users A-H  │  │Users I-P  │  │Users Q-Z  │       │
│  │~33M users │  │~33M users │  │~33M users │       │
│  └───────────┘  └───────────┘  └───────────┘       │
└─────────────────────────────────────────────────────┘
```

**Sharding Strategies:**

**1. Range-Based Sharding:**

```
Shard Key: user_id (numeric)

Shard 1: user_id 1 - 1,000,000
Shard 2: user_id 1,000,001 - 2,000,000
Shard 3: user_id 2,000,001 - 3,000,000

┌─────────────────┐
│  Query Router   │
│  user_id: 1,500,050
└────────┬────────┘
         │ (1M < 1,500,050 < 2M)
         ↓
    ┌─────────┐
    │ Shard 2 │
    └─────────┘

Pros:
  - Simple to implement
  - Range queries efficient
  - Easy to understand

Cons:
  - Hotspots (new users on latest shard)
  - Uneven distribution
  - Rebalancing is complex
```

**2. Hash-Based Sharding:**

```
Shard Key: user_id
Hash Function: MD5 or consistent hashing
Number of Shards: 4

shard_id = hash(user_id) % num_shards

Example:
  user_id = 12345
  hash(12345) = 7829374
  shard_id = 7829374 % 4 = 2 → Shard 2

┌─────────────────┐
│  Query Router   │
│  hash(12345) % 4 = 2
└────────┬────────┘
         ↓
    ┌─────────┐
    │ Shard 2 │
    └─────────┘

Pros:
  - Even distribution
  - No hotspots
  
Cons:
  - Range queries span all shards
  - Adding shards requires rehashing
```

**3. Consistent Hashing:**

```
            0°
            │
     ┌──────┼──────┐
    /       │       \
   /   S1   │   S2   \
270°────────┼────────90°
   \   S4   │   S3   /
    \       │       /
     └──────┼──────┘
            │
           180°

Keys and servers mapped to ring:
  - Key 'user_123' hashes to 45° → Shard 2
  - Key 'user_456' hashes to 200° → Shard 4

Adding a new shard:
  - Only keys between new and next shard move
  - Minimal data movement

Used by: Cassandra, DynamoDB, Redis Cluster
```

**4. Directory-Based Sharding:**

```
┌────────────────────────────────────────┐
│         Shard Lookup Table             │
├──────────────┬─────────────────────────┤
│   user_id    │        shard_id         │
├──────────────┼─────────────────────────┤
│   1-1000     │        shard_1          │
│   1001-5000  │        shard_2          │
│   5001-5500  │        shard_3          │
│   5501-10000 │        shard_1          │
└──────────────┴─────────────────────────┘

Query Flow:
  1. Lookup shard for user_id in directory
  2. Route query to appropriate shard

Pros:
  - Flexible shard assignment
  - Easy rebalancing
  
Cons:
  - Directory becomes bottleneck
  - Additional lookup overhead
  - Single point of failure
```

**5. Geo-Based Sharding:**

```
┌─────────────────────────────────────────────────────┐
│                 Global Application                   │
└─────────────────────────────────────────────────────┘
         │              │              │
         ↓              ↓              ↓
   ┌───────────┐  ┌───────────┐  ┌───────────┐
   │ US Shard  │  │ EU Shard  │  │Asia Shard │
   │ Region:   │  │ Region:   │  │ Region:   │
   │ us-east-1 │  │ eu-west-1 │  │ap-south-1 │
   │ Users: US │  │Users: EU  │  │Users: Asia│
   └───────────┘  └───────────┘  └───────────┘

Routing:
  - User from US → US Shard
  - User from Germany → EU Shard
  - User from India → Asia Shard

Pros:
  - Low latency for users
  - Data residency compliance (GDPR)
  
Cons:
  - Complex for global queries
  - Cross-region transactions
```

**Sharding Challenges:**

**1. Cross-Shard Queries:**
```sql
-- This becomes expensive with sharding
SELECT * FROM orders 
WHERE created_at > '2024-01-01' 
ORDER BY total_amount DESC 
LIMIT 100;

-- Must query all shards and merge results
```

**2. Cross-Shard Joins:**
```sql
-- Avoid this in sharded database
SELECT u.name, o.total 
FROM users u 
JOIN orders o ON u.id = o.user_id;

-- Solutions:
-- 1. Denormalize data
-- 2. Application-level joins
-- 3. Use same shard key for related data
```

**3. Transactions Across Shards:**
```python
# Two-Phase Commit (2PC)
def transfer_money(from_user, to_user, amount):
    # Phase 1: Prepare
    shard1.prepare(f"UPDATE accounts SET balance = balance - {amount} WHERE user_id = {from_user}")
    shard2.prepare(f"UPDATE accounts SET balance = balance + {amount} WHERE user_id = {to_user}")
    
    # Phase 2: Commit
    if shard1.can_commit() and shard2.can_commit():
        shard1.commit()
        shard2.commit()
    else:
        shard1.rollback()
        shard2.rollback()
```

**Shard Key Selection:**

```yaml
Good Shard Keys:
  - High cardinality (many unique values)
  - Even distribution
  - Frequently used in queries
  - Doesn't change often

Examples:
  - user_id: Good for user-centric apps
  - tenant_id: Good for multi-tenant SaaS
  - timestamp: Good for time-series (with care)
  
Bad Shard Keys:
  - Low cardinality (status, country)
  - Monotonically increasing (auto-increment ID)
  - Frequently updated fields
```

---

## 5. Explain caching strategies and cache invalidation approaches.

**Answer:**

**Caching Architecture:**

```
┌─────────────────────────────────────────────────────┐
│                  Client Request                      │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────┐
│              CDN Cache (Edge)                        │
│         Static assets, API responses                 │
└─────────────────────────────────────────────────────┘
                         │ Cache Miss
                         ↓
┌─────────────────────────────────────────────────────┐
│           Application Cache (Local)                  │
│         In-memory, per-instance                      │
└─────────────────────────────────────────────────────┘
                         │ Cache Miss
                         ↓
┌─────────────────────────────────────────────────────┐
│         Distributed Cache (Redis/Memcached)          │
│         Shared across instances                      │
└─────────────────────────────────────────────────────┘
                         │ Cache Miss
                         ↓
┌─────────────────────────────────────────────────────┐
│                   Database                           │
└─────────────────────────────────────────────────────┘
```

**Caching Strategies:**

**1. Cache-Aside (Lazy Loading):**

```python
def get_user(user_id):
    # 1. Check cache first
    user = cache.get(f"user:{user_id}")
    
    if user is None:
        # 2. Cache miss - load from database
        user = database.query(f"SELECT * FROM users WHERE id = {user_id}")
        
        # 3. Store in cache for future requests
        if user:
            cache.set(f"user:{user_id}", user, ttl=3600)
    
    return user

def update_user(user_id, data):
    # Update database
    database.update(f"UPDATE users SET ... WHERE id = {user_id}")
    
    # Invalidate cache
    cache.delete(f"user:{user_id}")
```

```
Pros:
  - Only requested data is cached
  - Cache failures don't break the app
  - Good for read-heavy workloads

Cons:
  - Initial request is slow (cache miss)
  - Stale data possible (database updated externally)
```

**2. Read-Through Cache:**

```python
# Cache handles database interaction
class ReadThroughCache:
    def get(self, key):
        value = self.cache.get(key)
        
        if value is None:
            # Cache loads from database
            value = self.database.get(key)
            self.cache.set(key, value)
        
        return value

# Application code is simpler
user = cache.get(f"user:{user_id}")
```

```
Pros:
  - Application code is simpler
  - Cache manages data loading

Cons:
  - Tighter coupling with cache library
  - Less control over database queries
```

**3. Write-Through Cache:**

```python
def update_user(user_id, data):
    # Write to cache (cache writes to database)
    cache.set(f"user:{user_id}", data)  # Synchronously writes to DB

# Cache implementation
class WriteThroughCache:
    def set(self, key, value):
        # Write to database first
        self.database.update(key, value)
        # Then update cache
        self.cache.set(key, value)
```

```
Pros:
  - Cache always consistent with database
  - No stale data

Cons:
  - Higher write latency
  - All writes go through cache
```

**4. Write-Behind (Write-Back) Cache:**

```python
class WriteBehindCache:
    def __init__(self):
        self.write_queue = Queue()
        self.start_background_writer()
    
    def set(self, key, value):
        # Write to cache immediately
        self.cache.set(key, value)
        # Queue for async database write
        self.write_queue.put((key, value))
    
    def background_writer(self):
        while True:
            batch = []
            # Collect writes for batching
            while len(batch) < 100 and not self.write_queue.empty():
                batch.append(self.write_queue.get())
            
            if batch:
                self.database.batch_write(batch)
            
            time.sleep(1)
```

```
Pros:
  - Very low write latency
  - Batching improves database performance

Cons:
  - Risk of data loss (cache failure before DB write)
  - Complexity in failure handling
```

**5. Refresh-Ahead Cache:**

```python
class RefreshAheadCache:
    def get(self, key):
        value, expiry = self.cache.get_with_expiry(key)
        
        # If close to expiry, refresh asynchronously
        if expiry and (expiry - time.now()) < REFRESH_THRESHOLD:
            self.async_refresh(key)
        
        return value
    
    async def async_refresh(self, key):
        new_value = self.database.get(key)
        self.cache.set(key, new_value, ttl=3600)
```

```
Pros:
  - Reduces cache miss latency
  - Proactive refresh

Cons:
  - May refresh data that won't be accessed
  - More complex implementation
```

**Cache Invalidation Strategies:**

**1. Time-To-Live (TTL):**
```python
# Simple expiration
cache.set("user:123", user_data, ttl=3600)  # Expires in 1 hour

# Different TTLs for different data types
TTL_CONFIG = {
    "user_profile": 3600,      # 1 hour
    "product_catalog": 86400,  # 24 hours
    "session": 1800,           # 30 minutes
    "real_time_data": 60       # 1 minute
}
```

**2. Event-Based Invalidation:**
```python
# Publish event when data changes
def update_user(user_id, data):
    database.update_user(user_id, data)
    event_bus.publish("user_updated", {"user_id": user_id})

# Subscribe to events and invalidate
@event_handler("user_updated")
def handle_user_update(event):
    cache.delete(f"user:{event['user_id']}")
    cache.delete(f"user_orders:{event['user_id']}")
    cache.delete_pattern(f"user_*:{event['user_id']}")
```

**3. Version-Based Invalidation:**
```python
# Store version with cached data
def get_user(user_id):
    cached = cache.get(f"user:{user_id}")
    current_version = cache.get(f"user_version:{user_id}")
    
    if cached and cached['version'] == current_version:
        return cached['data']
    
    user = database.get_user(user_id)
    cache.set(f"user:{user_id}", {
        'data': user,
        'version': current_version
    })
    return user

def update_user(user_id, data):
    database.update_user(user_id, data)
    cache.incr(f"user_version:{user_id}")  # Increment version
```

**4. Tag-Based Invalidation:**
```python
# Tag related cache entries
cache.set("product:123", product_data, tags=["category:electronics", "brand:apple"])
cache.set("product:456", product_data, tags=["category:electronics", "brand:samsung"])

# Invalidate all electronics products
cache.invalidate_by_tag("category:electronics")
```

**Cache Patterns for Specific Scenarios:**

**1. Cache Stampede Prevention:**
```python
import threading

locks = {}

def get_with_lock(key):
    value = cache.get(key)
    if value is not None:
        return value
    
    # Acquire lock to prevent stampede
    lock = locks.setdefault(key, threading.Lock())
    
    with lock:
        # Double-check after acquiring lock
        value = cache.get(key)
        if value is not None:
            return value
        
        value = database.get(key)
        cache.set(key, value, ttl=3600)
        return value
```

**2. Probabilistic Early Expiration:**
```python
import random

def get_with_early_expiration(key):
    value, ttl_remaining = cache.get_with_ttl(key)
    
    if value is None:
        return fetch_and_cache(key)
    
    # Probabilistic early refresh
    # As TTL decreases, probability of refresh increases
    if random.random() < (1 - ttl_remaining / ORIGINAL_TTL):
        async_refresh(key)
    
    return value
```

---

## 6. Design a URL shortening service like bit.ly.

**Answer:**

**Functional Requirements:**
- Generate short URL from long URL
- Redirect short URL to original URL
- Custom short URLs (optional)
- Analytics (click count, location)
- URL expiration

**Non-Functional Requirements:**
- High availability (99.99%)
- Low latency (<100ms redirect)
- Highly scalable (billions of URLs)
- Secure (no enumeration attacks)

**Capacity Estimation:**

```
Assumptions:
  - 500M new URLs per month
  - Read:Write ratio = 100:1
  - URL stored for 5 years
  
Write QPS:
  - 500M / (30 days * 24 hours * 3600 sec) ≈ 200 URLs/sec

Read QPS:
  - 200 * 100 = 20,000 redirects/sec

Storage (5 years):
  - URLs: 500M * 12 months * 5 years = 30 billion URLs
  - Each URL entry: ~500 bytes
  - Total: 30B * 500 bytes = 15 TB

Bandwidth:
  - Write: 200 * 500 bytes = 100 KB/sec
  - Read: 20,000 * 500 bytes = 10 MB/sec
```

**High-Level Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     CDN / DNS                               │
│              (Geographic distribution)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer                            │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   API Server 1   │ │   API Server 2   │ │   API Server 3   │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ↓                               ↓
┌─────────────────────────┐    ┌─────────────────────────┐
│      Redis Cache        │    │    Key Generation       │
│  (Hot URLs, counters)   │    │      Service            │
└─────────────────────────┘    └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Database Cluster                         │
│        (Sharded by short URL hash)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Analytics Pipeline                        │
│           (Kafka → Spark → Data Warehouse)                  │
└─────────────────────────────────────────────────────────────┘
```

**URL Encoding Algorithm:**

**Option 1: Base62 Encoding**
```python
import string

BASE62_CHARS = string.ascii_letters + string.digits  # a-z, A-Z, 0-9

def encode_base62(num):
    """Convert number to base62 string"""
    if num == 0:
        return BASE62_CHARS[0]
    
    result = []
    while num > 0:
        result.append(BASE62_CHARS[num % 62])
        num //= 62
    
    return ''.join(reversed(result))

def decode_base62(s):
    """Convert base62 string to number"""
    num = 0
    for char in s:
        num = num * 62 + BASE62_CHARS.index(char)
    return num

# 7 characters can represent 62^7 = 3.5 trillion URLs
# Examples:
#   1 → "b"
#   1000000 → "4c92"
#   1000000000 → "15FTGf"
```

**Option 2: MD5 Hash (First N characters)**
```python
import hashlib

def generate_short_url(long_url):
    # Create MD5 hash
    hash_object = hashlib.md5(long_url.encode())
    hash_hex = hash_object.hexdigest()
    
    # Take first 7 characters (base16 → base62)
    hash_int = int(hash_hex[:12], 16)
    return encode_base62(hash_int)[:7]

# Problem: Collisions
# Solution: Check for collision and regenerate
```

**Option 3: Pre-generated Keys (Recommended)**
```python
class KeyGenerationService:
    def __init__(self):
        self.used_keys = set()
        self.available_keys = Queue()
        self.generate_keys_batch()
    
    def generate_keys_batch(self, batch_size=10000):
        """Pre-generate random keys"""
        for _ in range(batch_size):
            while True:
                key = self.generate_random_key(7)
                if key not in self.used_keys:
                    self.available_keys.put(key)
                    self.used_keys.add(key)
                    break
    
    def get_key(self):
        """Get a unique key"""
        if self.available_keys.qsize() < 1000:
            # Async refill
            self.async_generate_keys_batch()
        
        return self.available_keys.get()
    
    @staticmethod
    def generate_random_key(length):
        return ''.join(random.choices(BASE62_CHARS, k=length))
```

**Database Schema:**

```sql
-- Main URL table (sharded by short_url hash)
CREATE TABLE urls (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_url VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    click_count BIGINT DEFAULT 0,
    INDEX idx_short_url (short_url),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Analytics table (time-series optimized)
CREATE TABLE url_analytics (
    id BIGINT PRIMARY KEY,
    short_url VARCHAR(10) NOT NULL,
    clicked_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer TEXT,
    country VARCHAR(2),
    city VARCHAR(100),
    device_type VARCHAR(20),
    INDEX idx_short_url_time (short_url, clicked_at)
) PARTITION BY RANGE (UNIX_TIMESTAMP(clicked_at));
```

**API Design:**

```yaml
# Create Short URL
POST /api/v1/shorten
Request:
  {
    "long_url": "https://example.com/very/long/path",
    "custom_alias": "my-link",  # Optional
    "expires_at": "2025-12-31"  # Optional
  }
Response:
  {
    "short_url": "https://bit.ly/abc123",
    "long_url": "https://example.com/very/long/path",
    "expires_at": "2025-12-31",
    "created_at": "2024-01-15T10:30:00Z"
  }

# Redirect (GET)
GET /{short_url}
Response: 301 Redirect to long_url
Headers:
  Location: https://example.com/very/long/path

# Get Analytics
GET /api/v1/analytics/{short_url}
Response:
  {
    "short_url": "abc123",
    "total_clicks": 15234,
    "clicks_by_day": [...],
    "clicks_by_country": {...},
    "clicks_by_device": {...}
  }
```

**Redirect Flow:**

```python
async def redirect(short_url: str):
    # 1. Check cache first
    long_url = await cache.get(f"url:{short_url}")
    
    if not long_url:
        # 2. Query database
        url_record = await db.get_url(short_url)
        
        if not url_record:
            raise HTTPException(404, "URL not found")
        
        if url_record.expires_at and url_record.expires_at < datetime.now():
            raise HTTPException(410, "URL expired")
        
        long_url = url_record.long_url
        
        # 3. Cache the result
        await cache.set(f"url:{short_url}", long_url, ttl=86400)
    
    # 4. Async analytics logging
    asyncio.create_task(log_analytics(short_url, request))
    
    # 5. Return redirect
    return RedirectResponse(url=long_url, status_code=301)
```

**Scaling Considerations:**

```yaml
Database Sharding:
  Strategy: Hash-based on short_url
  Shards: 16 (can expand)
  Routing: short_url[0:2] determines shard

Caching:
  L1: Local cache (Caffeine) - 10K entries per server
  L2: Redis Cluster - 100M entries
  TTL: 24 hours for active URLs
  
Rate Limiting:
  Anonymous: 10 URLs/hour
  Authenticated: 100 URLs/hour
  Premium: 1000 URLs/hour

Geographical Distribution:
  - DNS-based routing to nearest region
  - Each region has read replicas
  - Writes go to primary region
```

---

## 7. Design a distributed message queue like Kafka.

**Answer:**

**Requirements:**

**Functional:**
- Publish messages to topics
- Subscribe to topics
- Message persistence
- Message ordering (per partition)
- Consumer groups
- Message replay

**Non-Functional:**
- High throughput (millions msgs/sec)
- Low latency (<10ms)
- Durability (no message loss)
- Horizontal scalability
- Fault tolerance

**High-Level Architecture:**

```
┌────────────────────────────────────────────────────────────────────┐
│                         Producers                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │Producer 1 │  │Producer 2 │  │Producer 3 │  │Producer N │       │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘       │
└────────┼──────────────┼──────────────┼──────────────┼──────────────┘
         └──────────────┴──────────────┴──────────────┘
                                │
                                ↓
┌────────────────────────────────────────────────────────────────────┐
│                      Broker Cluster                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Topic: orders                             │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐               │   │
│  │  │Partition 0│  │Partition 1│  │Partition 2│               │   │
│  │  │ Leader:B1 │  │ Leader:B2 │  │ Leader:B3 │               │   │
│  │  │ Replica:B2│  │ Replica:B3│  │ Replica:B1│               │   │
│  │  │ Replica:B3│  │ Replica:B1│  │ Replica:B2│               │   │
│  │  └───────────┘  └───────────┘  └───────────┘               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                   │
│  │  Broker 1  │  │  Broker 2  │  │  Broker 3  │                   │
│  └────────────┘  └────────────┘  └────────────┘                   │
└────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│                     Consumer Groups                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐         │
│  │   Consumer Group A      │  │   Consumer Group B      │         │
│  │  ┌────────┐ ┌────────┐  │  │  ┌────────┐ ┌────────┐  │         │
│  │  │ C1(P0) │ │ C2(P1) │  │  │  │ C1(all)│ │        │  │         │
│  │  │        │ │ C3(P2) │  │  │  │        │ │        │  │         │
│  │  └────────┘ └────────┘  │  │  └────────┘ └────────┘  │         │
│  └─────────────────────────┘  └─────────────────────────┘         │
└────────────────────────────────────────────────────────────────────┘
```

**Core Components:**

**1. Topic & Partition:**

```
Topic: "orders"
  │
  ├── Partition 0: [msg0, msg3, msg6, msg9, ...]
  │                 └─ Offset: 0, 1, 2, 3, ...
  │
  ├── Partition 1: [msg1, msg4, msg7, msg10, ...]
  │                 └─ Offset: 0, 1, 2, 3, ...
  │
  └── Partition 2: [msg2, msg5, msg8, msg11, ...]
                    └─ Offset: 0, 1, 2, 3, ...

Partitioning Strategy:
  - Key-based: hash(key) % num_partitions
  - Round-robin: Distribute evenly
  - Custom: User-defined logic
```

**2. Message Storage (Append-Only Log):**

```
Partition Storage Structure:
/data/topics/orders/partition-0/
  ├── 00000000000000000000.log   # Segment file (0-1000)
  ├── 00000000000000000000.index # Offset index
  ├── 00000000000000001000.log   # Segment file (1000-2000)
  ├── 00000000000000001000.index
  └── ...

Message Format:
┌────────────────────────────────────────────────────┐
│ Offset (8 bytes) │ Size (4 bytes) │ CRC (4 bytes)  │
├────────────────────────────────────────────────────┤
│ Timestamp (8 bytes) │ Key Length │ Key (variable)  │
├────────────────────────────────────────────────────┤
│ Value Length │ Value (variable) │ Headers          │
└────────────────────────────────────────────────────┘
```

**3. Broker Implementation:**

```python
class Broker:
    def __init__(self, broker_id):
        self.broker_id = broker_id
        self.partitions = {}  # topic -> partition -> log
        self.zookeeper = ZookeeperClient()
        
    def produce(self, topic, partition, messages):
        """Append messages to partition log"""
        log = self.get_partition_log(topic, partition)
        
        for message in messages:
            offset = log.append(message)
            
            # Replicate to followers
            if self.is_leader(topic, partition):
                self.replicate_to_followers(topic, partition, message)
        
        return offset
    
    def consume(self, topic, partition, offset, max_bytes):
        """Read messages from offset"""
        log = self.get_partition_log(topic, partition)
        return log.read(offset, max_bytes)
    
    def replicate_to_followers(self, topic, partition, message):
        """Sync replication to follower brokers"""
        followers = self.get_followers(topic, partition)
        
        acks = []
        for follower in followers:
            try:
                follower.append(topic, partition, message)
                acks.append(follower.broker_id)
            except Exception as e:
                log.error(f"Replication failed to {follower.broker_id}")
        
        return acks
```

**4. Producer:**

```python
class Producer:
    def __init__(self, bootstrap_servers):
        self.metadata = MetadataCache(bootstrap_servers)
        self.batch_buffer = {}
        self.batch_size = 16384
        self.linger_ms = 5
        
    def send(self, topic, key, value, callback=None):
        """Send message to topic"""
        # 1. Determine partition
        partition = self.partition_for(topic, key)
        
        # 2. Serialize message
        message = Message(key=key, value=value, timestamp=time.time())
        
        # 3. Add to batch buffer
        batch_key = (topic, partition)
        if batch_key not in self.batch_buffer:
            self.batch_buffer[batch_key] = Batch()
        
        self.batch_buffer[batch_key].add(message, callback)
        
        # 4. Send if batch is full
        if self.batch_buffer[batch_key].size() >= self.batch_size:
            self.flush_batch(batch_key)
    
    def partition_for(self, topic, key):
        """Determine partition for message"""
        if key is None:
            # Round-robin for null keys
            return self.round_robin_counter.next() % self.num_partitions(topic)
        else:
            # Hash-based for keyed messages
            return hash(key) % self.num_partitions(topic)
    
    def flush_batch(self, batch_key):
        """Send batch to broker"""
        topic, partition = batch_key
        leader = self.metadata.get_leader(topic, partition)
        
        batch = self.batch_buffer.pop(batch_key)
        
        try:
            response = leader.produce(topic, partition, batch.messages)
            batch.complete(response)
        except Exception as e:
            batch.fail(e)
```

**5. Consumer & Consumer Groups:**

```python
class Consumer:
    def __init__(self, group_id, topics):
        self.group_id = group_id
        self.topics = topics
        self.coordinator = self.find_coordinator()
        self.assignments = {}  # topic-partition -> offset
        
        # Join consumer group
        self.join_group()
    
    def join_group(self):
        """Join consumer group and get partition assignments"""
        # 1. Send JoinGroup request
        response = self.coordinator.join_group(
            group_id=self.group_id,
            member_id=self.member_id,
            protocol_type="consumer",
            protocols=self.supported_protocols
        )
        
        # 2. If elected as leader, assign partitions
        if response.leader == self.member_id:
            assignments = self.assign_partitions(response.members)
            self.coordinator.sync_group(assignments)
        
        # 3. Get my assignments
        self.assignments = self.coordinator.sync_group()
    
    def poll(self, timeout_ms):
        """Fetch messages from assigned partitions"""
        messages = []
        
        for (topic, partition), offset in self.assignments.items():
            leader = self.metadata.get_leader(topic, partition)
            
            batch = leader.fetch(
                topic=topic,
                partition=partition,
                offset=offset,
                max_bytes=1048576
            )
            
            messages.extend(batch.messages)
            self.assignments[(topic, partition)] = batch.last_offset + 1
        
        return messages
    
    def commit(self):
        """Commit current offsets"""
        self.coordinator.commit_offsets(self.group_id, self.assignments)


class PartitionAssignor:
    """Assign partitions to consumers in group"""
    
    @staticmethod
    def range_assign(topics, consumers):
        """Range assignment strategy"""
        assignments = {c: [] for c in consumers}
        
        for topic in topics:
            partitions = get_partitions(topic)
            num_partitions = len(partitions)
            num_consumers = len(consumers)
            
            partitions_per_consumer = num_partitions // num_consumers
            extra = num_partitions % num_consumers
            
            partition_idx = 0
            for i, consumer in enumerate(consumers):
                num_assigned = partitions_per_consumer + (1 if i < extra else 0)
                for j in range(num_assigned):
                    assignments[consumer].append((topic, partition_idx))
                    partition_idx += 1
        
        return assignments
```

**6. Replication & Fault Tolerance:**

```python
class ReplicationManager:
    def __init__(self, broker):
        self.broker = broker
        self.isr = {}  # In-Sync Replicas per partition
        
    def handle_produce(self, topic, partition, messages, acks):
        """Handle produce with different ack levels"""
        
        if acks == 0:
            # Fire and forget
            self.append_local(topic, partition, messages)
            return
        
        if acks == 1:
            # Wait for leader ack only
            self.append_local(topic, partition, messages)
            return {"offset": offset}
        
        if acks == -1:  # all
            # Wait for all ISR acks
            self.append_local(topic, partition, messages)
            self.wait_for_isr_acks(topic, partition)
            return {"offset": offset}
    
    def update_isr(self, topic, partition):
        """Update in-sync replica set"""
        replicas = self.get_replicas(topic, partition)
        leader_leo = self.get_leo(topic, partition)  # Log End Offset
        
        new_isr = []
        for replica in replicas:
            replica_leo = self.get_replica_leo(replica, topic, partition)
            lag = leader_leo - replica_leo
            
            if lag <= MAX_LAG_MESSAGES and self.is_alive(replica):
                new_isr.append(replica)
            else:
                self.mark_out_of_sync(replica, topic, partition)
        
        self.isr[(topic, partition)] = new_isr
```

**7. Zookeeper Coordination:**

```
ZooKeeper Structure:
/brokers
  /ids
    /1  -> {"host": "broker1.example.com", "port": 9092}
    /2  -> {"host": "broker2.example.com", "port": 9092}
  /topics
    /orders
      /partitions
        /0
          /state -> {"leader": 1, "isr": [1, 2, 3]}
          /leader_epoch -> 5
        /1
          /state -> {"leader": 2, "isr": [2, 3, 1]}
/consumers
  /group-1
    /ids
    /owners
    /offsets
/controller -> {"broker_id": 1, "timestamp": 1234567890}
```

**Message Delivery Semantics:**

```yaml
At-Most-Once:
  Producer: acks=0
  Consumer: Commit before processing
  Risk: Message loss
  Use: Metrics, logs

At-Least-Once:
  Producer: acks=1 or acks=all, retries enabled
  Consumer: Commit after processing
  Risk: Duplicate messages
  Use: Most applications

Exactly-Once:
  Producer: Idempotent producer + transactions
  Consumer: Transactional consumer
  Mechanism: Producer ID + Sequence Number
  Use: Financial transactions, critical data
```

**Exactly-Once Implementation:**

```python
class IdempotentProducer:
    def __init__(self):
        self.producer_id = self.get_producer_id()
        self.sequence_numbers = {}  # partition -> sequence
        
    def send(self, topic, partition, message):
        seq = self.sequence_numbers.get(partition, 0)
        
        message.producer_id = self.producer_id
        message.sequence = seq
        
        response = self.broker.produce(topic, partition, message)
        
        if response.success:
            self.sequence_numbers[partition] = seq + 1
        
        return response

# Broker deduplication
class BrokerDeduplication:
    def __init__(self):
        self.producer_states = {}  # producer_id -> {partition: last_seq}
    
    def is_duplicate(self, producer_id, partition, sequence):
        state = self.producer_states.get(producer_id, {})
        last_seq = state.get(partition, -1)
        
        if sequence <= last_seq:
            return True  # Duplicate
        
        if sequence > last_seq + 1:
            raise OutOfOrderException()
        
        state[partition] = sequence
        self.producer_states[producer_id] = state
        return False
```

---

# Part 2: Cloud Architecture

## 8. What are the different types of cloud service models? Explain IaaS, PaaS, and SaaS.

**Answer:**

**Cloud Service Models Comparison:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cloud Service Models                         │
├─────────────────┬──────────────────┬───────────────┬────────────┤
│   On-Premises   │      IaaS        │     PaaS      │    SaaS    │
├─────────────────┼──────────────────┼───────────────┼────────────┤
│  Applications   │  Applications    │ Applications  │ ██████████ │
│  Data           │  Data            │ Data          │ ██████████ │
│  Runtime        │  Runtime         │ ██████████████│ ██████████ │
│  Middleware     │  Middleware      │ ██████████████│ ██████████ │
│  O/S            │  O/S             │ ██████████████│ ██████████ │
│  Virtualization │  ████████████████│ ██████████████│ ██████████ │
│  Servers        │  ████████████████│ ██████████████│ ██████████ │
│  Storage        │  ████████████████│ ██████████████│ ██████████ │
│  Networking     │  ████████████████│ ██████████████│ ██████████ │
├─────────────────┼──────────────────┼───────────────┼────────────┤
│  You Manage     │  You Manage      │  You Manage   │  Provider  │
│  Everything     │  Apps, Data,     │  Apps, Data   │  Manages   │
│                 │  Runtime, MW, OS │               │  Everything│
└─────────────────┴──────────────────┴───────────────┴────────────┘
   ████ = Managed by Cloud Provider
```

**1. Infrastructure as a Service (IaaS):**

```yaml
Definition:
  Provides virtualized computing resources over the internet

You Manage:
  - Applications
  - Data
  - Runtime
  - Middleware
  - Operating System

Provider Manages:
  - Virtualization
  - Servers
  - Storage
  - Networking

Examples:
  AWS: EC2, EBS, VPC
  Azure: Virtual Machines, Managed Disks
  GCP: Compute Engine, Persistent Disk

Use Cases:
  - Full control over infrastructure needed
  - Lift-and-shift migrations
  - Development and testing environments
  - High-performance computing
  - Big data analysis

Pricing Model:
  - Pay per hour/second of usage
  - Pay for storage consumed
  - Pay for data transfer
```

**IaaS Example - AWS:**

```python
# Terraform - Provision EC2 Instance
resource "aws_instance" "web_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  
  vpc_security_group_ids = [aws_security_group.web.id]
  subnet_id              = aws_subnet.public.id
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              EOF
  
  tags = {
    Name = "WebServer"
  }
}

resource "aws_ebs_volume" "data" {
  availability_zone = "us-east-1a"
  size              = 100
  type              = "gp3"
}
```

**2. Platform as a Service (PaaS):**

```yaml
Definition:
  Provides platform for developing, running, and managing applications
  without dealing with infrastructure

You Manage:
  - Applications
  - Data

Provider Manages:
  - Runtime
  - Middleware
  - Operating System
  - Virtualization
  - Servers
  - Storage
  - Networking

Examples:
  AWS: Elastic Beanstalk, Lambda, ECS/EKS
  Azure: App Service, Azure Functions, AKS
  GCP: App Engine, Cloud Run, GKE
  Others: Heroku, Vercel, Netlify

Use Cases:
  - Rapid application development
  - API development and deployment
  - Microservices architecture
  - CI/CD pipelines
  - Serverless applications

Pricing Model:
  - Pay per request/execution
  - Pay for compute time
  - Often includes free tier
```

**PaaS Example - AWS Lambda:**

```python
# serverless.yml - Deploy Lambda function
service: order-processor

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  memorySize: 256
  timeout: 30

functions:
  processOrder:
    handler: handler.process_order
    events:
      - http:
          path: /orders
          method: post
      - sqs:
          arn: arn:aws:sqs:us-east-1:123456789:orders-queue

# handler.py
import json

def process_order(event, context):
    body = json.loads(event['body'])
    order_id = body['order_id']
    
    # Process order logic
    result = process(order_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'order_id': order_id, 'status': 'processed'})
    }
```

**3. Software as a Service (SaaS):**

```yaml
Definition:
  Complete software application delivered over the internet

You Manage:
  - Just use the software
  - Configure settings
  - Manage users and data

Provider Manages:
  - Everything (infrastructure to application)

Examples:
  Productivity: Google Workspace, Microsoft 365
  CRM: Salesforce, HubSpot
  Communication: Slack, Zoom
  Analytics: Google Analytics, Mixpanel
  Dev Tools: GitHub, Jira, Datadog

Use Cases:
  - Email and collaboration
  - Customer relationship management
  - Project management
  - Accounting and HR systems
  - Business intelligence

Pricing Model:
  - Per user/month subscription
  - Tiered plans (Free, Pro, Enterprise)
  - Usage-based for some features
```

**Comparison Summary:**

| Aspect | IaaS | PaaS | SaaS |
|--------|------|------|------|
| **Control** | High | Medium | Low |
| **Flexibility** | High | Medium | Low |
| **Maintenance** | High | Low | None |
| **Cost** | Variable | Variable | Predictable |
| **Expertise Needed** | High | Medium | Low |
| **Time to Market** | Slow | Fast | Immediate |
| **Scalability** | Manual/Auto | Automatic | Automatic |
| **Customization** | Full | Limited | Minimal |

**Choosing the Right Model:**

```
                 ┌─────────────────────────────────────┐
                 │    What do you need?                │
                 └─────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ↓                       ↓                       ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Full control    │    │ Focus on code   │    │ Ready-to-use    │
│ over infra?     │    │ not infra?      │    │ software?       │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         ↓                      ↓                      ↓
    ┌─────────┐            ┌─────────┐            ┌─────────┐
    │  IaaS   │            │  PaaS   │            │  SaaS   │
    └─────────┘            └─────────┘            └─────────┘
```

---

## 9. Explain different cloud deployment models: Public, Private, Hybrid, and Multi-Cloud.

**Answer:**

**Cloud Deployment Models:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Public Cloud                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Resources shared among multiple organizations           │   │
│  │  Owned and operated by cloud provider                    │   │
│  │  Examples: AWS, Azure, GCP                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Private Cloud                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Dedicated resources for single organization             │   │
│  │  On-premises or hosted by provider                       │   │
│  │  Examples: VMware, OpenStack, Azure Stack                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Hybrid Cloud                                  │
│  ┌───────────────────┐    ┌────────────────────────────────┐   │
│  │   Private Cloud   │<-->│        Public Cloud            │   │
│  │   (On-premises)   │    │        (AWS/Azure/GCP)         │   │
│  └───────────────────┘    └────────────────────────────────┘   │
│  Workloads can move between private and public                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Cloud                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │    AWS     │  │   Azure    │  │    GCP     │                │
│  │            │  │            │  │            │                │
│  └────────────┘  └────────────┘  └────────────┘                │
│  Using multiple cloud providers simultaneously                   │
└─────────────────────────────────────────────────────────────────┘
```

**Detailed Comparison:**

| Aspect | Public | Private | Hybrid | Multi-Cloud |
|--------|--------|---------|--------|-------------|
| **Ownership** | Provider | Organization | Mixed | Multiple Providers |
| **Cost** | Pay-as-you-go | High upfront | Medium | Variable |
| **Scalability** | Virtually unlimited | Limited | Flexible | Highly flexible |
| **Security** | Shared responsibility | Full control | Mixed | Complex |
| **Compliance** | Provider controls | Full control | Flexible | Complex |
| **Performance** | Variable | Consistent | Mixed | Variable |
| **Management** | Provider | In-house | Mixed | Complex |

**1. Public Cloud:**

```yaml
Advantages:
  - No upfront infrastructure costs
  - Instant scalability
  - Global availability
  - Latest technology access
  - Reduced management overhead

Disadvantages:
  - Less control over infrastructure
  - Potential compliance issues
  - Vendor lock-in risk
  - Variable costs can surprise

Best For:
  - Startups and small businesses
  - Variable workloads
  - Development and testing
  - Web applications
  - Big data analytics

Example Architecture:
  ┌──────────────────────────────────────┐
  │            AWS Region                │
  │  ┌──────────────────────────────┐   │
  │  │      VPC (10.0.0.0/16)       │   │
  │  │  ┌─────────┐  ┌─────────┐   │   │
  │  │  │Public   │  │Private  │   │   │
  │  │  │Subnet   │  │Subnet   │   │   │
  │  │  │ (ALB)   │  │ (EC2)   │   │   │
  │  │  └─────────┘  └─────────┘   │   │
  │  └──────────────────────────────┘   │
  │        │              │             │
  │   ┌────┴────┐   ┌────┴────┐        │
  │   │   RDS   │   │ ElastiCache│      │
  │   └─────────┘   └──────────┘        │
  └──────────────────────────────────────┘
```

**2. Private Cloud:**

```yaml
Advantages:
  - Complete control over infrastructure
  - Enhanced security and privacy
  - Regulatory compliance
  - Customization freedom
  - Predictable performance

Disadvantages:
  - High capital expenditure
  - Requires skilled staff
  - Limited scalability
  - Hardware maintenance burden

Best For:
  - Government agencies
  - Healthcare organizations
  - Financial institutions
  - Large enterprises with sensitive data

Example Architecture (VMware vSphere):
  ┌────────────────────────────────────────────┐
  │         Private Data Center                │
  │  ┌──────────────────────────────────────┐ │
  │  │         vSphere Cluster               │ │
  │  │  ┌──────────┐  ┌──────────┐         │ │
  │  │  │  Host 1  │  │  Host 2  │  ...    │ │
  │  │  │ (ESXi)   │  │ (ESXi)   │         │ │
  │  │  └────┬─────┘  └────┬─────┘         │ │
  │  │       └──────┬──────┘               │ │
  │  │              │                       │ │
  │  │  ┌───────────┴───────────┐          │ │
  │  │  │   vSAN Storage       │          │ │
  │  │  └───────────────────────┘          │ │
  │  └──────────────────────────────────────┘ │
  │         │                                 │
  │  ┌──────┴──────┐                          │
  │  │  NSX-T SDN  │                          │
  │  └─────────────┘                          │
  └────────────────────────────────────────────┘
```

**3. Hybrid Cloud:**

```yaml
Advantages:
  - Best of both worlds
  - Flexibility in workload placement
  - Compliance for sensitive data
  - Cloud bursting capability
  - Gradual cloud migration

Disadvantages:
  - Complex architecture
  - Network connectivity challenges
  - Data synchronization issues
  - Higher operational complexity

Best For:
  - Organizations with compliance requirements
  - Seasonal workload spikes
  - Gradual cloud adoption
  - Disaster recovery

Example Architecture:
  ┌─────────────────────────────────────────────────────────┐
  │                     Hybrid Cloud                        │
  │                                                         │
  │  ┌──────────────────┐         ┌────────────────────┐   │
  │  │  Private Cloud   │   VPN   │    Public Cloud    │   │
  │  │  (On-premises)   │◄───────►│    (AWS)           │   │
  │  │                  │         │                    │   │
  │  │  ┌────────────┐  │         │  ┌──────────────┐  │   │
  │  │  │ Databases  │  │         │  │ Web Servers  │  │   │
  │  │  │ (PII Data) │  │         │  │ (Stateless)  │  │   │
  │  │  └────────────┘  │         │  └──────────────┘  │   │
  │  │                  │         │                    │   │
  │  │  ┌────────────┐  │         │  ┌──────────────┐  │   │
  │  │  │ Legacy     │  │  Cloud  │  │ Modern Apps  │  │   │
  │  │  │ Systems    │◄─┼──Burst──┼─►│ Auto-scaling │  │   │
  │  │  └────────────┘  │         │  └──────────────┘  │   │
  │  └──────────────────┘         └────────────────────┘   │
  └─────────────────────────────────────────────────────────┘
```

**Hybrid Cloud Implementation:**

```python
# AWS Outposts + AWS Cloud

# Terraform configuration
resource "aws_outposts_outpost" "example" {
  name               = "my-outpost"
  site_id            = aws_outposts_site.example.id
  availability_zone  = "us-east-1a"
}

# Workload on Outpost (on-premises)
resource "aws_instance" "local_database" {
  ami           = "ami-xxxxx"
  instance_type = "m5.xlarge"
  
  # Deploy to Outpost
  subnet_id = aws_subnet.outpost_subnet.id
  
  tags = {
    Name        = "LocalDatabase"
    Environment = "hybrid"
    Location    = "on-premises"
  }
}

# Workload on AWS Cloud
resource "aws_instance" "cloud_web_server" {
  ami           = "ami-xxxxx"
  instance_type = "t3.medium"
  
  # Deploy to cloud region
  subnet_id = aws_subnet.cloud_subnet.id
  
  tags = {
    Name        = "CloudWebServer"
    Environment = "hybrid"
    Location    = "cloud"
  }
}

# VPN connection between on-premises and cloud
resource "aws_vpn_connection" "hybrid" {
  customer_gateway_id = aws_customer_gateway.on_prem.id
  vpn_gateway_id      = aws_vpn_gateway.cloud.id
  type                = "ipsec.1"
}
```

**4. Multi-Cloud:**

```yaml
Advantages:
  - Avoid vendor lock-in
  - Best-of-breed services
  - Geographic distribution
  - Improved resilience
  - Cost optimization

Disadvantages:
  - High complexity
  - Difficult data management
  - Skills gap across platforms
  - Higher operational costs
  - Security complexity

Best For:
  - Large enterprises
  - Regulatory requirements (data residency)
  - Risk mitigation
  - Specialized workloads

Example Architecture:
  ┌────────────────────────────────────────────────────────┐
  │                    Multi-Cloud                         │
  │                                                        │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
  │  │    AWS      │  │   Azure     │  │    GCP      │   │
  │  │             │  │             │  │             │   │
  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │   │
  │  │ │ Compute │ │  │ │ AI/ML   │ │  │ │ BigQuery│ │   │
  │  │ │ Lambda  │ │  │ │ Cognitive│ │  │ │Analytics│ │   │
  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │   │
  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
  │         │                │                │          │
  │         └────────────────┼────────────────┘          │
  │                          │                           │
  │                 ┌────────┴────────┐                  │
  │                 │ Multi-Cloud     │                  │
  │                 │ Management      │                  │
  │                 │ (Terraform,     │                  │
  │                 │  Kubernetes)    │                  │
  │                 └─────────────────┘                  │
  └────────────────────────────────────────────────────────┘
```

**Multi-Cloud Management:**

```python
# Terraform - Multi-cloud deployment

# AWS Provider
provider "aws" {
  alias  = "aws"
  region = "us-east-1"
}

# Azure Provider
provider "azurerm" {
  alias           = "azure"
  features {}
  subscription_id = var.azure_subscription_id
}

# GCP Provider
provider "google" {
  alias   = "gcp"
  project = var.gcp_project
  region  = "us-central1"
}

# Deploy web tier on AWS
resource "aws_instance" "web" {
  provider      = aws.aws
  ami           = "ami-xxxxx"
  instance_type = "t3.medium"
}

# Deploy AI/ML on Azure
resource "azurerm_cognitive_account" "ai" {
  provider            = azurerm.azure
  name                = "ai-service"
  location            = "eastus"
  resource_group_name = azurerm_resource_group.main.name
  kind                = "CognitiveServices"
  sku_name            = "S0"
}

# Deploy analytics on GCP
resource "google_bigquery_dataset" "analytics" {
  provider   = google.gcp
  dataset_id = "analytics"
  location   = "US"
}
```

---

## 10. What is a Content Delivery Network (CDN)? How does it work?

**Answer:**

**What is a CDN?**

A CDN is a geographically distributed network of servers that delivers content to users based on their location, ensuring fast, reliable content delivery.

**CDN Architecture:**

```
                         ┌─────────────────┐
                         │  Origin Server  │
                         │  (Your Server)  │
                         └────────┬────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
           ↓                      ↓                      ↓
    ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
    │ Edge Server │        │ Edge Server │        │ Edge Server │
    │  (US-East)  │        │  (Europe)   │        │   (Asia)    │
    └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
           │                      │                      │
    ┌──────┴──────┐        ┌──────┴──────┐        ┌──────┴──────┐
    │    PoP      │        │    PoP      │        │    PoP      │
    │  New York   │        │   London    │        │   Tokyo     │
    │  Boston     │        │   Paris     │        │  Singapore  │
    │  Miami      │        │   Berlin    │        │   Mumbai    │
    └─────────────┘        └─────────────┘        └─────────────┘
           │                      │                      │
           ↓                      ↓                      ↓
       Users in                Users in               Users in
       Americas                Europe                 Asia
```

**How CDN Works:**

```
User Request Flow:
                                                  
1. User requests: https://cdn.example.com/image.jpg
                     │
                     ↓
2. DNS Resolution (GeoDNS)
   ┌─────────────────────────────────────────────┐
   │ DNS Server determines user's location       │
   │ Returns IP of nearest edge server           │
   │ User in Paris → European PoP               │
   └─────────────────────────────────────────────┘
                     │
                     ↓
3. Edge Server Lookup
   ┌─────────────────────────────────────────────┐
   │ Edge Server (Paris)                         │
   │                                             │
   │ Cache HIT?                                  │
   │   Yes → Return cached content (fast!)      │
   │   No  → Fetch from origin                  │
   └─────────────────────────────────────────────┘
                     │
                     ↓ (Cache Miss)
4. Origin Fetch
   ┌─────────────────────────────────────────────┐
   │ Edge Server fetches from Origin            │
   │ Caches the response                         │
   │ Returns to user                             │
   └─────────────────────────────────────────────┘
```

**CDN Benefits:**

```yaml
Performance:
  - Reduced latency (content served from nearby)
  - Faster page load times
  - Improved user experience

Scalability:
  - Handle traffic spikes
  - Distribute load across edge servers
  - No single point of failure

Reliability:
  - DDoS protection
  - Redundant infrastructure
  - Automatic failover

Cost Reduction:
  - Lower bandwidth costs (origin offloading)
  - Reduced infrastructure needs
  - Pay-per-use pricing
```

**CDN Caching Strategies:**

```python
# Cache-Control Headers

# 1. Cache static assets for 1 year
Cache-Control: public, max-age=31536000, immutable

# 2. Cache with revalidation
Cache-Control: public, max-age=3600, must-revalidate

# 3. No caching (dynamic content)
Cache-Control: private, no-cache, no-store

# 4. Stale-while-revalidate
Cache-Control: public, max-age=3600, stale-while-revalidate=86400
```

**CDN Configuration (CloudFront Example):**

```python
# Terraform - AWS CloudFront Distribution

resource "aws_cloudfront_distribution" "cdn" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_All"
  
  # Origin configuration
  origin {
    domain_name = aws_s3_bucket.static.bucket_regional_domain_name
    origin_id   = "S3-static-content"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }
  
  origin {
    domain_name = "api.example.com"
    origin_id   = "API-backend"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  # Default cache behavior (static content)
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-static-content"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 86400    # 1 day
    max_ttl     = 31536000 # 1 year
  }
  
  # API cache behavior (dynamic content)
  ordered_cache_behavior {
    path_pattern           = "/api/*"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "API-backend"
    viewer_protocol_policy = "https-only"
    
    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Origin"]
      cookies {
        forward = "all"
      }
    }
    
    min_ttl     = 0
    default_ttl = 0  # No caching for API
    max_ttl     = 0
  }
  
  # Custom error responses
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"  # SPA routing
  }
  
  # Geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA", "GB", "DE"]
    }
  }
  
  # SSL certificate
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.cert.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}
```

**Cache Invalidation:**

```bash
# AWS CloudFront - Invalidate specific paths
aws cloudfront create-invalidation \
    --distribution-id E12345 \
    --paths "/images/*" "/css/*"

# Invalidate everything
aws cloudfront create-invalidation \
    --distribution-id E12345 \
    --paths "/*"
```

**CDN Comparison:**

| Provider | Strengths | Best For |
|----------|-----------|----------|
| **CloudFront** | AWS integration, Lambda@Edge | AWS-heavy workloads |
| **Cloudflare** | Security, Workers, Free tier | Security-focused apps |
| **Fastly** | Real-time purging, VCL | Dynamic content |
| **Akamai** | Enterprise features, Scale | Large enterprises |
| **Azure CDN** | Azure integration | Microsoft ecosystem |

**Advanced CDN Features:**

```yaml
Edge Computing:
  - CloudFront Lambda@Edge
  - Cloudflare Workers
  - Fastly Compute@Edge
  
  Use Cases:
    - A/B testing at edge
    - Authentication
    - Request/response manipulation
    - Personalization
    - Bot detection

Example - Cloudflare Worker:
```

```javascript
// Cloudflare Worker - A/B Testing at Edge
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Get or set A/B test cookie
  const cookie = request.headers.get('Cookie')
  let variant = getCookie(cookie, 'ab-variant')
  
  if (!variant) {
    variant = Math.random() < 0.5 ? 'A' : 'B'
  }
  
  // Route to appropriate origin
  const origin = variant === 'A' 
    ? 'https://variant-a.example.com'
    : 'https://variant-b.example.com'
  
  const response = await fetch(origin + url.pathname, request)
  
  // Set cookie for consistent experience
  const newResponse = new Response(response.body, response)
  newResponse.headers.append('Set-Cookie', `ab-variant=${variant}; Path=/; Max-Age=86400`)
  
  return newResponse
}
```

---

## 11. Explain different database types and when to use each (SQL, NoSQL, Graph, Time-Series).

**Answer:**

**Database Types Overview:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Database Types                                │
├─────────────────┬────────────────┬───────────────┬──────────────┤
│   Relational    │    Document    │   Key-Value   │    Graph     │
│     (SQL)       │    (NoSQL)     │   (NoSQL)     │   (NoSQL)    │
├─────────────────┼────────────────┼───────────────┼──────────────┤
│ PostgreSQL      │ MongoDB        │ Redis         │ Neo4j        │
│ MySQL           │ CouchDB        │ Memcached     │ Amazon Neptune│
│ Oracle          │ DynamoDB       │ DynamoDB      │ JanusGraph   │
│ SQL Server      │ Elasticsearch  │ Aerospike     │ ArangoDB     │
├─────────────────┼────────────────┼───────────────┼──────────────┤
│ Tables, Rows    │ JSON Documents │ Key → Value   │ Nodes, Edges │
│ Fixed Schema    │ Flexible Schema│ Simple lookup │ Relationships│
│ ACID            │ Eventually     │ Ultra-fast    │ Traversals   │
│ Joins           │ consistent     │ Caching       │              │
└─────────────────┴────────────────┴───────────────┴──────────────┘

┌─────────────────┬────────────────┬───────────────┐
│  Time-Series    │  Column-Family │   Search      │
│   Database      │   (Wide-Column)│   Engine      │
├─────────────────┼────────────────┼───────────────┤
│ InfluxDB        │ Cassandra      │ Elasticsearch │
│ TimescaleDB     │ HBase          │ Solr          │
│ Prometheus      │ ScyllaDB       │ OpenSearch    │
│ QuestDB         │ BigTable       │ Meilisearch   │
├─────────────────┼────────────────┼───────────────┤
│ Metrics, Events │ Large scale    │ Full-text     │
│ IoT data        │ Write-heavy    │ Aggregations  │
│ Time-based      │ Distributed    │ Faceted search│
└─────────────────┴────────────────┴───────────────┘
```

**1. Relational Databases (SQL):**

```sql
-- Schema Definition
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER,
    quantity INTEGER,
    price DECIMAL(10, 2)
);

-- Complex Query with Joins
SELECT 
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2024-01-01'
GROUP BY u.id
HAVING SUM(o.total_amount) > 1000
ORDER BY total_spent DESC;
```

```yaml
When to Use SQL:
  - Structured data with clear relationships
  - ACID compliance required
  - Complex queries and joins
  - Reporting and analytics
  - Financial transactions

Examples:
  - E-commerce product catalog
  - User management systems
  - Inventory management
  - Banking systems

Strengths:
  - Data integrity (foreign keys, constraints)
  - Mature ecosystem
  - Standard query language
  - Strong consistency

Weaknesses:
  - Vertical scaling limitations
  - Schema changes can be complex
  - Not ideal for unstructured data
```

**2. Document Databases (MongoDB):**

```javascript
// Flexible Schema - User Document
{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "profile": {
    "name": "John Doe",
    "avatar": "https://...",
    "preferences": {
      "theme": "dark",
      "notifications": true
    }
  },
  "addresses": [
    {
      "type": "home",
      "street": "123 Main St",
      "city": "New York",
      "zip": "10001"
    },
    {
      "type": "work",
      "street": "456 Office Ave",
      "city": "New York",
      "zip": "10002"
    }
  ],
  "orders": [
    { "order_id": "...", "total": 99.99, "date": ISODate("...") }
  ]
}

// Query Examples
db.users.find({
  "profile.preferences.theme": "dark",
  "addresses.city": "New York"
})

// Aggregation Pipeline
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: {
      _id: "$customer_id",
      totalSpent: { $sum: "$total" },
      orderCount: { $sum: 1 }
  }},
  { $sort: { totalSpent: -1 } },
  { $limit: 10 }
])
```

```yaml
When to Use Document DB:
  - Semi-structured or varying data
  - Rapid development (schema flexibility)
  - Content management
  - Real-time analytics
  - Mobile app backends

Examples:
  - User profiles with varying attributes
  - Product catalogs with different attributes
  - Content management systems
  - Event logging

Strengths:
  - Schema flexibility
  - Horizontal scaling (sharding)
  - Developer-friendly (JSON)
  - Fast for document-centric queries

Weaknesses:
  - No joins (requires denormalization)
  - Less mature for complex transactions
  - Data duplication for related data
```

**3. Key-Value Stores (Redis):**

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Simple key-value
r.set('user:1000:name', 'John Doe')
r.get('user:1000:name')

# With expiration (session data)
r.setex('session:abc123', 3600, 'user_id:1000')  # 1 hour TTL

# Hash (object storage)
r.hset('user:1000', mapping={
    'name': 'John Doe',
    'email': 'john@example.com',
    'login_count': 42
})
r.hgetall('user:1000')
r.hincrby('user:1000', 'login_count', 1)

# List (queue)
r.lpush('queue:tasks', 'task1', 'task2', 'task3')
r.rpop('queue:tasks')  # Dequeue

# Sorted Set (leaderboard)
r.zadd('leaderboard', {'player1': 100, 'player2': 200, 'player3': 150})
r.zrevrange('leaderboard', 0, 9, withscores=True)  # Top 10

# Pub/Sub
r.publish('notifications', 'New message!')

# Distributed Lock
lock = r.lock('resource:lock', timeout=10)
if lock.acquire(blocking=True):
    try:
        # Critical section
        process_resource()
    finally:
        lock.release()
```

```yaml
When to Use Key-Value:
  - Caching
  - Session management
  - Real-time leaderboards
  - Rate limiting
  - Distributed locks
  - Message queues

Examples:
  - API response caching
  - Shopping cart storage
  - Real-time analytics counters
  - Feature flags

Strengths:
  - Extremely fast (in-memory)
  - Simple data model
  - Horizontal scaling
  - Versatile data structures

Weaknesses:
  - Limited query capabilities
  - Data size limited by memory
  - No complex relationships
```

**4. Graph Databases (Neo4j):**

```cypher
// Create nodes and relationships
CREATE (john:Person {name: 'John', age: 30})
CREATE (jane:Person {name: 'Jane', age: 28})
CREATE (acme:Company {name: 'Acme Corp'})
CREATE (techco:Company {name: 'Tech Co'})

CREATE (john)-[:WORKS_AT {since: 2020}]->(acme)
CREATE (jane)-[:WORKS_AT {since: 2019}]->(techco)
CREATE (john)-[:FRIENDS_WITH]->(jane)
CREATE (acme)-[:PARTNER_OF]->(techco)

// Find friends of friends
MATCH (person:Person {name: 'John'})-[:FRIENDS_WITH*2]-(fof)
WHERE person <> fof
RETURN DISTINCT fof.name

// Shortest path between two people
MATCH path = shortestPath(
  (a:Person {name: 'John'})-[*]-(b:Person {name: 'Alice'})
)
RETURN path

// Recommendation engine - Products bought by similar users
MATCH (user:User {id: '123'})-[:PURCHASED]->(product:Product)
      <-[:PURCHASED]-(similar:User)-[:PURCHASED]->(recommended:Product)
WHERE NOT (user)-[:PURCHASED]->(recommended)
RETURN recommended, COUNT(*) as score
ORDER BY score DESC
LIMIT 10

// Social network influence
MATCH (influencer:Person)-[:FOLLOWS*1..3]->(follower:Person)
WITH influencer, COUNT(DISTINCT follower) as reach
RETURN influencer.name, reach
ORDER BY reach DESC
LIMIT 10
```

```yaml
When to Use Graph DB:
  - Highly connected data
  - Relationship-heavy queries
  - Social networks
  - Recommendation engines
  - Fraud detection
  - Knowledge graphs

Examples:
  - LinkedIn connections
  - Facebook friend suggestions
  - Network topology
  - Access control systems

Strengths:
  - Fast relationship traversal
  - Intuitive data modeling
  - Flexible schema
  - Complex pattern matching

Weaknesses:
  - Not suitable for bulk analytics
  - Limited ecosystem
  - Learning curve (Cypher)
  - Scaling can be challenging
```

**5. Time-Series Databases (InfluxDB):**

```python
# InfluxDB Line Protocol
# measurement,tag1=value1,tag2=value2 field1=value1,field2=value2 timestamp

# Example: Server metrics
cpu_usage,host=server01,region=us-east value=0.64 1609459200000000000
memory_usage,host=server01,region=us-east used=8192,total=16384 1609459200000000000
requests,host=server01,endpoint=/api/users count=1523,latency_ms=45 1609459200000000000

# InfluxQL Queries
# Average CPU over 5-minute windows
SELECT MEAN(value) 
FROM cpu_usage 
WHERE time > now() - 1h 
GROUP BY time(5m), host

# Moving average
SELECT MOVING_AVERAGE(value, 3) 
FROM cpu_usage 
WHERE time > now() - 1d

# Alerting - High CPU
SELECT MEAN(value) 
FROM cpu_usage 
WHERE time > now() - 5m 
GROUP BY host
HAVING MEAN(value) > 0.9
```

```sql
-- TimescaleDB (PostgreSQL extension)

-- Create hypertable (time-partitioned table)
CREATE TABLE metrics (
    time        TIMESTAMPTZ NOT NULL,
    host        TEXT NOT NULL,
    cpu         DOUBLE PRECISION,
    memory      DOUBLE PRECISION,
    disk_io     DOUBLE PRECISION
);

SELECT create_hypertable('metrics', 'time');

-- Time-bucket aggregations
SELECT 
    time_bucket('5 minutes', time) AS bucket,
    host,
    AVG(cpu) as avg_cpu,
    MAX(cpu) as max_cpu,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY cpu) as p95_cpu
FROM metrics
WHERE time > NOW() - INTERVAL '1 day'
GROUP BY bucket, host
ORDER BY bucket DESC;

-- Continuous aggregates (materialized views)
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS hour,
    host,
    AVG(cpu) as avg_cpu,
    AVG(memory) as avg_memory
FROM metrics
GROUP BY hour, host;
```

```yaml
When to Use Time-Series DB:
  - Metrics and monitoring
  - IoT sensor data
  - Financial tick data
  - Application performance monitoring
  - Log analytics

Examples:
  - Server monitoring (CPU, memory, disk)
  - IoT sensor readings
  - Stock price history
  - User activity tracking

Strengths:
  - Optimized for time-based queries
  - Efficient data compression
  - Built-in downsampling
  - High write throughput

Weaknesses:
  - Limited query flexibility
  - Not for general-purpose use
  - Specialized skill set needed
```

**Database Selection Matrix:**

| Use Case | Recommended DB | Why |
|----------|---------------|-----|
| E-commerce orders | PostgreSQL | ACID, complex queries |
| User sessions | Redis | Fast, TTL support |
| Product catalog | MongoDB | Flexible attributes |
| Social network | Neo4j | Relationship traversal |
| Server metrics | TimescaleDB/InfluxDB | Time-series optimized |
| Search | Elasticsearch | Full-text, aggregations |
| Chat messages | Cassandra | High write throughput |
| Real-time analytics | ClickHouse | Column-oriented, fast |

---

## 12. Design a notification system that can send notifications via multiple channels (push, email, SMS).

**Answer:**

**Requirements:**

**Functional:**
- Send notifications via push, email, SMS
- Support templates and personalization
- Priority levels (critical, high, normal, low)
- User preferences (opt-in/opt-out per channel)
- Scheduled notifications
- Delivery tracking and retry

**Non-Functional:**
- Handle 1M+ notifications/day
- Delivery latency <5 seconds for critical
- 99.9% delivery success rate
- Scalable and fault-tolerant

**High-Level Architecture:**

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Notification System                                │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Service A  │     │  Service B  │     │  Service C  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────┴──────┐
                    │ API Gateway │
                    └──────┬──────┘
                           │
            ┌──────────────┴──────────────┐
            │     Notification Service     │
            │  ┌─────────────────────────┐ │
            │  │    Request Handler      │ │
            │  │  - Validation           │ │
            │  │  - Rate Limiting        │ │
            │  │  - Deduplication        │ │
            │  └───────────┬─────────────┘ │
            └──────────────┼──────────────┘
                           │
                    ┌──────┴──────┐
                    │ Message Queue│
                    │   (Kafka)    │
                    └──────┬──────┘
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ↓                   ↓                   ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Priority Q  │     │ Priority Q  │     │ Priority Q  │
│  Critical   │     │    High     │     │   Normal    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │      Worker Service          │
            │  ┌─────────────────────────┐ │
            │  │  Channel Router         │ │
            │  └─────────┬───────────────┘ │
            └────────────┼────────────────┘
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│Push Provider│   │Email Provider│   │SMS Provider │
│ (FCM/APNS)  │   │ (SendGrid)  │   │  (Twilio)   │
└─────────────┘   └─────────────┘   └─────────────┘
```

**Database Schema:**

```sql
-- Notification requests
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,  -- order_update, promo, alert
    priority VARCHAR(20) DEFAULT 'normal',  -- critical, high, normal, low
    title VARCHAR(255),
    body TEXT,
    data JSONB,
    channels VARCHAR[] NOT NULL,  -- {push, email, sms}
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    idempotency_key VARCHAR(255) UNIQUE
);

-- Delivery attempts per channel
CREATE TABLE notification_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID REFERENCES notifications(id),
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    provider VARCHAR(50),
    provider_message_id VARCHAR(255),
    attempt_count INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB
);

-- User preferences
CREATE TABLE user_notification_preferences (
    user_id UUID PRIMARY KEY,
    push_enabled BOOLEAN DEFAULT true,
    email_enabled BOOLEAN DEFAULT true,
    sms_enabled BOOLEAN DEFAULT true,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB  -- {"promo": {"push": false, "email": true}}
);

-- User devices (for push)
CREATE TABLE user_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    device_token VARCHAR(500) NOT NULL,
    platform VARCHAR(20) NOT NULL,  -- ios, android, web
    app_version VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    UNIQUE(device_token)
);

-- Templates
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    subject VARCHAR(255),  -- for email
    title VARCHAR(255),
    body TEXT NOT NULL,
    variables VARCHAR[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API Design:**

```yaml
# Send Notification
POST /api/v1/notifications
Request:
  {
    "user_id": "user-123",
    "type": "order_shipped",
    "priority": "high",
    "channels": ["push", "email"],
    "template": "order_shipped",
    "data": {
      "order_id": "ORD-456",
      "tracking_number": "1Z999AA10123456784",
      "estimated_delivery": "2024-01-20"
    },
    "scheduled_at": null,  # null for immediate
    "idempotency_key": "order-456-shipped"
  }

Response:
  {
    "notification_id": "notif-789",
    "status": "queued",
    "channels": {
      "push": "pending",
      "email": "pending"
    }
  }

# Batch Send
POST /api/v1/notifications/batch
Request:
  {
    "notifications": [
      {"user_id": "user-1", "type": "promo", ...},
      {"user_id": "user-2", "type": "promo", ...}
    ]
  }

# Get Status
GET /api/v1/notifications/{id}/status
Response:
  {
    "notification_id": "notif-789",
    "status": "delivered",
    "channels": {
      "push": {"status": "delivered", "delivered_at": "..."},
      "email": {"status": "delivered", "delivered_at": "..."}
    }
  }
```

**Core Services Implementation:**

```python
# notification_service.py

from dataclasses import dataclass
from enum import Enum
import asyncio

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class Channel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"

@dataclass
class NotificationRequest:
    user_id: str
    type: str
    title: str
    body: str
    channels: list[Channel]
    priority: Priority = Priority.NORMAL
    data: dict = None
    template: str = None
    scheduled_at: datetime = None
    idempotency_key: str = None

class NotificationService:
    def __init__(self, kafka_producer, user_service, preference_service):
        self.kafka = kafka_producer
        self.user_service = user_service
        self.preference_service = preference_service
    
    async def send(self, request: NotificationRequest) -> str:
        # 1. Validate request
        self.validate(request)
        
        # 2. Check idempotency
        if request.idempotency_key:
            existing = await self.get_by_idempotency_key(request.idempotency_key)
            if existing:
                return existing.id
        
        # 3. Get user preferences
        preferences = await self.preference_service.get(request.user_id)
        
        # 4. Filter channels based on preferences
        allowed_channels = self.filter_channels(request.channels, preferences)
        
        if not allowed_channels:
            raise NoValidChannelsError("User has opted out of all requested channels")
        
        # 5. Render templates
        notification = await self.create_notification(request, allowed_channels)
        
        # 6. Schedule or send immediately
        if request.scheduled_at:
            await self.schedule(notification)
        else:
            await self.enqueue(notification)
        
        return notification.id
    
    async def enqueue(self, notification):
        # Route to priority queue
        topic = f"notifications.{notification.priority.value}"
        
        for channel in notification.channels:
            message = {
                "notification_id": notification.id,
                "user_id": notification.user_id,
                "channel": channel.value,
                "payload": self.build_payload(notification, channel)
            }
            await self.kafka.send(topic, message)
    
    def filter_channels(self, requested: list, preferences) -> list:
        allowed = []
        for channel in requested:
            if channel == Channel.PUSH and preferences.push_enabled:
                allowed.append(channel)
            elif channel == Channel.EMAIL and preferences.email_enabled:
                allowed.append(channel)
            elif channel == Channel.SMS and preferences.sms_enabled:
                allowed.append(channel)
        
        # Check quiet hours
        if preferences.quiet_hours_start and preferences.quiet_hours_end:
            if self.is_quiet_hours(preferences):
                # Only allow critical notifications
                allowed = [c for c in allowed if notification.priority == Priority.CRITICAL]
        
        return allowed
```

**Channel Providers:**

```python
# providers/push_provider.py
import firebase_admin
from firebase_admin import messaging

class PushProvider:
    def __init__(self):
        firebase_admin.initialize_app()
    
    async def send(self, notification, user_devices):
        results = []
        
        for device in user_devices:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=notification.title,
                        body=notification.body
                    ),
                    data=notification.data,
                    token=device.token,
                    android=messaging.AndroidConfig(
                        priority='high' if notification.priority in [Priority.CRITICAL, Priority.HIGH] else 'normal',
                        notification=messaging.AndroidNotification(
                            click_action='OPEN_NOTIFICATION'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                alert=messaging.ApsAlert(
                                    title=notification.title,
                                    body=notification.body
                                ),
                                sound='default',
                                badge=1
                            )
                        )
                    )
                )
                
                response = messaging.send(message)
                results.append({
                    'device_id': device.id,
                    'status': 'delivered',
                    'provider_message_id': response
                })
                
            except messaging.UnregisteredError:
                # Device token is invalid, mark device as inactive
                await self.mark_device_inactive(device.id)
                results.append({
                    'device_id': device.id,
                    'status': 'failed',
                    'error': 'unregistered'
                })
                
            except Exception as e:
                results.append({
                    'device_id': device.id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results


# providers/email_provider.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailProvider:
    def __init__(self, api_key):
        self.client = SendGridAPIClient(api_key)
    
    async def send(self, notification, user_email):
        message = Mail(
            from_email='notifications@example.com',
            to_emails=user_email,
            subject=notification.title,
            html_content=notification.body
        )
        
        # Add tracking
        message.tracking_settings = TrackingSettings(
            click_tracking=ClickTracking(True),
            open_tracking=OpenTracking(True)
        )
        
        try:
            response = self.client.send(message)
            return {
                'status': 'delivered' if response.status_code == 202 else 'failed',
                'provider_message_id': response.headers.get('X-Message-Id')
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }


# providers/sms_provider.py
from twilio.rest import Client

class SMSProvider:
    def __init__(self, account_sid, auth_token, from_number):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
    
    async def send(self, notification, phone_number):
        try:
            message = self.client.messages.create(
                body=notification.body,
                from_=self.from_number,
                to=phone_number
            )
            
            return {
                'status': 'delivered' if message.status == 'sent' else 'pending',
                'provider_message_id': message.sid
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
```

**Worker Service:**

```python
# worker.py
class NotificationWorker:
    def __init__(self, providers: dict, delivery_repo, retry_policy):
        self.providers = providers
        self.delivery_repo = delivery_repo
        self.retry_policy = retry_policy
    
    async def process(self, message):
        notification_id = message['notification_id']
        channel = Channel(message['channel'])
        payload = message['payload']
        
        # Get or create delivery record
        delivery = await self.delivery_repo.get_or_create(
            notification_id, channel
        )
        
        # Check retry count
        if delivery.attempt_count >= self.retry_policy.max_attempts:
            await self.delivery_repo.mark_failed(
                delivery.id, 
                "Max retry attempts exceeded"
            )
            return
        
        # Get appropriate provider
        provider = self.providers[channel]
        
        try:
            # Send notification
            result = await provider.send(payload)
            
            if result['status'] == 'delivered':
                await self.delivery_repo.mark_delivered(
                    delivery.id,
                    result.get('provider_message_id')
                )
            else:
                # Schedule retry with exponential backoff
                await self.schedule_retry(delivery, result.get('error'))
                
        except Exception as e:
            await self.schedule_retry(delivery, str(e))
    
    async def schedule_retry(self, delivery, error):
        delay = self.retry_policy.get_delay(delivery.attempt_count)
        
        await self.delivery_repo.update(delivery.id, {
            'attempt_count': delivery.attempt_count + 1,
            'last_attempt_at': datetime.utcnow(),
            'error_message': error
        })
        
        # Requeue with delay
        await self.kafka.send_with_delay(
            f"notifications.retry",
            {'delivery_id': delivery.id},
            delay_seconds=delay
        )


class RetryPolicy:
    def __init__(self, max_attempts=3, base_delay=60):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
    
    def get_delay(self, attempt_count):
        # Exponential backoff: 60s, 120s, 240s
        return self.base_delay * (2 ** attempt_count)
```

**Monitoring and Analytics:**

```python
# Metrics to track
metrics = {
    "notifications_sent_total": Counter(
        "notifications_sent_total",
        "Total notifications sent",
        ["channel", "type", "status"]
    ),
    "notification_latency": Histogram(
        "notification_latency_seconds",
        "Time from request to delivery",
        ["channel", "priority"]
    ),
    "notification_queue_size": Gauge(
        "notification_queue_size",
        "Current queue size",
        ["priority"]
    )
}

# Dashboard queries
dashboard_queries = {
    "delivery_rate": """
        SELECT 
            channel,
            COUNT(*) FILTER (WHERE status = 'delivered') * 100.0 / COUNT(*) as delivery_rate
        FROM notification_deliveries
        WHERE created_at > NOW() - INTERVAL '1 hour'
        GROUP BY channel
    """,
    
    "avg_latency": """
        SELECT 
            channel,
            AVG(EXTRACT(EPOCH FROM (delivered_at - created_at))) as avg_latency_seconds
        FROM notification_deliveries
        WHERE delivered_at IS NOT NULL
        AND created_at > NOW() - INTERVAL '1 hour'
        GROUP BY channel
    """,
    
    "failure_reasons": """
        SELECT 
            channel,
            error_message,
            COUNT(*) as count
        FROM notification_deliveries
        WHERE status = 'failed'
        AND created_at > NOW() - INTERVAL '24 hours'
        GROUP BY channel, error_message
        ORDER BY count DESC
        LIMIT 10
    """
}
```

This comprehensive guide covers all major aspects of Cloud and System Design that are commonly asked in senior engineering interviews.
