# Chapter 73: Atlas Security

## Table of Contents
- [Security Overview](#security-overview)
- [Authentication](#authentication)
- [Authorization](#authorization)
- [Network Security](#network-security)
- [Encryption](#encryption)
- [Compliance and Auditing](#compliance-and-auditing)
- [Security Best Practices](#security-best-practices)
- [Summary](#summary)

---

## Security Overview

### Atlas Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Atlas Security Layers                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: Network Security                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • IP Access Lists                                           │   │
│  │  • VPC Peering                                               │   │
│  │  • Private Endpoints (AWS PrivateLink, Azure Private Link)   │   │
│  │  • Network Encryption (TLS 1.2+)                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  Layer 2: Authentication                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • SCRAM (Default)                                           │   │
│  │  • X.509 Certificates                                        │   │
│  │  • LDAP                                                      │   │
│  │  • AWS IAM / Azure AD / GCP Service Accounts                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  Layer 3: Authorization                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Role-Based Access Control (RBAC)                         │   │
│  │  • Built-in Roles                                           │   │
│  │  • Custom Roles                                             │   │
│  │  • Field-Level Access Control                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  Layer 4: Encryption                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Encryption at Rest (AES-256)                             │   │
│  │  • Encryption in Transit (TLS)                              │   │
│  │  • Client-Side Field Level Encryption (CSFLE)               │   │
│  │  • Customer Key Management (BYOK)                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  Layer 5: Auditing & Compliance                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Database Auditing                                        │   │
│  │  • Access Logs                                              │   │
│  │  • Compliance Certifications (SOC 2, HIPAA, PCI DSS, etc.) │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Compliance Certifications

| Certification | Description |
|---------------|-------------|
| SOC 2 Type II | Security, availability, processing integrity |
| ISO 27001 | Information security management |
| HIPAA | Health data protection |
| PCI DSS Level 1 | Payment card data security |
| GDPR | EU data protection |
| CCPA | California consumer privacy |
| FedRAMP | US government cloud security |
| CSA STAR | Cloud security assessment |

---

## Authentication

### SCRAM Authentication (Default)

```javascript
// Create user with SCRAM authentication
const user = {
  databaseName: "admin",
  username: "appUser",
  password: "SecureP@ssw0rd!",  // Will be hashed
  
  roles: [
    { databaseName: "mydb", roleName: "readWrite" }
  ],
  
  // Optional: LDAP/X.509 group membership
  ldapAuthType: "NONE",
  x509Type: "NONE"
}

await atlas.request(
  'POST',
  `/groups/${projectId}/databaseUsers`,
  user
)

// Connection with SCRAM
const uri = "mongodb+srv://appUser:SecureP@ssw0rd!@cluster0.abc123.mongodb.net/mydb"

// Password requirements (recommended):
// - Minimum 8 characters
// - Mix of uppercase, lowercase, numbers, special characters
// - No username in password
// - Rotate regularly
```

### X.509 Certificate Authentication

```javascript
// Create user for X.509 authentication
const x509User = {
  databaseName: "$external",  // Required for X.509
  username: "CN=myapp,OU=apps,O=mycompany,L=NYC,ST=NY,C=US",  // Subject from certificate
  
  roles: [
    { databaseName: "mydb", roleName: "readWrite" }
  ],
  
  x509Type: "MANAGED"  // or "CUSTOMER" for your own CA
}

await atlas.request(
  'POST',
  `/groups/${projectId}/databaseUsers`,
  x509User
)

// Generate managed certificate
const certResponse = await atlas.request(
  'POST',
  `/groups/${projectId}/databaseUsers/${encodeURIComponent(username)}/certs`,
  { monthsUntilExpiration: 12 }
)

// Save certificate files
// certResponse contains: certificate, privateKey

// Connection with X.509
const { MongoClient } = require('mongodb')

const client = new MongoClient(
  "mongodb+srv://cluster0.abc123.mongodb.net/mydb?authMechanism=MONGODB-X509",
  {
    tls: true,
    tlsCertificateKeyFile: '/path/to/client.pem',
    tlsCAFile: '/path/to/ca.pem'
  }
)

await client.connect()
```

### AWS IAM Authentication

```javascript
// Create user for AWS IAM authentication
const iamUser = {
  databaseName: "$external",
  username: "arn:aws:iam::123456789012:user/myapp",  // IAM user ARN
  // or "arn:aws:iam::123456789012:role/myapp-role"  // IAM role ARN
  
  awsIAMType: "USER",  // or "ROLE"
  
  roles: [
    { databaseName: "mydb", roleName: "readWrite" }
  ]
}

await atlas.request(
  'POST',
  `/groups/${projectId}/databaseUsers`,
  iamUser
)

// Connection with AWS IAM
const { MongoClient } = require('mongodb')
const { fromIni } = require('@aws-sdk/credential-providers')

// Get AWS credentials
const credentials = await fromIni({ profile: 'default' })()

const uri = `mongodb+srv://cluster0.abc123.mongodb.net/mydb?` +
  `authMechanism=MONGODB-AWS&` +
  `authMechanismProperties=AWS_SESSION_TOKEN:${credentials.sessionToken}`

const client = new MongoClient(uri, {
  auth: {
    username: credentials.accessKeyId,
    password: credentials.secretAccessKey
  }
})

await client.connect()

// Or use environment variables
// AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
const clientEnv = new MongoClient(
  "mongodb+srv://cluster0.abc123.mongodb.net/mydb?authMechanism=MONGODB-AWS"
)
```

### LDAP Authentication

```javascript
// Configure LDAP (Atlas Advanced tier required)
const ldapConfig = {
  ldap: {
    authenticationEnabled: true,
    
    // LDAP server settings
    hostname: "ldap.mycompany.com",
    port: 636,
    
    // Bind credentials
    bindUsername: "cn=atlas,ou=services,dc=mycompany,dc=com",
    bindPassword: "ldapBindPassword",
    
    // User search
    userToDNMapping: [
      {
        match: "(.*)",
        substitution: "uid={0},ou=users,dc=mycompany,dc=com"
      }
    ],
    
    // TLS settings
    caCertificate: "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
  }
}

await atlas.request(
  'PATCH',
  `/groups/${projectId}/userSecurity`,
  ldapConfig
)

// Create LDAP user
const ldapUser = {
  databaseName: "$external",
  username: "jsmith",  // LDAP username
  ldapAuthType: "USER",  // or "GROUP"
  
  roles: [
    { databaseName: "mydb", roleName: "readWrite" }
  ]
}

// Connection with LDAP
const uri = "mongodb+srv://jsmith:ldapPassword@cluster0.abc123.mongodb.net/mydb" +
  "?authMechanism=PLAIN&authSource=$external"
```

---

## Authorization

### Built-in Database Roles

```javascript
// Built-in roles reference
const builtInRoles = {
  // Database User Roles
  read: "Read all non-system collections in database",
  readWrite: "Read and write all non-system collections",
  
  // Database Admin Roles
  dbAdmin: "Schema management, indexing, statistics",
  userAdmin: "Create and modify users and roles",
  dbOwner: "Combines readWrite, dbAdmin, and userAdmin",
  
  // Cluster Admin Roles
  clusterAdmin: "Cluster administration operations",
  clusterManager: "Management and monitoring",
  clusterMonitor: "Read-only monitoring access",
  hostManager: "Monitor and manage servers",
  
  // Backup/Restore Roles
  backup: "Backup data",
  restore: "Restore data",
  
  // All-Database Roles
  readAnyDatabase: "Read any database except local and config",
  readWriteAnyDatabase: "Read/write any database",
  userAdminAnyDatabase: "User admin for any database",
  dbAdminAnyDatabase: "Database admin for any database",
  
  // Atlas-Specific
  atlasAdmin: "Full Atlas project access"
}

// Create user with specific roles
const userWithRoles = {
  databaseName: "admin",
  username: "reportUser",
  password: "ReportP@ss123!",
  
  roles: [
    // Read access to analytics database
    { databaseName: "analytics", roleName: "read" },
    
    // Read/write to reports collection only (via custom role)
    { databaseName: "admin", roleName: "reportsWriter" }
  ]
}
```

### Custom Roles

```javascript
// Create custom role
const customRole = {
  roleName: "orderProcessor",
  
  // Actions on specific resources
  actions: [
    {
      // Read orders
      action: "find",
      resources: [
        { db: "ecommerce", collection: "orders" }
      ]
    },
    {
      // Update order status only
      action: "update",
      resources: [
        { db: "ecommerce", collection: "orders" }
      ]
    },
    {
      // Insert into order_logs
      action: "insert",
      resources: [
        { db: "ecommerce", collection: "order_logs" }
      ]
    }
  ],
  
  // Inherit from other roles
  inheritedRoles: [
    { db: "ecommerce", role: "read" }  // Base read access
  ]
}

await atlas.request(
  'POST',
  `/groups/${projectId}/customDBRoles/roles`,
  customRole
)

// More granular custom role
const financeRole = {
  roleName: "financeAnalyst",
  
  actions: [
    // Aggregation on specific collections
    {
      action: "find",
      resources: [
        { db: "finance", collection: "transactions" },
        { db: "finance", collection: "reports" }
      ]
    },
    {
      action: "aggregate",
      resources: [
        { db: "finance", collection: "transactions" }
      ]
    },
    // Create indexes (for optimization)
    {
      action: "createIndex",
      resources: [
        { db: "finance", collection: "transactions" }
      ]
    },
    // View collection stats
    {
      action: "collStats",
      resources: [
        { db: "finance", collection: "" }  // All collections
      ]
    }
  ]
}
```

### Collection-Level Access

```javascript
// Role with collection-level restrictions
const collectionRole = {
  roleName: "customerSupport",
  
  actions: [
    // Read customers but not passwords
    {
      action: "find",
      resources: [
        { db: "mydb", collection: "customers" }
      ]
    },
    // Update specific fields only
    {
      action: "update",
      resources: [
        { db: "mydb", collection: "support_tickets" }
      ]
    },
    // Insert support notes
    {
      action: "insert",
      resources: [
        { db: "mydb", collection: "support_notes" }
      ]
    }
  ]
}

// View-based access control (hide sensitive fields)
db.createView(
  "customers_safe",
  "customers",
  [
    {
      $project: {
        name: 1,
        email: 1,
        phone: 1,
        // Exclude: ssn, creditCard, password
        createdAt: 1
      }
    }
  ]
)

// Grant access to view only
const viewRole = {
  roleName: "customerViewer",
  actions: [
    {
      action: "find",
      resources: [
        { db: "mydb", collection: "customers_safe" }
      ]
    }
  ]
}
```

---

## Network Security

### IP Access Lists

```javascript
// Manage IP access list
class IPAccessManager {
  constructor(atlas, projectId) {
    this.atlas = atlas
    this.projectId = projectId
  }
  
  // Add IP addresses
  async addIPs(entries) {
    return await this.atlas.request(
      'POST',
      `/groups/${this.projectId}/accessList`,
      entries
    )
  }
  
  // Add AWS security group
  async addSecurityGroup(sgId, comment) {
    return await this.addIPs([{
      awsSecurityGroup: sgId,
      comment: comment
    }])
  }
  
  // Add temporary access
  async addTemporary(ip, hours = 1, comment = 'Temporary access') {
    const deleteAfter = new Date(Date.now() + hours * 3600000)
    
    return await this.addIPs([{
      ipAddress: ip,
      comment: comment,
      deleteAfterDate: deleteAfter.toISOString()
    }])
  }
  
  // Audit current access list
  async audit() {
    const list = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/accessList`
    )
    
    const audit = {
      totalEntries: list.totalCount,
      byType: {
        individual: [],
        cidr: [],
        securityGroup: [],
        temporary: []
      },
      warnings: []
    }
    
    for (const entry of list.results) {
      if (entry.awsSecurityGroup) {
        audit.byType.securityGroup.push(entry)
      } else if (entry.cidrBlock === '0.0.0.0/0') {
        audit.warnings.push('WARNING: Allow all IPs (0.0.0.0/0) is enabled!')
        audit.byType.cidr.push(entry)
      } else if (entry.cidrBlock) {
        audit.byType.cidr.push(entry)
      } else if (entry.deleteAfterDate) {
        audit.byType.temporary.push(entry)
      } else {
        audit.byType.individual.push(entry)
      }
    }
    
    return audit
  }
}
```

### Private Endpoints

```javascript
// AWS PrivateLink setup
async function setupAWSPrivateLink(atlas, projectId, region) {
  // Step 1: Create Atlas private endpoint service
  const service = await atlas.request(
    'POST',
    `/groups/${projectId}/privateEndpoint/endpointService`,
    {
      providerName: "AWS",
      region: region
    }
  )
  
  console.log('Atlas Service Name:', service.endpointServiceName)
  // Use this to create VPC endpoint in AWS
  
  // Step 2: After creating AWS VPC endpoint, get its ID
  const vpcEndpointId = "vpce-0123456789abcdef0"  // From AWS
  
  // Step 3: Create interface endpoint in Atlas
  const endpoint = await atlas.request(
    'POST',
    `/groups/${projectId}/privateEndpoint/${service.id}/interfaceEndpoints`,
    {
      interfaceEndpointId: vpcEndpointId
    }
  )
  
  // Step 4: Wait for endpoint to be available
  let status = 'INITIATING'
  while (status !== 'AVAILABLE') {
    await new Promise(r => setTimeout(r, 10000))  // Wait 10 seconds
    
    const check = await atlas.request(
      'GET',
      `/groups/${projectId}/privateEndpoint/${service.id}/interfaceEndpoints/${endpoint.interfaceEndpointId}`
    )
    status = check.connectionStatus
    console.log('Endpoint status:', status)
  }
  
  // Connection string will use private endpoint automatically
  return service.endpointServiceName
}

// Azure Private Link setup
async function setupAzurePrivateLink(atlas, projectId, region) {
  const service = await atlas.request(
    'POST',
    `/groups/${projectId}/privateEndpoint/endpointService`,
    {
      providerName: "AZURE",
      region: region
    }
  )
  
  console.log('Private Link Service ID:', service.privateLinkServiceResourceId)
  // Use this to create private endpoint in Azure
  
  return service
}
```

### Network Peering

```javascript
// VPC Peering configuration
async function setupVPCPeering(atlas, projectId, config) {
  const {
    provider,  // AWS, AZURE, or GCP
    vpcId,
    region,
    cidrBlock
  } = config
  
  // Get or create Atlas network container
  let containers = await atlas.request(
    'GET',
    `/groups/${projectId}/containers`
  )
  
  let container = containers.results.find(c => 
    c.providerName === provider && c.regionName === region
  )
  
  if (!container) {
    container = await atlas.request(
      'POST',
      `/groups/${projectId}/containers`,
      {
        providerName: provider,
        regionName: region,
        atlasCidrBlock: "192.168.0.0/21"  // Atlas VPC CIDR
      }
    )
  }
  
  // Create peering connection
  const peering = await atlas.request(
    'POST',
    `/groups/${projectId}/peers`,
    {
      containerId: container.id,
      vpcId: vpcId,
      awsAccountId: config.awsAccountId,  // For AWS
      routeTableCidrBlock: cidrBlock,
      accepterRegionName: region
    }
  )
  
  console.log('Peering Connection ID:', peering.connectionId)
  // Accept peering in your cloud provider console
  
  return peering
}
```

---

## Encryption

### Encryption at Rest

```javascript
// Enable encryption at rest with AWS KMS
const encryptionConfig = {
  encryptionAtRestProvider: "AWS",
  
  awsKms: {
    enabled: true,
    
    // Customer-managed key (BYOK)
    customerMasterKeyID: "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012",
    
    // IAM role for Atlas to access KMS
    roleId: "arn:aws:iam::123456789012:role/AtlasKMSRole",
    
    region: "US_EAST_1"
  }
}

await atlas.request(
  'PATCH',
  `/groups/${projectId}/encryptionAtRest`,
  encryptionConfig
)

// Azure Key Vault configuration
const azureEncryption = {
  encryptionAtRestProvider: "AZURE",
  
  azureKeyVault: {
    enabled: true,
    clientID: "client-id-guid",
    tenantID: "tenant-id-guid",
    secret: "client-secret",
    keyIdentifier: "https://mykeyvault.vault.azure.net/keys/mykey/version",
    subscriptionID: "subscription-id",
    resourceGroupName: "my-resource-group",
    keyVaultName: "mykeyvault"
  }
}

// GCP Cloud KMS configuration
const gcpEncryption = {
  encryptionAtRestProvider: "GCP",
  
  googleCloudKms: {
    enabled: true,
    serviceAccountKey: "base64-encoded-service-account-json",
    keyVersionResourceID: "projects/my-project/locations/global/keyRings/my-ring/cryptoKeys/my-key/cryptoKeyVersions/1"
  }
}
```

### Client-Side Field Level Encryption (CSFLE)

```javascript
const { MongoClient, ClientEncryption } = require('mongodb')

// Key Management Service configuration
const kmsProviders = {
  aws: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  }
}

// Master key (from AWS KMS)
const masterKey = {
  key: "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012",
  region: "us-east-1"
}

// Create encryption client
async function setupEncryption(client) {
  const keyVaultNamespace = "encryption.__keyVault"
  
  const encryption = new ClientEncryption(client, {
    keyVaultNamespace,
    kmsProviders
  })
  
  // Create data encryption key
  const dataKeyId = await encryption.createDataKey("aws", {
    masterKey: masterKey,
    keyAltNames: ["myDataKey"]
  })
  
  return { encryption, dataKeyId }
}

// Schema with automatic encryption
const encryptedFieldsMap = {
  "mydb.patients": {
    fields: [
      {
        path: "ssn",
        keyId: dataKeyId,
        bsonType: "string",
        queries: { queryType: "equality" }  // Allows equality queries
      },
      {
        path: "medicalRecord",
        keyId: dataKeyId,
        bsonType: "object"
        // No queries - fully encrypted
      },
      {
        path: "creditCard.number",
        keyId: dataKeyId,
        bsonType: "string"
      }
    ]
  }
}

// Connect with auto-encryption
const secureClient = new MongoClient(uri, {
  autoEncryption: {
    keyVaultNamespace: "encryption.__keyVault",
    kmsProviders,
    schemaMap: encryptedFieldsMap,
    extraOptions: {
      mongocryptdSpawnPath: '/usr/local/bin/mongocryptd'
    }
  }
})

// Usage - encryption/decryption is automatic
const patients = secureClient.db('mydb').collection('patients')

// Insert - SSN and medicalRecord are automatically encrypted
await patients.insertOne({
  name: "John Doe",
  ssn: "123-45-6789",  // Encrypted before storage
  medicalRecord: {     // Encrypted before storage
    conditions: ["diabetes"],
    medications: ["insulin"]
  },
  dateOfBirth: new Date("1980-01-15")  // Not encrypted
})

// Query - can query on SSN (equality)
const patient = await patients.findOne({ ssn: "123-45-6789" })
// Result: SSN is automatically decrypted for authorized clients
```

### Queryable Encryption

```javascript
// Queryable Encryption (MongoDB 7.0+)
const encryptedFieldsMap = {
  fields: [
    {
      path: "ssn",
      keyId: dataKeyId,
      bsonType: "string",
      queries: [{ queryType: "equality" }]
    },
    {
      path: "salary",
      keyId: dataKeyId,
      bsonType: "int",
      queries: [
        { queryType: "equality" },
        { queryType: "range" }  // Allows range queries!
      ]
    }
  ]
}

// Create encrypted collection
await db.createCollection("employees", {
  encryptedFields: encryptedFieldsMap
})

// Now you can do range queries on encrypted data!
const highEarners = await db.collection('employees').find({
  salary: { $gt: 100000 }
}).toArray()
```

---

## Compliance and Auditing

### Database Auditing

```javascript
// Enable auditing (M10+ clusters)
const auditConfig = {
  auditLog: {
    auditAuthorizationSuccess: true,  // Log successful auth
    auditFilter: JSON.stringify({
      // Filter what to audit
      "$and": [
        { "users": { "$elemMatch": { "$eq": "admin.appUser" } } },
        { "atype": { "$in": ["authCheck", "authenticate"] } }
      ]
    })
  }
}

await atlas.request(
  'PATCH',
  `/groups/${projectId}/clusters/${clusterName}`,
  auditConfig
)

// Audit filter examples
const auditFilters = {
  // Audit all authentication events
  allAuth: {
    atype: { $in: ["authenticate", "authCheck"] }
  },
  
  // Audit specific users
  specificUsers: {
    users: { $elemMatch: { user: "sensitiveDataUser" } }
  },
  
  // Audit specific databases
  specificDatabases: {
    "param.ns": { $regex: "^sensitive\\." }
  },
  
  // Audit DDL operations
  schemaChanges: {
    atype: { 
      $in: [
        "createCollection",
        "dropCollection",
        "createIndex",
        "dropIndex",
        "createDatabase",
        "dropDatabase"
      ]
    }
  },
  
  // Comprehensive audit (high volume)
  everything: {
    atype: { $nin: [] }  // All types
  }
}

// Download audit logs
const auditLogs = await atlas.request(
  'GET',
  `/groups/${projectId}/clusters/${clusterName}/logs/mongodb-audit-log.gz`,
  null,
  { responseType: 'arraybuffer' }
)
```

### Access Tracking

```javascript
// Track and review access
async function reviewAccess(atlas, projectId) {
  // Get all database users
  const users = await atlas.request(
    'GET',
    `/groups/${projectId}/databaseUsers`
  )
  
  // Get access list
  const accessList = await atlas.request(
    'GET',
    `/groups/${projectId}/accessList`
  )
  
  // Audit report
  const report = {
    generatedAt: new Date().toISOString(),
    
    users: users.results.map(u => ({
      username: u.username,
      database: u.databaseName,
      roles: u.roles,
      authType: u.ldapAuthType || u.x509Type || 'SCRAM',
      scopes: u.scopes
    })),
    
    networkAccess: accessList.results.map(a => ({
      entry: a.cidrBlock || a.ipAddress || a.awsSecurityGroup,
      comment: a.comment,
      temporary: !!a.deleteAfterDate,
      expiresAt: a.deleteAfterDate
    })),
    
    warnings: []
  }
  
  // Check for security issues
  for (const entry of accessList.results) {
    if (entry.cidrBlock === '0.0.0.0/0') {
      report.warnings.push('CRITICAL: All IPs allowed (0.0.0.0/0)')
    }
  }
  
  for (const user of users.results) {
    if (user.roles.some(r => r.roleName === 'atlasAdmin')) {
      report.warnings.push(`HIGH: User ${user.username} has atlasAdmin role`)
    }
  }
  
  return report
}
```

### Compliance Reports

```javascript
// Generate compliance report
async function generateComplianceReport(atlas, projectId) {
  const report = {
    timestamp: new Date().toISOString(),
    projectId,
    
    sections: {}
  }
  
  // Encryption status
  const encryption = await atlas.request(
    'GET',
    `/groups/${projectId}/encryptionAtRest`
  )
  
  report.sections.encryption = {
    atRestEnabled: !!encryption.awsKms?.enabled || 
                   !!encryption.azureKeyVault?.enabled ||
                   !!encryption.googleCloudKms?.enabled,
    provider: encryption.encryptionAtRestProvider,
    customerManagedKeys: !!encryption.awsKms?.customerMasterKeyID
  }
  
  // Network security
  const accessList = await atlas.request(
    'GET',
    `/groups/${projectId}/accessList`
  )
  
  report.sections.network = {
    ipRestricted: !accessList.results.some(a => a.cidrBlock === '0.0.0.0/0'),
    privateEndpointsOnly: accessList.totalCount === 0,  // If using private endpoints
    totalAccessEntries: accessList.totalCount
  }
  
  // Authentication
  const users = await atlas.request(
    'GET',
    `/groups/${projectId}/databaseUsers`
  )
  
  report.sections.authentication = {
    totalUsers: users.totalCount,
    mfaEnabled: true,  // Atlas UI MFA
    x509Users: users.results.filter(u => u.x509Type !== 'NONE').length,
    ldapUsers: users.results.filter(u => u.ldapAuthType !== 'NONE').length
  }
  
  // Clusters
  const clusters = await atlas.request(
    'GET',
    `/groups/${projectId}/clusters`
  )
  
  report.sections.clusters = clusters.results.map(c => ({
    name: c.name,
    backupEnabled: c.backupEnabled,
    pitEnabled: c.pitEnabled,
    encryptionAtRest: c.encryptionAtRestProvider !== 'NONE',
    tlsVersion: 'TLS1.2+',  // Atlas enforces this
    mongoDBVersion: c.mongoDBVersion
  }))
  
  return report
}
```

---

## Security Best Practices

### Security Checklist

```markdown
## Atlas Security Checklist

### Authentication
□ Use strong, unique passwords for database users
□ Implement X.509 or AWS IAM authentication for applications
□ Enable MFA for Atlas UI access
□ Rotate credentials regularly
□ Use temporary credentials where possible

### Authorization
□ Follow principle of least privilege
□ Create custom roles for specific use cases
□ Avoid using atlasAdmin role for applications
□ Review and audit user permissions regularly
□ Use collection-level access control

### Network Security
□ Never use 0.0.0.0/0 in production
□ Use VPC peering or private endpoints
□ Whitelist specific IP addresses only
□ Use temporary IP access for debugging
□ Implement network segmentation

### Encryption
□ Enable encryption at rest
□ Use customer-managed keys (BYOK)
□ Implement CSFLE for sensitive data
□ Verify TLS 1.2+ is enforced
□ Secure key management practices

### Monitoring & Auditing
□ Enable database auditing
□ Set up alerts for security events
□ Review audit logs regularly
□ Monitor for unusual access patterns
□ Implement log retention policy

### Compliance
□ Document security controls
□ Perform regular security assessments
□ Maintain compliance certifications
□ Train team on security practices
□ Have incident response plan
```

### Security Automation

```javascript
// Automated security checks
class AtlasSecurityAuditor {
  constructor(atlas, projectId) {
    this.atlas = atlas
    this.projectId = projectId
  }
  
  async runAudit() {
    const findings = []
    
    // Check network access
    const accessList = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/accessList`
    )
    
    for (const entry of accessList.results) {
      if (entry.cidrBlock === '0.0.0.0/0') {
        findings.push({
          severity: 'CRITICAL',
          category: 'NETWORK',
          finding: 'All IPs allowed (0.0.0.0/0)',
          recommendation: 'Remove 0.0.0.0/0 and add specific IP addresses'
        })
      }
      
      // Check for broad CIDR blocks
      if (entry.cidrBlock && this.getCIDRSize(entry.cidrBlock) > 65536) {
        findings.push({
          severity: 'MEDIUM',
          category: 'NETWORK',
          finding: `Broad CIDR block: ${entry.cidrBlock}`,
          recommendation: 'Use more specific CIDR blocks'
        })
      }
    }
    
    // Check users
    const users = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/databaseUsers`
    )
    
    for (const user of users.results) {
      // Check for admin roles
      const hasAdmin = user.roles.some(r => 
        ['atlasAdmin', 'dbAdminAnyDatabase', 'userAdminAnyDatabase']
          .includes(r.roleName)
      )
      
      if (hasAdmin && user.ldapAuthType === 'NONE' && user.x509Type === 'NONE') {
        findings.push({
          severity: 'HIGH',
          category: 'AUTHENTICATION',
          finding: `Admin user ${user.username} uses password auth`,
          recommendation: 'Use X.509 or federated auth for admin users'
        })
      }
      
      // Check for wide database access
      const hasAnyDb = user.roles.some(r => 
        r.roleName.includes('AnyDatabase')
      )
      
      if (hasAnyDb) {
        findings.push({
          severity: 'MEDIUM',
          category: 'AUTHORIZATION',
          finding: `User ${user.username} has AnyDatabase role`,
          recommendation: 'Restrict to specific databases'
        })
      }
    }
    
    // Check encryption
    const encryption = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/encryptionAtRest`
    )
    
    if (!encryption.awsKms?.customerMasterKeyID && 
        !encryption.azureKeyVault?.keyIdentifier &&
        !encryption.googleCloudKms?.keyVersionResourceID) {
      findings.push({
        severity: 'MEDIUM',
        category: 'ENCRYPTION',
        finding: 'Not using customer-managed encryption keys',
        recommendation: 'Configure BYOK for encryption at rest'
      })
    }
    
    return {
      auditedAt: new Date().toISOString(),
      projectId: this.projectId,
      findingsCount: findings.length,
      findings: findings.sort((a, b) => 
        this.severityOrder(a.severity) - this.severityOrder(b.severity)
      )
    }
  }
  
  getCIDRSize(cidr) {
    const bits = parseInt(cidr.split('/')[1])
    return Math.pow(2, 32 - bits)
  }
  
  severityOrder(severity) {
    const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }
    return order[severity] ?? 4
  }
}
```

---

## Summary

### Security Features by Tier

| Feature | M0 | M2/M5 | M10+ |
|---------|-----|-------|------|
| IP Access List | ✓ | ✓ | ✓ |
| TLS Encryption | ✓ | ✓ | ✓ |
| SCRAM Auth | ✓ | ✓ | ✓ |
| X.509 Auth | - | - | ✓ |
| LDAP Auth | - | - | ✓ |
| AWS IAM Auth | - | - | ✓ |
| VPC Peering | - | - | ✓ |
| Private Endpoints | - | - | ✓ |
| Customer Keys (BYOK) | - | - | ✓ |
| Database Auditing | - | - | ✓ |
| CSFLE | ✓ | ✓ | ✓ |

### Key Security Principles

| Principle | Implementation |
|-----------|----------------|
| Defense in Depth | Multiple security layers |
| Least Privilege | Minimal necessary permissions |
| Zero Trust | Verify every access request |
| Encryption Everywhere | At rest and in transit |
| Audit Everything | Comprehensive logging |

---

## Practice Questions

1. What authentication methods does Atlas support?
2. How do you configure customer-managed encryption keys?
3. What is the difference between VPC peering and private endpoints?
4. How do you create custom database roles?
5. What is Client-Side Field Level Encryption (CSFLE)?
6. How do you enable and configure database auditing?
7. What are the security implications of using 0.0.0.0/0 in the IP access list?
8. How do you implement AWS IAM authentication with Atlas?

---

[← Previous: Atlas Configuration](72-atlas-configuration.md) | [Next: Atlas Monitoring →](74-atlas-monitoring.md)
