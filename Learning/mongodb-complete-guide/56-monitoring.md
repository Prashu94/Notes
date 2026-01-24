# Chapter 56: Monitoring

## Table of Contents
- [Monitoring Overview](#monitoring-overview)
- [MongoDB Built-in Tools](#mongodb-built-in-tools)
- [serverStatus and dbStats](#serverstatus-and-dbstats)
- [Profiling](#profiling)
- [Log Analysis](#log-analysis)
- [External Monitoring Tools](#external-monitoring-tools)
- [Alerting Strategies](#alerting-strategies)
- [Summary](#summary)

---

## Monitoring Overview

### Why Monitor MongoDB

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Monitoring Objectives                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Performance                                                        │
│  ├── Query response times                                          │
│  ├── Operation throughput                                          │
│  ├── Index efficiency                                              │
│  └── Resource utilization                                          │
│                                                                     │
│  Availability                                                       │
│  ├── Node health                                                   │
│  ├── Replica set status                                            │
│  ├── Failover detection                                            │
│  └── Connection availability                                       │
│                                                                     │
│  Capacity                                                          │
│  ├── Disk usage and growth                                         │
│  ├── Memory utilization                                            │
│  ├── Connection count                                              │
│  └── Oplog window                                                  │
│                                                                     │
│  Security                                                          │
│  ├── Authentication failures                                       │
│  ├── Authorization denials                                         │
│  └── Unusual activity patterns                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Metrics

| Category | Metric | Normal Range |
|----------|--------|--------------|
| Operations | ops/sec | Depends on workload |
| Latency | avg query time | < 100ms |
| Connections | current | < 80% of max |
| Memory | resident | < available RAM |
| Storage | disk usage | < 80% |
| Replication | lag | < 10 seconds |

---

## MongoDB Built-in Tools

### mongostat

```bash
# Basic usage
mongostat

# With authentication
mongostat --username admin --authenticationDatabase admin

# Connect to replica set
mongostat --host rs0/primary:27017,secondary:27017

# Custom interval (2 seconds)
mongostat 2

# Output specific fields
mongostat --rowcount 10
```

```
# Sample output
insert query update delete getmore command dirty used flushes vsize   res qrw arw net_in net_out conn                time
   *0    *0     *0     *0       0     2|0  0.0% 0.0%       0 1.50G 75.0M 0|0 1|0   159b   63.1k    5 Jan 15 10:30:01.234
   *0   100     10     *0       5     5|0  0.1% 0.2%       0 1.50G 76.0M 0|0 0|0  10.5k   25.3k   10 Jan 15 10:30:03.234
```

### mongostat Columns

| Column | Description |
|--------|-------------|
| insert | Inserts per second |
| query | Queries per second |
| update | Updates per second |
| delete | Deletes per second |
| getmore | Cursor fetches per second |
| command | Commands per second |
| dirty | Percentage of dirty cache |
| used | Percentage of cache in use |
| flushes | Flushes to disk per interval |
| vsize | Virtual memory size |
| res | Resident memory |
| qrw | Queue read/write |
| arw | Active read/write |
| net_in | Network bytes in |
| net_out | Network bytes out |
| conn | Connections |

### mongotop

```bash
# Basic usage
mongotop

# With 5 second interval
mongotop 5

# Show specific number of results
mongotop --rowcount 20

# Lock mode (show lock statistics)
mongotop --locks
```

```
# Sample output
                    ns    total    read    write    2024-01-15T10:30:00Z
    mydb.users          102ms    55ms     47ms
    mydb.orders         85ms     30ms     55ms
    admin.system.roles  10ms     10ms      0ms
```

### currentOp

```javascript
// View all current operations
db.currentOp()

// View only active operations
db.currentOp({ active: true })

// View operations running longer than 5 seconds
db.currentOp({
  active: true,
  secs_running: { $gt: 5 }
})

// View operations on specific database
db.currentOp({
  ns: /^mydb\./
})

// View write operations only
db.currentOp({
  op: { $in: ['insert', 'update', 'delete'] }
})

// Kill a specific operation
db.killOp(12345)  // opid
```

### currentOp Output Analysis

```javascript
// Sample currentOp entry
{
  "opid": 12345,
  "active": true,
  "secs_running": 10,
  "microsecs_running": NumberLong(10000000),
  "op": "query",
  "ns": "mydb.users",
  "command": {
    "find": "users",
    "filter": { "status": "active" }
  },
  "client": "192.168.1.100:45678",
  "appName": "MyApp",
  "waitingForLock": false,
  "numYields": 100,
  "planSummary": "COLLSCAN"  // Red flag!
}
```

---

## serverStatus and dbStats

### serverStatus

```javascript
// Full server status
db.serverStatus()

// Specific sections
db.serverStatus().connections
db.serverStatus().network
db.serverStatus().opcounters
db.serverStatus().mem
db.serverStatus().wiredTiger
```

### Key serverStatus Sections

```javascript
// Connections
db.serverStatus().connections
// {
//   "current": 50,        // Current connections
//   "available": 51150,   // Available connections
//   "totalCreated": 1000  // Total connections created
// }

// Operations counter
db.serverStatus().opcounters
// {
//   "insert": 1000,
//   "query": 5000,
//   "update": 2000,
//   "delete": 500,
//   "getmore": 100,
//   "command": 3000
// }

// Memory
db.serverStatus().mem
// {
//   "bits": 64,
//   "resident": 100,      // MB
//   "virtual": 1500       // MB
// }

// Replication (replica sets)
db.serverStatus().repl
// {
//   "setName": "rs0",
//   "ismaster": true,
//   "secondary": false,
//   "hosts": ["primary:27017", "secondary1:27017", "secondary2:27017"]
// }
```

### WiredTiger Statistics

```javascript
// WiredTiger cache statistics
const wt = db.serverStatus().wiredTiger

// Cache usage
wt.cache
// {
//   "bytes currently in the cache": 1073741824,
//   "bytes read into cache": 500000000,
//   "bytes written from cache": 200000000,
//   "maximum bytes configured": 2147483648,
//   "tracked dirty bytes in the cache": 1000000,
//   "pages evicted": 10000
// }

// Concurrency
wt.concurrentTransactions
// {
//   "write": { "out": 5, "available": 123, "totalTickets": 128 },
//   "read": { "out": 10, "available": 118, "totalTickets": 128 }
// }
```

### dbStats

```javascript
// Database statistics
db.stats()

// Result
{
  "db": "mydb",
  "collections": 10,
  "views": 2,
  "objects": 1000000,           // Total documents
  "avgObjSize": 500,            // Bytes
  "dataSize": 500000000,        // Total data size
  "storageSize": 200000000,     // Storage size (compressed)
  "indexes": 25,
  "indexSize": 50000000,
  "totalSize": 250000000,
  "scaleFactor": 1,
  "ok": 1
}

// Scaled to MB
db.stats(1024 * 1024)
```

### collStats

```javascript
// Collection statistics
db.users.stats()

// Result
{
  "ns": "mydb.users",
  "count": 100000,
  "size": 50000000,
  "avgObjSize": 500,
  "storageSize": 20000000,
  "nindexes": 5,
  "indexSizes": {
    "_id_": 1000000,
    "email_1": 2000000,
    "status_1_createdAt_-1": 3000000
  },
  "totalSize": 26000000,
  "scaleFactor": 1
}
```

---

## Profiling

### Enable Profiling

```javascript
// Profiling levels:
// 0 = Off
// 1 = Slow operations only
// 2 = All operations

// Enable profiling for slow operations (>100ms)
db.setProfilingLevel(1, { slowms: 100 })

// Enable profiling for all operations
db.setProfilingLevel(2)

// Disable profiling
db.setProfilingLevel(0)

// Check current level
db.getProfilingStatus()
```

### Query system.profile

```javascript
// View recent slow queries
db.system.profile.find().sort({ ts: -1 }).limit(10)

// Find queries taking > 1 second
db.system.profile.find({
  millis: { $gt: 1000 }
})

// Find collection scans
db.system.profile.find({
  planSummary: "COLLSCAN"
})

// Find queries with no index
db.system.profile.find({
  "nscannedObjects": { $gt: 1000 },
  "nreturned": { $lt: 10 }
})

// Aggregate by collection
db.system.profile.aggregate([
  { $group: {
    _id: "$ns",
    count: { $sum: 1 },
    avgMillis: { $avg: "$millis" },
    maxMillis: { $max: "$millis" }
  }},
  { $sort: { avgMillis: -1 }}
])
```

### Profile Entry Analysis

```javascript
// Sample profile entry
{
  "op": "query",
  "ns": "mydb.users",
  "command": {
    "find": "users",
    "filter": { "email": "user@example.com" }
  },
  "keysExamined": 1,        // Index keys examined
  "docsExamined": 1,        // Documents examined
  "nreturned": 1,           // Documents returned
  "millis": 5,              // Execution time
  "planSummary": "IXSCAN { email: 1 }",
  "ts": ISODate("2024-01-15T10:30:00.000Z")
}

// Red flags:
// - docsExamined >> nreturned (inefficient)
// - planSummary: "COLLSCAN" (no index)
// - millis > 100 (slow query)
```

---

## Log Analysis

### Log Configuration

```yaml
# mongod.conf
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  logRotate: rename  # or 'reopen' for external rotation

# Log verbosity
systemLog:
  verbosity: 0  # 0-5, higher = more verbose
  component:
    accessControl:
      verbosity: 1
    command:
      verbosity: 1
    query:
      verbosity: 2
```

### Log Verbosity Levels

| Level | Description |
|-------|-------------|
| 0 | Informational (default) |
| 1 | Debug level 1 |
| 2 | Debug level 2 |
| 3 | Debug level 3 |
| 4 | Debug level 4 |
| 5 | Debug level 5 (most verbose) |

### Set Log Verbosity Dynamically

```javascript
// Set global verbosity
db.setLogLevel(1)

// Set component-specific verbosity
db.setLogLevel(2, "query")
db.setLogLevel(1, "replication")

// Get current log verbosity
db.getLogComponents()
```

### Common Log Messages

```bash
# Connection events
grep "connection accepted" /var/log/mongodb/mongod.log
grep "end connection" /var/log/mongodb/mongod.log

# Slow queries
grep "Slow query" /var/log/mongodb/mongod.log

# Replica set events
grep "transition to PRIMARY" /var/log/mongodb/mongod.log
grep "transition to SECONDARY" /var/log/mongodb/mongod.log

# Index builds
grep "Index Build" /var/log/mongodb/mongod.log

# Errors
grep -i "error\|exception" /var/log/mongodb/mongod.log
```

### Log Parsing Script

```python
#!/usr/bin/env python3
"""
MongoDB log analyzer
"""

import json
import re
from collections import defaultdict
from datetime import datetime

def parse_log_line(line):
    """Parse a MongoDB log line (JSON format)"""
    try:
        return json.loads(line)
    except:
        return None

def analyze_logs(log_file):
    stats = {
        'slow_queries': [],
        'errors': [],
        'connections': {'opened': 0, 'closed': 0},
        'operations': defaultdict(int)
    }
    
    with open(log_file, 'r') as f:
        for line in f:
            entry = parse_log_line(line)
            if not entry:
                continue
            
            msg = entry.get('msg', '')
            attr = entry.get('attr', {})
            
            # Track slow queries
            if 'Slow query' in msg:
                stats['slow_queries'].append({
                    'ns': attr.get('ns'),
                    'millis': attr.get('durationMillis'),
                    'command': attr.get('command')
                })
            
            # Track errors
            if entry.get('s') == 'E':
                stats['errors'].append({
                    'time': entry.get('t'),
                    'msg': msg
                })
            
            # Track connections
            if 'connection accepted' in msg:
                stats['connections']['opened'] += 1
            elif 'end connection' in msg:
                stats['connections']['closed'] += 1
    
    return stats

if __name__ == '__main__':
    import sys
    log_file = sys.argv[1] if len(sys.argv) > 1 else '/var/log/mongodb/mongod.log'
    stats = analyze_logs(log_file)
    
    print(f"Slow Queries: {len(stats['slow_queries'])}")
    print(f"Errors: {len(stats['errors'])}")
    print(f"Connections Opened: {stats['connections']['opened']}")
    print(f"Connections Closed: {stats['connections']['closed']}")
```

---

## External Monitoring Tools

### Prometheus + Grafana

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']

# MongoDB exporter docker-compose
services:
  mongodb-exporter:
    image: percona/mongodb_exporter:0.40
    environment:
      - MONGODB_URI=mongodb://user:pass@mongodb:27017
    ports:
      - "9216:9216"
```

### Key Prometheus Metrics

```
# Connections
mongodb_connections{state="current"}
mongodb_connections{state="available"}

# Operations
mongodb_op_counters_total{type="insert"}
mongodb_op_counters_total{type="query"}
mongodb_op_counters_total{type="update"}
mongodb_op_counters_total{type="delete"}

# Memory
mongodb_memory{type="resident"}
mongodb_memory{type="virtual"}

# Replication
mongodb_mongod_replset_member_state
mongodb_mongod_replset_member_replication_lag

# WiredTiger
mongodb_wiredtiger_cache_bytes
mongodb_wiredtiger_cache_bytes_total
```

### Datadog Integration

```yaml
# datadog.yaml for MongoDB
init_config:

instances:
  - hosts:
      - localhost:27017
    username: datadog
    password: <password>
    database: admin
    options:
      authSource: admin
    additional_metrics:
      - durability
      - locks
      - metrics.commands
      - tcmalloc
      - top
      - collection
```

### CloudWatch (AWS)

```javascript
// Custom CloudWatch metrics
const AWS = require('aws-sdk');
const cloudwatch = new AWS.CloudWatch();

async function publishMetrics(stats) {
  const params = {
    Namespace: 'MongoDB',
    MetricData: [
      {
        MetricName: 'Connections',
        Value: stats.connections.current,
        Unit: 'Count',
        Dimensions: [
          { Name: 'Instance', Value: 'prod-mongo-1' }
        ]
      },
      {
        MetricName: 'QueriesPerSecond',
        Value: stats.opcountersPerSec.query,
        Unit: 'Count/Second'
      }
    ]
  };
  
  await cloudwatch.putMetricData(params).promise();
}
```

---

## Alerting Strategies

### Alert Thresholds

```javascript
const alertThresholds = {
  // Critical alerts - immediate action
  critical: {
    connectionUtilization: 90,      // %
    diskUsage: 90,                  // %
    replicationLag: 60,             // seconds
    memoryUsage: 95,                // %
    queryLatencyP99: 5000           // ms
  },
  
  // Warning alerts - investigate soon
  warning: {
    connectionUtilization: 70,
    diskUsage: 75,
    replicationLag: 30,
    memoryUsage: 85,
    queryLatencyP99: 1000
  },
  
  // Info alerts - trending
  info: {
    connectionUtilization: 50,
    diskUsage: 60,
    replicationLag: 10,
    memoryUsage: 70,
    queryLatencyP99: 500
  }
}
```

### Alert Rules

```yaml
# Prometheus alerting rules
groups:
  - name: mongodb-alerts
    rules:
      # High connection usage
      - alert: MongoDBHighConnections
        expr: mongodb_connections{state="current"} / mongodb_connections{state="available"} > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High connection usage on {{ $labels.instance }}"
          
      # Replication lag
      - alert: MongoDBReplicationLag
        expr: mongodb_mongod_replset_member_replication_lag > 30
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Replication lag > 30s on {{ $labels.instance }}"
          
      # Slow queries
      - alert: MongoDBSlowQueries
        expr: rate(mongodb_mongod_metrics_document_total[5m]) < 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low query throughput on {{ $labels.instance }}"
```

### On-Call Runbook

```javascript
function generateRunbook() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           ON-CALL RUNBOOK - MONGODB                         ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const alerts = {
    'High CPU Usage': {
      check: 'top, htop, or cloud metrics',
      causes: [
        'Slow/inefficient queries',
        'Missing indexes',
        'Large aggregations'
      ],
      actions: [
        'Check db.currentOp() for long-running queries',
        'Review profiler: db.system.profile.find()',
        'Check for collection scans',
        'Consider killing problematic queries'
      ]
    },
    
    'High Connection Count': {
      check: 'db.serverStatus().connections',
      causes: [
        'Connection leaks in application',
        'Increased traffic',
        'Slow queries holding connections'
      ],
      actions: [
        'Check application connection pooling',
        'Review slow queries',
        'Consider increasing maxIncomingConnections',
        'Check for connection storms'
      ]
    },
    
    'Replication Lag': {
      check: 'rs.status()',
      causes: [
        'Network latency',
        'Secondary under heavy load',
        'Large write volume',
        'Index builds'
      ],
      actions: [
        'Check secondary server resources',
        'Review network connectivity',
        'Check for long-running operations',
        'Consider adding secondaries'
      ]
    }
  }
  
  Object.entries(alerts).forEach(([name, details]) => {
    print(`\n${"═".repeat(60)}`)
    print(`ALERT: ${name}`)
    print("═".repeat(60))
    
    print(`\nCheck: ${details.check}`)
    
    print("\nPossible Causes:")
    details.causes.forEach(c => print(`  • ${c}`))
    
    print("\nActions:")
    details.actions.forEach((a, i) => print(`  ${i + 1}. ${a}`))
  })
}

generateRunbook()
```

---

## Summary

### Monitoring Tools

| Tool | Purpose | Best For |
|------|---------|----------|
| mongostat | Real-time stats | Quick checks |
| mongotop | Collection activity | Identifying hot spots |
| currentOp | Active operations | Troubleshooting |
| serverStatus | Server metrics | Detailed analysis |
| Profiler | Query analysis | Performance tuning |

### Key Metrics to Monitor

| Category | Metrics |
|----------|---------|
| Performance | Query latency, throughput |
| Connections | Current, available |
| Memory | Resident, cache |
| Storage | Disk usage, data size |
| Replication | Lag, oplog window |

### Best Practices

| Practice | Reason |
|----------|--------|
| Monitor continuously | Catch issues early |
| Set appropriate thresholds | Reduce alert fatigue |
| Trend analysis | Capacity planning |
| Correlate metrics | Root cause analysis |
| Automate responses | Faster resolution |

### What's Next?

In the next chapter, we'll explore Performance Tuning.

---

## Practice Questions

1. What is the difference between mongostat and mongotop?
2. How do you enable profiling in MongoDB?
3. What does a COLLSCAN in plan summary indicate?
4. What key metrics should you monitor for replication?
5. How do you identify slow queries?
6. What is the purpose of WiredTiger cache monitoring?
7. How do you set log verbosity dynamically?
8. What are appropriate alert thresholds for connections?

---

## Hands-On Exercises

### Exercise 1: Real-Time Monitoring Dashboard

```javascript
// Real-time monitoring script

function realtimeMonitor(intervalSeconds = 5) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           REAL-TIME MONGODB MONITOR                         ║")
  print("║           Press Ctrl+C to stop                              ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  let previousStats = null
  
  while (true) {
    const currentStats = db.serverStatus()
    
    // Clear screen (in terminal)
    print('\x1b[2J\x1b[H')
    
    print(`Time: ${new Date().toISOString()}`)
    print("═".repeat(60))
    
    // Connections
    print("\n┌─ CONNECTIONS ─────────────────────────────────────────────┐")
    const conn = currentStats.connections
    const connPct = ((conn.current / (conn.current + conn.available)) * 100).toFixed(1)
    print(`│  Current: ${conn.current}`.padEnd(60) + "│")
    print(`│  Available: ${conn.available}`.padEnd(60) + "│")
    print(`│  Utilization: ${connPct}%`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘")
    
    // Operations
    print("\n┌─ OPERATIONS (/sec) ───────────────────────────────────────┐")
    const ops = currentStats.opcounters
    if (previousStats) {
      const prevOps = previousStats.opcounters
      const insert = (ops.insert - prevOps.insert) / intervalSeconds
      const query = (ops.query - prevOps.query) / intervalSeconds
      const update = (ops.update - prevOps.update) / intervalSeconds
      const del = (ops.delete - prevOps.delete) / intervalSeconds
      
      print(`│  Insert: ${insert.toFixed(1)}`.padEnd(60) + "│")
      print(`│  Query: ${query.toFixed(1)}`.padEnd(60) + "│")
      print(`│  Update: ${update.toFixed(1)}`.padEnd(60) + "│")
      print(`│  Delete: ${del.toFixed(1)}`.padEnd(60) + "│")
    } else {
      print(`│  Collecting...`.padEnd(60) + "│")
    }
    print("└────────────────────────────────────────────────────────────┘")
    
    // Memory
    print("\n┌─ MEMORY (MB) ─────────────────────────────────────────────┐")
    const mem = currentStats.mem
    print(`│  Resident: ${mem.resident}`.padEnd(60) + "│")
    print(`│  Virtual: ${mem.virtual}`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘")
    
    // WiredTiger Cache
    if (currentStats.wiredTiger) {
      print("\n┌─ WIREDTIGER CACHE ────────────────────────────────────────┐")
      const cache = currentStats.wiredTiger.cache
      const used = cache['bytes currently in the cache']
      const max = cache['maximum bytes configured']
      const pct = ((used / max) * 100).toFixed(1)
      
      print(`│  Used: ${(used / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
      print(`│  Max: ${(max / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
      print(`│  Utilization: ${pct}%`.padEnd(60) + "│")
      print("└────────────────────────────────────────────────────────────┘")
    }
    
    // Active operations
    const activeOps = db.currentOp({ active: true }).inprog.length
    print(`\nActive Operations: ${activeOps}`)
    
    previousStats = currentStats
    
    // Sleep (in practice, use setInterval in Node.js)
    sleep(intervalSeconds * 1000)
  }
}

// Single snapshot
function monitorSnapshot() {
  const stats = db.serverStatus()
  
  print("=== MongoDB Status Snapshot ===\n")
  
  print("Connections:")
  print(`  Current: ${stats.connections.current}`)
  print(`  Available: ${stats.connections.available}`)
  
  print("\nOperations (total):")
  Object.entries(stats.opcounters).forEach(([op, count]) => {
    print(`  ${op}: ${count}`)
  })
  
  print("\nMemory:")
  print(`  Resident: ${stats.mem.resident} MB`)
  print(`  Virtual: ${stats.mem.virtual} MB`)
}

monitorSnapshot()
```

### Exercise 2: Slow Query Analyzer

```javascript
// Analyze slow queries from profiler

function analyzeSlowQueries(options = {}) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           SLOW QUERY ANALYZER                               ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const {
    minMillis = 100,
    limit = 20,
    since = new Date(Date.now() - 24 * 60 * 60 * 1000)  // Last 24 hours
  } = options
  
  // Check profiling status
  const profStatus = db.getProfilingStatus()
  print(`Profiling Level: ${profStatus.was}`)
  print(`Slow Query Threshold: ${profStatus.slowms}ms\n`)
  
  // Query profiler
  const slowQueries = db.system.profile.find({
    ts: { $gte: since },
    millis: { $gte: minMillis }
  }).sort({ millis: -1 }).limit(limit).toArray()
  
  if (slowQueries.length === 0) {
    print("No slow queries found in the specified period.")
    print("Tip: Enable profiling with db.setProfilingLevel(1, { slowms: 100 })")
    return
  }
  
  print(`Found ${slowQueries.length} slow queries:\n`)
  
  // Analyze each query
  slowQueries.forEach((q, i) => {
    print(`\n${"─".repeat(60)}`)
    print(`Query ${i + 1}:`)
    print(`  Time: ${q.ts?.toISOString() || 'N/A'}`)
    print(`  Duration: ${q.millis}ms`)
    print(`  Namespace: ${q.ns}`)
    print(`  Operation: ${q.op}`)
    print(`  Plan: ${q.planSummary}`)
    print(`  Keys Examined: ${q.keysExamined}`)
    print(`  Docs Examined: ${q.docsExamined}`)
    print(`  Docs Returned: ${q.nreturned}`)
    
    // Efficiency calculation
    if (q.docsExamined && q.nreturned) {
      const efficiency = (q.nreturned / q.docsExamined * 100).toFixed(1)
      print(`  Efficiency: ${efficiency}%`)
      
      if (efficiency < 10) {
        print(`  ⚠ LOW EFFICIENCY - Consider adding/optimizing indexes`)
      }
    }
    
    // Check for collection scan
    if (q.planSummary === 'COLLSCAN') {
      print(`  ⚠ COLLECTION SCAN - No index used!`)
    }
  })
  
  // Summary by collection
  print("\n\n" + "═".repeat(60))
  print("Summary by Collection:")
  
  const byCollection = {}
  slowQueries.forEach(q => {
    if (!byCollection[q.ns]) {
      byCollection[q.ns] = { count: 0, totalMillis: 0, maxMillis: 0 }
    }
    byCollection[q.ns].count++
    byCollection[q.ns].totalMillis += q.millis
    byCollection[q.ns].maxMillis = Math.max(byCollection[q.ns].maxMillis, q.millis)
  })
  
  Object.entries(byCollection)
    .sort((a, b) => b[1].totalMillis - a[1].totalMillis)
    .forEach(([ns, stats]) => {
      print(`\n${ns}:`)
      print(`  Slow queries: ${stats.count}`)
      print(`  Total time: ${stats.totalMillis}ms`)
      print(`  Avg time: ${(stats.totalMillis / stats.count).toFixed(0)}ms`)
      print(`  Max time: ${stats.maxMillis}ms`)
    })
}

analyzeSlowQueries({ minMillis: 50 })
```

### Exercise 3: Connection Pool Monitor

```javascript
// Monitor connection patterns

function connectionMonitor() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           CONNECTION MONITOR                                ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const serverStatus = db.serverStatus()
  const connections = serverStatus.connections
  
  // Current stats
  print("┌─ CONNECTION STATISTICS ───────────────────────────────────┐")
  print(`│  Current Connections: ${connections.current}`.padEnd(60) + "│")
  print(`│  Available Connections: ${connections.available}`.padEnd(60) + "│")
  print(`│  Total Created: ${connections.totalCreated}`.padEnd(60) + "│")
  
  const utilization = (connections.current / (connections.current + connections.available) * 100).toFixed(1)
  print(`│  Utilization: ${utilization}%`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Connection by client
  print("┌─ ACTIVE CONNECTIONS BY CLIENT ────────────────────────────┐")
  
  const currentOps = db.currentOp({ active: true }).inprog
  const byClient = {}
  
  currentOps.forEach(op => {
    const client = op.client?.split(':')[0] || 'unknown'
    const app = op.appName || 'unknown'
    const key = `${app} (${client})`
    byClient[key] = (byClient[key] || 0) + 1
  })
  
  Object.entries(byClient)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([client, count]) => {
      print(`│  ${client}: ${count}`.padEnd(60) + "│")
    })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Recommendations
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  
  if (parseFloat(utilization) > 80) {
    print("│  ⚠ High connection utilization".padEnd(60) + "│")
    print("│    - Check for connection leaks".padEnd(60) + "│")
    print("│    - Consider increasing pool size".padEnd(60) + "│")
  } else if (parseFloat(utilization) > 50) {
    print("│  ! Moderate connection utilization".padEnd(60) + "│")
    print("│    - Monitor for trends".padEnd(60) + "│")
  } else {
    print("│  ✓ Connection utilization is healthy".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
}

connectionMonitor()
```

### Exercise 4: Replica Set Health Check

```javascript
// Comprehensive replica set health check

function replicaSetHealthCheck() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           REPLICA SET HEALTH CHECK                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  let rsStatus
  try {
    rsStatus = rs.status()
  } catch (e) {
    print("Not a replica set or not connected to one.")
    return
  }
  
  // Basic info
  print(`Replica Set: ${rsStatus.set}`)
  print(`Members: ${rsStatus.members.length}`)
  print(`Heartbeat Interval: ${rsStatus.heartbeatIntervalMillis}ms\n`)
  
  // Member status
  print("┌─ MEMBER STATUS ───────────────────────────────────────────┐")
  print("│  Host                   State        Health  Lag         │")
  print("├────────────────────────────────────────────────────────────┤")
  
  const primary = rsStatus.members.find(m => m.stateStr === 'PRIMARY')
  const primaryOptime = primary?.optimeDate
  
  rsStatus.members.forEach(member => {
    const host = member.name.substring(0, 20).padEnd(22)
    const state = member.stateStr.padEnd(12)
    const health = member.health === 1 ? '✓' : '✗'
    
    let lag = 'N/A'
    if (member.stateStr === 'SECONDARY' && primaryOptime && member.optimeDate) {
      const lagSeconds = (primaryOptime - member.optimeDate) / 1000
      lag = `${lagSeconds.toFixed(1)}s`
    } else if (member.stateStr === 'PRIMARY') {
      lag = '-'
    }
    
    print(`│  ${host} ${state} ${health}       ${lag.padEnd(10)} │`)
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Oplog info
  print("┌─ OPLOG STATUS ────────────────────────────────────────────┐")
  
  try {
    const oplog = db.getSiblingDB('local').oplog.rs.stats()
    const oplogSizeMB = (oplog.maxSize / 1024 / 1024).toFixed(0)
    const oplogUsedMB = (oplog.size / 1024 / 1024).toFixed(0)
    
    // Get oplog window
    const first = db.getSiblingDB('local').oplog.rs.find().sort({ $natural: 1 }).limit(1).next()
    const last = db.getSiblingDB('local').oplog.rs.find().sort({ $natural: -1 }).limit(1).next()
    
    if (first && last) {
      const windowHours = ((last.ts.t - first.ts.t) / 3600).toFixed(1)
      print(`│  Oplog Size: ${oplogSizeMB} MB`.padEnd(60) + "│")
      print(`│  Oplog Used: ${oplogUsedMB} MB`.padEnd(60) + "│")
      print(`│  Oplog Window: ${windowHours} hours`.padEnd(60) + "│")
    }
  } catch (e) {
    print(`│  Unable to get oplog stats`.padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Alerts
  print("┌─ HEALTH ALERTS ───────────────────────────────────────────┐")
  
  const alerts = []
  
  // Check for unhealthy members
  const unhealthy = rsStatus.members.filter(m => m.health !== 1)
  if (unhealthy.length > 0) {
    alerts.push({ level: 'CRITICAL', msg: `${unhealthy.length} unhealthy member(s)` })
  }
  
  // Check for no primary
  if (!primary) {
    alerts.push({ level: 'CRITICAL', msg: 'No primary member!' })
  }
  
  // Check for high replication lag
  rsStatus.members.forEach(m => {
    if (m.stateStr === 'SECONDARY' && primaryOptime && m.optimeDate) {
      const lagSeconds = (primaryOptime - m.optimeDate) / 1000
      if (lagSeconds > 30) {
        alerts.push({ level: 'WARNING', msg: `${m.name} lag: ${lagSeconds}s` })
      }
    }
  })
  
  if (alerts.length === 0) {
    print("│  ✓ All health checks passed".padEnd(60) + "│")
  } else {
    alerts.forEach(a => {
      const icon = a.level === 'CRITICAL' ? '🔴' : '🟠'
      print(`│  ${icon} [${a.level}] ${a.msg}`.padEnd(60) + "│")
    })
  }
  
  print("└────────────────────────────────────────────────────────────┘")
}

// Run health check (will fail if not a replica set)
try {
  replicaSetHealthCheck()
} catch (e) {
  print("Note: Replica set health check requires a replica set connection")
}
```

### Exercise 5: Performance Report Generator

```javascript
// Generate comprehensive performance report

function generatePerformanceReport() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           MONGODB PERFORMANCE REPORT                        ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Generated: ${new Date().toISOString()}\n`)
  
  const serverStatus = db.serverStatus()
  
  // Executive Summary
  print("## EXECUTIVE SUMMARY")
  print("─".repeat(60))
  
  const conn = serverStatus.connections
  const connPct = ((conn.current / (conn.current + conn.available)) * 100).toFixed(1)
  
  const summary = {
    'Connection Utilization': `${connPct}%`,
    'Memory (Resident)': `${serverStatus.mem.resident} MB`,
    'Uptime': `${(serverStatus.uptime / 86400).toFixed(1)} days`,
    'Total Operations': Object.values(serverStatus.opcounters).reduce((a, b) => a + b, 0)
  }
  
  Object.entries(summary).forEach(([key, value]) => {
    print(`  ${key}: ${value}`)
  })
  
  // Operations breakdown
  print("\n## OPERATIONS BREAKDOWN")
  print("─".repeat(60))
  
  const ops = serverStatus.opcounters
  const totalOps = Object.values(ops).reduce((a, b) => a + b, 0)
  
  Object.entries(ops).forEach(([op, count]) => {
    const pct = ((count / totalOps) * 100).toFixed(1)
    const bar = '█'.repeat(Math.round(pct / 5))
    print(`  ${op.padEnd(10)} ${bar.padEnd(20)} ${pct}% (${count})`)
  })
  
  // Database sizes
  print("\n## DATABASE SIZES")
  print("─".repeat(60))
  
  const dbList = db.adminCommand({ listDatabases: 1 })
  dbList.databases
    .filter(d => !['admin', 'local', 'config'].includes(d.name))
    .sort((a, b) => b.sizeOnDisk - a.sizeOnDisk)
    .forEach(d => {
      const sizeMB = (d.sizeOnDisk / 1024 / 1024).toFixed(2)
      print(`  ${d.name.padEnd(20)} ${sizeMB} MB`)
    })
  
  // Index efficiency
  print("\n## INDEX RECOMMENDATIONS")
  print("─".repeat(60))
  
  const profStatus = db.getProfilingStatus()
  if (profStatus.was > 0) {
    const collScans = db.system.profile.find({
      planSummary: 'COLLSCAN'
    }).limit(5).toArray()
    
    if (collScans.length > 0) {
      print("  Collections with COLLSCAN (need indexes):")
      collScans.forEach(q => {
        print(`    - ${q.ns}: ${q.millis}ms`)
      })
    } else {
      print("  ✓ No recent collection scans detected")
    }
  } else {
    print("  Enable profiling to detect index issues:")
    print("  db.setProfilingLevel(1, { slowms: 100 })")
  }
  
  // Recommendations
  print("\n## RECOMMENDATIONS")
  print("─".repeat(60))
  
  const recommendations = []
  
  if (parseFloat(connPct) > 70) {
    recommendations.push("Review connection pooling configuration")
  }
  
  if (serverStatus.mem.resident > 1000) {
    recommendations.push("Consider memory optimization")
  }
  
  if (profStatus.was === 0) {
    recommendations.push("Enable query profiling for optimization insights")
  }
  
  if (recommendations.length === 0) {
    print("  ✓ No immediate recommendations")
  } else {
    recommendations.forEach((r, i) => {
      print(`  ${i + 1}. ${r}`)
    })
  }
}

generatePerformanceReport()
```

---

[← Previous: Backup and Recovery](55-backup-recovery.md) | [Next: Performance Tuning →](57-performance-tuning.md)
