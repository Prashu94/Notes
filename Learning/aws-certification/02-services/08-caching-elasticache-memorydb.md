# Caching: ElastiCache and MemoryDB

SAA 3.3 and 4.3. SAP 2.5. DVA 1.3.8 and 4.3.6.

Official:

- https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.html
- https://docs.aws.amazon.com/memorydb/latest/devguide/what-is-memorydb.html
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.html

## Where a cache sits

| Layer | What it saves | Trap |
| --- | --- | --- |
| CloudFront | Bytes at the edge for many users | Personalized responses cached on a shared key |
| API Gateway REST cache | The method response | Same trap, closer to the origin |
| Application memory | One process's hot set | Lost on scale-out and on every new Lambda environment. Fine for a 5-second TTL |
| ElastiCache | A shared hot set across a fleet | A cache is not a system of record unless you deliberately chose MemoryDB |
| DAX | DynamoDB reads | Only DynamoDB. Not a general Redis |
| RDS read replica | SQL reads that must be current-ish and relational | A replica is not a cache of a single key. It is another database |

Use a cache when the same read happens often, the origin is expensive, and a bounded staleness is acceptable. Do not put the only copy of a checkout in a cache node.

## Redis OSS, Valkey, and Memcached

ElastiCache runs Redis OSS, Valkey, and Memcached. Valkey is the open Redis-compatible engine AWS has been steering new designs toward. On the exam you will still see the word Redis. Treat Valkey as the Redis-compatible answer when both appear and the stem does not pin a version.

| | Redis OSS / Valkey | Memcached |
| --- | --- | --- |
| Data structures | Strings, lists, sets, sorted sets, hashes, streams | Strings |
| Replication | Yes | No |
| Multi-AZ failover | Yes | No. You add nodes and the client rehashes |
| Persistence | Optional snapshots and AOF, still not MemoryDB | No |
| Threading | Command processing has historically been single-threaded per shard. Cluster mode scales out | Multi-threaded |
| Stem | Leaderboards, sessions with failover, pub/sub, locks | A simple cache that can grow by adding nodes, and a lost node is only a cache miss |

Cluster mode shards data. The client must be cluster-aware. Online resharding is the scale path. A single shard that fills up is a vertical scale until you enable cluster mode.

## Patterns

| Pattern | How |
| --- | --- |
| Cache-aside | The app reads the cache, on miss reads the database, then writes the cache. The common pattern |
| Write-through | The app writes the cache and the database together. More consistent, more write latency |
| TTL | Every cache entry expires. The safety net for a missed invalidation |
| Invalidation | On write, delete the key. Hard when many keys represent one row |
| Thundering herd | A popular key expires and every app hits the database. A lock or a short stale-while-revalidate prevents it |
| Session store | The session id is the key. The fleet is stateless. Sticky sessions go away |

Security: a subnet with no route to the internet, a security group that allows the app SG on 6379 (Redis) or 11211 (Memcached), encryption in transit, AUTH or RBAC on Redis, and no public endpoint. Redis without AUTH in a subnet that a compromised app can scan is a known incident shape.

## MemoryDB

Redis-compatible, Multi-AZ, and a transaction log so the data is durable. Use it when the stem says the in-memory store is the database, not a cache in front of one. ElastiCache with a snapshot is not the same durability story. Failover and a recent snapshot can still lose the last seconds. MemoryDB is the answer for that sentence.

## DAX

A DynamoDB write-through cache cluster. Microsecond reads. The application uses the DAX client. Item cache and query cache. Strongly consistent reads bypass DAX or you accept that a read-your-write may be stale. DAX is not a second database and it does not help a write-heavy hot key. A hot key is a data-model problem.

## Exercises

1. A leaderboard updates continuously and must survive a node failure. Memcached or Redis?
2. Sessions are stored on the EC2 instance. An ASG scale-in logs people out. Where do you move the session, and what do you turn off on the ALB?
3. The cache is empty after a deployment and the database saturates. Name the failure mode and one mitigation.
4. The stem says "Redis API, and a node loss must not lose acknowledged writes." ElastiCache or MemoryDB?
5. A DynamoDB table's GetItem p99 is fine except for one popular product page. DAX or a GSI?

## Answers

1. Redis (or Valkey) with Multi-AZ replication. Memcached will not fail the node over with the data.
2. ElastiCache or DynamoDB (or MemoryDB if the session is the record). Disable sticky sessions once the session is no longer on the instance.
3. A thundering herd, also called a cache stampede. Mitigate with a mutex around the reload, jittered TTLs so keys do not expire together, or serving a slightly stale value while one worker refreshes.
4. MemoryDB. ElastiCache is a cache with optional snapshots. The stem made durability a requirement.
5. DAX, or an application cache of that one key. A GSI does not make one popular item faster. It makes a different query possible. If the hot key is a single item, caching is the tool. If the key is hot because every user writes the same partition, fix the key.

## Which engine, in the words the stem uses

| Stem | Engine | Why the neighbor loses |
| --- | --- | --- |
| Simple cache, horizontal shards, a node can disappear and the data can be reloaded | Memcached | No replication, no sorted sets, no persistence story |
| Leaderboard, pub/sub, locks, sessions, a replica | Redis OSS or Valkey, with Multi-AZ | Memcached cannot fail a node over and keep the data |
| The in-memory data is the system of record | MemoryDB | ElastiCache snapshots still lose the last writes |
| DynamoDB GetItem is hot | DAX | ElastiCache means you write the cache logic. DAX is the DynamoDB client swap. DAX does not fix a hot write key |
| SQL query is hot and repeated | ElastiCache in front of RDS or Aurora, cache-aside | A read replica if the queries vary and are not cacheable. Multi-AZ if the problem is failover rather than read rate |

Valkey is the open-source Redis-compatible engine ElastiCache offers alongside Redis OSS. On the exam, "Redis" and "Valkey" answer the same design sentence unless the stem names a specific engine feature. Do not pick Memcached because it was cheaper if the stem required replication.

Cluster mode on Redis shards the keyspace. A single-shard replication group is a primary and replicas. Cluster mode is how you grow past one shard's memory and write rate. A hot key is still one shard even in cluster mode. The fix is the key, not another node that does not own that slot.

## Cache-aside is the default, and it fails in specific ways

The application reads the cache. On a miss it reads the database and writes the cache with a TTL. On a database write it deletes the key, or updates it. The TTL is what saves you when the delete was missed. A cache with no TTL and a missed invalidation serves wrong data until someone restarts the cluster.

Write-through writes the cache and the database in one path. Reads are more likely to hit. The write is slower, and a crash between the two writes is a consistency bug you still have to name. Write-behind (write to the cache, flush to the database later) loses acknowledged data if the cache dies before the flush. That is the pattern MemoryDB exists to refuse.

Thundering herd: a popular key expires, every application server misses, every server queries the database, the database falls over, which is the outage the cache was supposed to prevent. Mitigations are jitter on the TTL so keys do not expire together, a lock so one worker reloads, or serving a stale value while one worker refreshes. "Add a bigger database" is the Domain 3 answer that ignores the stampede. "Add a bigger cache" does not help in the second after expiry.

Stampede after a deploy is the same shape: a new fleet with an empty cache. Warm the cache, or stagger the deploy, or accept a reader in front of the database sized for the miss.

Sessions. The session id is the key. The instance disk is not. Sticky sessions on the ALB hide the bug until scale-in or a deploy kills the instance the user was pinned to. Turn sticky sessions off after the session store exists. DynamoDB is also a fine session store when you do not want another cluster. ElastiCache is the answer when the session is read on every request and the latency budget is sub-millisecond.

## Network and security

The cluster sits in private subnets, at least two AZs for a Multi-AZ Redis or Valkey replication group. The security group allows 6379 from the application security group only, or 11211 for Memcached. There is no internet route and no public endpoint. Encryption in transit, and at rest with a KMS key when they asked for a key policy. Redis AUTH or RBAC so a process that can open a TCP connection still cannot read every key. A compromised application in the same subnet without AUTH is a full dump of sessions.

A Lambda function that uses the cache must be in the VPC, in subnets that can reach the cache subnets, with the security group allowed. That VPC attachment is why the function then needs endpoints or a NAT for Secrets Manager and S3. Do not put the cache on a public subnet to make Lambda's life easier.

## What a cache is not

It is not the only copy, unless the product is MemoryDB and the stem said so. A design that cannot serve a request when ElastiCache is down has made the cache a database and then chosen the wrong durability. The miss path has to work, slower. Health checks should not require the cache to be up if the database can answer, or a cache blip drains the fleet.

It does not make a hot DynamoDB partition key writable. DAX caches reads. Writes still land on the partition. It does not replace a read replica for arbitrary SQL. It replaces the repeated query you chose to cache.

## More exercises

6. Redis cluster mode is on. One product id receives 90 percent of writes. Adding shards does not drop the throttle. Why?
7. The application writes the cache and returns 200, then writes the database asynchronously. The cache node fails. What did the user get that the database does not have?
8. Sticky sessions are on, and the session is also in ElastiCache. What do you turn off, and what bug returns if you turn it off before the session store is actually used?
9. Memcached is proposed for a distributed lock around the cache reload. Why is that the wrong engine?
10. DAX is in front of DynamoDB. The code uses a strongly consistent read because the next step depends on the write. What does DAX do with that read?

## Answers

6. The hot key hashes to one slot, and one slot lives on one shard. More shards move other keys. They do not split one key. Change the key so writes spread, or stop writing that key on every request.
7. An acknowledgement of data that was only in memory. That is write-behind. The stem that cannot lose acknowledged writes wants the database write to commit first, or MemoryDB if the in-memory store itself must be the durable log.
8. Turn off sticky sessions. If the application still reads the session from local memory, turning stickiness off sends the user to an instance with no session. Confirm the read path uses ElastiCache first.
9. Memcached has no atomic lock primitive of the Redis `SET NX` kind, and it will not keep the lock across a node failure in a way you can reason about. Use Redis or Valkey for the lock, with an expiry so a crashed worker does not hold it forever.
10. Strongly consistent reads are served from DynamoDB, not from the cache, or you must accept that the DAX response can be stale. If the next step depends on the write, do not read it from DAX. Read it from DynamoDB with a consistent read.
