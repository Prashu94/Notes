# Backup and Recovery

## Overview

Database backup and recovery are critical for data protection and business continuity. This comprehensive guide covers PostgreSQL backup strategies, recovery procedures, point-in-time recovery (PITR), replication, and disaster recovery planning.

## Table of Contents
- [Backup Strategies](#backup-strategies)
- [Logical Backups](#logical-backups)
- [Physical Backups](#physical-backups)
- [Continuous Archiving and PITR](#continuous-archiving-and-pitr)
- [Point-in-Time Recovery](#point-in-time-recovery)
- [Backup Tools](#backup-tools)
- [Recovery Procedures](#recovery-procedures)
- [High Availability](#high-availability)
- [Disaster Recovery Planning](#disaster-recovery-planning)
- [Backup Best Practices](#backup-best-practices)

## Backup Strategies

### Backup Types

```sql
-- Three main backup types:

-- 1. Logical Backup (pg_dump/pg_dumpall)
-- - Human-readable SQL
-- - Platform independent
-- - Selective backup (database, schema, table)
-- - Slower for large databases
-- - Online backup (no downtime)

-- 2. Physical Backup (pg_basebackup/filesystem copy)
-- - Binary copy of data directory
-- - Faster for large databases
-- - Entire cluster only
-- - Platform dependent
-- - Requires careful timing or pg_basebackup

-- 3. Continuous Archiving (WAL archiving + base backup)
-- - Point-in-time recovery
-- - Incremental backups (WAL files)
-- - Most flexible
-- - More complex setup

-- Backup comparison
CREATE TABLE backup_comparison (
    backup_type TEXT,
    speed TEXT,
    flexibility TEXT,
    size TEXT,
    restore_speed TEXT
);

INSERT INTO backup_comparison VALUES
    ('Logical (pg_dump)', 'Slow', 'High (selective)', 'Compressed', 'Slow'),
    ('Physical (pg_basebackup)', 'Fast', 'Low (cluster only)', 'Large', 'Fast'),
    ('Continuous Archiving', 'Fast (incremental)', 'High (PITR)', 'Medium', 'Fast');
```

### Backup Schedule

```sql
-- Recommended backup schedule:

-- Daily full backups (logical or physical)
-- Continuous WAL archiving (for PITR)
-- Weekly/monthly archival backups (long-term retention)

-- Example schedule:
-- Daily 2 AM: Full logical backup (pg_dump)
-- Daily 3 AM: Full physical backup (pg_basebackup)
-- Continuous: WAL archiving every 5 minutes
-- Sunday 4 AM: Weekly archival backup (long-term storage)
-- 1st of month: Monthly archival backup

-- Retention policy:
-- Daily backups: 7 days
-- Weekly backups: 4 weeks
-- Monthly backups: 12 months
-- Annual backups: 7 years (compliance)

-- Backup scheduling (cron example)
-- 0 2 * * * /usr/local/bin/backup-daily.sh
-- 0 4 * * 0 /usr/local/bin/backup-weekly.sh
```

## Logical Backups

### pg_dump (Single Database)

```sql
-- Basic pg_dump usage

-- Dump entire database to SQL file
-- $ pg_dump mydb > mydb_backup.sql

-- Dump with compression
-- $ pg_dump mydb | gzip > mydb_backup.sql.gz

-- Custom format (recommended, allows selective restore)
-- $ pg_dump -Fc mydb -f mydb_backup.dump

-- Directory format (parallel dump, faster)
-- $ pg_dump -Fd mydb -f mydb_backup_dir -j 4

-- Plain SQL format
-- $ pg_dump -Fp mydb -f mydb_backup.sql

-- Dump specific schema
-- $ pg_dump -n public mydb -f public_schema.sql

-- Dump specific table
-- $ pg_dump -t users mydb -f users_table.sql

-- Dump multiple tables
-- $ pg_dump -t orders -t order_items mydb -f orders.sql

-- Exclude tables
-- $ pg_dump --exclude-table=audit_log mydb -f mydb_no_audit.sql

-- Schema only (no data)
-- $ pg_dump --schema-only mydb -f mydb_schema.sql

-- Data only (no schema)
-- $ pg_dump --data-only mydb -f mydb_data.sql

-- With connection parameters
-- $ pg_dump -h localhost -p 5432 -U postgres -W mydb -f backup.sql
```

### pg_dumpall (Entire Cluster)

```sql
-- Dump entire PostgreSQL cluster (all databases)

-- All databases
-- $ pg_dumpall > cluster_backup.sql

-- Only global objects (roles, tablespaces)
-- $ pg_dumpall --globals-only > globals.sql

-- Only roles
-- $ pg_dumpall --roles-only > roles.sql

-- Only tablespaces
-- $ pg_dumpall --tablespaces-only > tablespaces.sql

-- Typical backup script combining both
-- $ pg_dumpall --globals-only > globals.sql
-- $ pg_dump -Fc mydb -f mydb.dump

-- Complete cluster backup script
-- #!/bin/bash
-- BACKUP_DIR="/backups/$(date +%Y%m%d)"
-- mkdir -p $BACKUP_DIR
-- 
-- # Backup globals
-- pg_dumpall --globals-only > $BACKUP_DIR/globals.sql
-- 
-- # Backup each database
-- for db in $(psql -t -c "SELECT datname FROM pg_database WHERE datname NOT IN ('template0', 'template1')"); do
--     pg_dump -Fc $db -f $BACKUP_DIR/${db}.dump
-- done
-- 
-- # Compress
-- tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
-- rm -rf $BACKUP_DIR
```

### Restoring Logical Backups

```sql
-- Restore from SQL dump
-- $ psql mydb < mydb_backup.sql

-- Restore from custom format
-- $ pg_restore -d mydb mydb_backup.dump

-- Restore with verbose output
-- $ pg_restore -v -d mydb mydb_backup.dump

-- Restore with parallel jobs
-- $ pg_restore -d mydb -j 4 mydb_backup_dir

-- Restore specific table
-- $ pg_restore -d mydb -t users mydb_backup.dump

-- Restore specific schema
-- $ pg_restore -d mydb -n public mydb_backup.dump

-- Clean before restore (drop existing objects)
-- $ pg_restore -c -d mydb mydb_backup.dump

-- Create database before restore
-- $ createdb mydb
-- $ pg_restore -d mydb mydb_backup.dump

-- Restore globals and databases
-- $ psql -f globals.sql
-- $ pg_restore -d mydb mydb.dump

-- Restore to different database name
-- $ createdb newdb
-- $ pg_restore -d newdb mydb_backup.dump
```

## Physical Backups

### pg_basebackup

```sql
-- pg_basebackup: Online physical backup of entire cluster

-- Basic backup
-- $ pg_basebackup -D /backup/base -Fp

-- With compression
-- $ pg_basebackup -D /backup/base -Ft -z

-- Format options:
-- -Fp: Plain (directory copy)
-- -Ft: Tar (creates tar files)

-- With WAL files (for PITR)
-- $ pg_basebackup -D /backup/base -Ft -z -X stream

-- -X options:
-- fetch: Collect WAL at end (may miss files)
-- stream: Stream WAL during backup (recommended)

-- Verbose output
-- $ pg_basebackup -D /backup/base -v -P

-- With connection parameters
-- $ pg_basebackup -h localhost -p 5432 -U replicator -W -D /backup/base -Ft -z -X stream

-- Label backup
-- $ pg_basebackup -D /backup/base -l "daily_backup_2024_01_15"

-- Checkpoint options
-- $ pg_basebackup -D /backup/base -c fast
-- fast: Checkpoint immediately
-- spread: Spread checkpoint I/O (default)

-- Exclude WAL files from backup directory (separate WAL)
-- $ pg_basebackup -D /backup/base -X stream --wal-method=stream

-- Example backup script
-- #!/bin/bash
-- BACKUP_DIR="/backups/base_$(date +%Y%m%d_%H%M%S)"
-- pg_basebackup -h localhost -U replicator -D $BACKUP_DIR \
--     -Ft -z -X stream -P -v \
--     -l "automated_backup_$(date +%Y%m%d)"
-- 
-- # Move to archive storage
-- mv $BACKUP_DIR /archive/
```

### Filesystem Backup

```sql
-- Filesystem-level backup (requires cluster stop)

-- 1. Stop PostgreSQL
-- $ pg_ctl stop -D /var/lib/postgresql/data

-- 2. Copy data directory
-- $ cp -r /var/lib/postgresql/data /backup/data_$(date +%Y%m%d)

-- Or use rsync
-- $ rsync -av /var/lib/postgresql/data/ /backup/data_$(date +%Y%m%d)/

-- 3. Start PostgreSQL
-- $ pg_ctl start -D /var/lib/postgresql/data

-- WARNING: Never copy files while PostgreSQL is running!
-- Use pg_basebackup for online backups

-- Snapshot-based backup (if filesystem supports)
-- LVM snapshot (Linux)
-- $ lvcreate -L 10G -s -n pg_snap /dev/vg0/pg_data
-- $ mount /dev/vg0/pg_snap /mnt/snapshot
-- $ tar -czf /backup/snapshot_$(date +%Y%m%d).tar.gz -C /mnt/snapshot .
-- $ umount /mnt/snapshot
-- $ lvremove -f /dev/vg0/pg_snap

-- ZFS snapshot
-- $ zfs snapshot pool/pgdata@backup_$(date +%Y%m%d)
-- $ zfs send pool/pgdata@backup_$(date +%Y%m%d) | gzip > /backup/zfs_$(date +%Y%m%d).gz
```

## Continuous Archiving and PITR

### Configuring WAL Archiving

```sql
-- Enable WAL archiving for point-in-time recovery

-- 1. Edit postgresql.conf
-- wal_level = replica  (or logical)
-- archive_mode = on
-- archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'
-- archive_timeout = 300  (5 minutes)

-- 2. Create archive directory
-- $ mkdir -p /archive
-- $ chown postgres:postgres /archive

-- 3. Restart PostgreSQL
-- $ pg_ctl restart

-- Alternative archive commands:

-- Copy with compression
-- archive_command = 'gzip < %p > /archive/%f.gz'

-- Copy to remote server (rsync)
-- archive_command = 'rsync -a %p user@remote:/archive/%f'

-- Copy to S3 (AWS)
-- archive_command = 'aws s3 cp %p s3://my-bucket/wal-archive/%f'

-- Copy with error handling
-- archive_command = 'test ! -f /archive/%f && cp %p /archive/%f || true'

-- Set archive command
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'test ! -f /archive/%f && cp %p /archive/%f';
ALTER SYSTEM SET archive_timeout = '5min';
-- Restart required
-- $ pg_ctl restart

-- Monitor archiving
SELECT 
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time
FROM pg_stat_archiver;

-- Check archive directory
-- $ ls -lh /archive/
-- Should see 000000010000000000000001, 000000010000000000000002, etc.
```

### Creating Base Backup for PITR

```sql
-- Create base backup with WAL archiving

-- 1. Ensure WAL archiving is configured (above)

-- 2. Create base backup
-- $ pg_basebackup -D /backup/pitr_base -Ft -z -X stream

-- 3. Backup includes:
-- - base.tar.gz: Data directory backup
-- - pg_wal.tar.gz: Required WAL files
-- - backup_label: Backup metadata

-- Complete PITR backup script
-- #!/bin/bash
-- BACKUP_DIR="/backup/pitr_$(date +%Y%m%d_%H%M%S)"
-- mkdir -p $BACKUP_DIR
-- 
-- # Create base backup
-- pg_basebackup -D $BACKUP_DIR -Ft -z -X stream -P
-- 
-- # Archive directory already has WAL files from continuous archiving
-- echo "Base backup created: $BACKUP_DIR"
-- echo "WAL archive: /archive/"
```

## Point-in-Time Recovery

### PITR Recovery Process

```sql
-- Recover database to specific point in time

-- 1. Stop PostgreSQL (if running)
-- $ pg_ctl stop

-- 2. Backup current data directory (just in case)
-- $ mv /var/lib/postgresql/data /var/lib/postgresql/data.old

-- 3. Extract base backup
-- $ mkdir /var/lib/postgresql/data
-- $ tar -xzf /backup/pitr_base/base.tar.gz -C /var/lib/postgresql/data

-- 4. Create recovery configuration
-- PostgreSQL 12+: Create recovery.signal file
-- $ touch /var/lib/postgresql/data/recovery.signal

-- PostgreSQL <12: Create recovery.conf file

-- 5. Configure recovery in postgresql.conf (or postgresql.auto.conf)
ALTER SYSTEM SET restore_command = 'cp /archive/%f %p';
ALTER SYSTEM SET recovery_target_time = '2024-01-15 14:30:00';

-- Alternative recovery targets:

-- Recover to specific transaction ID
-- recovery_target_xid = '12345'

-- Recover to specific named restore point
-- recovery_target_name = 'before_bad_update'

-- Recover to specific WAL location
-- recovery_target_lsn = '0/15D4E48'

-- Recover to specific time
-- recovery_target_time = '2024-01-15 14:30:00'

-- Recovery target action
-- recovery_target_action = 'pause'  (default, pause at target)
-- recovery_target_action = 'promote'  (become primary after recovery)
-- recovery_target_action = 'shutdown'  (shutdown after recovery)

-- 6. Start PostgreSQL (starts in recovery mode)
-- $ pg_ctl start

-- 7. Monitor recovery
-- $ tail -f /var/log/postgresql/postgresql-*.log
-- Watch for "recovery complete" or "paused"

-- 8. Check recovery status
SELECT pg_is_in_recovery();  -- true during recovery

-- 9. If paused, review data and promote
SELECT pg_wal_replay_resume();  -- Resume recovery
-- Or promote to primary
SELECT pg_promote();
```

### Creating Restore Points

```sql
-- Create named restore points for easier PITR

-- Create restore point before risky operation
SELECT pg_create_restore_point('before_major_update');

-- Perform operation
UPDATE products SET price = price * 1.1;

-- If operation successful, create success point
SELECT pg_create_restore_point('after_major_update');

-- Recovery to named restore point
-- recovery_target_name = 'before_major_update'

-- View current WAL location
SELECT pg_current_wal_lsn();

-- View WAL replay location (during recovery)
SELECT pg_last_wal_replay_lsn();
```

## Backup Tools

### Barman (Backup and Recovery Manager)

```sql
-- Barman: Enterprise-grade backup tool for PostgreSQL
-- Features: Incremental backups, compression, retention policies

-- Install Barman (on backup server)
-- $ sudo apt-get install barman

-- Configure Barman server (/etc/barman.conf)
-- [barman]
-- barman_home = /var/lib/barman
-- barman_user = barman
-- log_file = /var/log/barman/barman.log
-- 
-- [pg_server]
-- description = "PostgreSQL Production Server"
-- conninfo = host=pg.example.com user=barman dbname=postgres
-- backup_method = postgres
-- streaming_conninfo = host=pg.example.com user=streaming_barman
-- streaming_archiver = on
-- slot_name = barman
-- retention_policy = RECOVERY WINDOW OF 7 DAYS

-- Create replication slot on PostgreSQL
SELECT pg_create_physical_replication_slot('barman');

-- Barman commands:
-- $ barman list-server
-- $ barman check pg_server
-- $ barman backup pg_server
-- $ barman list-backup pg_server
-- $ barman recover pg_server latest /var/lib/postgresql/data
-- $ barman recover pg_server 20240115T120000 /var/lib/postgresql/data
```

### pgBackRest

```sql
-- pgBackRest: Advanced backup tool with compression, encryption
-- Features: Parallel backup/restore, incremental, delta restore

-- Install pgBackRest
-- $ sudo apt-get install pgbackrest

-- Configure pgBackRest (/etc/pgbackrest/pgbackrest.conf)
-- [global]
-- repo1-path=/backup/pgbackrest
-- repo1-retention-full=7
-- 
-- [mydb]
-- pg1-path=/var/lib/postgresql/data
-- pg1-port=5432

-- Create backup
-- $ pgbackrest --stanza=mydb backup

-- Backup types:
-- Full backup:
-- $ pgbackrest --stanza=mydb --type=full backup

-- Differential backup:
-- $ pgbackrest --stanza=mydb --type=diff backup

-- Incremental backup:
-- $ pgbackrest --stanza=mydb --type=incr backup

-- Restore:
-- $ pgbackrest --stanza=mydb restore

-- PITR restore:
-- $ pgbackrest --stanza=mydb --type=time "--target=2024-01-15 14:30:00" restore

-- Check backup info:
-- $ pgbackrest info
```

### WAL-G

```sql
-- WAL-G: Fast backup tool with cloud storage support
-- Features: Compression, encryption, S3/GCS/Azure storage

-- Install WAL-G
-- $ go get github.com/wal-g/wal-g

-- Configure environment variables
-- export WALG_S3_PREFIX=s3://my-bucket/wal-g
-- export AWS_REGION=us-east-1
-- export AWS_ACCESS_KEY_ID=...
-- export AWS_SECRET_ACCESS_KEY=...

-- Configure PostgreSQL for WAL-G
-- archive_command = 'wal-g wal-push %p'
-- restore_command = 'wal-g wal-fetch %f %p'

-- Create backup
-- $ wal-g backup-push /var/lib/postgresql/data

-- List backups
-- $ wal-g backup-list

-- Restore backup
-- $ wal-g backup-fetch /var/lib/postgresql/data LATEST

-- Delete old backups (retain last 7)
-- $ wal-g delete retain 7
```

## Recovery Procedures

### Recovery from Logical Backup

```sql
-- Scenario: Restore from pg_dump backup

-- 1. Create new database
CREATE DATABASE mydb_restored;

-- 2. Restore from SQL dump
-- $ psql mydb_restored < mydb_backup.sql

-- Or from custom format
-- $ pg_restore -d mydb_restored mydb_backup.dump

-- 3. Verify restoration
\c mydb_restored
SELECT count(*) FROM users;

-- 4. If successful, switch to restored database
-- Rename databases
ALTER DATABASE mydb RENAME TO mydb_old;
ALTER DATABASE mydb_restored RENAME TO mydb;

-- 5. Drop old database after verification
DROP DATABASE mydb_old;
```

### Recovery from Physical Backup

```sql
-- Scenario: Restore from pg_basebackup

-- 1. Stop PostgreSQL
-- $ pg_ctl stop

-- 2. Backup current data directory
-- $ mv /var/lib/postgresql/data /var/lib/postgresql/data.backup

-- 3. Extract base backup
-- $ mkdir /var/lib/postgresql/data
-- $ tar -xzf /backup/base.tar.gz -C /var/lib/postgresql/data

-- 4. If tar format with WAL
-- $ tar -xzf /backup/pg_wal.tar.gz -C /var/lib/postgresql/data/pg_wal

-- 5. Start PostgreSQL
-- $ pg_ctl start

-- 6. Verify restoration
-- $ psql -c "SELECT now(), pg_database_size('mydb')"
```

### Recovery from Corruption

```sql
-- Scenario: Database corruption detected

-- 1. Identify corruption
-- ERROR: invalid page header
-- ERROR: could not read block X in file "base/16384/12345"

-- 2. Try to extract data from corrupted table
CREATE TABLE users_backup AS SELECT * FROM users;
-- May fail if corruption is severe

-- 3. If extraction fails, restore from backup
-- Stop PostgreSQL
-- $ pg_ctl stop

-- Restore from latest backup
-- $ pg_restore -d mydb latest_backup.dump

-- 4. If partial recovery possible
-- Use zero_damaged_pages (DANGEROUS, data loss)
-- ALTER SYSTEM SET zero_damaged_pages = on;
-- Start PostgreSQL (will zero out corrupted pages)
-- Extract recoverable data
-- Restore from backup

-- 5. Verify data integrity after recovery
-- $ pg_dump mydb | pg_restore -d mydb_test
-- Run consistency checks
```

## High Availability

### Streaming Replication

```sql
-- Setup streaming replication for high availability

-- On Primary Server:

-- 1. Create replication user
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'strong_password';

-- 2. Configure pg_hba.conf (allow replication connections)
-- host replication replicator 10.0.1.0/24 scram-sha-256

-- 3. Configure postgresql.conf
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 5;
ALTER SYSTEM SET wal_keep_size = '1GB';
ALTER SYSTEM SET hot_standby = on;
-- Restart required
-- $ pg_ctl restart

-- On Standby Server:

-- 1. Create base backup from primary
-- $ pg_basebackup -h primary_host -U replicator -D /var/lib/postgresql/data -P -X stream

-- 2. Create standby.signal
-- $ touch /var/lib/postgresql/data/standby.signal

-- 3. Configure postgresql.conf (or postgresql.auto.conf)
ALTER SYSTEM SET primary_conninfo = 'host=primary_host port=5432 user=replicator password=strong_password';
ALTER SYSTEM SET hot_standby = on;

-- 4. Start standby
-- $ pg_ctl start

-- Monitor replication on primary
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state
FROM pg_stat_replication;

-- Monitor replication lag
SELECT 
    now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

### Failover and Switchover

```sql
-- Promote standby to primary (failover)

-- On Standby (becomes new primary):
-- 1. Promote standby
SELECT pg_promote();
-- Or use command line:
-- $ pg_ctl promote

-- 2. Verify promotion
SELECT pg_is_in_recovery();  -- Should be false

-- 3. Update application connection strings to new primary

-- Switchover (planned failover):

-- 1. Stop writes on old primary
-- Prevent new connections
ALTER SYSTEM SET default_transaction_read_only = on;
SELECT pg_reload_conf();

-- 2. Wait for standby to catch up
-- On Primary:
SELECT pg_current_wal_lsn();
-- On Standby:
SELECT pg_last_wal_replay_lsn();
-- Wait until they match

-- 3. Promote standby (above)

-- 4. Optionally reconfigure old primary as new standby
-- On old primary:
-- Create standby.signal
-- Configure primary_conninfo to point to new primary
-- Restart
```

## Disaster Recovery Planning

### DR Strategy

```sql
-- Comprehensive disaster recovery plan

-- 1. Recovery Time Objective (RTO): Max acceptable downtime
-- RTO = 4 hours (example)

-- 2. Recovery Point Objective (RPO): Max acceptable data loss
-- RPO = 15 minutes (example)

-- 3. Backup schedule matching RPO
-- Full backup: Daily
-- WAL archiving: Continuous (5 minute archive_timeout)

-- 4. Offsite backup storage
-- Replicate backups to different geographic location
-- $ rsync -av /backup/ remote:/backup/
-- Or use cloud storage (S3, GCS, Azure)

-- 5. Regular restore testing
-- Monthly: Test restore from backup
-- Quarterly: Full DR drill

-- 6. Documentation
-- Document recovery procedures
-- Maintain runbook with step-by-step instructions
-- Keep contact list for incident response

-- 7. Monitoring and alerting
-- Alert on backup failures
-- Alert on replication lag
-- Alert on archive failures

-- Example DR test checklist:
-- [ ] Stop production access (read-only mode)
-- [ ] Create snapshot of current state
-- [ ] Restore from backup to DR site
-- [ ] Verify data integrity
-- [ ] Test application connectivity
-- [ ] Measure recovery time (compare to RTO)
-- [ ] Document findings
-- [ ] Resume normal operations
```

## Backup Best Practices

### Backup Checklist

```sql
-- Comprehensive backup best practices

-- [ ] Multiple backup types
--   [ ] Daily logical backups (pg_dump)
--   [ ] Daily physical backups (pg_basebackup)
--   [ ] Continuous WAL archiving

-- [ ] Offsite storage
--   [ ] Replicate to remote location
--   [ ] Use cloud storage (S3, GCS)
--   [ ] Encrypt backups in transit

-- [ ] Backup encryption
--   [ ] Encrypt sensitive backups
--   [ ] Secure key management

-- [ ] Retention policy
--   [ ] Daily: 7 days
--   [ ] Weekly: 4 weeks
--   [ ] Monthly: 12 months
--   [ ] Annual: 7 years (compliance)

-- [ ] Regular testing
--   [ ] Monthly restore test
--   [ ] Verify backup integrity
--   [ ] Measure restore time

-- [ ] Monitoring
--   [ ] Alert on backup failures
--   [ ] Monitor backup size growth
--   [ ] Track backup duration

-- [ ] Documentation
--   [ ] Document backup procedures
--   [ ] Document restore procedures
--   [ ] Maintain DR runbook

-- [ ] Automation
--   [ ] Automate backup scheduling
--   [ ] Automate backup verification
--   [ ] Automate cleanup of old backups

-- Backup verification script
-- #!/bin/bash
-- BACKUP_FILE="/backup/mydb_$(date +%Y%m%d).dump"
-- TEST_DB="test_restore_$(date +%s)"
-- 
-- # Create test database
-- createdb $TEST_DB
-- 
-- # Restore backup
-- pg_restore -d $TEST_DB $BACKUP_FILE
-- 
-- # Verify data
-- ROW_COUNT=$(psql -t -d $TEST_DB -c "SELECT count(*) FROM users")
-- if [ $ROW_COUNT -gt 0 ]; then
--     echo "Backup verification successful: $ROW_COUNT users"
-- else
--     echo "Backup verification FAILED"
--     exit 1
-- fi
-- 
-- # Cleanup
-- dropdb $TEST_DB
```

## Summary

PostgreSQL backup and recovery requires:
- **Backup Strategy**: Logical, physical, and continuous archiving
- **Regular Backups**: Automated daily/weekly/monthly backups
- **WAL Archiving**: Continuous archiving for PITR
- **Offsite Storage**: Geographic redundancy
- **Testing**: Regular restore drills
- **Monitoring**: Alert on failures
- **Documentation**: Detailed runbooks
- **High Availability**: Streaming replication for redundancy

Proper backup strategy ensures data protection and business continuity.

## Next Steps

- Learn [High Availability and Replication](./36-high-availability-replication.md)
- Study [Monitoring and Logging](./38-monitoring-and-logging.md)
- Explore [Configuration and Tuning](./34-configuration-and-tuning.md)
- Practice [Disaster Recovery](./37-disaster-recovery.md)
