# Chapter 70: Data Migration

## Table of Contents
- [Migration Strategy Overview](#migration-strategy-overview)
- [Schema Migration](#schema-migration)
- [Data Transformation](#data-transformation)
- [Migration Tools and Techniques](#migration-tools-and-techniques)
- [Zero-Downtime Migration](#zero-downtime-migration)
- [Migration Best Practices](#migration-best-practices)
- [Summary](#summary)

---

## Migration Strategy Overview

### Migration Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Data Migration Types                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   1. Schema Evolution                                               │
│   ┌─────────────┐      ┌─────────────┐                             │
│   │ Old Schema  │ ───► │ New Schema  │                             │
│   │ { name }    │      │ { firstName,│                             │
│   │             │      │   lastName }│                             │
│   └─────────────┘      └─────────────┘                             │
│                                                                     │
│   2. Cross-Database Migration                                       │
│   ┌─────────────┐      ┌─────────────┐                             │
│   │   MySQL     │ ───► │  MongoDB    │                             │
│   │ (Tables)    │      │(Collections)│                             │
│   └─────────────┘      └─────────────┘                             │
│                                                                     │
│   3. Infrastructure Migration                                       │
│   ┌─────────────┐      ┌─────────────┐                             │
│   │ Self-hosted │ ───► │   Atlas     │                             │
│   │  MongoDB    │      │  (Cloud)    │                             │
│   └─────────────┘      └─────────────┘                             │
│                                                                     │
│   4. Version Upgrade Migration                                      │
│   ┌─────────────┐      ┌─────────────┐                             │
│   │ MongoDB 4.x │ ───► │ MongoDB 7.x │                             │
│   └─────────────┘      └─────────────┘                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Migration Planning Checklist

| Phase | Tasks |
|-------|-------|
| Assessment | Analyze current schema, data volume, dependencies |
| Planning | Design target schema, estimate timeline, plan rollback |
| Development | Write migration scripts, create tests |
| Testing | Test in staging, validate data integrity |
| Execution | Run migration, monitor progress |
| Verification | Validate results, check application functionality |
| Cleanup | Remove temporary data, document changes |

---

## Schema Migration

### Basic Schema Migration Script

```javascript
// Migration framework
class MigrationRunner {
  constructor(db) {
    this.db = db
    this.migrationsCollection = db.collection('_migrations')
  }
  
  async run(migrations) {
    // Get completed migrations
    const completed = await this.migrationsCollection
      .find({})
      .project({ name: 1 })
      .toArray()
    const completedNames = new Set(completed.map(m => m.name))
    
    // Run pending migrations
    for (const migration of migrations) {
      if (completedNames.has(migration.name)) {
        console.log(`Skipping ${migration.name} (already applied)`)
        continue
      }
      
      console.log(`Running migration: ${migration.name}`)
      const startTime = Date.now()
      
      try {
        await migration.up(this.db)
        
        // Record migration
        await this.migrationsCollection.insertOne({
          name: migration.name,
          appliedAt: new Date(),
          durationMs: Date.now() - startTime
        })
        
        console.log(`Completed ${migration.name} in ${Date.now() - startTime}ms`)
      } catch (error) {
        console.error(`Failed ${migration.name}:`, error.message)
        throw error
      }
    }
  }
  
  async rollback(migrationName, migrations) {
    const migration = migrations.find(m => m.name === migrationName)
    
    if (!migration || !migration.down) {
      throw new Error(`Cannot rollback ${migrationName}`)
    }
    
    console.log(`Rolling back: ${migrationName}`)
    await migration.down(this.db)
    await this.migrationsCollection.deleteOne({ name: migrationName })
    console.log(`Rollback complete: ${migrationName}`)
  }
}

// Define migrations
const migrations = [
  {
    name: '001_add_user_status',
    up: async (db) => {
      // Add status field with default value
      await db.collection('users').updateMany(
        { status: { $exists: false } },
        { $set: { status: 'active' } }
      )
      
      // Create index
      await db.collection('users').createIndex({ status: 1 })
    },
    down: async (db) => {
      await db.collection('users').dropIndex({ status: 1 })
      await db.collection('users').updateMany(
        {},
        { $unset: { status: '' } }
      )
    }
  },
  
  {
    name: '002_split_name_field',
    up: async (db) => {
      // Transform name to firstName/lastName
      const cursor = db.collection('users').find({ name: { $exists: true } })
      
      const bulkOps = []
      for await (const doc of cursor) {
        const [firstName, ...rest] = (doc.name || '').split(' ')
        const lastName = rest.join(' ')
        
        bulkOps.push({
          updateOne: {
            filter: { _id: doc._id },
            update: {
              $set: { firstName, lastName },
              $unset: { name: '' }
            }
          }
        })
        
        if (bulkOps.length >= 1000) {
          await db.collection('users').bulkWrite(bulkOps)
          bulkOps.length = 0
        }
      }
      
      if (bulkOps.length > 0) {
        await db.collection('users').bulkWrite(bulkOps)
      }
    },
    down: async (db) => {
      // Merge firstName/lastName back to name
      await db.collection('users').updateMany(
        { firstName: { $exists: true } },
        [
          {
            $set: {
              name: {
                $trim: {
                  input: { $concat: ['$firstName', ' ', { $ifNull: ['$lastName', ''] }] }
                }
              }
            }
          },
          { $unset: ['firstName', 'lastName'] }
        ]
      )
    }
  },
  
  {
    name: '003_add_email_verification',
    up: async (db) => {
      await db.collection('users').updateMany(
        { emailVerified: { $exists: false } },
        { 
          $set: { 
            emailVerified: false,
            emailVerifiedAt: null
          } 
        }
      )
    },
    down: async (db) => {
      await db.collection('users').updateMany(
        {},
        { $unset: { emailVerified: '', emailVerifiedAt: '' } }
      )
    }
  }
]

// Run migrations
const runner = new MigrationRunner(db)
await runner.run(migrations)
```

### Batch Migration with Progress

```javascript
class BatchMigrator {
  constructor(options = {}) {
    this.batchSize = options.batchSize || 1000
    this.progressCallback = options.onProgress || (() => {})
    this.errorCallback = options.onError || ((err) => { throw err })
  }
  
  async migrate(collection, filter, transform) {
    // Get total count
    const total = await collection.countDocuments(filter)
    let processed = 0
    let errors = 0
    
    console.log(`Starting migration of ${total} documents`)
    
    // Process in batches using cursor
    const cursor = collection.find(filter).batchSize(this.batchSize)
    let batch = []
    
    for await (const doc of cursor) {
      try {
        const update = await transform(doc)
        
        if (update) {
          batch.push({
            updateOne: {
              filter: { _id: doc._id },
              update: update
            }
          })
        }
        
        if (batch.length >= this.batchSize) {
          await this.executeBatch(collection, batch)
          processed += batch.length
          batch = []
          
          this.progressCallback({
            processed,
            total,
            percentage: Math.round((processed / total) * 100),
            errors
          })
        }
      } catch (error) {
        errors++
        this.errorCallback(error, doc)
      }
    }
    
    // Process remaining
    if (batch.length > 0) {
      await this.executeBatch(collection, batch)
      processed += batch.length
    }
    
    return { processed, errors, total }
  }
  
  async executeBatch(collection, operations) {
    if (operations.length === 0) return
    
    try {
      await collection.bulkWrite(operations, { ordered: false })
    } catch (error) {
      // Handle partial failures
      if (error.writeErrors) {
        console.error(`Batch had ${error.writeErrors.length} errors`)
      }
      throw error
    }
  }
}

// Usage example: Migrate price format
const migrator = new BatchMigrator({
  batchSize: 500,
  onProgress: ({ processed, total, percentage }) => {
    console.log(`Progress: ${processed}/${total} (${percentage}%)`)
  },
  onError: (error, doc) => {
    console.error(`Error processing ${doc._id}:`, error.message)
  }
})

await migrator.migrate(
  db.collection('products'),
  { price: { $type: 'double' } },  // Filter: only products with old format
  (doc) => {
    // Transform: convert price number to price object
    return {
      $set: {
        price: {
          amount: doc.price,
          currency: 'USD'
        }
      }
    }
  }
)
```

---

## Data Transformation

### Aggregation Pipeline Migration

```javascript
// Complex data transformation using aggregation
async function migrateOrdersToNewSchema(db) {
  // Use $merge to transform and write to new collection
  await db.collection('orders_old').aggregate([
    // Flatten nested customer data
    {
      $lookup: {
        from: 'customers',
        localField: 'customerId',
        foreignField: '_id',
        as: 'customerData'
      }
    },
    { $unwind: '$customerData' },
    
    // Transform document structure
    {
      $project: {
        // Keep original ID
        _id: 1,
        
        // New order number format
        orderNumber: {
          $concat: ['ORD-', { $toString: '$orderNumber' }]
        },
        
        // Customer snapshot
        customer: {
          id: '$customerId',
          name: '$customerData.name',
          email: '$customerData.email'
        },
        
        // Transform items
        items: {
          $map: {
            input: '$items',
            as: 'item',
            in: {
              productId: '$$item.productId',
              sku: '$$item.sku',
              name: '$$item.name',
              quantity: '$$item.qty',  // Renamed field
              unitPrice: '$$item.price',
              totalPrice: { $multiply: ['$$item.qty', '$$item.price'] }
            }
          }
        },
        
        // Calculate totals
        subtotal: {
          $reduce: {
            input: '$items',
            initialValue: 0,
            in: {
              $add: [
                '$$value',
                { $multiply: ['$$this.qty', '$$this.price'] }
              ]
            }
          }
        },
        
        // Tax and shipping
        tax: { $ifNull: ['$tax', 0] },
        shipping: { $ifNull: ['$shippingCost', 0] },
        
        // Total
        total: {
          $add: [
            {
              $reduce: {
                input: '$items',
                initialValue: 0,
                in: {
                  $add: [
                    '$$value',
                    { $multiply: ['$$this.qty', '$$this.price'] }
                  ]
                }
              }
            },
            { $ifNull: ['$tax', 0] },
            { $ifNull: ['$shippingCost', 0] }
          ]
        },
        
        // Status mapping
        status: {
          $switch: {
            branches: [
              { case: { $eq: ['$status', 'new'] }, then: 'pending' },
              { case: { $eq: ['$status', 'paid'] }, then: 'confirmed' },
              { case: { $eq: ['$status', 'shipped'] }, then: 'shipped' },
              { case: { $eq: ['$status', 'complete'] }, then: 'delivered' }
            ],
            default: '$status'
          }
        },
        
        // Timestamps
        createdAt: '$created',
        updatedAt: '$modified',
        shippedAt: '$shipDate'
      }
    },
    
    // Write to new collection
    {
      $merge: {
        into: 'orders',
        on: '_id',
        whenMatched: 'replace',
        whenNotMatched: 'insert'
      }
    }
  ]).toArray()
}
```

### Incremental Migration with Versioning

```javascript
// Schema versioning approach
const CURRENT_SCHEMA_VERSION = 3

async function migrateDocument(db, collectionName, doc) {
  let current = doc
  let version = doc.schemaVersion || 1
  
  while (version < CURRENT_SCHEMA_VERSION) {
    const migrator = documentMigrators[`v${version}_to_v${version + 1}`]
    
    if (!migrator) {
      throw new Error(`No migrator for v${version} to v${version + 1}`)
    }
    
    current = await migrator(current)
    version++
  }
  
  current.schemaVersion = CURRENT_SCHEMA_VERSION
  return current
}

const documentMigrators = {
  v1_to_v2: (doc) => {
    // Split name field
    const [firstName, ...rest] = (doc.name || '').split(' ')
    return {
      ...doc,
      firstName,
      lastName: rest.join(' '),
      name: undefined  // Remove old field
    }
  },
  
  v2_to_v3: (doc) => {
    // Add preferences with defaults
    return {
      ...doc,
      preferences: {
        newsletter: doc.newsletter || false,
        theme: 'system',
        language: 'en'
      },
      newsletter: undefined  // Remove old field
    }
  }
}

// On-the-fly migration (lazy migration)
async function getUser(db, userId) {
  const user = await db.collection('users').findOne({ _id: userId })
  
  if (!user) return null
  
  // Check if migration needed
  if ((user.schemaVersion || 1) < CURRENT_SCHEMA_VERSION) {
    const migrated = await migrateDocument(db, 'users', user)
    
    // Update in database
    await db.collection('users').replaceOne(
      { _id: userId },
      migrated
    )
    
    return migrated
  }
  
  return user
}
```

### Data Type Conversion

```javascript
// Convert string dates to Date objects
async function migrateStringDatesToDate(db) {
  const collection = db.collection('events')
  
  // Find documents with string dates
  const cursor = collection.find({
    startDate: { $type: 'string' }
  })
  
  const bulkOps = []
  
  for await (const doc of cursor) {
    const updates = {}
    
    // Convert date strings
    if (typeof doc.startDate === 'string') {
      updates.startDate = new Date(doc.startDate)
    }
    if (typeof doc.endDate === 'string') {
      updates.endDate = new Date(doc.endDate)
    }
    if (typeof doc.createdAt === 'string') {
      updates.createdAt = new Date(doc.createdAt)
    }
    
    if (Object.keys(updates).length > 0) {
      bulkOps.push({
        updateOne: {
          filter: { _id: doc._id },
          update: { $set: updates }
        }
      })
    }
    
    if (bulkOps.length >= 1000) {
      await collection.bulkWrite(bulkOps)
      bulkOps.length = 0
    }
  }
  
  if (bulkOps.length > 0) {
    await collection.bulkWrite(bulkOps)
  }
}

// Convert embedded arrays to references
async function normalizeUserAddresses(db) {
  const users = db.collection('users')
  const addresses = db.collection('addresses')
  
  const cursor = users.find({ 'addresses.0': { $exists: true } })
  
  for await (const user of cursor) {
    const addressIds = []
    
    // Create separate address documents
    for (const address of user.addresses) {
      const result = await addresses.insertOne({
        ...address,
        userId: user._id,
        createdAt: new Date()
      })
      addressIds.push(result.insertedId)
    }
    
    // Update user with references
    await users.updateOne(
      { _id: user._id },
      {
        $set: { addressIds },
        $unset: { addresses: '' }
      }
    )
  }
}
```

---

## Migration Tools and Techniques

### mongodump and mongorestore

```bash
# Export collection
mongodump --uri="mongodb://localhost:27017/mydb" \
  --collection=users \
  --out=/backup/migration

# Export with query filter
mongodump --uri="mongodb://localhost:27017/mydb" \
  --collection=orders \
  --query='{"status":"completed"}' \
  --out=/backup/completed_orders

# Restore to new collection
mongorestore --uri="mongodb://localhost:27017/mydb" \
  --collection=users_new \
  --nsFrom="mydb.users" \
  --nsTo="mydb.users_new" \
  /backup/migration/mydb/users.bson

# Restore with drop (replace existing)
mongorestore --uri="mongodb://localhost:27017/mydb" \
  --drop \
  /backup/migration
```

### Python Migration Script

```python
from pymongo import MongoClient, UpdateOne
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self, uri: str, database: str):
        self.client = MongoClient(uri)
        self.db = self.client[database]
        self.migrations_collection = self.db['_migrations']
    
    def get_applied_migrations(self) -> set:
        migrations = self.migrations_collection.find({}, {'name': 1})
        return {m['name'] for m in migrations}
    
    def apply_migration(self, migration: dict):
        name = migration['name']
        applied = self.get_applied_migrations()
        
        if name in applied:
            logger.info(f"Migration {name} already applied, skipping")
            return
        
        logger.info(f"Applying migration: {name}")
        start_time = datetime.now()
        
        try:
            migration['up'](self.db)
            
            self.migrations_collection.insert_one({
                'name': name,
                'applied_at': datetime.now(),
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
            })
            
            logger.info(f"Migration {name} completed successfully")
        except Exception as e:
            logger.error(f"Migration {name} failed: {e}")
            raise
    
    def rollback_migration(self, migration: dict):
        name = migration['name']
        
        if 'down' not in migration:
            raise ValueError(f"Migration {name} does not support rollback")
        
        logger.info(f"Rolling back migration: {name}")
        
        try:
            migration['down'](self.db)
            self.migrations_collection.delete_one({'name': name})
            logger.info(f"Rollback of {name} completed")
        except Exception as e:
            logger.error(f"Rollback of {name} failed: {e}")
            raise
    
    def run_all(self, migrations: list):
        for migration in sorted(migrations, key=lambda m: m['name']):
            self.apply_migration(migration)


def batch_update(collection, filter_query: dict, transform_func, batch_size: int = 1000):
    """Batch update documents with progress tracking"""
    total = collection.count_documents(filter_query)
    processed = 0
    errors = 0
    
    cursor = collection.find(filter_query).batch_size(batch_size)
    operations = []
    
    for doc in cursor:
        try:
            update = transform_func(doc)
            if update:
                operations.append(UpdateOne(
                    {'_id': doc['_id']},
                    update
                ))
            
            if len(operations) >= batch_size:
                collection.bulk_write(operations, ordered=False)
                processed += len(operations)
                operations = []
                logger.info(f"Progress: {processed}/{total} ({processed*100//total}%)")
        
        except Exception as e:
            errors += 1
            logger.error(f"Error processing {doc['_id']}: {e}")
    
    if operations:
        collection.bulk_write(operations, ordered=False)
        processed += len(operations)
    
    return {'processed': processed, 'errors': errors, 'total': total}


# Define migrations
migrations = [
    {
        'name': '20240101_add_user_roles',
        'up': lambda db: db.users.update_many(
            {'roles': {'$exists': False}},
            {'$set': {'roles': ['user']}}
        ),
        'down': lambda db: db.users.update_many(
            {},
            {'$unset': {'roles': ''}}
        )
    },
    {
        'name': '20240102_normalize_emails',
        'up': lambda db: batch_update(
            db.users,
            {'email': {'$exists': True}},
            lambda doc: {'$set': {'email': doc['email'].lower().strip()}}
        ),
        'down': None  # Non-reversible
    },
    {
        'name': '20240103_add_created_at',
        'up': lambda db: db.users.update_many(
            {'createdAt': {'$exists': False}},
            {'$set': {'createdAt': datetime.now()}}
        ),
        'down': lambda db: db.users.update_many(
            {},
            {'$unset': {'createdAt': ''}}
        )
    }
]

# Run migrations
if __name__ == '__main__':
    manager = MigrationManager(
        'mongodb://localhost:27017',
        'mydb'
    )
    manager.run_all(migrations)
```

### Relational to MongoDB Migration

```javascript
// SQL to MongoDB migration helper
class SQLToMongoMigrator {
  constructor(sqlPool, mongoDb) {
    this.sql = sqlPool
    this.mongo = mongoDb
  }
  
  async migrateTable(tableName, options = {}) {
    const {
      collectionName = tableName,
      transform = (row) => row,
      batchSize = 1000,
      relations = []
    } = options
    
    // Get total count
    const [countResult] = await this.sql.query(`SELECT COUNT(*) as count FROM ${tableName}`)
    const total = countResult[0].count
    
    console.log(`Migrating ${total} rows from ${tableName}`)
    
    let offset = 0
    let migrated = 0
    
    while (offset < total) {
      // Fetch batch from SQL
      const [rows] = await this.sql.query(
        `SELECT * FROM ${tableName} LIMIT ? OFFSET ?`,
        [batchSize, offset]
      )
      
      // Transform and resolve relations
      const documents = await Promise.all(
        rows.map(async (row) => {
          let doc = transform(row)
          
          // Resolve relations
          for (const relation of relations) {
            doc = await this.resolveRelation(row, doc, relation)
          }
          
          return doc
        })
      )
      
      // Insert into MongoDB
      if (documents.length > 0) {
        await this.mongo.collection(collectionName).insertMany(documents)
      }
      
      migrated += documents.length
      offset += batchSize
      
      console.log(`Progress: ${migrated}/${total}`)
    }
    
    return { migrated, total }
  }
  
  async resolveRelation(row, doc, relation) {
    const { type, foreignKey, targetTable, targetField, as, embed } = relation
    
    if (type === 'one-to-one' || type === 'many-to-one') {
      if (embed) {
        // Embed related document
        const [related] = await this.sql.query(
          `SELECT * FROM ${targetTable} WHERE ${targetField} = ?`,
          [row[foreignKey]]
        )
        if (related.length > 0) {
          doc[as] = related[0]
        }
      } else {
        // Keep as reference (already in foreignKey)
        doc[as + 'Id'] = row[foreignKey]
      }
    } else if (type === 'one-to-many') {
      if (embed) {
        // Embed array of related documents
        const [related] = await this.sql.query(
          `SELECT * FROM ${targetTable} WHERE ${foreignKey} = ?`,
          [row.id]
        )
        doc[as] = related
      }
    }
    
    return doc
  }
}

// Usage: Migrate e-commerce database
async function migrateEcommerce(sqlPool, mongoDb) {
  const migrator = new SQLToMongoMigrator(sqlPool, mongoDb)
  
  // Migrate users
  await migrator.migrateTable('users', {
    transform: (row) => ({
      _id: row.id,
      email: row.email.toLowerCase(),
      name: {
        first: row.first_name,
        last: row.last_name
      },
      passwordHash: row.password_hash,
      createdAt: row.created_at,
      updatedAt: row.updated_at
    }),
    relations: [
      {
        type: 'one-to-many',
        foreignKey: 'user_id',
        targetTable: 'addresses',
        as: 'addresses',
        embed: true
      }
    ]
  })
  
  // Migrate products
  await migrator.migrateTable('products', {
    transform: (row) => ({
      _id: row.id,
      sku: row.sku,
      name: row.name,
      description: row.description,
      price: {
        amount: parseFloat(row.price),
        currency: row.currency || 'USD'
      },
      inventory: row.stock_quantity,
      categoryId: row.category_id,
      createdAt: row.created_at
    })
  })
  
  // Migrate orders with embedded items
  await migrator.migrateTable('orders', {
    transform: (row) => ({
      _id: row.id,
      orderNumber: `ORD-${row.id}`,
      customerId: row.user_id,
      status: row.status,
      subtotal: parseFloat(row.subtotal),
      tax: parseFloat(row.tax),
      shipping: parseFloat(row.shipping_cost),
      total: parseFloat(row.total),
      createdAt: row.created_at
    }),
    relations: [
      {
        type: 'one-to-many',
        foreignKey: 'order_id',
        targetTable: 'order_items',
        as: 'items',
        embed: true
      }
    ]
  })
}
```

---

## Zero-Downtime Migration

### Blue-Green Migration Strategy

```
┌─────────────────────────────────────────────────────────────────────┐
│               Blue-Green Migration Strategy                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Phase 1: Setup                                                    │
│   ┌─────────────────┐                                              │
│   │   Application   │                                              │
│   │                 │                                              │
│   │  ┌───────────┐  │                                              │
│   │  │  Blue DB  │◄─┼── Active (reads + writes)                   │
│   │  │  (Old)    │  │                                              │
│   │  └───────────┘  │                                              │
│   │                 │                                              │
│   │  ┌───────────┐  │                                              │
│   │  │ Green DB  │◄─┼── Standby (sync from Blue)                  │
│   │  │  (New)    │  │                                              │
│   │  └───────────┘  │                                              │
│   └─────────────────┘                                              │
│                                                                     │
│   Phase 2: Dual Write                                               │
│   ┌─────────────────┐                                              │
│   │   Application   │                                              │
│   │                 │                                              │
│   │  ┌───────────┐  │                                              │
│   │  │  Blue DB  │◄─┼── Reads + Writes                            │
│   │  │  (Old)    │  │                                              │
│   │  └───────────┘  │                                              │
│   │        │        │                                              │
│   │        ▼        │                                              │
│   │  ┌───────────┐  │                                              │
│   │  │ Green DB  │◄─┼── Writes (transformed)                      │
│   │  │  (New)    │  │                                              │
│   │  └───────────┘  │                                              │
│   └─────────────────┘                                              │
│                                                                     │
│   Phase 3: Switch                                                   │
│   ┌─────────────────┐                                              │
│   │   Application   │                                              │
│   │                 │                                              │
│   │  ┌───────────┐  │                                              │
│   │  │  Blue DB  │◄─┼── Standby (for rollback)                    │
│   │  │  (Old)    │  │                                              │
│   │  └───────────┘  │                                              │
│   │                 │                                              │
│   │  ┌───────────┐  │                                              │
│   │  │ Green DB  │◄─┼── Active (reads + writes)                   │
│   │  │  (New)    │  │                                              │
│   │  └───────────┘  │                                              │
│   └─────────────────┘                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Dual Write Implementation

```javascript
// Dual-write service for zero-downtime migration
class DualWriteService {
  constructor(oldDb, newDb, transformer) {
    this.oldDb = oldDb
    this.newDb = newDb
    this.transformer = transformer
    this.mode = 'old_primary'  // 'old_primary', 'dual_write', 'new_primary'
  }
  
  setMode(mode) {
    console.log(`Switching mode from ${this.mode} to ${mode}`)
    this.mode = mode
  }
  
  async insert(collection, document) {
    switch (this.mode) {
      case 'old_primary':
        return await this.oldDb.collection(collection).insertOne(document)
      
      case 'dual_write':
        // Write to old first (primary)
        const oldResult = await this.oldDb.collection(collection).insertOne(document)
        
        // Transform and write to new
        try {
          const transformed = this.transformer.transform(document)
          await this.newDb.collection(collection).insertOne(transformed)
        } catch (error) {
          console.error('New DB write failed:', error)
          // Log for later sync, don't fail the operation
        }
        
        return oldResult
      
      case 'new_primary':
        const transformed = this.transformer.transform(document)
        return await this.newDb.collection(collection).insertOne(transformed)
    }
  }
  
  async update(collection, filter, update) {
    switch (this.mode) {
      case 'old_primary':
        return await this.oldDb.collection(collection).updateOne(filter, update)
      
      case 'dual_write':
        const oldResult = await this.oldDb.collection(collection).updateOne(filter, update)
        
        try {
          const transformedUpdate = this.transformer.transformUpdate(update)
          await this.newDb.collection(collection).updateOne(filter, transformedUpdate)
        } catch (error) {
          console.error('New DB update failed:', error)
        }
        
        return oldResult
      
      case 'new_primary':
        const transformedUpdate = this.transformer.transformUpdate(update)
        return await this.newDb.collection(collection).updateOne(filter, transformedUpdate)
    }
  }
  
  async find(collection, filter, options = {}) {
    switch (this.mode) {
      case 'old_primary':
      case 'dual_write':
        return await this.oldDb.collection(collection).find(filter, options).toArray()
      
      case 'new_primary':
        return await this.newDb.collection(collection).find(filter, options).toArray()
    }
  }
  
  async findOne(collection, filter) {
    switch (this.mode) {
      case 'old_primary':
      case 'dual_write':
        return await this.oldDb.collection(collection).findOne(filter)
      
      case 'new_primary':
        return await this.newDb.collection(collection).findOne(filter)
    }
  }
}

// Document transformer
class DocumentTransformer {
  transform(doc) {
    // Apply schema transformations
    const transformed = { ...doc }
    
    // Example: Split name field
    if (doc.name) {
      const [firstName, ...rest] = doc.name.split(' ')
      transformed.firstName = firstName
      transformed.lastName = rest.join(' ')
      delete transformed.name
    }
    
    // Example: Add schema version
    transformed.schemaVersion = 2
    
    return transformed
  }
  
  transformUpdate(update) {
    // Transform update operations
    const transformed = { ...update }
    
    if (update.$set) {
      transformed.$set = { ...update.$set }
      
      // Transform name to firstName/lastName
      if (update.$set.name) {
        const [firstName, ...rest] = update.$set.name.split(' ')
        transformed.$set.firstName = firstName
        transformed.$set.lastName = rest.join(' ')
        delete transformed.$set.name
      }
    }
    
    return transformed
  }
}
```

### Change Stream for Sync

```javascript
// Use change streams to keep collections in sync
async function syncCollections(sourceDb, targetDb, collectionName, transformer) {
  const changeStream = sourceDb.collection(collectionName).watch([], {
    fullDocument: 'updateLookup'
  })
  
  console.log(`Watching changes on ${collectionName}`)
  
  for await (const change of changeStream) {
    try {
      switch (change.operationType) {
        case 'insert':
          const insertDoc = transformer.transform(change.fullDocument)
          await targetDb.collection(collectionName).insertOne(insertDoc)
          break
        
        case 'update':
        case 'replace':
          const updateDoc = transformer.transform(change.fullDocument)
          await targetDb.collection(collectionName).replaceOne(
            { _id: change.documentKey._id },
            updateDoc,
            { upsert: true }
          )
          break
        
        case 'delete':
          await targetDb.collection(collectionName).deleteOne({
            _id: change.documentKey._id
          })
          break
      }
    } catch (error) {
      console.error(`Sync error for ${change.operationType}:`, error)
      // Log failed operations for retry
    }
  }
}
```

---

## Migration Best Practices

### Pre-Migration Checklist

```javascript
// Pre-migration validation
async function validateMigration(db, migration) {
  const checks = []
  
  // Check source data exists
  const sourceCount = await db.collection(migration.source).countDocuments()
  checks.push({
    check: 'Source data exists',
    passed: sourceCount > 0,
    details: `Found ${sourceCount} documents`
  })
  
  // Check required indexes
  const indexes = await db.collection(migration.source).indexes()
  const requiredIndexes = migration.requiredIndexes || []
  
  for (const required of requiredIndexes) {
    const exists = indexes.some(idx => 
      JSON.stringify(idx.key) === JSON.stringify(required)
    )
    checks.push({
      check: `Index ${JSON.stringify(required)} exists`,
      passed: exists
    })
  }
  
  // Check disk space (approximate)
  const stats = await db.collection(migration.source).stats()
  checks.push({
    check: 'Sufficient disk space',
    passed: true,  // Would check actual disk space in production
    details: `Source size: ${Math.round(stats.storageSize / 1024 / 1024)}MB`
  })
  
  // Sample document validation
  const sampleDocs = await db.collection(migration.source)
    .aggregate([{ $sample: { size: 10 } }])
    .toArray()
  
  for (const doc of sampleDocs) {
    try {
      migration.transform(doc)
      checks.push({
        check: `Transform sample ${doc._id}`,
        passed: true
      })
    } catch (error) {
      checks.push({
        check: `Transform sample ${doc._id}`,
        passed: false,
        details: error.message
      })
    }
  }
  
  return {
    allPassed: checks.every(c => c.passed),
    checks
  }
}
```

### Rollback Strategy

```javascript
// Migration with automatic rollback
class SafeMigration {
  constructor(db) {
    this.db = db
    this.backupCollection = '_migration_backup'
  }
  
  async execute(migration) {
    const { name, source, transform, validate } = migration
    const backupName = `${this.backupCollection}_${name}_${Date.now()}`
    
    console.log(`Starting migration: ${name}`)
    
    try {
      // Create backup
      console.log('Creating backup...')
      await this.db.collection(source).aggregate([
        { $match: {} },
        { $out: backupName }
      ]).toArray()
      
      // Run migration
      console.log('Running migration...')
      const result = await this.runMigration(source, transform)
      
      // Validate results
      if (validate) {
        console.log('Validating results...')
        const isValid = await validate(this.db.collection(source))
        
        if (!isValid) {
          throw new Error('Validation failed')
        }
      }
      
      // Clean up backup after success
      console.log('Cleaning up backup...')
      await this.db.collection(backupName).drop()
      
      console.log(`Migration ${name} completed successfully`)
      return result
      
    } catch (error) {
      console.error(`Migration ${name} failed:`, error)
      console.log('Rolling back...')
      
      // Restore from backup
      await this.rollback(source, backupName)
      
      throw error
    }
  }
  
  async runMigration(collection, transform) {
    const cursor = this.db.collection(collection).find()
    const bulkOps = []
    let processed = 0
    
    for await (const doc of cursor) {
      const update = transform(doc)
      
      if (update) {
        bulkOps.push({
          updateOne: {
            filter: { _id: doc._id },
            update
          }
        })
      }
      
      if (bulkOps.length >= 1000) {
        await this.db.collection(collection).bulkWrite(bulkOps)
        processed += bulkOps.length
        bulkOps.length = 0
      }
    }
    
    if (bulkOps.length > 0) {
      await this.db.collection(collection).bulkWrite(bulkOps)
      processed += bulkOps.length
    }
    
    return { processed }
  }
  
  async rollback(collection, backupName) {
    // Drop current collection
    await this.db.collection(collection).drop()
    
    // Rename backup to original
    await this.db.collection(backupName).rename(collection)
    
    console.log('Rollback completed')
  }
}
```

### Migration Monitoring

```javascript
// Migration progress monitoring
class MigrationMonitor {
  constructor() {
    this.startTime = null
    this.stats = {
      total: 0,
      processed: 0,
      errors: 0,
      batchTimes: []
    }
  }
  
  start(total) {
    this.startTime = Date.now()
    this.stats.total = total
    console.log(`Migration started: ${total} documents to process`)
  }
  
  recordBatch(count, duration) {
    this.stats.processed += count
    this.stats.batchTimes.push(duration)
    
    const progress = (this.stats.processed / this.stats.total * 100).toFixed(1)
    const elapsed = (Date.now() - this.startTime) / 1000
    const rate = this.stats.processed / elapsed
    const remaining = (this.stats.total - this.stats.processed) / rate
    
    console.log([
      `Progress: ${this.stats.processed}/${this.stats.total} (${progress}%)`,
      `Rate: ${rate.toFixed(0)} docs/sec`,
      `ETA: ${this.formatTime(remaining)}`
    ].join(' | '))
  }
  
  recordError(error, doc) {
    this.stats.errors++
    console.error(`Error processing ${doc._id}: ${error.message}`)
  }
  
  complete() {
    const elapsed = (Date.now() - this.startTime) / 1000
    const avgBatchTime = this.stats.batchTimes.reduce((a, b) => a + b, 0) / this.stats.batchTimes.length
    
    console.log('\n=== Migration Complete ===')
    console.log(`Total processed: ${this.stats.processed}`)
    console.log(`Errors: ${this.stats.errors}`)
    console.log(`Total time: ${this.formatTime(elapsed)}`)
    console.log(`Average batch time: ${avgBatchTime.toFixed(0)}ms`)
    console.log(`Average rate: ${(this.stats.processed / elapsed).toFixed(0)} docs/sec`)
  }
  
  formatTime(seconds) {
    if (seconds < 60) return `${seconds.toFixed(0)}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }
}
```

---

## Summary

### Migration Strategy Comparison

| Strategy | Downtime | Complexity | Risk | Use Case |
|----------|----------|------------|------|----------|
| Direct | High | Low | Low | Small datasets |
| Batch | Medium | Medium | Medium | Medium datasets |
| Blue-Green | Zero | High | Low | Production systems |
| Lazy | None | Medium | Medium | Non-critical fields |
| Change Stream | Zero | High | Low | Real-time sync |

### Best Practices Summary

| Practice | Description |
|----------|-------------|
| Backup first | Always create backups before migration |
| Test thoroughly | Test on staging with production data |
| Monitor progress | Track migration progress and errors |
| Plan rollback | Have clear rollback procedures |
| Version schemas | Track schema versions in documents |
| Batch operations | Use bulk operations for performance |
| Validate data | Validate before and after migration |

### Migration Checklist

```markdown
□ Assessment
  □ Document current schema
  □ Define target schema
  □ Estimate data volume and time
  □ Identify dependencies

□ Planning
  □ Choose migration strategy
  □ Write migration scripts
  □ Define rollback procedures
  □ Schedule maintenance window

□ Testing
  □ Test on copy of production data
  □ Validate all edge cases
  □ Verify application compatibility
  □ Test rollback procedure

□ Execution
  □ Create backup
  □ Stop writes (if required)
  □ Run migration
  □ Validate results
  □ Switch traffic

□ Verification
  □ Verify data integrity
  □ Check application functionality
  □ Monitor for errors
  □ Remove old data/backups
```

---

## Practice Questions

1. What are the main types of data migrations in MongoDB?
2. How do you implement zero-downtime migration?
3. What is lazy migration and when should you use it?
4. How do you handle rollback in case of migration failure?
5. What tools can you use for MongoDB data migration?
6. How do you migrate data from a relational database to MongoDB?
7. What is dual-write strategy and how does it work?
8. How do you monitor migration progress effectively?

---

[← Previous: Schema Validation](69-schema-validation.md) | [Next: Atlas Overview →](71-atlas-overview.md)
