# Chapter 55: Backup and Recovery

## Table of Contents
- [Backup Overview](#backup-overview)
- [mongodump and mongorestore](#mongodump-and-mongorestore)
- [Filesystem Snapshots](#filesystem-snapshots)
- [Replica Set Backups](#replica-set-backups)
- [Sharded Cluster Backups](#sharded-cluster-backups)
- [Point-in-Time Recovery](#point-in-time-recovery)
- [Backup Strategies](#backup-strategies)
- [Summary](#summary)

---

## Backup Overview

### Backup Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Backup Types                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Logical Backup (mongodump)                                  │   │
│  │                                                             │   │
│  │ • Exports data in BSON format                               │   │
│  │ • Database/collection level granularity                     │   │
│  │ • Portable across versions                                  │   │
│  │ • Slower for large datasets                                 │   │
│  │ • Requires reading all data                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Physical Backup (Filesystem Snapshot)                       │   │
│  │                                                             │   │
│  │ • Copies raw data files                                     │   │
│  │ • Faster for large datasets                                 │   │
│  │ • Requires same MongoDB version                             │   │
│  │ • Must capture consistent state                             │   │
│  │ • Works with LVM, EBS snapshots, etc.                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Cloud Backup (Atlas/Ops Manager)                            │   │
│  │                                                             │   │
│  │ • Automated continuous backup                               │   │
│  │ • Point-in-time recovery                                    │   │
│  │ • Managed by MongoDB                                        │   │
│  │ • Enterprise/Atlas feature                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Backup Comparison

| Feature | mongodump | Filesystem Snapshot | Cloud Backup |
|---------|-----------|---------------------|--------------|
| Speed | Slower | Faster | Varies |
| Granularity | Collection | Full cluster | Configurable |
| Version portable | Yes | No | Yes |
| Point-in-time | With oplog | With journal | Yes |
| Complexity | Low | Medium | Low |

---

## mongodump and mongorestore

### Basic mongodump

```bash
# Dump entire server
mongodump --host localhost --port 27017

# Dump with authentication
mongodump --host localhost --port 27017 \
  --username backupUser \
  --password "secret" \
  --authenticationDatabase admin

# Dump specific database
mongodump --db mydb

# Dump specific collection
mongodump --db mydb --collection users

# Dump with query filter
mongodump --db mydb --collection orders \
  --query '{"createdAt": {"$gte": {"$date": "2024-01-01T00:00:00Z"}}}'

# Dump with compression
mongodump --gzip --out /backup/$(date +%Y%m%d)

# Dump to single archive file
mongodump --archive=/backup/backup.gz --gzip
```

### mongodump Options

```bash
# Output options
--out, -o          # Output directory
--archive          # Output to single archive file
--gzip             # Compress output

# Selection options
--db, -d           # Database name
--collection, -c   # Collection name
--query, -q        # Query filter (JSON)
--queryFile        # Query filter from file

# Connection options
--host, -h         # Server hostname
--port             # Server port
--uri              # Connection string

# Authentication
--username, -u     # Username
--password, -p     # Password
--authenticationDatabase  # Auth database

# Performance
--numParallelCollections  # Parallel dump (default: 4)
--readPreference          # Read preference

# Oplog options
--oplog            # Include oplog for PIT recovery
```

### mongodump with Oplog

```bash
# Capture oplog for point-in-time recovery
mongodump --oplog --out /backup/full_backup

# This creates:
# /backup/full_backup/
#   ├── admin/
#   ├── mydb/
#   └── oplog.bson  # Operations during backup
```

### Basic mongorestore

```bash
# Restore entire backup
mongorestore /backup/full_backup

# Restore with authentication
mongorestore \
  --username admin \
  --password "secret" \
  --authenticationDatabase admin \
  /backup/full_backup

# Restore specific database
mongorestore --db mydb /backup/full_backup/mydb

# Restore specific collection
mongorestore --db mydb --collection users \
  /backup/full_backup/mydb/users.bson

# Restore from archive
mongorestore --archive=/backup/backup.gz --gzip

# Restore with drop (replace existing)
mongorestore --drop /backup/full_backup

# Restore to different database
mongorestore --nsFrom="olddb.*" --nsTo="newdb.*" /backup/full_backup
```

### mongorestore Options

```bash
# Input options
--dir              # Input directory
--archive          # Input archive file
--gzip             # Decompress input

# Target options
--db, -d           # Target database
--collection, -c   # Target collection
--nsFrom           # Source namespace pattern
--nsTo             # Target namespace pattern

# Behavior options
--drop             # Drop collections before restore
--dryRun           # Show what would be done
--noIndexRestore   # Skip index restoration
--noOptionsRestore # Skip collection options

# Performance
--numParallelCollections      # Parallel restore
--numInsertionWorkersPerCollection  # Workers per collection
--batchSize                   # Documents per batch

# Oplog replay
--oplogReplay      # Replay oplog for PIT recovery
--oplogLimit       # Stop oplog replay at timestamp
--oplogFile        # Oplog file location
```

### mongorestore with Oplog Replay

```bash
# Restore with oplog replay (point-in-time)
mongorestore --oplogReplay /backup/full_backup

# Replay oplog up to specific timestamp
mongorestore --oplogReplay \
  --oplogLimit "1705312800:1" \
  /backup/full_backup
```

---

## Filesystem Snapshots

### Prerequisites

```bash
# For consistent snapshots, journal must be enabled
# and data/journal must be on same volume

# Check journal status
mongosh --eval "db.serverStatus().dur"
```

### LVM Snapshot

```bash
#!/bin/bash
# LVM snapshot backup script

# Configuration
DB_HOST="localhost"
DB_PORT="27017"
VG_NAME="vg_mongo"
LV_NAME="lv_data"
SNAPSHOT_SIZE="10G"
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Lock the database
mongosh --host $DB_HOST --port $DB_PORT --eval "
  db.fsyncLock()
"

# Create snapshot
lvcreate -L $SNAPSHOT_SIZE -s -n snap_$DATE /dev/$VG_NAME/$LV_NAME

# Unlock the database
mongosh --host $DB_HOST --port $DB_PORT --eval "
  db.fsyncUnlock()
"

# Mount snapshot and copy
mkdir -p /mnt/snap_$DATE
mount /dev/$VG_NAME/snap_$DATE /mnt/snap_$DATE

# Copy data
rsync -av /mnt/snap_$DATE/ $BACKUP_DIR/$DATE/

# Cleanup
umount /mnt/snap_$DATE
lvremove -f /dev/$VG_NAME/snap_$DATE

echo "Backup completed: $BACKUP_DIR/$DATE"
```

### AWS EBS Snapshot

```bash
#!/bin/bash
# EBS snapshot backup script

INSTANCE_ID="i-1234567890abcdef0"
VOLUME_ID="vol-0123456789abcdef0"
REGION="us-east-1"

# Lock MongoDB
mongosh --eval "db.fsyncLock()"

# Create EBS snapshot
SNAPSHOT_ID=$(aws ec2 create-snapshot \
  --volume-id $VOLUME_ID \
  --description "MongoDB backup $(date +%Y%m%d)" \
  --tag-specifications "ResourceType=snapshot,Tags=[{Key=Name,Value=mongodb-backup}]" \
  --region $REGION \
  --query SnapshotId \
  --output text)

# Unlock MongoDB
mongosh --eval "db.fsyncUnlock()"

echo "Created snapshot: $SNAPSHOT_ID"

# Wait for snapshot completion
aws ec2 wait snapshot-completed \
  --snapshot-ids $SNAPSHOT_ID \
  --region $REGION

echo "Snapshot completed"
```

### GCP Persistent Disk Snapshot

```bash
#!/bin/bash
# GCP disk snapshot backup

PROJECT="my-project"
ZONE="us-central1-a"
DISK_NAME="mongodb-data"
SNAPSHOT_NAME="mongodb-backup-$(date +%Y%m%d)"

# Lock MongoDB
mongosh --eval "db.fsyncLock()"

# Create snapshot
gcloud compute disks snapshot $DISK_NAME \
  --project=$PROJECT \
  --zone=$ZONE \
  --snapshot-names=$SNAPSHOT_NAME

# Unlock MongoDB
mongosh --eval "db.fsyncUnlock()"

echo "Created snapshot: $SNAPSHOT_NAME"
```

---

## Replica Set Backups

### Backup from Secondary

```bash
# Always backup from secondary to avoid primary impact
mongodump \
  --host "rs0/primary:27017,secondary1:27017,secondary2:27017" \
  --readPreference secondaryPreferred \
  --oplog \
  --out /backup/$(date +%Y%m%d)
```

### Hidden Member for Backup

```javascript
// Configure a hidden member for backups
rs.reconfig({
  _id: "rs0",
  members: [
    { _id: 0, host: "primary:27017" },
    { _id: 1, host: "secondary1:27017" },
    { _id: 2, host: "backup:27017", hidden: true, priority: 0 }
  ]
})
```

### Backup Script for Replica Set

```bash
#!/bin/bash
# Replica set backup script

RS_NAME="rs0"
BACKUP_HOST="backup.example.com:27017"
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Perform backup from hidden member
mongodump \
  --host $BACKUP_HOST \
  --oplog \
  --gzip \
  --out $BACKUP_DIR/$DATE

# Verify backup
if [ $? -eq 0 ]; then
  echo "Backup successful: $BACKUP_DIR/$DATE"
  
  # Create latest symlink
  ln -sfn $BACKUP_DIR/$DATE $BACKUP_DIR/latest
  
  # Cleanup old backups
  find $BACKUP_DIR -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;
else
  echo "Backup failed!"
  exit 1
fi
```

---

## Sharded Cluster Backups

### Sharded Cluster Backup Strategy

```
┌─────────────────────────────────────────────────────────────────────┐
│              Sharded Cluster Backup Process                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Stop the balancer                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  sh.stopBalancer()                                          │   │
│  │  // Wait for migrations to complete                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Step 2: Backup config servers                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  mongodump --host configRS/cfg1,cfg2,cfg3 --oplog           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Step 3: Backup each shard                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  For each shard:                                            │   │
│  │    mongodump --host shardRS/shard1,shard2,shard3 --oplog   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Step 4: Start the balancer                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  sh.startBalancer()                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sharded Cluster Backup Script

```bash
#!/bin/bash
# Sharded cluster backup script

MONGOS="mongos.example.com:27017"
CONFIG_RS="configRS/cfg1:27017,cfg2:27017,cfg3:27017"
SHARDS=(
  "shard0RS/shard0-1:27017,shard0-2:27017,shard0-3:27017"
  "shard1RS/shard1-1:27017,shard1-2:27017,shard1-3:27017"
)
BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"

mkdir -p $BACKUP_DIR

echo "Starting sharded cluster backup..."

# Step 1: Stop balancer
echo "Stopping balancer..."
mongosh --host $MONGOS --eval "
  sh.stopBalancer()
  while (sh.isBalancerRunning()) {
    print('Waiting for balancer to stop...')
    sleep(1000)
  }
  print('Balancer stopped')
"

# Step 2: Backup config servers
echo "Backing up config servers..."
mongodump --host $CONFIG_RS \
  --oplog \
  --gzip \
  --out $BACKUP_DIR/config

# Step 3: Backup each shard
for i in "${!SHARDS[@]}"; do
  echo "Backing up shard $i..."
  mongodump --host "${SHARDS[$i]}" \
    --oplog \
    --gzip \
    --out $BACKUP_DIR/shard$i
done

# Step 4: Start balancer
echo "Starting balancer..."
mongosh --host $MONGOS --eval "sh.startBalancer()"

# Record cluster metadata
mongosh --host $MONGOS --eval "
  print('=== Cluster Metadata ===')
  printjson(sh.status())
" > $BACKUP_DIR/cluster_metadata.txt

echo "Backup completed: $BACKUP_DIR"
```

### Restore Sharded Cluster

```bash
#!/bin/bash
# Sharded cluster restore script

BACKUP_DIR="/backup/20240115_120000"
CONFIG_RS="configRS/cfg1:27017,cfg2:27017,cfg3:27017"
SHARDS=(
  "shard0RS/shard0-1:27017,shard0-2:27017,shard0-3:27017"
  "shard1RS/shard1-1:27017,shard1-2:27017,shard1-3:27017"
)

echo "Starting sharded cluster restore..."

# Step 1: Restore config servers
echo "Restoring config servers..."
mongorestore --host $CONFIG_RS \
  --oplogReplay \
  --gzip \
  $BACKUP_DIR/config

# Step 2: Restore each shard
for i in "${!SHARDS[@]}"; do
  echo "Restoring shard $i..."
  mongorestore --host "${SHARDS[$i]}" \
    --oplogReplay \
    --gzip \
    $BACKUP_DIR/shard$i
done

echo "Restore completed"
```

---

## Point-in-Time Recovery

### Understanding Oplog

```javascript
// Oplog is a capped collection in local database
use local
db.oplog.rs.find().limit(5)

// Oplog entry structure
{
  "ts": Timestamp(1705312800, 1),    // Timestamp
  "t": NumberLong(1),                 // Term
  "h": NumberLong("1234567890"),      // Hash
  "v": 2,                             // Version
  "op": "i",                          // Operation type
  "ns": "mydb.users",                 // Namespace
  "o": { "_id": 1, "name": "John" }   // Document
}

// Operation types:
// i = insert
// u = update
// d = delete
// c = command (e.g., create collection)
// n = no-op
```

### Capture Oplog for PITR

```bash
# Full backup with oplog
mongodump --oplog --out /backup/full

# Later, dump oplog entries since backup
mongodump --db local --collection oplog.rs \
  --query '{"ts": {"$gt": {"$timestamp": {"t": 1705312800, "i": 1}}}}' \
  --out /backup/oplog_since_backup
```

### Point-in-Time Restore

```bash
#!/bin/bash
# Point-in-time restore script

BACKUP_DIR="/backup/full"
TARGET_TIME="1705316400"  # Unix timestamp

# Step 1: Restore full backup
mongorestore --drop $BACKUP_DIR

# Step 2: Replay oplog up to target time
mongorestore --oplogReplay \
  --oplogLimit "$TARGET_TIME:1" \
  $BACKUP_DIR

echo "Restored to point-in-time: $TARGET_TIME"
```

### Continuous Oplog Backup

```bash
#!/bin/bash
# Continuous oplog backup script

MONGO_HOST="localhost:27017"
OPLOG_DIR="/backup/oplog"
INTERVAL=60  # seconds

mkdir -p $OPLOG_DIR

# Get initial timestamp
LAST_TS=$(mongosh --host $MONGO_HOST --quiet --eval "
  db.getSiblingDB('local').oplog.rs.find().sort({\$natural: -1}).limit(1).next().ts
")

while true; do
  DATE=$(date +%Y%m%d_%H%M%S)
  
  # Dump new oplog entries
  mongodump --host $MONGO_HOST \
    --db local \
    --collection oplog.rs \
    --query "{\"ts\": {\"\$gt\": $LAST_TS}}" \
    --out $OPLOG_DIR/$DATE \
    --gzip
  
  # Update timestamp
  LAST_TS=$(mongosh --host $MONGO_HOST --quiet --eval "
    db.getSiblingDB('local').oplog.rs.find().sort({\$natural: -1}).limit(1).next().ts
  ")
  
  sleep $INTERVAL
done
```

---

## Backup Strategies

### 3-2-1 Backup Rule

```
┌─────────────────────────────────────────────────────────────────────┐
│                    3-2-1 Backup Strategy                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  3 - Keep THREE copies of your data                                │
│      ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│      │ Primary │  │ Backup  │  │ Backup  │                         │
│      │ Data    │  │ Copy 1  │  │ Copy 2  │                         │
│      └─────────┘  └─────────┘  └─────────┘                         │
│                                                                     │
│  2 - Store on TWO different media types                            │
│      ┌─────────────────────┐  ┌─────────────────────┐              │
│      │ Local Storage       │  │ Cloud Storage       │              │
│      │ (SSD/HDD)          │  │ (S3/GCS/Azure)      │              │
│      └─────────────────────┘  └─────────────────────┘              │
│                                                                     │
│  1 - Keep ONE copy offsite                                         │
│      ┌────────────────────────────────────────────────┐            │
│      │ Different geographic region or cloud provider  │            │
│      └────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Backup Schedule Template

```javascript
// Backup schedule configuration
const backupSchedule = {
  // Full backup
  full: {
    frequency: 'weekly',
    day: 'Sunday',
    time: '02:00',
    retention: '4 weeks',
    method: 'mongodump --oplog'
  },
  
  // Incremental (oplog)
  incremental: {
    frequency: 'hourly',
    retention: '7 days',
    method: 'oplog capture'
  },
  
  // Snapshot
  snapshot: {
    frequency: 'daily',
    time: '04:00',
    retention: '14 days',
    method: 'filesystem snapshot'
  }
}
```

### Backup Verification Script

```bash
#!/bin/bash
# Backup verification script

BACKUP_DIR=$1
RESTORE_PORT=27018
RESTORE_DBPATH="/tmp/mongo_restore_test"

if [ -z "$BACKUP_DIR" ]; then
  echo "Usage: $0 <backup_directory>"
  exit 1
fi

echo "Verifying backup: $BACKUP_DIR"

# Cleanup
rm -rf $RESTORE_DBPATH
mkdir -p $RESTORE_DBPATH

# Start temporary MongoDB
mongod --port $RESTORE_PORT --dbpath $RESTORE_DBPATH --fork --logpath /tmp/mongod_test.log

# Wait for startup
sleep 5

# Restore backup
mongorestore --port $RESTORE_PORT $BACKUP_DIR

# Verify data
COLLECTIONS=$(mongosh --port $RESTORE_PORT --quiet --eval "
  let count = 0
  db.adminCommand({listDatabases: 1}).databases.forEach(d => {
    if (d.name !== 'admin' && d.name !== 'local' && d.name !== 'config') {
      db.getSiblingDB(d.name).getCollectionNames().forEach(c => {
        count++
      })
    }
  })
  print(count)
")

echo "Restored $COLLECTIONS collections"

# Sample document counts
mongosh --port $RESTORE_PORT --quiet --eval "
  db.adminCommand({listDatabases: 1}).databases.forEach(d => {
    if (d.name !== 'admin' && d.name !== 'local' && d.name !== 'config') {
      db.getSiblingDB(d.name).getCollectionNames().forEach(c => {
        const count = db.getSiblingDB(d.name).getCollection(c).countDocuments()
        print(d.name + '.' + c + ': ' + count + ' documents')
      })
    }
  })
"

# Cleanup
mongosh --port $RESTORE_PORT --quiet --eval "db.adminCommand({shutdown: 1})"
rm -rf $RESTORE_DBPATH

echo "Verification complete"
```

---

## Summary

### Backup Methods

| Method | Best For | RPO | Complexity |
|--------|----------|-----|------------|
| mongodump | Small-medium DBs | Hours | Low |
| Filesystem Snapshot | Large DBs | Minutes | Medium |
| Oplog Backup | PITR | Seconds | Medium |
| Cloud Backup | Atlas/Enterprise | Seconds | Low |

### Key Commands

| Command | Purpose |
|---------|---------|
| mongodump | Export data to BSON |
| mongorestore | Import BSON data |
| --oplog | Include oplog |
| --oplogReplay | Replay oplog on restore |
| db.fsyncLock() | Lock for snapshot |
| db.fsyncUnlock() | Unlock after snapshot |

### Best Practices

| Practice | Reason |
|----------|--------|
| Backup from secondary | Don't impact primary |
| Use --oplog | Enable PITR |
| Test restores | Verify backups work |
| Store offsite | Disaster recovery |
| Automate | Consistency |
| Monitor | Detect failures |

### What's Next?

In the next chapter, we'll explore Monitoring MongoDB.

---

## Practice Questions

1. What's the difference between logical and physical backups?
2. When should you use mongodump vs filesystem snapshots?
3. What is the purpose of the --oplog flag?
4. How do you perform point-in-time recovery?
5. Why backup from a secondary?
6. How do you backup a sharded cluster?
7. What is the 3-2-1 backup rule?
8. How do you verify a backup?

---

## Hands-On Exercises

### Exercise 1: Automated Backup System

```javascript
// Backup management system

function backupManager() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           BACKUP MANAGEMENT SYSTEM                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Store backup metadata
  const backupDb = db.getSiblingDB('_backups')
  
  const operations = {
    // Record backup
    recordBackup: function(details) {
      const backup = {
        _id: new ObjectId(),
        timestamp: new Date(),
        type: details.type,         // 'full', 'incremental', 'snapshot'
        method: details.method,     // 'mongodump', 'snapshot', etc.
        location: details.location,
        size: details.size,
        databases: details.databases || [],
        status: 'completed',
        verified: false
      }
      
      backupDb.history.insertOne(backup)
      print(`Recorded backup: ${backup._id}`)
      return backup._id
    },
    
    // List backups
    listBackups: function(filter = {}) {
      print("\nBackup History:")
      print("─".repeat(60))
      
      const backups = backupDb.history.find(filter)
        .sort({ timestamp: -1 })
        .limit(10)
        .toArray()
      
      if (backups.length === 0) {
        print("No backups found")
        return
      }
      
      backups.forEach(b => {
        const date = b.timestamp.toISOString().split('T')[0]
        const verified = b.verified ? '✓' : '✗'
        print(`${verified} ${date} | ${b.type.padEnd(12)} | ${b.method.padEnd(10)} | ${b.location}`)
      })
    },
    
    // Mark as verified
    verifyBackup: function(backupId) {
      backupDb.history.updateOne(
        { _id: backupId },
        { 
          $set: { 
            verified: true, 
            verifiedAt: new Date() 
          } 
        }
      )
      print(`Backup ${backupId} marked as verified`)
    },
    
    // Get backup statistics
    getStats: function() {
      print("\nBackup Statistics:")
      print("─".repeat(40))
      
      const stats = backupDb.history.aggregate([
        {
          $group: {
            _id: "$type",
            count: { $sum: 1 },
            lastBackup: { $max: "$timestamp" },
            totalSize: { $sum: "$size" },
            verifiedCount: { 
              $sum: { $cond: ["$verified", 1, 0] } 
            }
          }
        }
      ]).toArray()
      
      stats.forEach(s => {
        print(`${s._id}:`)
        print(`  Count: ${s.count}`)
        print(`  Verified: ${s.verifiedCount}`)
        print(`  Last: ${s.lastBackup?.toISOString() || 'Never'}`)
        print(`  Total Size: ${(s.totalSize / 1024 / 1024).toFixed(2)} MB`)
      })
    },
    
    // Check backup age
    checkBackupAge: function(maxAge = 24) {
      const cutoff = new Date(Date.now() - maxAge * 60 * 60 * 1000)
      
      const recent = backupDb.history.findOne({
        timestamp: { $gte: cutoff }
      })
      
      if (recent) {
        print(`✓ Recent backup found: ${recent.timestamp.toISOString()}`)
        return true
      } else {
        print(`⚠ No backup in last ${maxAge} hours!`)
        return false
      }
    }
  }
  
  return operations
}

// Usage
const bm = backupManager()

// Record a backup
bm.recordBackup({
  type: 'full',
  method: 'mongodump',
  location: '/backup/20240115',
  size: 1024 * 1024 * 500,  // 500MB
  databases: ['mydb', 'analytics']
})

bm.listBackups()
bm.getStats()
bm.checkBackupAge(24)
```

### Exercise 2: Backup Verification Framework

```javascript
// Backup verification framework

function verifyBackup(options = {}) {
  print("=== Backup Verification Framework ===\n")
  
  const {
    backupPath = '/backup/latest',
    originalHost = 'localhost:27017'
  } = options
  
  const checks = []
  
  // Check 1: Backup files exist
  print("1. Checking backup structure...")
  // In practice, check filesystem
  checks.push({
    name: 'Backup files exist',
    passed: true,  // Simulated
    details: 'All expected files found'
  })
  
  // Check 2: Compare collection counts
  print("2. Comparing collection counts...")
  const dbList = db.adminCommand({ listDatabases: 1 }).databases
  
  dbList.forEach(dbInfo => {
    if (['admin', 'local', 'config'].includes(dbInfo.name)) return
    
    const colls = db.getSiblingDB(dbInfo.name).getCollectionNames()
    colls.forEach(coll => {
      const count = db.getSiblingDB(dbInfo.name).getCollection(coll).countDocuments()
      checks.push({
        name: `${dbInfo.name}.${coll} count`,
        passed: true,  // Would compare with restored backup
        details: `${count} documents`,
        count
      })
    })
  })
  
  // Check 3: Verify indexes
  print("3. Verifying indexes...")
  dbList.forEach(dbInfo => {
    if (['admin', 'local', 'config'].includes(dbInfo.name)) return
    
    const colls = db.getSiblingDB(dbInfo.name).getCollectionNames()
    colls.forEach(coll => {
      const indexes = db.getSiblingDB(dbInfo.name).getCollection(coll).getIndexes()
      checks.push({
        name: `${dbInfo.name}.${coll} indexes`,
        passed: true,
        details: `${indexes.length} indexes`
      })
    })
  })
  
  // Summary
  print("\n" + "═".repeat(50))
  print("Verification Results:")
  print("─".repeat(50))
  
  let passed = 0
  let failed = 0
  
  checks.forEach(check => {
    if (check.passed) {
      passed++
      print(`  ✓ ${check.name}`)
    } else {
      failed++
      print(`  ✗ ${check.name}: ${check.details}`)
    }
  })
  
  print("─".repeat(50))
  print(`Total: ${passed} passed, ${failed} failed`)
  print(`Status: ${failed === 0 ? 'VERIFIED' : 'FAILED'}`)
  
  return { checks, passed, failed }
}

verifyBackup()
```

### Exercise 3: Restore Planner

```javascript
// Plan and execute restore operations

function restorePlanner() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              RESTORE PLANNER                                ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const scenarios = {
    'full-restore': {
      description: 'Complete database restore',
      steps: [
        '1. Stop application connections',
        '2. Backup current state (if recoverable)',
        '3. Drop existing databases (if --drop)',
        '4. Restore from backup',
        '5. Replay oplog if PITR',
        '6. Verify data integrity',
        '7. Restart applications'
      ],
      command: 'mongorestore --drop --oplogReplay /backup/latest',
      estimatedTime: 'Depends on data size'
    },
    
    'single-collection': {
      description: 'Restore specific collection',
      steps: [
        '1. Identify backup with collection',
        '2. Optional: backup current collection',
        '3. Restore collection (with or without drop)',
        '4. Rebuild indexes if needed',
        '5. Verify data'
      ],
      command: 'mongorestore --db mydb --collection users /backup/mydb/users.bson',
      estimatedTime: 'Minutes for small collections'
    },
    
    'point-in-time': {
      description: 'Restore to specific point in time',
      steps: [
        '1. Identify target timestamp',
        '2. Find backup before target time',
        '3. Restore full backup',
        '4. Replay oplog to target timestamp',
        '5. Verify target state achieved'
      ],
      command: 'mongorestore --oplogReplay --oplogLimit "1705316400:1" /backup/full',
      estimatedTime: 'Depends on oplog size'
    },
    
    'selective-restore': {
      description: 'Restore specific databases only',
      steps: [
        '1. List databases in backup',
        '2. Select databases to restore',
        '3. Restore each database',
        '4. Verify inter-database relationships'
      ],
      command: 'mongorestore --nsInclude "mydb.*" /backup/latest',
      estimatedTime: 'Varies'
    }
  }
  
  function showScenario(name) {
    const scenario = scenarios[name]
    if (!scenario) {
      print(`Unknown scenario: ${name}`)
      print(`Available: ${Object.keys(scenarios).join(', ')}`)
      return
    }
    
    print(`Scenario: ${name}`)
    print(`Description: ${scenario.description}`)
    print("\nSteps:")
    scenario.steps.forEach(s => print(`  ${s}`))
    print(`\nCommand: ${scenario.command}`)
    print(`Estimated Time: ${scenario.estimatedTime}`)
  }
  
  function generateRestorePlan(options) {
    const {
      scenario,
      backupPath,
      targetTime,
      databases,
      dryRun = true
    } = options
    
    print("\n=== Generated Restore Plan ===\n")
    
    // Pre-flight checks
    print("Pre-flight Checks:")
    print("  ☐ Backup exists and is valid")
    print("  ☐ Sufficient disk space")
    print("  ☐ Application traffic stopped")
    print("  ☐ Team notified")
    
    // Generate command
    let cmd = 'mongorestore'
    if (dryRun) cmd += ' --dryRun'
    if (backupPath) cmd += ` ${backupPath}`
    if (targetTime) cmd += ` --oplogReplay --oplogLimit "${targetTime}:1"`
    if (databases) cmd += ` --nsInclude "${databases}.*"`
    
    print("\nCommand:")
    print(`  ${cmd}`)
    
    // Post-restore
    print("\nPost-restore Verification:")
    print("  ☐ Document counts match")
    print("  ☐ Indexes present")
    print("  ☐ Application connectivity")
    print("  ☐ Data spot checks")
    
    return cmd
  }
  
  return { scenarios, showScenario, generateRestorePlan }
}

const rp = restorePlanner()

// Show available scenarios
Object.keys(rp.scenarios).forEach(s => {
  print(`• ${s}: ${rp.scenarios[s].description}`)
})

print()

// Show specific scenario
rp.showScenario('point-in-time')

print()

// Generate restore plan
rp.generateRestorePlan({
  scenario: 'point-in-time',
  backupPath: '/backup/20240115',
  targetTime: '1705316400',
  dryRun: true
})
```

### Exercise 4: Backup Monitoring Dashboard

```javascript
// Backup monitoring and alerting

function backupMonitor() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           BACKUP MONITORING DASHBOARD                       ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Simulated backup history
  const backupHistory = [
    { date: '2024-01-15', type: 'full', size: 512, duration: 45, status: 'success' },
    { date: '2024-01-14', type: 'full', size: 510, duration: 43, status: 'success' },
    { date: '2024-01-13', type: 'full', size: 508, duration: 44, status: 'success' },
    { date: '2024-01-12', type: 'full', size: 505, duration: 42, status: 'success' },
    { date: '2024-01-11', type: 'full', size: 502, duration: 41, status: 'success' },
    { date: '2024-01-10', type: 'full', size: 500, duration: 40, status: 'success' },
    { date: '2024-01-09', type: 'full', size: 498, duration: 39, status: 'failed' }
  ]
  
  // Current status
  print("┌─ CURRENT STATUS ──────────────────────────────────────────┐")
  
  const lastBackup = backupHistory[0]
  const lastSuccessful = backupHistory.find(b => b.status === 'success')
  
  const hoursSince = Math.round(
    (new Date() - new Date(lastSuccessful.date)) / (1000 * 60 * 60)
  )
  
  print(`│  Last Backup: ${lastBackup.date} (${lastBackup.status})`.padEnd(60) + "│")
  print(`│  Hours Since Last Backup: ${hoursSince}`.padEnd(60) + "│")
  print(`│  Status: ${hoursSince < 24 ? '✓ OK' : '⚠ ALERT'}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // History
  print("┌─ BACKUP HISTORY ──────────────────────────────────────────┐")
  print("│  Date        Type     Size(MB)  Duration(min)  Status    │")
  print("├────────────────────────────────────────────────────────────┤")
  
  backupHistory.forEach(b => {
    const status = b.status === 'success' ? '✓' : '✗'
    print(`│  ${b.date}   ${b.type.padEnd(8)} ${String(b.size).padEnd(9)} ${String(b.duration).padEnd(14)} ${status}        │`)
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Trends
  print("┌─ TRENDS ──────────────────────────────────────────────────┐")
  
  const avgSize = backupHistory.reduce((a, b) => a + b.size, 0) / backupHistory.length
  const avgDuration = backupHistory.reduce((a, b) => a + b.duration, 0) / backupHistory.length
  const successRate = backupHistory.filter(b => b.status === 'success').length / backupHistory.length * 100
  
  print(`│  Average Backup Size: ${avgSize.toFixed(0)} MB`.padEnd(60) + "│")
  print(`│  Average Duration: ${avgDuration.toFixed(0)} minutes`.padEnd(60) + "│")
  print(`│  Success Rate: ${successRate.toFixed(1)}%`.padEnd(60) + "│")
  
  // Size trend
  const sizeGrowth = (backupHistory[0].size - backupHistory[backupHistory.length - 1].size) / 
                     backupHistory[backupHistory.length - 1].size * 100
  print(`│  Size Growth: ${sizeGrowth.toFixed(1)}% over period`.padEnd(60) + "│")
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Alerts
  const alerts = []
  
  if (hoursSince > 24) {
    alerts.push({ level: 'CRITICAL', message: 'No backup in 24+ hours' })
  }
  if (successRate < 90) {
    alerts.push({ level: 'WARNING', message: 'Success rate below 90%' })
  }
  if (sizeGrowth > 20) {
    alerts.push({ level: 'INFO', message: 'Significant backup size growth' })
  }
  
  if (alerts.length > 0) {
    print("┌─ ALERTS ───────────────────────────────────────────────────┐")
    alerts.forEach(a => {
      const icon = a.level === 'CRITICAL' ? '🔴' : a.level === 'WARNING' ? '🟠' : '🔵'
      print(`│  ${icon} [${a.level}] ${a.message}`.padEnd(60) + "│")
    })
    print("└────────────────────────────────────────────────────────────┘")
  }
}

backupMonitor()
```

### Exercise 5: Disaster Recovery Runbook

```javascript
// Disaster recovery procedures

function disasterRecoveryRunbook() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         DISASTER RECOVERY RUNBOOK                           ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const scenarios = {
    'primary-failure': {
      severity: 'HIGH',
      description: 'Primary node failure in replica set',
      detection: 'Automatic election should promote secondary',
      steps: [
        'Verify automatic failover occurred',
        'Check application connectivity to new primary',
        'Investigate failed node',
        'Once recovered, rejoin as secondary',
        'Monitor for data consistency'
      ],
      rto: '< 30 seconds (automatic)',
      rpo: '0 (synchronous replication)'
    },
    
    'datacenter-outage': {
      severity: 'CRITICAL',
      description: 'Complete datacenter failure',
      detection: 'Multiple node failures, network unreachable',
      steps: [
        'Activate DR site',
        'Update DNS to DR cluster',
        'Restore from latest backup if needed',
        'Replay oplog to minimize data loss',
        'Verify application connectivity',
        'Begin data reconciliation'
      ],
      rto: '< 1 hour',
      rpo: 'Last backup + oplog'
    },
    
    'data-corruption': {
      severity: 'HIGH',
      description: 'Data corruption detected',
      detection: 'Checksum failures, invalid documents',
      steps: [
        'Stop writes to affected collection',
        'Identify corruption extent',
        'Restore from backup before corruption',
        'Replay oplog to just before corruption',
        'Validate restored data',
        'Resume operations'
      ],
      rto: '1-4 hours',
      rpo: 'Point-in-time before corruption'
    },
    
    'accidental-deletion': {
      severity: 'MEDIUM',
      description: 'Critical data accidentally deleted',
      detection: 'User report, monitoring alerts',
      steps: [
        'Identify deletion timestamp',
        'Locate backup from before deletion',
        'Export affected data from backup',
        'Import to production',
        'Verify data integrity',
        'Review access controls'
      ],
      rto: '30 minutes - 2 hours',
      rpo: 'Last backup before deletion'
    }
  }
  
  function showScenario(name) {
    const s = scenarios[name]
    if (!s) {
      print(`Unknown scenario. Available: ${Object.keys(scenarios).join(', ')}`)
      return
    }
    
    print(`\n${"═".repeat(60)}`)
    print(`SCENARIO: ${name.toUpperCase()}`)
    print(`Severity: ${s.severity}`)
    print("═".repeat(60))
    
    print(`\nDescription: ${s.description}`)
    print(`Detection: ${s.detection}`)
    
    print("\nRecovery Steps:")
    s.steps.forEach((step, i) => {
      print(`  ${i + 1}. ${step}`)
    })
    
    print(`\nRTO (Recovery Time Objective): ${s.rto}`)
    print(`RPO (Recovery Point Objective): ${s.rpo}`)
  }
  
  function runDRChecklist() {
    print("\n=== DR Readiness Checklist ===\n")
    
    const checklist = [
      { item: 'Recent backup exists', check: () => true },
      { item: 'Backup verified', check: () => true },
      { item: 'DR site accessible', check: () => true },
      { item: 'Runbooks documented', check: () => true },
      { item: 'Team trained', check: () => true },
      { item: 'Communication plan exists', check: () => true },
      { item: 'Last DR drill within 90 days', check: () => false }
    ]
    
    let ready = 0
    let notReady = 0
    
    checklist.forEach(c => {
      const status = c.check() ? '✓' : '✗'
      if (c.check()) ready++
      else notReady++
      print(`  ${status} ${c.item}`)
    })
    
    print(`\nReadiness: ${ready}/${checklist.length} items`)
    print(`Status: ${notReady === 0 ? 'READY' : 'NOT FULLY READY'}`)
  }
  
  // Show all scenarios
  print("Available DR Scenarios:")
  Object.entries(scenarios).forEach(([name, s]) => {
    print(`  • ${name} (${s.severity}): ${s.description}`)
  })
  
  // Show one scenario
  showScenario('datacenter-outage')
  
  // Run checklist
  runDRChecklist()
}

disasterRecoveryRunbook()
```

---

[← Previous: Security Best Practices](54-security-best-practices.md) | [Next: Monitoring →](56-monitoring.md)
