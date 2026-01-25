# Chapter 72: Atlas Configuration

## Table of Contents
- [Cluster Configuration](#cluster-configuration)
- [Storage Configuration](#storage-configuration)
- [Network Configuration](#network-configuration)
- [Performance Configuration](#performance-configuration)
- [Backup Configuration](#backup-configuration)
- [Advanced Settings](#advanced-settings)
- [Summary](#summary)

---

## Cluster Configuration

### Cluster Topology Options

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Cluster Topology Options                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   REPLICA SET (Default)                                             │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │   │
│   │  │ Primary │  │Secondary│  │Secondary│                     │   │
│   │  │         │◄─┤         │◄─┤         │                     │   │
│   │  └─────────┘  └─────────┘  └─────────┘                     │   │
│   │  Best for: Most workloads, up to ~1M ops/sec               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   SHARDED CLUSTER                                                   │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    ┌─────────┐                              │   │
│   │                    │ mongos  │                              │   │
│   │                    └────┬────┘                              │   │
│   │            ┌───────────┼───────────┐                       │   │
│   │            │           │           │                       │   │
│   │       ┌────┴────┐ ┌────┴────┐ ┌────┴────┐                 │   │
│   │       │ Shard 1 │ │ Shard 2 │ │ Shard 3 │                 │   │
│   │       │(3 nodes)│ │(3 nodes)│ │(3 nodes)│                 │   │
│   │       └─────────┘ └─────────┘ └─────────┘                 │   │
│   │  Best for: Very large datasets, high throughput            │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   GLOBAL CLUSTER (Multi-Region)                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  US-EAST        EU-WEST         AP-SOUTHEAST                │   │
│   │  ┌───────┐      ┌───────┐       ┌───────┐                  │   │
│   │  │Primary│◄────►│Second │◄─────►│Second │                  │   │
│   │  │Zone   │      │Zone   │       │Zone   │                  │   │
│   │  └───────┘      └───────┘       └───────┘                  │   │
│   │  Best for: Global applications, data residency             │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Creating a Replica Set Cluster

```javascript
// Atlas API - Create Replica Set
const clusterConfig = {
  name: "production-cluster",
  clusterType: "REPLICASET",
  
  // Replication configuration
  replicationSpecs: [{
    numShards: 1,
    regionConfigs: [{
      providerName: "AWS",
      regionName: "US_EAST_1",
      
      // Electable nodes (can become primary)
      electableSpecs: {
        instanceSize: "M30",
        nodeCount: 3,
        diskIOPS: 3000,
        ebsVolumeType: "PROVISIONED"
      },
      
      // Priority for primary election (1-7, higher = more likely)
      priority: 7,
      
      // Read-only nodes (optional)
      readOnlySpecs: {
        instanceSize: "M30",
        nodeCount: 0
      },
      
      // Analytics nodes (optional, isolated workload)
      analyticsSpecs: {
        instanceSize: "M30",
        nodeCount: 0
      }
    }]
  }],
  
  // MongoDB version
  mongoDBMajorVersion: "7.0",
  
  // Backup
  backupEnabled: true,
  pitEnabled: true,  // Point-in-time recovery
  
  // Encryption
  encryptionAtRestProvider: "AWS",
  
  // Auto-scaling
  autoScaling: {
    diskGBEnabled: true,
    compute: {
      enabled: true,
      scaleDownEnabled: true
    }
  }
}

await atlas.createCluster(projectId, clusterConfig)
```

### Creating a Sharded Cluster

```javascript
// Sharded cluster configuration
const shardedClusterConfig = {
  name: "sharded-production",
  clusterType: "SHARDED",
  
  replicationSpecs: [{
    numShards: 3,  // Number of shards
    
    regionConfigs: [{
      providerName: "AWS",
      regionName: "US_EAST_1",
      
      electableSpecs: {
        instanceSize: "M40",
        nodeCount: 3  // 3 nodes per shard = 9 total electable nodes
      },
      priority: 7
    }]
  }],
  
  mongoDBMajorVersion: "7.0",
  backupEnabled: true
}

// After creation, configure sharding
// Connect to cluster and run:
db.adminCommand({
  shardCollection: "mydb.orders",
  key: { customerId: "hashed" }  // Hashed sharding for even distribution
})

// Or range-based sharding
db.adminCommand({
  shardCollection: "mydb.logs",
  key: { timestamp: 1 }  // Range sharding for time-series data
})
```

### Multi-Region / Global Cluster

```javascript
// Global cluster with zone sharding
const globalClusterConfig = {
  name: "global-cluster",
  clusterType: "GEOSHARDED",
  
  replicationSpecs: [
    {
      // Zone 1: Americas
      zoneName: "Americas",
      numShards: 1,
      regionConfigs: [
        {
          providerName: "AWS",
          regionName: "US_EAST_1",
          electableSpecs: { instanceSize: "M30", nodeCount: 3 },
          priority: 7
        },
        {
          providerName: "AWS",
          regionName: "US_WEST_2",
          electableSpecs: { instanceSize: "M30", nodeCount: 2 },
          priority: 6
        }
      ]
    },
    {
      // Zone 2: Europe
      zoneName: "Europe",
      numShards: 1,
      regionConfigs: [
        {
          providerName: "AWS",
          regionName: "EU_WEST_1",
          electableSpecs: { instanceSize: "M30", nodeCount: 3 },
          priority: 7
        },
        {
          providerName: "AWS",
          regionName: "EU_CENTRAL_1",
          electableSpecs: { instanceSize: "M30", nodeCount: 2 },
          priority: 6
        }
      ]
    },
    {
      // Zone 3: Asia Pacific
      zoneName: "APAC",
      numShards: 1,
      regionConfigs: [
        {
          providerName: "AWS",
          regionName: "AP_SOUTHEAST_1",
          electableSpecs: { instanceSize: "M30", nodeCount: 3 },
          priority: 7
        }
      ]
    }
  ],
  
  mongoDBMajorVersion: "7.0",
  backupEnabled: true
}

// Configure zone sharding for data locality
// Users' data stays in their region
db.adminCommand({
  shardCollection: "mydb.users",
  key: { region: 1, _id: 1 }
})

// Define zone ranges
sh.addShardTag("shard0", "Americas")
sh.addShardTag("shard1", "Europe")
sh.addShardTag("shard2", "APAC")

sh.addTagRange("mydb.users", { region: "US" }, { region: "UZ" }, "Americas")
sh.addTagRange("mydb.users", { region: "EU" }, { region: "EZ" }, "Europe")
sh.addTagRange("mydb.users", { region: "AP" }, { region: "AZ" }, "APAC")
```

---

## Storage Configuration

### Storage Options

| Provider | Storage Type | Use Case |
|----------|--------------|----------|
| AWS | General Purpose (gp3) | Standard workloads |
| AWS | Provisioned IOPS (io1/io2) | High I/O requirements |
| Azure | Premium SSD | Production workloads |
| Azure | Standard SSD | Development/testing |
| GCP | SSD Persistent Disk | All workloads |

### Auto-Scaling Storage

```javascript
// Enable auto-scaling storage
const storageConfig = {
  autoScaling: {
    diskGBEnabled: true  // Automatically increase storage when needed
  },
  
  // Initial storage size
  diskSizeGB: 100,
  
  // For AWS Provisioned IOPS
  providerSettings: {
    providerName: "AWS",
    regionName: "US_EAST_1",
    instanceSizeName: "M30",
    diskIOPS: 3000,
    volumeType: "PROVISIONED"  // or "STANDARD"
  }
}

// Storage increases automatically when:
// - Disk usage exceeds 90%
// - Approaching storage limits

// Manual storage increase
await atlas.updateCluster(projectId, "my-cluster", {
  diskSizeGB: 200  // New size must be larger than current
})
```

### Online Archive Configuration

```javascript
// Configure Online Archive to automatically tier data
const archiveConfig = {
  clusterName: "production-cluster",
  collName: "orders",
  dbName: "mydb",
  
  // Archive criteria - move data older than 90 days
  criteria: {
    type: "DATE",
    dateField: "createdAt",
    dateFormat: "ISODATE",
    expireAfterDays: 90
  },
  
  // Partition fields for efficient querying
  partitionFields: [
    {
      fieldName: "createdAt",
      order: 0
    },
    {
      fieldName: "status",
      order: 1
    }
  ],
  
  // Schedule (optional)
  schedule: {
    type: "DAILY",
    startHour: 2,  // 2 AM UTC
    startMinute: 0
  }
}

// Create archive via API
await axios.post(
  `${atlasBaseUrl}/groups/${projectId}/clusters/${clusterName}/onlineArchives`,
  archiveConfig,
  { auth: { username: publicKey, password: privateKey } }
)

// Query archived data seamlessly
// Data Lake connection string automatically queries both live and archived data
db.orders.find({
  createdAt: { $gte: ISODate("2023-01-01") },
  status: "completed"
})
```

---

## Network Configuration

### Network Peering

```javascript
// AWS VPC Peering
const peeringConfig = {
  // Your AWS account
  awsAccountId: "123456789012",
  
  // Your VPC
  vpcId: "vpc-0123456789abcdef0",
  routeTableCidrBlock: "10.0.0.0/16",
  
  // Atlas configuration
  containerId: "container-id",  // Get from Atlas network container
  
  // Region must match
  accepterRegionName: "us-east-1"
}

// Create peering via Atlas API
await atlas.request('POST', `/groups/${projectId}/peers`, peeringConfig)

// After creation, accept peering in your AWS console
// Then update route tables to route traffic through peering connection

// Azure VNet Peering
const azurePeeringConfig = {
  azureDirectoryId: "your-directory-id",
  azureSubscriptionId: "your-subscription-id",
  resourceGroupName: "your-resource-group",
  vnetName: "your-vnet-name"
}

// GCP VPC Peering
const gcpPeeringConfig = {
  gcpProjectId: "your-gcp-project",
  networkName: "your-vpc-network"
}
```

### Private Endpoints

```javascript
// AWS PrivateLink Configuration
/*
Step 1: Create private endpoint service in Atlas
Step 2: Create VPC endpoint in your AWS account
Step 3: Configure security groups
*/

// Atlas API - Create private endpoint service
const privateEndpointConfig = {
  providerName: "AWS",
  region: "US_EAST_1"
}

const service = await atlas.request(
  'POST',
  `/groups/${projectId}/privateEndpoint/endpointService`,
  privateEndpointConfig
)

// Get service name for AWS
console.log('Service Name:', service.endpointServiceName)
// Output: com.amazonaws.vpce.us-east-1.vpce-svc-xxxxx

// Create VPC endpoint in AWS (via Terraform or AWS CLI)
/*
resource "aws_vpc_endpoint" "mongodb" {
  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.vpce.us-east-1.vpce-svc-xxxxx"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.mongodb.id]
}
*/

// Confirm endpoint in Atlas
await atlas.request(
  'PUT',
  `/groups/${projectId}/privateEndpoint/${service.id}/interfaceEndpoints/${endpointId}`,
  {}
)

// Connection string for private endpoint
const privateConnectionString = 
  "mongodb+srv://cluster0-pl-0.abc123.mongodb.net/mydb?retryWrites=true&w=majority"
```

### IP Access List Configuration

```javascript
// IP Access List management
class AtlasNetworkManager {
  constructor(atlas, projectId) {
    this.atlas = atlas
    this.projectId = projectId
  }
  
  async addIpAccess(entries) {
    // entries: [{ ipAddress: "x.x.x.x", comment: "description" }]
    // or [{ cidrBlock: "x.x.x.x/xx", comment: "description" }]
    // or [{ awsSecurityGroup: "sg-xxx", comment: "description" }]
    
    return await this.atlas.request(
      'POST',
      `/groups/${this.projectId}/accessList`,
      entries
    )
  }
  
  async removeIpAccess(entry) {
    // entry is IP address or CIDR block
    const encoded = encodeURIComponent(entry)
    return await this.atlas.request(
      'DELETE',
      `/groups/${this.projectId}/accessList/${encoded}`
    )
  }
  
  async listIpAccess() {
    return await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/accessList`
    )
  }
  
  // Temporary access (useful for CI/CD)
  async addTemporaryAccess(ip, durationMinutes = 60) {
    const deleteAfter = new Date(Date.now() + durationMinutes * 60 * 1000)
    
    return await this.addIpAccess([{
      ipAddress: ip,
      comment: `Temporary access until ${deleteAfter.toISOString()}`,
      deleteAfterDate: deleteAfter.toISOString()
    }])
  }
}

// Usage
const networkManager = new AtlasNetworkManager(atlas, projectId)

// Add permanent access
await networkManager.addIpAccess([
  { cidrBlock: "10.0.0.0/8", comment: "VPC CIDR" },
  { cidrBlock: "192.168.1.0/24", comment: "Office network" }
])

// Add temporary access for deployment
await networkManager.addTemporaryAccess("203.0.113.50", 30)  // 30 minutes
```

---

## Performance Configuration

### Compute Auto-Scaling

```javascript
// Configure compute auto-scaling
const autoScalingConfig = {
  autoScaling: {
    compute: {
      enabled: true,
      scaleDownEnabled: true,  // Allow scaling down during low usage
      
      // Scaling boundaries
      minInstanceSize: "M30",
      maxInstanceSize: "M60"
    },
    diskGBEnabled: true
  }
}

await atlas.updateCluster(projectId, "my-cluster", autoScalingConfig)

// Auto-scaling triggers:
// Scale UP when:
// - CPU utilization > 75% for sustained period
// - Memory utilization > 75% for sustained period
// - Disk I/O approaching limits

// Scale DOWN when:
// - CPU utilization < 50% for extended period
// - Memory utilization < 50% for extended period
```

### Connection Limits

| Tier | Max Connections |
|------|-----------------|
| M0 | 500 |
| M2/M5 | 500 |
| M10 | 1,500 |
| M20 | 3,000 |
| M30 | 6,000 |
| M40 | 16,000 |
| M50 | 32,000 |
| M60+ | 64,000+ |

### Index Management

```javascript
// Use Performance Advisor recommendations
// Via Atlas UI or API

// Get index suggestions
const suggestions = await atlas.request(
  'GET',
  `/groups/${projectId}/clusters/${clusterName}/performanceAdvisor/suggestedIndexes`
)

// Example response
/*
{
  "shapes": [
    {
      "avgMs": 1250,
      "count": 15000,
      "id": "shape-1",
      "inefficiencyScore": 85,
      "namespace": "mydb.orders",
      "operations": [
        {
          "predicates": [
            { "field": "status", "type": "equality" },
            { "field": "createdAt", "type": "range" }
          ],
          "stats": { "ms": 1250, "count": 15000 }
        }
      ],
      "suggestedIndex": {
        "status": 1,
        "createdAt": -1
      }
    }
  ],
  "suggestedIndexes": [
    {
      "id": "suggested-1",
      "impact": ["shape-1"],
      "index": { "status": 1, "createdAt": -1 },
      "namespace": "mydb.orders",
      "weight": 0.85
    }
  ]
}
*/

// Create suggested index
db.orders.createIndex({ status: 1, createdAt: -1 })

// Programmatic index management
async function applyIndexSuggestions(db, suggestions, minWeight = 0.5) {
  for (const suggestion of suggestions.suggestedIndexes) {
    if (suggestion.weight >= minWeight) {
      const [dbName, collName] = suggestion.namespace.split('.')
      
      console.log(`Creating index on ${suggestion.namespace}:`, suggestion.index)
      
      await db.getSiblingDB(dbName)
        .collection(collName)
        .createIndex(suggestion.index, { background: true })
    }
  }
}
```

### Query Profiler Configuration

```javascript
// Enable profiling via Atlas (UI or API)
/*
Profiling levels:
- Off: No profiling
- Slow Operations: Log operations > threshold
- All Operations: Log all operations (high overhead)
*/

// Set profiling via mongosh
db.setProfilingLevel(1, { slowms: 100 })  // Log ops > 100ms

// Query profiler data
db.system.profile.find({
  millis: { $gt: 100 }
}).sort({ ts: -1 }).limit(10)

// Atlas Query Profiler API
const slowQueries = await atlas.request(
  'GET',
  `/groups/${projectId}/clusters/${clusterName}/performanceAdvisor/slowQueryLogs?duration=PT24H`
)

// Analyze slow queries
function analyzeSlowQueries(queries) {
  const analysis = {
    byNamespace: {},
    byOperation: {},
    totalCount: queries.length,
    avgDuration: 0
  }
  
  let totalMs = 0
  
  for (const query of queries) {
    // Group by namespace
    const ns = query.namespace
    if (!analysis.byNamespace[ns]) {
      analysis.byNamespace[ns] = { count: 0, totalMs: 0 }
    }
    analysis.byNamespace[ns].count++
    analysis.byNamespace[ns].totalMs += query.millis
    
    // Group by operation type
    const op = query.op
    if (!analysis.byOperation[op]) {
      analysis.byOperation[op] = { count: 0, totalMs: 0 }
    }
    analysis.byOperation[op].count++
    analysis.byOperation[op].totalMs += query.millis
    
    totalMs += query.millis
  }
  
  analysis.avgDuration = totalMs / queries.length
  
  return analysis
}
```

---

## Backup Configuration

### Backup Policies

```javascript
// Configure backup policy
const backupPolicy = {
  policies: [{
    id: "policy-1",
    policyItems: [
      // Hourly snapshots - keep for 24 hours
      {
        frequencyType: "hourly",
        frequencyInterval: 6,  // Every 6 hours
        retentionUnit: "days",
        retentionValue: 1
      },
      // Daily snapshots - keep for 7 days
      {
        frequencyType: "daily",
        frequencyInterval: 1,
        retentionUnit: "days",
        retentionValue: 7
      },
      // Weekly snapshots - keep for 4 weeks
      {
        frequencyType: "weekly",
        frequencyInterval: 1,
        retentionUnit: "weeks",
        retentionValue: 4
      },
      // Monthly snapshots - keep for 12 months
      {
        frequencyType: "monthly",
        frequencyInterval: 1,
        retentionUnit: "months",
        retentionValue: 12
      }
    ]
  }],
  
  // Reference hour for daily/weekly/monthly (UTC)
  referenceHourOfDay: 3,
  referenceMinuteOfHour: 0,
  
  // Enable point-in-time recovery
  restoreWindowDays: 7,  // PITR window
  
  // Copy to another region (disaster recovery)
  copySettings: [{
    cloudProvider: "AWS",
    regionName: "US_WEST_2",
    frequencies: ["DAILY", "WEEKLY"]
  }]
}

await atlas.request(
  'PATCH',
  `/groups/${projectId}/clusters/${clusterName}/backup/schedule`,
  backupPolicy
)
```

### Restore Operations

```javascript
// List available snapshots
const snapshots = await atlas.request(
  'GET',
  `/groups/${projectId}/clusters/${clusterName}/backup/snapshots`
)

// Restore to same cluster (in-place)
const restoreJob = await atlas.request(
  'POST',
  `/groups/${projectId}/clusters/${clusterName}/backup/restoreJobs`,
  {
    snapshotId: "snapshot-id",
    deliveryType: "automated",
    targetClusterName: clusterName,
    targetGroupId: projectId
  }
)

// Restore to new cluster
const restoreToNew = await atlas.request(
  'POST',
  `/groups/${projectId}/clusters/${clusterName}/backup/restoreJobs`,
  {
    snapshotId: "snapshot-id",
    deliveryType: "automated",
    targetClusterName: "restored-cluster",
    targetGroupId: projectId
  }
)

// Point-in-time restore
const pitrRestore = await atlas.request(
  'POST',
  `/groups/${projectId}/clusters/${clusterName}/backup/restoreJobs`,
  {
    deliveryType: "automated",
    targetClusterName: "pitr-restored",
    targetGroupId: projectId,
    oplogTs: 1704067200,  // Unix timestamp
    oplogInc: 1
  }
)

// Download snapshot
const downloadJob = await atlas.request(
  'POST',
  `/groups/${projectId}/clusters/${clusterName}/backup/restoreJobs`,
  {
    snapshotId: "snapshot-id",
    deliveryType: "download"
  }
)

// Check restore status
const status = await atlas.request(
  'GET',
  `/groups/${projectId}/clusters/${clusterName}/backup/restoreJobs/${restoreJob.id}`
)
```

### Backup Compliance

```javascript
// Enable backup compliance policy (prevents deletion)
const compliancePolicy = {
  // Minimum retention requirements
  scheduledPolicyItems: [
    {
      frequencyType: "daily",
      frequencyInterval: 1,
      retentionUnit: "days",
      retentionValue: 30  // Minimum 30 days retention
    }
  ],
  
  // Point-in-time recovery
  restoreWindowDays: 14,
  
  // Compliance settings
  onDemandPolicyItem: {
    frequencyInterval: 1,
    retentionUnit: "days",
    retentionValue: 365  // Keep on-demand backups for 1 year
  },
  
  // Prevent accidental deletion
  encryptionAtRestEnabled: true,
  pitEnabled: true
}

// Apply at project level for compliance
await atlas.request(
  'PUT',
  `/groups/${projectId}/backupCompliancePolicy`,
  compliancePolicy
)
```

---

## Advanced Settings

### Cluster Advanced Configuration

```javascript
// Advanced cluster settings
const advancedConfig = {
  // Fail index key limit
  failIndexKeyTooLong: false,
  
  // JavaScript execution
  javascriptEnabled: true,
  
  // Minimum TLS version
  minimumEnabledTlsProtocol: "TLS1_2",
  
  // OpLog size (MB)
  oplogSizeMB: 2048,
  
  // Sample size for slow operations
  sampleSizeBIConnector: 1000,
  
  // Sample refresh interval
  sampleRefreshIntervalBIConnector: 300,
  
  // Default read concern
  defaultReadConcern: {
    level: "majority"
  },
  
  // Default write concern
  defaultWriteConcern: {
    w: "majority",
    j: true,
    wtimeout: 5000
  }
}

await atlas.request(
  'PATCH',
  `/groups/${projectId}/clusters/${clusterName}/processArgs`,
  advancedConfig
)
```

### Maintenance Windows

```javascript
// Configure maintenance window
const maintenanceConfig = {
  dayOfWeek: 7,  // Sunday (1=Sunday in some APIs, 7 in others)
  hourOfDay: 3,  // 3 AM UTC
  startASAP: false,
  
  // Auto-defer maintenance
  autoDeferOnceEnabled: true
}

await atlas.request(
  'PATCH',
  `/groups/${projectId}/maintenanceWindow`,
  maintenanceConfig
)

// Defer upcoming maintenance
await atlas.request(
  'POST',
  `/groups/${projectId}/maintenanceWindow/defer`
)

// Start maintenance immediately (if needed)
await atlas.request(
  'POST',
  `/groups/${projectId}/maintenanceWindow/startASAP`
)
```

### Labels and Tags

```javascript
// Add labels for organization and cost tracking
const labels = [
  { key: "environment", value: "production" },
  { key: "team", value: "backend" },
  { key: "cost-center", value: "engineering" },
  { key: "application", value: "ecommerce" }
]

await atlas.updateCluster(projectId, "my-cluster", {
  labels: labels
})

// Query clusters by label
const clusters = await atlas.listClusters(projectId)
const prodClusters = clusters.results.filter(c => 
  c.labels?.some(l => l.key === "environment" && l.value === "production")
)
```

### Serverless Configuration

```javascript
// Create serverless instance
const serverlessConfig = {
  name: "serverless-app",
  providerSettings: {
    providerName: "SERVERLESS",
    backingProviderName: "AWS",
    regionName: "US_EAST_1"
  },
  
  // Serverless-specific settings
  serverlessBackupOptions: {
    serverlessContinuousBackupEnabled: true
  },
  
  // Termination protection
  terminationProtectionEnabled: true
}

await atlas.request(
  'POST',
  `/groups/${projectId}/serverless`,
  serverlessConfig
)

// Serverless connection
const serverlessUri = "mongodb+srv://serverless-app.abc123.mongodb.net/mydb"

// Note: Serverless has some limitations:
// - No sharding
// - No $out/$merge to different databases
// - No collMod command
// - Fixed read/write concern
```

---

## Summary

### Configuration Checklist

```markdown
□ Cluster Setup
  □ Choose cluster type (replica set, sharded, global)
  □ Select appropriate tier
  □ Configure regions and zones
  □ Set MongoDB version

□ Storage
  □ Choose storage type
  □ Enable auto-scaling
  □ Configure Online Archive (if needed)

□ Network
  □ Configure IP access list
  □ Set up VPC peering or private endpoints
  □ Plan for production isolation

□ Performance
  □ Enable compute auto-scaling
  □ Review Performance Advisor
  □ Configure profiling level

□ Backup
  □ Set backup policy
  □ Configure retention periods
  □ Enable PITR if needed
  □ Set up cross-region backups

□ Security
  □ Configure encryption
  □ Set minimum TLS version
  □ Review database users and roles

□ Maintenance
  □ Set maintenance window
  □ Configure auto-defer settings
```

### Configuration Best Practices

| Area | Recommendation |
|------|----------------|
| Cluster Type | Start with replica set, shard when needed |
| Tier Selection | Start small, use auto-scaling |
| Network | Use private endpoints for production |
| Backups | Enable PITR, configure cross-region |
| Monitoring | Set up alerts for key metrics |
| Maintenance | Schedule during low-traffic periods |

---

## Practice Questions

1. What are the differences between replica set and sharded clusters?
2. How do you configure auto-scaling for compute resources?
3. What is Online Archive and when should you use it?
4. How do you set up VPC peering with Atlas?
5. What backup options are available in Atlas?
6. How do you configure point-in-time recovery?
7. What is the purpose of Analytics nodes?
8. How do you configure a maintenance window?

---

[← Previous: Atlas Overview](71-atlas-overview.md) | [Next: Atlas Security →](73-atlas-security.md)
