# Cloud Storage, file, backup, and transfer

ACE 2.2, 3.4, 4.4. PCA 1.3 and 2.2.

## Object, file, or block

| Model | Product | Not this product |
| --- | --- | --- |
| Object (blobs, data lake, static site, backup dumps) | Cloud Storage | A disk |
| File (NFS or SMB mount, lift-and-shift file server) | Filestore, NetApp Volumes | Cloud Storage, unless the app speaks the object API |
| HPC / training scratch file system | Managed Lustre | Filestore Basic, if the stem says Lustre or extreme throughput |
| Block disk on a VM | Persistent Disk, Hyperdisk, Local SSD | Cloud Storage |

## Storage classes

| Class | Read pattern | Minimum duration | Retrieval fee |
| --- | --- | --- | --- |
| Standard | Often | None | None |
| Nearline | About monthly | 30 days | Yes |
| Coldline | About quarterly | 90 days | Yes |
| Archive | About yearly. Still millisecond access, not tape delay. | 365 days | Yes |
| Autoclass | Unknown or changing | Moves for you, including a faster “hot” path | You pay for the transitions the feature defines |

Location: region (one region), dual-region (two specific regions, for HA and residency), multi-region (`us`, `eu`, `asia`). Multi-region is not “every zone”. It is a location type with geo-redundancy inside that area.

**Uniform bucket-level access** turns off object ACLs and uses IAM only. Organization policy can force it. That is the exam answer. Object ACLs are legacy.

**Public access prevention** blocks `allUsers`. Use it.

```bash
gcloud storage buckets create gs://$PROJECT_ID-lake \
  --location="$REGION" \
  --uniform-bucket-level-access \
  --public-access-prevention

gcloud storage buckets update gs://$PROJECT_ID-lake --default-storage-class=STANDARD

# Lifecycle: standard to coldline after 90 days, delete after 365
cat > lifecycle.json << 'EOF'
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 90, "matchesStorageClass": ["STANDARD", "NEARLINE"]}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    }
  ]
}
EOF
gcloud storage buckets update gs://$PROJECT_ID-lake --lifecycle-file=lifecycle.json

# Versioning protects overwrite and delete
gcloud storage buckets update gs://$PROJECT_ID-lake --versioning

# Retention lock (compliance): objects cannot be deleted until the period ends
gcloud storage buckets update gs://$PROJECT_ID-lake --retention-period=31557600

gcloud storage ls gs://$PROJECT_ID-lake
gcloud storage cp report.csv gs://$PROJECT_ID-lake/in/report.csv
```

IAM roles: `roles/storage.objectViewer` reads objects. `roles/storage.objectAdmin` creates and deletes. `roles/storage.admin` administers the bucket. Grant on the bucket, not the project, when you can.

**Signed URLs** give time-limited access to someone who should not be in IAM. **HMAC keys** are for S3-compatible clients. Prefer IAM or signed URLs.

**Customer-managed encryption keys** use Cloud KMS. Google-managed encryption is already on. Customer-supplied keys mean you send the key material on each call. CMEK is the usual PCA answer.

**Requester pays** puts egress on the reader. Rare.

**Object holds** and **bucket lock** are the compliance “cannot delete” controls. A lifecycle delete will not beat a retention policy.

**Autoclass** is the answer when access frequency is unknown and you do not want to hand-write lifecycle class changes. A known archive policy is still a lifecycle rule.

## Load and transfer

ACE 3.4: command-line upload, load from Cloud Storage, Storage Transfer Service.

| Method | When |
| --- | --- |
| `gcloud storage cp` / `gsutil cp` | You have the files and a network |
| Storage Transfer Service | Another bucket, S3, Azure, or an HTTP list. Scheduled, retries, checksums. |
| Transfer Appliance | Too big for the network. A physical appliance. Offline. |
| `gcloud storage rsync` | Keep a directory in sync |
| BigQuery load job | Files already in Cloud Storage, destination is a table |
| `bq load` | The command for that load |

```bash
gcloud transfer jobs create \
  s3://source-bucket gs://$PROJECT_ID-lake/s3 \
  --source-creds-file=aws.json

gcloud transfer jobs list
gcloud transfer operations list
```

Event-driven processing of new objects is Eventarc or a Pub/Sub notification on the bucket, not a cron listing the bucket.

```bash
gcloud storage buckets notifications create gs://$PROJECT_ID-lake \
  --topic=projects/$PROJECT_ID/topics/object-events
```

## Filestore and NetApp Volumes

```bash
gcloud filestore instances create nfs1 \
  --zone="$ZONE" \
  --tier=BASIC_HDD \
  --file-share=name=share1,capacity=1TB \
  --network=name=prod

# ENTERPRISE and REGIONAL tiers exist for HA. BASIC is zonal.
gcloud filestore instances list
```

Mount with the NFS client on the VM or a GKE persistent volume. Snapshots exist for Filestore.

**NetApp Volumes** when the protocol is NFS or SMB and the stem mentions NetApp features (snapshots, SMB ACLs, migration from NetApp). **Managed Lustre** when the stem says Lustre or high-performance computing scratch.

## Backup and DR

| Need | Product |
| --- | --- |
| Disk snapshot on a schedule | Snapshot schedule on Persistent Disk |
| Whole VM backup, application-consistent, cross-project or cross-region restore | Backup and DR service |
| GKE volumes and config | Backup for GKE |
| Database | The database’s own backup (next chapter), not a disk snapshot of a running database as the only plan |
| Object versioning and retention | Cloud Storage features above |

Backup and DR is the centralized product. A one-off snapshot is not a disaster-recovery plan. A plan names RPO (how much data you can lose) and RTO (how fast you must be back), a destination region, and a tested restore.

```bash
gcloud services enable backupdr.googleapis.com
# Backup plans are created per management server in the Backup and DR console
# or API. Know the product. Do not invent a one-line flag.
```

## Static website

A public bucket plus a load balancer, or Cloud CDN in front of a backend bucket. Do not enable `allUsers` on a bucket that also holds data. Split static site and data lake.

## Exercises

1. Logs are read once a quarter and must be cheap, but a compliance review must open them in seconds. Which class?
2. An application `open()`s `/mnt/data`. Which product?
3. 200 TB from S3, every night, with retries. Which service?
4. Finance must prove objects cannot be deleted for one year, even by admins. Which setting?
5. You enabled versioning and a lifecycle delete of noncurrent versions after 7 days. What did you protect, and what did you cap?

### Answers

1. Coldline. Archive if it is closer to yearly. Access is still milliseconds. Do not pick a tape product Google Cloud does not require here.
2. Filestore or NetApp Volumes. Cloud Storage would require the app to use the object API or FUSE, which is a different design.
3. Storage Transfer Service.
4. Bucket retention policy, then lock it. IAM alone does not stop a principal who has delete permission.
5. Versioning protects overwrite and delete by keeping generations. Lifecycle caps the cost of those generations.
