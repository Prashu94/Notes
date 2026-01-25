# Chapter 74: Atlas Monitoring

## Table of Contents
- [Monitoring Overview](#monitoring-overview)
- [Real-Time Performance Panel](#real-time-performance-panel)
- [Metrics and Measurements](#metrics-and-measurements)
- [Alerting](#alerting)
- [Performance Advisor](#performance-advisor)
- [Integration with External Tools](#integration-with-external-tools)
- [Summary](#summary)

---

## Monitoring Overview

### Atlas Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Atlas Monitoring System                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Data Collection                                                   │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│   │  │ MongoDB  │  │  System  │  │  Network │  │  Storage │   │   │
│   │  │ Metrics  │  │ Metrics  │  │  Metrics │  │  Metrics │   │   │
│   │  │          │  │          │  │          │  │          │   │   │
│   │  │• Ops/sec │  │• CPU %   │  │• Bytes   │  │• Disk    │   │   │
│   │  │• Latency │  │• Memory  │  │  In/Out  │  │  IOPS    │   │   │
│   │  │• Conns   │  │• Load    │  │• Conns   │  │• Space   │   │   │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│   Processing & Storage                                              │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  ┌────────────────┐  ┌────────────────┐                    │   │
│   │  │   Time Series  │  │   Aggregation  │                    │   │
│   │  │   Database     │  │   Engine       │                    │   │
│   │  │                │  │                │                    │   │
│   │  │ • 8-day raw    │  │ • 1-min avg    │                    │   │
│   │  │ • Granular     │  │ • 5-min avg    │                    │   │
│   │  │                │  │ • 1-hour avg   │                    │   │
│   │  └────────────────┘  └────────────────┘                    │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│   Visualization & Alerting                                          │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│   │  │   UI     │  │   API    │  │  Alerts  │  │ External │   │   │
│   │  │ Charts   │  │  Access  │  │  Engine  │  │ Systems  │   │   │
│   │  │          │  │          │  │          │  │          │   │   │
│   │  │• Real    │  │• REST    │  │• Email   │  │• DataDog │   │   │
│   │  │  time    │  │• JSON    │  │• Slack   │  │• PagerD  │   │   │
│   │  │• History │  │• CSV     │  │• Webhook │  │• Splunk  │   │   │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Monitoring Areas

| Area | Metrics | Purpose |
|------|---------|---------|
| Operations | ops/sec, latency | Query performance |
| Resources | CPU, memory, disk | Capacity planning |
| Connections | current, available | Connection management |
| Replication | lag, oplog window | Data consistency |
| Storage | disk usage, IOPS | Storage health |
| Network | bytes in/out | Traffic patterns |

---

## Real-Time Performance Panel

### Accessing Real-Time Metrics

```javascript
// Via Atlas UI:
// Clusters → Select Cluster → Metrics tab → Real Time

// Via Atlas API - Get real-time metrics
async function getRealTimeMetrics(atlas, projectId, processId) {
  const metrics = await atlas.request(
    'GET',
    `/groups/${projectId}/processes/${processId}/measurements`,
    {
      granularity: 'PT1M',  // 1 minute
      period: 'PT1H',       // Last hour
      m: [
        'OPCOUNTER_CMD',
        'OPCOUNTER_QUERY', 
        'OPCOUNTER_UPDATE',
        'OPCOUNTER_DELETE',
        'OPCOUNTER_INSERT',
        'CONNECTIONS',
        'SYSTEM_CPU_USER',
        'SYSTEM_MEMORY_USED'
      ].join(',')
    }
  )
  
  return metrics
}

// Process ID format: cluster0-shard-00-00.abc123.mongodb.net:27017
// Get process IDs for a cluster
async function getClusterProcesses(atlas, projectId, clusterName) {
  const processes = await atlas.request(
    'GET',
    `/groups/${projectId}/processes`
  )
  
  return processes.results.filter(p => 
    p.userAlias === clusterName || p.hostname.includes(clusterName)
  )
}
```

### Key Real-Time Panels

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Real-Time Performance Dashboard                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Operations                                                   │   │
│  │  ┌───────────────────────────────────────────────────────┐   │   │
│  │  │  Query: ████████████████████░░░░  850/sec             │   │   │
│  │  │  Insert: ██████░░░░░░░░░░░░░░░░░  150/sec             │   │   │
│  │  │  Update: ████████░░░░░░░░░░░░░░░  200/sec             │   │   │
│  │  │  Delete: █░░░░░░░░░░░░░░░░░░░░░░   25/sec             │   │   │
│  │  │  Command: ██░░░░░░░░░░░░░░░░░░░░░  50/sec             │   │   │
│  │  └───────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Latency (ms)                                                │   │
│  │  ┌───────────────────────────────────────────────────────┐   │   │
│  │  │  Read:  █████░░░░░░░░░░░░░░░░░░░  5ms avg             │   │   │
│  │  │  Write: ████████░░░░░░░░░░░░░░░░  8ms avg             │   │   │
│  │  └───────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐   │
│  │  Connections             │  │  Document Metrics            │   │
│  │  Current: 450/1500       │  │  Returned: 12,500/sec        │   │
│  │  ████████████░░░░░░░░░░░ │  │  Inserted: 150/sec           │   │
│  │  30% utilized            │  │  Updated: 200/sec            │   │
│  └──────────────────────────┘  │  Deleted: 25/sec             │   │
│                                └──────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Metrics and Measurements

### Available Metrics

```javascript
// Comprehensive metrics list
const atlasMetrics = {
  // Operation Counters
  operations: [
    'OPCOUNTER_CMD',       // Commands per second
    'OPCOUNTER_QUERY',     // Queries per second
    'OPCOUNTER_UPDATE',    // Updates per second
    'OPCOUNTER_DELETE',    // Deletes per second
    'OPCOUNTER_INSERT',    // Inserts per second
    'OPCOUNTER_GETMORE',   // GetMore operations per second
    'OPCOUNTER_REPL_CMD',  // Replicated commands
    'OPCOUNTER_REPL_UPDATE',
    'OPCOUNTER_REPL_DELETE',
    'OPCOUNTER_REPL_INSERT'
  ],
  
  // Document Metrics
  documents: [
    'DOCUMENT_METRICS_RETURNED',  // Documents returned
    'DOCUMENT_METRICS_INSERTED',  // Documents inserted
    'DOCUMENT_METRICS_UPDATED',   // Documents updated
    'DOCUMENT_METRICS_DELETED'    // Documents deleted
  ],
  
  // Operation Latency
  latency: [
    'OP_EXECUTION_TIME_READS',    // Read operation time
    'OP_EXECUTION_TIME_WRITES',   // Write operation time
    'OP_EXECUTION_TIME_COMMANDS'  // Command execution time
  ],
  
  // Connections
  connections: [
    'CONNECTIONS',          // Current connections
    'CONNECTIONS_MAX'       // Maximum connections
  ],
  
  // Memory
  memory: [
    'SYSTEM_MEMORY_USED',      // Used memory bytes
    'SYSTEM_MEMORY_AVAILABLE', // Available memory bytes
    'MEMORY_RESIDENT',         // Resident memory
    'MEMORY_VIRTUAL',          // Virtual memory
    'MEMORY_MAPPED'            // Memory mapped
  ],
  
  // CPU
  cpu: [
    'SYSTEM_CPU_USER',         // User CPU %
    'SYSTEM_CPU_KERNEL',       // Kernel CPU %
    'SYSTEM_CPU_IOWAIT',       // IO Wait CPU %
    'PROCESS_CPU_USER',        // MongoDB user CPU %
    'PROCESS_CPU_KERNEL',      // MongoDB kernel CPU %
    'PROCESS_NORMALIZED_CPU_USER',   // Normalized CPU
    'PROCESS_NORMALIZED_CPU_KERNEL'
  ],
  
  // Disk
  disk: [
    'DISK_PARTITION_IOPS_READ',    // Read IOPS
    'DISK_PARTITION_IOPS_WRITE',   // Write IOPS
    'DISK_PARTITION_IOPS_TOTAL',   // Total IOPS
    'DISK_PARTITION_UTILIZATION',  // Disk utilization %
    'DISK_PARTITION_LATENCY_READ', // Read latency ms
    'DISK_PARTITION_LATENCY_WRITE',// Write latency ms
    'DISK_PARTITION_SPACE_FREE',   // Free disk space
    'DISK_PARTITION_SPACE_USED',   // Used disk space
    'DISK_PARTITION_SPACE_PERCENT_FREE',
    'DISK_PARTITION_SPACE_PERCENT_USED'
  ],
  
  // Network
  network: [
    'NETWORK_BYTES_IN',    // Bytes received
    'NETWORK_BYTES_OUT',   // Bytes sent
    'NETWORK_NUM_REQUESTS' // Number of requests
  ],
  
  // Replication
  replication: [
    'OPLOG_MASTER_TIME',         // Oplog window (seconds)
    'OPLOG_MASTER_LAG_TIME_DIFF',// Replication lag
    'OPLOG_SLAVE_LAG_MASTER_TIME',
    'OPLOG_RATE_GB_PER_HOUR'     // Oplog growth rate
  ],
  
  // Query Targeting
  queryTargeting: [
    'QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED',
    'QUERY_TARGETING_SCANNED_PER_RETURNED'
  ],
  
  // Cache
  cache: [
    'CACHE_BYTES_READ_INTO',      // Bytes read into cache
    'CACHE_BYTES_WRITTEN_FROM',   // Bytes written from cache
    'CACHE_DIRTY_BYTES',          // Dirty bytes in cache
    'CACHE_USED_BYTES'            // Used cache bytes
  ]
}
```

### Retrieving Metrics via API

```javascript
// Metrics retrieval class
class AtlasMetricsClient {
  constructor(atlas, projectId) {
    this.atlas = atlas
    this.projectId = projectId
  }
  
  async getClusterMetrics(clusterName, options = {}) {
    const {
      period = 'PT24H',      // Last 24 hours
      granularity = 'PT5M',  // 5 minute intervals
      metrics = ['OPCOUNTER_QUERY', 'CONNECTIONS', 'SYSTEM_CPU_USER']
    } = options
    
    // Get processes for cluster
    const processes = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/processes`
    )
    
    const clusterProcesses = processes.results.filter(p => 
      p.userAlias === clusterName
    )
    
    // Get metrics for primary
    const primary = clusterProcesses.find(p => p.typeName === 'REPLICA_PRIMARY')
    
    if (!primary) {
      throw new Error(`No primary found for cluster ${clusterName}`)
    }
    
    const measurements = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/processes/${primary.id}/measurements`,
      {
        granularity,
        period,
        m: metrics.join(',')
      }
    )
    
    return this.formatMetrics(measurements)
  }
  
  async getDiskMetrics(clusterName, options = {}) {
    const {
      period = 'PT24H',
      granularity = 'PT1H'
    } = options
    
    const processes = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/processes`
    )
    
    const primary = processes.results.find(p => 
      p.userAlias === clusterName && p.typeName === 'REPLICA_PRIMARY'
    )
    
    // Get disk partitions
    const disks = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/processes/${primary.id}/disks`
    )
    
    const diskMetrics = []
    
    for (const disk of disks.results) {
      const metrics = await this.atlas.request(
        'GET',
        `/groups/${this.projectId}/processes/${primary.id}/disks/${disk.partitionName}/measurements`,
        {
          granularity,
          period,
          m: [
            'DISK_PARTITION_IOPS_READ',
            'DISK_PARTITION_IOPS_WRITE',
            'DISK_PARTITION_SPACE_PERCENT_USED',
            'DISK_PARTITION_LATENCY_READ',
            'DISK_PARTITION_LATENCY_WRITE'
          ].join(',')
        }
      )
      
      diskMetrics.push({
        partition: disk.partitionName,
        metrics: this.formatMetrics(metrics)
      })
    }
    
    return diskMetrics
  }
  
  formatMetrics(measurements) {
    const formatted = {}
    
    for (const measurement of measurements.measurements) {
      formatted[measurement.name] = {
        units: measurement.units,
        dataPoints: measurement.dataPoints.map(dp => ({
          timestamp: dp.timestamp,
          value: dp.value
        }))
      }
    }
    
    return formatted
  }
  
  // Calculate statistics
  calculateStats(dataPoints) {
    const values = dataPoints.filter(dp => dp.value !== null).map(dp => dp.value)
    
    if (values.length === 0) return null
    
    const sum = values.reduce((a, b) => a + b, 0)
    const avg = sum / values.length
    const sorted = [...values].sort((a, b) => a - b)
    
    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: avg,
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)]
    }
  }
}

// Usage
const metricsClient = new AtlasMetricsClient(atlas, projectId)

const metrics = await metricsClient.getClusterMetrics('production-cluster', {
  period: 'P7D',
  granularity: 'PT1H',
  metrics: [
    'OPCOUNTER_QUERY',
    'OPCOUNTER_INSERT',
    'OP_EXECUTION_TIME_READS',
    'CONNECTIONS',
    'SYSTEM_CPU_USER',
    'SYSTEM_MEMORY_USED'
  ]
})
```

### Database-Level Metrics

```javascript
// Get database statistics
async function getDatabaseStats(db) {
  const stats = await db.command({ dbStats: 1 })
  
  return {
    name: stats.db,
    collections: stats.collections,
    views: stats.views,
    objects: stats.objects,
    avgObjSize: stats.avgObjSize,
    dataSize: formatBytes(stats.dataSize),
    storageSize: formatBytes(stats.storageSize),
    indexes: stats.indexes,
    indexSize: formatBytes(stats.indexSize),
    totalSize: formatBytes(stats.totalSize),
    scaleFactor: stats.scaleFactor
  }
}

// Get collection statistics
async function getCollectionStats(db, collectionName) {
  const stats = await db.command({ collStats: collectionName })
  
  return {
    namespace: stats.ns,
    count: stats.count,
    size: formatBytes(stats.size),
    avgObjSize: stats.avgObjSize,
    storageSize: formatBytes(stats.storageSize),
    capped: stats.capped,
    nindexes: stats.nindexes,
    indexSizes: Object.entries(stats.indexSizes).map(([name, size]) => ({
      name,
      size: formatBytes(size)
    })),
    totalIndexSize: formatBytes(stats.totalIndexSize)
  }
}

// Get server status
async function getServerStatus(db) {
  const status = await db.admin().command({ serverStatus: 1 })
  
  return {
    uptime: status.uptime,
    connections: {
      current: status.connections.current,
      available: status.connections.available,
      totalCreated: status.connections.totalCreated
    },
    opcounters: status.opcounters,
    network: {
      bytesIn: formatBytes(status.network.bytesIn),
      bytesOut: formatBytes(status.network.bytesOut),
      numRequests: status.network.numRequests
    },
    memory: {
      resident: formatBytes(status.mem.resident * 1024 * 1024),
      virtual: formatBytes(status.mem.virtual * 1024 * 1024)
    },
    replication: status.repl
  }
}

function formatBytes(bytes) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let size = bytes
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`
}
```

---

## Alerting

### Alert Configuration

```javascript
// Create alert configuration
const alertConfig = {
  // Alert conditions
  eventTypeName: "OUTSIDE_METRIC_THRESHOLD",
  
  // Metric threshold
  metricThreshold: {
    metricName: "SYSTEM_CPU_USER",
    operator: "GREATER_THAN",
    threshold: 80,
    units: "RAW",
    mode: "AVERAGE"
  },
  
  // Notification settings
  notifications: [
    {
      // Email notification
      typeName: "EMAIL",
      emailAddress: "ops@company.com",
      intervalMin: 60,
      delayMin: 0
    },
    {
      // Slack notification
      typeName: "SLACK",
      apiToken: "xoxb-slack-token",
      channelName: "#mongodb-alerts",
      intervalMin: 15
    },
    {
      // PagerDuty notification
      typeName: "PAGERDUTY",
      serviceKey: "pagerduty-service-key",
      intervalMin: 5
    },
    {
      // Webhook notification
      typeName: "WEBHOOK",
      webhookUrl: "https://api.company.com/webhooks/atlas",
      webhookSecret: "webhook-secret",
      intervalMin: 5
    }
  ],
  
  // Enable/disable
  enabled: true
}

await atlas.request(
  'POST',
  `/groups/${projectId}/alertConfigs`,
  alertConfig
)
```

### Common Alert Configurations

```javascript
// Alert templates for common scenarios
const alertTemplates = {
  // High CPU usage
  highCPU: {
    eventTypeName: "OUTSIDE_METRIC_THRESHOLD",
    metricThreshold: {
      metricName: "SYSTEM_CPU_USER",
      operator: "GREATER_THAN",
      threshold: 80,
      units: "RAW",
      mode: "AVERAGE"
    }
  },
  
  // Low disk space
  lowDiskSpace: {
    eventTypeName: "OUTSIDE_METRIC_THRESHOLD",
    metricThreshold: {
      metricName: "DISK_PARTITION_SPACE_PERCENT_USED",
      operator: "GREATER_THAN",
      threshold: 85,
      units: "RAW",
      mode: "AVERAGE"
    }
  },
  
  // High connection usage
  highConnections: {
    eventTypeName: "OUTSIDE_METRIC_THRESHOLD",
    metricThreshold: {
      metricName: "CONNECTIONS",
      operator: "GREATER_THAN",
      threshold: 1000,  // Adjust based on tier
      units: "RAW",
      mode: "AVERAGE"
    }
  },
  
  // Replication lag
  replicationLag: {
    eventTypeName: "OUTSIDE_METRIC_THRESHOLD",
    metricThreshold: {
      metricName: "OPLOG_SLAVE_LAG_MASTER_TIME",
      operator: "GREATER_THAN",
      threshold: 60,  // 60 seconds
      units: "SECONDS",
      mode: "AVERAGE"
    }
  },
  
  // Query targeting
  poorQueryTargeting: {
    eventTypeName: "OUTSIDE_METRIC_THRESHOLD",
    metricThreshold: {
      metricName: "QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED",
      operator: "GREATER_THAN",
      threshold: 1000,  // Scanning 1000x more than returned
      units: "RAW",
      mode: "AVERAGE"
    }
  },
  
  // Slow queries
  slowOperations: {
    eventTypeName: "OUTSIDE_METRIC_THRESHOLD",
    metricThreshold: {
      metricName: "OP_EXECUTION_TIME_READS",
      operator: "GREATER_THAN",
      threshold: 100,  // 100ms
      units: "MILLISECONDS",
      mode: "AVERAGE"
    }
  },
  
  // Cluster events
  primaryElection: {
    eventTypeName: "PRIMARY_ELECTED"
  },
  
  nodeRecovering: {
    eventTypeName: "REPLICATION_OPLOG_WINDOW_RUNNING_OUT"
  },
  
  userCreated: {
    eventTypeName: "USER_CREATED"
  },
  
  clusterScaled: {
    eventTypeName: "CLUSTER_MONGOS_IS_MISSING"
  }
}

// Create multiple alerts
async function setupStandardAlerts(atlas, projectId, notifications) {
  const alertsToCreate = [
    { ...alertTemplates.highCPU, notifications },
    { ...alertTemplates.lowDiskSpace, notifications },
    { ...alertTemplates.highConnections, notifications },
    { ...alertTemplates.replicationLag, notifications },
    { ...alertTemplates.poorQueryTargeting, notifications }
  ]
  
  const results = []
  
  for (const alert of alertsToCreate) {
    const result = await atlas.request(
      'POST',
      `/groups/${projectId}/alertConfigs`,
      { ...alert, enabled: true }
    )
    results.push(result)
  }
  
  return results
}
```

### Alert Management

```javascript
// Alert management class
class AtlasAlertManager {
  constructor(atlas, projectId) {
    this.atlas = atlas
    this.projectId = projectId
  }
  
  // List all alerts
  async listAlerts(status = null) {
    const params = status ? { status } : {}
    
    return await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/alerts`,
      params
    )
  }
  
  // Get active alerts
  async getActiveAlerts() {
    return await this.listAlerts('OPEN')
  }
  
  // Acknowledge alert
  async acknowledgeAlert(alertId, comment = '') {
    return await this.atlas.request(
      'PATCH',
      `/groups/${this.projectId}/alerts/${alertId}`,
      {
        status: 'ACKNOWLEDGED',
        acknowledgedUntil: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        acknowledgementComment: comment
      }
    )
  }
  
  // List alert configurations
  async listAlertConfigs() {
    return await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/alertConfigs`
    )
  }
  
  // Toggle alert config
  async toggleAlertConfig(configId, enabled) {
    return await this.atlas.request(
      'PATCH',
      `/groups/${this.projectId}/alertConfigs/${configId}`,
      { enabled }
    )
  }
  
  // Delete alert config
  async deleteAlertConfig(configId) {
    return await this.atlas.request(
      'DELETE',
      `/groups/${this.projectId}/alertConfigs/${configId}`
    )
  }
  
  // Generate alert summary
  async getAlertSummary() {
    const alerts = await this.listAlerts()
    
    const summary = {
      total: alerts.totalCount,
      byStatus: {},
      byType: {},
      recentAlerts: []
    }
    
    for (const alert of alerts.results) {
      // Count by status
      summary.byStatus[alert.status] = (summary.byStatus[alert.status] || 0) + 1
      
      // Count by type
      summary.byType[alert.eventTypeName] = (summary.byType[alert.eventTypeName] || 0) + 1
      
      // Recent alerts (last 24 hours)
      const alertDate = new Date(alert.created)
      if (Date.now() - alertDate.getTime() < 24 * 60 * 60 * 1000) {
        summary.recentAlerts.push({
          id: alert.id,
          type: alert.eventTypeName,
          status: alert.status,
          created: alert.created,
          cluster: alert.clusterName
        })
      }
    }
    
    return summary
  }
}
```

---

## Performance Advisor

### Using Performance Advisor

```javascript
// Performance Advisor API client
class PerformanceAdvisor {
  constructor(atlas, projectId, clusterName) {
    this.atlas = atlas
    this.projectId = projectId
    this.clusterName = clusterName
  }
  
  // Get suggested indexes
  async getSuggestedIndexes(options = {}) {
    const {
      duration = 'PT24H',  // Last 24 hours
      namespaces = null    // Filter by namespace
    } = options
    
    let path = `/groups/${this.projectId}/clusters/${this.clusterName}` +
               `/performanceAdvisor/suggestedIndexes?duration=${duration}`
    
    if (namespaces) {
      path += `&namespaces=${namespaces.join(',')}`
    }
    
    return await this.atlas.request('GET', path)
  }
  
  // Get slow query logs
  async getSlowQueryLogs(options = {}) {
    const {
      duration = 'PT24H',
      nLogs = 20000
    } = options
    
    return await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/clusters/${this.clusterName}` +
      `/performanceAdvisor/slowQueryLogs?duration=${duration}&nLogs=${nLogs}`
    )
  }
  
  // Get namespaces with slow queries
  async getSlowQueryNamespaces(options = {}) {
    const { duration = 'PT24H' } = options
    
    return await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/clusters/${this.clusterName}` +
      `/performanceAdvisor/namespaces?duration=${duration}`
    )
  }
  
  // Analyze and generate report
  async generateReport() {
    const [suggestions, slowLogs, namespaces] = await Promise.all([
      this.getSuggestedIndexes(),
      this.getSlowQueryLogs({ nLogs: 1000 }),
      this.getSlowQueryNamespaces()
    ])
    
    const report = {
      generatedAt: new Date().toISOString(),
      cluster: this.clusterName,
      
      indexSuggestions: suggestions.suggestedIndexes?.map(s => ({
        namespace: s.namespace,
        index: s.index,
        impact: s.impact,
        weight: s.weight
      })) || [],
      
      slowQuerySummary: this.summarizeSlowQueries(slowLogs.slowQueries || []),
      
      hotNamespaces: namespaces.namespaces?.map(ns => ({
        namespace: ns.namespace,
        type: ns.type
      })) || []
    }
    
    return report
  }
  
  summarizeSlowQueries(queries) {
    const byNamespace = {}
    const byOperation = {}
    let totalMs = 0
    
    for (const query of queries) {
      // Group by namespace
      if (!byNamespace[query.namespace]) {
        byNamespace[query.namespace] = { count: 0, totalMs: 0 }
      }
      byNamespace[query.namespace].count++
      byNamespace[query.namespace].totalMs += query.millis
      
      // Group by operation
      const op = query.op || 'unknown'
      if (!byOperation[op]) {
        byOperation[op] = { count: 0, totalMs: 0 }
      }
      byOperation[op].count++
      byOperation[op].totalMs += query.millis
      
      totalMs += query.millis
    }
    
    return {
      totalQueries: queries.length,
      totalTimeMs: totalMs,
      avgTimeMs: queries.length > 0 ? totalMs / queries.length : 0,
      byNamespace: Object.entries(byNamespace)
        .map(([ns, data]) => ({ namespace: ns, ...data }))
        .sort((a, b) => b.totalMs - a.totalMs)
        .slice(0, 10),
      byOperation
    }
  }
}

// Usage
const advisor = new PerformanceAdvisor(atlas, projectId, 'production-cluster')
const report = await advisor.generateReport()

console.log('Index Suggestions:', report.indexSuggestions)
console.log('Slow Query Summary:', report.slowQuerySummary)
```

### Implementing Suggestions

```javascript
// Apply index suggestions
async function applyIndexSuggestions(db, suggestions, options = {}) {
  const {
    minWeight = 0.5,
    dryRun = true
  } = options
  
  const results = []
  
  for (const suggestion of suggestions) {
    if (suggestion.weight < minWeight) {
      results.push({
        namespace: suggestion.namespace,
        index: suggestion.index,
        applied: false,
        reason: `Weight ${suggestion.weight} below threshold ${minWeight}`
      })
      continue
    }
    
    const [dbName, collName] = suggestion.namespace.split('.')
    
    if (dryRun) {
      results.push({
        namespace: suggestion.namespace,
        index: suggestion.index,
        applied: false,
        reason: 'Dry run mode'
      })
    } else {
      try {
        await db.getSiblingDB(dbName)
          .collection(collName)
          .createIndex(suggestion.index, { background: true })
        
        results.push({
          namespace: suggestion.namespace,
          index: suggestion.index,
          applied: true
        })
      } catch (error) {
        results.push({
          namespace: suggestion.namespace,
          index: suggestion.index,
          applied: false,
          reason: error.message
        })
      }
    }
  }
  
  return results
}
```

---

## Integration with External Tools

### DataDog Integration

```javascript
// Configure DataDog integration
const datadogConfig = {
  type: "DATADOG",
  apiKey: process.env.DATADOG_API_KEY,
  region: "US"  // or "EU"
}

await atlas.request(
  'POST',
  `/groups/${projectId}/integrations/DATADOG`,
  datadogConfig
)

// DataDog dashboards will automatically receive:
// - MongoDB metrics
// - Atlas cluster metrics
// - Custom metrics via tags
```

### Prometheus Integration

```javascript
// Export metrics for Prometheus
// Atlas provides a Prometheus endpoint

// In your Prometheus config:
/*
scrape_configs:
  - job_name: 'mongodb-atlas'
    scheme: https
    basic_auth:
      username: '<public-key>'
      password: '<private-key>'
    static_configs:
      - targets:
        - 'cloud.mongodb.com'
    metrics_path: '/api/atlas/v2/groups/<project-id>/prometheus/metrics'
    params:
      period: ['PT1M']
*/

// Custom metrics exporter
class AtlasPrometheusExporter {
  constructor(atlas, projectId) {
    this.atlas = atlas
    this.projectId = projectId
  }
  
  async getMetrics() {
    const processes = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/processes`
    )
    
    let output = ''
    
    for (const process of processes.results) {
      const measurements = await this.atlas.request(
        'GET',
        `/groups/${this.projectId}/processes/${process.id}/measurements`,
        {
          granularity: 'PT1M',
          period: 'PT5M',
          m: 'OPCOUNTER_QUERY,CONNECTIONS,SYSTEM_CPU_USER'
        }
      )
      
      for (const measurement of measurements.measurements) {
        const latest = measurement.dataPoints[measurement.dataPoints.length - 1]
        
        if (latest && latest.value !== null) {
          const metricName = `mongodb_${measurement.name.toLowerCase()}`
          const labels = `{cluster="${process.userAlias}",host="${process.hostname}"}`
          
          output += `${metricName}${labels} ${latest.value}\n`
        }
      }
    }
    
    return output
  }
}

// Express endpoint for Prometheus
app.get('/metrics', async (req, res) => {
  const exporter = new AtlasPrometheusExporter(atlas, projectId)
  const metrics = await exporter.getMetrics()
  
  res.set('Content-Type', 'text/plain')
  res.send(metrics)
})
```

### Slack Notifications

```javascript
// Custom Slack notification handler
class AtlasSlackNotifier {
  constructor(webhookUrl) {
    this.webhookUrl = webhookUrl
  }
  
  async sendAlert(alert) {
    const color = this.getColorForSeverity(alert.severity)
    
    const message = {
      attachments: [{
        color: color,
        title: `Atlas Alert: ${alert.eventTypeName}`,
        text: alert.description,
        fields: [
          {
            title: 'Cluster',
            value: alert.clusterName,
            short: true
          },
          {
            title: 'Status',
            value: alert.status,
            short: true
          },
          {
            title: 'Metric',
            value: alert.metricName || 'N/A',
            short: true
          },
          {
            title: 'Current Value',
            value: alert.currentValue?.number?.toString() || 'N/A',
            short: true
          }
        ],
        footer: 'MongoDB Atlas',
        ts: Math.floor(new Date(alert.created).getTime() / 1000)
      }]
    }
    
    await fetch(this.webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(message)
    })
  }
  
  getColorForSeverity(severity) {
    const colors = {
      CRITICAL: '#FF0000',
      WARNING: '#FFA500',
      INFO: '#0000FF'
    }
    return colors[severity] || '#808080'
  }
}

// Webhook handler for Atlas alerts
app.post('/webhooks/atlas', async (req, res) => {
  const alert = req.body
  
  const notifier = new AtlasSlackNotifier(process.env.SLACK_WEBHOOK_URL)
  await notifier.sendAlert(alert)
  
  res.status(200).send('OK')
})
```

### Custom Dashboard

```javascript
// Build custom monitoring dashboard data
class AtlasDashboard {
  constructor(atlas, projectId) {
    this.atlas = atlas
    this.projectId = projectId
    this.metricsClient = new AtlasMetricsClient(atlas, projectId)
  }
  
  async getDashboardData(clusterName) {
    const [
      realtimeMetrics,
      alerts,
      performanceAdvice
    ] = await Promise.all([
      this.metricsClient.getClusterMetrics(clusterName, {
        period: 'PT1H',
        granularity: 'PT1M',
        metrics: [
          'OPCOUNTER_QUERY',
          'OPCOUNTER_INSERT',
          'OPCOUNTER_UPDATE',
          'CONNECTIONS',
          'SYSTEM_CPU_USER',
          'SYSTEM_MEMORY_USED',
          'OP_EXECUTION_TIME_READS'
        ]
      }),
      this.getAlertSummary(),
      this.getPerformanceAdvice(clusterName)
    ])
    
    return {
      cluster: clusterName,
      timestamp: new Date().toISOString(),
      
      realtime: {
        operations: this.getLatestValue(realtimeMetrics, 'OPCOUNTER_QUERY'),
        connections: this.getLatestValue(realtimeMetrics, 'CONNECTIONS'),
        cpuPercent: this.getLatestValue(realtimeMetrics, 'SYSTEM_CPU_USER'),
        readLatencyMs: this.getLatestValue(realtimeMetrics, 'OP_EXECUTION_TIME_READS')
      },
      
      trends: {
        operations: this.calculateTrend(realtimeMetrics, 'OPCOUNTER_QUERY'),
        connections: this.calculateTrend(realtimeMetrics, 'CONNECTIONS'),
        cpu: this.calculateTrend(realtimeMetrics, 'SYSTEM_CPU_USER')
      },
      
      alerts: alerts,
      
      recommendations: performanceAdvice
    }
  }
  
  getLatestValue(metrics, metricName) {
    const metric = metrics[metricName]
    if (!metric) return null
    
    const dataPoints = metric.dataPoints.filter(dp => dp.value !== null)
    return dataPoints.length > 0 ? dataPoints[dataPoints.length - 1].value : null
  }
  
  calculateTrend(metrics, metricName) {
    const metric = metrics[metricName]
    if (!metric) return 'stable'
    
    const values = metric.dataPoints
      .filter(dp => dp.value !== null)
      .map(dp => dp.value)
    
    if (values.length < 2) return 'stable'
    
    const firstHalf = values.slice(0, Math.floor(values.length / 2))
    const secondHalf = values.slice(Math.floor(values.length / 2))
    
    const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length
    const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length
    
    const change = (secondAvg - firstAvg) / firstAvg
    
    if (change > 0.1) return 'increasing'
    if (change < -0.1) return 'decreasing'
    return 'stable'
  }
  
  async getAlertSummary() {
    const alerts = await this.atlas.request(
      'GET',
      `/groups/${this.projectId}/alerts?status=OPEN`
    )
    
    return {
      open: alerts.totalCount,
      critical: alerts.results.filter(a => a.severity === 'CRITICAL').length,
      warning: alerts.results.filter(a => a.severity === 'WARNING').length
    }
  }
  
  async getPerformanceAdvice(clusterName) {
    const advisor = new PerformanceAdvisor(this.atlas, this.projectId, clusterName)
    const suggestions = await advisor.getSuggestedIndexes({ duration: 'PT24H' })
    
    return {
      indexSuggestions: suggestions.suggestedIndexes?.length || 0,
      topSuggestion: suggestions.suggestedIndexes?.[0] || null
    }
  }
}
```

---

## Summary

### Key Metrics to Monitor

| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|-------------------|
| CPU Usage | > 70% | > 90% |
| Memory Usage | > 80% | > 95% |
| Disk Usage | > 80% | > 90% |
| Connections | > 80% of max | > 95% of max |
| Replication Lag | > 10 sec | > 60 sec |
| Query Targeting | > 100:1 | > 1000:1 |
| Read Latency | > 50ms | > 200ms |

### Monitoring Best Practices

| Practice | Description |
|----------|-------------|
| Set baseline | Understand normal metrics before alerting |
| Multi-level alerts | Warning → Critical escalation |
| Right granularity | 1 min for real-time, 1 hour for trends |
| Include context | Alert messages should be actionable |
| Regular review | Weekly review of alert configs |
| Integration | Connect to team tools (Slack, PagerDuty) |

### Alert Response Runbook

```markdown
## High CPU Alert
1. Check slow query log for expensive operations
2. Review Performance Advisor suggestions
3. Check for index scans (COLLSCAN)
4. Consider scaling up or optimizing queries

## Low Disk Space Alert
1. Review data growth patterns
2. Enable auto-scaling if not enabled
3. Archive old data if appropriate
4. Increase storage allocation

## High Connection Count
1. Check for connection leaks in application
2. Review connection pool settings
3. Consider connection limits per user
4. Scale up if legitimate traffic

## Replication Lag
1. Check secondary node health
2. Review oplog size
3. Check network between nodes
4. Investigate write heavy operations
```

---

## Practice Questions

1. What are the key metrics to monitor in Atlas?
2. How do you configure custom alerts?
3. What is Performance Advisor and how does it help?
4. How do you integrate Atlas with external monitoring tools?
5. What metrics indicate poor query performance?
6. How do you access slow query logs in Atlas?
7. What is query targeting and why is it important?
8. How do you set up Prometheus integration with Atlas?

---

[← Previous: Atlas Security](73-atlas-security.md) | [Next: Real-World Patterns →](75-real-world-patterns.md)
