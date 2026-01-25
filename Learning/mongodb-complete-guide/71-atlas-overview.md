# Chapter 71: Atlas Overview

## Table of Contents
- [What is MongoDB Atlas?](#what-is-mongodb-atlas)
- [Atlas Architecture](#atlas-architecture)
- [Cluster Types and Tiers](#cluster-types-and-tiers)
- [Getting Started with Atlas](#getting-started-with-atlas)
- [Atlas Features](#atlas-features)
- [Atlas CLI and API](#atlas-cli-and-api)
- [Summary](#summary)

---

## What is MongoDB Atlas?

### MongoDB Atlas Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Atlas Platform                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Atlas Control Plane                       │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │   │
│   │  │   UI     │ │   API    │ │   CLI    │ │ Terraform│       │   │
│   │  │ Console  │ │          │ │          │ │ Provider │       │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Data Services                             │   │
│   │                                                              │   │
│   │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │   │
│   │  │   Database     │  │   Data Lake    │  │   Vector     │  │   │
│   │  │   Clusters     │  │                │  │   Search     │  │   │
│   │  │                │  │                │  │              │  │   │
│   │  │ • Dedicated    │  │ • Federated    │  │ • AI/ML      │  │   │
│   │  │ • Serverless   │  │   Queries      │  │ • Embeddings │  │   │
│   │  │ • Shared       │  │ • S3/Azure     │  │              │  │   │
│   │  └────────────────┘  └────────────────┘  └──────────────┘  │   │
│   │                                                              │   │
│   │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │   │
│   │  │  Atlas Search  │  │   App Services │  │   Charts     │  │   │
│   │  │                │  │                │  │              │  │   │
│   │  │ • Full-text    │  │ • Functions    │  │ • Dashboards │  │   │
│   │  │ • Facets       │  │ • Triggers     │  │ • Reports    │  │   │
│   │  │ • Autocomplete │  │ • GraphQL      │  │ • Embeds     │  │   │
│   │  └────────────────┘  └────────────────┘  └──────────────┘  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              Cloud Provider Infrastructure                   │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│   │  │     AWS      │  │    Azure     │  │     GCP      │      │   │
│   │  │              │  │              │  │              │      │   │
│   │  │  80+ Regions │  │  60+ Regions │  │  35+ Regions │      │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Benefits

| Benefit | Description |
|---------|-------------|
| Fully Managed | Automated provisioning, patching, scaling |
| Multi-Cloud | Deploy on AWS, Azure, or GCP |
| Global Distribution | Deploy across multiple regions |
| Built-in Security | Encryption, network isolation, compliance |
| Automatic Backups | Point-in-time recovery, snapshots |
| Performance | Auto-scaling, performance advisor |
| Developer Experience | Easy setup, comprehensive APIs |

---

## Atlas Architecture

### Global Cluster Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Global Cluster Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Region: US-EAST-1 (Primary)                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │   │
│   │  │  Primary    │  │  Secondary  │  │  Secondary  │         │   │
│   │  │    Node     │  │    Node     │  │    Node     │         │   │
│   │  │             │◄─┤             │◄─┤             │         │   │
│   │  │  Writes +   │  │   Reads     │  │   Reads     │         │   │
│   │  │   Reads     │  │             │  │             │         │   │
│   │  └─────────────┘  └─────────────┘  └─────────────┘         │   │
│   │        AZ-1            AZ-2            AZ-3                 │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                    Replication                                      │
│                              │                                      │
│   Region: EU-WEST-1 (Analytics)                                    │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  ┌─────────────┐  ┌─────────────┐                          │   │
│   │  │  Analytics  │  │  Analytics  │                          │   │
│   │  │    Node     │  │    Node     │                          │   │
│   │  │             │  │             │                          │   │
│   │  │ Read-only   │  │  Read-only  │                          │   │
│   │  └─────────────┘  └─────────────┘                          │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   Region: AP-SOUTHEAST-1 (Read Replica)                            │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │   │
│   │  │  Secondary  │  │  Secondary  │  │  Secondary  │         │   │
│   │  │    Node     │  │    Node     │  │    Node     │         │   │
│   │  │   Reads     │  │   Reads     │  │   Reads     │         │   │
│   │  └─────────────┘  └─────────────┘  └─────────────┘         │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Node Types

| Node Type | Purpose | Features |
|-----------|---------|----------|
| Electable | Primary/Secondary | Can become primary, handles writes |
| Read-Only | Read replicas | Cannot become primary, local reads |
| Analytics | Analytics workloads | Isolated from operational workload |

---

## Cluster Types and Tiers

### Cluster Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Atlas Cluster Types                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  FREE TIER (M0)           SHARED CLUSTERS        DEDICATED CLUSTERS │
│  ┌─────────────┐          ┌─────────────┐        ┌─────────────┐   │
│  │             │          │             │        │             │   │
│  │   512 MB    │          │   2-5 GB    │        │  10GB - TB  │   │
│  │   Storage   │          │   Storage   │        │   Storage   │   │
│  │             │          │             │        │             │   │
│  │  Learning   │          │   Dev/Test  │        │ Production  │   │
│  │  & Testing  │          │   Small     │        │  Workloads  │   │
│  │             │          │   Apps      │        │             │   │
│  └─────────────┘          └─────────────┘        └─────────────┘   │
│       Free                  $9-57/mo              $57+/mo          │
│                                                                     │
│  SERVERLESS                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │   Pay-per-operation pricing                                  │   │
│  │   Auto-scales to zero                                        │   │
│  │   No cluster management                                      │   │
│  │   Best for: Variable/unpredictable workloads                 │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Dedicated Cluster Tiers

| Tier | RAM | vCPUs | Storage | Use Case |
|------|-----|-------|---------|----------|
| M10 | 2 GB | 2 | 10 GB | Development |
| M20 | 4 GB | 2 | 20 GB | Small production |
| M30 | 8 GB | 2 | 40 GB | Medium workloads |
| M40 | 16 GB | 4 | 80 GB | Large workloads |
| M50 | 32 GB | 8 | 160 GB | High performance |
| M60 | 64 GB | 16 | 320 GB | Enterprise |
| M80 | 128 GB | 32 | 750 GB | Mission critical |
| M140+ | 192 GB+ | 48+ | 1 TB+ | Extreme workloads |

### Serverless Pricing

| Resource | Price |
|----------|-------|
| Read Processing Units (RPU) | $0.10 per million |
| Write Processing Units (WPU) | $1.00 per million |
| Storage | $0.25 per GB/month |
| Data Transfer | Standard cloud rates |

---

## Getting Started with Atlas

### Creating an Account and Cluster

```javascript
// Step 1: Sign up at cloud.mongodb.com

// Step 2: Create organization and project

// Step 3: Create cluster via UI or CLI/API

// Using Atlas CLI
// Install: brew install mongodb-atlas-cli

// Login
// atlas auth login

// Create cluster
/*
atlas clusters create my-cluster \
  --provider AWS \
  --region US_EAST_1 \
  --tier M10 \
  --mdbVersion 7.0
*/
```

### Connection String Formats

```javascript
// Standard Connection String
const standardUri = "mongodb+srv://username:password@cluster0.abc123.mongodb.net/mydb?retryWrites=true&w=majority"

// Connection with options
const optionsUri = "mongodb+srv://username:password@cluster0.abc123.mongodb.net/mydb" +
  "?retryWrites=true" +
  "&w=majority" +
  "&maxPoolSize=50" +
  "&readPreference=secondaryPreferred"

// Node.js connection
const { MongoClient } = require('mongodb')

async function connect() {
  const client = new MongoClient(standardUri, {
    // Additional options
    maxPoolSize: 50,
    wtimeoutMS: 2500,
    serverSelectionTimeoutMS: 5000
  })
  
  try {
    await client.connect()
    console.log('Connected to Atlas!')
    
    // Test connection
    await client.db('admin').command({ ping: 1 })
    console.log('Ping successful')
    
    return client
  } catch (error) {
    console.error('Connection failed:', error)
    throw error
  }
}
```

### Network Access Configuration

```javascript
// IP Access List - Allow specific IPs
/*
Via Atlas UI:
1. Go to Network Access
2. Add IP Address
3. Enter IP or CIDR block

Via Atlas CLI:
atlas accessLists create --currentIp
atlas accessLists create --ip 203.0.113.0/24 --comment "Office network"
*/

// Allow access from anywhere (not recommended for production)
// atlas accessLists create --ip 0.0.0.0/0 --comment "Allow all"

// Private endpoints for production
/*
AWS PrivateLink:
- Create VPC endpoint in your AWS account
- Configure Atlas to use private endpoint

Azure Private Link:
- Create private endpoint in Azure
- Connect to Atlas cluster

GCP Private Service Connect:
- Create forwarding rule
- Configure DNS
*/
```

### Database User Management

```javascript
// Create database user via Atlas CLI
/*
atlas dbusers create \
  --username appUser \
  --password mySecurePassword123 \
  --role readWriteAnyDatabase \
  --projectId <projectId>
*/

// User with specific database access
/*
atlas dbusers create \
  --username reportUser \
  --password reportPass123 \
  --role read@mydb \
  --projectId <projectId>
*/

// Built-in roles
const builtInRoles = {
  // Database-level
  'read': 'Read all non-system collections',
  'readWrite': 'Read and write all non-system collections',
  
  // Admin-level
  'dbAdmin': 'Database administration tasks',
  'userAdmin': 'Create and modify users and roles',
  
  // Cluster-level
  'readAnyDatabase': 'Read any database',
  'readWriteAnyDatabase': 'Read/write any database',
  'dbAdminAnyDatabase': 'Admin tasks any database',
  'clusterMonitor': 'Read-only access to monitoring tools',
  'atlasAdmin': 'Full Atlas administration'
}
```

---

## Atlas Features

### Atlas Search

```javascript
// Create search index
/*
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "title": {
        "type": "string",
        "analyzer": "lucene.standard"
      },
      "description": {
        "type": "string",
        "analyzer": "lucene.english"
      },
      "price": {
        "type": "number"
      },
      "categories": {
        "type": "string",
        "analyzer": "lucene.keyword"
      }
    }
  }
}
*/

// Search query with Atlas Search
db.products.aggregate([
  {
    $search: {
      index: "products_search",
      compound: {
        must: [
          {
            text: {
              query: "wireless headphones",
              path: ["title", "description"],
              fuzzy: { maxEdits: 1 }
            }
          }
        ],
        filter: [
          {
            range: {
              path: "price",
              gte: 50,
              lte: 200
            }
          }
        ]
      },
      highlight: {
        path: ["title", "description"]
      }
    }
  },
  {
    $project: {
      title: 1,
      description: 1,
      price: 1,
      score: { $meta: "searchScore" },
      highlights: { $meta: "searchHighlights" }
    }
  },
  { $limit: 10 }
])

// Autocomplete search
db.products.aggregate([
  {
    $search: {
      index: "autocomplete_index",
      autocomplete: {
        query: "wire",
        path: "title",
        tokenOrder: "sequential",
        fuzzy: { maxEdits: 1 }
      }
    }
  },
  { $limit: 5 },
  { $project: { title: 1, _id: 0 } }
])
```

### Atlas Vector Search

```javascript
// Create vector search index
/*
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "category"
    }
  ]
}
*/

// Vector search query
async function semanticSearch(queryEmbedding, category = null) {
  const pipeline = [
    {
      $vectorSearch: {
        index: "vector_index",
        path: "embedding",
        queryVector: queryEmbedding,
        numCandidates: 100,
        limit: 10,
        filter: category ? { category: category } : undefined
      }
    },
    {
      $project: {
        title: 1,
        content: 1,
        category: 1,
        score: { $meta: "vectorSearchScore" }
      }
    }
  ]
  
  return await db.collection('documents').aggregate(pipeline).toArray()
}

// Generate embedding and search
async function searchWithAI(query) {
  // Generate embedding using OpenAI
  const response = await openai.embeddings.create({
    model: "text-embedding-ada-002",
    input: query
  })
  
  const embedding = response.data[0].embedding
  return await semanticSearch(embedding)
}
```

### Atlas Data Lake

```javascript
// Federated query across Atlas and S3
/*
Data Lake Configuration:
{
  "databases": [
    {
      "name": "analytics",
      "collections": [
        {
          "name": "historical_orders",
          "dataSources": [
            {
              "storeName": "s3-archive",
              "path": "orders/{year}/{month}/*.json"
            }
          ]
        }
      ]
    }
  ],
  "stores": [
    {
      "name": "s3-archive",
      "provider": "s3",
      "bucket": "my-data-archive",
      "region": "us-east-1"
    }
  ]
}
*/

// Query across Atlas and Data Lake
db.getSiblingDB("analytics").historical_orders.aggregate([
  {
    $match: {
      year: 2024,
      status: "completed"
    }
  },
  {
    $unionWith: {
      coll: "orders",  // Current Atlas data
      pipeline: [
        { $match: { status: "completed" } }
      ]
    }
  },
  {
    $group: {
      _id: "$customerId",
      totalOrders: { $sum: 1 },
      totalSpent: { $sum: "$total" }
    }
  }
])
```

### Atlas Charts

```javascript
// Embed Atlas Charts in your application
/*
<iframe
  style="background: #F1F5F4; border: none; border-radius: 2px;"
  width="640"
  height="480"
  src="https://charts.mongodb.com/charts-project-abc123/embed/charts?id=chart-id&maxDataAge=3600&theme=light&autoRefresh=true">
</iframe>
*/

// Authenticated embedding
const getChartEmbedding = async (chartId) => {
  const token = await getAtlasToken()  // Your auth logic
  
  return `https://charts.mongodb.com/charts-project-abc123/embed/charts` +
    `?id=${chartId}` +
    `&maxDataAge=3600` +
    `&theme=light` +
    `&autoRefresh=true` +
    `&token=${token}`
}
```

### Atlas App Services (Realm)

```javascript
// Atlas Functions
exports = async function(payload) {
  const { userId, action } = payload
  
  const collection = context.services
    .get("mongodb-atlas")
    .db("mydb")
    .collection("users")
  
  if (action === "getProfile") {
    return await collection.findOne({ _id: userId })
  }
  
  if (action === "updateProfile") {
    return await collection.updateOne(
      { _id: userId },
      { $set: payload.updates }
    )
  }
}

// Atlas Triggers
/*
Database Trigger Configuration:
{
  "name": "onNewOrder",
  "type": "DATABASE",
  "config": {
    "operation_types": ["INSERT"],
    "database": "mydb",
    "collection": "orders",
    "service_name": "mongodb-atlas",
    "match": {},
    "full_document": true
  },
  "function_name": "processNewOrder"
}
*/

// Trigger function
exports = async function(changeEvent) {
  const order = changeEvent.fullDocument
  
  // Send notification
  await context.functions.execute("sendOrderNotification", {
    orderId: order._id,
    email: order.customerEmail
  })
  
  // Update inventory
  for (const item of order.items) {
    await context.services
      .get("mongodb-atlas")
      .db("mydb")
      .collection("inventory")
      .updateOne(
        { productId: item.productId },
        { $inc: { quantity: -item.quantity } }
      )
  }
}
```

---

## Atlas CLI and API

### Atlas CLI Commands

```bash
# Authentication
atlas auth login
atlas auth whoami
atlas auth logout

# Organizations and Projects
atlas organizations list
atlas projects list
atlas projects create "My Project" --orgId <orgId>

# Clusters
atlas clusters list
atlas clusters describe my-cluster
atlas clusters create my-cluster --provider AWS --region US_EAST_1 --tier M10
atlas clusters update my-cluster --tier M20
atlas clusters delete my-cluster
atlas clusters pause my-cluster
atlas clusters start my-cluster

# Database Users
atlas dbusers list
atlas dbusers create --username app --password secret123 --role readWrite
atlas dbusers delete app

# Network Access
atlas accessLists list
atlas accessLists create --currentIp
atlas accessLists create --ip 10.0.0.0/8 --comment "Private network"
atlas accessLists delete 10.0.0.0/8

# Backups
atlas backups snapshots list my-cluster
atlas backups restores start --clusterName my-cluster --snapshotId <id>

# Metrics
atlas metrics processes my-cluster --period P1D --granularity PT1H
```

### Atlas Admin API

```javascript
// Using Atlas Admin API
const axios = require('axios')
const crypto = require('crypto')

class AtlasAPI {
  constructor(publicKey, privateKey) {
    this.publicKey = publicKey
    this.privateKey = privateKey
    this.baseUrl = 'https://cloud.mongodb.com/api/atlas/v2'
  }
  
  async request(method, path, data = null) {
    const url = `${this.baseUrl}${path}`
    
    try {
      const response = await axios({
        method,
        url,
        data,
        auth: {
          username: this.publicKey,
          password: this.privateKey
        },
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/vnd.atlas.2023-01-01+json'
        }
      })
      
      return response.data
    } catch (error) {
      console.error('Atlas API Error:', error.response?.data || error.message)
      throw error
    }
  }
  
  // Clusters
  async listClusters(projectId) {
    return this.request('GET', `/groups/${projectId}/clusters`)
  }
  
  async getCluster(projectId, clusterName) {
    return this.request('GET', `/groups/${projectId}/clusters/${clusterName}`)
  }
  
  async createCluster(projectId, config) {
    return this.request('POST', `/groups/${projectId}/clusters`, config)
  }
  
  async updateCluster(projectId, clusterName, updates) {
    return this.request('PATCH', `/groups/${projectId}/clusters/${clusterName}`, updates)
  }
  
  async deleteCluster(projectId, clusterName) {
    return this.request('DELETE', `/groups/${projectId}/clusters/${clusterName}`)
  }
  
  // Database Users
  async listDbUsers(projectId) {
    return this.request('GET', `/groups/${projectId}/databaseUsers`)
  }
  
  async createDbUser(projectId, user) {
    return this.request('POST', `/groups/${projectId}/databaseUsers`, user)
  }
  
  // IP Access List
  async listAccessList(projectId) {
    return this.request('GET', `/groups/${projectId}/accessList`)
  }
  
  async addToAccessList(projectId, entries) {
    return this.request('POST', `/groups/${projectId}/accessList`, entries)
  }
  
  // Metrics
  async getProcessMetrics(projectId, processId, options) {
    const params = new URLSearchParams(options).toString()
    return this.request('GET', `/groups/${projectId}/processes/${processId}/measurements?${params}`)
  }
}

// Usage
const atlas = new AtlasAPI(
  process.env.ATLAS_PUBLIC_KEY,
  process.env.ATLAS_PRIVATE_KEY
)

// Create cluster
await atlas.createCluster(projectId, {
  name: "production-cluster",
  clusterType: "REPLICASET",
  replicationSpecs: [{
    numShards: 1,
    regionConfigs: [{
      providerName: "AWS",
      regionName: "US_EAST_1",
      electableSpecs: {
        instanceSize: "M30",
        nodeCount: 3
      },
      priority: 7
    }]
  }],
  backupEnabled: true,
  mongoDBMajorVersion: "7.0"
})
```

### Terraform Provider

```hcl
# Configure the MongoDB Atlas Provider
terraform {
  required_providers {
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.12"
    }
  }
}

provider "mongodbatlas" {
  public_key  = var.atlas_public_key
  private_key = var.atlas_private_key
}

# Create a project
resource "mongodbatlas_project" "myproject" {
  name   = "my-project"
  org_id = var.atlas_org_id
}

# Create a cluster
resource "mongodbatlas_cluster" "mycluster" {
  project_id = mongodbatlas_project.myproject.id
  name       = "production-cluster"
  
  # Provider settings
  provider_name               = "AWS"
  provider_region_name        = "US_EAST_1"
  provider_instance_size_name = "M30"
  
  # Cluster settings
  cluster_type = "REPLICASET"
  
  replication_specs {
    num_shards = 1
    regions_config {
      region_name     = "US_EAST_1"
      electable_nodes = 3
      priority        = 7
    }
  }
  
  # Backup
  cloud_backup = true
  
  # Version
  mongo_db_major_version = "7.0"
  
  # Auto-scaling
  auto_scaling_disk_gb_enabled = true
}

# Create database user
resource "mongodbatlas_database_user" "appuser" {
  project_id         = mongodbatlas_project.myproject.id
  username           = "app-user"
  password           = var.db_password
  auth_database_name = "admin"
  
  roles {
    role_name     = "readWrite"
    database_name = "mydb"
  }
}

# IP Access List
resource "mongodbatlas_project_ip_access_list" "myipaccess" {
  project_id = mongodbatlas_project.myproject.id
  cidr_block = "10.0.0.0/8"
  comment    = "VPC CIDR"
}

# Output connection string
output "connection_string" {
  value     = mongodbatlas_cluster.mycluster.connection_strings[0].standard_srv
  sensitive = true
}
```

---

## Summary

### Atlas vs Self-Managed

| Aspect | Atlas | Self-Managed |
|--------|-------|--------------|
| Setup time | Minutes | Hours/Days |
| Maintenance | Automated | Manual |
| Scaling | Click/API | Manual |
| Backups | Automated | Manual setup |
| Security | Built-in | Configure yourself |
| Monitoring | Included | Set up separately |
| Cost | Pay-as-you-go | Infrastructure + labor |
| Expertise needed | Low | High |

### Cluster Selection Guide

| Workload | Recommended Tier | Notes |
|----------|------------------|-------|
| Learning/Testing | M0 (Free) | 512MB, shared |
| Development | M10 | Dedicated, basic features |
| Small Production | M20-M30 | Most features, good performance |
| Medium Production | M40-M50 | High performance |
| Large Production | M60+ | Enterprise features |
| Variable Workload | Serverless | Pay per operation |

### Key Features Summary

| Feature | Description |
|---------|-------------|
| Atlas Search | Full-text search with Lucene |
| Vector Search | AI/ML embeddings search |
| Data Lake | Query S3/Azure Blob data |
| Charts | Embedded visualizations |
| App Services | Serverless functions, triggers |
| Online Archive | Automatic data tiering |

---

## Practice Questions

1. What are the differences between dedicated and serverless clusters?
2. How do you configure network access for Atlas clusters?
3. What is Atlas Search and how does it differ from regular MongoDB queries?
4. How do you set up cross-region replication in Atlas?
5. What are the benefits of using Atlas Data Lake?
6. How do you manage Atlas infrastructure with Terraform?
7. What built-in roles are available for database users?
8. How does Atlas Vector Search work with AI applications?

---

[← Previous: Data Migration](70-data-migration.md) | [Next: Atlas Configuration →](72-atlas-configuration.md)
