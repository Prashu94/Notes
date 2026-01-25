# Chapter 77: Migration Strategies

## Table of Contents
- [Migration Planning](#migration-planning)
- [SQL to MongoDB Migration](#sql-to-mongodb-migration)
- [MongoDB Version Upgrades](#mongodb-version-upgrades)
- [Cloud Migration](#cloud-migration)
- [Data Center Migration](#data-center-migration)
- [Schema Evolution](#schema-evolution)
- [Migration Tools and Automation](#migration-tools-and-automation)
- [Summary](#summary)

---

## Migration Planning

### Migration Assessment Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Migration Planning Framework                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 1: Assessment                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Current system analysis                                    │   │
│  │  • Data volume and complexity                                 │   │
│  │  • Application dependencies                                   │   │
│  │  • Performance requirements                                   │   │
│  │  • Downtime tolerance                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  Phase 2: Design                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Target schema design                                       │   │
│  │  • Migration strategy selection                               │   │
│  │  • Tooling decisions                                          │   │
│  │  • Rollback plan                                              │   │
│  │  • Testing approach                                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  Phase 3: Execution                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Environment setup                                          │   │
│  │  • Initial data migration                                     │   │
│  │  • Incremental sync                                           │   │
│  │  • Application cutover                                        │   │
│  │  • Validation                                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  Phase 4: Optimization                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Performance tuning                                         │   │
│  │  • Index optimization                                         │   │
│  │  • Monitoring setup                                           │   │
│  │  • Documentation                                              │   │
│  │  • Training                                                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Migration Strategy Selection

| Strategy | Downtime | Complexity | Risk | Best For |
|----------|----------|------------|------|----------|
| Big Bang | Hours-Days | Low | High | Small datasets |
| Phased | Minutes per phase | Medium | Medium | Modular systems |
| Parallel Run | Zero | High | Low | Critical systems |
| Strangler Fig | Zero | High | Low | Gradual modernization |

### Migration Checklist

```javascript
// Migration planning checklist
const migrationChecklist = {
  assessment: {
    dataAnalysis: [
      { task: 'Document current schema', status: 'pending' },
      { task: 'Calculate data volumes', status: 'pending' },
      { task: 'Identify relationships', status: 'pending' },
      { task: 'Map data types', status: 'pending' },
      { task: 'Document constraints', status: 'pending' }
    ],
    applicationAnalysis: [
      { task: 'List all applications', status: 'pending' },
      { task: 'Document query patterns', status: 'pending' },
      { task: 'Identify connection strings', status: 'pending' },
      { task: 'Map ORM usage', status: 'pending' }
    ],
    requirements: [
      { task: 'Define downtime tolerance', status: 'pending' },
      { task: 'Set performance targets', status: 'pending' },
      { task: 'Identify compliance needs', status: 'pending' },
      { task: 'Document SLAs', status: 'pending' }
    ]
  },
  
  planning: {
    design: [
      { task: 'Design target schema', status: 'pending' },
      { task: 'Plan index strategy', status: 'pending' },
      { task: 'Design sharding strategy', status: 'pending' }
    ],
    strategy: [
      { task: 'Choose migration approach', status: 'pending' },
      { task: 'Create rollback plan', status: 'pending' },
      { task: 'Define success criteria', status: 'pending' }
    ],
    testing: [
      { task: 'Create test plan', status: 'pending' },
      { task: 'Prepare test data', status: 'pending' },
      { task: 'Define validation queries', status: 'pending' }
    ]
  },
  
  execution: {
    preparation: [
      { task: 'Set up target environment', status: 'pending' },
      { task: 'Configure networking', status: 'pending' },
      { task: 'Set up monitoring', status: 'pending' }
    ],
    migration: [
      { task: 'Run initial migration', status: 'pending' },
      { task: 'Verify data integrity', status: 'pending' },
      { task: 'Set up incremental sync', status: 'pending' }
    ],
    cutover: [
      { task: 'Update application configs', status: 'pending' },
      { task: 'Switch traffic', status: 'pending' },
      { task: 'Monitor for issues', status: 'pending' }
    ]
  },
  
  postMigration: {
    validation: [
      { task: 'Run validation queries', status: 'pending' },
      { task: 'Compare record counts', status: 'pending' },
      { task: 'Test application functionality', status: 'pending' }
    ],
    optimization: [
      { task: 'Review query performance', status: 'pending' },
      { task: 'Optimize indexes', status: 'pending' },
      { task: 'Configure alerts', status: 'pending' }
    ],
    cleanup: [
      { task: 'Remove temporary resources', status: 'pending' },
      { task: 'Update documentation', status: 'pending' },
      { task: 'Decommission old system', status: 'pending' }
    ]
  }
}
```

---

## SQL to MongoDB Migration

### Schema Transformation

```javascript
// SQL to MongoDB schema mapping
const schemaTransformations = {
  // 1. One-to-One: Embed or reference based on access patterns
  oneToOne: {
    sql: `
      users (id, name, email)
      user_profiles (id, user_id, bio, avatar, settings)
    `,
    mongodb: {
      // Option A: Embed (frequent together access)
      embedded: {
        users: {
          _id: ObjectId(),
          name: String,
          email: String,
          profile: {
            bio: String,
            avatar: String,
            settings: Object
          }
        }
      },
      // Option B: Reference (independent access, large profile)
      referenced: {
        users: { _id: ObjectId(), name: String, email: String },
        profiles: { _id: ObjectId(), userId: ObjectId(), bio: String }
      }
    }
  },
  
  // 2. One-to-Many: Embed array or reference
  oneToMany: {
    sql: `
      orders (id, user_id, total, status)
      order_items (id, order_id, product_id, quantity, price)
    `,
    mongodb: {
      // Embed items in order (bounded, always accessed together)
      orders: {
        _id: ObjectId(),
        userId: ObjectId(),
        total: Decimal128,
        status: String,
        items: [{
          productId: ObjectId(),
          quantity: Number,
          price: Decimal128
        }]
      }
    }
  },
  
  // 3. Many-to-Many: Array of references
  manyToMany: {
    sql: `
      students (id, name)
      courses (id, title)
      enrollments (student_id, course_id, enrolled_at)
    `,
    mongodb: {
      // Option A: Array in one side
      students: {
        _id: ObjectId(),
        name: String,
        enrollments: [{
          courseId: ObjectId(),
          enrolledAt: Date
        }]
      },
      // Option B: Separate collection (if relationship has many attributes)
      enrollments: {
        _id: ObjectId(),
        studentId: ObjectId(),
        courseId: ObjectId(),
        enrolledAt: Date,
        grade: String,
        status: String
      }
    }
  }
}
```

### SQL Migration Tool

```javascript
// SQL to MongoDB migration helper
class SQLToMongoMigrator {
  constructor(sqlConnection, mongoClient, config) {
    this.sql = sqlConnection
    this.mongo = mongoClient.db(config.targetDb)
    this.config = config
    this.mappings = config.mappings || {}
    this.transforms = config.transforms || {}
  }
  
  async migrate() {
    const report = {
      startTime: new Date(),
      tables: [],
      totalRows: 0,
      errors: []
    }
    
    for (const table of this.config.tables) {
      console.log(`Migrating table: ${table.name}`)
      
      const tableReport = await this.migrateTable(table)
      report.tables.push(tableReport)
      report.totalRows += tableReport.rowCount
    }
    
    report.endTime = new Date()
    report.duration = report.endTime - report.startTime
    
    return report
  }
  
  async migrateTable(tableConfig) {
    const {
      name: tableName,
      targetCollection,
      query = `SELECT * FROM ${tableName}`,
      batchSize = 10000,
      transform
    } = tableConfig
    
    const collection = this.mongo.collection(targetCollection || tableName)
    const report = { name: tableName, rowCount: 0, errors: [] }
    
    let offset = 0
    let hasMore = true
    
    while (hasMore) {
      try {
        // Fetch batch from SQL
        const rows = await this.sql.query(
          `${query} LIMIT ${batchSize} OFFSET ${offset}`
        )
        
        if (rows.length === 0) {
          hasMore = false
          continue
        }
        
        // Transform rows
        const documents = rows.map(row => {
          let doc = this.transformRow(row, tableConfig)
          
          if (transform) {
            doc = transform(doc)
          }
          
          return doc
        })
        
        // Insert batch
        await collection.insertMany(documents, { ordered: false })
        
        report.rowCount += documents.length
        offset += batchSize
        
        console.log(`  Migrated ${report.rowCount} rows...`)
        
      } catch (error) {
        report.errors.push({
          offset,
          error: error.message
        })
        
        // Continue with next batch
        offset += batchSize
      }
    }
    
    return report
  }
  
  transformRow(row, tableConfig) {
    const doc = {}
    const fieldMappings = tableConfig.fieldMappings || {}
    
    for (const [sqlField, value] of Object.entries(row)) {
      const mapping = fieldMappings[sqlField]
      
      if (mapping === false) {
        // Skip field
        continue
      }
      
      const mongoField = mapping?.field || this.toMongoFieldName(sqlField)
      let mongoValue = value
      
      // Type conversions
      if (mapping?.type) {
        mongoValue = this.convertType(value, mapping.type)
      } else {
        mongoValue = this.autoConvertType(value, sqlField)
      }
      
      // Handle nested fields
      if (mongoField.includes('.')) {
        this.setNestedValue(doc, mongoField, mongoValue)
      } else {
        doc[mongoField] = mongoValue
      }
    }
    
    // Handle _id
    if (tableConfig.idField && doc[tableConfig.idField]) {
      doc._id = doc[tableConfig.idField]
      if (tableConfig.idField !== '_id') {
        delete doc[tableConfig.idField]
      }
    }
    
    return doc
  }
  
  toMongoFieldName(sqlField) {
    // Convert snake_case to camelCase
    return sqlField.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
  }
  
  convertType(value, type) {
    if (value === null) return null
    
    switch (type) {
      case 'objectId':
        return new ObjectId(value)
      case 'date':
        return new Date(value)
      case 'decimal':
        return NumberDecimal(value.toString())
      case 'int':
        return parseInt(value)
      case 'float':
        return parseFloat(value)
      case 'boolean':
        return Boolean(value)
      case 'json':
        return typeof value === 'string' ? JSON.parse(value) : value
      default:
        return value
    }
  }
  
  autoConvertType(value, fieldName) {
    if (value === null) return null
    
    // Auto-detect dates
    if (fieldName.endsWith('_at') || fieldName.endsWith('_date')) {
      return new Date(value)
    }
    
    // Auto-detect IDs
    if (fieldName === 'id' || fieldName.endsWith('_id')) {
      // Keep as-is for now, can be converted to ObjectId if needed
      return value
    }
    
    return value
  }
  
  setNestedValue(obj, path, value) {
    const parts = path.split('.')
    let current = obj
    
    for (let i = 0; i < parts.length - 1; i++) {
      if (!current[parts[i]]) {
        current[parts[i]] = {}
      }
      current = current[parts[i]]
    }
    
    current[parts[parts.length - 1]] = value
  }
}

// Usage example
const migrationConfig = {
  targetDb: 'ecommerce',
  tables: [
    {
      name: 'users',
      targetCollection: 'users',
      idField: 'id',
      fieldMappings: {
        'id': { field: '_id', type: 'objectId' },
        'created_at': { field: 'createdAt', type: 'date' },
        'updated_at': { field: 'updatedAt', type: 'date' },
        'password_hash': false  // Skip sensitive field
      }
    },
    {
      name: 'orders',
      targetCollection: 'orders',
      query: `
        SELECT o.*, 
          JSON_ARRAYAGG(
            JSON_OBJECT('productId', oi.product_id, 'quantity', oi.quantity, 'price', oi.price)
          ) as items
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.id
      `,
      fieldMappings: {
        'user_id': { field: 'userId', type: 'objectId' },
        'items': { type: 'json' }
      },
      transform: (doc) => {
        // Parse items if string
        if (typeof doc.items === 'string') {
          doc.items = JSON.parse(doc.items)
        }
        return doc
      }
    }
  ]
}

const migrator = new SQLToMongoMigrator(sqlConn, mongoClient, migrationConfig)
const report = await migrator.migrate()
```

### Incremental Sync with CDC

```javascript
// Change Data Capture for continuous sync
class CDCSyncService {
  constructor(sqlConnection, mongoClient, config) {
    this.sql = sqlConnection
    this.mongo = mongoClient.db(config.targetDb)
    this.config = config
    this.lastPosition = null
  }
  
  // For MySQL binlog
  async startMySQLSync() {
    const binlogClient = new MySQLBinlog({
      host: this.config.mysql.host,
      user: this.config.mysql.user,
      password: this.config.mysql.password
    })
    
    binlogClient.on('tablemap', (event) => {
      // Store table metadata
    })
    
    binlogClient.on('writerows', async (event) => {
      await this.handleInsert(event)
    })
    
    binlogClient.on('updaterows', async (event) => {
      await this.handleUpdate(event)
    })
    
    binlogClient.on('deleterows', async (event) => {
      await this.handleDelete(event)
    })
    
    binlogClient.start({
      startAtEnd: true,
      includeSchema: this.config.schemas,
      includeEvents: ['tablemap', 'writerows', 'updaterows', 'deleterows']
    })
  }
  
  async handleInsert(event) {
    const { table, rows } = event
    const mapping = this.config.tables.find(t => t.name === table)
    
    if (!mapping) return
    
    const collection = this.mongo.collection(mapping.targetCollection)
    const documents = rows.map(row => this.transformRow(row, mapping))
    
    try {
      await collection.insertMany(documents, { ordered: false })
    } catch (error) {
      if (error.code !== 11000) {  // Ignore duplicate key errors
        console.error(`Insert error for ${table}:`, error)
      }
    }
  }
  
  async handleUpdate(event) {
    const { table, rows } = event
    const mapping = this.config.tables.find(t => t.name === table)
    
    if (!mapping) return
    
    const collection = this.mongo.collection(mapping.targetCollection)
    
    for (const { before, after } of rows) {
      const id = after[mapping.idField] || after.id
      const document = this.transformRow(after, mapping)
      delete document._id
      
      await collection.updateOne(
        { _id: id },
        { $set: document }
      )
    }
  }
  
  async handleDelete(event) {
    const { table, rows } = event
    const mapping = this.config.tables.find(t => t.name === table)
    
    if (!mapping) return
    
    const collection = this.mongo.collection(mapping.targetCollection)
    const ids = rows.map(row => row[mapping.idField] || row.id)
    
    await collection.deleteMany({ _id: { $in: ids } })
  }
  
  transformRow(row, mapping) {
    // Reuse transformation logic from SQLToMongoMigrator
    // ...
  }
}
```

---

## MongoDB Version Upgrades

### Upgrade Path Planning

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Version Upgrade Path                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Current: 4.4                                                       │
│      ↓                                                              │
│  Step 1: Upgrade to 5.0                                             │
│  • Set feature compatibility to 4.4                                 │
│  • Upgrade mongod binaries                                          │
│  • Test application compatibility                                   │
│  • Set feature compatibility to 5.0                                 │
│      ↓                                                              │
│  Step 2: Upgrade to 6.0                                             │
│  • Set feature compatibility to 5.0                                 │
│  • Upgrade mongod binaries                                          │
│  • Test application compatibility                                   │
│  • Set feature compatibility to 6.0                                 │
│      ↓                                                              │
│  Step 3: Upgrade to 7.0                                             │
│  • Set feature compatibility to 6.0                                 │
│  • Upgrade mongod binaries                                          │
│  • Test application compatibility                                   │
│  • Set feature compatibility to 7.0                                 │
│                                                                     │
│  Note: Cannot skip major versions!                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Replica Set Upgrade Procedure

```javascript
// Replica set rolling upgrade script
class ReplicaSetUpgradeService {
  constructor(client) {
    this.client = client
    this.admin = client.db('admin')
  }
  
  async preUpgradeChecks(targetVersion) {
    const checks = []
    
    // Check current version
    const buildInfo = await this.admin.command({ buildInfo: 1 })
    checks.push({
      check: 'currentVersion',
      value: buildInfo.version,
      pass: true
    })
    
    // Check feature compatibility version
    const fcv = await this.admin.command({ getParameter: 1, featureCompatibilityVersion: 1 })
    checks.push({
      check: 'featureCompatibilityVersion',
      value: fcv.featureCompatibilityVersion.version,
      pass: true
    })
    
    // Check replica set health
    const rsStatus = await this.admin.command({ replSetGetStatus: 1 })
    const unhealthyMembers = rsStatus.members.filter(m => 
      m.health !== 1 || !['PRIMARY', 'SECONDARY'].includes(m.stateStr)
    )
    checks.push({
      check: 'replicaSetHealth',
      value: `${rsStatus.members.length - unhealthyMembers.length}/${rsStatus.members.length} healthy`,
      pass: unhealthyMembers.length === 0
    })
    
    // Check for deprecated features
    const deprecatedFeatures = await this.checkDeprecatedFeatures(targetVersion)
    checks.push({
      check: 'deprecatedFeatures',
      value: deprecatedFeatures.length === 0 ? 'None' : deprecatedFeatures.join(', '),
      pass: deprecatedFeatures.length === 0
    })
    
    // Check driver compatibility
    checks.push({
      check: 'driverCompatibility',
      value: 'Manual verification required',
      pass: null
    })
    
    return checks
  }
  
  async checkDeprecatedFeatures(targetVersion) {
    const deprecated = []
    
    // Check for deprecated index types
    const collections = await this.client.db().listCollections().toArray()
    for (const coll of collections) {
      const indexes = await this.client.db().collection(coll.name).indexes()
      
      for (const index of indexes) {
        // Check for deprecated index options
        if (index.background !== undefined) {
          deprecated.push(`${coll.name}: background index option (deprecated in 4.2+)`)
        }
      }
    }
    
    // Check for deprecated query operators
    // Would need to analyze query patterns
    
    return deprecated
  }
  
  async setFeatureCompatibility(version) {
    return await this.admin.command({
      setFeatureCompatibilityVersion: version,
      confirm: true
    })
  }
  
  async generateUpgradePlan() {
    const rsStatus = await this.admin.command({ replSetGetStatus: 1 })
    const members = rsStatus.members
    
    // Order: secondaries first, then primary
    const secondaries = members.filter(m => m.stateStr === 'SECONDARY')
    const primary = members.find(m => m.stateStr === 'PRIMARY')
    
    const plan = []
    
    // Secondaries
    for (const secondary of secondaries) {
      plan.push({
        step: plan.length + 1,
        host: secondary.name,
        role: 'SECONDARY',
        actions: [
          'Stop mongod process',
          'Backup data directory (optional but recommended)',
          'Install new MongoDB version',
          'Start mongod with same configuration',
          'Wait for member to become SECONDARY',
          'Verify replication is caught up'
        ]
      })
    }
    
    // Primary (will require step-down)
    plan.push({
      step: plan.length + 1,
      host: primary.name,
      role: 'PRIMARY',
      actions: [
        'Run rs.stepDown() to elect new primary',
        'Wait for new primary election',
        'Stop mongod process',
        'Install new MongoDB version',
        'Start mongod with same configuration',
        'Verify member rejoins as SECONDARY',
        'Optionally rs.stepUp() to restore as primary'
      ]
    })
    
    // Final step: Update feature compatibility
    plan.push({
      step: plan.length + 1,
      host: 'any',
      role: 'CLUSTER',
      actions: [
        'Connect to primary',
        'Run: db.adminCommand({ setFeatureCompatibilityVersion: "X.X" })',
        'Verify all members report new FCV'
      ]
    })
    
    return plan
  }
}

// Usage
const upgradeService = new ReplicaSetUpgradeService(client)

// Pre-upgrade checks
const checks = await upgradeService.preUpgradeChecks('7.0')
console.log('Pre-upgrade checks:', checks)

// Generate plan
const plan = await upgradeService.generateUpgradePlan()
console.log('Upgrade plan:', JSON.stringify(plan, null, 2))
```

---

## Cloud Migration

### On-Premise to Atlas Migration

```javascript
// Atlas Live Migration Service
class AtlasMigrationService {
  constructor(atlasApi, sourceCluster) {
    this.atlas = atlasApi
    this.sourceCluster = sourceCluster
  }
  
  async initiateLiveMigration(projectId, config) {
    const migrationConfig = {
      // Source cluster details
      source: {
        clusterName: config.sourceClusterName,
        groupId: config.sourceProjectId,
        
        // For non-Atlas sources
        connectionString: config.sourceConnectionString,
        ssl: true,
        caCertificatePath: config.caCertPath
      },
      
      // Target Atlas cluster
      destination: {
        clusterName: config.targetClusterName,
        groupId: projectId
      },
      
      // Migration options
      dropDestinationData: false,
      migrationHosts: config.migrationHosts || []
    }
    
    // Start live migration
    const result = await this.atlas.request(
      'POST',
      `/groups/${projectId}/liveMigrations`,
      migrationConfig
    )
    
    return result
  }
  
  async checkMigrationStatus(projectId, migrationId) {
    return await this.atlas.request(
      'GET',
      `/groups/${projectId}/liveMigrations/${migrationId}`
    )
  }
  
  async performCutover(projectId, migrationId) {
    // Initiate cutover when lag is acceptable
    return await this.atlas.request(
      'PUT',
      `/groups/${projectId}/liveMigrations/${migrationId}/cutover`
    )
  }
}

// Migration monitoring
class MigrationMonitor {
  constructor(atlasApi, projectId, migrationId) {
    this.atlas = atlasApi
    this.projectId = projectId
    this.migrationId = migrationId
    this.metrics = []
  }
  
  async startMonitoring(intervalMs = 30000) {
    this.intervalId = setInterval(async () => {
      const status = await this.atlas.request(
        'GET',
        `/groups/${this.projectId}/liveMigrations/${this.migrationId}`
      )
      
      const metric = {
        timestamp: new Date(),
        status: status.status,
        lagSeconds: status.lagTimeSeconds,
        bytesTransferred: status.copiedBytes,
        percentComplete: status.percentComplete
      }
      
      this.metrics.push(metric)
      this.logStatus(metric)
      
      // Check for completion or error
      if (['COMPLETE', 'FAILED', 'CANCELLED'].includes(status.status)) {
        this.stopMonitoring()
        this.generateReport()
      }
    }, intervalMs)
  }
  
  stopMonitoring() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
    }
  }
  
  logStatus(metric) {
    console.log(`[${metric.timestamp.toISOString()}] ` +
      `Status: ${metric.status}, ` +
      `Lag: ${metric.lagSeconds}s, ` +
      `Progress: ${metric.percentComplete}%`)
  }
  
  generateReport() {
    console.log('\n=== Migration Report ===')
    console.log(`Total duration: ${this.calculateDuration()}`)
    console.log(`Final status: ${this.metrics[this.metrics.length - 1].status}`)
    console.log(`Data transferred: ${this.formatBytes(this.metrics[this.metrics.length - 1].bytesTransferred)}`)
    console.log(`Average lag: ${this.calculateAverageLag()}s`)
  }
  
  calculateDuration() {
    const start = this.metrics[0].timestamp
    const end = this.metrics[this.metrics.length - 1].timestamp
    const durationMs = end - start
    
    const hours = Math.floor(durationMs / 3600000)
    const minutes = Math.floor((durationMs % 3600000) / 60000)
    
    return `${hours}h ${minutes}m`
  }
  
  calculateAverageLag() {
    const totalLag = this.metrics.reduce((sum, m) => sum + (m.lagSeconds || 0), 0)
    return (totalLag / this.metrics.length).toFixed(1)
  }
  
  formatBytes(bytes) {
    const units = ['B', 'KB', 'MB', 'GB', 'TB']
    let unitIndex = 0
    let size = bytes
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    
    return `${size.toFixed(2)} ${units[unitIndex]}`
  }
}
```

### mongomirror Tool Usage

```bash
# mongomirror for Atlas migration

# Basic usage
mongomirror \
  --host "source-rs/source1:27017,source2:27017,source3:27017" \
  --destination "atlas-cluster-shard-00-00.mongodb.net:27017,atlas-cluster-shard-00-01.mongodb.net:27017,atlas-cluster-shard-00-02.mongodb.net:27017" \
  --destinationUsername "atlas-user" \
  --destinationPassword "password" \
  --ssl \
  --sslCAFile /path/to/ca.pem

# With specific database filter
mongomirror \
  --host "source-rs/source1:27017,source2:27017" \
  --destination "atlas-cluster.mongodb.net:27017" \
  --destinationUsername "admin" \
  --destinationPassword "password" \
  --includeNamespace "mydb.*" \
  --drop \
  --ssl

# Tail oplog only (for already synced clusters)
mongomirror \
  --host "source-rs/source1:27017,source2:27017" \
  --destination "atlas-cluster.mongodb.net:27017" \
  --destinationUsername "admin" \
  --destinationPassword "password" \
  --oplogOnly \
  --ssl
```

---

## Data Center Migration

### Cross-Region Replica Set Extension

```javascript
// Extend replica set to new data center
class CrossRegionMigration {
  constructor(client) {
    this.client = client
    this.admin = client.db('admin')
  }
  
  async addCrossRegionMember(newMemberConfig) {
    // Get current config
    const config = await this.admin.command({ replSetGetConfig: 1 })
    const rsConfig = config.config
    
    // Increment version
    rsConfig.version++
    
    // Add new member
    const newMemberId = Math.max(...rsConfig.members.map(m => m._id)) + 1
    
    rsConfig.members.push({
      _id: newMemberId,
      host: newMemberConfig.host,
      priority: newMemberConfig.priority || 0,  // Start with 0 for sync
      votes: newMemberConfig.votes || 0,
      tags: newMemberConfig.tags || {}
    })
    
    // Apply new config
    await this.admin.command({ replSetReconfig: rsConfig })
    
    return { memberId: newMemberId, status: 'added' }
  }
  
  async monitorSyncProgress(memberHost) {
    const status = await this.admin.command({ replSetGetStatus: 1 })
    const member = status.members.find(m => m.name === memberHost)
    
    if (!member) {
      throw new Error(`Member ${memberHost} not found`)
    }
    
    const primary = status.members.find(m => m.stateStr === 'PRIMARY')
    
    return {
      state: member.stateStr,
      syncSourceHost: member.syncSourceHost,
      optimeDate: member.optimeDate,
      lagSeconds: member.optimeDate && primary.optimeDate
        ? (primary.optimeDate - member.optimeDate) / 1000
        : null,
      health: member.health
    }
  }
  
  async promoteNewRegion(memberHost, newPriority = 1, newVotes = 1) {
    const config = await this.admin.command({ replSetGetConfig: 1 })
    const rsConfig = config.config
    
    const member = rsConfig.members.find(m => m.host === memberHost)
    
    if (!member) {
      throw new Error(`Member ${memberHost} not found in config`)
    }
    
    member.priority = newPriority
    member.votes = newVotes
    
    rsConfig.version++
    
    await this.admin.command({ replSetReconfig: rsConfig })
    
    return { status: 'promoted', priority: newPriority, votes: newVotes }
  }
  
  async performRegionFailover(targetRegion) {
    // Get members in target region
    const status = await this.admin.command({ replSetGetStatus: 1 })
    const config = await this.admin.command({ replSetGetConfig: 1 })
    
    const targetMembers = config.config.members.filter(m => 
      m.tags?.region === targetRegion
    )
    
    if (targetMembers.length === 0) {
      throw new Error(`No members found in region ${targetRegion}`)
    }
    
    // Adjust priorities to favor target region
    const newConfig = { ...config.config }
    newConfig.version++
    
    for (const member of newConfig.members) {
      if (member.tags?.region === targetRegion) {
        member.priority = 10  // High priority
      } else {
        member.priority = 1   // Lower priority
      }
    }
    
    // Apply config and step down current primary
    await this.admin.command({ replSetReconfig: newConfig })
    
    // Step down to force election
    try {
      await this.admin.command({ replSetStepDown: 60 })
    } catch (error) {
      // Expected: connection drops during step down
    }
    
    return { status: 'failover_initiated', targetRegion }
  }
}
```

### Zero-Downtime Data Center Migration

```javascript
// Complete data center migration workflow
class DataCenterMigration {
  constructor(sourceClient, config) {
    this.sourceClient = sourceClient
    this.config = config
    this.migrationState = {
      phase: 'init',
      startTime: null,
      completedSteps: []
    }
  }
  
  async execute() {
    this.migrationState.startTime = new Date()
    
    try {
      // Phase 1: Add new DC members as hidden
      await this.phase1_addNewMembers()
      
      // Phase 2: Wait for initial sync
      await this.phase2_waitForSync()
      
      // Phase 3: Promote new members
      await this.phase3_promoteMembers()
      
      // Phase 4: Update application configs
      await this.phase4_updateApplications()
      
      // Phase 5: Demote old members
      await this.phase5_demoteOldMembers()
      
      // Phase 6: Remove old members
      await this.phase6_removeOldMembers()
      
      // Phase 7: Cleanup
      await this.phase7_cleanup()
      
      return this.generateReport()
      
    } catch (error) {
      this.migrationState.error = error.message
      throw error
    }
  }
  
  async phase1_addNewMembers() {
    this.migrationState.phase = 'adding_members'
    console.log('Phase 1: Adding new data center members...')
    
    const migration = new CrossRegionMigration(this.sourceClient)
    
    for (const member of this.config.newMembers) {
      await migration.addCrossRegionMember({
        host: member.host,
        priority: 0,
        votes: 0,
        tags: { region: this.config.newRegion, dc: this.config.newDataCenter }
      })
      
      console.log(`  Added member: ${member.host}`)
    }
    
    this.migrationState.completedSteps.push('add_members')
  }
  
  async phase2_waitForSync() {
    this.migrationState.phase = 'syncing'
    console.log('Phase 2: Waiting for initial sync...')
    
    const migration = new CrossRegionMigration(this.sourceClient)
    
    for (const member of this.config.newMembers) {
      let synced = false
      
      while (!synced) {
        const progress = await migration.monitorSyncProgress(member.host)
        
        console.log(`  ${member.host}: ${progress.state}, lag: ${progress.lagSeconds}s`)
        
        if (progress.state === 'SECONDARY' && progress.lagSeconds < 10) {
          synced = true
        } else {
          await this.sleep(10000)  // Wait 10 seconds
        }
      }
    }
    
    this.migrationState.completedSteps.push('sync_complete')
  }
  
  async phase3_promoteMembers() {
    this.migrationState.phase = 'promoting'
    console.log('Phase 3: Promoting new members...')
    
    const migration = new CrossRegionMigration(this.sourceClient)
    
    for (const member of this.config.newMembers) {
      await migration.promoteNewRegion(member.host, member.priority || 1, 1)
      console.log(`  Promoted: ${member.host}`)
    }
    
    this.migrationState.completedSteps.push('promote_members')
  }
  
  async phase4_updateApplications() {
    this.migrationState.phase = 'updating_apps'
    console.log('Phase 4: Update application connection strings')
    console.log('  Manual step: Update application configurations')
    console.log('  New members should now be included in connection strings')
    
    // This would typically involve:
    // - Updating environment variables
    // - Rotating secrets
    // - Redeploying applications
    
    this.migrationState.completedSteps.push('update_applications')
  }
  
  async phase5_demoteOldMembers() {
    this.migrationState.phase = 'demoting'
    console.log('Phase 5: Demoting old data center members...')
    
    const admin = this.sourceClient.db('admin')
    const config = await admin.command({ replSetGetConfig: 1 })
    const rsConfig = config.config
    
    for (const member of rsConfig.members) {
      if (member.tags?.dc === this.config.oldDataCenter) {
        member.priority = 0
        console.log(`  Demoting: ${member.host}`)
      }
    }
    
    rsConfig.version++
    await admin.command({ replSetReconfig: rsConfig })
    
    this.migrationState.completedSteps.push('demote_old_members')
  }
  
  async phase6_removeOldMembers() {
    this.migrationState.phase = 'removing'
    console.log('Phase 6: Removing old data center members...')
    
    const admin = this.sourceClient.db('admin')
    
    for (const member of this.config.oldMembers) {
      const config = await admin.command({ replSetGetConfig: 1 })
      const rsConfig = config.config
      
      rsConfig.members = rsConfig.members.filter(m => m.host !== member.host)
      rsConfig.version++
      
      await admin.command({ replSetReconfig: rsConfig })
      console.log(`  Removed: ${member.host}`)
      
      await this.sleep(5000)  // Allow election if needed
    }
    
    this.migrationState.completedSteps.push('remove_old_members')
  }
  
  async phase7_cleanup() {
    this.migrationState.phase = 'cleanup'
    console.log('Phase 7: Cleanup...')
    
    // Verify final state
    const admin = this.sourceClient.db('admin')
    const status = await admin.command({ replSetGetStatus: 1 })
    
    console.log('  Final replica set state:')
    for (const member of status.members) {
      console.log(`    ${member.name}: ${member.stateStr}`)
    }
    
    this.migrationState.completedSteps.push('cleanup')
    this.migrationState.phase = 'complete'
  }
  
  generateReport() {
    return {
      status: 'complete',
      startTime: this.migrationState.startTime,
      endTime: new Date(),
      duration: new Date() - this.migrationState.startTime,
      completedSteps: this.migrationState.completedSteps,
      sourceDataCenter: this.config.oldDataCenter,
      targetDataCenter: this.config.newDataCenter
    }
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// Usage
const migrationConfig = {
  oldDataCenter: 'dc-east',
  newDataCenter: 'dc-west',
  oldRegion: 'us-east-1',
  newRegion: 'us-west-2',
  oldMembers: [
    { host: 'mongo-east-1:27017' },
    { host: 'mongo-east-2:27017' },
    { host: 'mongo-east-3:27017' }
  ],
  newMembers: [
    { host: 'mongo-west-1:27017', priority: 2 },
    { host: 'mongo-west-2:27017', priority: 1 },
    { host: 'mongo-west-3:27017', priority: 1 }
  ]
}

const migration = new DataCenterMigration(client, migrationConfig)
const report = await migration.execute()
```

---

## Schema Evolution

### Backward-Compatible Schema Changes

```javascript
// Schema version management
class SchemaVersionManager {
  constructor(db) {
    this.db = db
    this.migrations = db.collection('schema_migrations')
  }
  
  async runMigrations(migrations) {
    // Sort by version
    const sorted = [...migrations].sort((a, b) => a.version - b.version)
    
    for (const migration of sorted) {
      const executed = await this.migrations.findOne({ version: migration.version })
      
      if (!executed) {
        console.log(`Running migration ${migration.version}: ${migration.name}`)
        
        try {
          await migration.up(this.db)
          
          await this.migrations.insertOne({
            version: migration.version,
            name: migration.name,
            executedAt: new Date()
          })
          
          console.log(`  Migration ${migration.version} completed`)
          
        } catch (error) {
          console.error(`  Migration ${migration.version} failed:`, error)
          throw error
        }
      }
    }
  }
  
  async rollback(targetVersion) {
    const executed = await this.migrations
      .find({ version: { $gt: targetVersion } })
      .sort({ version: -1 })
      .toArray()
    
    for (const migration of executed) {
      const migrationDef = this.getMigrationDefinition(migration.version)
      
      if (migrationDef && migrationDef.down) {
        console.log(`Rolling back migration ${migration.version}`)
        
        await migrationDef.down(this.db)
        
        await this.migrations.deleteOne({ version: migration.version })
      }
    }
  }
}

// Example migrations
const migrations = [
  {
    version: 1,
    name: 'add_user_email_index',
    up: async (db) => {
      await db.collection('users').createIndex(
        { email: 1 },
        { unique: true, background: true }
      )
    },
    down: async (db) => {
      await db.collection('users').dropIndex('email_1')
    }
  },
  
  {
    version: 2,
    name: 'rename_user_name_to_fullName',
    up: async (db) => {
      // Add new field with value from old field
      await db.collection('users').updateMany(
        { name: { $exists: true }, fullName: { $exists: false } },
        [{ $set: { fullName: '$name' } }]
      )
      
      // Don't remove old field yet for backward compatibility
    },
    down: async (db) => {
      await db.collection('users').updateMany(
        { fullName: { $exists: true } },
        { $unset: { fullName: '' } }
      )
    }
  },
  
  {
    version: 3,
    name: 'remove_deprecated_name_field',
    up: async (db) => {
      // Only run after applications are updated
      await db.collection('users').updateMany(
        { name: { $exists: true } },
        { $unset: { name: '' } }
      )
    },
    down: async (db) => {
      // Restore from fullName
      await db.collection('users').updateMany(
        { fullName: { $exists: true }, name: { $exists: false } },
        [{ $set: { name: '$fullName' } }]
      )
    }
  },
  
  {
    version: 4,
    name: 'add_address_subdocument',
    up: async (db) => {
      // Restructure flat address fields into subdocument
      await db.collection('users').updateMany(
        { street: { $exists: true }, address: { $exists: false } },
        [{
          $set: {
            address: {
              street: '$street',
              city: '$city',
              state: '$state',
              zip: '$zip',
              country: '$country'
            }
          }
        }]
      )
    },
    down: async (db) => {
      // Flatten back
      await db.collection('users').updateMany(
        { address: { $exists: true } },
        [{
          $set: {
            street: '$address.street',
            city: '$address.city',
            state: '$address.state',
            zip: '$address.zip',
            country: '$address.country'
          },
          $unset: { address: '' }
        }]
      )
    }
  }
]
```

### Document Version Pattern

```javascript
// Versioned documents for schema evolution
class VersionedDocumentService {
  constructor(db, collectionName) {
    this.collection = db.collection(collectionName)
    this.currentVersion = 3
    this.upgraders = new Map()
    
    // Register upgraders
    this.registerUpgrader(1, 2, this.upgradeV1toV2.bind(this))
    this.registerUpgrader(2, 3, this.upgradeV2toV3.bind(this))
  }
  
  registerUpgrader(fromVersion, toVersion, upgraderFn) {
    this.upgraders.set(`${fromVersion}->${toVersion}`, upgraderFn)
  }
  
  async findOne(filter) {
    const doc = await this.collection.findOne(filter)
    
    if (!doc) return null
    
    // Upgrade document to current version
    return await this.upgradeDocument(doc)
  }
  
  async find(filter, options) {
    const docs = await this.collection.find(filter, options).toArray()
    
    // Upgrade all documents
    return await Promise.all(docs.map(doc => this.upgradeDocument(doc)))
  }
  
  async upgradeDocument(doc) {
    let currentDoc = doc
    let docVersion = doc._schemaVersion || 1
    
    while (docVersion < this.currentVersion) {
      const nextVersion = docVersion + 1
      const upgrader = this.upgraders.get(`${docVersion}->${nextVersion}`)
      
      if (upgrader) {
        currentDoc = await upgrader(currentDoc)
        docVersion = nextVersion
      } else {
        throw new Error(`No upgrader found for ${docVersion} -> ${nextVersion}`)
      }
    }
    
    currentDoc._schemaVersion = this.currentVersion
    
    // Optionally persist upgraded document
    // await this.collection.replaceOne({ _id: doc._id }, currentDoc)
    
    return currentDoc
  }
  
  async insertOne(doc) {
    const versionedDoc = {
      ...doc,
      _schemaVersion: this.currentVersion
    }
    
    return await this.collection.insertOne(versionedDoc)
  }
  
  // V1 -> V2: Add createdAt, updatedAt timestamps
  async upgradeV1toV2(doc) {
    return {
      ...doc,
      createdAt: doc.createdAt || doc._id.getTimestamp(),
      updatedAt: doc.updatedAt || new Date(),
      _schemaVersion: 2
    }
  }
  
  // V2 -> V3: Restructure nested fields
  async upgradeV2toV3(doc) {
    const upgraded = { ...doc }
    
    // Example: Move status fields into status subdocument
    if (doc.isActive !== undefined || doc.isVerified !== undefined) {
      upgraded.status = {
        active: doc.isActive ?? true,
        verified: doc.isVerified ?? false,
        verifiedAt: doc.verifiedAt || null
      }
      
      delete upgraded.isActive
      delete upgraded.isVerified
      delete upgraded.verifiedAt
    }
    
    upgraded._schemaVersion = 3
    return upgraded
  }
  
  // Batch upgrade all documents
  async upgradeAllDocuments(batchSize = 1000) {
    let upgraded = 0
    let processed = 0
    
    const cursor = this.collection.find({
      $or: [
        { _schemaVersion: { $lt: this.currentVersion } },
        { _schemaVersion: { $exists: false } }
      ]
    }).batchSize(batchSize)
    
    const bulkOps = []
    
    while (await cursor.hasNext()) {
      const doc = await cursor.next()
      const upgradedDoc = await this.upgradeDocument(doc)
      
      bulkOps.push({
        replaceOne: {
          filter: { _id: doc._id },
          replacement: upgradedDoc
        }
      })
      
      processed++
      
      if (bulkOps.length >= batchSize) {
        const result = await this.collection.bulkWrite(bulkOps)
        upgraded += result.modifiedCount
        bulkOps.length = 0
        
        console.log(`Upgraded ${upgraded} documents (${processed} processed)`)
      }
    }
    
    if (bulkOps.length > 0) {
      const result = await this.collection.bulkWrite(bulkOps)
      upgraded += result.modifiedCount
    }
    
    return { upgraded, processed }
  }
}
```

---

## Migration Tools and Automation

### Automated Migration Pipeline

```javascript
// Complete migration automation
class MigrationPipeline {
  constructor(config) {
    this.config = config
    this.state = {
      phase: 'init',
      steps: [],
      errors: []
    }
  }
  
  async execute() {
    const pipeline = [
      this.validatePrerequisites.bind(this),
      this.createBackup.bind(this),
      this.runPreMigrationTests.bind(this),
      this.performMigration.bind(this),
      this.validateMigration.bind(this),
      this.runPostMigrationTests.bind(this),
      this.switchTraffic.bind(this),
      this.cleanup.bind(this)
    ]
    
    for (const step of pipeline) {
      try {
        const result = await step()
        this.state.steps.push({
          name: step.name,
          status: 'success',
          result,
          timestamp: new Date()
        })
      } catch (error) {
        this.state.errors.push({
          step: step.name,
          error: error.message,
          timestamp: new Date()
        })
        
        // Attempt rollback
        await this.rollback()
        throw error
      }
    }
    
    return this.generateReport()
  }
  
  async validatePrerequisites() {
    const checks = []
    
    // Check source connectivity
    checks.push(await this.checkConnectivity(this.config.source))
    
    // Check target connectivity
    checks.push(await this.checkConnectivity(this.config.target))
    
    // Check disk space
    checks.push(await this.checkDiskSpace())
    
    // Check version compatibility
    checks.push(await this.checkVersionCompatibility())
    
    const failed = checks.filter(c => !c.pass)
    
    if (failed.length > 0) {
      throw new Error(`Prerequisites failed: ${failed.map(f => f.name).join(', ')}`)
    }
    
    return { checks }
  }
  
  async createBackup() {
    console.log('Creating backup...')
    
    // mongodump or snapshot
    const backupPath = `/backups/migration-${Date.now()}`
    
    // Execute backup command
    // This would call mongodump or trigger a cloud snapshot
    
    return { backupPath }
  }
  
  async runPreMigrationTests() {
    console.log('Running pre-migration tests...')
    
    const tests = this.config.tests?.preMigration || []
    const results = []
    
    for (const test of tests) {
      const result = await test.execute()
      results.push(result)
      
      if (!result.pass && test.required) {
        throw new Error(`Required pre-migration test failed: ${test.name}`)
      }
    }
    
    return { results }
  }
  
  async performMigration() {
    console.log('Performing migration...')
    
    // Execute migration based on strategy
    switch (this.config.strategy) {
      case 'mongomirror':
        return await this.runMongomirror()
      case 'mongodump':
        return await this.runMongodumpRestore()
      case 'application':
        return await this.runApplicationMigration()
      default:
        throw new Error(`Unknown migration strategy: ${this.config.strategy}`)
    }
  }
  
  async validateMigration() {
    console.log('Validating migration...')
    
    const validations = []
    
    // Count comparison
    for (const collection of this.config.collections) {
      const sourceCount = await this.getCount(this.config.source, collection)
      const targetCount = await this.getCount(this.config.target, collection)
      
      validations.push({
        type: 'count',
        collection,
        sourceCount,
        targetCount,
        match: sourceCount === targetCount
      })
    }
    
    // Sample document comparison
    for (const collection of this.config.collections) {
      const sampleMatch = await this.compareSamples(collection, 100)
      
      validations.push({
        type: 'sample',
        collection,
        samplesChecked: 100,
        matchRate: sampleMatch
      })
    }
    
    const failed = validations.filter(v => !v.match && v.matchRate < 1)
    
    if (failed.length > 0) {
      throw new Error(`Validation failed for: ${failed.map(f => f.collection).join(', ')}`)
    }
    
    return { validations }
  }
  
  async runPostMigrationTests() {
    console.log('Running post-migration tests...')
    
    const tests = this.config.tests?.postMigration || []
    const results = []
    
    for (const test of tests) {
      const result = await test.execute()
      results.push(result)
      
      if (!result.pass && test.required) {
        throw new Error(`Required post-migration test failed: ${test.name}`)
      }
    }
    
    return { results }
  }
  
  async switchTraffic() {
    console.log('Switching traffic...')
    
    // This would update DNS, load balancer, or application configs
    // Implementation depends on deployment setup
    
    return { status: 'traffic_switched' }
  }
  
  async cleanup() {
    console.log('Cleaning up...')
    
    // Remove temporary resources
    // Archive backup if successful
    
    return { status: 'cleanup_complete' }
  }
  
  async rollback() {
    console.log('Rolling back migration...')
    
    // Restore from backup
    // Revert traffic switch
    // Clean up target
    
    this.state.rolledBack = true
  }
  
  generateReport() {
    return {
      status: this.state.errors.length === 0 ? 'success' : 'failed',
      startTime: this.state.steps[0]?.timestamp,
      endTime: this.state.steps[this.state.steps.length - 1]?.timestamp,
      steps: this.state.steps,
      errors: this.state.errors,
      rolledBack: this.state.rolledBack || false
    }
  }
}

// Usage
const migrationConfig = {
  source: {
    uri: 'mongodb://source-cluster:27017',
    database: 'mydb'
  },
  target: {
    uri: 'mongodb+srv://atlas-cluster.mongodb.net',
    database: 'mydb'
  },
  strategy: 'mongomirror',
  collections: ['users', 'orders', 'products'],
  tests: {
    preMigration: [
      {
        name: 'check_source_indexes',
        required: true,
        execute: async () => ({ pass: true })
      }
    ],
    postMigration: [
      {
        name: 'verify_user_login',
        required: true,
        execute: async () => ({ pass: true })
      }
    ]
  }
}

const pipeline = new MigrationPipeline(migrationConfig)
const report = await pipeline.execute()
```

---

## Summary

### Migration Strategy Comparison

| Strategy | Downtime | Data Loss Risk | Complexity | Rollback |
|----------|----------|----------------|------------|----------|
| mongodump/restore | High | Low | Low | Easy |
| mongomirror | Low | Very Low | Medium | Medium |
| Live Migration | Zero | Very Low | High | Complex |
| Application Migration | Zero | Low | High | Easy |

### Key Migration Considerations

| Factor | Consideration |
|--------|---------------|
| Data Volume | Affects migration time and method |
| Downtime Tolerance | Determines strategy |
| Network Bandwidth | Affects sync speed |
| Consistency Requirements | Transaction support needs |
| Application Changes | Driver and query updates |
| Testing | Comprehensive validation |

### Migration Checklist Summary

```markdown
## Pre-Migration
- [ ] Assessment complete
- [ ] Schema design finalized
- [ ] Indexes planned
- [ ] Rollback plan documented
- [ ] Testing environment ready
- [ ] Backup verified

## During Migration
- [ ] Source data frozen or synced
- [ ] Data transfer monitored
- [ ] Incremental sync verified
- [ ] Application ready for cutover

## Post-Migration
- [ ] Data validation passed
- [ ] Performance verified
- [ ] Applications functional
- [ ] Monitoring active
- [ ] Old system decommissioned
- [ ] Documentation updated
```

---

## Practice Questions

1. What factors determine the choice of migration strategy?
2. How do you handle schema transformation from SQL to MongoDB?
3. What is the MongoDB version upgrade path and why can't you skip versions?
4. How does mongomirror work for Atlas migration?
5. What is the process for cross-region data center migration?
6. How do you implement backward-compatible schema changes?
7. What are the key validations after a migration?
8. How do you handle rollback in different migration scenarios?

---

## Congratulations!

You have completed the comprehensive MongoDB guide covering:

- **Fundamentals**: Document model, CRUD operations, data types
- **Querying**: Query operators, aggregation framework, text search
- **Indexing**: Index types, strategies, and optimization
- **Data Modeling**: Schema design patterns and relationships
- **Administration**: Replication, sharding, security
- **Performance**: Optimization, profiling, troubleshooting
- **Advanced Topics**: Transactions, change streams, time series
- **Application Development**: Drivers, error handling, migrations
- **MongoDB Atlas**: Cloud deployment, monitoring, security
- **Real-World Applications**: Patterns, case studies, migrations

---

[← Previous: Performance Case Studies](76-performance-case-studies.md) | [Back to Index →](README.md)
