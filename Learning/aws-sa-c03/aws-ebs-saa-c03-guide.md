## Amazon EBS (Elastic Block Store) – AWS Solutions Architect (SAA-C03) Comprehensive Guide

> Fast reference + deep dive aligned to SAA-C03 exam domains (Design Resilient Architectures, High-Performing Architectures, Secure Applications, Cost Optimization).

---

### 1. What Is EBS?
Amazon EBS = network-attached, AZ-scoped, persistent block storage for EC2 instances. Think of it as a virtual SAN disk you can attach/detach to EC2. Provides low-latency block device semantics for databases, transactional workloads, filesystems (ext4, XFS, NTFS, etc.).

Key attributes:
- Persistent across instance stop/start (unlike Instance Store)
- Designed for 99.999% availability (service), durability depends on volume type (io2 higher than io1)
- Automatically replicated within its Availability Zone
- Snapshots to S3 (incremental, durable across AZs/Regions when copied)
- Encryption integrated with KMS

Scope & Limits (2025 status – always verify latest):
- Volume size: 1 GiB – 64 TiB (all current modern types)
- Attach per instance: Up to 40 volumes (soft limit; can increase)
- Max IOPS single volume: up to 64,000 (io1/io2), up to 256,000 with io2 Block Express on supported instance families
- Max throughput single volume: up to 1,000 MB/s (gp3), 4,000 MB/s (io2 Block Express)
- AZ-scoped: snapshots portable; volumes are not multi-AZ

---

### 2. Core Concepts
- Block vs Object: EBS presents raw block device, no API-level object semantics.
- Performance Dimensions: IOPS, throughput (MB/s), latency, burst mechanics.
- Provisioned vs Baseline: gp2 ties IOPS to size; gp3 decouples; io1/io2 let you explicitly provision.
- Consistency: Writes are synchronous within AZ replication.
- Boot Volumes: Most AMIs launch an EBS root volume (except instance store–backed legacy AMIs).

---

### 3. EBS Volume Types & Primary Use Cases

| Family | Type | Key Traits | Size Range | Max IOPS | Max Throughput | Typical Use Cases |
|--------|------|-----------|------------|----------|----------------|-------------------|
| General Purpose | gp3 | Decoupled perf; 3,000 baseline IOPS & 125 MB/s, can provision up to 16,000 IOPS / 1,000 MB/s | 1 GiB–64 TiB | 16,000 | 1,000 MB/s | Most workloads, system disks, small DBs, dev/test |
| General Purpose (legacy) | gp2 | 3 IOPS/GB baseline (min 100, max 16,000), burst to 3,000 for <1,000 GiB | 1 GiB–64 TiB | 16,000 | ~250-300 MB/s | Legacy existing deployments (migrate to gp3 for cost) |
| Provisioned IOPS | io1 | Provision IOPS (up to 64k), durability lower than io2, Multi-Attach supported | 4 GiB–64 TiB | 64,000 | 1,000 MB/s (depends) | Latency-sensitive DB (still prefer io2) |
| Provisioned IOPS | io2 | Higher durability (99.999%), better price-per-IOPS, Multi-Attach, consistent perf | 4 GiB–64 TiB | 64,000 (classic) | 1,000+ MB/s | Enterprise DB (Oracle, SQL Server), large prod systems |
| Provisioned IOPS (Block Express) | io2 Block Express | Next-gen architecture; up to 256,000 IOPS, 4,000 MB/s, sub-ms latency | 4 GiB–64 TiB | 256,000 | 4,000 MB/s | Extreme scale DB, SAP HANA, high consolidation |
| Throughput Optimized HDD | st1 | Magnetic HDD, optimized for large sequential throughput; cannot be boot | 125 GiB–64 TiB | ~500 IOPS burst | 500 MB/s (per TB scaling) | Big data, streaming logs, data warehouses |
| Cold HDD | sc1 | Lowest cost HDD; infrequent access; cannot be boot | 125 GiB–64 TiB | ~250 IOPS burst | ~250 MB/s (per TB scaling) | Cold data, infrequent scans |
| Previous-generation | standard (magnetic) | Legacy, lowest performance; avoid new use | 1 GiB–1 TiB (legacy) | Low | Low | Only for legacy systems |

Exam Pointers:
- Choose gp3 by default unless a strong reason (predictable perf, cheaper than gp2 for same perf).
- io2 vs io1: if question mentions higher durability, consistency, enterprise DB: prefer io2.
- st1 vs sc1: both sequential; st1 = active streaming; sc1 = cold archive.
- HDD types cannot be root / boot volumes.
- Multi-Attach only: io1 & io2 (NOT gp2/gp3/st1/sc1) and only in the same AZ.

---

### 4. Performance Mechanics & Key Numbers
General Purpose (gp2):
- Baseline IOPS = 3 × GiB size (minimum 100; max 16,000 at ~5,334 GiB)
- Burst bucket up to 3,000 IOPS for volumes < 1,000 GiB accumulating credits when under baseline.

General Purpose (gp3):
- Baseline included: 3,000 IOPS & 125 MB/s regardless of size
- Can provision (independently) up to 16,000 IOPS & 1,000 MB/s for additional cost.

Provisioned IOPS (io1/io2):
- Specify IOPS explicitly (ratio: up to 50:1 IOPS:GiB recommended for io1; io2 supports higher efficiency). You pay for provisioned even if unused.
- Block Express: Achieves extremely low latency and higher concurrency; only on supported Nitro instances (e.g., certain r5b, x2idn/x2iedn, m6in, c7gn families—verify current list on exam conceptually only).

Throughput vs IOPS:
- Small random reads/writes: optimize IOPS
- Large sequential scans: throughput (MB/s) dominates
- HDD volumes defined by throughput baseline (MB/s per TiB) + burst.

Monitoring Metrics (CloudWatch):
- VolumeIdleTime, BurstBalance (gp2, st1, sc1), VolumeReadOps, VolumeWriteOps, VolumeQueueLength, VolumeConsumedReadWriteOps (provisioned vs used), VolumeThroughputPercentage (provisioned IOPS types).

Latency Tuning Tips:
- Use Nitro-based instances (EBS-optimized by default with high network bandwidth)
- Align filesystem sector size (most modern OS auto-handle)
- Use RAID 0 across multiple EBS volumes to scale IOPS/throughput (trade-off: no redundancy) – replicate at higher layer or use snapshots.

---

### 5. Snapshots & Backup Strategy
- Point-in-time, incremental, stored in S3 (managed, not shown in your bucket).
- First snapshot = full baseline; subsequent store changed blocks only.
- Restoring a volume from snapshot is lazy: initial reads may incur higher latency until blocks are pre-warmed (READ them or use Fast Snapshot Restore).
- Fast Snapshot Restore (FSR): Pre-allocate performance in selected AZs -> no initialization penalty; cost per snapshot per AZ hour.
- Crash-Consistent: Single-volume snapshot without application flush may require journaling DB recovery. Use application quiesce scripts (e.g., `fsfreeze` on Linux) or database-native snapshot coordination.
- Multi-Volume Snapshots: Group snapshots across volumes for crash-consistent sets (e.g., DB + logs). Use tags & console feature.
- Cross-Region & Cross-Account Copy: Supports disaster recovery; encryption state can change (re-encrypt with a different CMK).
- AWS Backup Integration: Central policy-based scheduling, retention, copy to secondary Region.
- Recycle Bin: Define retention for deleted snapshots to protect against accidental deletion.

Exam Clues:
- “Need to recover quickly with full performance on restore” → Enable FSR.
- “Need automated lifecycle retention for snapshots” → Data Lifecycle Manager (DLM) or AWS Backup depending on multi-service scope.
- “Cross-account DR compliance” → Copy snapshots with CMK management.

---

### 6. Encryption & Security
- At-Rest Encryption: AES-256; handled transparently; includes data, metadata, snapshot, and all replicas.
- KMS CMK: Default AWS-managed key or customer-managed key (CMK) for granular control & audit.
- Default EBS Encryption Setting (per Region) enforces new volume encryption automatically.
- In-Transit: Data between EC2 & EBS uses dedicated secure channels on Nitro; (not user-managed TLS).
- Snapshot Copy Re-Encryption: Provide different CMK when copying.
- Cannot retroactively encrypt an unencrypted volume directly; must create encrypted snapshot (copy with encryption) -> new encrypted volume.
- Envelope encryption layering with OS-level encryption (LUKS/BitLocker) is supported (double encryption) but rarely needed unless regulatory.
- IAM Policies: Control `ec2:CreateVolume`, `ec2:CreateSnapshot`, `ec2:ModifyVolume`, `ec2:EnableFastSnapshotRestores` etc.

Security Scenario Patterns:
- “Need to ensure all volumes created are encrypted” → Enable EBS encryption by default + SCP in Organizations.
- “Forensics copy without instance access” → Create snapshot then share or copy (respecting encryption keys).

---

### 7. Elastic Volumes (Modification Without Detach)
- You can live-modify volume size, type, and (for gp3/io1/io2) provisioned performance.
- Most changes apply seamlessly; file system must be extended at OS level (e.g., `growpart`, `resize2fs`, `xfs_growfs`).
- Monitor modification progress with `DescribeVolumesModifications`.
- Downgrading performance (reducing IOPS) may have a cooldown.

Exam Cue: “Increase IOPS quickly without downtime” → Use Elastic Volumes (modify gp3 or io2). Avoid creating & migrating unless changing AZ.

---

### 8. Multi-Attach (Shared Block Device)
- Supported only for io1 & io2 (including Block Express) volumes.
- Attach the SAME volume to up to 16 Nitro-based instances in the SAME AZ.
- Use a cluster-aware filesystem (e.g., GFS2, OCFS2) or application-level locking. DO NOT use standard ext4/XFS concurrently unless read-only and safe.
- Not supported for boot volumes.

Exam Trap: If question suggests “Shared write access for low-latency database cluster at block layer” → Multi-Attach (io2) OR consider EFS / FSx (but those are managed filesystems). If it needs POSIX & simpler mgmt, prefer EFS; Multi-Attach: niche.

---

### 9. Instance Store vs EBS
| Attribute | EBS | Instance Store |
|-----------|-----|----------------|
| Persistence | Survives stop/start; deleted on explicit delete (unless DeleteOnTermination) | Ephemeral; lost on stop/terminate (except hibernation for RAM only) |
| Snapshot | Supported | Not supported |
| Performance | Consistent; network-based | Very high (NVMe local) |
| Use Cases | DBs, root disks, persistent app data | Caches, buffers, ephemeral processing, scratch |
| Cost Model | Pay per GB-month + provisioned perf | Included in instance price |

Exam Tip: “High-performance temporary scratch storage for distributed analytics” → Instance Store. “Need durability & snapshot backup” → EBS.

---

### 10. Cost Optimization Strategies
- Prefer gp3 over gp2 (lower cost for same or better baseline; tune only needed IOPS/throughput).
- Right-size volumes & periodically trim unused capacity (analyze with `df`, CloudWatch metrics, AWS Compute Optimizer recommendations when available).
- Use st1/sc1 only for large sequential throughput / cold storage to reduce cost.
- Schedule automated snapshot retention pruning (DLM / AWS Backup) to avoid runaway storage costs.
- Compress & deduplicate data at application layer (snapshots are block-level; unchanged compressed blocks reduce incremental growth).
- Use RAID 0 only when you need aggregated performance; be aware it may increase snapshot costs if more total GB.
- Delete orphaned snapshots after retention period (Recycle Bin policies ensure safety window).
- Consider Data Lifecycle Manager vs AWS Backup: If only EBS volumes, DLM cheaper/simpler; multi-service compliance -> AWS Backup.

Exam Clues: “Reduce cost without sacrificing performance for general workloads currently on gp2” → Migrate to gp3.

---

### 11. Advanced Features & Integrations
- Fast Snapshot Restore (FSR): Eliminate initialization latency.
- Data Lifecycle Manager (DLM): Policy-based snapshot & AMI automation.
- Recycle Bin: Retention window after deletion to protect against accidents.
- Amazon EBS Direct APIs: `ListChangedBlocks`, `GetSnapshotBlock` – efficient backup vendor integration.
- EBS Snapshot Archive (if supported in region): Move older snapshots to lower-cost archive tier (higher restore time) – exam may reference “archive snapshots to lower cost.”
- Snapshot Lock (emerging/region-specific) – WORM compliance (if GA; know conceptually for ransomware mitigation).
- EBS Local Snapshot (Outposts) – for hybrid edge (SAA might lightly touch hybrid; remember Outposts keeps data local unless you copy to Region).

---

### 12. Performance Tuning & Patterns
Tactics:
1. Use gp3 modernization: explicitly raise IOPS until queue length stabilizes (< 5 ideally for many workloads).
2. RAID 0 stripe identical volumes for linear scaling (IOPS & throughput). Snapshot each component volume (automation recommended).
3. Pre-warm restored volumes: run a sequential `dd` or `fio` read; OR rely on FSR.
4. Align instance EBS bandwidth: choose instance families with adequate `EBSOptimized` throughput (e.g., `r5b` for higher bandwidth, `c7i` with Nitro advantages). If CloudWatch shows throttling at instance network/EBS bandwidth, scale instance type first.
5. For write-heavy DB: consider io2 or io2 Block Express to reduce latency jitter.

What NOT To Do:
- Don’t oversubscribe IOPS beyond workload need: wasted spend.
- Don’t put shared-write uncoordinated FS on Multi-Attach.
- Don’t rely on `dd` zero fill for performance improvements (only pre-warms) — use FSR for production.

---

### 13. Monitoring & Metrics Cheat Sheet
CloudWatch Metrics (per-volume):
- VolumeReadOps / VolumeWriteOps – I/O counts
- VolumeReadBytes / VolumeWriteBytes – data transfer
- VolumeThroughputPercentage – actual vs provisioned (for PIOPS)
- VolumeConsumedReadWriteOps – consumed provisioned operations (billing insight)
- BurstBalance – remaining burst credits (gp2, st1, sc1)
- VolumeQueueLength – outstanding I/O requests (watch for sustained high value)
- VolumeIdleTime – low means busy volume; correlated with queue

Alarms:
- High `VolumeQueueLength` sustained → consider more IOPS or different volume type.
- Low `BurstBalance` trending to 0 on gp2/st1/sc1 → increase size or migrate to gp3 / provisioned IOPS.

Integrations:
- CloudTrail logs volume & snapshot API actions (security/audit).
- AWS Backup & DLM events in EventBridge.

---

### 13. AWS CLI Commands Reference

This section provides comprehensive AWS CLI commands for managing Amazon EBS volumes, snapshots, and related resources.

#### Prerequisites

```bash
# Ensure AWS CLI is installed and configured
aws --version
aws configure

# Set default region (optional)
export AWS_DEFAULT_REGION=us-east-1
```

#### Create EBS Volumes

```bash
# Create a gp3 volume (default, most cost-effective)
aws ec2 create-volume \
  --volume-type gp3 \
  --size 100 \
  --iops 3000 \
  --throughput 125 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=MyGP3Volume},{Key=Environment,Value=Production}]'

# Create a gp3 volume with custom IOPS and throughput
aws ec2 create-volume \
  --volume-type gp3 \
  --size 200 \
  --iops 10000 \
  --throughput 500 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=HighPerfGP3}]'

# Create a gp2 volume (legacy, for comparison)
aws ec2 create-volume \
  --volume-type gp2 \
  --size 100 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=MyGP2Volume}]'

# Create an io2 volume (high durability, provisioned IOPS)
aws ec2 create-volume \
  --volume-type io2 \
  --size 500 \
  --iops 32000 \
  --availability-zone us-east-1a \
  --multi-attach-enabled \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=EnterpriseDB-IO2},{Key=Application,Value=Database}]'

# Create an io1 volume (legacy provisioned IOPS)
aws ec2 create-volume \
  --volume-type io1 \
  --size 400 \
  --iops 20000 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=MyIO1Volume}]'

# Create an st1 volume (throughput-optimized HDD)
aws ec2 create-volume \
  --volume-type st1 \
  --size 500 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=BigDataST1},{Key=Purpose,Value=Analytics}]'

# Create an sc1 volume (cold HDD, lowest cost)
aws ec2 create-volume \
  --volume-type sc1 \
  --size 500 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=ArchiveSC1},{Key=Purpose,Value=ColdStorage}]'

# Create an encrypted volume with default KMS key
aws ec2 create-volume \
  --volume-type gp3 \
  --size 100 \
  --availability-zone us-east-1a \
  --encrypted \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=EncryptedVolume}]'

# Create an encrypted volume with custom KMS key
aws ec2 create-volume \
  --volume-type gp3 \
  --size 100 \
  --availability-zone us-east-1a \
  --encrypted \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=CustomKMSVolume}]'

# Create volume from snapshot
aws ec2 create-volume \
  --snapshot-id snap-0123456789abcdef0 \
  --volume-type gp3 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=RestoredVolume}]'
```

#### List and Describe Volumes

```bash
# List all volumes
aws ec2 describe-volumes

# Describe a specific volume
aws ec2 describe-volumes \
  --volume-ids vol-0123456789abcdef0

# List volumes by tag
aws ec2 describe-volumes \
  --filters "Name=tag:Environment,Values=Production"

# List volumes in a specific availability zone
aws ec2 describe-volumes \
  --filters "Name=availability-zone,Values=us-east-1a"

# List available (unattached) volumes
aws ec2 describe-volumes \
  --filters "Name=status,Values=available"

# Get volume details in table format
aws ec2 describe-volumes \
  --query 'Volumes[*].{ID:VolumeId,Type:VolumeType,Size:Size,State:State,AZ:AvailabilityZone}' \
  --output table

# List volumes attached to a specific instance
aws ec2 describe-volumes \
  --filters "Name=attachment.instance-id,Values=i-0123456789abcdef0"

# Check volume encryption status
aws ec2 describe-volumes \
  --volume-ids vol-0123456789abcdef0 \
  --query 'Volumes[0].{Encrypted:Encrypted,KmsKeyId:KmsKeyId}' \
  --output table
```

#### Attach and Detach Volumes

```bash
# Attach a volume to an EC2 instance
aws ec2 attach-volume \
  --volume-id vol-0123456789abcdef0 \
  --instance-id i-0123456789abcdef0 \
  --device /dev/sdf

# Attach with specific device name (NVMe instances)
aws ec2 attach-volume \
  --volume-id vol-0123456789abcdef0 \
  --instance-id i-0123456789abcdef0 \
  --device /dev/nvme1n1

# Detach a volume
aws ec2 detach-volume \
  --volume-id vol-0123456789abcdef0

# Force detach (use with caution)
aws ec2 detach-volume \
  --volume-id vol-0123456789abcdef0 \
  --force

# Check attachment state
aws ec2 describe-volumes \
  --volume-ids vol-0123456789abcdef0 \
  --query 'Volumes[0].Attachments[0].{State:State,Instance:InstanceId,Device:Device}' \
  --output table
```

#### Create Snapshots

```bash
# Create a snapshot of a volume
aws ec2 create-snapshot \
  --volume-id vol-0123456789abcdef0 \
  --description "Daily backup $(date +%Y-%m-%d)" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=DailyBackup},{Key=Date,Value='$(date +%Y-%m-%d)'}]'

# Create snapshot with custom tags
aws ec2 create-snapshot \
  --volume-id vol-0123456789abcdef0 \
  --description "Production database backup" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=ProdDBSnapshot},{Key=Type,Value=Database},{Key=Retention,Value=30days}]'

# Create snapshots of multiple volumes (crash-consistent set)
VOLUME_IDS=("vol-0123456789abcdef0" "vol-0123456789abcdef1" "vol-0123456789abcdef2")
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

for vol_id in "${VOLUME_IDS[@]}"; do
  aws ec2 create-snapshot \
    --volume-id $vol_id \
    --description "Multi-volume backup $TIMESTAMP" \
    --tag-specifications 'ResourceType=snapshot,Tags=[{Key=SnapshotGroup,Value='$TIMESTAMP'}]'
done

# List snapshots
aws ec2 describe-snapshots \
  --owner-ids self

# Describe a specific snapshot
aws ec2 describe-snapshots \
  --snapshot-ids snap-0123456789abcdef0

# Check snapshot progress
aws ec2 describe-snapshots \
  --snapshot-ids snap-0123456789abcdef0 \
  --query 'Snapshots[0].{State:State,Progress:Progress}' \
  --output table

# List snapshots by tag
aws ec2 describe-snapshots \
  --owner-ids self \
  --filters "Name=tag:Type,Values=Database"
```

#### Copy Snapshots

```bash
# Copy snapshot to another region
aws ec2 copy-snapshot \
  --region us-west-2 \
  --source-region us-east-1 \
  --source-snapshot-id snap-0123456789abcdef0 \
  --description "DR copy from us-east-1" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=DRSnapshot},{Key=SourceRegion,Value=us-east-1}]'

# Copy snapshot with encryption
aws ec2 copy-snapshot \
  --region us-west-2 \
  --source-region us-east-1 \
  --source-snapshot-id snap-0123456789abcdef0 \
  --encrypted \
  --kms-key-id arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --description "Encrypted DR copy"

# Copy snapshot to different account (requires sharing first)
# First, modify snapshot permissions in source account
aws ec2 modify-snapshot-attribute \
  --snapshot-id snap-0123456789abcdef0 \
  --attribute createVolumePermission \
  --operation-type add \
  --user-ids 123456789012

# Then, in target account, copy the snapshot
aws ec2 copy-snapshot \
  --source-region us-east-1 \
  --source-snapshot-id snap-0123456789abcdef0 \
  --description "Cross-account copy"
```

#### Create AMI from Snapshot

```bash
# Create AMI from EBS snapshot
aws ec2 register-image \
  --name "MyCustomAMI-$(date +%Y%m%d)" \
  --description "Custom AMI created from snapshot" \
  --architecture x86_64 \
  --root-device-name /dev/xvda \
  --block-device-mappings \
    DeviceName=/dev/xvda,Ebs={SnapshotId=snap-0123456789abcdef0,VolumeType=gp3,DeleteOnTermination=true} \
    DeviceName=/dev/sdf,Ebs={SnapshotId=snap-0123456789abcdef1,VolumeType=gp3,VolumeSize=100} \
  --virtualization-type hvm \
  --ena-support \
  --sriov-net-support simple

# Create AMI with multiple volumes
aws ec2 register-image \
  --name "MultiVolumeAMI" \
  --architecture x86_64 \
  --root-device-name /dev/xvda \
  --block-device-mappings \
    '[{"DeviceName":"/dev/xvda","Ebs":{"SnapshotId":"snap-root123","VolumeType":"gp3"}},{"DeviceName":"/dev/sdf","Ebs":{"SnapshotId":"snap-data123","VolumeType":"io2","Iops":10000}}]'

# List AMIs
aws ec2 describe-images \
  --owners self

# Deregister AMI
aws ec2 deregister-image \
  --image-id ami-0123456789abcdef0
```

#### Fast Snapshot Restore (FSR)

```bash
# Enable Fast Snapshot Restore for a snapshot
aws ec2 enable-fast-snapshot-restores \
  --availability-zones us-east-1a us-east-1b \
  --source-snapshot-ids snap-0123456789abcdef0

# Enable FSR in multiple AZs
aws ec2 enable-fast-snapshot-restores \
  --availability-zones us-east-1a us-east-1b us-east-1c \
  --source-snapshot-ids snap-0123456789abcdef0 snap-0123456789abcdef1

# Describe FSR status
aws ec2 describe-fast-snapshot-restores \
  --filters "Name=snapshot-id,Values=snap-0123456789abcdef0"

# Disable Fast Snapshot Restore
aws ec2 disable-fast-snapshot-restores \
  --availability-zones us-east-1a us-east-1b \
  --source-snapshot-ids snap-0123456789abcdef0

# Check FSR costs and status
aws ec2 describe-fast-snapshot-restores \
  --query 'FastSnapshotRestores[*].{Snapshot:SnapshotId,AZ:AvailabilityZone,State:State}' \
  --output table
```

#### EBS Encryption

```bash
# Enable EBS encryption by default for the account
aws ec2 enable-ebs-encryption-by-default

# Check if encryption by default is enabled
aws ec2 get-ebs-encryption-by-default

# Set default KMS key for EBS encryption
aws ec2 modify-ebs-default-kms-key-id \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Get default KMS key
aws ec2 get-ebs-default-kms-key-id

# Disable EBS encryption by default
aws ec2 disable-ebs-encryption-by-default

# Create encrypted snapshot from unencrypted volume
# Step 1: Create snapshot of unencrypted volume
UNENCRYPTED_SNAP=$(aws ec2 create-snapshot \
  --volume-id vol-unencrypted123 \
  --description "Temp snapshot for encryption" \
  --query 'SnapshotId' \
  --output text)

# Step 2: Wait for snapshot completion
aws ec2 wait snapshot-completed \
  --snapshot-ids $UNENCRYPTED_SNAP

# Step 3: Copy snapshot with encryption
ENCRYPTED_SNAP=$(aws ec2 copy-snapshot \
  --source-region us-east-1 \
  --source-snapshot-id $UNENCRYPTED_SNAP \
  --encrypted \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
  --description "Encrypted copy" \
  --query 'SnapshotId' \
  --output text)

# Step 4: Create encrypted volume from encrypted snapshot
aws ec2 create-volume \
  --snapshot-id $ENCRYPTED_SNAP \
  --availability-zone us-east-1a \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=EncryptedVolume}]'
```

#### Volume Modifications (Elastic Volumes)

```bash
# Modify volume size
aws ec2 modify-volume \
  --volume-id vol-0123456789abcdef0 \
  --size 200

# Modify volume type from gp2 to gp3
aws ec2 modify-volume \
  --volume-id vol-0123456789abcdef0 \
  --volume-type gp3

# Modify gp3 IOPS and throughput
aws ec2 modify-volume \
  --volume-id vol-0123456789abcdef0 \
  --iops 10000 \
  --throughput 500

# Modify io2 volume IOPS
aws ec2 modify-volume \
  --volume-id vol-0123456789abcdef0 \
  --iops 50000

# Comprehensive modification (size, type, IOPS, throughput)
aws ec2 modify-volume \
  --volume-id vol-0123456789abcdef0 \
  --size 500 \
  --volume-type io2 \
  --iops 40000

# Check modification state
aws ec2 describe-volumes-modifications \
  --volume-ids vol-0123456789abcdef0

# Monitor all ongoing modifications
aws ec2 describe-volumes-modifications \
  --filters "Name=modification-state,Values=modifying,optimizing" \
  --query 'VolumesModifications[*].{Volume:VolumeId,State:ModificationState,Progress:Progress}' \
  --output table

# Wait for modification to complete (if using in scripts)
while true; do
  STATUS=$(aws ec2 describe-volumes-modifications \
    --volume-ids vol-0123456789abcdef0 \
    --query 'VolumesModifications[0].ModificationState' \
    --output text)
  if [ "$STATUS" == "completed" ]; then
    echo "Volume modification completed"
    break
  fi
  echo "Current state: $STATUS, waiting..."
  sleep 30
done
```

#### Snapshot Lifecycle Policies (Data Lifecycle Manager)

```bash
# Create a lifecycle policy for daily snapshots
cat > dlm-policy.json <<EOF
{
  "ExecutionRoleArn": "arn:aws:iam::123456789012:role/AWSDataLifecycleManagerDefaultRole",
  "Description": "Daily snapshot policy with 7-day retention",
  "State": "ENABLED",
  "PolicyDetails": {
    "PolicyType": "EBS_SNAPSHOT_MANAGEMENT",
    "ResourceTypes": ["VOLUME"],
    "TargetTags": [
      {
        "Key": "Backup",
        "Value": "Daily"
      }
    ],
    "Schedules": [
      {
        "Name": "DailySnapshot",
        "CopyTags": true,
        "TagsToAdd": [
          {
            "Key": "SnapshotType",
            "Value": "DLMAutomatic"
          }
        ],
        "CreateRule": {
          "Interval": 24,
          "IntervalUnit": "HOURS",
          "Times": ["03:00"]
        },
        "RetainRule": {
          "Count": 7
        }
      }
    ]
  }
}
EOF

aws dlm create-lifecycle-policy \
  --cli-input-json file://dlm-policy.json

# Create weekly snapshot policy with cross-region copy
cat > dlm-weekly-policy.json <<EOF
{
  "ExecutionRoleArn": "arn:aws:iam::123456789012:role/AWSDataLifecycleManagerDefaultRole",
  "Description": "Weekly snapshots with DR copy",
  "State": "ENABLED",
  "PolicyDetails": {
    "PolicyType": "EBS_SNAPSHOT_MANAGEMENT",
    "ResourceTypes": ["VOLUME"],
    "TargetTags": [
      {
        "Key": "Backup",
        "Value": "Weekly"
      }
    ],
    "Schedules": [
      {
        "Name": "WeeklySnapshot",
        "CopyTags": true,
        "CreateRule": {
          "Interval": 7,
          "IntervalUnit": "DAYS",
          "Times": ["02:00"]
        },
        "RetainRule": {
          "Count": 4
        },
        "CrossRegionCopyRules": [
          {
            "TargetRegion": "us-west-2",
            "Encrypted": true,
            "RetainRule": {
              "Interval": 30,
              "IntervalUnit": "DAYS"
            }
          }
        ]
      }
    ]
  }
}
EOF

aws dlm create-lifecycle-policy \
  --cli-input-json file://dlm-weekly-policy.json

# List all lifecycle policies
aws dlm get-lifecycle-policies

# Describe a specific policy
aws dlm get-lifecycle-policy \
  --policy-id policy-0123456789abcdef0

# Update a lifecycle policy
aws dlm update-lifecycle-policy \
  --policy-id policy-0123456789abcdef0 \
  --state DISABLED

# Delete a lifecycle policy
aws dlm delete-lifecycle-policy \
  --policy-id policy-0123456789abcdef0
```

#### Tags Management

```bash
# Add tags to a volume
aws ec2 create-tags \
  --resources vol-0123456789abcdef0 \
  --tags Key=Environment,Value=Production Key=Application,Value=Database Key=Owner,Value=TeamA

# Add tags to multiple volumes
aws ec2 create-tags \
  --resources vol-0123456789abcdef0 vol-0123456789abcdef1 vol-0123456789abcdef2 \
  --tags Key=Project,Value=WebApp Key=CostCenter,Value=Engineering

# Add tags to snapshots
aws ec2 create-tags \
  --resources snap-0123456789abcdef0 \
  --tags Key=Retention,Value=30days Key=Type,Value=Backup

# List tags for a volume
aws ec2 describe-tags \
  --filters "Name=resource-id,Values=vol-0123456789abcdef0"

# Remove tags from a volume
aws ec2 delete-tags \
  --resources vol-0123456789abcdef0 \
  --tags Key=OldTag

# Find all volumes with specific tag
aws ec2 describe-volumes \
  --filters "Name=tag:Environment,Values=Production" \
  --query 'Volumes[*].{ID:VolumeId,Type:VolumeType,Size:Size}' \
  --output table
```

#### Delete Volumes and Snapshots

```bash
# Delete a volume (must be detached first)
aws ec2 delete-volume \
  --volume-id vol-0123456789abcdef0

# Delete a snapshot
aws ec2 delete-snapshot \
  --snapshot-id snap-0123456789abcdef0

# Cleanup script: Delete all available (unattached) volumes in a region
for vol_id in $(aws ec2 describe-volumes \
  --filters "Name=status,Values=available" \
  --query "Volumes[*].VolumeId" \
  --output text); do
  echo "Deleting volume: $vol_id"
  aws ec2 delete-volume --volume-id $vol_id
done

# Cleanup script: Delete old snapshots (older than 90 days)
CUTOFF_DATE=$(date -u -d '90 days ago' +%Y-%m-%d)

for snap_id in $(aws ec2 describe-snapshots \
  --owner-ids self \
  --query "Snapshots[?StartTime<'$CUTOFF_DATE'].SnapshotId" \
  --output text); do
  echo "Deleting old snapshot: $snap_id"
  aws ec2 delete-snapshot --snapshot-id $snap_id
done
```

#### Monitoring and CloudWatch Metrics

```bash
# Get volume IOPS metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EBS \
  --metric-name VolumeReadOps \
  --dimensions Name=VolumeId,Value=vol-0123456789abcdef0 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --output table

# Get burst balance for gp2/st1/sc1 volumes
aws cloudwatch get-metric-statistics \
  --namespace AWS/EBS \
  --metric-name BurstBalance \
  --dimensions Name=VolumeId,Value=vol-0123456789abcdef0 \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  --output table

# Create CloudWatch alarm for low burst balance
aws cloudwatch put-metric-alarm \
  --alarm-name "EBS-LowBurstBalance-vol-0123456789abcdef0" \
  --alarm-description "Alert when burst balance drops below 20%" \
  --metric-name BurstBalance \
  --namespace AWS/EBS \
  --statistic Average \
  --period 300 \
  --threshold 20 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=VolumeId,Value=vol-0123456789abcdef0

# Create alarm for high volume queue length
aws cloudwatch put-metric-alarm \
  --alarm-name "EBS-HighQueueLength-vol-0123456789abcdef0" \
  --metric-name VolumeQueueLength \
  --namespace AWS/EBS \
  --statistic Average \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 3 \
  --dimensions Name=VolumeId,Value=vol-0123456789abcdef0
```

#### Automation Scripts

```bash
#!/bin/bash
# Comprehensive EBS backup script with error handling

VOLUME_ID="vol-0123456789abcdef0"
RETENTION_DAYS=7
REGION="us-east-1"

echo "Starting backup for volume: $VOLUME_ID"

# Create snapshot
SNAPSHOT_ID=$(aws ec2 create-snapshot \
  --region $REGION \
  --volume-id $VOLUME_ID \
  --description "Automated backup $(date +%Y-%m-%d-%H-%M)" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Type,Value=AutomatedBackup},{Key=Date,Value='$(date +%Y-%m-%d)'}]' \
  --query 'SnapshotId' \
  --output text)

if [ $? -eq 0 ]; then
  echo "Snapshot created: $SNAPSHOT_ID"
else
  echo "Failed to create snapshot"
  exit 1
fi

# Wait for snapshot to complete
echo "Waiting for snapshot to complete..."
aws ec2 wait snapshot-completed \
  --region $REGION \
  --snapshot-ids $SNAPSHOT_ID

echo "Snapshot completed successfully"

# Delete old snapshots
CUTOFF_DATE=$(date -u -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
echo "Deleting snapshots older than $CUTOFF_DATE"

OLD_SNAPSHOTS=$(aws ec2 describe-snapshots \
  --region $REGION \
  --owner-ids self \
  --filters \
    "Name=volume-id,Values=$VOLUME_ID" \
    "Name=tag:Type,Values=AutomatedBackup" \
  --query "Snapshots[?StartTime<'$CUTOFF_DATE'].SnapshotId" \
  --output text)

for snap in $OLD_SNAPSHOTS; do
  echo "Deleting snapshot: $snap"
  aws ec2 delete-snapshot --region $REGION --snapshot-id $snap
done

echo "Backup process completed"
```

```bash
#!/bin/bash
# Script to migrate from gp2 to gp3 and optimize costs

REGION="us-east-1"

echo "Finding all gp2 volumes..."
GP2_VOLUMES=$(aws ec2 describe-volumes \
  --region $REGION \
  --filters "Name=volume-type,Values=gp2" \
  --query "Volumes[*].VolumeId" \
  --output text)

for vol_id in $GP2_VOLUMES; do
  echo "Processing volume: $vol_id"
  
  # Get current size
  SIZE=$(aws ec2 describe-volumes \
    --region $REGION \
    --volume-ids $vol_id \
    --query "Volumes[0].Size" \
    --output text)
  
  # Calculate current gp2 baseline IOPS (3 IOPS per GB, min 100, max 16000)
  BASELINE_IOPS=$((SIZE * 3))
  if [ $BASELINE_IOPS -lt 100 ]; then
    BASELINE_IOPS=100
  elif [ $BASELINE_IOPS -gt 16000 ]; then
    BASELINE_IOPS=16000
  fi
  
  # Migrate to gp3 with baseline 3000 IOPS (free)
  echo "Migrating $vol_id from gp2 to gp3 (Size: ${SIZE}GB, Old IOPS: ${BASELINE_IOPS})"  
  
  aws ec2 modify-volume \
    --region $REGION \
    --volume-id $vol_id \
    --volume-type gp3
  
  echo "Migration initiated for $vol_id"
  echo "---"
done

echo "Migration script completed"
```

---

### 14. Architecture & Design Scenario Patterns
Scenario 1: “Need low-latency, highly durable storage for mission-critical OLTP database.” → io2 (or io2 Block Express if extreme scale). Add Multi-AZ DB replication at application/DB layer (EBS itself is AZ-scoped).

Scenario 2: “Large analytics application doing sequential scans of >100 TB raw logs daily.” → st1 (throughput optimized HDD). If logs age out, move cold to S3 Glacier.

Scenario 3: “General web application with moderate RDS-style I/O on EC2-managed DB and budget concerns.” → gp3 tuned to required IOPS.

Scenario 4: “Need to share a block device between multiple instances for clustered filesystem.” → io2 Multi-Attach (BUT evaluate EFS/FSx first depending on semantics). Provide cluster-aware FS.

Scenario 5: “Disaster recovery requirement: copy backups to another Region & different account.” → Snapshot copy cross-account+region with KMS re-encryption + lifecycle policies.

Scenario 6: “Restore from snapshot must have full performance immediately.” → Enable Fast Snapshot Restore in target AZ(s) before provisioning volume.

Scenario 7: “Must protect against accidental deletion of snapshots.” → Configure Recycle Bin retention + IAM/SCP restrictions.

Scenario 8: “Need to quickly increase database storage & IOPS without downtime.” → Elastic Volumes modify size & IOPS (gp3 or io2) + grow filesystem.

Scenario 9: “Large ephemeral scratch space for parallel transcoding, cost sensitive.” → Instance Store (NVMe) + EBS only for metadata persistence.

Scenario 10: “Need immutable backups for compliance (WORM).” → Use Snapshot Lock (if GA) or external backup to S3 with Object Lock.

---

### 15. Exam Tips & Common Traps
1. gp3 vs gp2: If cost + flexibility mentioned → gp3.
2. io2 vs io1: Higher durability & consistent performance → io2.
3. Multi-Attach only io1/io2; same AZ; not for boot.
4. Snapshot restore slow initial performance → pre-warm or FSR.
5. Cross-region DR requires snapshot copy (volumes are AZ-bound); cannot “attach” cross-AZ.
6. Encryption cannot be toggled directly; create encrypted copy snapshot → new volume.
7. HDD (st1/sc1) cannot be boot volumes; only sequential. If random small I/O → DO NOT pick st1/sc1.
8. Need file-sharing semantics? Choose EFS/FSx unless block-level requirement explicitly.
9. “Improve performance by increasing size” – works for gp2 (more baseline IOPS) but not needed for gp3 (decoupled) or provisioned types.
10. RAID 0 to scale; remember single volume limits for IOPS/throughput.

High-Frequency Numbers (memorize):
- Size range: 1 GiB – 64 TiB
- gp3 baseline: 3,000 IOPS / 125 MB/s; max 16,000 IOPS / 1,000 MB/s
- gp2 baseline: 3 IOPS/GB (min 100; max 16,000) & burst 3,000 IOPS
- io1/io2: up to 64,000 IOPS (classic), Block Express up to 256,000 & 4,000 MB/s
- Volume types enabling Multi-Attach: io1 & io2 only
- FSR: pay-per-snapshot-per-AZ; eliminates initialization penalty

---

### 16. Quick Decision Matrix (Cheat Sheet)
| Need | Choose |
|------|--------|
| Default balanced cost/perf | gp3 |
| Legacy already on gp2 | Migrate to gp3 to save cost |
| High random IOPS, durability | io2 (Block Express if extreme) |
| Shared block device writes | io2 / io1 Multi-Attach (cluster FS) |
| Large sequential streaming | st1 |
| Cold infrequently accessed large data | sc1 |
| Temporary very high-performance scratch | Instance Store |
| Immediate full perf after restore | FSR enabled snapshot |
| Automated snapshot retention | DLM (EBS-focused) / AWS Backup (multi-service) |
| Cross-account & encryption control | Snapshot copy w/ CMK |

---

### 17. Migration & Modernization Notes
- gp2 → gp3: Use ModifyVolume; no downtime; then optionally decrease size? (Cannot shrink; need new smaller volume + data copy.)
- io1 → io2: ModifyVolume supported; reduces cost / increases durability.
- Consolidate multiple gp2 volumes (RAID 0) into single high-perf gp3 with provisioned IOPS if simpler management preferred (ensure perf parity).

---

### 18. Operational Playbook Examples
Increase gp3 IOPS:
1. `ModifyVolume` set `Iops` & optionally `Throughput`.
2. Monitor state = `optimizing` then `completed`.
3. Validate CloudWatch `VolumeQueueLength` improves.

Expand Filesystem (Linux ext4 example):
1. `lsblk` confirm new size
2. `growpart /dev/nvme0n1 1` (if partitioned)
3. `resize2fs /dev/nvme0n1p1`

Create Encrypted Copy of Unencrypted Volume:
1. Snapshot unencrypted volume
2. Copy snapshot with encryption + CMK
3. Create new encrypted volume & swap

---

### 19. Practice Question Samples
Q: An analytics team needs 200 TB of log data scanned daily, sequential reads, cost sensitive. Which volume? → st1.

Q: Startup wants to cut storage cost: many gp2 volumes at 500 GiB each ~1,500 IOPS baseline but only consuming 800 IOPS. Migration path? → Modify to gp3 and provision just needed IOPS.

Q: After restoring a volume from snapshot, initial queries are slow. Solution? → Enable Fast Snapshot Restore (or pre-warm by reading all blocks) – FSR is best.

Q: Need to attach same storage to up to 10 EC2 instances to coordinate low-latency database writes. Options? → io2 Multi-Attach (with cluster-aware FS) or reconsider architecture (maybe Amazon RDS / Aurora / EFS). For exam: io2 Multi-Attach.

Q: Compliance requires encrypted backups in another account & region. Steps? → Copy snapshot specifying destination Region & re-encrypt with destination account CMK.

Q: Want to avoid accidental snapshot deletion while still pruning after 30 days. Approach? → Recycle Bin with 7-day retention + DLM for scheduled creation + retention rules.

---

### 20. Final Exam-Day Rapid Recall
- gp3 baseline 3k/125 – independent scaling.
- gp2 ties IOPS to size (3 per GiB).
- io2 > io1 (durability & price/IOPS); Block Express for extreme.
- st1/sequential active; sc1/sequential cold.
- Snapshots incremental; FSR removes warm-up.
- Elastic Volumes live modify.
- Multi-Attach only io1/io2 same AZ up to 16 instances.
- Encryption by default recommended; copy snapshot to change encryption.
- Instance Store ephemeral – use for cache / scratch only.

---

### 21. References (Review Outside Exam)
- AWS EBS Product Page & FAQs
- EBS Volume Type docs (performance tables)
- EBS Snapshots, DLM, FSR, Recycle Bin docs
- AWS Storage Lens / Backup service integration

---

Disclaimer: AWS continuously evolves. Re-validate numerical limits (IOPS, throughput, sizes, supported instance families) just before the exam using official documentation.

End of Guide.
