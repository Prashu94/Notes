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
