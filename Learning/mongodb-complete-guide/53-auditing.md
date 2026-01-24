# Chapter 53: Auditing

## Table of Contents
- [Auditing Overview](#auditing-overview)
- [Enabling Auditing](#enabling-auditing)
- [Audit Filters](#audit-filters)
- [Audit Log Formats](#audit-log-formats)
- [Audit Event Types](#audit-event-types)
- [Log Management](#log-management)
- [Summary](#summary)

---

## Auditing Overview

Auditing tracks administrative actions and operations on MongoDB (Enterprise only).

### Why Audit

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Why Auditing Matters                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Compliance Requirements:                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ PCI DSS      - Track access to cardholder data              │  │
│  │ HIPAA        - Monitor access to health information         │  │
│  │ SOX          - Record financial data access                 │  │
│  │ GDPR         - Demonstrate data handling practices          │  │
│  │ SOC 2        - Evidence of security controls                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Security Benefits:                                                │
│  ├── Detect unauthorized access attempts                           │
│  ├── Track data changes and who made them                          │
│  ├── Investigate security incidents                                │
│  ├── Monitor privileged user activities                            │
│  └── Provide forensic evidence                                     │
│                                                                     │
│  Operational Benefits:                                             │
│  ├── Track configuration changes                                   │
│  ├── Debug application issues                                      │
│  └── Understand usage patterns                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### What Can Be Audited

| Category | Events |
|----------|--------|
| Authentication | Login attempts, failures |
| Authorization | Permission checks |
| Schema | Collection/database operations |
| CRUD | Read and write operations |
| Replication | Replica set changes |
| Sharding | Cluster configuration |

---

## Enabling Auditing

### Command Line

```bash
# Enable auditing with console output
mongod --auditDestination console

# Enable auditing with file output
mongod --auditDestination file \
  --auditFormat JSON \
  --auditPath /var/log/mongodb/audit.json

# Enable auditing with syslog
mongod --auditDestination syslog
```

### Configuration File

```yaml
# mongod.conf
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  # Optional: Apply filter
  filter: '{ "atype": { "$in": ["authenticate", "createCollection"] } }'
```

### Verify Auditing

```javascript
// Check audit configuration
db.adminCommand({ getParameter: 1, auditAuthorizationSuccess: 1 })

// View server configuration
db.adminCommand({ getCmdLineOpts: 1 })
```

---

## Audit Filters

### Filter Syntax

```javascript
// Audit filter uses query expression syntax

// Audit only authentication events
{ "atype": "authenticate" }

// Audit multiple event types
{ "atype": { "$in": ["authenticate", "createUser", "dropUser"] } }

// Audit events for specific user
{ "param.user": "admin" }

// Audit events on specific database
{ "param.ns": { "$regex": "^mydb\\." } }

// Exclude certain collections
{ "param.ns": { "$not": { "$regex": "^admin\\." } } }
```

### Common Filter Examples

```yaml
# mongod.conf examples

# Authentication and authorization only
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: |
    {
      "atype": {
        "$in": [
          "authenticate",
          "authCheck",
          "createUser",
          "dropUser",
          "updateUser",
          "grantRolesToUser",
          "revokeRolesFromUser"
        ]
      }
    }

# Schema changes only
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: |
    {
      "atype": {
        "$in": [
          "createCollection",
          "createDatabase",
          "createIndex",
          "dropCollection",
          "dropDatabase",
          "dropIndex"
        ]
      }
    }

# Specific collection access
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: |
    {
      "$or": [
        { "atype": { "$in": ["authenticate", "authCheck"] } },
        { "param.ns": "mydb.sensitive_data" }
      ]
    }
```

### Filter by Result

```javascript
// Audit only failed operations
{ "result": { "$ne": 0 } }

// Audit only successful operations
{ "result": 0 }

// Audit failed authentication attempts
{
  "atype": "authenticate",
  "result": { "$ne": 0 }
}
```

---

## Audit Log Formats

### JSON Format (Recommended)

```json
{
  "atype": "authCheck",
  "ts": { "$date": "2024-01-15T10:30:00.000Z" },
  "local": { "ip": "127.0.0.1", "port": 27017 },
  "remote": { "ip": "192.168.1.100", "port": 45678 },
  "users": [
    { "user": "appUser", "db": "admin" }
  ],
  "roles": [
    { "role": "readWrite", "db": "mydb" }
  ],
  "param": {
    "command": "find",
    "ns": "mydb.users",
    "args": {
      "find": "users",
      "filter": { "email": "user@example.com" }
    }
  },
  "result": 0
}
```

### BSON Format

```javascript
// BSON format - compact but requires parsing
// Useful for high-volume environments

// Configuration
auditLog:
  destination: file
  format: BSON
  path: /var/log/mongodb/audit.bson

// Read with bsondump
// bsondump /var/log/mongodb/audit.bson
```

### Syslog Format

```javascript
// Output to system syslog
// Useful for centralized log management

// Configuration
auditLog:
  destination: syslog
  syslogFacility: local0  // Can be user, local0-7

// Example syslog entry
// Jan 15 10:30:00 mongodb mongod: BSON ... (audit event)
```

---

## Audit Event Types

### Authentication Events

| Event Type | Description |
|------------|-------------|
| authenticate | Authentication attempt |
| authCheck | Authorization check |
| logout | User logout |

```json
// Successful authentication
{
  "atype": "authenticate",
  "ts": { "$date": "2024-01-15T10:30:00.000Z" },
  "param": {
    "user": "appUser",
    "db": "admin",
    "mechanism": "SCRAM-SHA-256"
  },
  "result": 0
}

// Failed authentication
{
  "atype": "authenticate",
  "ts": { "$date": "2024-01-15T10:30:01.000Z" },
  "param": {
    "user": "appUser",
    "db": "admin",
    "mechanism": "SCRAM-SHA-256"
  },
  "result": 18  // Authentication failed error code
}
```

### User Management Events

| Event Type | Description |
|------------|-------------|
| createUser | User created |
| dropUser | User deleted |
| updateUser | User modified |
| grantRolesToUser | Roles granted |
| revokeRolesFromUser | Roles revoked |
| dropAllUsersFromDatabase | All users dropped |

```json
// User created
{
  "atype": "createUser",
  "ts": { "$date": "2024-01-15T10:30:00.000Z" },
  "users": [{ "user": "admin", "db": "admin" }],
  "param": {
    "user": "newUser",
    "db": "mydb",
    "roles": [
      { "role": "readWrite", "db": "mydb" }
    ]
  },
  "result": 0
}
```

### Role Management Events

| Event Type | Description |
|------------|-------------|
| createRole | Role created |
| dropRole | Role deleted |
| updateRole | Role modified |
| grantPrivilegesToRole | Privileges added |
| revokePrivilegesFromRole | Privileges removed |

### Schema Events

| Event Type | Description |
|------------|-------------|
| createCollection | Collection created |
| dropCollection | Collection dropped |
| createDatabase | Database created |
| dropDatabase | Database dropped |
| createIndex | Index created |
| dropIndex | Index dropped |
| renameCollection | Collection renamed |

```json
// Collection created
{
  "atype": "createCollection",
  "ts": { "$date": "2024-01-15T10:30:00.000Z" },
  "users": [{ "user": "admin", "db": "admin" }],
  "param": {
    "ns": "mydb.newCollection"
  },
  "result": 0
}
```

### CRUD Events

```javascript
// Enable CRUD auditing (performance impact!)
// Only use when required for compliance

// Configure to audit reads
db.adminCommand({
  setParameter: 1,
  auditAuthorizationSuccess: true
})
```

```json
// Read operation
{
  "atype": "authCheck",
  "ts": { "$date": "2024-01-15T10:30:00.000Z" },
  "param": {
    "command": "find",
    "ns": "mydb.users"
  },
  "result": 0
}
```

---

## Log Management

### Log Rotation

```yaml
# mongod.conf
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  logRotate: reopen  # Use 'reopen' for external rotation

auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
```

```bash
# External log rotation (logrotate)
# /etc/logrotate.d/mongodb-audit

/var/log/mongodb/audit.json {
    daily
    rotate 30
    compress
    dateext
    notifempty
    sharedscripts
    postrotate
        /bin/kill -SIGUSR1 $(cat /var/run/mongodb/mongod.pid 2>/dev/null) 2>/dev/null || true
    endscript
}
```

### Centralized Logging

```yaml
# Send to centralized logging via syslog
auditLog:
  destination: syslog
  syslogFacility: local1

# Then configure rsyslog to forward
# /etc/rsyslog.d/mongodb-audit.conf
# local1.* @logserver.example.com:514
```

### Audit Log Analysis

```javascript
// Parse and analyze JSON audit logs

// Sample analysis script (run outside MongoDB)
/*
const fs = require('fs');
const readline = require('readline');

async function analyzeAuditLog(logPath) {
  const events = {
    byType: {},
    byUser: {},
    byResult: { success: 0, failure: 0 },
    failedAuth: []
  };
  
  const fileStream = fs.createReadStream(logPath);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity
  });
  
  for await (const line of rl) {
    try {
      const event = JSON.parse(line);
      
      // Count by type
      events.byType[event.atype] = (events.byType[event.atype] || 0) + 1;
      
      // Count by user
      event.users?.forEach(u => {
        const key = `${u.user}@${u.db}`;
        events.byUser[key] = (events.byUser[key] || 0) + 1;
      });
      
      // Count results
      if (event.result === 0) {
        events.byResult.success++;
      } else {
        events.byResult.failure++;
        
        if (event.atype === 'authenticate') {
          events.failedAuth.push({
            time: event.ts.$date,
            user: event.param?.user,
            ip: event.remote?.ip
          });
        }
      }
    } catch (e) {
      // Skip invalid lines
    }
  }
  
  return events;
}
*/
```

---

## Summary

### Audit Configuration

| Setting | Options |
|---------|---------|
| destination | file, console, syslog |
| format | JSON, BSON |
| filter | Query expression |
| path | File path (for file destination) |

### Key Event Types

| Category | Events |
|----------|--------|
| Auth | authenticate, authCheck |
| Users | createUser, dropUser, updateUser |
| Roles | createRole, dropRole |
| Schema | createCollection, dropCollection |
| CRUD | find, insert, update, delete (with authCheck) |

### Best Practices

| Practice | Reason |
|----------|--------|
| Use filters | Reduce volume, focus on important events |
| Use JSON format | Easier parsing and analysis |
| Implement log rotation | Manage disk space |
| Centralize logs | Easier monitoring |
| Regular review | Detect anomalies |

### What's Next?

In the next chapter, we'll explore Security Best Practices.

---

## Practice Questions

1. What is the purpose of MongoDB auditing?
2. What are the three audit destinations?
3. How do you filter audit events?
4. What compliance requirements may require auditing?
5. What's the difference between JSON and BSON audit formats?
6. What events should you audit for security?
7. How do you manage audit log size?
8. What is the performance impact of auditing CRUD operations?

---

## Hands-On Exercises

### Exercise 1: Audit Configuration Generator

```javascript
// Generate audit configuration based on requirements

function generateAuditConfig(requirements) {
  print("=== Audit Configuration Generator ===\n")
  
  const {
    compliance = [],
    destination = 'file',
    format = 'JSON',
    logPath = '/var/log/mongodb/audit.json'
  } = requirements
  
  // Define events for compliance frameworks
  const complianceEvents = {
    'PCI-DSS': [
      'authenticate',
      'authCheck',
      'createUser',
      'dropUser',
      'updateUser',
      'grantRolesToUser',
      'revokeRolesFromUser',
      'createRole',
      'dropRole'
    ],
    'HIPAA': [
      'authenticate',
      'authCheck',
      'createUser',
      'dropUser',
      'createCollection',
      'dropCollection'
    ],
    'SOX': [
      'authenticate',
      'createUser',
      'dropUser',
      'updateUser',
      'dropDatabase',
      'dropCollection'
    ],
    'GDPR': [
      'authenticate',
      'authCheck',
      'createUser',
      'dropUser'
    ]
  }
  
  // Collect required events
  const events = new Set()
  
  compliance.forEach(framework => {
    const frameworkEvents = complianceEvents[framework.toUpperCase()]
    if (frameworkEvents) {
      frameworkEvents.forEach(e => events.add(e))
    } else {
      print(`Warning: Unknown framework '${framework}'`)
    }
  })
  
  if (events.size === 0) {
    // Default security events
    ['authenticate', 'authCheck', 'createUser', 'dropUser'].forEach(e => events.add(e))
  }
  
  // Generate filter
  const filter = {
    atype: { $in: [...events] }
  }
  
  // Generate configuration
  const config = `
# MongoDB Audit Configuration
# Generated for: ${compliance.join(', ') || 'General Security'}
# Generated at: ${new Date().toISOString()}

auditLog:
  destination: ${destination}
  format: ${format}
  ${destination === 'file' ? `path: ${logPath}` : ''}
  filter: '${JSON.stringify(filter)}'
`
  
  print("Generated Configuration:")
  print("─".repeat(50))
  print(config)
  
  print("Events Audited:")
  print("─".repeat(50))
  events.forEach(e => print(`  - ${e}`))
  
  print("\nNext Steps:")
  print("  1. Add configuration to mongod.conf")
  print("  2. Restart MongoDB")
  print("  3. Verify with: db.adminCommand({ getCmdLineOpts: 1 })")
  
  return config
}

// Examples
print("Example 1: PCI-DSS Compliance")
generateAuditConfig({
  compliance: ['PCI-DSS'],
  destination: 'file',
  logPath: '/var/log/mongodb/audit.json'
})

print("\n\nExample 2: Multiple Frameworks")
generateAuditConfig({
  compliance: ['PCI-DSS', 'HIPAA'],
  destination: 'syslog'
})
```

### Exercise 2: Audit Log Analyzer

```javascript
// Analyze audit events (simulated)

function analyzeAuditEvents(events) {
  print("=== Audit Log Analysis ===\n")
  
  const analysis = {
    totalEvents: events.length,
    byType: {},
    byUser: {},
    byResult: { success: 0, failure: 0 },
    timeline: {},
    suspiciousActivity: []
  }
  
  events.forEach(event => {
    // Count by type
    analysis.byType[event.atype] = (analysis.byType[event.atype] || 0) + 1
    
    // Count by user
    if (event.users) {
      event.users.forEach(u => {
        const key = `${u.user}@${u.db}`
        analysis.byUser[key] = (analysis.byUser[key] || 0) + 1
      })
    }
    
    // Count results
    if (event.result === 0) {
      analysis.byResult.success++
    } else {
      analysis.byResult.failure++
      
      // Track failed auth
      if (event.atype === 'authenticate') {
        analysis.suspiciousActivity.push({
          type: 'Failed Authentication',
          time: event.ts,
          user: event.param?.user,
          ip: event.remote?.ip
        })
      }
    }
    
    // Timeline by hour
    if (event.ts) {
      const hour = event.ts.substring(11, 13) + ':00'
      analysis.timeline[hour] = (analysis.timeline[hour] || 0) + 1
    }
  })
  
  // Print report
  print(`Total Events: ${analysis.totalEvents}`)
  print(`Success: ${analysis.byResult.success}`)
  print(`Failure: ${analysis.byResult.failure}`)
  print()
  
  print("Events by Type:")
  print("─".repeat(40))
  Object.entries(analysis.byType)
    .sort((a, b) => b[1] - a[1])
    .forEach(([type, count]) => {
      const bar = "█".repeat(Math.min(count, 20))
      print(`  ${type.padEnd(25)} ${bar} ${count}`)
    })
  print()
  
  print("Top Users:")
  print("─".repeat(40))
  Object.entries(analysis.byUser)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .forEach(([user, count]) => {
      print(`  ${user}: ${count} events`)
    })
  print()
  
  if (analysis.suspiciousActivity.length > 0) {
    print("⚠ Suspicious Activity:")
    print("─".repeat(40))
    analysis.suspiciousActivity.slice(0, 5).forEach(activity => {
      print(`  ${activity.type}`)
      print(`    Time: ${activity.time}`)
      print(`    User: ${activity.user}`)
      print(`    IP: ${activity.ip}`)
    })
    if (analysis.suspiciousActivity.length > 5) {
      print(`  ... and ${analysis.suspiciousActivity.length - 5} more`)
    }
  }
  
  return analysis
}

// Simulated audit events
const sampleEvents = [
  { atype: 'authenticate', ts: '2024-01-15T10:30:00Z', users: [{user: 'admin', db: 'admin'}], result: 0, remote: {ip: '192.168.1.100'} },
  { atype: 'authenticate', ts: '2024-01-15T10:31:00Z', param: {user: 'hacker'}, result: 18, remote: {ip: '10.0.0.5'} },
  { atype: 'authenticate', ts: '2024-01-15T10:32:00Z', param: {user: 'hacker'}, result: 18, remote: {ip: '10.0.0.5'} },
  { atype: 'createCollection', ts: '2024-01-15T11:00:00Z', users: [{user: 'admin', db: 'admin'}], result: 0 },
  { atype: 'authCheck', ts: '2024-01-15T11:05:00Z', users: [{user: 'appUser', db: 'admin'}], result: 0 },
  { atype: 'authCheck', ts: '2024-01-15T11:06:00Z', users: [{user: 'appUser', db: 'admin'}], result: 0 },
  { atype: 'authCheck', ts: '2024-01-15T11:07:00Z', users: [{user: 'appUser', db: 'admin'}], result: 0 },
  { atype: 'createUser', ts: '2024-01-15T12:00:00Z', users: [{user: 'admin', db: 'admin'}], result: 0 },
  { atype: 'authenticate', ts: '2024-01-15T14:00:00Z', users: [{user: 'reportUser', db: 'admin'}], result: 0 }
]

analyzeAuditEvents(sampleEvents)
```

### Exercise 3: Security Alert Generator

```javascript
// Generate security alerts from audit events

function securityAlertGenerator(events, thresholds = {}) {
  print("=== Security Alert Generator ===\n")
  
  const defaults = {
    failedAuthThreshold: 5,     // Failed auths before alert
    failedAuthWindow: 300,      // Window in seconds
    unusualHourStart: 22,       // Unusual activity hours
    unusualHourEnd: 6,
    sensitiveCollections: ['users', 'credentials', 'payments']
  }
  
  const config = { ...defaults, ...thresholds }
  const alerts = []
  
  // Group failed auths by IP
  const failedAuthByIP = {}
  const failedAuthByUser = {}
  
  events.forEach(event => {
    // Track failed authentication
    if (event.atype === 'authenticate' && event.result !== 0) {
      const ip = event.remote?.ip || 'unknown'
      const user = event.param?.user || 'unknown'
      
      if (!failedAuthByIP[ip]) failedAuthByIP[ip] = []
      failedAuthByIP[ip].push(event)
      
      if (!failedAuthByUser[user]) failedAuthByUser[user] = []
      failedAuthByUser[user].push(event)
    }
    
    // Check for unusual hours
    if (event.ts) {
      const hour = parseInt(event.ts.substring(11, 13))
      if (hour >= config.unusualHourStart || hour < config.unusualHourEnd) {
        if (event.atype === 'createUser' || event.atype === 'dropUser') {
          alerts.push({
            severity: 'HIGH',
            type: 'Unusual Hour Activity',
            description: `${event.atype} at unusual hour (${hour}:00)`,
            event
          })
        }
      }
    }
    
    // Check sensitive collection access
    if (event.param?.ns) {
      const collection = event.param.ns.split('.')[1]
      if (config.sensitiveCollections.includes(collection)) {
        if (event.atype === 'dropCollection' || event.atype === 'dropIndex') {
          alerts.push({
            severity: 'CRITICAL',
            type: 'Sensitive Collection Modified',
            description: `${event.atype} on sensitive collection: ${event.param.ns}`,
            event
          })
        }
      }
    }
  })
  
  // Check for brute force by IP
  Object.entries(failedAuthByIP).forEach(([ip, attempts]) => {
    if (attempts.length >= config.failedAuthThreshold) {
      alerts.push({
        severity: 'HIGH',
        type: 'Possible Brute Force',
        description: `${attempts.length} failed auth attempts from IP: ${ip}`,
        ips: [ip],
        attempts: attempts.length
      })
    }
  })
  
  // Check for brute force by user
  Object.entries(failedAuthByUser).forEach(([user, attempts]) => {
    if (attempts.length >= config.failedAuthThreshold) {
      alerts.push({
        severity: 'MEDIUM',
        type: 'Account Under Attack',
        description: `${attempts.length} failed auth attempts for user: ${user}`,
        user,
        attempts: attempts.length
      })
    }
  })
  
  // Sort by severity
  const severityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }
  alerts.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity])
  
  // Print alerts
  if (alerts.length === 0) {
    print("✓ No security alerts generated")
  } else {
    print(`⚠ ${alerts.length} alert(s) generated:\n`)
    
    alerts.forEach((alert, i) => {
      const icon = alert.severity === 'CRITICAL' ? '🔴' : 
                   alert.severity === 'HIGH' ? '🟠' : 
                   alert.severity === 'MEDIUM' ? '🟡' : '🟢'
      
      print(`${icon} Alert ${i + 1}: ${alert.type}`)
      print(`   Severity: ${alert.severity}`)
      print(`   ${alert.description}`)
      print()
    })
  }
  
  return alerts
}

// Test with sample events
securityAlertGenerator(sampleEvents)
```

### Exercise 4: Compliance Report Generator

```javascript
// Generate compliance audit report

function generateComplianceReport(events, options = {}) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║            AUDIT COMPLIANCE REPORT                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const {
    framework = 'General',
    startDate = '2024-01-01',
    endDate = '2024-12-31'
  } = options
  
  print(`Framework: ${framework}`)
  print(`Period: ${startDate} to ${endDate}`)
  print(`Generated: ${new Date().toISOString()}`)
  print("\n" + "─".repeat(60) + "\n")
  
  // Summary statistics
  print("┌─ SUMMARY ─────────────────────────────────────────────────┐")
  print(`│  Total Audited Events: ${events.length}`.padEnd(60) + "│")
  
  const successful = events.filter(e => e.result === 0).length
  const failed = events.filter(e => e.result !== 0).length
  
  print(`│  Successful Operations: ${successful}`.padEnd(60) + "│")
  print(`│  Failed Operations: ${failed}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Authentication metrics
  print("┌─ AUTHENTICATION METRICS ──────────────────────────────────┐")
  
  const authEvents = events.filter(e => e.atype === 'authenticate')
  const successfulAuth = authEvents.filter(e => e.result === 0).length
  const failedAuth = authEvents.filter(e => e.result !== 0).length
  
  print(`│  Total Auth Attempts: ${authEvents.length}`.padEnd(60) + "│")
  print(`│  Successful: ${successfulAuth}`.padEnd(60) + "│")
  print(`│  Failed: ${failedAuth}`.padEnd(60) + "│")
  
  const failRate = authEvents.length > 0 
    ? (failedAuth / authEvents.length * 100).toFixed(1) 
    : 0
  print(`│  Failure Rate: ${failRate}%`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // User management
  print("┌─ USER MANAGEMENT ─────────────────────────────────────────┐")
  
  const userEvents = events.filter(e => 
    ['createUser', 'dropUser', 'updateUser', 'grantRolesToUser', 'revokeRolesFromUser']
    .includes(e.atype)
  )
  
  print(`│  User Management Events: ${userEvents.length}`.padEnd(60) + "│")
  
  const byUserEvent = {}
  userEvents.forEach(e => {
    byUserEvent[e.atype] = (byUserEvent[e.atype] || 0) + 1
  })
  
  Object.entries(byUserEvent).forEach(([type, count]) => {
    print(`│    ${type}: ${count}`.padEnd(60) + "│")
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Schema changes
  print("┌─ SCHEMA CHANGES ──────────────────────────────────────────┐")
  
  const schemaEvents = events.filter(e => 
    ['createCollection', 'dropCollection', 'createDatabase', 'dropDatabase', 
     'createIndex', 'dropIndex']
    .includes(e.atype)
  )
  
  print(`│  Schema Change Events: ${schemaEvents.length}`.padEnd(60) + "│")
  
  const bySchemaEvent = {}
  schemaEvents.forEach(e => {
    bySchemaEvent[e.atype] = (bySchemaEvent[e.atype] || 0) + 1
  })
  
  Object.entries(bySchemaEvent).forEach(([type, count]) => {
    print(`│    ${type}: ${count}`.padEnd(60) + "│")
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Compliance checklist
  print("┌─ COMPLIANCE CHECKLIST ────────────────────────────────────┐")
  
  const checks = [
    { name: 'Authentication logging', passed: authEvents.length > 0 },
    { name: 'Failed auth tracking', passed: failedAuth !== undefined },
    { name: 'User management tracking', passed: userEvents.length >= 0 },
    { name: 'Schema change tracking', passed: schemaEvents.length >= 0 }
  ]
  
  checks.forEach(check => {
    const icon = check.passed ? '✓' : '✗'
    print(`│  ${icon} ${check.name}`.padEnd(60) + "│")
  })
  
  print("└────────────────────────────────────────────────────────────┘")
  
  // Summary
  const passedChecks = checks.filter(c => c.passed).length
  print(`\nCompliance Score: ${passedChecks}/${checks.length} checks passed`)
}

// Generate report
generateComplianceReport(sampleEvents, {
  framework: 'PCI-DSS',
  startDate: '2024-01-01',
  endDate: '2024-01-31'
})
```

### Exercise 5: Audit Filter Tester

```javascript
// Test audit filters against sample events

function testAuditFilter(filter, events) {
  print("=== Audit Filter Tester ===\n")
  
  print("Filter:")
  print(JSON.stringify(filter, null, 2))
  print()
  
  // Simple filter evaluation
  function evaluateFilter(event, filter) {
    for (const [key, value] of Object.entries(filter)) {
      // Handle special operators
      if (key === '$in') {
        // Parent key needed
        continue
      }
      
      if (key === '$or') {
        return value.some(subFilter => evaluateFilter(event, subFilter))
      }
      
      if (key === '$and') {
        return value.every(subFilter => evaluateFilter(event, subFilter))
      }
      
      // Get nested value
      const eventValue = key.split('.').reduce((obj, k) => obj?.[k], event)
      
      if (typeof value === 'object' && value !== null) {
        // Handle operators
        if ('$in' in value) {
          if (!value.$in.includes(eventValue)) return false
        }
        if ('$ne' in value) {
          if (eventValue === value.$ne) return false
        }
        if ('$regex' in value) {
          if (!new RegExp(value.$regex).test(eventValue)) return false
        }
      } else {
        // Direct comparison
        if (eventValue !== value) return false
      }
    }
    return true
  }
  
  // Test each event
  const matched = []
  const notMatched = []
  
  events.forEach(event => {
    if (evaluateFilter(event, filter)) {
      matched.push(event)
    } else {
      notMatched.push(event)
    }
  })
  
  print(`Total Events: ${events.length}`)
  print(`Matched: ${matched.length}`)
  print(`Not Matched: ${notMatched.length}`)
  print()
  
  // Show matched events
  print("Matched Events:")
  print("─".repeat(40))
  matched.forEach(event => {
    print(`  ${event.atype} - ${event.users?.[0]?.user || event.param?.user || 'unknown'}`)
  })
  
  if (notMatched.length > 0 && notMatched.length <= 5) {
    print("\nNot Matched Events:")
    print("─".repeat(40))
    notMatched.forEach(event => {
      print(`  ${event.atype} - ${event.users?.[0]?.user || event.param?.user || 'unknown'}`)
    })
  }
  
  // Effectiveness
  const effectiveness = (matched.length / events.length * 100).toFixed(1)
  print(`\nFilter Effectiveness: ${effectiveness}% of events captured`)
  
  return { matched, notMatched }
}

// Test filters
print("Test 1: Authentication events only")
testAuditFilter(
  { atype: 'authenticate' },
  sampleEvents
)

print("\n\nTest 2: Multiple event types")
testAuditFilter(
  { atype: { $in: ['authenticate', 'createUser', 'authCheck'] } },
  sampleEvents
)

print("\n\nTest 3: Failed operations only")
testAuditFilter(
  { result: { $ne: 0 } },
  sampleEvents
)
```

---

[← Previous: Encryption](52-encryption.md) | [Next: Security Best Practices →](54-security-best-practices.md)
