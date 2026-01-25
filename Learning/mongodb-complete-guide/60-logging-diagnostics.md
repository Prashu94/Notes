# Chapter 60: Logging and Diagnostics

## Table of Contents
- [Logging Overview](#logging-overview)
- [Log Configuration](#log-configuration)
- [Log Analysis](#log-analysis)
- [Diagnostic Tools](#diagnostic-tools)
- [Troubleshooting](#troubleshooting)
- [Summary](#summary)

---

## Logging Overview

### MongoDB Log Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Logging System                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Log Entry Format (JSON - MongoDB 4.4+):                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ {                                                            │   │
│  │   "t": {"$date": "2024-01-15T10:30:00.000Z"},  // Timestamp  │   │
│  │   "s": "I",                                     // Severity   │   │
│  │   "c": "NETWORK",                               // Component  │   │
│  │   "id": 12345,                                  // Message ID │   │
│  │   "ctx": "listener",                            // Context    │   │
│  │   "msg": "Connection accepted",                 // Message    │   │
│  │   "attr": {...}                                 // Attributes │   │
│  │ }                                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Severity Levels:                                                  │
│  ┌─────┬───────────┬────────────────────────────────────────────┐ │
│  │ F   │ Fatal     │ Unrecoverable errors                       │ │
│  │ E   │ Error     │ Errors that need attention                 │ │
│  │ W   │ Warning   │ Potential issues                           │ │
│  │ I   │ Info      │ Normal operations                          │ │
│  │ D1-5│ Debug     │ Debug levels (verbose)                     │ │
│  └─────┴───────────┴────────────────────────────────────────────┘ │
│                                                                     │
│  Components:                                                       │
│  ACCESS, COMMAND, CONTROL, GEO, INDEX, NETWORK, QUERY,            │
│  REPL, SHARDING, STORAGE, JOURNAL, WRITE                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Log Components

| Component | Description |
|-----------|-------------|
| ACCESS | Authentication and authorization |
| COMMAND | Database commands |
| CONTROL | Control activities |
| FTDC | Diagnostic data collection |
| GEO | Geospatial queries |
| INDEX | Index operations |
| NETWORK | Network activities |
| QUERY | Query operations |
| REPL | Replication |
| SHARDING | Sharding operations |
| STORAGE | Storage engine |
| WRITE | Write operations |

---

## Log Configuration

### Basic Configuration

```yaml
# mongod.conf
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  logRotate: reopen  # or rename
  
  # Verbosity settings
  verbosity: 0  # Default info level
  
  # Component-specific verbosity
  component:
    accessControl:
      verbosity: 1
    command:
      verbosity: 0
    query:
      verbosity: 1
    replication:
      verbosity: 1
    storage:
      verbosity: 0
```

### Runtime Log Configuration

```javascript
// Get current log verbosity
db.adminCommand({ getParameter: 1, logLevel: 1 })

// Set global log verbosity
db.adminCommand({ setParameter: 1, logLevel: 1 })

// Set component-specific verbosity
db.adminCommand({
  setParameter: 1,
  logComponentVerbosity: {
    query: { verbosity: 2 },
    storage: { verbosity: 1 },
    replication: { verbosity: 1 }
  }
})

// Get current component verbosity
db.adminCommand({ getParameter: 1, logComponentVerbosity: 1 })
```

### Slow Query Logging

```yaml
# mongod.conf
operationProfiling:
  mode: slowOp          # off, slowOp, all
  slowOpThresholdMs: 100
  slowOpSampleRate: 1.0  # 0.0 to 1.0
```

```javascript
// Set slow query threshold at runtime
db.setProfilingLevel(1, { slowms: 100 })

// Check current profiling level
db.getProfilingStatus()

// View slow queries in log
// Queries exceeding threshold are logged with QUERY component
```

### Log Rotation

```bash
# Signal MongoDB to rotate logs (Linux)
kill -SIGUSR1 $(pgrep mongod)

# Or use admin command
mongosh --eval 'db.adminCommand({ logRotate: 1 })'
```

```javascript
// Rotate logs from shell
db.adminCommand({ logRotate: 1 })

// Configure log rotation with logrotate (Linux)
// /etc/logrotate.d/mongodb
/*
/var/log/mongodb/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        /bin/kill -SIGUSR1 $(cat /var/run/mongodb/mongod.pid 2>/dev/null) 2>/dev/null || true
    endscript
}
*/
```

---

## Log Analysis

### Reading JSON Logs

```javascript
// Parse JSON log entries
function parseLogEntry(logLine) {
  try {
    return JSON.parse(logLine)
  } catch (e) {
    return null
  }
}

// Example log entry
const logEntry = {
  "t": { "$date": "2024-01-15T10:30:00.123Z" },
  "s": "I",
  "c": "QUERY",
  "id": 51803,
  "ctx": "conn123",
  "msg": "Slow query",
  "attr": {
    "type": "command",
    "ns": "mydb.orders",
    "command": { "find": "orders", "filter": { "status": "pending" } },
    "planSummary": "COLLSCAN",
    "keysExamined": 0,
    "docsExamined": 100000,
    "cursorExhausted": true,
    "numYields": 781,
    "nreturned": 500,
    "queryHash": "ABC123",
    "planCacheKey": "DEF456",
    "durationMillis": 1234
  }
}
```

### Log Analysis Script

```javascript
// Analyze MongoDB logs for patterns

function analyzeLogFile(logContent) {
  const lines = logContent.split('\n').filter(l => l.trim())
  
  const stats = {
    total: 0,
    byComponent: {},
    bySeverity: {},
    slowQueries: [],
    errors: [],
    warnings: []
  }
  
  lines.forEach(line => {
    try {
      const entry = JSON.parse(line)
      stats.total++
      
      // Count by component
      const component = entry.c || 'UNKNOWN'
      stats.byComponent[component] = (stats.byComponent[component] || 0) + 1
      
      // Count by severity
      const severity = entry.s || 'UNKNOWN'
      stats.bySeverity[severity] = (stats.bySeverity[severity] || 0) + 1
      
      // Collect slow queries
      if (entry.attr?.durationMillis > 100) {
        stats.slowQueries.push({
          timestamp: entry.t?.$date,
          namespace: entry.attr?.ns,
          duration: entry.attr?.durationMillis,
          plan: entry.attr?.planSummary
        })
      }
      
      // Collect errors
      if (entry.s === 'E') {
        stats.errors.push({
          timestamp: entry.t?.$date,
          message: entry.msg,
          id: entry.id
        })
      }
      
      // Collect warnings
      if (entry.s === 'W') {
        stats.warnings.push({
          timestamp: entry.t?.$date,
          message: entry.msg,
          id: entry.id
        })
      }
    } catch (e) {
      // Skip non-JSON lines
    }
  })
  
  return stats
}

// Print analysis results
function printLogAnalysis(stats) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║                 LOG ANALYSIS REPORT                         ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Total log entries: ${stats.total}\n`)
  
  print("┌─ BY SEVERITY ─────────────────────────────────────────────┐")
  Object.entries(stats.bySeverity)
    .sort((a, b) => b[1] - a[1])
    .forEach(([sev, count]) => {
      const pct = (count / stats.total * 100).toFixed(1)
      print(`│  ${sev.padEnd(10)} ${String(count).padStart(8)} (${pct}%)`.padEnd(60) + "│")
    })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ BY COMPONENT ────────────────────────────────────────────┐")
  Object.entries(stats.byComponent)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([comp, count]) => {
      const pct = (count / stats.total * 100).toFixed(1)
      print(`│  ${comp.padEnd(15)} ${String(count).padStart(8)} (${pct}%)`.padEnd(60) + "│")
    })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  if (stats.errors.length > 0) {
    print("┌─ ERRORS ───────────────────────────────────────────────────┐")
    stats.errors.slice(0, 5).forEach(err => {
      print(`│  ${err.timestamp}`.padEnd(60) + "│")
      print(`│    ${err.message.substring(0, 50)}`.padEnd(60) + "│")
    })
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  if (stats.slowQueries.length > 0) {
    print("┌─ SLOW QUERIES (Top 5) ────────────────────────────────────┐")
    stats.slowQueries
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 5)
      .forEach(q => {
        print(`│  ${q.namespace}: ${q.duration}ms (${q.plan})`.padEnd(60) + "│")
      })
    print("└────────────────────────────────────────────────────────────┘")
  }
}
```

### Common Log Patterns

```javascript
// Common patterns to search for in logs

const logPatterns = {
  // Authentication failures
  authFailure: '"c":"ACCESS".*"msg":"Authentication failed"',
  
  // Connection issues
  connectionReset: '"msg":"Connection ended"',
  connectionAccepted: '"msg":"Connection accepted"',
  
  // Slow queries
  slowQuery: '"msg":"Slow query"',
  collScan: '"planSummary":"COLLSCAN"',
  
  // Replication issues
  replError: '"c":"REPL".*"s":"E"',
  rollback: '"msg":"rollback"',
  
  // Storage issues
  storageError: '"c":"STORAGE".*"s":"E"',
  checkpointIssue: '"msg":"checkpoint".*"s":"W"',
  
  // Index issues
  indexBuild: '"msg":"Index build"',
  indexCorrupt: '"msg":"index".*"corrupt"'
}

// Use with grep
// grep -E '"planSummary":"COLLSCAN"' /var/log/mongodb/mongod.log
```

---

## Diagnostic Tools

### Full-Time Diagnostic Data Capture (FTDC)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FTDC (Full-Time Diagnostic Data)                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Location: <dbPath>/diagnostic.data/                               │
│                                                                     │
│  Captures:                                                         │
│  • serverStatus output                                             │
│  • replSetGetStatus output                                         │
│  • collStats for collections                                       │
│  • dbStats for databases                                           │
│                                                                     │
│  Frequency:                                                        │
│  • Every 1 second (configurable)                                   │
│                                                                     │
│  Retention:                                                        │
│  • Default: 200MB max size                                         │
│  • Automatic rotation                                              │
│                                                                     │
│  Files:                                                            │
│  metrics.2024-01-15T10-00-00Z-00000                               │
│  metrics.interim                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```yaml
# mongod.conf - FTDC configuration
setParameter:
  diagnosticDataCollectionEnabled: true
  diagnosticDataCollectionDirectorySizeMB: 200
  diagnosticDataCollectionFileSizeMB: 10
  diagnosticDataCollectionPeriodMillis: 1000
```

```javascript
// Check FTDC status
db.adminCommand({ getParameter: 1, diagnosticDataCollectionEnabled: 1 })

// View FTDC files
// ls -la <dbPath>/diagnostic.data/

// Analyze with MongoDB provided tools
// mongod --diagnose-data diagnostic.data/
```

### currentOp Analysis

```javascript
// View current operations
function analyzeCurrentOp() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              CURRENT OPERATIONS ANALYSIS                    ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const ops = db.currentOp({ active: true })
  
  print(`Total active operations: ${ops.inprog.length}\n`)
  
  // Group by operation type
  const byType = {}
  const byNamespace = {}
  const longRunning = []
  
  ops.inprog.forEach(op => {
    // By type
    const type = op.op || 'unknown'
    byType[type] = (byType[type] || 0) + 1
    
    // By namespace
    const ns = op.ns || 'system'
    byNamespace[ns] = (byNamespace[ns] || 0) + 1
    
    // Long running (> 1 second)
    if (op.secs_running > 1) {
      longRunning.push({
        opid: op.opid,
        type: op.op,
        ns: op.ns,
        secs: op.secs_running,
        desc: op.desc
      })
    }
  })
  
  print("┌─ BY OPERATION TYPE ────────────────────────────────────────┐")
  Object.entries(byType)
    .sort((a, b) => b[1] - a[1])
    .forEach(([type, count]) => {
      print(`│  ${type.padEnd(20)} ${count}`.padEnd(60) + "│")
    })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ BY NAMESPACE (Top 5) ────────────────────────────────────┐")
  Object.entries(byNamespace)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .forEach(([ns, count]) => {
      print(`│  ${ns.substring(0, 40).padEnd(42)} ${count}`.padEnd(60) + "│")
    })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  if (longRunning.length > 0) {
    print("┌─ LONG RUNNING (>1s) ──────────────────────────────────────┐")
    longRunning
      .sort((a, b) => b.secs - a.secs)
      .slice(0, 10)
      .forEach(op => {
        print(`│  [${op.opid}] ${op.type} on ${op.ns || 'N/A'} - ${op.secs}s`.padEnd(60) + "│")
      })
    print("└────────────────────────────────────────────────────────────┘\n")
    
    print("To kill an operation: db.killOp(<opid>)")
  }
  
  return { byType, byNamespace, longRunning }
}

analyzeCurrentOp()
```

### serverStatus Diagnostics

```javascript
// Comprehensive server diagnostics
function serverDiagnostics() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              SERVER DIAGNOSTICS                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const status = db.serverStatus()
  
  // Uptime
  print("┌─ UPTIME ──────────────────────────────────────────────────┐")
  const days = Math.floor(status.uptime / 86400)
  const hours = Math.floor((status.uptime % 86400) / 3600)
  print(`│  Server Uptime: ${days} days, ${hours} hours`.padEnd(60) + "│")
  print(`│  Since: ${status.localTime}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Connections
  print("┌─ CONNECTIONS ─────────────────────────────────────────────┐")
  const conn = status.connections
  print(`│  Current: ${conn.current}`.padEnd(60) + "│")
  print(`│  Available: ${conn.available}`.padEnd(60) + "│")
  print(`│  Total Created: ${conn.totalCreated}`.padEnd(60) + "│")
  if (conn.current > conn.available * 0.8) {
    print("│  ⚠ Connection usage high".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Operations
  print("┌─ OPERATION COUNTERS ──────────────────────────────────────┐")
  const ops = status.opcounters
  print(`│  Insert: ${ops.insert.toLocaleString()}`.padEnd(60) + "│")
  print(`│  Query: ${ops.query.toLocaleString()}`.padEnd(60) + "│")
  print(`│  Update: ${ops.update.toLocaleString()}`.padEnd(60) + "│")
  print(`│  Delete: ${ops.delete.toLocaleString()}`.padEnd(60) + "│")
  print(`│  GetMore: ${ops.getmore.toLocaleString()}`.padEnd(60) + "│")
  print(`│  Command: ${ops.command.toLocaleString()}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Memory
  print("┌─ MEMORY ──────────────────────────────────────────────────┐")
  const mem = status.mem
  print(`│  Resident: ${mem.resident} MB`.padEnd(60) + "│")
  print(`│  Virtual: ${mem.virtual} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Network
  print("┌─ NETWORK ─────────────────────────────────────────────────┐")
  const net = status.network
  print(`│  Bytes In: ${(net.bytesIn / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Bytes Out: ${(net.bytesOut / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Requests: ${net.numRequests.toLocaleString()}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Asserts
  print("┌─ ASSERTS ─────────────────────────────────────────────────┐")
  const asserts = status.asserts
  print(`│  Regular: ${asserts.regular}`.padEnd(60) + "│")
  print(`│  Warning: ${asserts.warning}`.padEnd(60) + "│")
  print(`│  Message: ${asserts.msg}`.padEnd(60) + "│")
  print(`│  User: ${asserts.user}`.padEnd(60) + "│")
  print(`│  Rollovers: ${asserts.rollovers}`.padEnd(60) + "│")
  if (asserts.regular > 0 || asserts.warning > 0) {
    print("│  ⚠ Asserts detected - check logs".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘")
  
  return status
}

serverDiagnostics()
```

### Database Profiler

```javascript
// Enable profiling
db.setProfilingLevel(1, { slowms: 50 })

// Profile all operations
db.setProfilingLevel(2)

// Disable profiling
db.setProfilingLevel(0)

// Analyze profiler data
function analyzeProfiler(limit = 20) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              PROFILER ANALYSIS                              ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const profileData = db.system.profile.find()
    .sort({ ts: -1 })
    .limit(limit)
    .toArray()
  
  print(`Recent profiled operations: ${profileData.length}\n`)
  
  // Group by operation type
  const byOp = {}
  const byNs = {}
  
  profileData.forEach(p => {
    const op = p.op || 'unknown'
    byOp[op] = (byOp[op] || 0) + 1
    
    const ns = p.ns || 'unknown'
    byNs[ns] = (byNs[ns] || 0) + 1
  })
  
  print("┌─ BY OPERATION ─────────────────────────────────────────────┐")
  Object.entries(byOp).forEach(([op, count]) => {
    print(`│  ${op.padEnd(20)} ${count}`.padEnd(60) + "│")
  })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ SLOWEST OPERATIONS ──────────────────────────────────────┐")
  profileData
    .sort((a, b) => b.millis - a.millis)
    .slice(0, 5)
    .forEach(p => {
      print(`│  ${p.millis}ms - ${p.op} on ${p.ns}`.padEnd(60) + "│")
      if (p.planSummary) {
        print(`│    Plan: ${p.planSummary}`.padEnd(60) + "│")
      }
    })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Find collection scans
  const collScans = profileData.filter(p => 
    p.planSummary && p.planSummary.includes('COLLSCAN')
  )
  
  if (collScans.length > 0) {
    print("┌─ COLLECTION SCANS (No Index) ─────────────────────────────┐")
    collScans.slice(0, 5).forEach(p => {
      print(`│  ${p.ns} - ${p.millis}ms`.padEnd(60) + "│")
    })
    print("│  ⚠ Consider adding indexes for these queries".padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘")
  }
  
  return { profileData, byOp, byNs, collScans }
}

analyzeProfiler()
```

---

## Troubleshooting

### Common Issues and Solutions

```javascript
// Troubleshooting guide

const troubleshootingGuide = {
  "High CPU Usage": {
    symptoms: [
      "mongod process using high CPU",
      "Slow query response times"
    ],
    diagnostics: [
      "db.currentOp() - check for long-running operations",
      "Check profiler for expensive queries",
      "Review explain() plans for COLLSCAN"
    ],
    solutions: [
      "Add appropriate indexes",
      "Optimize queries",
      "Increase hardware resources"
    ]
  },
  
  "High Memory Usage": {
    symptoms: [
      "mongod using all available RAM",
      "OOM killer terminating mongod"
    ],
    diagnostics: [
      "Check WiredTiger cache size",
      "Review connection count",
      "Check for large aggregations"
    ],
    solutions: [
      "Adjust cacheSizeGB in config",
      "Reduce connection pool size",
      "Use allowDiskUse for aggregations"
    ]
  },
  
  "Slow Queries": {
    symptoms: [
      "Queries taking longer than expected",
      "Timeout errors in application"
    ],
    diagnostics: [
      "Enable profiler (slowms: 100)",
      "Check explain() output",
      "Review index usage"
    ],
    solutions: [
      "Add/optimize indexes",
      "Rewrite inefficient queries",
      "Add projections to limit data"
    ]
  },
  
  "Connection Issues": {
    symptoms: [
      "Cannot connect to MongoDB",
      "Connection reset errors"
    ],
    diagnostics: [
      "Check mongod is running",
      "Verify network connectivity",
      "Check maxIncomingConnections"
    ],
    solutions: [
      "Restart mongod if needed",
      "Check firewall rules",
      "Increase connection limits"
    ]
  },
  
  "Replication Lag": {
    symptoms: [
      "Secondary behind primary",
      "Read inconsistencies"
    ],
    diagnostics: [
      "rs.printSlaveReplicationInfo()",
      "Check oplog size",
      "Network latency between nodes"
    ],
    solutions: [
      "Increase oplog size",
      "Improve network",
      "Reduce write load"
    ]
  }
}

function showTroubleshootingGuide(issue) {
  if (!troubleshootingGuide[issue]) {
    print("Available issues:")
    Object.keys(troubleshootingGuide).forEach(i => print(`  - ${i}`))
    return
  }
  
  const guide = troubleshootingGuide[issue]
  
  print(`\n╔════════════════════════════════════════════════════════════╗`)
  print(`║  TROUBLESHOOTING: ${issue}`.padEnd(61) + "║")
  print(`╚════════════════════════════════════════════════════════════╝\n`)
  
  print("┌─ SYMPTOMS ────────────────────────────────────────────────┐")
  guide.symptoms.forEach(s => {
    print(`│  • ${s}`.padEnd(60) + "│")
  })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ DIAGNOSTICS ─────────────────────────────────────────────┐")
  guide.diagnostics.forEach(d => {
    print(`│  • ${d}`.padEnd(60) + "│")
  })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ SOLUTIONS ───────────────────────────────────────────────┐")
  guide.solutions.forEach(s => {
    print(`│  • ${s}`.padEnd(60) + "│")
  })
  print("└────────────────────────────────────────────────────────────┘")
}

// Usage
// showTroubleshootingGuide("High CPU Usage")
```

### Health Check Script

```javascript
// Comprehensive health check

function healthCheck() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              MONGODB HEALTH CHECK                           ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const checks = []
  const status = db.serverStatus()
  
  // 1. Server Availability
  print("┌─ 1. SERVER AVAILABILITY ──────────────────────────────────┐")
  try {
    db.adminCommand({ ping: 1 })
    print("│  ✓ Server responding".padEnd(60) + "│")
    checks.push({ name: "Availability", status: "PASS" })
  } catch (e) {
    print("│  ✗ Server not responding".padEnd(60) + "│")
    checks.push({ name: "Availability", status: "FAIL" })
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 2. Connection Health
  print("┌─ 2. CONNECTION HEALTH ────────────────────────────────────┐")
  const connPct = (status.connections.current / 
    (status.connections.current + status.connections.available) * 100).toFixed(1)
  print(`│  Usage: ${connPct}%`.padEnd(60) + "│")
  if (parseFloat(connPct) < 80) {
    print("│  ✓ Connection usage healthy".padEnd(60) + "│")
    checks.push({ name: "Connections", status: "PASS" })
  } else {
    print("│  ⚠ High connection usage".padEnd(60) + "│")
    checks.push({ name: "Connections", status: "WARN" })
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 3. Memory Health
  print("┌─ 3. MEMORY HEALTH ────────────────────────────────────────┐")
  if (status.wiredTiger) {
    const cache = status.wiredTiger.cache
    const cachePct = (cache["bytes currently in the cache"] / 
      cache["maximum bytes configured"] * 100).toFixed(1)
    print(`│  Cache usage: ${cachePct}%`.padEnd(60) + "│")
    if (parseFloat(cachePct) < 95) {
      print("│  ✓ Cache utilization healthy".padEnd(60) + "│")
      checks.push({ name: "Memory", status: "PASS" })
    } else {
      print("│  ⚠ Cache nearly full".padEnd(60) + "│")
      checks.push({ name: "Memory", status: "WARN" })
    }
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 4. Replication Health (if applicable)
  print("┌─ 4. REPLICATION HEALTH ───────────────────────────────────┐")
  try {
    const replStatus = rs.status()
    const primary = replStatus.members.find(m => m.stateStr === 'PRIMARY')
    const secondaries = replStatus.members.filter(m => m.stateStr === 'SECONDARY')
    
    print(`│  Primary: ${primary ? 'Yes' : 'No'}`.padEnd(60) + "│")
    print(`│  Secondaries: ${secondaries.length}`.padEnd(60) + "│")
    
    // Check replication lag
    let maxLag = 0
    secondaries.forEach(s => {
      if (s.optimeDate && primary.optimeDate) {
        const lag = (primary.optimeDate - s.optimeDate) / 1000
        maxLag = Math.max(maxLag, lag)
      }
    })
    
    print(`│  Max lag: ${maxLag} seconds`.padEnd(60) + "│")
    if (maxLag < 10) {
      print("│  ✓ Replication healthy".padEnd(60) + "│")
      checks.push({ name: "Replication", status: "PASS" })
    } else {
      print("│  ⚠ Replication lag detected".padEnd(60) + "│")
      checks.push({ name: "Replication", status: "WARN" })
    }
  } catch (e) {
    print("│  Not a replica set".padEnd(60) + "│")
    checks.push({ name: "Replication", status: "N/A" })
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 5. Disk Health
  print("┌─ 5. DISK HEALTH ──────────────────────────────────────────┐")
  const dbStats = db.stats()
  print(`│  Data Size: ${(dbStats.dataSize / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Storage Size: ${(dbStats.storageSize / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print("│  ✓ Disk accessible".padEnd(60) + "│")
  checks.push({ name: "Disk", status: "PASS" })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Summary
  const passed = checks.filter(c => c.status === "PASS").length
  const warned = checks.filter(c => c.status === "WARN").length
  const failed = checks.filter(c => c.status === "FAIL").length
  
  print("╔════════════════════════════════════════════════════════════╗")
  print(`║  SUMMARY: ${passed} PASS, ${warned} WARN, ${failed} FAIL`.padEnd(61) + "║")
  print("╚════════════════════════════════════════════════════════════╝")
  
  return checks
}

healthCheck()
```

---

## Summary

### Log Configuration Reference

| Setting | Description | Default |
|---------|-------------|---------|
| destination | file, syslog, console | stdout |
| path | Log file path | none |
| logRotate | reopen, rename | rename |
| verbosity | 0-5 (global) | 0 |

### Key Diagnostic Commands

| Command | Purpose |
|---------|---------|
| db.currentOp() | Active operations |
| db.serverStatus() | Server metrics |
| db.setProfilingLevel() | Query profiling |
| rs.status() | Replication status |
| sh.status() | Sharding status |

### Log Analysis Tips

| What to Check | Why |
|---------------|-----|
| COLLSCAN entries | Missing indexes |
| Error severity (E) | System problems |
| Warning severity (W) | Potential issues |
| Connection logs | Access patterns |
| Replication logs | Sync issues |

---

## Practice Questions

1. What are the different log severity levels in MongoDB?
2. How do you enable slow query logging?
3. What is FTDC and what data does it capture?
4. How do you rotate MongoDB log files?
5. What command shows current active operations?
6. How do you enable the database profiler?
7. What log component shows authentication events?
8. How do you set verbosity for a specific component?

---

## Hands-On Exercises

### Exercise 1: Log Parser

```javascript
// Parse and summarize MongoDB logs

function parseLogSummary(logLines) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║                    LOG SUMMARY                              ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const stats = {
    total: 0,
    errors: 0,
    warnings: 0,
    slowQueries: 0,
    connections: { opened: 0, closed: 0 },
    authFailures: 0,
    collScans: 0
  }
  
  logLines.forEach(line => {
    try {
      const entry = JSON.parse(line)
      stats.total++
      
      // Count severity
      if (entry.s === 'E') stats.errors++
      if (entry.s === 'W') stats.warnings++
      
      // Check for patterns
      if (entry.msg?.includes('Slow query')) stats.slowQueries++
      if (entry.msg?.includes('Connection accepted')) stats.connections.opened++
      if (entry.msg?.includes('Connection ended')) stats.connections.closed++
      if (entry.msg?.includes('Authentication failed')) stats.authFailures++
      if (entry.attr?.planSummary?.includes('COLLSCAN')) stats.collScans++
      
    } catch (e) {
      // Skip non-JSON
    }
  })
  
  print("┌─ SUMMARY STATISTICS ──────────────────────────────────────┐")
  print(`│  Total Entries: ${stats.total}`.padEnd(60) + "│")
  print(`│  Errors: ${stats.errors}`.padEnd(60) + "│")
  print(`│  Warnings: ${stats.warnings}`.padEnd(60) + "│")
  print(`│  Slow Queries: ${stats.slowQueries}`.padEnd(60) + "│")
  print(`│  Collection Scans: ${stats.collScans}`.padEnd(60) + "│")
  print(`│  Auth Failures: ${stats.authFailures}`.padEnd(60) + "│")
  print(`│  Connections Opened: ${stats.connections.opened}`.padEnd(60) + "│")
  print(`│  Connections Closed: ${stats.connections.closed}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Alerts
  if (stats.errors > 0 || stats.authFailures > 0 || stats.collScans > 0) {
    print("┌─ ALERTS ───────────────────────────────────────────────────┐")
    if (stats.errors > 0) {
      print(`│  ⚠ ${stats.errors} error(s) detected - review immediately`.padEnd(60) + "│")
    }
    if (stats.authFailures > 0) {
      print(`│  ⚠ ${stats.authFailures} auth failure(s) - possible attack`.padEnd(60) + "│")
    }
    if (stats.collScans > 0) {
      print(`│  ⚠ ${stats.collScans} COLLSCAN(s) - add indexes`.padEnd(60) + "│")
    }
    print("└────────────────────────────────────────────────────────────┘")
  }
  
  return stats
}

// Usage (with actual log content)
// parseLogSummary(logContent.split('\n'))
```

### Exercise 2: Operations Monitor

```javascript
// Real-time operations monitor

function monitorOperations(intervalSec = 5, iterations = 12) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              OPERATIONS MONITOR                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print("Time         Active   Queries   Updates   Inserts   Deletes")
  print("─".repeat(65))
  
  let prevOps = null
  
  for (let i = 0; i < iterations; i++) {
    const status = db.serverStatus()
    const ops = status.opcounters
    const currentOp = db.currentOp({ active: true })
    const time = new Date().toISOString().substring(11, 19)
    
    if (prevOps) {
      const queries = ops.query - prevOps.query
      const updates = ops.update - prevOps.update
      const inserts = ops.insert - prevOps.insert
      const deletes = ops.delete - prevOps.delete
      
      print(`${time}     ${String(currentOp.inprog.length).padStart(6)}    ${String(queries).padStart(6)}    ${String(updates).padStart(6)}    ${String(inserts).padStart(6)}    ${String(deletes).padStart(6)}`)
    } else {
      print(`${time}     ${String(currentOp.inprog.length).padStart(6)}    (first sample)`)
    }
    
    prevOps = { ...ops }
    
    if (i < iterations - 1) {
      sleep(intervalSec * 1000)
    }
  }
  
  print("\nMonitoring complete")
}

// Usage
// monitorOperations(5, 12)
```

### Exercise 3: Diagnostic Report Generator

```javascript
// Generate comprehensive diagnostic report

function generateDiagnosticReport() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║            DIAGNOSTIC REPORT                                ║")
  print("║            " + new Date().toISOString().padEnd(47) + "║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const report = {
    timestamp: new Date(),
    server: {},
    databases: [],
    performance: {},
    issues: []
  }
  
  // Server Info
  print("═══════════════════════════════════════════════════════════════")
  print("  1. SERVER INFORMATION")
  print("═══════════════════════════════════════════════════════════════\n")
  
  const buildInfo = db.adminCommand({ buildInfo: 1 })
  const hostInfo = db.adminCommand({ hostInfo: 1 })
  
  report.server = {
    version: buildInfo.version,
    os: hostInfo.os?.type,
    hostname: hostInfo.system?.hostname,
    cpuCores: hostInfo.system?.numCores,
    memSizeMB: hostInfo.system?.memSizeMB
  }
  
  print(`  MongoDB Version: ${report.server.version}`)
  print(`  OS: ${report.server.os}`)
  print(`  Hostname: ${report.server.hostname}`)
  print(`  CPU Cores: ${report.server.cpuCores}`)
  print(`  Memory: ${report.server.memSizeMB} MB`)
  print()
  
  // Database Summary
  print("═══════════════════════════════════════════════════════════════")
  print("  2. DATABASE SUMMARY")
  print("═══════════════════════════════════════════════════════════════\n")
  
  const dbs = db.adminCommand({ listDatabases: 1 }).databases
  
  dbs.forEach(database => {
    if (!['admin', 'local', 'config'].includes(database.name)) {
      const dbStats = db.getSiblingDB(database.name).stats()
      report.databases.push({
        name: database.name,
        collections: dbStats.collections,
        dataSize: dbStats.dataSize,
        indexSize: dbStats.indexSize
      })
      
      print(`  ${database.name}:`)
      print(`    Collections: ${dbStats.collections}`)
      print(`    Data: ${(dbStats.dataSize / 1024 / 1024).toFixed(2)} MB`)
      print(`    Indexes: ${(dbStats.indexSize / 1024 / 1024).toFixed(2)} MB`)
      print()
    }
  })
  
  // Performance Metrics
  print("═══════════════════════════════════════════════════════════════")
  print("  3. PERFORMANCE METRICS")
  print("═══════════════════════════════════════════════════════════════\n")
  
  const status = db.serverStatus()
  
  report.performance = {
    connections: status.connections.current,
    activeOps: db.currentOp({ active: true }).inprog.length,
    cacheUsage: status.wiredTiger?.cache 
      ? (status.wiredTiger.cache["bytes currently in the cache"] / 
         status.wiredTiger.cache["maximum bytes configured"] * 100).toFixed(1)
      : 'N/A'
  }
  
  print(`  Active Connections: ${report.performance.connections}`)
  print(`  Active Operations: ${report.performance.activeOps}`)
  print(`  Cache Usage: ${report.performance.cacheUsage}%`)
  print()
  
  // Issue Detection
  print("═══════════════════════════════════════════════════════════════")
  print("  4. DETECTED ISSUES")
  print("═══════════════════════════════════════════════════════════════\n")
  
  // Check for issues
  if (status.connections.current > status.connections.available * 0.8) {
    report.issues.push("High connection usage (>80%)")
  }
  
  if (status.wiredTiger?.cache) {
    const cachePct = parseFloat(report.performance.cacheUsage)
    if (cachePct > 95) {
      report.issues.push("Critical cache usage (>95%)")
    }
  }
  
  const longOps = db.currentOp({ active: true, secs_running: { $gt: 60 } }).inprog
  if (longOps.length > 0) {
    report.issues.push(`${longOps.length} operation(s) running > 60 seconds`)
  }
  
  if (report.issues.length === 0) {
    print("  ✓ No critical issues detected")
  } else {
    report.issues.forEach(issue => {
      print(`  ⚠ ${issue}`)
    })
  }
  
  print("\n═══════════════════════════════════════════════════════════════")
  print("  END OF REPORT")
  print("═══════════════════════════════════════════════════════════════")
  
  return report
}

generateDiagnosticReport()
```

### Exercise 4: Profiler Dashboard

```javascript
// Query profiler dashboard

function profilerDashboard() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              PROFILER DASHBOARD                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Check profiler status
  const profStatus = db.getProfilingStatus()
  
  print("┌─ PROFILER STATUS ─────────────────────────────────────────┐")
  print(`│  Level: ${profStatus.was} (0=off, 1=slow, 2=all)`.padEnd(60) + "│")
  print(`│  Slow ms threshold: ${profStatus.slowms}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  if (profStatus.was === 0) {
    print("Profiler is disabled. Enable with:")
    print("  db.setProfilingLevel(1, { slowms: 100 })")
    return
  }
  
  // Get profile data
  const totalCount = db.system.profile.countDocuments()
  print(`Total profiled operations: ${totalCount}\n`)
  
  if (totalCount === 0) {
    print("No profiled operations yet")
    return
  }
  
  // Top slow operations
  print("┌─ TOP 10 SLOWEST OPERATIONS ───────────────────────────────┐")
  
  db.system.profile.find()
    .sort({ millis: -1 })
    .limit(10)
    .forEach(p => {
      const ns = (p.ns || 'N/A').substring(0, 30)
      const op = (p.op || 'N/A').padEnd(10)
      const ms = String(p.millis).padStart(8)
      print(`│  ${op} ${ns.padEnd(32)} ${ms}ms │`)
    })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Operations by type
  print("┌─ OPERATIONS BY TYPE ──────────────────────────────────────┐")
  
  const byType = db.system.profile.aggregate([
    { $group: { 
      _id: "$op", 
      count: { $sum: 1 }, 
      avgMs: { $avg: "$millis" },
      maxMs: { $max: "$millis" }
    }},
    { $sort: { count: -1 } }
  ]).toArray()
  
  byType.forEach(t => {
    const type = (t._id || 'unknown').padEnd(12)
    const count = String(t.count).padStart(6)
    const avg = t.avgMs.toFixed(0).padStart(8)
    const max = String(t.maxMs).padStart(8)
    print(`│  ${type} Count:${count}  Avg:${avg}ms  Max:${max}ms │`)
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Collection scans
  const collScans = db.system.profile.find({
    "planSummary": /COLLSCAN/
  }).limit(5).toArray()
  
  if (collScans.length > 0) {
    print("┌─ COLLECTION SCANS (Need Indexes) ─────────────────────────┐")
    collScans.forEach(p => {
      print(`│  ${p.ns} - ${p.millis}ms`.padEnd(60) + "│")
    })
    print("└────────────────────────────────────────────────────────────┘")
  }
}

profilerDashboard()
```

---

[← Previous: Storage Engines](59-storage-engines.md) | [Next: Change Streams →](61-change-streams.md)
