# Chapter 22: Database Administration

## Learning Objectives
By the end of this chapter, you will:
- Configure Neo4j for production
- Perform backup and restore operations
- Monitor database performance
- Manage memory and resources
- Handle maintenance tasks

---

## 22.1 Neo4j Configuration

### Configuration Files

```
neo4j/
├── conf/
│   ├── neo4j.conf          # Main configuration
│   ├── apoc.conf           # APOC settings
│   └── neo4j-admin.conf    # Admin tool settings
├── data/                   # Database files
├── logs/                   # Log files
├── import/                 # CSV import directory
└── plugins/                # Extensions (APOC, GDS)
```

### Essential Settings (neo4j.conf)

```properties
# Memory Configuration
server.memory.heap.initial_size=2g
server.memory.heap.max_size=2g
server.memory.pagecache.size=4g

# Network
server.default_listen_address=0.0.0.0
server.bolt.listen_address=:7687
server.http.listen_address=:7474
server.https.listen_address=:7473

# Default database
initial.dbms.default_database=neo4j

# Directories
server.directories.data=data
server.directories.logs=logs
server.directories.import=import

# Query logging
db.logs.query.enabled=true
db.logs.query.threshold=1000ms
db.logs.query.rotation.size=10M
db.logs.query.rotation.keep_number=10
```

### Memory Sizing Guidelines

```properties
# Rule of thumb for dedicated server:
# - Heap: 50% of RAM (max 31g for compressed pointers)
# - Page Cache: 25-35% of RAM
# - OS/Other: 15-25% of RAM

# Example: 16GB server
server.memory.heap.initial_size=8g
server.memory.heap.max_size=8g
server.memory.pagecache.size=4g

# Example: 64GB server  
server.memory.heap.initial_size=31g
server.memory.heap.max_size=31g
server.memory.pagecache.size=20g
```

---

## 22.2 Backup and Restore

### Online Backup (Enterprise Edition)

```bash
# Full backup
neo4j-admin database backup --database=neo4j --to-path=/backup/

# Backup with compression
neo4j-admin database backup --database=neo4j --to-path=/backup/ --compress

# Incremental backup
neo4j-admin database backup --database=neo4j --to-path=/backup/ --type=incremental

# Backup all databases
neo4j-admin database backup --database=* --to-path=/backup/
```

### Offline Backup (Community Edition)

```bash
# Stop Neo4j first
neo4j stop

# Copy data directory
cp -r /var/lib/neo4j/data/databases/neo4j /backup/neo4j-backup-$(date +%Y%m%d)

# Or use dump
neo4j-admin database dump --database=neo4j --to-path=/backup/neo4j.dump

# Start Neo4j
neo4j start
```

### Restore Operations

```bash
# Restore from dump (stop database first)
neo4j stop

# Restore
neo4j-admin database load --database=neo4j --from-path=/backup/neo4j.dump --overwrite-destination=true

# Restore from backup
neo4j-admin database restore --database=neo4j --from-path=/backup/neo4j-backup

neo4j start
```

### Automated Backup Script

```bash
#!/bin/bash
# backup-neo4j.sh

BACKUP_DIR="/backup/neo4j"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup
neo4j-admin database backup \
    --database=neo4j \
    --to-path="$BACKUP_DIR/$DATE" \
    --compress

# Remove old backups
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;

# Log result
echo "$(date): Backup completed to $BACKUP_DIR/$DATE" >> /var/log/neo4j-backup.log
```

---

## 22.3 Monitoring

### Built-in Monitoring Queries

```cypher
// Database information
CALL dbms.listDatabases()
YIELD name, currentStatus, requestedStatus, error
RETURN name, currentStatus, requestedStatus, error

// Store size
CALL apoc.monitor.store()
YIELD logSize, stringStoreSize, nodeStoreSize, relStoreSize, propStoreSize, totalStoreSize
RETURN *

// Transaction information
CALL dbms.listTransactions()
YIELD transactionId, username, currentQuery, elapsedTime, status
RETURN transactionId, username, currentQuery, elapsedTime, status
ORDER BY elapsedTime DESC

// Current connections
CALL dbms.listConnections()
YIELD connectionId, connectTime, connector, username, clientAddress
RETURN *

// Running queries
CALL dbms.listQueries()
YIELD queryId, username, query, elapsedTimeMillis, allocatedBytes
WHERE elapsedTimeMillis > 1000
RETURN queryId, username, query, elapsedTimeMillis
```

### Memory Monitoring

```cypher
// JVM memory
CALL dbms.queryJmx('java.lang:type=Memory')
YIELD attributes
RETURN attributes.HeapMemoryUsage, attributes.NonHeapMemoryUsage

// Page cache
CALL dbms.queryJmx('org.neo4j:*')
YIELD name, attributes
WHERE name CONTAINS 'PageCache'
RETURN name, attributes
```

### Performance Metrics

```cypher
// Query statistics (requires configuration)
CALL db.stats.retrieve('QUERIES')
YIELD data
RETURN data

// Index statistics
CALL db.stats.retrieve('INDEX USAGE')
YIELD data
RETURN data

// Store files
CALL db.stats.retrieve('STORE')
YIELD data
RETURN data
```

### Logs

```bash
# View debug log
tail -f /var/log/neo4j/debug.log

# View query log
tail -f /var/log/neo4j/query.log

# View security log
tail -f /var/log/neo4j/security.log
```

---

## 22.4 Index and Constraint Management

### Index Maintenance

```cypher
// List all indexes
SHOW INDEXES
YIELD name, type, labelsOrTypes, properties, state, populationPercent
RETURN name, type, labelsOrTypes, properties, state, populationPercent

// Check index status
SHOW INDEXES WHERE state <> 'ONLINE'

// Wait for indexes to come online
CALL db.awaitIndexes(300)  // Wait up to 300 seconds

// Drop unused indexes
// First, check usage
SELECT * FROM db.stats.retrieve('INDEX USAGE')

// Then drop
DROP INDEX index_name IF EXISTS

// Rebuild index (drop and recreate)
DROP INDEX idx_person_email IF EXISTS;
CREATE INDEX idx_person_email FOR (p:Person) ON (p.email);
```

### Constraint Management

```cypher
// Show all constraints
SHOW CONSTRAINTS

// Add constraint (creates implicit index)
CREATE CONSTRAINT user_email_unique FOR (u:User) REQUIRE u.email IS UNIQUE

// Drop constraint
DROP CONSTRAINT user_email_unique IF EXISTS
```

---

## 22.5 Database Maintenance

### Clearing Data

```cypher
// Delete all data (small datasets)
MATCH (n) DETACH DELETE n

// Delete in batches (large datasets)
CALL apoc.periodic.iterate(
    "MATCH (n) RETURN n",
    "DETACH DELETE n",
    {batchSize: 10000}
)

// Delete specific label
CALL apoc.periodic.iterate(
    "MATCH (n:TempData) RETURN n",
    "DETACH DELETE n",
    {batchSize: 10000}
)
```

### Checking Data Integrity

```cypher
// Find orphaned relationships (shouldn't exist)
MATCH ()-[r]->()
WHERE NOT EXISTS { MATCH (startNode(r)) }
   OR NOT EXISTS { MATCH (endNode(r)) }
RETURN r

// Find duplicate nodes
MATCH (n:User)
WITH n.email AS email, collect(n) AS nodes
WHERE size(nodes) > 1
RETURN email, size(nodes) AS count

// Check for required properties
MATCH (u:User)
WHERE u.email IS NULL OR u.name IS NULL
RETURN u.id, labels(u)
```

### Store Optimization

```bash
# Compact store files (offline operation)
neo4j stop
neo4j-admin database copy --from-database=neo4j --to-database=neo4j-compacted
neo4j start
```

---

## 22.6 Managing Multiple Databases

### Database Operations

```cypher
// Create new database
CREATE DATABASE customers

// Show databases
SHOW DATABASES

// Switch database
:use customers

// Start/Stop database
STOP DATABASE customers
START DATABASE customers

// Drop database
DROP DATABASE customers IF EXISTS
```

### Cross-Database Queries (Enterprise)

```cypher
// Query across databases using Fabric
USE fabric.graph
MATCH (c:Customer)
CALL {
    USE neo4j.customers
    MATCH (o:Order)
    RETURN count(o) AS orderCount
}
RETURN c.name, orderCount
```

---

## 22.7 Performance Tuning

### Query Tuning

```cypher
// Enable query logging for slow queries
// In neo4j.conf:
// db.logs.query.enabled=true
// db.logs.query.threshold=1000ms

// Use PROFILE to analyze
PROFILE MATCH (p:Person)-[:KNOWS*2..4]->(friend)
WHERE p.name = 'Alice'
RETURN friend.name

// Check for missing indexes
EXPLAIN MATCH (p:Person) WHERE p.email = 'test@test.com' RETURN p
// Look for NodeByLabelScan instead of NodeIndexSeek
```

### Connection Pool Settings

```properties
# In neo4j.conf
# Maximum concurrent connections
dbms.connector.bolt.connection_keep_alive_for_requests=STRICT
dbms.connector.bolt.connection_keep_alive=300s
dbms.connector.bolt.connection_keep_alive_streaming_scheduling_interval=1m

# Thread pool
dbms.threads.worker_count=100
```

### Garbage Collection Tuning

```properties
# In neo4j.conf or JAVA_OPTS
# G1GC settings (recommended)
server.jvm.additional=-XX:+UseG1GC
server.jvm.additional=-XX:MaxGCPauseMillis=200
server.jvm.additional=-XX:+ParallelRefProcEnabled
server.jvm.additional=-XX:+ExplicitGCInvokesConcurrent
```

---

## 22.8 High Availability (Enterprise)

### Cluster Configuration

```properties
# Primary (neo4j.conf)
server.cluster.advertised_address=primary:6000
server.cluster.raft.advertised_address=primary:7000
server.discovery.advertised_address=primary:5000
initial.server.mode_constraint=PRIMARY

# Secondary (neo4j.conf)
server.cluster.advertised_address=secondary1:6000
server.cluster.raft.advertised_address=secondary1:7000
server.discovery.advertised_address=secondary1:5000
initial.dbms.cluster.discovery.endpoints=primary:5000,secondary1:5000,secondary2:5000
```

### Cluster Monitoring

```cypher
// Show cluster status
CALL dbms.cluster.overview()
YIELD id, addresses, databases, groups
RETURN *

// Show routing table
CALL dbms.routing.getRoutingTable({}, 'neo4j')
YIELD ttl, servers
RETURN *
```

---

## 22.9 Python Administration Scripts

```python
from neo4j import GraphDatabase
from datetime import datetime
import json

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class Neo4jAdmin:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def get_database_status(self):
        """Get status of all databases."""
        with self.driver.session(database="system") as session:
            result = session.run("""
                SHOW DATABASES
                YIELD name, currentStatus, requestedStatus
                RETURN name, currentStatus, requestedStatus
            """)
            return [dict(r) for r in result]
    
    def get_store_sizes(self):
        """Get database store sizes."""
        with self.driver.session() as session:
            result = session.run("CALL apoc.monitor.store()")
            return dict(result.single())
    
    def get_slow_queries(self, threshold_ms: int = 1000):
        """Get currently running slow queries."""
        with self.driver.session(database="system") as session:
            result = session.run("""
                CALL dbms.listQueries()
                YIELD queryId, username, query, elapsedTimeMillis
                WHERE elapsedTimeMillis > $threshold
                RETURN queryId, username, query, elapsedTimeMillis
                ORDER BY elapsedTimeMillis DESC
            """, threshold=threshold_ms)
            return [dict(r) for r in result]
    
    def kill_query(self, query_id: str):
        """Kill a running query."""
        with self.driver.session(database="system") as session:
            session.run("CALL dbms.killQuery($queryId)", queryId=query_id)
    
    def get_index_status(self):
        """Get status of all indexes."""
        with self.driver.session() as session:
            result = session.run("""
                SHOW INDEXES
                YIELD name, type, labelsOrTypes, properties, state, populationPercent
                RETURN name, type, labelsOrTypes, properties, state, populationPercent
            """)
            return [dict(r) for r in result]
    
    def get_constraint_status(self):
        """Get all constraints."""
        with self.driver.session() as session:
            result = session.run("""
                SHOW CONSTRAINTS
                YIELD name, type, entityType, labelsOrTypes, properties
                RETURN name, type, entityType, labelsOrTypes, properties
            """)
            return [dict(r) for r in result]
    
    def analyze_database_health(self):
        """Comprehensive health check."""
        health = {
            'timestamp': datetime.now().isoformat(),
            'databases': self.get_database_status(),
            'indexes': self.get_index_status(),
            'constraints': self.get_constraint_status(),
            'slow_queries': self.get_slow_queries()
        }
        
        # Check for issues
        issues = []
        
        for idx in health['indexes']:
            if idx['state'] != 'ONLINE':
                issues.append(f"Index {idx['name']} is {idx['state']}")
        
        for db in health['databases']:
            if db['currentStatus'] != 'online':
                issues.append(f"Database {db['name']} is {db['currentStatus']}")
        
        if health['slow_queries']:
            issues.append(f"{len(health['slow_queries'])} slow queries running")
        
        health['issues'] = issues
        health['healthy'] = len(issues) == 0
        
        return health
    
    def cleanup_old_data(self, label: str, date_property: str, days_old: int):
        """Delete nodes older than specified days."""
        with self.driver.session() as session:
            result = session.run("""
                CALL apoc.periodic.iterate(
                    "MATCH (n:$label) 
                     WHERE n[$prop] < datetime() - duration('P' + $days + 'D')
                     RETURN n",
                    "DETACH DELETE n",
                    {batchSize: 10000, params: {label: $label, prop: $prop, days: $days}}
                )
                YIELD batches, total, timeTaken
                RETURN batches, total, timeTaken
            """.replace('$label', label), 
                prop=date_property, days=str(days_old), label=label)
            return dict(result.single())

# Usage
admin = Neo4jAdmin(URI, AUTH)
try:
    # Health check
    health = admin.analyze_database_health()
    print(json.dumps(health, indent=2))
    
    if not health['healthy']:
        print("Issues found:")
        for issue in health['issues']:
            print(f"  - {issue}")
    
    # Kill slow queries
    for query in health['slow_queries']:
        if query['elapsedTimeMillis'] > 60000:  # > 1 minute
            admin.kill_query(query['queryId'])
            print(f"Killed query: {query['queryId']}")
    
finally:
    admin.close()
```

---

## Summary

### Key Administration Tasks

| Task | Command/Procedure |
|------|-------------------|
| Backup | `neo4j-admin database backup` |
| Restore | `neo4j-admin database load` |
| Show Databases | `SHOW DATABASES` |
| List Queries | `CALL dbms.listQueries()` |
| Kill Query | `CALL dbms.killQuery($id)` |
| Index Status | `SHOW INDEXES` |
| Wait for Indexes | `CALL db.awaitIndexes()` |

### Configuration Priorities

1. **Memory**: Heap and page cache sizing
2. **Logging**: Query logging for slow query identification
3. **Security**: Authentication and authorization
4. **Backup**: Regular automated backups

---

## Exercises

### Exercise 22.1: Backup Strategy
1. Create a backup script for your database
2. Set up automated daily backups
3. Test restore procedure

### Exercise 22.2: Monitoring Dashboard
1. Write queries to collect key metrics
2. Create a Python script for health checks
3. Set up alerting for issues

### Exercise 22.3: Performance Analysis
1. Enable query logging
2. Identify slow queries
3. Optimize with indexes and query changes

---

**Next Chapter: [Chapter 23: Security](23-security.md)**
