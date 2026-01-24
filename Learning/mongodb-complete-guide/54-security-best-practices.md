# Chapter 54: Security Best Practices

## Table of Contents
- [Security Checklist](#security-checklist)
- [Network Security](#network-security)
- [Authentication Best Practices](#authentication-best-practices)
- [Authorization Best Practices](#authorization-best-practices)
- [Encryption Best Practices](#encryption-best-practices)
- [Operational Security](#operational-security)
- [Security Monitoring](#security-monitoring)
- [Summary](#summary)

---

## Security Checklist

### Essential Security Configuration

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Security Checklist                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ☐ Authentication                                                  │
│    ☐ Enable authentication (--auth or security.authorization)     │
│    ☐ Create admin user before enabling auth                       │
│    ☐ Use strong passwords (12+ chars, mixed case, symbols)        │
│    ☐ Use SCRAM-SHA-256 mechanism                                  │
│                                                                     │
│  ☐ Authorization                                                   │
│    ☐ Apply principle of least privilege                           │
│    ☐ Create role-based access control                             │
│    ☐ Use custom roles for fine-grained control                    │
│    ☐ Regularly audit user permissions                             │
│                                                                     │
│  ☐ Network Security                                                │
│    ☐ Bind to specific IP addresses (not 0.0.0.0)                  │
│    ☐ Enable TLS/SSL for all connections                           │
│    ☐ Use firewalls to restrict access                             │
│    ☐ Disable unused network interfaces                            │
│                                                                     │
│  ☐ Encryption                                                      │
│    ☐ Enable TLS for client connections                            │
│    ☐ Enable TLS for replica set members                           │
│    ☐ Enable encryption at rest (Enterprise)                       │
│    ☐ Use CSFLE for sensitive fields                               │
│                                                                     │
│  ☐ Auditing                                                        │
│    ☐ Enable audit logging (Enterprise)                            │
│    ☐ Configure appropriate audit filters                          │
│    ☐ Implement log retention policy                               │
│                                                                     │
│  ☐ Operational                                                     │
│    ☐ Keep MongoDB updated                                         │
│    ☐ Disable unnecessary features                                 │
│    ☐ Implement backup strategy                                    │
│    ☐ Test recovery procedures                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Security Assessment Script

```javascript
function securityAssessment() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           MONGODB SECURITY ASSESSMENT                       ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const issues = []
  const warnings = []
  const passed = []
  
  // Check 1: Authentication enabled
  print("1. Authentication Status")
  const authStatus = db.runCommand({ connectionStatus: 1 })
  if (authStatus.authInfo.authenticatedUsers.length > 0) {
    passed.push("Authentication is enabled")
    print("   ✓ Authentication enabled")
  } else {
    // Try to list users - if it works without auth, auth is disabled
    try {
      const users = db.getSiblingDB("admin").getUsers()
      if (users.users?.length === 0) {
        issues.push("No users created - authentication may be disabled")
        print("   ✗ No users found")
      }
    } catch (e) {
      passed.push("Authentication appears to be enabled")
      print("   ✓ Authentication required")
    }
  }
  
  // Check 2: Network binding
  print("\n2. Network Binding")
  try {
    const params = db.adminCommand({ getCmdLineOpts: 1 })
    const bindIp = params.parsed?.net?.bindIp || 'localhost'
    
    if (bindIp === '0.0.0.0' || bindIp.includes('0.0.0.0')) {
      issues.push("MongoDB bound to all interfaces (0.0.0.0)")
      print("   ✗ Bound to all interfaces - security risk")
    } else {
      passed.push(`Network bound to: ${bindIp}`)
      print(`   ✓ Bound to: ${bindIp}`)
    }
  } catch (e) {
    warnings.push("Could not check network binding")
    print("   ? Unable to check (requires admin)")
  }
  
  // Check 3: TLS/SSL
  print("\n3. TLS/SSL Status")
  try {
    const serverStatus = db.adminCommand({ serverStatus: 1 })
    const tlsInfo = serverStatus.security
    
    if (tlsInfo?.SSLServerSubjectName) {
      passed.push("TLS is enabled")
      print("   ✓ TLS enabled")
    } else {
      warnings.push("TLS may not be enabled")
      print("   ? TLS status unclear")
    }
  } catch (e) {
    warnings.push("Could not check TLS status")
    print("   ? Unable to verify TLS")
  }
  
  // Check 4: User count
  print("\n4. User Management")
  try {
    const users = db.getSiblingDB("admin").getUsers().users
    const adminUsers = users.filter(u => 
      u.roles.some(r => r.role === 'root' || r.role === 'userAdminAnyDatabase')
    )
    
    print(`   Total users: ${users.length}`)
    print(`   Admin users: ${adminUsers.length}`)
    
    if (adminUsers.length > 3) {
      warnings.push(`High number of admin users: ${adminUsers.length}`)
      print("   ⚠ Consider reducing admin users")
    } else {
      passed.push("Reasonable number of admin users")
    }
  } catch (e) {
    print("   ? Unable to check users")
  }
  
  // Summary
  print("\n" + "═".repeat(60))
  print("\nSummary:")
  print(`  ✓ Passed: ${passed.length}`)
  print(`  ⚠ Warnings: ${warnings.length}`)
  print(`  ✗ Issues: ${issues.length}`)
  
  if (issues.length > 0) {
    print("\nCritical Issues:")
    issues.forEach(i => print(`  • ${i}`))
  }
  
  if (warnings.length > 0) {
    print("\nWarnings:")
    warnings.forEach(w => print(`  • ${w}`))
  }
  
  // Score
  const total = passed.length + warnings.length + issues.length
  const score = Math.round((passed.length / total) * 100)
  print(`\nSecurity Score: ${score}%`)
  
  return { passed, warnings, issues, score }
}

securityAssessment()
```

---

## Network Security

### Bind to Specific Interfaces

```yaml
# mongod.conf
net:
  port: 27017
  bindIp: 127.0.0.1,192.168.1.100  # Only these IPs
  # Never use 0.0.0.0 in production!
```

### Firewall Configuration

```bash
# Linux (iptables)
# Allow MongoDB from specific IP
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 27017 -j ACCEPT
# Block all other MongoDB access
iptables -A INPUT -p tcp --dport 27017 -j DROP

# Linux (firewalld)
firewall-cmd --permanent --add-rich-rule='
  rule family="ipv4"
  source address="192.168.1.0/24"
  port port="27017" protocol="tcp"
  accept'
firewall-cmd --reload

# AWS Security Group (conceptual)
# Inbound rule:
# - Type: Custom TCP
# - Port: 27017
# - Source: Application server security group
```

### VPN/Private Network

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Recommended Network Architecture                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Internet                                                          │
│      │                                                             │
│      ▼                                                             │
│  ┌──────────────────┐                                              │
│  │ Load Balancer    │  (Public Subnet)                             │
│  │ (HTTPS only)     │                                              │
│  └────────┬─────────┘                                              │
│           │                                                        │
│  ─────────┼─────────────────────────────────────────────────────   │
│           │  (Private Subnet)                                      │
│           ▼                                                        │
│  ┌──────────────────┐                                              │
│  │ Application      │                                              │
│  │ Servers          │                                              │
│  └────────┬─────────┘                                              │
│           │                                                        │
│  ─────────┼─────────────────────────────────────────────────────   │
│           │  (Database Subnet - Most Restricted)                   │
│           ▼                                                        │
│  ┌──────────────────┐                                              │
│  │ MongoDB          │  • No public IP                              │
│  │ Cluster          │  • Only app servers can connect              │
│  │                  │  • TLS required                              │
│  └──────────────────┘                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Authentication Best Practices

### Strong Password Policy

```javascript
// Password requirements
const passwordPolicy = {
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSymbols: true,
  noUsername: true,
  noCommonWords: true
}

// Password generator helper
function generateSecurePassword(length = 16) {
  const upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const lower = 'abcdefghijklmnopqrstuvwxyz'
  const numbers = '0123456789'
  const symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?'
  const all = upper + lower + numbers + symbols
  
  let password = ''
  // Ensure at least one of each type
  password += upper[Math.floor(Math.random() * upper.length)]
  password += lower[Math.floor(Math.random() * lower.length)]
  password += numbers[Math.floor(Math.random() * numbers.length)]
  password += symbols[Math.floor(Math.random() * symbols.length)]
  
  // Fill rest randomly
  for (let i = password.length; i < length; i++) {
    password += all[Math.floor(Math.random() * all.length)]
  }
  
  // Shuffle
  return password.split('').sort(() => Math.random() - 0.5).join('')
}

// Validate password strength
function validatePassword(password, username) {
  const issues = []
  
  if (password.length < 12) {
    issues.push('Password must be at least 12 characters')
  }
  if (!/[A-Z]/.test(password)) {
    issues.push('Password must contain uppercase letter')
  }
  if (!/[a-z]/.test(password)) {
    issues.push('Password must contain lowercase letter')
  }
  if (!/[0-9]/.test(password)) {
    issues.push('Password must contain number')
  }
  if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
    issues.push('Password must contain symbol')
  }
  if (username && password.toLowerCase().includes(username.toLowerCase())) {
    issues.push('Password cannot contain username')
  }
  
  return {
    valid: issues.length === 0,
    issues
  }
}
```

### User Management Standards

```javascript
// Create users with proper configuration
function createSecureUser(config) {
  const {
    username,
    database,
    roles,
    description
  } = config
  
  // Validate
  if (!username || !database || !roles) {
    throw new Error('Missing required fields')
  }
  
  // Use passwordPrompt() in real scenarios
  const password = generateSecurePassword(16)
  
  db.getSiblingDB(database).createUser({
    user: username,
    pwd: password,
    roles: roles,
    mechanisms: ['SCRAM-SHA-256'],
    customData: {
      description: description || '',
      createdAt: new Date(),
      createdBy: db.runCommand({ connectionStatus: 1 })
        .authInfo.authenticatedUsers[0]?.user || 'system'
    }
  })
  
  print(`User '${username}' created successfully`)
  print(`Password: ${password}`)
  print('IMPORTANT: Change this password immediately!')
  
  return { username, database }
}

// Example: Create application user
/*
createSecureUser({
  username: 'appUser',
  database: 'admin',
  roles: [{ role: 'readWrite', db: 'myapp' }],
  description: 'Application service account'
})
*/
```

### Credential Rotation

```javascript
// Password rotation procedure
function rotateCredentials(username) {
  print(`=== Credential Rotation for ${username} ===\n`)
  
  const steps = [
    '1. Generate new password',
    '2. Update in secret manager/vault',
    '3. Update application configurations',
    '4. Deploy application updates',
    '5. Verify connectivity',
    '6. Update MongoDB password',
    '7. Verify again'
  ]
  
  print('Rotation Steps:')
  steps.forEach(step => print(`  ${step}`))
  
  print('\nTo change password:')
  print(`  db.changeUserPassword("${username}", passwordPrompt())`)
  
  print('\nPost-rotation checklist:')
  print('  ☐ Old password no longer works')
  print('  ☐ Application connects with new password')
  print('  ☐ No authentication errors in logs')
  print('  ☐ Document rotation in change log')
}
```

---

## Authorization Best Practices

### Least Privilege Implementation

```javascript
// Define minimum required roles per user type

const userProfiles = {
  // Application read/write
  'application': {
    roles: [
      { role: 'readWrite', db: 'appdata' }
    ],
    description: 'Application service account'
  },
  
  // Read-only reporting
  'reporting': {
    roles: [
      { role: 'read', db: 'appdata' },
      { role: 'read', db: 'analytics' }
    ],
    description: 'Reporting and analytics'
  },
  
  // Database admin (no data access)
  'dba': {
    roles: [
      { role: 'dbAdminAnyDatabase', db: 'admin' },
      { role: 'clusterMonitor', db: 'admin' }
    ],
    description: 'Database administration'
  },
  
  // Backup operator
  'backup': {
    roles: [
      { role: 'backup', db: 'admin' }
    ],
    description: 'Backup operations only'
  },
  
  // Monitoring
  'monitor': {
    roles: [
      { role: 'clusterMonitor', db: 'admin' }
    ],
    description: 'Monitoring only'
  }
}

function provisionUser(type, username) {
  const profile = userProfiles[type]
  
  if (!profile) {
    print(`Unknown user type: ${type}`)
    print(`Available types: ${Object.keys(userProfiles).join(', ')}`)
    return
  }
  
  print(`Creating ${type} user: ${username}`)
  print(`Roles: ${JSON.stringify(profile.roles)}`)
  print(`Description: ${profile.description}`)
  
  // In real usage:
  // db.getSiblingDB('admin').createUser({
  //   user: username,
  //   pwd: passwordPrompt(),
  //   roles: profile.roles
  // })
}
```

### Custom Role Design

```javascript
// Well-designed custom roles

// Read-only for specific collection
db.getSiblingDB('admin').createRole({
  role: 'ordersViewer',
  privileges: [
    {
      resource: { db: 'shop', collection: 'orders' },
      actions: ['find']
    }
  ],
  roles: []
})

// Update status only (no full update)
db.getSiblingDB('admin').createRole({
  role: 'orderStatusUpdater',
  privileges: [
    {
      resource: { db: 'shop', collection: 'orders' },
      actions: ['find', 'update']
      // Note: Can't restrict to specific fields via RBAC
      // Use application logic for field-level restrictions
    }
  ],
  roles: []
})

// Schema manager (no data access)
db.getSiblingDB('admin').createRole({
  role: 'schemaManager',
  privileges: [
    {
      resource: { db: 'myapp', collection: '' },
      actions: [
        'createCollection',
        'dropCollection',
        'createIndex',
        'dropIndex',
        'collMod',
        'listCollections',
        'listIndexes'
      ]
    }
  ],
  roles: []
})
```

### Regular Access Review

```javascript
function accessReview() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              USER ACCESS REVIEW                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const users = db.getSiblingDB('admin').getUsers().users
  
  // Categorize users
  const superUsers = []
  const adminUsers = []
  const regularUsers = []
  const inactiveUsers = []
  
  users.forEach(user => {
    const hasRoot = user.roles.some(r => r.role === 'root')
    const hasAdmin = user.roles.some(r => 
      ['userAdminAnyDatabase', 'dbAdminAnyDatabase', 'clusterAdmin']
      .includes(r.role)
    )
    
    if (hasRoot) {
      superUsers.push(user)
    } else if (hasAdmin) {
      adminUsers.push(user)
    } else {
      regularUsers.push(user)
    }
    
    // Check for inactive (based on customData if tracked)
    if (user.customData?.lastAccess) {
      const lastAccess = new Date(user.customData.lastAccess)
      const daysSinceAccess = (Date.now() - lastAccess) / (1000 * 60 * 60 * 24)
      if (daysSinceAccess > 90) {
        inactiveUsers.push({ ...user, daysSinceAccess })
      }
    }
  })
  
  // Report
  print("User Distribution:")
  print("─".repeat(40))
  print(`  Root/Superusers: ${superUsers.length}`)
  print(`  Admin Users: ${adminUsers.length}`)
  print(`  Regular Users: ${regularUsers.length}`)
  print()
  
  if (superUsers.length > 0) {
    print("⚠ Superusers (require justification):")
    superUsers.forEach(u => print(`  • ${u.user}@${u.db}`))
    print()
  }
  
  if (adminUsers.length > 3) {
    print("⚠ High admin count - review needed:")
    adminUsers.forEach(u => print(`  • ${u.user}@${u.db}`))
    print()
  }
  
  if (inactiveUsers.length > 0) {
    print("⚠ Inactive users (90+ days):")
    inactiveUsers.forEach(u => 
      print(`  • ${u.user}@${u.db} (${Math.floor(u.daysSinceAccess)} days)`)
    )
    print()
  }
  
  print("Recommendations:")
  print("  1. Review superuser access quarterly")
  print("  2. Disable inactive accounts")
  print("  3. Document access justifications")
  print("  4. Use service accounts for applications")
}

accessReview()
```

---

## Encryption Best Practices

### TLS Configuration Checklist

```yaml
# Production TLS configuration

net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/ssl/server.pem
    CAFile: /etc/mongodb/ssl/ca.pem
    
    # Strong cipher suites only
    disabledProtocols: TLS1_0,TLS1_1
    
    # Require client certificate (mutual TLS)
    # clusterFile: /etc/mongodb/ssl/cluster.pem
    # allowConnectionsWithoutCertificates: false
```

### Field-Level Encryption Guidelines

```javascript
// Data classification for encryption

const dataClassification = {
  // Always encrypt
  highSensitivity: [
    'ssn',
    'taxId',
    'creditCard',
    'bankAccount',
    'password',
    'secretKey'
  ],
  
  // Encrypt when possible
  mediumSensitivity: [
    'dateOfBirth',
    'address',
    'phone',
    'email',
    'salary',
    'medicalInfo'
  ],
  
  // Generally okay unencrypted
  lowSensitivity: [
    'name',
    'username',
    'publicProfile'
  ]
}

// Encryption decision helper
function shouldEncrypt(fieldName, dataType) {
  const lower = fieldName.toLowerCase()
  
  if (dataClassification.highSensitivity.some(f => lower.includes(f))) {
    return { encrypt: true, algorithm: 'random', reason: 'High sensitivity data' }
  }
  
  if (dataClassification.mediumSensitivity.some(f => lower.includes(f))) {
    return { encrypt: true, algorithm: 'deterministic', reason: 'Medium sensitivity - queryable' }
  }
  
  return { encrypt: false, reason: 'Low sensitivity' }
}

// Test
print("Field encryption recommendations:")
['ssn', 'email', 'name', 'creditCardNumber', 'phoneNumber'].forEach(field => {
  const rec = shouldEncrypt(field)
  print(`  ${field}: ${rec.encrypt ? `Encrypt (${rec.algorithm})` : 'No encryption'} - ${rec.reason}`)
})
```

---

## Operational Security

### Secure Configuration Baseline

```yaml
# mongod.conf - Security hardened

# Logging
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  verbosity: 0  # Don't log excessively
  
# Network
net:
  port: 27017
  bindIp: 127.0.0.1,10.0.1.100  # Specific IPs only
  maxIncomingConnections: 1000
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/ssl/server.pem
    CAFile: /etc/mongodb/ssl/ca.pem

# Security
security:
  authorization: enabled
  javascriptEnabled: false  # Disable unless needed
  
# Auditing (Enterprise)
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: '{ "atype": { "$in": ["authenticate", "createUser", "dropUser"] } }'

# Operations
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100
```

### Disable Unnecessary Features

```javascript
// Disable JavaScript execution (if not needed)
// Set in mongod.conf: security.javascriptEnabled: false

// This disables:
// - $where queries
// - mapReduce with JavaScript
// - $function aggregation operator
// - $accumulator with JavaScript

// Alternative: Use aggregation operators instead
// Instead of: { $where: "this.a > this.b" }
// Use: { $expr: { $gt: ["$a", "$b"] } }
```

### Secure Backup Procedures

```javascript
// Backup security checklist

const backupChecklist = {
  beforeBackup: [
    'Verify backup user has only backup role',
    'Ensure backup destination is secure',
    'Check encryption for backup files',
    'Verify network path is encrypted'
  ],
  
  duringBackup: [
    'Use mongodump with --ssl',
    'Encrypt backup files at rest',
    'Log backup operations',
    'Monitor for anomalies'
  ],
  
  afterBackup: [
    'Verify backup integrity',
    'Move to secure long-term storage',
    'Update backup inventory',
    'Test restore periodically'
  ],
  
  retention: [
    'Define retention policy',
    'Securely delete expired backups',
    'Document disposal'
  ]
}

// Secure mongodump command
const secureDumpCommand = `
mongodump \\
  --ssl \\
  --sslCAFile /path/to/ca.pem \\
  --host mongodb.example.com \\
  --username backupUser \\
  --authenticationDatabase admin \\
  --out /secure/backup/location \\
  --gzip
`
```

---

## Security Monitoring

### Security Event Detection

```javascript
function securityMonitor() {
  print("=== Security Event Monitor ===\n")
  
  // This would connect to audit logs in practice
  // Here we simulate checking common security events
  
  const checksToRun = [
    {
      name: 'Failed Authentication Attempts',
      check: () => {
        // In practice: query audit logs
        return { status: 'ok', count: 0 }
      }
    },
    {
      name: 'Admin Role Changes',
      check: () => {
        return { status: 'ok', count: 0 }
      }
    },
    {
      name: 'Unusual Connection Sources',
      check: () => {
        return { status: 'ok', count: 0 }
      }
    },
    {
      name: 'Schema Changes',
      check: () => {
        return { status: 'ok', count: 0 }
      }
    }
  ]
  
  checksToRun.forEach(check => {
    const result = check.check()
    const icon = result.status === 'ok' ? '✓' : '⚠'
    print(`${icon} ${check.name}: ${result.count}`)
  })
}
```

### Alert Configuration

```javascript
// Security alerts to configure

const securityAlerts = {
  critical: [
    {
      name: 'Multiple Failed Auth from Same IP',
      threshold: '5 failures in 5 minutes',
      action: 'Block IP, alert security team'
    },
    {
      name: 'Root User Login Outside Hours',
      threshold: 'Any login between 10PM-6AM',
      action: 'Alert security team immediately'
    },
    {
      name: 'Data Export Large Volume',
      threshold: '>1GB exported',
      action: 'Alert and review'
    }
  ],
  
  warning: [
    {
      name: 'New Admin User Created',
      threshold: 'Any',
      action: 'Alert database team'
    },
    {
      name: 'Collection Dropped',
      threshold: 'Any production collection',
      action: 'Alert database team'
    }
  ],
  
  info: [
    {
      name: 'New Connection Source',
      threshold: 'Previously unseen IP',
      action: 'Log for review'
    }
  ]
}

function printAlertConfig() {
  print("=== Recommended Security Alerts ===\n")
  
  Object.entries(securityAlerts).forEach(([severity, alerts]) => {
    print(`${severity.toUpperCase()} Alerts:`)
    print("─".repeat(40))
    alerts.forEach(alert => {
      print(`  ${alert.name}`)
      print(`    Threshold: ${alert.threshold}`)
      print(`    Action: ${alert.action}`)
    })
    print()
  })
}

printAlertConfig()
```

---

## Summary

### Security Layers

| Layer | Implementation |
|-------|---------------|
| Network | Firewalls, VPN, private subnets |
| Transport | TLS/SSL encryption |
| Authentication | SCRAM-SHA-256, x.509 |
| Authorization | RBAC, custom roles |
| Data | Encryption at rest, CSFLE |
| Audit | Logging, monitoring |

### Quick Reference

| Task | Command/Config |
|------|----------------|
| Enable auth | security.authorization: enabled |
| Enable TLS | net.tls.mode: requireTLS |
| Create user | db.createUser() |
| Create role | db.createRole() |
| Audit | auditLog.destination: file |

### Top 10 Security Rules

1. **Always enable authentication**
2. **Use TLS for all connections**
3. **Apply least privilege principle**
4. **Keep MongoDB updated**
5. **Encrypt sensitive data**
6. **Monitor and audit access**
7. **Secure network access**
8. **Rotate credentials regularly**
9. **Test backup and recovery**
10. **Document security configuration**

### What's Next?

In the next chapter, we'll begin Part 11: Administration with Backup and Recovery.

---

## Practice Questions

1. What is the principle of least privilege?
2. Why should you avoid binding to 0.0.0.0?
3. What is the minimum TLS version you should allow?
4. How often should credentials be rotated?
5. What should be in a security audit log?
6. Why disable JavaScript in MongoDB?
7. What is mutual TLS?
8. How do you securely delete old backups?

---

## Hands-On Exercises

### Exercise 1: Security Configuration Audit

```javascript
// Comprehensive security audit script

function fullSecurityAudit() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         COMPREHENSIVE SECURITY AUDIT                        ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const report = {
    timestamp: new Date().toISOString(),
    checks: [],
    score: 0,
    maxScore: 0
  }
  
  function addCheck(category, name, passed, points, details) {
    report.checks.push({ category, name, passed, points, details })
    report.maxScore += points
    if (passed) report.score += points
    
    const icon = passed ? '✓' : '✗'
    print(`  ${icon} ${name}${details ? ': ' + details : ''}`)
  }
  
  // Authentication
  print("AUTHENTICATION")
  print("─".repeat(50))
  
  const authStatus = db.runCommand({ connectionStatus: 1 })
  addCheck(
    'auth',
    'Authentication enabled',
    authStatus.authInfo.authenticatedUsers.length > 0,
    20,
    null
  )
  
  try {
    const users = db.getSiblingDB('admin').getUsers().users
    const strongMech = users.every(u => 
      u.mechanisms?.includes('SCRAM-SHA-256')
    )
    addCheck('auth', 'SCRAM-SHA-256 for all users', strongMech, 10, null)
  } catch (e) {
    addCheck('auth', 'User check', false, 10, 'Unable to check')
  }
  
  print()
  
  // Authorization
  print("AUTHORIZATION")
  print("─".repeat(50))
  
  try {
    const users = db.getSiblingDB('admin').getUsers().users
    const rootUsers = users.filter(u => 
      u.roles.some(r => r.role === 'root')
    )
    addCheck(
      'authz',
      'Limited root users',
      rootUsers.length <= 2,
      15,
      `${rootUsers.length} root users`
    )
    
    const customRoles = db.getSiblingDB('admin').getRoles()
    addCheck(
      'authz',
      'Custom roles defined',
      customRoles.length > 0,
      10,
      `${customRoles.length} custom roles`
    )
  } catch (e) {
    print(`  ? Unable to check authorization`)
  }
  
  print()
  
  // Network
  print("NETWORK")
  print("─".repeat(50))
  
  try {
    const opts = db.adminCommand({ getCmdLineOpts: 1 })
    const bindIp = opts.parsed?.net?.bindIp || 'localhost'
    const badBind = bindIp === '0.0.0.0' || bindIp.includes('0.0.0.0')
    addCheck(
      'network',
      'Restricted bind IP',
      !badBind,
      20,
      bindIp
    )
  } catch (e) {
    print(`  ? Unable to check network binding`)
  }
  
  print()
  
  // Summary
  print("═".repeat(60))
  const percentage = Math.round((report.score / report.maxScore) * 100)
  print(`\nSecurity Score: ${report.score}/${report.maxScore} (${percentage}%)`)
  
  if (percentage >= 80) {
    print("Status: GOOD - Minor improvements possible")
  } else if (percentage >= 60) {
    print("Status: FAIR - Several improvements needed")
  } else {
    print("Status: POOR - Immediate action required")
  }
  
  return report
}

fullSecurityAudit()
```

### Exercise 2: Hardening Guide Generator

```javascript
// Generate customized hardening guide

function generateHardeningGuide(options = {}) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           MONGODB HARDENING GUIDE                           ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const {
    environment = 'production',
    compliance = [],
    features = []
  } = options
  
  print(`Environment: ${environment}`)
  print(`Compliance: ${compliance.join(', ') || 'General'}`)
  print(`Features: ${features.join(', ') || 'Standard'}`)
  print("\n" + "═".repeat(60) + "\n")
  
  // Base configuration
  print("1. BASE CONFIGURATION (mongod.conf)")
  print("─".repeat(50))
  print(`
net:
  port: 27017
  bindIp: 127.0.0.1${environment === 'production' ? ',<app-server-ip>' : ''}
  tls:
    mode: ${environment === 'production' ? 'requireTLS' : 'preferTLS'}
    certificateKeyFile: /etc/mongodb/ssl/server.pem
    CAFile: /etc/mongodb/ssl/ca.pem

security:
  authorization: enabled
  javascriptEnabled: ${features.includes('mapReduce') ? 'true' : 'false'}
`)
  
  // Authentication setup
  print("\n2. AUTHENTICATION SETUP")
  print("─".repeat(50))
  print(`
# Create admin user (run once before enabling auth)
use admin
db.createUser({
  user: "admin",
  pwd: passwordPrompt(),
  roles: [{ role: "root", db: "admin" }],
  mechanisms: ["SCRAM-SHA-256"]
})

# Create application user
db.createUser({
  user: "appUser",
  pwd: passwordPrompt(),
  roles: [{ role: "readWrite", db: "application" }],
  mechanisms: ["SCRAM-SHA-256"]
})
`)
  
  // Compliance-specific
  if (compliance.includes('PCI-DSS')) {
    print("\n3. PCI-DSS REQUIREMENTS")
    print("─".repeat(50))
    print(`
# Enable auditing (Enterprise)
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: '{"atype": {"$in": ["authenticate", "authCheck", "createUser", "dropUser"]}}'

# Encrypt cardholder data
# Use Client-Side Field Level Encryption for card numbers
`)
  }
  
  // Post-configuration
  print("\n4. POST-CONFIGURATION CHECKLIST")
  print("─".repeat(50))
  print(`
☐ Enable firewall rules
☐ Configure log rotation
☐ Set up monitoring
☐ Test backup/restore
☐ Document configuration
☐ Schedule security review
`)
}

// Generate guide
generateHardeningGuide({
  environment: 'production',
  compliance: ['PCI-DSS'],
  features: ['aggregation']
})
```

### Exercise 3: Incident Response Playbook

```javascript
// Security incident response procedures

function incidentResponsePlaybook() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         INCIDENT RESPONSE PLAYBOOK                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const incidents = {
    'Failed Authentication Spike': {
      severity: 'HIGH',
      indicators: [
        'Multiple failed logins from same IP',
        'Failed logins for non-existent users',
        'Geographically unusual login locations'
      ],
      response: [
        '1. Block suspicious IPs at firewall',
        '2. Check for compromised credentials',
        '3. Review recent successful logins',
        '4. Force password reset if needed',
        '5. Enable additional logging'
      ],
      commands: [
        '// Block IP (application level)',
        '// db.runCommand({ blockIP: "x.x.x.x" }) // hypothetical',
        '',
        '// Check recent auth events',
        'db.getSiblingDB("config").changelog.find({',
        '  what: "authenticate",',
        '  time: { $gte: new Date(Date.now() - 3600000) }',
        '})'
      ]
    },
    
    'Unauthorized Data Access': {
      severity: 'CRITICAL',
      indicators: [
        'Large data exports',
        'Access from new IPs',
        'Off-hours activity'
      ],
      response: [
        '1. Immediately revoke suspected user access',
        '2. Capture current connections',
        '3. Preserve audit logs',
        '4. Determine scope of access',
        '5. Notify stakeholders'
      ],
      commands: [
        '// Disable user immediately',
        'db.updateUser("suspectUser", { roles: [] })',
        '',
        '// Kill user connections',
        'db.currentOp().inprog.forEach(op => {',
        '  if (op.user === "suspectUser") {',
        '    db.killOp(op.opid)',
        '  }',
        '})'
      ]
    },
    
    'Database Compromise': {
      severity: 'CRITICAL',
      indicators: [
        'Unexpected admin users',
        'Modified system collections',
        'Ransomware notes in databases'
      ],
      response: [
        '1. Isolate the server (network)',
        '2. Preserve evidence (don\'t restart)',
        '3. Assess scope of compromise',
        '4. Restore from known-good backup',
        '5. Investigate entry point',
        '6. Rebuild with security hardening'
      ],
      commands: [
        '// Check for rogue users',
        'db.getSiblingDB("admin").getUsers()',
        '',
        '// List all databases',
        'db.adminCommand({ listDatabases: 1 })',
        '',
        '// Check for unusual collections',
        'db.getSiblingDB("admin").getCollectionNames()'
      ]
    }
  }
  
  Object.entries(incidents).forEach(([name, details]) => {
    print(`\n${"═".repeat(60)}`)
    print(`INCIDENT: ${name}`)
    print(`SEVERITY: ${details.severity}`)
    print("═".repeat(60))
    
    print("\nIndicators:")
    details.indicators.forEach(i => print(`  • ${i}`))
    
    print("\nResponse Steps:")
    details.response.forEach(r => print(`  ${r}`))
    
    print("\nUseful Commands:")
    details.commands.forEach(c => print(`  ${c}`))
  })
}

incidentResponsePlaybook()
```

### Exercise 4: Security Metrics Dashboard

```javascript
// Security metrics collection

function securityMetrics() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           SECURITY METRICS DASHBOARD                        ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Report Time: ${new Date().toISOString()}\n`)
  
  // User metrics
  print("┌─ USER METRICS ─────────────────────────────────────────────┐")
  
  try {
    const users = db.getSiblingDB('admin').getUsers().users
    print(`│  Total Users: ${users.length}`.padEnd(60) + "│")
    
    const byRole = {}
    users.forEach(u => {
      u.roles.forEach(r => {
        byRole[r.role] = (byRole[r.role] || 0) + 1
      })
    })
    
    print(`│  Roles Distribution:`.padEnd(60) + "│")
    Object.entries(byRole)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .forEach(([role, count]) => {
        print(`│    ${role}: ${count}`.padEnd(60) + "│")
      })
  } catch (e) {
    print(`│  Unable to retrieve user metrics`.padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Connection metrics
  print("┌─ CONNECTION METRICS ──────────────────────────────────────┐")
  
  try {
    const serverStatus = db.serverStatus()
    const connections = serverStatus.connections
    
    print(`│  Current: ${connections.current}`.padEnd(60) + "│")
    print(`│  Available: ${connections.available}`.padEnd(60) + "│")
    print(`│  Total Created: ${connections.totalCreated}`.padEnd(60) + "│")
  } catch (e) {
    print(`│  Unable to retrieve connection metrics`.padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Configuration status
  print("┌─ SECURITY CONFIGURATION ──────────────────────────────────┐")
  
  const checks = [
    { name: 'Authentication', check: () => {
      const status = db.runCommand({ connectionStatus: 1 })
      return status.authInfo.authenticatedUsers.length > 0
    }},
    { name: 'Authorization', check: () => true },  // If auth works, authz is on
    { name: 'TLS', check: () => {
      try {
        const status = db.serverStatus()
        return !!status.security?.SSLServerSubjectName
      } catch { return false }
    }}
  ]
  
  checks.forEach(check => {
    const status = check.check() ? '✓ Enabled' : '✗ Disabled'
    print(`│  ${check.name}: ${status}`.padEnd(60) + "│")
  })
  
  print("└────────────────────────────────────────────────────────────┘")
}

securityMetrics()
```

### Exercise 5: Security Documentation Generator

```javascript
// Generate security documentation

function generateSecurityDocs() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         SECURITY DOCUMENTATION                              ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Generated: ${new Date().toISOString()}\n`)
  
  // User documentation
  print("## User Accounts\n")
  
  try {
    const users = db.getSiblingDB('admin').getUsers().users
    
    print("| Username | Database | Roles | Purpose |")
    print("|----------|----------|-------|---------|")
    
    users.forEach(user => {
      const roles = user.roles.map(r => `${r.role}@${r.db}`).join(', ')
      const purpose = user.customData?.description || 'Not documented'
      print(`| ${user.user} | ${user.db} | ${roles} | ${purpose} |`)
    })
  } catch (e) {
    print("Unable to document users")
  }
  
  print("\n## Custom Roles\n")
  
  try {
    const roles = db.getSiblingDB('admin').getRoles({ showPrivileges: true })
    
    if (roles.length === 0) {
      print("No custom roles defined")
    } else {
      roles.forEach(role => {
        print(`### ${role.role}\n`)
        print("Privileges:")
        role.privileges?.forEach(p => {
          print(`- ${p.resource.db}.${p.resource.collection || '*'}: ${p.actions.join(', ')}`)
        })
        print()
      })
    }
  } catch (e) {
    print("Unable to document roles")
  }
  
  print("\n## Security Configuration\n")
  print("```yaml")
  print("# Recommended configuration")
  print("security:")
  print("  authorization: enabled")
  print("net:")
  print("  tls:")
  print("    mode: requireTLS")
  print("```")
  
  print("\n## Emergency Procedures\n")
  print("1. **Disable compromised user:**")
  print("   ```javascript")
  print("   db.updateUser('username', { roles: [] })")
  print("   ```")
  print()
  print("2. **Kill all connections:**")
  print("   ```javascript")
  print("   db.currentOp().inprog.forEach(op => db.killOp(op.opid))")
  print("   ```")
}

generateSecurityDocs()
```

---

[← Previous: Auditing](53-auditing.md) | [Next: Backup and Recovery →](55-backup-recovery.md)
