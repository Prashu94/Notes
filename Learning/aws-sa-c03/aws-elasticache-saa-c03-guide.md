# Amazon ElastiCache - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [ElastiCache Fundamentals](#elasticache-fundamentals)
3. [ElastiCache for Redis](#elasticache-for-redis)
4. [ElastiCache for Memcached](#elasticache-for-memcached)
5. [Redis vs Memcached Comparison](#redis-vs-memcached-comparison)
6. [Cluster Architecture](#cluster-architecture)
7. [Replication and High Availability](#replication-and-high-availability)
8. [Caching Strategies](#caching-strategies)
9. [Security](#security)
10. [Monitoring and Performance](#monitoring-and-performance)
11. [Scaling](#scaling)
12. [Backup and Recovery](#backup-and-recovery)
13. [Cost Optimization](#cost-optimization)
14. [Best Practices](#best-practices)
15. [Common Use Cases](#common-use-cases)
16. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
17. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What is Amazon ElastiCache?

Amazon ElastiCache is a fully managed in-memory caching service that makes it easy to deploy, operate, and scale an in-memory cache in the cloud. ElastiCache supports two popular open-source caching engines: **Redis** and **Memcached**.

### Why Use In-Memory Caching?

- **Performance**: Sub-millisecond latency for cached data
- **Reduce Database Load**: Offload read-heavy workloads
- **Cost Efficiency**: Reduce expensive database queries
- **Scalability**: Handle traffic spikes without database changes
- **Session Management**: Store user sessions for stateless applications

### Key Benefits

- **Fully Managed**: AWS handles patching, monitoring, failure recovery
- **High Performance**: In-memory data store with microsecond latency
- **Scalability**: Scale from small to large workloads
- **High Availability**: Multi-AZ deployments with automatic failover
- **Security**: VPC support, encryption, IAM authentication

### ElastiCache Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Application                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                  │
│              ┌─────────────┴─────────────┐                   │
│              │                           │                   │
│              ▼                           ▼                   │
│  ┌───────────────────────┐   ┌───────────────────────┐     │
│  │    ElastiCache        │   │      Database          │     │
│  │    (Cache Layer)      │   │   (Persistent Store)   │     │
│  │                       │   │                        │     │
│  │  • Sub-ms latency     │   │  • RDS                 │     │
│  │  • In-memory          │   │  • Aurora              │     │
│  │  • Redis/Memcached    │   │  • DynamoDB            │     │
│  └───────────────────────┘   └───────────────────────┘     │
│                                                               │
│  Cache Hit Flow:                                              │
│  1. App checks cache → 2. Return cached data                 │
│                                                               │
│  Cache Miss Flow:                                             │
│  1. App checks cache → 2. Query database →                   │
│  3. Store in cache → 4. Return data                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ElastiCache Fundamentals

### Core Concepts

#### Clusters
- Collection of one or more cache nodes
- Deploy in a VPC for network isolation
- Regional resource

#### Nodes
- Individual compute unit
- Fixed memory and compute capacity
- Node type determines resources

#### Node Types

| Family | Use Case | Examples |
|--------|----------|----------|
| **Standard (M)** | General purpose | cache.m6g.large, cache.m5.xlarge |
| **Memory Optimized (R)** | Memory-intensive | cache.r6g.large, cache.r5.2xlarge |
| **Burstable (T)** | Variable workloads | cache.t3.micro, cache.t4g.medium |

#### Endpoints
- **Primary Endpoint**: Read/write operations (Redis)
- **Reader Endpoint**: Read operations (Redis with replicas)
- **Configuration Endpoint**: Memcached auto-discovery
- **Node Endpoints**: Direct connection to specific nodes

### Supported Engines

| Feature | Redis | Memcached |
|---------|-------|-----------|
| **Data Structures** | Strings, Lists, Sets, Hashes, Sorted Sets | Simple key-value |
| **Persistence** | Yes (RDB, AOF) | No |
| **Replication** | Yes (up to 5 replicas) | No |
| **Multi-AZ** | Yes | No (but multi-node) |
| **Pub/Sub** | Yes | No |
| **Lua Scripting** | Yes | No |
| **Transactions** | Yes | No |
| **Backup/Restore** | Yes | No |

---

## ElastiCache for Redis

### Redis Overview

Redis (Remote Dictionary Server) is an open-source, in-memory data structure store used as a database, cache, message broker, and queue.

### Redis Features

- **Data Structures**: Rich data types beyond simple key-value
- **Persistence**: Optional data persistence (RDB snapshots, AOF)
- **Replication**: Built-in replication with automatic failover
- **Pub/Sub**: Publish/subscribe messaging
- **Lua Scripting**: Server-side scripting
- **Transactions**: MULTI/EXEC atomic operations
- **Geospatial**: Location-based queries

### Redis Cluster Modes

#### Cluster Mode Disabled (Single Shard)
- One primary node + up to 5 replicas
- All data on single shard
- Simpler architecture
- Maximum 500 connections per node

```
┌──────────────────────────────────────────┐
│       Cluster Mode Disabled               │
├──────────────────────────────────────────┤
│                                           │
│   ┌─────────┐                            │
│   │ Primary │                            │
│   │  Node   │                            │
│   └────┬────┘                            │
│        │                                  │
│   ┌────┴────┬────────┬────────┐         │
│   │         │        │        │         │
│   ▼         ▼        ▼        ▼         │
│ ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐     │
│ │Rep 1│  │Rep 2│  │Rep 3│  │Rep 4│     │
│ └─────┘  └─────┘  └─────┘  └─────┘     │
│                                           │
│ • Single shard                            │
│ • Up to 5 read replicas                   │
│ • Automatic failover                      │
│                                           │
└──────────────────────────────────────────┘
```

#### Cluster Mode Enabled (Multiple Shards)
- Data partitioned across multiple shards
- Each shard has primary + replicas
- Up to 500 shards
- Higher scalability and availability

```
┌──────────────────────────────────────────────────────────┐
│               Cluster Mode Enabled                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Shard 1          Shard 2          Shard 3               │
│  ┌────────┐       ┌────────┐       ┌────────┐           │
│  │Primary │       │Primary │       │Primary │           │
│  │Slot 0- │       │Slot    │       │Slot    │           │
│  │5460    │       │5461-   │       │10923-  │           │
│  └───┬────┘       │10922   │       │16383   │           │
│      │            └───┬────┘       └───┬────┘           │
│   ┌──┴──┐          ┌──┴──┐          ┌──┴──┐            │
│   │Rep  │          │Rep  │          │Rep  │            │
│   └─────┘          └─────┘          └─────┘            │
│                                                           │
│ • Data sharded using hash slots (16384 total)            │
│ • Each shard handles subset of slots                      │
│ • Up to 500 shards, 500 nodes per cluster                │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Redis Data Types

```
┌────────────────────────────────────────────────────────────┐
│                    Redis Data Types                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Strings:     SET user:1 "John"                            │
│               GET user:1 → "John"                          │
│                                                             │
│  Lists:       LPUSH notifications:user1 "msg1" "msg2"      │
│               (Ordered, duplicates allowed)                 │
│                                                             │
│  Sets:        SADD tags:post1 "aws" "cloud" "tech"         │
│               (Unordered, unique values)                    │
│                                                             │
│  Sorted Sets: ZADD leaderboard 100 "player1" 95 "player2"  │
│               (Ordered by score, unique values)             │
│                                                             │
│  Hashes:      HSET user:1 name "John" email "j@test.com"   │
│               (Field-value pairs)                           │
│                                                             │
│  Streams:     XADD mystream * field value                  │
│               (Append-only log)                             │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Redis Global Datastore

Cross-region replication for disaster recovery:

- **Primary Region**: Accepts writes
- **Secondary Regions**: Read-only replicas
- **Replication**: Asynchronous, typically < 1 second
- **Failover**: Promote secondary to primary (manual)

```
┌─────────────────────────────────────────────────────────────┐
│                  Redis Global Datastore                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   us-east-1 (Primary)          eu-west-1 (Secondary)        │
│   ┌──────────────────┐         ┌──────────────────┐         │
│   │ ┌──────┐┌──────┐ │   Async │ ┌──────┐┌──────┐ │         │
│   │ │Pri   ││Rep   │ │ ──────► │ │Pri   ││Rep   │ │         │
│   │ └──────┘└──────┘ │  Repl  │ └──────┘└──────┘ │         │
│   │ Read/Write       │         │ Read Only       │         │
│   └──────────────────┘         └──────────────────┘         │
│                                                              │
│   • Up to 2 secondary regions                                │
│   • Sub-second replication lag                               │
│   • RPO typically < 1 second                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ElastiCache for Memcached

### Memcached Overview

Memcached is a high-performance, distributed memory object caching system designed for simplicity and speed.

### Memcached Features

- **Simplicity**: Simple key-value store
- **Multi-threaded**: Utilizes multiple CPU cores
- **Auto-discovery**: Clients auto-discover cluster nodes
- **Horizontal Scaling**: Add nodes for more capacity
- **No Persistence**: Data lost on node failure

### Memcached Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Memcached Cluster Architecture               │
├──────────────────────────────────────────────────────────┤
│                                                           │
│              ┌──────────────────────┐                    │
│              │  Configuration       │                    │
│              │  Endpoint            │                    │
│              └──────────┬───────────┘                    │
│                         │                                │
│         ┌───────────────┼───────────────┐               │
│         │               │               │               │
│    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐          │
│    │  Node 1 │    │  Node 2 │    │  Node 3 │          │
│    │ (AZ-a)  │    │ (AZ-b)  │    │ (AZ-c)  │          │
│    └─────────┘    └─────────┘    └─────────┘          │
│                                                           │
│  • Data distributed via consistent hashing               │
│  • Each node is independent (no replication)             │
│  • Node failure = data loss on that node                 │
│  • Up to 300 nodes per cluster                           │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Memcached Use Cases

1. **Simple Caching**: Database query results
2. **Session Storage**: Web application sessions
3. **Page Caching**: Full or partial page content
4. **API Response Caching**: REST API responses
5. **Object Caching**: Frequently accessed objects

---

## Redis vs Memcached Comparison

### Feature Comparison

| Feature | Redis | Memcached |
|---------|-------|-----------|
| **Data Types** | Rich (strings, lists, sets, hashes, etc.) | Simple key-value only |
| **Persistence** | Yes (RDB, AOF) | No |
| **Replication** | Yes (up to 5 replicas per shard) | No |
| **Multi-AZ** | Yes with automatic failover | No (multi-node only) |
| **Cluster Mode** | Yes (data sharding) | Yes (data partitioning) |
| **Backup/Restore** | Yes | No |
| **Pub/Sub** | Yes | No |
| **Transactions** | Yes | No |
| **Lua Scripting** | Yes | No |
| **Geospatial** | Yes | No |
| **Multi-threaded** | Single-threaded (6.0+ multi-threaded I/O) | Yes |
| **Maximum Data Size** | 512 MB per key | 1 MB per key |

### When to Use Redis

✅ **Choose Redis when you need:**
- Data persistence
- High availability with Multi-AZ
- Complex data structures
- Pub/Sub messaging
- Geospatial queries
- Atomic operations
- Backup and recovery
- Sorted data (leaderboards)

### When to Use Memcached

✅ **Choose Memcached when you need:**
- Simplest caching model
- Multi-threaded performance
- Scale out/in (add/remove nodes easily)
- Large object caching (up to 1 MB)
- No persistence required
- Lower memory overhead per key

### Decision Matrix

| Requirement | Recommended |
|-------------|-------------|
| Need persistence | **Redis** |
| Need high availability | **Redis** |
| Simple key-value only | **Memcached** |
| Leaderboards/ranking | **Redis** (sorted sets) |
| Session management (HA required) | **Redis** |
| Session management (simple) | **Memcached** |
| Pub/Sub messaging | **Redis** |
| Maximum simplicity | **Memcached** |
| Multi-threaded I/O | **Memcached** |

---

## Cluster Architecture

### VPC Deployment

ElastiCache clusters must be deployed within a VPC:

```
┌─────────────────────────────────────────────────────────────┐
│                          VPC                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Private Subnet (AZ-a)                   │   │
│   │   ┌─────────────────────────────────────────────┐   │   │
│   │   │           ElastiCache Subnet Group           │   │   │
│   │   │  ┌──────────┐                               │   │   │
│   │   │  │  Redis   │                               │   │   │
│   │   │  │  Primary │                               │   │   │
│   │   │  └──────────┘                               │   │   │
│   │   └─────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Private Subnet (AZ-b)                   │   │
│   │   ┌─────────────────────────────────────────────┐   │   │
│   │   │           ElastiCache Subnet Group           │   │   │
│   │   │  ┌──────────┐                               │   │   │
│   │   │  │  Redis   │                               │   │   │
│   │   │  │  Replica │                               │   │   │
│   │   │  └──────────┘                               │   │   │
│   │   └─────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Security Group: Allow port 6379 from application SG       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Subnet Groups

- Collection of subnets for cluster deployment
- Must span multiple AZs for Multi-AZ
- Private subnets recommended

### Parameter Groups

Configure cache engine parameters:

```
# Redis Parameter Group Example
maxmemory-policy: allkeys-lru
timeout: 0
tcp-keepalive: 300
activedefrag: yes
```

Common Parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| **maxmemory-policy** | Eviction policy when memory full | volatile-lru |
| **timeout** | Idle connection timeout (seconds) | 0 (no timeout) |
| **tcp-keepalive** | TCP keepalive interval | 300 |
| **reserved-memory-percent** | Memory reserved for non-data | 25% |

### Eviction Policies

| Policy | Description |
|--------|-------------|
| **noeviction** | Return errors when memory limit reached |
| **allkeys-lru** | Evict least recently used keys |
| **allkeys-lfu** | Evict least frequently used keys |
| **volatile-lru** | Evict LRU keys with TTL set |
| **volatile-lfu** | Evict LFU keys with TTL set |
| **volatile-ttl** | Evict keys with shortest TTL |
| **volatile-random** | Evict random keys with TTL set |
| **allkeys-random** | Evict random keys |

---

## Replication and High Availability

### Redis Replication

#### Cluster Mode Disabled
- 1 primary + up to 5 read replicas
- Asynchronous replication
- Automatic failover with Multi-AZ

#### Cluster Mode Enabled
- Multiple shards (up to 500)
- Each shard: 1 primary + up to 5 replicas
- Automatic failover per shard

### Multi-AZ with Automatic Failover

```
┌─────────────────────────────────────────────────────────────┐
│              Multi-AZ Automatic Failover                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Normal Operation:                                          │
│   ┌──────────┐  Replication  ┌──────────┐                  │
│   │  Primary │ ────────────► │  Replica │                  │
│   │  (AZ-a)  │               │  (AZ-b)  │                  │
│   └──────────┘               └──────────┘                  │
│                                                              │
│   After Failover:                                            │
│   ┌──────────┐               ┌──────────┐                  │
│   │  Failed  │               │  Primary │ ◄── Promoted     │
│   │  (AZ-a)  │               │  (AZ-b)  │                  │
│   └──────────┘               └──────────┘                  │
│                                                              │
│   Failover Time: Typically 60-120 seconds                   │
│   DNS Update: Automatic (use primary endpoint)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Failover Triggers

- Primary node failure
- Network issues
- Maintenance events
- Manual failover for testing

### Reader Endpoint

Load balances read traffic across replicas:

```python
# Application code using endpoints
import redis

# Write operations - use primary endpoint
primary = redis.Redis(
    host='my-cluster.xxxxx.ng.0001.use1.cache.amazonaws.com',
    port=6379
)
primary.set('key', 'value')

# Read operations - use reader endpoint
reader = redis.Redis(
    host='my-cluster-ro.xxxxx.ng.0001.use1.cache.amazonaws.com',
    port=6379
)
value = reader.get('key')
```

---

## Caching Strategies

### Lazy Loading (Cache-Aside)

Data loaded into cache only when necessary:

```
┌──────────────────────────────────────────────────────────────┐
│                    Lazy Loading Pattern                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   Cache Hit:                                                  │
│   ┌─────────┐  1.Request  ┌──────────┐                       │
│   │   App   │ ──────────► │  Cache   │                       │
│   └─────────┘ ◄────────── └──────────┘                       │
│               2.Data                                          │
│                                                               │
│   Cache Miss:                                                 │
│   ┌─────────┐  1.Request  ┌──────────┐                       │
│   │   App   │ ──────────► │  Cache   │                       │
│   └─────────┘ ◄────────── └──────────┘                       │
│       │       2.Miss                                         │
│       │                                                       │
│       │ 3.Query  ┌──────────┐                                │
│       └────────► │ Database │                                │
│       ◄────────  └──────────┘                                │
│       4.Data                                                  │
│       │                                                       │
│       │ 5.Store  ┌──────────┐                                │
│       └────────► │  Cache   │                                │
│                  └──────────┘                                │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Only requested data is cached
- Node failures don't break application
- Resilient to cache failures

**Cons:**
- Cache miss = 3 round trips
- Stale data possible
- Initial requests slower

```python
def get_user(user_id):
    # Try cache first
    user = cache.get(f"user:{user_id}")
    
    if user is None:
        # Cache miss - query database
        user = database.query(f"SELECT * FROM users WHERE id = {user_id}")
        
        # Store in cache with TTL
        cache.setex(f"user:{user_id}", 3600, user)
    
    return user
```

### Write-Through

Data written to cache and database simultaneously:

```
┌──────────────────────────────────────────────────────────────┐
│                   Write-Through Pattern                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌─────────┐  1.Write    ┌──────────┐  2.Write  ┌────────┐ │
│   │   App   │ ──────────► │  Cache   │ ────────► │   DB   │ │
│   └─────────┘             └──────────┘           └────────┘ │
│                                                               │
│   Read:                                                       │
│   ┌─────────┐  Request    ┌──────────┐                       │
│   │   App   │ ──────────► │  Cache   │ (Always cache hit)   │
│   └─────────┘ ◄────────── └──────────┘                       │
│               Data                                            │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Data in cache is never stale
- Every write updates cache
- Read operations are fast

**Cons:**
- Write latency is higher
- Cache may contain unused data
- Node failure = data loss until re-written

```python
def update_user(user_id, data):
    # Write to database
    database.update(f"UPDATE users SET ... WHERE id = {user_id}")
    
    # Write to cache
    cache.setex(f"user:{user_id}", 3600, data)
```

### Write-Behind (Write-Back)

Write to cache immediately, sync to database asynchronously:

```
┌──────────────────────────────────────────────────────────────┐
│                   Write-Behind Pattern                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌─────────┐  1.Write    ┌──────────┐                       │
│   │   App   │ ──────────► │  Cache   │                       │
│   └─────────┘  (Fast ACK) └────┬─────┘                       │
│                                │                              │
│                                │ 2.Async                      │
│                                │    Write                     │
│                                ▼                              │
│                           ┌────────┐                         │
│                           │   DB   │                         │
│                           └────────┘                         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Fastest write performance
- Batches writes for efficiency
- Resilient to database issues

**Cons:**
- Data loss risk if cache fails before sync
- Complex implementation
- Eventual consistency

### Adding TTL (Time-To-Live)

Always use TTL to prevent stale data:

```python
# Set with TTL (seconds)
cache.setex('key', 3600, 'value')  # Expires in 1 hour

# Set with TTL (milliseconds)
cache.psetex('key', 3600000, 'value')

# Add TTL to existing key
cache.expire('key', 3600)
```

### Recommended Strategy Combinations

| Use Case | Strategy |
|----------|----------|
| **General caching** | Lazy Loading + TTL |
| **High read frequency** | Write-Through + Lazy Loading |
| **Write-heavy workloads** | Write-Behind |
| **Session storage** | Write-Through + TTL |
| **Real-time data** | Write-Through (no TTL) |

---

## Security

### Encryption in Transit

Enable TLS encryption for data in transit:

```
┌─────────────────────────────────────────────────────────────┐
│                  Encryption in Transit                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────┐    TLS 1.2/1.3    ┌──────────────────────┐   │
│   │   App   │ ◄───────────────► │  ElastiCache Cluster  │   │
│   └─────────┘    Encrypted      └──────────────────────┘   │
│                                                              │
│   • Requires TLS-enabled client                              │
│   • AWS managed certificates                                 │
│   • Minimal performance impact                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Encryption at Rest

Encrypt data stored in memory and backups:

- **AWS Managed Key**: Default KMS key
- **Customer Managed Key**: Your own CMK in KMS
- **Encrypted Backups**: Snapshots encrypted automatically

### Redis AUTH

Password protection for Redis clusters:

```python
import redis

r = redis.Redis(
    host='my-cluster.xxxxx.cache.amazonaws.com',
    port=6379,
    password='my-auth-token',  # AUTH token
    ssl=True  # Enable TLS
)
```

### IAM Authentication (Redis 7.0+)

Use IAM users and roles for authentication:

```python
import redis
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

# IAM-based authentication
credentials = Credentials(access_key, secret_key, token)
# ... generate auth token using SigV4
```

### Security Groups

Control network access to clusters:

```
Inbound Rules:
┌─────────────────┬──────────────┬─────────────────────────┐
│ Type            │ Port         │ Source                  │
├─────────────────┼──────────────┼─────────────────────────┤
│ Custom TCP      │ 6379         │ Application SG          │
│ Custom TCP      │ 6379         │ 10.0.0.0/16 (VPC CIDR) │
└─────────────────┴──────────────┴─────────────────────────┘
```

### Security Best Practices

1. **Deploy in Private Subnets**: No public access
2. **Use Security Groups**: Restrict access to application tier
3. **Enable Encryption**: Both in-transit and at-rest
4. **Use AUTH Tokens**: Password protection for Redis
5. **Rotate AUTH Tokens**: Regular rotation
6. **Enable CloudTrail**: Audit API calls
7. **Use IAM Authentication**: For Redis 7.0+

---

## Monitoring and Performance

### CloudWatch Metrics

#### Key Metrics

| Metric | Description | Alarm Threshold |
|--------|-------------|-----------------|
| **CPUUtilization** | CPU usage percentage | > 90% |
| **EngineCPUUtilization** | Redis engine CPU | > 90% |
| **FreeableMemory** | Available memory | < 10% of total |
| **DatabaseMemoryUsagePercentage** | Memory used by data | > 80% |
| **CacheHits** | Number of cache hits | Monitor trend |
| **CacheMisses** | Number of cache misses | Monitor trend |
| **CurrConnections** | Current connections | Near max connections |
| **Evictions** | Keys evicted due to memory | > 0 (investigate) |
| **ReplicationLag** | Replica lag (seconds) | > 1 second |

#### Cache Hit Ratio

```
Cache Hit Ratio = CacheHits / (CacheHits + CacheMisses)

Target: > 80% (ideally > 95%)
```

### CloudWatch Alarms

```yaml
# Example CloudWatch Alarm
AlarmName: ElastiCache-HighCPU
MetricName: CPUUtilization
Namespace: AWS/ElastiCache
Statistic: Average
Period: 300
EvaluationPeriods: 2
Threshold: 90
ComparisonOperator: GreaterThanThreshold
AlarmActions:
  - arn:aws:sns:us-east-1:123456789:alerts
```

### Slow Log (Redis)

Capture slow queries:

```
# Parameter Group Settings
slowlog-log-slower-than: 10000  # microseconds
slowlog-max-len: 128

# View slow log
SLOWLOG GET 10
```

### Performance Optimization Tips

1. **Connection Pooling**: Reuse connections
2. **Pipelining**: Batch commands
3. **Appropriate Data Structures**: Use optimal types
4. **Key Design**: Short, meaningful keys
5. **TTL Management**: Prevent memory bloat
6. **Monitor Evictions**: Scale before evictions occur

---

## Scaling

### Vertical Scaling (Scale Up/Down)

Change node type for more CPU/memory:

- **Scale Up**: Larger node type
- **Scale Down**: Smaller node type
- **Downtime**: Brief (during maintenance window)

### Horizontal Scaling

#### Redis Cluster Mode Enabled
- **Add Shards**: More write capacity
- **Add Replicas**: More read capacity
- **Online Resharding**: No downtime

```
┌──────────────────────────────────────────────────────────────┐
│                  Horizontal Scaling (Redis)                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   Before:                  After (Add Shard):                │
│   ┌───────┐ ┌───────┐     ┌───────┐ ┌───────┐ ┌───────┐    │
│   │Shard 1│ │Shard 2│     │Shard 1│ │Shard 2│ │Shard 3│    │
│   └───────┘ └───────┘     └───────┘ └───────┘ └───────┘    │
│                                                               │
│   After (Add Replica):                                       │
│   ┌───────┐                                                  │
│   │Primary│                                                  │
│   └───┬───┘                                                  │
│       ├──────────┬──────────┐                               │
│   ┌───┴───┐  ┌───┴───┐  ┌───┴───┐                          │
│   │Replica│  │Replica│  │Replica│  (NEW)                   │
│   └───────┘  └───────┘  └───────┘                          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

#### Memcached
- **Add Nodes**: More capacity
- **Remove Nodes**: Reduce capacity
- **Data Redistribution**: Handled by client

### Auto Scaling (Redis)

Auto scale shards or replicas based on metrics:

```json
{
  "scalableTargetAction": {
    "serviceNamespace": "elasticache",
    "resourceId": "replication-group/my-cluster",
    "scalableDimension": "elasticache:replication-group:NodeGroups"
  },
  "targetTrackingScalingPolicyConfiguration": {
    "targetValue": 75.0,
    "predefinedMetricSpecification": {
      "predefinedMetricType": "ElastiCachePrimaryEngineCPUUtilization"
    }
  }
}
```

---

## Backup and Recovery

### Automatic Backups (Redis Only)

- **Daily Snapshots**: Automatic backup during backup window
- **Retention**: 1-35 days
- **Storage**: S3 (managed by ElastiCache)

### Manual Snapshots

- **On-Demand**: Create anytime
- **No Expiration**: Until manually deleted
- **Copy**: Can copy to other regions

### Backup Best Practices

1. **Enable Automatic Backups**: For production clusters
2. **Set Appropriate Retention**: Based on RPO requirements
3. **Schedule During Low Traffic**: Minimize impact
4. **Test Restores**: Regularly verify backup integrity
5. **Cross-Region Copy**: For disaster recovery

### Restore Process

```
┌──────────────────────────────────────────────────────────────┐
│                     Restore from Backup                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   1. Select Snapshot                                          │
│      └── Automatic or Manual backup                          │
│                                                               │
│   2. Create New Cluster                                       │
│      └── New cluster name required                           │
│      └── Can change node type                                │
│      └── Can change cluster mode                             │
│                                                               │
│   3. Restore Data                                             │
│      └── Data populated from snapshot                        │
│                                                               │
│   4. Update Application                                       │
│      └── Point to new endpoint                               │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Cost Optimization

### Pricing Components

| Component | Pricing Basis |
|-----------|---------------|
| **Node Hours** | Per node per hour |
| **Data Transfer** | Outbound data transfer |
| **Backup Storage** | Storage exceeding free tier |

### Reserved Nodes

Save up to 55% with reserved capacity:

| Term | Payment | Discount |
|------|---------|----------|
| 1 Year | All Upfront | ~31% |
| 1 Year | Partial Upfront | ~29% |
| 1 Year | No Upfront | ~25% |
| 3 Year | All Upfront | ~55% |
| 3 Year | Partial Upfront | ~52% |
| 3 Year | No Upfront | ~47% |

### Cost Optimization Strategies

1. **Right-Size Nodes**: Match node type to workload
2. **Use Reserved Nodes**: For predictable workloads
3. **Reduce Replicas**: If high availability not critical
4. **Data Tiering (Redis)**: Extend memory with SSD
5. **Monitor Usage**: Scale down unused capacity
6. **Use Graviton**: ARM-based nodes for better price/performance

### Data Tiering (Redis 7.x)

Extend memory capacity with SSDs:

- **Hot Data**: In memory (fast access)
- **Warm Data**: On SSD (slightly slower)
- **Cost Savings**: Up to 60% for large datasets
- **Transparent**: Automatic data movement

---

## Best Practices

### Design Best Practices

1. **Key Naming Convention**: Use prefixes (e.g., `user:123:profile`)
2. **Avoid Large Keys**: Keep values under 100 KB
3. **Use TTL**: Prevent memory bloat
4. **Design for Cache Misses**: Application must handle misses
5. **Connection Pooling**: Reuse connections

### Operational Best Practices

1. **Deploy Multi-AZ**: For production workloads
2. **Enable Encryption**: In-transit and at-rest
3. **Use Parameter Groups**: Custom configurations
4. **Monitor Key Metrics**: CPU, memory, hit ratio
5. **Set Up Alarms**: Proactive alerting
6. **Regular Backups**: Enable automatic backups

### Application Best Practices

```python
# Connection pooling example
import redis

pool = redis.ConnectionPool(
    host='my-cluster.xxxxx.cache.amazonaws.com',
    port=6379,
    max_connections=100,
    socket_timeout=5,
    socket_connect_timeout=5
)

r = redis.Redis(connection_pool=pool)

# Use TTL for all keys
r.setex('user:123', 3600, 'data')

# Handle cache failures gracefully
try:
    value = r.get('key')
except redis.RedisError:
    # Fall back to database
    value = database.get('key')
```

---

## Common Use Cases

### 1. Database Caching

Reduce database load by caching query results:

```python
def get_product(product_id):
    cache_key = f"product:{product_id}"
    
    # Try cache
    product = cache.get(cache_key)
    if product:
        return json.loads(product)
    
    # Cache miss - query database
    product = db.query("SELECT * FROM products WHERE id = ?", product_id)
    
    # Store in cache (1 hour TTL)
    cache.setex(cache_key, 3600, json.dumps(product))
    
    return product
```

### 2. Session Management

Store user sessions for web applications:

```python
def create_session(user_id):
    session_id = str(uuid.uuid4())
    session_data = {
        'user_id': user_id,
        'created': datetime.now().isoformat()
    }
    
    # Store session (30 minute TTL)
    cache.setex(f"session:{session_id}", 1800, json.dumps(session_data))
    
    return session_id

def get_session(session_id):
    session = cache.get(f"session:{session_id}")
    if session:
        # Extend TTL on access
        cache.expire(f"session:{session_id}", 1800)
        return json.loads(session)
    return None
```

### 3. Leaderboards (Redis Sorted Sets)

Real-time leaderboards with sorted sets:

```python
# Add/update score
cache.zadd('leaderboard', {'player1': 1000, 'player2': 950})

# Get top 10
top_10 = cache.zrevrange('leaderboard', 0, 9, withscores=True)

# Get player rank
rank = cache.zrevrank('leaderboard', 'player1')
```

### 4. Rate Limiting

Implement API rate limiting:

```python
def is_rate_limited(user_id, limit=100, window=60):
    key = f"rate:{user_id}"
    current = cache.get(key)
    
    if current is None:
        cache.setex(key, window, 1)
        return False
    
    if int(current) >= limit:
        return True
    
    cache.incr(key)
    return False
```

### 5. Real-Time Analytics

Count events in real-time:

```python
# Increment page view counter
cache.hincrby('pageviews:2024-01-15', '/home', 1)

# Get all page views for a day
views = cache.hgetall('pageviews:2024-01-15')
```

---

## SAA-C03 Exam Tips

### Key Concepts to Remember

1. **Redis** = Advanced features, persistence, replication
2. **Memcached** = Simple key-value, multi-threaded, no persistence
3. **Lazy Loading** = Data cached on first request
4. **Write-Through** = Cache always up-to-date
5. **TTL** = Prevents stale data, manages memory

### Common Exam Scenarios

#### Scenario 1: High Availability Caching
**Question**: Need caching with automatic failover and no data loss on node failure.
**Answer**: ElastiCache for Redis with Multi-AZ enabled

#### Scenario 2: Simple Session Storage
**Question**: Store web sessions with simple key-value access, persistence not required.
**Answer**: ElastiCache for Memcached (simplest option)

#### Scenario 3: Leaderboard Implementation
**Question**: Build real-time leaderboard with ranking.
**Answer**: ElastiCache for Redis with Sorted Sets

#### Scenario 4: Database Read Offloading
**Question**: Reduce load on RDS by caching frequent queries.
**Answer**: ElastiCache with Lazy Loading strategy + TTL

#### Scenario 5: Cross-Region Disaster Recovery
**Question**: Need cache data available in multiple regions.
**Answer**: ElastiCache for Redis with Global Datastore

### Default Values to Remember

| Setting | Default |
|---------|---------|
| Redis Port | 6379 |
| Memcached Port | 11211 |
| Max Replicas (Redis) | 5 per shard |
| Max Shards (Cluster Mode) | 500 |
| Backup Retention | 1 day (if enabled) |
| Max Backup Retention | 35 days |
| Parameter Group | default.redis7 or default.memcached1.6 |

### Exam Question Keywords

- "In-memory caching" → **ElastiCache**
- "Complex data structures" → **Redis**
- "Sorted sets/leaderboards" → **Redis**
- "Multi-threaded" → **Memcached**
- "Persistence required" → **Redis**
- "Pub/Sub messaging" → **Redis**
- "Automatic failover" → **Redis Multi-AZ**
- "Session storage (HA)" → **Redis**
- "Simple key-value" → **Memcached**

---

## Practice Questions

### Question 1
A company needs to implement a caching layer for their database-backed web application. The cache must support automatic failover and data persistence. Which solution meets these requirements?

A) ElastiCache for Memcached with Multi-AZ  
B) ElastiCache for Redis with cluster mode disabled and Multi-AZ  
C) ElastiCache for Memcached with multiple nodes  
D) ElastiCache for Redis without Multi-AZ  

**Answer: B** - Redis supports both data persistence and Multi-AZ with automatic failover. Memcached does not support either feature.

### Question 2
A gaming company needs to implement real-time leaderboards where players are ranked by their scores. Which ElastiCache feature is BEST suited for this use case?

A) Redis Strings  
B) Redis Lists  
C) Redis Sorted Sets  
D) Memcached key-value store  

**Answer: C** - Redis Sorted Sets automatically maintain elements sorted by score, perfect for leaderboards.

### Question 3
An application experiences occasional high traffic spikes. Which caching strategy ensures the cache is always populated with the most current data?

A) Lazy Loading  
B) Write-Through  
C) Write-Behind  
D) Cache-Aside only  

**Answer: B** - Write-Through writes to cache on every database write, ensuring cache always has current data.

### Question 4
A company wants to reduce their ElastiCache costs for a production Redis cluster that runs 24/7. Which option provides the HIGHEST cost savings?

A) On-Demand pricing  
B) 1-year Reserved Nodes with No Upfront payment  
C) 3-year Reserved Nodes with All Upfront payment  
D) Spot instances  

**Answer: C** - 3-year All Upfront Reserved Nodes provide the highest discount (up to 55%). Note: ElastiCache does not support Spot pricing.

### Question 5
A web application stores user sessions in ElastiCache. The sessions should expire after 30 minutes of inactivity. How should this be implemented?

A) Use Redis with TTL and extend TTL on each access  
B) Use Memcached with permanent keys  
C) Use Redis without TTL and delete keys manually  
D) Use database instead of cache  

**Answer: A** - Set initial TTL of 30 minutes and extend/reset TTL on each session access using EXPIRE command.

---

## Summary

Amazon ElastiCache provides managed in-memory caching with two engine options:

**Redis**: Feature-rich, persistent, highly available
- Best for: Complex data types, HA requirements, persistence, pub/sub

**Memcached**: Simple, multi-threaded, horizontally scalable
- Best for: Simple key-value, maximum simplicity, multi-threaded workloads

**Key Exam Points**:
1. Redis = Advanced features, Memcached = Simplicity
2. Multi-AZ = Redis only (automatic failover)
3. Persistence = Redis only
4. Lazy Loading + TTL = Most common caching pattern
5. Always use TTL to prevent stale data
