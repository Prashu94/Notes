# Google Cloud Storage - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Storage Classes](#storage-classes)
4. [Buckets](#buckets)
5. [Objects](#objects)
6. [Access Control](#access-control)
7. [Lifecycle Management](#lifecycle-management)
8. [Data Transfer](#data-transfer)
9. [Monitoring & Logging](#monitoring--logging)
10. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

Cloud Storage is Google's object storage service for storing and accessing unstructured data. It's globally available, highly durable (99.999999999% annual durability), and scales automatically.

**Key Characteristics:**
- **Object Storage:** Store any type of file
- **Globally Accessible:** Access from anywhere via HTTP(S)
- **No Capacity Planning:** Unlimited storage
- **Strong Consistency:** Read-after-write consistency

---

## Core Concepts

### Buckets

Containers for objects. Bucket names are globally unique.

**Bucket Naming Rules:**
- 3-63 characters
- Lowercase letters, numbers, hyphens, underscores, periods
- Must start/end with letter or number
- Cannot contain "google" or variations

**Example:** `my-project-data-bucket`

### Objects

Files stored in buckets. Objects have:
- **Name (key):** Unique within bucket
- **Data (value):** The file contents
- **Metadata:** Content-type, ACLs, custom metadata

**Example:** `gs://my-bucket/folder/file.txt`

### Locations

**Region:** Single geographic location (e.g., `us-central1`)
- Lower latency for users in that region
- Lower cost

**Dual-Region:** Two specific regions (e.g., `nam4` = Iowa + South Carolina)
- Higher availability
- Synchronous replication

**Multi-Region:** Large geographic area (e.g., `us`, `eu`, `asia`)
- Highest availability
- Best for global access

---

## Storage Classes

### Standard Storage

**Use Case:** Hot data accessed frequently
**Minimum Storage:** None
**Retrieval Cost:** None

**Best For:**
- Website content
- Streaming videos
- Active databases
- Data analytics

**Example:**
```bash
gsutil mb -c STANDARD -l us-central1 gs://my-standard-bucket
```

### Nearline Storage

**Use Case:** Data accessed < 1/month
**Minimum Storage:** 30 days
**Retrieval Cost:** $0.01/GB

**Best For:**
- Data backups
- Long-tail multimedia content
- Data archiving (monthly access)

**Example:**
```bash
gsutil mb -c NEARLINE -l us-central1 gs://my-nearline-bucket
```

### Coldline Storage

**Use Case:** Data accessed < 1/quarter
**Minimum Storage:** 90 days
**Retrieval Cost:** $0.02/GB

**Best For:**
- Disaster recovery data
- Archives accessed quarterly
- Compliance data

**Example:**
```bash
gsutil mb -c COLDLINE -l us-central1 gs://my-coldline-bucket
```

### Archive Storage

**Use Case:** Data accessed < 1/year
**Minimum Storage:** 365 days
**Retrieval Cost:** $0.05/GB

**Best For:**
- Long-term archiving
- Regulatory compliance data
- Cold disaster recovery

**Example:**
```bash
gsutil mb -c ARCHIVE -l us-central1 gs://my-archive-bucket
```

### Comparison Table

| Class | Monthly Access | Min Duration | Retrieval Cost | Storage Cost (per GB/month) |
|-------|----------------|--------------|----------------|------------------------------|
| **Standard** | Frequent | None | None | $0.020 (regional) |
| **Nearline** | < 1/month | 30 days | $0.01/GB | $0.010 |
| **Coldline** | < 1/quarter | 90 days | $0.02/GB | $0.004 |
| **Archive** | < 1/year | 365 days | $0.05/GB | $0.0012 |

---

## Buckets

### Creating a Bucket

**Console:**
1. Go to **Cloud Storage > Buckets**
2. Click **Create Bucket**
3. Enter bucket name
4. Choose location type and region
5. Select default storage class
6. Choose access control (Uniform or Fine-grained)
7. Click **Create**

**gcloud:**
```bash
gsutil mb -p PROJECT_ID -c STORAGE_CLASS -l LOCATION gs://BUCKET_NAME
```

**Examples:**
```bash
# Regional bucket with Standard storage
gsutil mb -c STANDARD -l us-central1 gs://my-data-bucket

# Multi-region bucket with Nearline storage
gsutil mb -c NEARLINE -l us gs://my-backup-bucket
```

### Listing Buckets

```bash
gsutil ls

# With details
gsutil ls -L gs://BUCKET_NAME
```

### Deleting a Bucket

**Must be empty first!**

```bash
# Delete all objects
gsutil rm -r gs://BUCKET_NAME/*

# Delete bucket
gsutil rb gs://BUCKET_NAME
```

### Bucket Configuration

**Enable versioning:**
```bash
gsutil versioning set on gs://BUCKET_NAME
```

**Set default storage class:**
```bash
gsutil defstorageclass set NEARLINE gs://BUCKET_NAME
```

**Enable uniform bucket-level access:**
```bash
gsutil iam ch allUsers:objectViewer gs://BUCKET_NAME
```

---

## Objects

### Uploading Objects

**Single file:**
```bash
gsutil cp LOCAL_FILE gs://BUCKET_NAME/
```

**Multiple files:**
```bash
gsutil cp *.jpg gs://BUCKET_NAME/images/
```

**Recursive upload:**
```bash
gsutil cp -r LOCAL_FOLDER gs://BUCKET_NAME/
```

**With storage class:**
```bash
gsutil cp -s NEARLINE file.txt gs://BUCKET_NAME/
```

### Downloading Objects

**Single file:**
```bash
gsutil cp gs://BUCKET_NAME/file.txt ./
```

**Multiple files:**
```bash
gsutil cp gs://BUCKET_NAME/*.txt ./
```

**Recursive download:**
```bash
gsutil cp -r gs://BUCKET_NAME/folder ./
```

### Listing Objects

```bash
# List all objects
gsutil ls gs://BUCKET_NAME

# List with details (size, timestamp)
gsutil ls -l gs://BUCKET_NAME

# List recursively
gsutil ls -r gs://BUCKET_NAME/**
```

### Deleting Objects

```bash
# Single object
gsutil rm gs://BUCKET_NAME/file.txt

# Multiple objects
gsutil rm gs://BUCKET_NAME/*.txt

# Delete folder recursively
gsutil rm -r gs://BUCKET_NAME/folder/
```

### Copying/Moving Objects

**Copy within Cloud Storage:**
```bash
gsutil cp gs://SOURCE_BUCKET/file.txt gs://DEST_BUCKET/
```

**Move (rename):**
```bash
gsutil mv gs://BUCKET/old-name.txt gs://BUCKET/new-name.txt
```

### Viewing Object Metadata

```bash
gsutil stat gs://BUCKET_NAME/file.txt
```

### Setting Object Metadata

```bash
gsutil setmeta -h "Content-Type:application/json" \
  -h "Cache-Control:public, max-age=3600" \
  gs://BUCKET_NAME/file.json
```

---

## Access Control

### IAM (Bucket-Level)

**Grant read access:**
```bash
gsutil iam ch user:EMAIL:roles/storage.objectViewer gs://BUCKET_NAME
```

**Grant write access:**
```bash
gsutil iam ch user:EMAIL:roles/storage.objectCreator gs://BUCKET_NAME
```

**Grant admin access:**
```bash
gsutil iam ch user:EMAIL:roles/storage.admin gs://BUCKET_NAME
```

**Make bucket publicly readable:**
```bash
gsutil iam ch allUsers:objectViewer gs://BUCKET_NAME
```

### ACLs (Object-Level)

**Enable fine-grained ACLs:**
```bash
gsutil uniformbucketlevelaccess set off gs://BUCKET_NAME
```

**Grant read access to object:**
```bash
gsutil acl ch -u EMAIL:READ gs://BUCKET_NAME/file.txt
```

**Make object public:**
```bash
gsutil acl ch -u AllUsers:READ gs://BUCKET_NAME/file.txt
```

### Signed URLs

Temporary access to private objects:

```bash
gsutil signurl -d 10m KEY_FILE gs://BUCKET_NAME/file.txt
```

---

## Lifecycle Management

Automatically transition or delete objects based on conditions.

### Lifecycle Rules

**Delete objects older than 30 days:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30}
      }
    ]
  }
}
```

**Transition to Nearline after 30 days:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      }
    ]
  }
}
```

**Apply lifecycle configuration:**
```bash
gsutil lifecycle set lifecycle.json gs://BUCKET_NAME
```

**View lifecycle configuration:**
```bash
gsutil lifecycle get gs://BUCKET_NAME
```

---

## Data Transfer

### gsutil (Command-Line)

**Parallel uploads:**
```bash
gsutil -m cp -r large-folder gs://BUCKET_NAME/
```

**Resume interrupted transfers:**
```bash
gsutil cp -c file.txt gs://BUCKET_NAME/
```

### Cloud Console (Web UI)

Upload/download via browser (good for small files < 100 MB).

### Storage Transfer Service

For large-scale transfers from:
- Other cloud providers (AWS S3, Azure Blob)
- On-premises via Transfer Service agent
- Another Cloud Storage bucket

**Use Case:** Migrate 10+ TB of data.

### Transfer Appliance

Physical device shipped by Google for massive data transfers (100+ TB).

---

## Monitoring & Logging

### Cloud Monitoring Metrics

- Total bytes
- Object count
- Request count
- Bandwidth

### Cloud Logging

Enable access logs:
```bash
gsutil logging set on -b gs://LOG_BUCKET gs://DATA_BUCKET
```

**Log Format:** JSON with request details (IP, timestamp, object, HTTP status).

---

## ACE Exam Tips

1. **Storage Classes:** Know the access frequency and minimum storage duration for each class.
   - Standard: No minimum, frequent access
   - Nearline: 30 days, < 1/month
   - Coldline: 90 days, < 1/quarter
   - Archive: 365 days, < 1/year

2. **gsutil Commands:** Memorize:
   - `gsutil mb`: Make bucket
   - `gsutil cp`: Copy/upload/download
   - `gsutil rm`: Delete
   - `gsutil ls`: List
   - `gsutil iam`: IAM permissions

3. **Access Control:**
   - IAM = Bucket-level (uniform)
   - ACL = Object-level (fine-grained)
   - Uniform access is recommended (simpler)

4. **Lifecycle Management:** Automatically transition storage classes or delete old objects to save costs.

5. **Signed URLs:** Provide temporary access to private objects without changing permissions.

6. **Object Versioning:** Enable to prevent accidental deletion. Old versions are kept.

7. **Multi-Region vs Region:**
   - Multi-region: Higher availability, higher cost, global access
   - Region: Lower cost, lower latency for single-region access

8. **Transfer Methods:**
   - < 1 TB: gsutil
   - 1-10 TB: Storage Transfer Service
   - 10+ TB: Storage Transfer Service with Transfer Appliance

9. **Bucket Naming:** Globally unique, 3-63 chars, lowercase only.

10. **Minimum Storage Duration:** If you delete an object before the minimum duration, you're charged for the full duration.

---

## Advanced Object Operations

### Object Versioning

**Enable versioning on a bucket:**
```bash
gsutil versioning set on gs://BUCKET_NAME
```

**How it works:**
- When enabled, every overwrite or deletion creates a new version
- Original object is preserved (non-current version)
- List all versions:
  ```bash
  gsutil ls -a gs://BUCKET_NAME/file.txt
  ```

**List all versions with details:**
```bash
gsutil ls -la gs://BUCKET_NAME/
```

**Download a specific version:**
```bash
gsutil cp gs://BUCKET_NAME/file.txt#1234567890123456 ./
```

**Delete a specific version:**
```bash
gsutil rm gs://BUCKET_NAME/file.txt#1234567890123456
```

**Restore a previous version:**
```bash
# Copy old version to become current version
gsutil cp gs://BUCKET_NAME/file.txt#1234567890123456 gs://BUCKET_NAME/file.txt
```

**Disable versioning:**
```bash
gsutil versioning set off gs://BUCKET_NAME
```

**Important:** Disabling versioning doesn't delete existing versions, it just stops creating new ones.

### Object Composition

Combine multiple objects into one:

```bash
gsutil compose gs://BUCKET/part1.txt gs://BUCKET/part2.txt gs://BUCKET/combined.txt
```

**Use Cases:**
- Reassemble files split for upload
- Combine log files
- Append data to existing objects

**Limitations:**
- Max 32 source objects per compose operation
- All objects must be in same bucket

### Parallel Composite Uploads

For large files (>150 MB), gsutil automatically splits into parts and uploads in parallel:

```bash
gsutil -o GSUtil:parallel_composite_upload_threshold=150M cp large-file.zip gs://BUCKET_NAME/
```

**How it works:**
1. File is split into chunks
2. Chunks upload in parallel (faster)
3. Chunks are composed into final object
4. Temporary chunks are deleted

**Benefits:**
- Faster uploads for large files
- Better utilization of bandwidth
- Automatic retry of failed chunks

### Object Hold and Retention

**Object Hold:**
- Prevents deletion of specific objects
- Types: Event-based hold, Temporary hold

```bash
# Set temporary hold
gsutil retention temp set gs://BUCKET_NAME/file.txt

# Release temporary hold
gsutil retention temp release gs://BUCKET_NAME/file.txt
```

**Bucket Retention Policy:**
- Objects cannot be deleted until retention period expires
- Compliance requirement

```bash
# Set 7-day retention policy
gsutil retention set 7d gs://BUCKET_NAME

# Lock retention policy (irreversible!)
gsutil retention lock gs://BUCKET_NAME
```

---

## Storage Security

### Encryption

**Default Encryption:**
- All data encrypted at rest automatically
- Google-managed encryption keys (GMEK)
- No action required

**Customer-Managed Encryption Keys (CMEK):**
- Use your own keys in Cloud KMS
- More control over key rotation and access

**Create KMS key:**
```bash
gcloud kms keyrings create my-keyring --location=us-central1

gcloud kms keys create my-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=encryption
```

**Set default CMEK for bucket:**
```bash
gsutil kms encryption \
  -k projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key \
  gs://BUCKET_NAME
```

**Upload with specific CMEK:**
```bash
gsutil -o "GSUtil:encryption_key=projects/PROJECT/locations/us-central1/keyRings/RING/cryptoKeys/KEY" \
  cp file.txt gs://BUCKET_NAME/
```

**Customer-Supplied Encryption Keys (CSEK):**
- You provide encryption key with each request
- Google doesn't store your key
- More complex but maximum control

### Bucket Lock

**Retention Policy Lock:**
- Once locked, retention policy cannot be reduced or removed
- Used for compliance (FINRA, SEC)
- **Warning:** This is irreversible!

```bash
# Set retention policy first
gsutil retention set 30d gs://BUCKET_NAME

# Lock it (cannot undo!)
gsutil retention lock gs://BUCKET_NAME
```

### Uniform Bucket-Level Access

**Enable uniform access (recommended):**
```bash
gsutil uniformbucketlevelaccess set on gs://BUCKET_NAME
```

**Benefits:**
- Simpler permission management (only IAM, no ACLs)
- Consistent with other GCP services
- Better for auditing

**Important:** Once enabled, you have 90 days to re-enable ACLs. After that, ACLs are permanently disabled.

### Public Access Prevention

Enforce that buckets cannot be made public:

```bash
# Enforce at organization level (policy)
gcloud resource-manager org-policies set-policy policy.yaml

# Check bucket public access
gsutil iam get gs://BUCKET_NAME
```

**Prevent accidental public access:**
- Use organization policies
- Enable uniform bucket-level access
- Regular audits with Cloud Asset Inventory

---

## Performance Optimization

### Request Rate Optimization

**Best Practices:**
- Avoid sequential object names (e.g., `file-0001`, `file-0002`)
  - Bad: Objects starting with same prefix hit same server
  - Good: Use random/hashed prefixes
- Add randomness: `a1b2-file-0001`, `c3d4-file-0002`

**Request Rate Limits:**
- Standard: 5,000 write requests/second, unlimited reads
- If exceeded: Use exponential backoff

### Caching with Cloud CDN

Enable Cloud CDN for static content:

**Steps:**
1. Create HTTP(S) Load Balancer
2. Backend: Cloud Storage bucket
3. Enable Cloud CDN on backend
4. Set cache headers on objects:
   ```bash
   gsutil setmeta -h "Cache-Control:public, max-age=3600" \
     gs://BUCKET_NAME/image.jpg
   ```

**Benefits:**
- Lower latency (content served from edge locations)
- Reduced egress costs
- Lower load on origin bucket

### Parallel Uploads/Downloads

**Parallel uploads:**
```bash
gsutil -m cp -r local-folder gs://BUCKET_NAME/
```

**Parallel downloads:**
```bash
gsutil -m cp -r gs://BUCKET_NAME/ ./local-folder
```

**Configure parallel threads:**
```bash
gsutil -o "GSUtil:parallel_thread_count=10" -m cp large-file.zip gs://BUCKET_NAME/
```

### Streaming Uploads

Upload without knowing final size (useful for logs, real-time data):

```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('my-bucket')
blob = bucket.blob('streaming-upload.log')

with blob.open('w') as f:
    f.write('Log line 1\n')
    f.write('Log line 2\n')
    # Data is uploaded as you write
```

---

## Data Backup and Recovery

### Versioning Strategy

**Enable versioning for critical data:**
```bash
gsutil versioning set on gs://BUCKET_NAME
```

**Lifecycle rule to delete old versions:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "isLive": false,
          "numNewerVersions": 3
        }
      }
    ]
  }
}
```

**This keeps only the 3 most recent versions of each object.**

### Cross-Region Replication

**Using gsutil with cron:**
```bash
# Sync buckets (one-way replication)
gsutil -m rsync -r -d gs://SOURCE_BUCKET gs://DEST_BUCKET
```

**Using Storage Transfer Service:**
- More reliable for ongoing replication
- Can schedule periodic transfers
- Better for large-scale operations

### Disaster Recovery Strategy

**Strategy 1: Regional bucket with versioning**
- Protects against accidental deletion
- Does NOT protect against regional outage
- **RPO:** Minutes (versioning lag)
- **RTO:** Minutes (restore from version)

**Strategy 2: Dual-region or multi-region bucket**
- Protects against regional outage
- Automatic replication
- **RPO:** Near-zero (synchronous replication)
- **RTO:** Automatic (no manual intervention)

**Strategy 3: Cross-region backup**
- Primary bucket in us-central1
- Backup bucket in europe-west1
- Scheduled replication (daily/hourly)
- **RPO:** Hours (replication frequency)
- **RTO:** Minutes to hours (manual failover)

---

## Cost Optimization

### Storage Class Selection

**Decision Tree:**
```
How often is data accessed?
├─ Frequently (daily) → Standard
├─ Monthly → Nearline
├─ Quarterly → Coldline
└─ Yearly or less → Archive
```

**Cost Calculation Example:**
- 1 TB data for 1 year
- Accessed once per month (12 retrievals)

**Standard:** $0.020/GB × 1000 GB × 12 months = $240  
**Nearline:** ($0.010/GB × 1000 GB × 12) + ($0.01/GB × 1000 GB × 12 retrievals) = $120 + $120 = $240  
**Coldline:** ($0.004/GB × 1000 GB × 12) + ($0.02/GB × 1000 GB × 12) = $48 + $240 = $288

**Best choice:** Nearline (same cost as Standard, but if access drops, savings)

### Lifecycle Policies for Cost Savings

**Example 1: Transition to cheaper storage classes**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
        "condition": {"age": 365}
      }
    ]
  }
}
```

**Example 2: Delete old versions**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "isLive": false,
          "age": 90
        }
      }
    ]
  }
}
```

**Example 3: Delete incomplete multipart uploads**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "AbortIncompleteMultipartUpload"},
        "condition": {"age": 7}
      }
    ]
  }
}
```

### Egress Cost Optimization

**Egress costs (data leaving Google Cloud):**
- To internet: $0.12/GB (North America)
- To same region: Free
- To different region: $0.01/GB (cheaper than internet)

**Optimization strategies:**
1. **Colocation:** Place compute resources in same region as bucket
2. **Cloud CDN:** Cache content at edge locations (reduces origin egress)
3. **Requester Pays:** Make users pay for their own egress

**Enable Requester Pays:**
```bash
gsutil requesterpays set on gs://BUCKET_NAME
```

**Access Requester Pays bucket:**
```bash
gsutil -u BILLING_PROJECT cp gs://BUCKET_NAME/file.txt ./
```

### Monitoring Costs

**View storage costs in Cloud Console:**
1. Go to **Billing > Reports**
2. Filter by SKU: Cloud Storage
3. Group by SKU to see: Storage, Operations, Egress

**Set budget alerts:**
1. Go to **Billing > Budgets & alerts**
2. Create budget for Cloud Storage
3. Set threshold alerts (e.g., 50%, 90%, 100%)

---

## Integration with Other Services

### Cloud Storage FUSE

Mount buckets as file systems on Compute Engine or GKE:

```bash
# Install Cloud Storage FUSE
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install gcsfuse

# Mount bucket
mkdir ~/my-bucket
gcsfuse BUCKET_NAME ~/my-bucket

# Now use like regular folder
ls ~/my-bucket
cp file.txt ~/my-bucket/
```

**Use Cases:**
- Legacy applications expecting file system access
- Temporary storage for processing pipelines
- Sharing data across multiple VMs

**Limitations:**
- Performance: Not as fast as local disk (network latency)
- Not POSIX-compliant (some operations not supported)

### Cloud Storage with BigQuery

**Load data from Cloud Storage to BigQuery:**
```bash
bq load --source_format=CSV \
  DATASET.TABLE \
  gs://BUCKET_NAME/data.csv \
  SCHEMA
```

**Export BigQuery results to Cloud Storage:**
```bash
bq extract --destination_format=CSV \
  DATASET.TABLE \
  gs://BUCKET_NAME/export-*.csv
```

### Cloud Storage with Dataflow

**Read from Cloud Storage:**
```python
import apache_beam as beam

with beam.Pipeline() as pipeline:
    lines = pipeline | beam.io.ReadFromText('gs://BUCKET/input.txt')
    # Process lines...
```

**Write to Cloud Storage:**
```python
processed | beam.io.WriteToText('gs://BUCKET/output')
```

### Cloud Storage Notifications

**Pub/Sub notifications on object changes:**

```bash
# Create Pub/Sub topic
gcloud pubsub topics create gcs-notifications

# Add notification configuration
gsutil notification create -t gcs-notifications -f json gs://BUCKET_NAME
```

**Event types:**
- OBJECT_FINALIZE (upload complete)
- OBJECT_DELETE
- OBJECT_ARCHIVE (versioning)
- OBJECT_METADATA_UPDATE

**Use Cases:**
- Trigger Cloud Functions on file upload
- Index files in database when uploaded
- Start processing pipelines

---

## Troubleshooting Common Issues

### Issue 1: "Access Denied" Error

**Cause:** Insufficient permissions

**Solution:**
```bash
# Check current IAM permissions
gsutil iam get gs://BUCKET_NAME

# Grant necessary role
gsutil iam ch user:EMAIL:roles/storage.objectViewer gs://BUCKET_NAME
```

**Common roles:**
- `roles/storage.objectViewer` - Read objects
- `roles/storage.objectCreator` - Upload objects
- `roles/storage.objectAdmin` - Full object control
- `roles/storage.admin` - Full bucket control

### Issue 2: Slow Upload/Download

**Causes & Solutions:**

**1. Network bandwidth:**
- Test: `gsutil perfdiag gs://BUCKET_NAME`
- Solution: Use parallel uploads (`-m` flag)

**2. Small files:**
- Problem: High overhead per file
- Solution: Combine files or use parallel operations

**3. Distance from bucket region:**
- Problem: High latency
- Solution: Use multi-region bucket or replicate to closer region

### Issue 3: Lifecycle Policy Not Working

**Common mistakes:**

**1. Check policy syntax:**
```bash
gsutil lifecycle get gs://BUCKET_NAME
```

**2. Verify conditions:**
- Age is in days (not hours)
- Storage class transitions must follow valid path:
  - Standard → Nearline → Coldline → Archive
  - Cannot skip classes (e.g., Standard → Coldline directly)

**3. Wait for policy to take effect:**
- Lifecycle actions run daily (not immediate)
- May take 24-48 hours for first run

### Issue 4: Versioning Taking Too Much Space

**Problem:** Old versions accumulating

**Solution:** Lifecycle rule to delete old versions
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "isLive": false,
          "numNewerVersions": 5
        }
      }
    ]
  }
}
```

### Issue 5: 403 Forbidden with Signed URL

**Causes:**
1. **URL expired:** Check expiration time
2. **Wrong service account:** Ensure SA has objectViewer role
3. **Clock skew:** Ensure system time is accurate
4. **Incorrect permissions:** SA needs storage.objects.get permission

**Generate new signed URL:**
```bash
gsutil signurl -d 1h SERVICE_ACCOUNT_KEY.json gs://BUCKET/file.txt
```

---

## Best Practices Summary

### Security
1. ✅ Enable uniform bucket-level access (disable ACLs)
2. ✅ Use IAM for permissions (principle of least privilege)
3. ✅ Enable versioning for critical data
4. ✅ Use CMEK for sensitive data
5. ✅ Set retention policies for compliance data
6. ✅ Use Public Access Prevention org policy
7. ✅ Enable audit logging
8. ✅ Use signed URLs for temporary access

### Performance
1. ✅ Use parallel uploads/downloads (`-m` flag)
2. ✅ Add random prefixes to object names for high write rates
3. ✅ Enable Cloud CDN for static content
4. ✅ Collocate compute and storage in same region
5. ✅ Use composite uploads for files >150MB
6. ✅ Set appropriate Cache-Control headers

### Cost Optimization
1. ✅ Choose correct storage class for access pattern
2. ✅ Use lifecycle policies to transition/delete objects
3. ✅ Delete incomplete multipart uploads
4. ✅ Monitor and set budget alerts
5. ✅ Use multi-region only when needed (higher cost)
6. ✅ Consider Requester Pays for public datasets
7. ✅ Delete old object versions

### Reliability
1. ✅ Use multi-region or dual-region for critical data
2. ✅ Enable versioning for disaster recovery
3. ✅ Set up cross-region replication for backups
4. ✅ Test disaster recovery procedures regularly
5. ✅ Use Cloud Monitoring for alerts

### Operational
1. ✅ Use consistent naming conventions
2. ✅ Tag objects with metadata for organization
3. ✅ Automate with Cloud Functions or Cloud Scheduler
4. ✅ Use Storage Transfer Service for large migrations
5. ✅ Document lifecycle policies and retention periods

---

## Practice Scenarios for ACE Exam

### Scenario 1: Cost Optimization

**Question:** A company stores 10 TB of log files in Standard storage. Logs are accessed frequently for 30 days, then rarely (once per quarter), and never after 1 year. How can they optimize costs?

**Answer:**
1. Keep objects in Standard for 30 days
2. Transition to Coldline after 30 days
3. Delete after 365 days

**Lifecycle policy:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
```

### Scenario 2: Access Control

**Question:** A development team needs to upload files to a bucket, but should not be able to delete them. How do you configure this?

**Answer:**
Grant `roles/storage.objectCreator` role (allows create, not delete):
```bash
gsutil iam ch group:dev-team@company.com:roles/storage.objectCreator gs://BUCKET_NAME
```

### Scenario 3: Data Protection

**Question:** Critical financial data must be retained for 7 years and protected from accidental deletion. How do you ensure this?

**Answer:**
1. Set bucket retention policy to 7 years (2555 days):
   ```bash
   gsutil retention set 2555d gs://financial-bucket
   ```
2. Lock the policy (irreversible):
   ```bash
   gsutil retention lock gs://financial-bucket
   ```
3. Enable versioning for additional protection:
   ```bash
   gsutil versioning set on gs://financial-bucket
   ```

### Scenario 4: Performance

**Question:** A web application serves images from Cloud Storage and experiences high latency for global users. How can you improve performance?

**Answer:**
1. Use multi-region bucket (e.g., `us` or `eu`)
2. Enable Cloud CDN:
   - Create HTTP(S) Load Balancer with bucket as backend
   - Enable Cloud CDN on backend
3. Set cache headers on images:
   ```bash
   gsutil setmeta -h "Cache-Control:public, max-age=86400" gs://BUCKET/*.jpg
   ```

### Scenario 5: Integration

**Question:** When a file is uploaded to a bucket, you need to trigger processing. How do you implement this?

**Answer:**
1. Enable Pub/Sub notifications:
   ```bash
   gcloud pubsub topics create file-uploads
   gsutil notification create -t file-uploads -f json gs://BUCKET_NAME
   ```
2. Create Cloud Function triggered by Pub/Sub topic
3. Function processes file when notification received

---

## Quick Reference Commands

### Bucket Operations
```bash
# Create bucket
gsutil mb -c STANDARD -l us-central1 gs://BUCKET_NAME

# List buckets
gsutil ls

# Delete bucket (must be empty)
gsutil rb gs://BUCKET_NAME

# Get bucket info
gsutil ls -L -b gs://BUCKET_NAME
```

### Object Operations
```bash
# Upload
gsutil cp file.txt gs://BUCKET/
gsutil cp -r folder gs://BUCKET/

# Download
gsutil cp gs://BUCKET/file.txt ./
gsutil cp -r gs://BUCKET/folder ./

# List
gsutil ls gs://BUCKET/
gsutil ls -l gs://BUCKET/  # with details

# Delete
gsutil rm gs://BUCKET/file.txt
gsutil rm -r gs://BUCKET/folder/

# Move/Rename
gsutil mv gs://BUCKET/old.txt gs://BUCKET/new.txt
```

### Access Control
```bash
# IAM (bucket-level)
gsutil iam ch user:EMAIL:roles/storage.objectViewer gs://BUCKET
gsutil iam ch allUsers:objectViewer gs://BUCKET  # public

# View IAM policy
gsutil iam get gs://BUCKET

# Signed URL (temporary access)
gsutil signurl -d 10m KEY_FILE gs://BUCKET/file.txt
```

### Lifecycle Management
```bash
# Set lifecycle policy
gsutil lifecycle set lifecycle.json gs://BUCKET

# View lifecycle policy
gsutil lifecycle get gs://BUCKET

# Remove lifecycle policy
gsutil lifecycle set /dev/null gs://BUCKET
```

### Versioning
```bash
# Enable versioning
gsutil versioning set on gs://BUCKET

# List all versions
gsutil ls -a gs://BUCKET/file.txt

# Download specific version
gsutil cp gs://BUCKET/file.txt#VERSION ./
```

### Other Operations
```bash
# Set storage class
gsutil defstorageclass set NEARLINE gs://BUCKET

# Enable uniform access
gsutil uniformbucketlevelaccess set on gs://BUCKET

# Set retention policy
gsutil retention set 30d gs://BUCKET

# Sync directories
gsutil rsync -r -d gs://SOURCE gs://DEST

# Performance diagnostics
gsutil perfdiag gs://BUCKET
```

---

## Exam-Style Practice Questions

**Q1:** Which storage class should you use for data that is accessed once per month and must be kept for at least 90 days?
- A) Standard
- B) Nearline
- C) Coldline
- D) Archive

**Answer:** B) Nearline (access < 1/month, 30-day minimum meets 90-day requirement)

**Q2:** What is the minimum storage duration for Coldline storage?
- A) 30 days
- B) 60 days
- C) 90 days
- D) 365 days

**Answer:** C) 90 days

**Q3:** How do you make a single object publicly readable without changing bucket permissions?
- A) Use IAM to grant allUsers:objectViewer on the bucket
- B) Use ACLs to grant allUsers:READ on the object
- C) Enable uniform bucket-level access
- D) Create a signed URL

**Answer:** B) Use ACLs (requires fine-grained access to be enabled)

**Q4:** Which command uploads a directory in parallel for better performance?
- A) `gsutil cp -r folder gs://bucket/`
- B) `gsutil -m cp -r folder gs://bucket/`
- C) `gsutil rsync folder gs://bucket/`
- D) `gsutil mv folder gs://bucket/`

**Answer:** B) `gsutil -m` enables parallel/multithreaded operations

**Q5:** What happens when you enable versioning and then delete an object?
- A) The object is permanently deleted
- B) The object is moved to a trash folder
- C) A delete marker is created, and the object becomes non-current
- D) The object is archived to Archive storage class

**Answer:** C) Delete marker is created, object is preserved as non-current version

---

**End of Cloud Storage ACE Guide**
