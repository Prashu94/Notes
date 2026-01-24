# Chapter 52: Encryption

## Table of Contents
- [Encryption Overview](#encryption-overview)
- [TLS/SSL Encryption](#tlsssl-encryption)
- [Encryption at Rest](#encryption-at-rest)
- [Client-Side Field Level Encryption](#client-side-field-level-encryption)
- [Queryable Encryption](#queryable-encryption)
- [Key Management](#key-management)
- [Summary](#summary)

---

## Encryption Overview

MongoDB supports multiple layers of encryption for comprehensive data protection.

### Encryption Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Encryption Layers                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Layer 1: Network Encryption (TLS/SSL)                       │   │
│  │                                                             │   │
│  │  Client ←──── Encrypted ────► MongoDB                       │   │
│  │              Connection                                     │   │
│  │                                                             │   │
│  │  Protects: Data in transit                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Layer 2: Encryption at Rest                                 │   │
│  │                                                             │   │
│  │  Storage ←──── Encrypted ────► Files on Disk               │   │
│  │                                                             │   │
│  │  Protects: Data files, journals, indexes                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Layer 3: Field-Level Encryption                             │   │
│  │                                                             │   │
│  │  { name: "John", ssn: BinData(...) }                        │   │
│  │                       ↑                                     │   │
│  │                  Encrypted                                  │   │
│  │                                                             │   │
│  │  Protects: Specific sensitive fields                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### When to Use Each

| Layer | Purpose | Required For |
|-------|---------|--------------|
| TLS/SSL | Secure communication | All production |
| Encryption at Rest | Secure storage | Compliance, sensitive data |
| Field-Level | Protect specific fields | PII, PCI, PHI data |

---

## TLS/SSL Encryption

### Generate Certificates

```bash
# Create Certificate Authority
openssl req -new -x509 -days 3650 -keyout ca-key.pem -out ca-cert.pem \
  -subj "/CN=MongoDB-CA" -nodes

# Generate server certificate request
openssl req -new -keyout server-key.pem -out server-req.pem \
  -subj "/CN=mongodb.example.com" -nodes

# Sign server certificate
openssl x509 -req -days 365 -in server-req.pem -CA ca-cert.pem \
  -CAkey ca-key.pem -CAcreateserial -out server-cert.pem

# Combine server key and certificate
cat server-key.pem server-cert.pem > server.pem

# Generate client certificate (for mutual TLS)
openssl req -new -keyout client-key.pem -out client-req.pem \
  -subj "/CN=client1" -nodes
openssl x509 -req -days 365 -in client-req.pem -CA ca-cert.pem \
  -CAkey ca-key.pem -CAcreateserial -out client-cert.pem
cat client-key.pem client-cert.pem > client.pem
```

### Configure MongoDB for TLS

```yaml
# mongod.conf
net:
  port: 27017
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/ssl/server.pem
    CAFile: /etc/mongodb/ssl/ca-cert.pem
    # Optional: allow invalid certificates (not for production!)
    # allowInvalidCertificates: false
    # Optional: allow connections without certificates
    # allowConnectionsWithoutCertificates: true

# TLS modes:
# - disabled: No TLS
# - allowTLS: Both TLS and non-TLS connections
# - preferTLS: Prefer TLS but allow non-TLS
# - requireTLS: Only TLS connections allowed
```

### Connect with TLS

```bash
# mongosh with TLS
mongosh --host mongodb.example.com --port 27017 \
  --tls \
  --tlsCAFile /path/to/ca-cert.pem

# With client certificate (mutual TLS)
mongosh --host mongodb.example.com --port 27017 \
  --tls \
  --tlsCAFile /path/to/ca-cert.pem \
  --tlsCertificateKeyFile /path/to/client.pem
```

### Connection String with TLS

```javascript
// Node.js
const uri = "mongodb://mongodb.example.com:27017/mydb?" +
  "tls=true&" +
  "tlsCAFile=/path/to/ca-cert.pem&" +
  "tlsCertificateKeyFile=/path/to/client.pem"

// Python
import ssl
from pymongo import MongoClient

client = MongoClient(
  "mongodb://mongodb.example.com:27017",
  tls=True,
  tlsCAFile="/path/to/ca-cert.pem",
  tlsCertificateKeyFile="/path/to/client.pem"
)
```

### Verify TLS Connection

```javascript
// Check if connection uses TLS
db.runCommand({ connectionStatus: 1, showPrivileges: true })

// Check server TLS configuration
db.adminCommand({ getParameter: 1, "net.tls.mode": 1 })

// View certificate info
db.adminCommand({ getCmdLineOpts: 1 })
```

---

## Encryption at Rest

### Configure Encryption at Rest (Enterprise)

```yaml
# mongod.conf (Enterprise only)
security:
  enableEncryption: true
  encryptionCipherMode: AES256-CBC
  encryptionKeyFile: /etc/mongodb/encryption/mongodb-keyfile

# Or with KMIP (Key Management Interoperability Protocol)
security:
  enableEncryption: true
  kmip:
    serverName: kmip.example.com
    port: 5696
    clientCertificateFile: /etc/mongodb/kmip/client.pem
    serverCAFile: /etc/mongodb/kmip/ca.pem
```

### Generate Encryption Key

```bash
# Generate local encryption key
openssl rand -base64 32 > /etc/mongodb/encryption/mongodb-keyfile
chmod 600 /etc/mongodb/encryption/mongodb-keyfile
chown mongodb:mongodb /etc/mongodb/encryption/mongodb-keyfile
```

### Rotate Encryption Keys

```javascript
// Key rotation (Enterprise)
// 1. Stop the secondary
// 2. Delete data files
// 3. Generate new key
// 4. Perform initial sync from primary
// 5. Repeat for each secondary
// 6. Step down primary and repeat

// For KMIP, keys are rotated through the KMIP server
```

### Verify Encryption Status

```javascript
// Check encryption status
db.adminCommand({ getParameter: 1, "encryptionAtRest": 1 })

// View server status
db.serverStatus().security
```

---

## Client-Side Field Level Encryption

### CSFLE Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│            Client-Side Field Level Encryption (CSFLE)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Application                     MongoDB Server                     │
│  ┌─────────────────────┐        ┌───────────────────────┐          │
│  │                     │        │                       │          │
│  │  Plain Document:    │        │  Encrypted Document:  │          │
│  │  {                  │        │  {                    │          │
│  │    name: "John",    │  ────► │    name: "John",      │          │
│  │    ssn: "123-45..."│        │    ssn: BinData(...)  │          │
│  │  }                  │        │  }                    │          │
│  │                     │        │                       │          │
│  │  Encryption happens │        │  Server never sees    │          │
│  │  HERE (client-side) │        │  plaintext SSN!       │          │
│  │                     │        │                       │          │
│  └─────────────────────┘        └───────────────────────┘          │
│                                                                     │
│  Key Management:                                                   │
│  ┌─────────────┐                                                   │
│  │ Data Keys   │ ←── Encrypted with ─── Master Key (KMS)          │
│  └─────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### CSFLE Setup (Node.js)

```javascript
// Install required packages
// npm install mongodb mongodb-client-encryption

const { MongoClient, Binary } = require('mongodb');
const { ClientEncryption } = require('mongodb-client-encryption');

// Configuration
const localMasterKey = require('crypto').randomBytes(96);

const kmsProviders = {
  local: {
    key: localMasterKey
  }
};

// Or use AWS KMS
/*
const kmsProviders = {
  aws: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  }
};
*/

// Key vault namespace (where data encryption keys are stored)
const keyVaultNamespace = 'encryption.__keyVault';

async function setupEncryption() {
  const client = new MongoClient('mongodb://localhost:27017');
  await client.connect();
  
  // Create ClientEncryption object
  const encryption = new ClientEncryption(client, {
    keyVaultNamespace,
    kmsProviders
  });
  
  // Create a data encryption key
  const dataKeyId = await encryption.createDataKey('local', {
    keyAltNames: ['myDataKey']
  });
  
  console.log('Data Key ID:', dataKeyId.toString('hex'));
  
  await client.close();
  return dataKeyId;
}
```

### Automatic Encryption Schema

```javascript
// Define encryption schema
const encryptionSchema = {
  'mydb.users': {
    bsonType: 'object',
    encryptMetadata: {
      keyId: [dataKeyId]  // Or keyAltName
    },
    properties: {
      ssn: {
        encrypt: {
          bsonType: 'string',
          algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic'
        }
      },
      medicalRecords: {
        encrypt: {
          bsonType: 'array',
          algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Random'
        }
      }
    }
  }
};

// Connect with auto encryption
const autoEncryptionOptions = {
  keyVaultNamespace,
  kmsProviders,
  schemaMap: encryptionSchema
};

const secureClient = new MongoClient('mongodb://localhost:27017', {
  autoEncryption: autoEncryptionOptions
});
```

### Encryption Algorithms

| Algorithm | Use Case | Query Support |
|-----------|----------|---------------|
| Deterministic | Equality queries needed | Exact match only |
| Random | Maximum security | No queries |

```javascript
// Deterministic: Same input = same output
// Can be used for equality queries
// More vulnerable to frequency analysis

// Random: Same input = different output each time
// Cannot be queried
// Maximum security for sensitive data
```

### Manual Encryption

```javascript
// For explicit control over encryption

async function manualEncrypt(client, dataKeyId) {
  const encryption = new ClientEncryption(client, {
    keyVaultNamespace,
    kmsProviders
  });
  
  // Encrypt a value
  const encryptedSSN = await encryption.encrypt(
    '123-45-6789',
    {
      keyId: dataKeyId,
      algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic'
    }
  );
  
  // Insert with encrypted field
  await client.db('mydb').collection('users').insertOne({
    name: 'John Doe',
    ssn: encryptedSSN
  });
  
  // Decrypt a value
  const doc = await client.db('mydb').collection('users').findOne();
  const decryptedSSN = await encryption.decrypt(doc.ssn);
  
  console.log('Decrypted SSN:', decryptedSSN);
}
```

---

## Queryable Encryption

### Queryable Encryption (MongoDB 6.0+)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Queryable Encryption                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Evolution of CSFLE with enhanced query capabilities:               │
│                                                                     │
│  Features:                                                          │
│  ✓ Equality queries on encrypted fields                            │
│  ✓ Range queries on encrypted fields (7.0+)                        │
│  ✓ Server-side processing without decryption                       │
│  ✓ Automatic encryption/decryption                                 │
│                                                                     │
│  How it works:                                                      │
│  1. Client encrypts data AND creates secure index tokens           │
│  2. Server stores encrypted data + tokens                          │
│  3. Queries use tokens for matching                                │
│  4. Server returns encrypted results                               │
│  5. Client decrypts                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Setup Queryable Encryption

```javascript
// Node.js with MongoDB 7.0+
const { MongoClient } = require('mongodb');

// Encryption configuration
const encryptedFieldsMap = {
  'mydb.patients': {
    fields: [
      {
        path: 'patientId',
        bsonType: 'string',
        queries: [{ queryType: 'equality' }]
      },
      {
        path: 'ssn',
        bsonType: 'string',
        queries: [{ queryType: 'equality' }]
      },
      {
        path: 'age',
        bsonType: 'int',
        queries: [{ queryType: 'range' }]  // Range queries!
      }
    ]
  }
};

const autoEncryptionOptions = {
  keyVaultNamespace: 'encryption.__keyVault',
  kmsProviders: {
    local: { key: masterKey }
  },
  encryptedFieldsMap
};

const client = new MongoClient(uri, {
  autoEncryption: autoEncryptionOptions
});
```

### Query Encrypted Data

```javascript
// With queryable encryption, you can query normally

// Equality query on encrypted field
const patient = await db.collection('patients').findOne({
  ssn: '123-45-6789'  // Client encrypts for query
});

// Range query (MongoDB 7.0+)
const patients = await db.collection('patients').find({
  age: { $gte: 18, $lt: 65 }
}).toArray();

// All encryption/decryption happens transparently
```

---

## Key Management

### Key Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Encryption Key Hierarchy                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                    ┌───────────────────┐                           │
│                    │ Customer Master   │                           │
│                    │ Key (CMK)         │                           │
│                    │                   │                           │
│                    │ Stored in KMS:    │                           │
│                    │ - AWS KMS         │                           │
│                    │ - Azure Key Vault │                           │
│                    │ - GCP KMS         │                           │
│                    │ - Local file      │                           │
│                    └─────────┬─────────┘                           │
│                              │                                      │
│                              │ Encrypts                             │
│                              ▼                                      │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │ Data Key 1    │  │ Data Key 2    │  │ Data Key 3    │          │
│  │ (DEK)         │  │ (DEK)         │  │ (DEK)         │          │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘          │
│          │                  │                  │                   │
│          │ Encrypts         │ Encrypts         │ Encrypts          │
│          ▼                  ▼                  ▼                   │
│    [ SSN fields ]    [ Medical ]       [ Financial ]              │
│                      [ Records ]       [ Data     ]               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Configure AWS KMS

```javascript
const kmsProviders = {
  aws: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  }
};

// Create data key with AWS KMS
const dataKeyId = await encryption.createDataKey('aws', {
  masterKey: {
    key: 'arn:aws:kms:us-east-1:123456789012:key/abcd1234-12ab-34cd-56ef-1234567890ab',
    region: 'us-east-1'
  },
  keyAltNames: ['myDataKey']
});
```

### Configure Azure Key Vault

```javascript
const kmsProviders = {
  azure: {
    tenantId: process.env.AZURE_TENANT_ID,
    clientId: process.env.AZURE_CLIENT_ID,
    clientSecret: process.env.AZURE_CLIENT_SECRET
  }
};

// Create data key with Azure Key Vault
const dataKeyId = await encryption.createDataKey('azure', {
  masterKey: {
    keyVaultEndpoint: 'https://mykeyvault.vault.azure.net',
    keyName: 'myKey'
  }
});
```

### Configure GCP KMS

```javascript
const kmsProviders = {
  gcp: {
    email: 'service-account@project.iam.gserviceaccount.com',
    privateKey: process.env.GCP_PRIVATE_KEY
  }
};

// Create data key with GCP KMS
const dataKeyId = await encryption.createDataKey('gcp', {
  masterKey: {
    projectId: 'my-project',
    location: 'us-east1',
    keyRing: 'my-keyring',
    keyName: 'my-key'
  }
});
```

### Key Rotation

```javascript
// Rotate data encryption keys

async function rotateDataKey(encryption, keyAltName) {
  // Find existing key
  const keyVault = encryption._keyVaultClient
    .db('encryption')
    .collection('__keyVault');
  
  const existingKey = await keyVault.findOne({
    keyAltNames: keyAltName
  });
  
  if (!existingKey) {
    throw new Error('Key not found');
  }
  
  // Create new key with new alt name
  const newKeyId = await encryption.createDataKey('aws', {
    masterKey: existingKey.masterKey,
    keyAltNames: [`${keyAltName}_new`]
  });
  
  // Re-encrypt documents with new key
  // This requires reading, decrypting, re-encrypting with new key
  
  // Update key alt name
  await keyVault.updateOne(
    { _id: newKeyId },
    { $set: { keyAltNames: [keyAltName] } }
  );
  
  // Remove old key (after verifying all data is re-encrypted)
  await keyVault.deleteOne({ _id: existingKey._id });
  
  return newKeyId;
}
```

---

## Summary

### Encryption Types

| Type | Scope | Protection |
|------|-------|------------|
| TLS/SSL | Network | Data in transit |
| Encryption at Rest | Storage | Data at rest |
| CSFLE | Field | Specific sensitive data |
| Queryable Encryption | Field + Query | Encrypted queries |

### Key Points

| Feature | Community | Enterprise |
|---------|-----------|------------|
| TLS/SSL | ✓ | ✓ |
| Encryption at Rest | ✗ | ✓ |
| CSFLE | ✓ | ✓ |
| Queryable Encryption | ✓ | ✓ |
| KMIP Integration | ✗ | ✓ |

### Best Practices

| Practice | Reason |
|----------|--------|
| Always use TLS | Protect all traffic |
| Use KMS for master keys | Secure key management |
| Rotate keys regularly | Limit exposure |
| Encrypt PII fields | Compliance requirements |
| Test encryption setup | Verify before production |

### What's Next?

In the next chapter, we'll explore Auditing in MongoDB.

---

## Practice Questions

1. What are the three layers of MongoDB encryption?
2. What is TLS and why is it important?
3. What is the difference between encryption at rest and TLS?
4. What is Client-Side Field Level Encryption?
5. What are the two CSFLE algorithms and when to use each?
6. What is Queryable Encryption?
7. What is a Data Encryption Key (DEK)?
8. Why use a KMS instead of local key files?

---

## Hands-On Exercises

### Exercise 1: TLS Configuration Checker

```javascript
// Check TLS configuration and status

function checkTLSConfiguration() {
  print("=== TLS Configuration Checker ===\n")
  
  // Check connection
  const isConnected = db.runCommand({ ping: 1 }).ok === 1
  if (!isConnected) {
    print("✗ Not connected to MongoDB")
    return
  }
  print("✓ Connected to MongoDB")
  
  // Check TLS status
  try {
    const serverInfo = db.adminCommand({ serverStatus: 1 })
    
    if (serverInfo.security) {
      print("\nSecurity Status:")
      print(`  TLS: ${serverInfo.security.SSLServerSubjectName ? "Enabled" : "Unknown"}`)
      
      if (serverInfo.security.SSLServerSubjectName) {
        print(`  Certificate Subject: ${serverInfo.security.SSLServerSubjectName}`)
      }
    }
    
    // Get TLS settings
    const tlsMode = db.adminCommand({ getParameter: 1, tlsMode: 1 })
    if (tlsMode.tlsMode) {
      print(`  TLS Mode: ${tlsMode.tlsMode}`)
    }
  } catch (e) {
    print(`\nNote: Some checks require admin privileges`)
  }
  
  // Connection check
  const connStatus = db.runCommand({ connectionStatus: 1 })
  print("\nConnection Info:")
  if (connStatus.authInfo) {
    print(`  Authenticated: ${connStatus.authInfo.authenticatedUsers.length > 0}`)
  }
  
  // Recommendations
  print("\nRecommendations:")
  print("  1. Always use requireTLS in production")
  print("  2. Use certificates from trusted CA")
  print("  3. Enable certificate validation")
  print("  4. Rotate certificates before expiry")
}

checkTLSConfiguration()
```

### Exercise 2: Encryption Schema Generator

```javascript
// Generate encryption schema for a collection

function generateEncryptionSchema(collectionInfo) {
  print("=== Encryption Schema Generator ===\n")
  
  const { database, collection, fields, keyId } = collectionInfo
  
  if (!database || !collection || !fields || !keyId) {
    print("Required: database, collection, fields[], keyId")
    print("Example field: { name: 'ssn', type: 'string', algorithm: 'deterministic' }")
    return
  }
  
  const algorithmMap = {
    deterministic: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic',
    random: 'AEAD_AES_256_CBC_HMAC_SHA_512-Random'
  }
  
  const properties = {}
  
  fields.forEach(field => {
    properties[field.name] = {
      encrypt: {
        bsonType: field.type || 'string',
        algorithm: algorithmMap[field.algorithm] || algorithmMap.random
      }
    }
  })
  
  const schema = {
    [`${database}.${collection}`]: {
      bsonType: 'object',
      encryptMetadata: {
        keyId: [{ '$binary': { base64: keyId, subType: '04' } }]
      },
      properties
    }
  }
  
  print("Generated Schema:")
  print(JSON.stringify(schema, null, 2))
  
  print("\nUsage:")
  print("const autoEncryptionOptions = {")
  print("  keyVaultNamespace: 'encryption.__keyVault',")
  print("  kmsProviders: { ... },")
  print("  schemaMap: " + JSON.stringify(schema))
  print("}")
  
  return schema
}

// Example
generateEncryptionSchema({
  database: 'healthcare',
  collection: 'patients',
  keyId: 'your-base64-key-id-here',
  fields: [
    { name: 'ssn', type: 'string', algorithm: 'deterministic' },
    { name: 'medicalRecords', type: 'array', algorithm: 'random' },
    { name: 'insuranceNumber', type: 'string', algorithm: 'deterministic' }
  ]
})
```

### Exercise 3: Encryption Compliance Checker

```javascript
// Check encryption compliance for sensitive data

function encryptionComplianceChecker(namespace) {
  print("=== Encryption Compliance Checker ===\n")
  
  const sensitivePatterns = {
    pii: ['ssn', 'social_security', 'passport', 'driver_license', 'tax_id'],
    pci: ['card_number', 'cvv', 'credit_card', 'cc_number', 'expiry'],
    phi: ['medical', 'health', 'diagnosis', 'prescription', 'insurance_id'],
    auth: ['password', 'secret', 'token', 'api_key', 'private_key']
  }
  
  const [dbName, collName] = namespace.split('.')
  
  if (!collName) {
    print("Please provide namespace as 'database.collection'")
    return
  }
  
  // Get collection sample
  const sample = db.getSiblingDB(dbName).getCollection(collName).findOne()
  
  if (!sample) {
    print("Collection is empty")
    return
  }
  
  print(`Analyzing: ${namespace}\n`)
  
  // Check each field
  const issues = []
  const fieldNames = Object.keys(sample)
  
  function checkField(fieldName, value, path = '') {
    const fullPath = path ? `${path}.${fieldName}` : fieldName
    const lowerName = fieldName.toLowerCase()
    
    // Check against sensitive patterns
    Object.entries(sensitivePatterns).forEach(([category, patterns]) => {
      patterns.forEach(pattern => {
        if (lowerName.includes(pattern)) {
          // Check if encrypted (BinData type 6 is encrypted)
          const isEncrypted = value instanceof Binary && value.sub_type === 6
          
          if (!isEncrypted) {
            issues.push({
              field: fullPath,
              category: category.toUpperCase(),
              status: 'NOT ENCRYPTED',
              recommendation: `Consider encrypting ${fullPath} for ${category.toUpperCase()} compliance`
            })
          } else {
            print(`✓ ${fullPath} is encrypted (${category.toUpperCase()})`)
          }
        }
      })
    })
    
    // Recursively check nested objects
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      Object.entries(value).forEach(([k, v]) => {
        checkField(k, v, fullPath)
      })
    }
  }
  
  Object.entries(sample).forEach(([k, v]) => {
    if (k !== '_id') checkField(k, v)
  })
  
  // Report
  if (issues.length > 0) {
    print("\n⚠ Potential Compliance Issues:")
    print("─".repeat(50))
    
    issues.forEach(issue => {
      print(`\nField: ${issue.field}`)
      print(`  Category: ${issue.category}`)
      print(`  Status: ${issue.status}`)
      print(`  Recommendation: ${issue.recommendation}`)
    })
    
    print("\n" + "─".repeat(50))
    print(`Total issues: ${issues.length}`)
  } else {
    print("✓ No obvious compliance issues detected")
    print("Note: This is a basic check. Always consult compliance requirements.")
  }
  
  return issues
}

// Usage
// encryptionComplianceChecker('mydb.users')
```

### Exercise 4: Certificate Expiry Monitor

```javascript
// Monitor certificate expiration (conceptual - requires cert parsing)

function certificateExpiryMonitor() {
  print("=== Certificate Expiry Monitor ===\n")
  
  // In practice, you'd parse the actual certificates
  // This is a conceptual example
  
  const certificates = [
    {
      name: "MongoDB Server",
      path: "/etc/mongodb/ssl/server.pem",
      expiry: new Date("2025-06-15"),
      type: "server"
    },
    {
      name: "Client Certificate",
      path: "/etc/mongodb/ssl/client.pem",
      expiry: new Date("2025-03-20"),
      type: "client"
    },
    {
      name: "CA Certificate",
      path: "/etc/mongodb/ssl/ca.pem",
      expiry: new Date("2030-01-01"),
      type: "ca"
    }
  ]
  
  const now = new Date()
  const warningDays = 30
  const criticalDays = 7
  
  print("Certificate Status:")
  print("─".repeat(60))
  
  certificates.forEach(cert => {
    const daysUntilExpiry = Math.floor(
      (cert.expiry - now) / (1000 * 60 * 60 * 24)
    )
    
    let status = "✓ OK"
    let urgency = ""
    
    if (daysUntilExpiry < 0) {
      status = "✗ EXPIRED"
      urgency = " [CRITICAL]"
    } else if (daysUntilExpiry < criticalDays) {
      status = "⚠ CRITICAL"
      urgency = " [ACTION REQUIRED]"
    } else if (daysUntilExpiry < warningDays) {
      status = "! WARNING"
      urgency = " [Plan renewal]"
    }
    
    print(`\n${cert.name} (${cert.type})`)
    print(`  Path: ${cert.path}`)
    print(`  Expiry: ${cert.expiry.toISOString().split('T')[0]}`)
    print(`  Days remaining: ${daysUntilExpiry}`)
    print(`  Status: ${status}${urgency}`)
  })
  
  print("\n" + "─".repeat(60))
  
  // Summary
  const expiring = certificates.filter(c => {
    const days = (c.expiry - now) / (1000 * 60 * 60 * 24)
    return days < warningDays
  })
  
  if (expiring.length > 0) {
    print(`\n⚠ ${expiring.length} certificate(s) need attention!`)
  } else {
    print("\n✓ All certificates are valid")
  }
  
  print("\nRecommendations:")
  print("  1. Renew certificates 30 days before expiry")
  print("  2. Automate certificate monitoring")
  print("  3. Document renewal procedures")
  print("  4. Test certificate rotation in staging")
}

certificateExpiryMonitor()
```

### Exercise 5: Encryption Key Inventory

```javascript
// Inventory and audit encryption keys

async function encryptionKeyInventory() {
  print("=== Encryption Key Inventory ===\n")
  
  // Simulated key inventory
  // In practice, query the __keyVault collection
  
  const keyVault = db.getSiblingDB('encryption').getCollection('__keyVault')
  
  try {
    const keys = keyVault.find({}).toArray()
    
    if (keys.length === 0) {
      print("No encryption keys found in key vault")
      print("\nTo create keys, use:")
      print("  encryption.createDataKey('aws', { masterKey: { ... }})")
      return
    }
    
    print(`Found ${keys.length} data encryption key(s):\n`)
    print("─".repeat(60))
    
    keys.forEach((key, i) => {
      print(`\nKey ${i + 1}:`)
      print(`  ID: ${key._id.toString('hex')}`)
      print(`  Alt Names: ${(key.keyAltNames || []).join(', ') || 'none'}`)
      print(`  KMS Provider: ${Object.keys(key.masterKey || {})[0] || 'unknown'}`)
      print(`  Created: ${key.creationDate?.toISOString() || 'unknown'}`)
      print(`  Updated: ${key.updateDate?.toISOString() || 'never'}`)
      
      // Check key age
      if (key.creationDate) {
        const ageInDays = Math.floor(
          (new Date() - key.creationDate) / (1000 * 60 * 60 * 24)
        )
        
        if (ageInDays > 365) {
          print(`  ⚠ Age: ${ageInDays} days (consider rotation)`)
        } else {
          print(`  Age: ${ageInDays} days`)
        }
      }
    })
    
    print("\n" + "─".repeat(60))
    
    // Key hygiene recommendations
    print("\nKey Management Recommendations:")
    print("  1. Rotate data keys annually")
    print("  2. Use unique keys per data classification")
    print("  3. Store master keys in KMS (AWS/Azure/GCP)")
    print("  4. Document key purposes in alt names")
    print("  5. Audit key access regularly")
    
  } catch (e) {
    print("Unable to access key vault")
    print("Ensure encryption is configured and you have access to:")
    print("  Database: encryption")
    print("  Collection: __keyVault")
  }
}

// Usage (in environment with CSFLE configured)
// encryptionKeyInventory()

// Simulated output
print("=== Encryption Key Inventory (Simulated) ===\n")
print("Found 3 data encryption key(s):\n")
print("─".repeat(60))
print("\nKey 1:")
print("  ID: abc123...")
print("  Alt Names: pii-data-key")
print("  KMS Provider: aws")
print("  Created: 2024-01-15")
print("  Age: 150 days")
print("\nKey 2:")
print("  ID: def456...")
print("  Alt Names: financial-data-key")
print("  KMS Provider: aws")
print("  Created: 2023-06-01")
print("  ⚠ Age: 380 days (consider rotation)")
```

---

[← Previous: Authorization and RBAC](51-authorization-rbac.md) | [Next: Auditing →](53-auditing.md)
