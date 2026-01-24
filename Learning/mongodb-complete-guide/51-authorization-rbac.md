# Chapter 51: Authorization and RBAC

## Table of Contents
- [Authorization Overview](#authorization-overview)
- [Built-in Roles](#built-in-roles)
- [Database Roles](#database-roles)
- [Cluster Administration Roles](#cluster-administration-roles)
- [Custom Roles](#custom-roles)
- [Privilege Actions](#privilege-actions)
- [Role Management](#role-management)
- [Summary](#summary)

---

## Authorization Overview

Authorization determines what authenticated users can do.

### Authentication vs Authorization

```
┌─────────────────────────────────────────────────────────────────────┐
│             Authentication vs Authorization                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Authentication: "Who are you?"                                     │
│  ─────────────────────────────                                      │
│  ┌─────────────┐                                                    │
│  │ Credentials │ ─► Verified? ─► Identity Established               │
│  │ - Username  │                                                    │
│  │ - Password  │                                                    │
│  └─────────────┘                                                    │
│                                                                     │
│  Authorization: "What can you do?"                                  │
│  ─────────────────────────────────                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────┐           │
│  │ Identity    │ ─► │ Roles       │ ─► │ Permissions   │           │
│  │ (User)      │    │             │    │ - read        │           │
│  │             │    │ - readWrite │    │ - insert      │           │
│  │             │    │ - dbAdmin   │    │ - update      │           │
│  └─────────────┘    └─────────────┘    └───────────────┘           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### RBAC Concepts

| Concept | Description |
|---------|-------------|
| User | Authenticated identity |
| Role | Collection of privileges |
| Privilege | Permission for actions on resources |
| Resource | Database, collection, or cluster |
| Action | Operation like find, insert, update |

### How RBAC Works

```javascript
// User → Roles → Privileges → Actions on Resources

// Example user with multiple roles
{
  user: "appUser",
  roles: [
    { role: "readWrite", db: "orders" },
    { role: "read", db: "products" }
  ]
}

// The readWrite role includes these privileges:
// - find, insert, update, remove on collection
// - createIndex, dropIndex
// - etc.

// Check effective privileges
db.runCommand({
  connectionStatus: 1,
  showPrivileges: true
})
```

---

## Built-in Roles

### Role Categories

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Built-in Role Categories                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Database User Roles                                                │
│  ├── read              - Read all non-system collections           │
│  └── readWrite         - Read and modify data                      │
│                                                                     │
│  Database Admin Roles                                               │
│  ├── dbAdmin           - Schema management                         │
│  ├── dbOwner           - Full control of database                  │
│  └── userAdmin         - User management                           │
│                                                                     │
│  Cluster Admin Roles                                                │
│  ├── clusterAdmin      - Full cluster management                   │
│  ├── clusterManager    - Monitoring and management                 │
│  ├── clusterMonitor    - Read-only cluster monitoring              │
│  └── hostManager       - Server management                         │
│                                                                     │
│  Backup/Restore Roles                                               │
│  ├── backup            - Backup operations                         │
│  └── restore           - Restore operations                        │
│                                                                     │
│  All-Database Roles (admin db only)                                │
│  ├── readAnyDatabase                                               │
│  ├── readWriteAnyDatabase                                          │
│  ├── userAdminAnyDatabase                                          │
│  └── dbAdminAnyDatabase                                            │
│                                                                     │
│  Superuser Roles                                                   │
│  └── root              - Full admin access                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Database Roles

### read Role

```javascript
// Grants read access to all non-system collections

// Actions included:
const readActions = [
  "changeStream",
  "collStats",
  "dbHash",
  "dbStats",
  "find",
  "killCursors",
  "listIndexes",
  "listCollections"
]

// Create read-only user
use admin
db.createUser({
  user: "reportReader",
  pwd: passwordPrompt(),
  roles: [
    { role: "read", db: "sales" },
    { role: "read", db: "inventory" }
  ]
})

// This user can:
db.getSiblingDB("sales").orders.find()       // ✓ Allowed
db.getSiblingDB("sales").orders.insertOne()  // ✗ Denied
```

### readWrite Role

```javascript
// Grants read and write access

// Actions included (in addition to read):
const readWriteActions = [
  // All read actions plus:
  "convertToCapped",
  "createCollection",
  "dropCollection",
  "createIndex",
  "dropIndex",
  "insert",
  "remove",
  "renameCollectionSameDB",
  "update"
]

// Create read-write user
use admin
db.createUser({
  user: "appUser",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "application" }
  ]
})

// This user can:
db.getSiblingDB("application").data.insertOne({ x: 1 })  // ✓ Allowed
db.getSiblingDB("application").data.find()               // ✓ Allowed
db.getSiblingDB("other").data.find()                     // ✗ Denied
```

### dbAdmin Role

```javascript
// Grants database administration privileges

// Actions included:
const dbAdminActions = [
  "bypassDocumentValidation",
  "collMod",
  "collStats",
  "compact",
  "convertToCapped",
  "createCollection",
  "createIndex",
  "dbStats",
  "dropCollection",
  "dropDatabase",
  "dropIndex",
  "enableProfiler",
  "listCollections",
  "listIndexes",
  "planCacheIndexFilter",
  "planCacheClear",
  "planCacheRead",
  "planCacheWrite",
  "reIndex",
  "renameCollectionSameDB",
  "storageDetails",
  "validate"
]

// Create database admin
use admin
db.createUser({
  user: "dbAdmin",
  pwd: passwordPrompt(),
  roles: [
    { role: "dbAdmin", db: "application" }
  ]
})

// This user can manage schema but not read data!
```

### dbOwner Role

```javascript
// Combines readWrite, dbAdmin, and userAdmin

use admin
db.createUser({
  user: "databaseOwner",
  pwd: passwordPrompt(),
  roles: [
    { role: "dbOwner", db: "myDatabase" }
  ]
})

// This user can:
// - Read and write data
// - Manage schema and indexes
// - Create and manage users for this database
```

### userAdmin Role

```javascript
// Grants user and role management

// Actions included:
const userAdminActions = [
  "changeCustomData",
  "changePassword",
  "createRole",
  "createUser",
  "dropRole",
  "dropUser",
  "grantRole",
  "revokeRole",
  "setAuthenticationRestriction",
  "viewRole",
  "viewUser"
]

// Create user admin
use admin
db.createUser({
  user: "userManager",
  pwd: passwordPrompt(),
  roles: [
    { role: "userAdmin", db: "application" }
  ]
})

// IMPORTANT: userAdmin can grant any role, including root!
// Use with caution
```

---

## Cluster Administration Roles

### clusterMonitor Role

```javascript
// Read-only access to monitoring tools

use admin
db.createUser({
  user: "monitor",
  pwd: passwordPrompt(),
  roles: [
    { role: "clusterMonitor", db: "admin" }
  ]
})

// Can run:
db.serverStatus()
db.currentOp()
sh.status()
rs.status()
```

### clusterManager Role

```javascript
// Management and monitoring

use admin
db.createUser({
  user: "clusterMgr",
  pwd: passwordPrompt(),
  roles: [
    { role: "clusterManager", db: "admin" }
  ]
})

// Can manage:
// - Replica set configuration
// - Sharding
// - But NOT user management
```

### clusterAdmin Role

```javascript
// Full cluster administration

use admin
db.createUser({
  user: "clusterAdmin",
  pwd: passwordPrompt(),
  roles: [
    { role: "clusterAdmin", db: "admin" }
  ]
})

// Includes clusterManager, clusterMonitor, hostManager
// Can do everything cluster-related
```

### Backup and Restore Roles

```javascript
// backup role
use admin
db.createUser({
  user: "backupOperator",
  pwd: passwordPrompt(),
  roles: [
    { role: "backup", db: "admin" }
  ]
})

// Can use mongodump

// restore role
db.createUser({
  user: "restoreOperator",
  pwd: passwordPrompt(),
  roles: [
    { role: "restore", db: "admin" }
  ]
})

// Can use mongorestore
```

---

## Custom Roles

### Create Custom Role

```javascript
// Create role with specific privileges

use admin
db.createRole({
  role: "orderProcessor",
  privileges: [
    // Read orders
    {
      resource: { db: "shop", collection: "orders" },
      actions: ["find"]
    },
    // Update order status only
    {
      resource: { db: "shop", collection: "orders" },
      actions: ["update"]
    },
    // Read products
    {
      resource: { db: "shop", collection: "products" },
      actions: ["find"]
    }
  ],
  roles: []  // No inherited roles
})

// Assign to user
db.createUser({
  user: "orderClerk",
  pwd: passwordPrompt(),
  roles: [
    { role: "orderProcessor", db: "admin" }
  ]
})
```

### Role with Inheritance

```javascript
// Create role that inherits from others

use admin
db.createRole({
  role: "seniorDeveloper",
  privileges: [
    // Additional privileges beyond inherited roles
    {
      resource: { db: "development", collection: "" },
      actions: ["createCollection", "dropCollection"]
    }
  ],
  roles: [
    // Inherit from these roles
    { role: "readWrite", db: "development" },
    { role: "read", db: "production" },
    { role: "dbAdmin", db: "development" }
  ]
})
```

### Collection-Specific Role

```javascript
// Role for specific collection only

use admin
db.createRole({
  role: "userProfileManager",
  privileges: [
    {
      resource: { 
        db: "application", 
        collection: "userProfiles" 
      },
      actions: [
        "find",
        "insert",
        "update",
        // No "remove" - can't delete profiles
      ]
    }
  ],
  roles: []
})
```

### Role with Document-Level Restrictions

```javascript
// View role - limits visible fields

use admin
db.createRole({
  role: "limitedUserViewer",
  privileges: [
    {
      resource: { db: "app", collection: "users" },
      actions: ["find"],
      // Note: For field-level security, use views instead
    }
  ],
  roles: []
})

// Better approach: Create a view
use app
db.createView(
  "publicUserInfo",        // View name
  "users",                 // Source collection
  [
    { $project: {
      name: 1,
      email: 1,
      department: 1
      // Excludes: password, salary, SSN, etc.
    }}
  ]
)

// Then grant read on the view
db.getSiblingDB("admin").createRole({
  role: "publicUserViewer",
  privileges: [
    {
      resource: { db: "app", collection: "publicUserInfo" },
      actions: ["find"]
    }
  ],
  roles: []
})
```

---

## Privilege Actions

### Common Actions

| Action | Description |
|--------|-------------|
| find | Query documents |
| insert | Add documents |
| update | Modify documents |
| remove | Delete documents |
| createIndex | Create indexes |
| dropIndex | Remove indexes |
| createCollection | Create collections |
| dropCollection | Delete collections |
| dropDatabase | Delete database |
| collStats | View collection statistics |
| dbStats | View database statistics |

### Administrative Actions

| Action | Description |
|--------|-------------|
| createUser | Create users |
| dropUser | Delete users |
| createRole | Create roles |
| dropRole | Delete roles |
| grantRole | Assign roles |
| revokeRole | Remove roles |
| changePassword | Modify passwords |
| viewUser | View user info |
| viewRole | View role info |

### Cluster Actions

| Action | Description |
|--------|-------------|
| replSetConfigure | Configure replica set |
| replSetGetStatus | Get RS status |
| addShard | Add shards |
| removeShard | Remove shards |
| enableSharding | Enable sharding |
| moveChunk | Move chunks |
| killOp | Kill operations |
| shutdown | Shutdown server |

### Resource Specification

```javascript
// Specific database and collection
{ resource: { db: "mydb", collection: "mycollection" }, actions: [...] }

// All collections in database
{ resource: { db: "mydb", collection: "" }, actions: [...] }

// Specific collection in all databases
{ resource: { db: "", collection: "logs" }, actions: [...] }

// All databases and collections (except system)
{ resource: { db: "", collection: "" }, actions: [...] }

// Cluster-wide resource
{ resource: { cluster: true }, actions: [...] }

// Any resource (careful!)
{ resource: { anyResource: true }, actions: [...] }
```

---

## Role Management

### View Roles

```javascript
// List all roles in database
use admin
db.getRoles()

// Show built-in roles too
db.getRoles({ showBuiltinRoles: true })

// Get specific role details
db.getRole("readWrite", { showPrivileges: true })

// View custom role
db.getRole("orderProcessor", { showPrivileges: true })
```

### Update Roles

```javascript
// Add privileges to role
db.grantPrivilegesToRole("orderProcessor", [
  {
    resource: { db: "shop", collection: "inventory" },
    actions: ["find"]
  }
])

// Remove privileges
db.revokePrivilegesFromRole("orderProcessor", [
  {
    resource: { db: "shop", collection: "inventory" },
    actions: ["find"]
  }
])

// Add inherited roles
db.grantRolesToRole("orderProcessor", [
  { role: "read", db: "reporting" }
])

// Remove inherited roles
db.revokeRolesFromRole("orderProcessor", [
  { role: "read", db: "reporting" }
])

// Update role completely
db.updateRole("orderProcessor", {
  privileges: [
    // New complete list of privileges
  ],
  roles: [
    // New complete list of inherited roles
  ]
})
```

### Delete Roles

```javascript
// Drop a custom role
use admin
db.dropRole("orderProcessor")

// Note: Can't drop built-in roles
```

### Role Management Script

```javascript
// Helper functions for role management

const RoleManager = {
  
  // List all custom roles
  listCustomRoles: function() {
    print("=== Custom Roles ===\n")
    
    const roles = db.getRoles({ showPrivileges: true })
    
    if (roles.length === 0) {
      print("No custom roles defined")
      return
    }
    
    roles.forEach(role => {
      print(`Role: ${role.role}`)
      print(`  Database: ${role.db}`)
      
      if (role.roles?.length > 0) {
        print("  Inherits from:")
        role.roles.forEach(r => {
          print(`    - ${r.role}@${r.db}`)
        })
      }
      
      if (role.privileges?.length > 0) {
        print("  Direct Privileges:")
        role.privileges.forEach(p => {
          const resource = p.resource.collection 
            ? `${p.resource.db}.${p.resource.collection}`
            : `${p.resource.db}.*`
          print(`    - ${resource}: ${p.actions.slice(0, 3).join(", ")}...`)
        })
      }
      print()
    })
  },
  
  // Audit role usage
  auditRoleUsage: function(roleName, db) {
    print(`=== Users with Role: ${roleName}@${db} ===\n`)
    
    const users = db.getSiblingDB("admin").getUsers().users
    const usersWithRole = users.filter(user => 
      user.roles.some(r => r.role === roleName && r.db === db)
    )
    
    if (usersWithRole.length === 0) {
      print("No users have this role")
    } else {
      usersWithRole.forEach(u => {
        print(`  ${u.user}@${u.db}`)
      })
    }
    
    return usersWithRole
  },
  
  // Compare two roles
  compareRoles: function(role1, role2) {
    print(`=== Comparing ${role1} vs ${role2} ===\n`)
    
    const r1 = db.getRole(role1, { showPrivileges: true })
    const r2 = db.getRole(role2, { showPrivileges: true })
    
    if (!r1 || !r2) {
      print("One or both roles not found")
      return
    }
    
    const r1Actions = new Set()
    const r2Actions = new Set()
    
    r1.privileges?.forEach(p => {
      p.actions.forEach(a => r1Actions.add(a))
    })
    
    r2.privileges?.forEach(p => {
      p.actions.forEach(a => r2Actions.add(a))
    })
    
    // Actions only in role1
    const onlyInR1 = [...r1Actions].filter(a => !r2Actions.has(a))
    // Actions only in role2
    const onlyInR2 = [...r2Actions].filter(a => !r1Actions.has(a))
    // Actions in both
    const inBoth = [...r1Actions].filter(a => r2Actions.has(a))
    
    print(`Actions only in ${role1}: ${onlyInR1.join(", ") || "none"}`)
    print(`Actions only in ${role2}: ${onlyInR2.join(", ") || "none"}`)
    print(`Actions in both: ${inBoth.join(", ")}`)
  }
}

// Usage:
// RoleManager.listCustomRoles()
// RoleManager.auditRoleUsage("readWrite", "mydb")
// RoleManager.compareRoles("read", "readWrite")
```

---

## Summary

### Built-in Role Summary

| Role | Level | Purpose |
|------|-------|---------|
| read | Database | Read access |
| readWrite | Database | Read and write |
| dbAdmin | Database | Schema management |
| userAdmin | Database | User management |
| dbOwner | Database | Full control |
| clusterMonitor | Cluster | Read-only monitoring |
| clusterManager | Cluster | Management |
| clusterAdmin | Cluster | Full cluster control |
| backup | Cluster | Backup operations |
| restore | Cluster | Restore operations |
| root | Cluster | Superuser |

### Custom Role Commands

| Command | Purpose |
|---------|---------|
| createRole | Create custom role |
| updateRole | Modify role |
| dropRole | Delete role |
| grantPrivilegesToRole | Add privileges |
| revokePrivilegesFromRole | Remove privileges |
| grantRolesToRole | Add inheritance |
| revokeRolesFromRole | Remove inheritance |
| getRole | View role details |
| getRoles | List roles |

### Best Practices

| Practice | Description |
|----------|-------------|
| Least privilege | Grant minimum required |
| Use custom roles | Don't rely only on built-in |
| Separate concerns | Different roles for different jobs |
| Regular audit | Review role assignments |
| Document roles | Maintain role documentation |

### What's Next?

In the next chapter, we'll explore Encryption in MongoDB.

---

## Practice Questions

1. What is the difference between authentication and authorization?
2. What does the readWrite role allow?
3. Why is userAdmin potentially dangerous?
4. How do you create a custom role?
5. What is role inheritance?
6. How do you grant collection-specific access?
7. What is the root role?
8. How do you audit role assignments?

---

## Hands-On Exercises

### Exercise 1: Role-Based Access Control Setup

```javascript
// Set up RBAC for a multi-team environment

function setupRBAC() {
  print("=== Setting Up RBAC ===\n")
  
  const adminDb = db.getSiblingDB("admin")
  
  // 1. Create custom roles
  print("Creating custom roles...")
  
  // Developer role
  try {
    adminDb.createRole({
      role: "developer",
      privileges: [
        {
          resource: { db: "development", collection: "" },
          actions: ["find", "insert", "update", "remove", "createIndex"]
        },
        {
          resource: { db: "staging", collection: "" },
          actions: ["find"]
        }
      ],
      roles: []
    })
    print("  ✓ Created 'developer' role")
  } catch (e) {
    print(`  ! 'developer' role: ${e.code === 51002 ? "already exists" : e.message}`)
  }
  
  // QA role
  try {
    adminDb.createRole({
      role: "qaEngineer",
      privileges: [
        {
          resource: { db: "staging", collection: "" },
          actions: ["find", "insert", "update", "remove"]
        },
        {
          resource: { db: "production", collection: "" },
          actions: ["find"]
        }
      ],
      roles: []
    })
    print("  ✓ Created 'qaEngineer' role")
  } catch (e) {
    print(`  ! 'qaEngineer' role: ${e.code === 51002 ? "already exists" : e.message}`)
  }
  
  // Support role
  try {
    adminDb.createRole({
      role: "support",
      privileges: [
        {
          resource: { db: "production", collection: "users" },
          actions: ["find"]
        },
        {
          resource: { db: "production", collection: "orders" },
          actions: ["find", "update"]  // Can update order status
        },
        {
          resource: { db: "production", collection: "tickets" },
          actions: ["find", "insert", "update"]
        }
      ],
      roles: []
    })
    print("  ✓ Created 'support' role")
  } catch (e) {
    print(`  ! 'support' role: ${e.code === 51002 ? "already exists" : e.message}`)
  }
  
  // Analytics role
  try {
    adminDb.createRole({
      role: "analyst",
      privileges: [
        {
          resource: { db: "analytics", collection: "" },
          actions: ["find", "insert", "createIndex", "collStats", "dbStats"]
        },
        {
          resource: { db: "production", collection: "" },
          actions: ["find"]  // Read-only on production
        }
      ],
      roles: []
    })
    print("  ✓ Created 'analyst' role")
  } catch (e) {
    print(`  ! 'analyst' role: ${e.code === 51002 ? "already exists" : e.message}`)
  }
  
  print("\n✓ RBAC setup complete!")
  
  // Display role summary
  print("\nRole Summary:")
  print("─".repeat(50))
  print("  developer  → Full dev, read staging")
  print("  qaEngineer → Full staging, read production")
  print("  support    → Limited production access")
  print("  analyst    → Full analytics, read production")
}

// Run setup
// setupRBAC()
```

### Exercise 2: Permission Checker

```javascript
// Check what a user can and cannot do

function checkPermissions(username) {
  print(`=== Permissions for: ${username} ===\n`)
  
  const adminDb = db.getSiblingDB("admin")
  const user = adminDb.getUser(username, { showPrivileges: true })
  
  if (!user) {
    print("User not found")
    return
  }
  
  // Organize permissions by database
  const permissionsByDb = {}
  
  user.inheritedPrivileges?.forEach(priv => {
    const db = priv.resource.db || "all"
    const coll = priv.resource.collection || "*"
    const key = `${db}.${coll}`
    
    if (!permissionsByDb[key]) {
      permissionsByDb[key] = new Set()
    }
    
    priv.actions.forEach(a => permissionsByDb[key].add(a))
  })
  
  // Display
  Object.entries(permissionsByDb).sort().forEach(([resource, actions]) => {
    print(`${resource}:`)
    
    // Check common operations
    const common = ["find", "insert", "update", "remove"]
    const crud = common.map(op => actions.has(op) ? "✓" : "✗")
    print(`  CRUD: ${common.map((op, i) => `${crud[i]}${op}`).join(", ")}`)
    
    // Other actions
    const other = [...actions].filter(a => !common.includes(a))
    if (other.length > 0) {
      print(`  Other: ${other.slice(0, 5).join(", ")}${other.length > 5 ? "..." : ""}`)
    }
    print()
  })
  
  // Roles
  print("Assigned Roles:")
  user.roles.forEach(r => {
    print(`  - ${r.role}@${r.db}`)
  })
}

// Usage
// checkPermissions("appUser")
```

### Exercise 3: Least Privilege Role Generator

```javascript
// Generate minimal role for specific operations

function generateMinimalRole(operations) {
  print("=== Minimal Role Generator ===\n")
  
  // Map common operations to required actions
  const operationMap = {
    "read_documents": ["find"],
    "insert_documents": ["insert"],
    "update_documents": ["update"],
    "delete_documents": ["remove"],
    "manage_indexes": ["createIndex", "dropIndex", "listIndexes"],
    "view_stats": ["collStats", "dbStats"],
    "aggregate": ["find"],  // aggregate requires find
    "change_streams": ["changeStream", "find"]
  }
  
  // Collect required actions
  const requiredActions = new Set()
  const invalidOps = []
  
  operations.forEach(op => {
    const actions = operationMap[op.operation]
    if (actions) {
      actions.forEach(a => requiredActions.add(a))
    } else {
      invalidOps.push(op.operation)
    }
  })
  
  if (invalidOps.length > 0) {
    print(`Invalid operations: ${invalidOps.join(", ")}`)
    print("\nValid operations:")
    Object.keys(operationMap).forEach(k => print(`  - ${k}`))
    return
  }
  
  // Group by resource
  const resourceMap = {}
  operations.forEach(op => {
    const key = `${op.database}.${op.collection || ""}`
    if (!resourceMap[key]) {
      resourceMap[key] = { 
        db: op.database, 
        collection: op.collection || "",
        actions: new Set()
      }
    }
    operationMap[op.operation].forEach(a => resourceMap[key].actions.add(a))
  })
  
  // Generate role definition
  const privileges = Object.values(resourceMap).map(r => ({
    resource: { db: r.db, collection: r.collection },
    actions: [...r.actions]
  }))
  
  const roleDefinition = {
    role: "generatedRole",
    privileges: privileges,
    roles: []
  }
  
  print("Generated Role Definition:")
  print(JSON.stringify(roleDefinition, null, 2))
  
  print("\nTo create this role:")
  print(`db.createRole(${JSON.stringify(roleDefinition, null, 2)})`)
  
  return roleDefinition
}

// Example usage
print("Example: Generate role for order processing\n")

generateMinimalRole([
  { operation: "read_documents", database: "shop", collection: "orders" },
  { operation: "update_documents", database: "shop", collection: "orders" },
  { operation: "read_documents", database: "shop", collection: "products" },
  { operation: "view_stats", database: "shop", collection: "orders" }
])
```

### Exercise 4: Role Comparison Tool

```javascript
// Compare roles and find differences

function compareRolesDetailed(roleName1, roleName2) {
  print(`=== Detailed Role Comparison ===\n`)
  print(`Comparing: ${roleName1} vs ${roleName2}\n`)
  
  const adminDb = db.getSiblingDB("admin")
  
  const role1 = adminDb.getRole(roleName1, { showPrivileges: true })
  const role2 = adminDb.getRole(roleName2, { showPrivileges: true })
  
  if (!role1 || !role2) {
    print("One or both roles not found")
    return
  }
  
  // Build action maps
  function buildActionMap(role) {
    const map = {}
    role.privileges?.forEach(priv => {
      const key = `${priv.resource.db || "*"}.${priv.resource.collection || "*"}`
      if (!map[key]) map[key] = new Set()
      priv.actions.forEach(a => map[key].add(a))
    })
    role.inheritedPrivileges?.forEach(priv => {
      const key = `${priv.resource.db || "*"}.${priv.resource.collection || "*"}`
      if (!map[key]) map[key] = new Set()
      priv.actions.forEach(a => map[key].add(a))
    })
    return map
  }
  
  const map1 = buildActionMap(role1)
  const map2 = buildActionMap(role2)
  
  // Get all resources
  const allResources = new Set([...Object.keys(map1), ...Object.keys(map2)])
  
  print("Resource Comparison:")
  print("─".repeat(60))
  
  allResources.forEach(resource => {
    const actions1 = map1[resource] || new Set()
    const actions2 = map2[resource] || new Set()
    
    const only1 = [...actions1].filter(a => !actions2.has(a))
    const only2 = [...actions2].filter(a => !actions1.has(a))
    const both = [...actions1].filter(a => actions2.has(a))
    
    if (only1.length > 0 || only2.length > 0) {
      print(`\n${resource}:`)
      
      if (both.length > 0) {
        print(`  Both: ${both.join(", ")}`)
      }
      if (only1.length > 0) {
        print(`  Only ${roleName1}: ${only1.join(", ")}`)
      }
      if (only2.length > 0) {
        print(`  Only ${roleName2}: ${only2.join(", ")}`)
      }
    }
  })
  
  // Summary
  print("\n" + "─".repeat(60))
  
  const total1 = Object.values(map1).reduce((sum, s) => sum + s.size, 0)
  const total2 = Object.values(map2).reduce((sum, s) => sum + s.size, 0)
  
  print(`\n${roleName1}: ${Object.keys(map1).length} resources, ${total1} total actions`)
  print(`${roleName2}: ${Object.keys(map2).length} resources, ${total2} total actions`)
  
  if (total1 > total2) {
    print(`\n${roleName1} has MORE permissions`)
  } else if (total2 > total1) {
    print(`\n${roleName2} has MORE permissions`)
  } else {
    print("\nRoles have similar scope")
  }
}

// Compare built-in roles
// compareRolesDetailed("read", "readWrite")
```

### Exercise 5: RBAC Audit Report

```javascript
// Generate comprehensive RBAC audit report

function rbacAuditReport() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║               RBAC AUDIT REPORT                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Generated: ${new Date().toISOString()}\n`)
  
  const adminDb = db.getSiblingDB("admin")
  
  // 1. User Summary
  print("┌─ USER SUMMARY ─────────────────────────────────────────────┐")
  
  const users = adminDb.getUsers().users
  print(`│  Total Users: ${users.length}`.padEnd(60) + "│")
  
  // Count by role
  const roleCounts = {}
  let adminUsers = 0
  
  users.forEach(user => {
    user.roles.forEach(role => {
      const key = `${role.role}@${role.db}`
      roleCounts[key] = (roleCounts[key] || 0) + 1
      
      if (["root", "userAdminAnyDatabase", "dbOwner", "clusterAdmin"].includes(role.role)) {
        adminUsers++
      }
    })
  })
  
  print(`│  Admin Users: ${adminUsers}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 2. Role Usage
  print("┌─ ROLE USAGE ──────────────────────────────────────────────┐")
  
  const sortedRoles = Object.entries(roleCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
  
  sortedRoles.forEach(([role, count]) => {
    const bar = "█".repeat(Math.min(count * 2, 20))
    print(`│  ${role.substring(0, 25).padEnd(25)} ${bar} ${count}`.padEnd(60) + "│")
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 3. Custom Roles
  print("┌─ CUSTOM ROLES ────────────────────────────────────────────┐")
  
  const customRoles = adminDb.getRoles()
  
  if (customRoles.length === 0) {
    print("│  No custom roles defined".padEnd(60) + "│")
  } else {
    customRoles.forEach(role => {
      print(`│  ${role.role}`.padEnd(60) + "│")
    })
  }
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 4. Recommendations
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  
  const recommendations = []
  
  if (adminUsers > 3) {
    recommendations.push("⚠ Too many admin users - review and reduce")
  }
  
  if (customRoles.length === 0 && users.length > 5) {
    recommendations.push("! Consider creating custom roles for specific needs")
  }
  
  // Check for users with only root
  const rootOnlyUsers = users.filter(u => 
    u.roles.length === 1 && u.roles[0].role === "root"
  )
  if (rootOnlyUsers.length > 1) {
    recommendations.push("⚠ Multiple users with only root role")
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
rbacAuditReport()
```

---

[← Previous: Authentication](50-authentication.md) | [Next: Encryption →](52-encryption.md)
