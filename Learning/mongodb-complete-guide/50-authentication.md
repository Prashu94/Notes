# Chapter 50: Authentication

## Table of Contents
- [Authentication Overview](#authentication-overview)
- [Authentication Mechanisms](#authentication-mechanisms)
- [SCRAM Authentication](#scram-authentication)
- [x.509 Certificate Authentication](#x509-certificate-authentication)
- [LDAP Authentication](#ldap-authentication)
- [Kerberos Authentication](#kerberos-authentication)
- [Managing Users](#managing-users)
- [Summary](#summary)

---

## Authentication Overview

Authentication verifies the identity of users and applications connecting to MongoDB.

### Why Authentication Matters

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Authentication Flow                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Without Authentication:                                            │
│  ┌─────────┐                      ┌─────────────┐                  │
│  │ Anyone  │ ─── Direct Access ──► │  MongoDB    │  ← DANGEROUS!   │
│  └─────────┘                      └─────────────┘                  │
│                                                                     │
│  With Authentication:                                               │
│  ┌─────────┐    ┌──────────────┐    ┌─────────────┐                │
│  │ Client  │ ─► │ Authenticate │ ─► │  MongoDB    │  ← SECURE      │
│  └─────────┘    │              │    └─────────────┘                │
│                 │ - Username   │                                    │
│                 │ - Password   │                                    │
│                 │ - or Cert    │                                    │
│                 └──────────────┘                                    │
│                                                                     │
│  Authentication answers: "Who are you?"                            │
│  (Authorization answers: "What can you do?" - next chapter)        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Enable Authentication

```javascript
// Method 1: Command line
// mongod --auth --port 27017 --dbpath /data/db

// Method 2: Configuration file (mongod.conf)
/*
security:
  authorization: enabled
*/

// IMPORTANT: Create admin user BEFORE enabling auth!
```

### Authentication Database

```javascript
// Users are stored in specific databases
// The authenticationDatabase is where the user was created

// Connect with authentication database specified
// mongosh --host localhost --port 27017 -u myUser -p myPassword --authenticationDatabase admin

// Or authenticate after connecting
db.auth("myUser", "myPassword")

// Check current user
db.runCommand({ connectionStatus: 1 })
```

---

## Authentication Mechanisms

### Supported Mechanisms

| Mechanism | Description | Use Case |
|-----------|-------------|----------|
| SCRAM-SHA-256 | Default, password-based | Standard deployments |
| SCRAM-SHA-1 | Legacy password auth | Older clients |
| x.509 | Certificate-based | High security |
| LDAP | External directory | Enterprise SSO |
| Kerberos | Enterprise SSO | Windows AD integration |

### Check Available Mechanisms

```javascript
// Check server mechanisms
db.adminCommand({ getParameter: 1, authenticationMechanisms: 1 })

// Configure mechanisms in mongod.conf
/*
setParameter:
  authenticationMechanisms: 
    - SCRAM-SHA-256
    - SCRAM-SHA-1
*/
```

---

## SCRAM Authentication

SCRAM (Salted Challenge Response Authentication Mechanism) is the default.

### SCRAM-SHA-256 (Recommended)

```javascript
// Create user with SCRAM-SHA-256
use admin
db.createUser({
  user: "appUser",
  pwd: passwordPrompt(),  // Prompts for password
  roles: [
    { role: "readWrite", db: "myapp" }
  ],
  mechanisms: ["SCRAM-SHA-256"]  // Explicitly set
})

// Or with password directly (not recommended for production)
db.createUser({
  user: "appUser",
  pwd: "securePassword123!",
  roles: [
    { role: "readWrite", db: "myapp" }
  ]
})
```

### How SCRAM Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SCRAM Authentication Process                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Client sends username                                          │
│     Client ───► Server: "user: admin"                              │
│                                                                     │
│  2. Server sends challenge (salt + iteration count)                │
│     Server ───► Client: { salt: "xxx", iterationCount: 15000 }     │
│                                                                     │
│  3. Client computes proof using password                           │
│     SaltedPassword = Hi(Password, Salt, i)                         │
│     ClientProof = HMAC(ClientKey, AuthMessage)                     │
│                                                                     │
│  4. Client sends proof                                             │
│     Client ───► Server: { proof: "xxx" }                           │
│                                                                     │
│  5. Server verifies and sends server signature                     │
│     Server ───► Client: { serverSignature: "xxx" }                 │
│                                                                     │
│  ✓ Password never transmitted                                      │
│  ✓ Mutual authentication                                           │
│  ✓ Protection against replay attacks                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Connect with SCRAM

```javascript
// Connection string
// mongodb://username:password@localhost:27017/mydb?authSource=admin

// mongosh with auth
// mongosh --host localhost --port 27017 -u admin -p password --authenticationDatabase admin

// Node.js driver
const { MongoClient } = require('mongodb');
const uri = "mongodb://admin:password@localhost:27017/?authSource=admin";
const client = new MongoClient(uri);

// Python driver
from pymongo import MongoClient
client = MongoClient('mongodb://admin:password@localhost:27017/?authSource=admin')
```

---

## x.509 Certificate Authentication

x.509 uses TLS certificates for authentication.

### Generate Certificates

```bash
# Generate CA certificate
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 1826 -key ca.key -out ca.crt \
  -subj "/CN=MyMongoDB-CA"

# Generate server certificate
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr \
  -subj "/CN=mongodb-server/O=MyOrg"
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt

# Create PEM file for MongoDB
cat server.key server.crt > server.pem

# Generate client certificate
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr \
  -subj "/CN=client1/O=MyOrg"
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt
cat client.key client.crt > client.pem
```

### Configure Server for x.509

```yaml
# mongod.conf
security:
  authorization: enabled
  clusterAuthMode: x509

net:
  ssl:
    mode: requireSSL
    PEMKeyFile: /etc/mongodb/server.pem
    CAFile: /etc/mongodb/ca.crt
```

### Create x.509 User

```javascript
// The subject from certificate becomes the username
// Subject: CN=client1,O=MyOrg

use $external
db.createUser({
  user: "CN=client1,O=MyOrg",
  roles: [
    { role: "readWrite", db: "myapp" }
  ]
})
```

### Connect with x.509

```bash
# mongosh with x.509
mongosh --host localhost --port 27017 \
  --tls \
  --tlsCertificateKeyFile /path/to/client.pem \
  --tlsCAFile /path/to/ca.crt \
  --authenticationMechanism MONGODB-X509 \
  --authenticationDatabase '$external'
```

---

## LDAP Authentication

LDAP allows authentication against external directories (Enterprise only).

### LDAP Configuration

```yaml
# mongod.conf (Enterprise only)
security:
  authorization: enabled
  ldap:
    servers: "ldap.example.com"
    bind:
      queryUser: "cn=admin,dc=example,dc=com"
      queryPassword: "password"
    userToDNMapping:
      '[
        {
          match: "(.+)",
          ldapQuery: "ou=users,dc=example,dc=com??sub?(uid={0})"
        }
      ]'
    authz:
      queryTemplate: "{USER}?memberOf?base"

setParameter:
  authenticationMechanisms: PLAIN
```

### Create LDAP User Mapping

```javascript
// Map LDAP group to MongoDB role
use admin
db.createRole({
  role: "cn=developers,ou=groups,dc=example,dc=com",
  privileges: [],
  roles: [
    { role: "readWrite", db: "development" }
  ]
})
```

### Connect with LDAP

```javascript
// Connection string
// mongodb://ldapUser:ldapPassword@localhost:27017/?authSource=$external&authMechanism=PLAIN

// mongosh
// mongosh --host localhost --port 27017 \
//   -u ldapUser -p \
//   --authenticationMechanism PLAIN \
//   --authenticationDatabase '$external'
```

---

## Kerberos Authentication

Kerberos provides single sign-on for enterprise environments (Enterprise only).

### Prerequisites

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Kerberos Authentication                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Requirements:                                                      │
│  1. Kerberos KDC (Key Distribution Center)                         │
│  2. Service principal for MongoDB                                  │
│  3. Keytab file on MongoDB server                                  │
│  4. Client with valid Kerberos ticket                              │
│                                                                     │
│  ┌─────────┐     ┌─────────┐     ┌─────────────┐                  │
│  │ Client  │ ──► │   KDC   │ ──► │  MongoDB    │                  │
│  │         │     │         │     │ (Service)   │                  │
│  └─────────┘     └─────────┘     └─────────────┘                  │
│                                                                     │
│  Flow:                                                             │
│  1. Client gets TGT from KDC                                       │
│  2. Client requests service ticket for MongoDB                     │
│  3. Client presents ticket to MongoDB                              │
│  4. MongoDB validates with KDC                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Configure Kerberos

```yaml
# mongod.conf (Enterprise only)
security:
  authorization: enabled

setParameter:
  authenticationMechanisms: GSSAPI
  
# Environment variable for keytab
# export KRB5_KTNAME=/etc/mongodb/mongodb.keytab
```

### Create Kerberos User

```javascript
// Principal format: user@REALM
use $external
db.createUser({
  user: "appuser@EXAMPLE.COM",
  roles: [
    { role: "readWrite", db: "myapp" }
  ]
})
```

### Connect with Kerberos

```bash
# Get Kerberos ticket first
kinit appuser@EXAMPLE.COM

# Connect with mongosh
mongosh --host mongodb.example.com --port 27017 \
  --authenticationMechanism GSSAPI \
  --authenticationDatabase '$external' \
  --gssapiServiceName mongodb
```

---

## Managing Users

### Create Users

```javascript
// Create admin user (do this first!)
use admin
db.createUser({
  user: "adminUser",
  pwd: passwordPrompt(),
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" },
    { role: "clusterAdmin", db: "admin" }
  ]
})

// Create application user
use admin
db.createUser({
  user: "appUser",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "myapp" }
  ]
})

// Create read-only user
db.createUser({
  user: "reportUser",
  pwd: passwordPrompt(),
  roles: [
    { role: "read", db: "myapp" }
  ]
})

// Create user with custom role
db.createUser({
  user: "customUser",
  pwd: passwordPrompt(),
  roles: [
    { role: "myCustomRole", db: "admin" }
  ],
  customData: {
    department: "Engineering",
    employeeId: "12345"
  }
})
```

### View Users

```javascript
// List users in current database
use admin
db.getUsers()

// Show specific user
db.getUser("appUser")

// Show user with privileges
db.getUser("appUser", { showPrivileges: true })

// Show all users with credentials
db.getUsers({ showCredentials: true })
```

### Update Users

```javascript
// Update password
db.changeUserPassword("appUser", passwordPrompt())

// Update roles
db.updateUser("appUser", {
  roles: [
    { role: "readWrite", db: "myapp" },
    { role: "read", db: "logs" }
  ]
})

// Grant additional roles
db.grantRolesToUser("appUser", [
  { role: "read", db: "analytics" }
])

// Revoke roles
db.revokeRolesFromUser("appUser", [
  { role: "read", db: "logs" }
])

// Update custom data
db.updateUser("appUser", {
  customData: {
    department: "Data Science",
    employeeId: "12345"
  }
})
```

### Delete Users

```javascript
// Drop a user
use admin
db.dropUser("appUser")

// Drop all users (careful!)
db.dropAllUsers()
```

### User Management Best Practices

```javascript
// Best practices script
print("=== User Management Best Practices ===\n")

const practices = [
  {
    practice: "Use passwordPrompt()",
    reason: "Avoids password in shell history",
    example: "db.createUser({user:'x', pwd: passwordPrompt(), roles:[...]})"
  },
  {
    practice: "Principle of least privilege",
    reason: "Users get only needed permissions",
    example: "Give 'read' not 'readWrite' if only reading"
  },
  {
    practice: "Separate admin and app users",
    reason: "Limits damage from compromised credentials",
    example: "Don't use admin user in application connection strings"
  },
  {
    practice: "Use SCRAM-SHA-256",
    reason: "Stronger than SCRAM-SHA-1",
    example: "mechanisms: ['SCRAM-SHA-256']"
  },
  {
    practice: "Regular password rotation",
    reason: "Limits exposure from leaked credentials",
    example: "db.changeUserPassword('user', passwordPrompt())"
  },
  {
    practice: "Audit user access",
    reason: "Track who has access",
    example: "db.getUsers() regularly"
  }
]

practices.forEach((p, i) => {
  print(`${i + 1}. ${p.practice}`)
  print(`   Reason: ${p.reason}`)
  print(`   Example: ${p.example}`)
  print()
})
```

---

## Summary

### Authentication Mechanisms

| Mechanism | Type | Edition |
|-----------|------|---------|
| SCRAM-SHA-256 | Password | Community |
| SCRAM-SHA-1 | Password | Community |
| x.509 | Certificate | Community |
| LDAP | External | Enterprise |
| Kerberos/GSSAPI | External | Enterprise |

### User Management Commands

| Command | Purpose |
|---------|---------|
| db.createUser() | Create new user |
| db.getUsers() | List users |
| db.getUser() | Get user details |
| db.updateUser() | Modify user |
| db.changeUserPassword() | Update password |
| db.dropUser() | Delete user |
| db.grantRolesToUser() | Add roles |
| db.revokeRolesFromUser() | Remove roles |

### Best Practices

| Practice | Description |
|----------|-------------|
| Enable auth | Never run production without auth |
| Use strong passwords | Minimum 12 characters, mixed case |
| Least privilege | Grant minimum required permissions |
| Rotate credentials | Regular password changes |
| Separate users | Different users for different purposes |
| Use TLS | Encrypt connections |

### What's Next?

In the next chapter, we'll explore Authorization and Role-Based Access Control (RBAC).

---

## Practice Questions

1. What is the difference between authentication and authorization?
2. What is SCRAM and why is it secure?
3. How do you create a user in MongoDB?
4. What is the authentication database?
5. When would you use x.509 authentication?
6. What are the enterprise-only authentication mechanisms?
7. How do you change a user's password?
8. What command enables authentication on a MongoDB server?

---

## Hands-On Exercises

### Exercise 1: User Management System

```javascript
// Create a user management helper

const UserManager = {
  
  // Create application user
  createAppUser: function(username, database, readWrite = true) {
    const role = readWrite ? "readWrite" : "read"
    
    return db.getSiblingDB("admin").createUser({
      user: username,
      pwd: passwordPrompt(),
      roles: [
        { role: role, db: database }
      ],
      mechanisms: ["SCRAM-SHA-256"]
    })
  },
  
  // Create admin user
  createAdmin: function(username) {
    return db.getSiblingDB("admin").createUser({
      user: username,
      pwd: passwordPrompt(),
      roles: [
        { role: "root", db: "admin" }
      ],
      mechanisms: ["SCRAM-SHA-256"]
    })
  },
  
  // List all users
  listUsers: function() {
    print("=== All Users ===\n")
    
    const adminDb = db.getSiblingDB("admin")
    const users = adminDb.getUsers().users
    
    users.forEach(user => {
      print(`User: ${user.user}`)
      print(`  Database: ${user.db}`)
      print(`  Roles:`)
      user.roles.forEach(role => {
        print(`    - ${role.role} on ${role.db}`)
      })
      print()
    })
  },
  
  // Audit user permissions
  auditUser: function(username) {
    print(`=== Audit: ${username} ===\n`)
    
    const user = db.getSiblingDB("admin").getUser(username, {
      showPrivileges: true
    })
    
    if (!user) {
      print("User not found")
      return
    }
    
    print(`User: ${user.user}`)
    print(`Created: ${user._id}`)
    print(`Mechanisms: ${user.mechanisms?.join(", ") || "default"}`)
    print()
    
    print("Roles:")
    user.roles.forEach(role => {
      print(`  - ${role.role} on ${role.db}`)
    })
    print()
    
    if (user.customData) {
      print("Custom Data:")
      print(`  ${JSON.stringify(user.customData)}`)
      print()
    }
    
    if (user.inheritedPrivileges) {
      print("Effective Privileges:")
      user.inheritedPrivileges.slice(0, 10).forEach(priv => {
        print(`  ${priv.resource.db}.${priv.resource.collection || "*"}: ${priv.actions.slice(0,3).join(", ")}...`)
      })
      if (user.inheritedPrivileges.length > 10) {
        print(`  ... and ${user.inheritedPrivileges.length - 10} more`)
      }
    }
  },
  
  // Rotate password
  rotatePassword: function(username) {
    print(`Rotating password for: ${username}`)
    
    db.getSiblingDB("admin").changeUserPassword(username, passwordPrompt())
    print("✓ Password updated")
    
    print("\nRemember to:")
    print("  1. Update application configurations")
    print("  2. Restart dependent services")
    print("  3. Test connectivity")
  },
  
  // Disable user (remove all roles)
  disableUser: function(username) {
    const user = db.getSiblingDB("admin").getUser(username)
    
    if (!user) {
      print("User not found")
      return
    }
    
    db.getSiblingDB("admin").updateUser(username, {
      roles: [],
      customData: {
        ...user.customData,
        disabled: true,
        disabledAt: new Date()
      }
    })
    
    print(`✓ User ${username} disabled`)
  }
}

// Usage:
// UserManager.createAppUser("myAppUser", "mydb")
// UserManager.listUsers()
// UserManager.auditUser("myAppUser")
// UserManager.rotatePassword("myAppUser")
// UserManager.disableUser("myAppUser")
```

### Exercise 2: Authentication Checker

```javascript
// Check authentication status and configuration

function authenticationChecker() {
  print("=== Authentication Checker ===\n")
  
  // Check if connected
  print("1. Connection Status:")
  const status = db.runCommand({ connectionStatus: 1 })
  
  if (status.authInfo.authenticatedUsers.length > 0) {
    print("   ✓ Authenticated as:")
    status.authInfo.authenticatedUsers.forEach(u => {
      print(`     ${u.user}@${u.db}`)
    })
  } else {
    print("   ! Not authenticated")
  }
  print()
  
  // Check authentication mechanisms
  print("2. Available Mechanisms:")
  try {
    const mechanisms = db.adminCommand({
      getParameter: 1,
      authenticationMechanisms: 1
    })
    mechanisms.authenticationMechanisms.forEach(m => {
      print(`   - ${m}`)
    })
  } catch (e) {
    print("   Unable to check (need admin privileges)")
  }
  print()
  
  // Check if auth is enabled
  print("3. Authorization Status:")
  try {
    // Try to list users - will fail if no auth
    const users = db.getSiblingDB("admin").getUsers()
    print("   ✓ Authorization appears to be enabled")
  } catch (e) {
    if (e.message.includes("unauthorized")) {
      print("   ✓ Authorization is enabled")
    } else {
      print("   ! Could not determine status")
    }
  }
  print()
  
  // Check current roles
  print("4. Current User Roles:")
  if (status.authInfo.authenticatedUserRoles.length > 0) {
    status.authInfo.authenticatedUserRoles.forEach(r => {
      print(`   - ${r.role} on ${r.db}`)
    })
  } else {
    print("   No roles (or not authenticated)")
  }
}

authenticationChecker()
```

### Exercise 3: Secure Setup Script

```javascript
// Script to set up authentication on a new deployment

function secureSetup() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           MongoDB Secure Setup                              ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Check if running localhost exception
  print("Step 1: Creating Admin User")
  print("─".repeat(40))
  
  try {
    db.getSiblingDB("admin").createUser({
      user: "superAdmin",
      pwd: "CHANGE_THIS_PASSWORD",  // In real setup: passwordPrompt()
      roles: [
        { role: "root", db: "admin" }
      ]
    })
    print("✓ Admin user created")
  } catch (e) {
    if (e.code === 51003) {
      print("! Admin user already exists")
    } else {
      print(`✗ Error: ${e.message}`)
      return
    }
  }
  print()
  
  print("Step 2: Creating Application User")
  print("─".repeat(40))
  
  try {
    db.getSiblingDB("admin").createUser({
      user: "appUser",
      pwd: "CHANGE_THIS_PASSWORD",  // In real setup: passwordPrompt()
      roles: [
        { role: "readWrite", db: "application" }
      ]
    })
    print("✓ Application user created")
  } catch (e) {
    if (e.code === 51003) {
      print("! Application user already exists")
    } else {
      print(`✗ Error: ${e.message}`)
    }
  }
  print()
  
  print("Step 3: Creating Backup User")
  print("─".repeat(40))
  
  try {
    db.getSiblingDB("admin").createUser({
      user: "backupUser",
      pwd: "CHANGE_THIS_PASSWORD",
      roles: [
        { role: "backup", db: "admin" }
      ]
    })
    print("✓ Backup user created")
  } catch (e) {
    if (e.code === 51003) {
      print("! Backup user already exists")
    } else {
      print(`✗ Error: ${e.message}`)
    }
  }
  print()
  
  print("Step 4: Creating Monitoring User")
  print("─".repeat(40))
  
  try {
    db.getSiblingDB("admin").createUser({
      user: "monitorUser",
      pwd: "CHANGE_THIS_PASSWORD",
      roles: [
        { role: "clusterMonitor", db: "admin" }
      ]
    })
    print("✓ Monitoring user created")
  } catch (e) {
    if (e.code === 51003) {
      print("! Monitoring user already exists")
    } else {
      print(`✗ Error: ${e.message}`)
    }
  }
  print()
  
  print("═".repeat(60))
  print("\n✓ Setup Complete!\n")
  
  print("IMPORTANT NEXT STEPS:")
  print("1. Change all passwords using db.changeUserPassword()")
  print("2. Enable authorization in mongod.conf:")
  print("   security:")
  print("     authorization: enabled")
  print("3. Restart MongoDB")
  print("4. Connect with: mongosh -u superAdmin -p --authenticationDatabase admin")
  print()
  
  print("Users Created:")
  print("  superAdmin - Full admin access")
  print("  appUser    - Read/write to 'application' database")
  print("  backupUser - Backup operations")
  print("  monitorUser - Cluster monitoring")
}

// Run setup
// secureSetup()
```

### Exercise 4: Connection String Builder

```javascript
// Build secure connection strings

function buildConnectionString(options) {
  const {
    hosts = ["localhost:27017"],
    username,
    password,
    database = "",
    authSource = "admin",
    replicaSet,
    tls = false,
    tlsCAFile,
    authMechanism
  } = options
  
  let uri = "mongodb://"
  
  // Credentials
  if (username && password) {
    uri += `${encodeURIComponent(username)}:${encodeURIComponent(password)}@`
  }
  
  // Hosts
  uri += hosts.join(",")
  
  // Database
  uri += `/${database}`
  
  // Options
  const params = []
  
  if (authSource) {
    params.push(`authSource=${authSource}`)
  }
  
  if (replicaSet) {
    params.push(`replicaSet=${replicaSet}`)
  }
  
  if (tls) {
    params.push("tls=true")
    if (tlsCAFile) {
      params.push(`tlsCAFile=${encodeURIComponent(tlsCAFile)}`)
    }
  }
  
  if (authMechanism) {
    params.push(`authMechanism=${authMechanism}`)
  }
  
  if (params.length > 0) {
    uri += "?" + params.join("&")
  }
  
  return uri
}

// Examples
print("=== Connection String Examples ===\n")

// Simple local connection
print("1. Local with auth:")
print(buildConnectionString({
  username: "appUser",
  password: "myPassword",
  database: "myapp"
}))
print()

// Replica set
print("2. Replica Set:")
print(buildConnectionString({
  hosts: ["mongo1:27017", "mongo2:27017", "mongo3:27017"],
  username: "appUser",
  password: "myPassword",
  database: "myapp",
  replicaSet: "rs0"
}))
print()

// With TLS
print("3. With TLS:")
print(buildConnectionString({
  hosts: ["secure-mongo.example.com:27017"],
  username: "appUser",
  password: "myPassword",
  database: "myapp",
  tls: true,
  tlsCAFile: "/path/to/ca.crt"
}))
print()

// LDAP
print("4. LDAP (Enterprise):")
print(buildConnectionString({
  username: "ldapUser",
  password: "ldapPassword",
  database: "myapp",
  authSource: "$external",
  authMechanism: "PLAIN"
}))
```

### Exercise 5: Authentication Audit Report

```javascript
// Generate authentication audit report

function authenticationAuditReport() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           AUTHENTICATION AUDIT REPORT                       ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Generated: ${new Date().toISOString()}\n`)
  
  const adminDb = db.getSiblingDB("admin")
  
  // 1. User Summary
  print("┌─ USER SUMMARY ─────────────────────────────────────────────┐")
  
  let totalUsers = 0
  let usersWithRoot = 0
  let usersWithWeakMechanisms = 0
  
  try {
    const users = adminDb.getUsers({ showCredentials: true }).users
    totalUsers = users.length
    
    users.forEach(user => {
      // Check for root role
      user.roles.forEach(role => {
        if (role.role === "root" || role.role === "userAdminAnyDatabase") {
          usersWithRoot++
        }
      })
      
      // Check mechanisms
      if (user.mechanisms?.includes("SCRAM-SHA-1") && 
          !user.mechanisms?.includes("SCRAM-SHA-256")) {
        usersWithWeakMechanisms++
      }
    })
  } catch (e) {
    print("│  Unable to retrieve user information")
    print("│  (Requires userAdmin or root role)")
    print("└────────────────────────────────────────────────────────────┘")
    return
  }
  
  print(`│  Total Users: ${totalUsers}`.padEnd(60) + "│")
  print(`│  Users with Root/Admin: ${usersWithRoot}`.padEnd(60) + "│")
  print(`│  Users with Legacy Auth Only: ${usersWithWeakMechanisms}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 2. User Details
  print("┌─ USER DETAILS ─────────────────────────────────────────────┐")
  
  const users = adminDb.getUsers().users
  users.forEach(user => {
    const hasRoot = user.roles.some(r => r.role === "root")
    const flag = hasRoot ? " [ADMIN]" : ""
    
    print(`│`.padEnd(60) + "│")
    print(`│  ${user.user}${flag}`.padEnd(60) + "│")
    print(`│    Database: ${user.db}`.padEnd(60) + "│")
    
    const roleList = user.roles.map(r => `${r.role}@${r.db}`).join(", ")
    const roleDisplay = roleList.length > 45 ? roleList.substring(0, 42) + "..." : roleList
    print(`│    Roles: ${roleDisplay}`.padEnd(60) + "│")
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 3. Recommendations
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  
  const recommendations = []
  
  if (usersWithRoot > 2) {
    recommendations.push("⚠ Too many admin users - review and reduce")
  }
  
  if (usersWithWeakMechanisms > 0) {
    recommendations.push("⚠ Upgrade users to SCRAM-SHA-256")
  }
  
  // Check for default user
  const hasDefaultAdmin = users.some(u => u.user === "admin" || u.user === "root")
  if (hasDefaultAdmin) {
    recommendations.push("⚠ Using default admin username - consider changing")
  }
  
  if (recommendations.length === 0) {
    print("│  ✓ No issues found".padEnd(60) + "│")
  } else {
    recommendations.forEach(r => {
      print(`│  ${r}`.padEnd(60) + "│")
    })
  }
  
  print("└────────────────────────────────────────────────────────────┘")
}

// Generate report
authenticationAuditReport()
```

---

[← Previous: Sharded Cluster Administration](49-sharded-cluster-administration.md) | [Next: Authorization and RBAC →](51-authorization-rbac.md)
