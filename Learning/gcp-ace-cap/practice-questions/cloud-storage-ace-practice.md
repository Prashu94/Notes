# Google Cloud Storage - ACE Practice Questions

## Question 1
Your company needs to store backup data that is accessed less than once per month and must be retained for 1 year minimum. Cost optimization is a priority. Which storage class should you use?

**A)** Standard

**B)** Nearline

**C)** Coldline

**D)** Archive

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Nearline is designed for data accessed less than once per month
  - 30-day minimum storage duration (meets the requirement)
  - Lower storage cost than Standard ($0.010/GB/month vs $0.020/GB/month)
  - Retrieval cost is $0.01/GB (acceptable for monthly access)
  - Good balance of cost and access frequency

Create Nearline bucket:
```bash
gsutil mb -c NEARLINE -l us-central1 gs://my-backup-bucket
```

Cost comparison for 1TB accessed once per month:
- Standard: $20/month storage + $0 retrieval = $20/month
- Nearline: $10/month storage + $10 retrieval = $20/month (similar but allows flexible access)
- Coldline: $4/month storage + $20 retrieval = $24/month
- Archive: $1.20/month storage + $50 retrieval = $51.20/month

- Option A is incorrect because:
  - Standard storage is more expensive ($0.020/GB/month)
  - Optimized for hot data accessed frequently
  - No cost advantage for infrequent access

- Option C is incorrect because:
  - Coldline is for data accessed less than once per quarter (90 days)
  - 90-day minimum storage duration
  - Higher retrieval cost ($0.02/GB)
  - Overkill for monthly access

- Option D is incorrect because:
  - Archive is for data accessed less than once per year
  - 365-day minimum storage duration (locks data for 1 year)
  - Highest retrieval cost ($0.05/GB)
  - Too expensive for monthly access

**Rule of Thumb:**
- Access > 1/month → Standard
- Access < 1/month → Nearline  
- Access < 1/quarter → Coldline
- Access < 1/year → Archive

---

## Question 2
You need to upload a 500GB file to Cloud Storage from your on-premises data center. The network connection is unreliable and the upload keeps failing. What should you do?

**A)** Use `gsutil cp` with resumable uploads enabled

**B)** Split the file manually and upload in parts

**C)** Use the Cloud Console upload feature

**D)** Request a Transfer Appliance from Google

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `gsutil` automatically uses resumable uploads for large files
  - Can resume interrupted transfers without starting over
  - No manual intervention needed
  - Handles network failures gracefully

Upload with resumable transfer:
```bash
# gsutil automatically uses resumable uploads for files > 8MB
gsutil cp large-file.zip gs://my-bucket/

# Explicitly enable resumable uploads
gsutil -o "GSUtil:resumable_threshold=8M" cp large-file.zip gs://my-bucket/

# If interrupted, run same command again - it will resume from where it stopped
```

For even better performance with parallel uploads:
```bash
# Enable parallel composite uploads for large files
gsutil -o GSUtil:parallel_composite_upload_threshold=150M cp large-file.zip gs://my-bucket/
```

How it works:
1. File is split into chunks
2. Each chunk uploaded independently  
3. If a chunk fails, only that chunk is re-uploaded
4. Chunks are composed into final object
5. Automatic retry with exponential backoff

- Option B is incorrect because:
  - Manual splitting is unnecessary
  - `gsutil` handles this automatically
  - More work and error-prone
  - Would need to manually compose parts

- Option C is incorrect because:
  - Console upload doesn't handle large files well
  - Size limits and timeout issues
  - Not designed for files > 100MB
  - No resumable upload in browser

- Option D is incorrect because:
  - Transfer Appliance is for 100+ TB of data
  - Requires physical shipping
  - Overkill for 500GB
  - Takes weeks to receive and return

**gsutil resumable uploads** are automatic for files > 8MB and handle network failures gracefully.

---

## Question 3
You need to make a specific object in your Cloud Storage bucket publicly accessible so anyone can download it. The bucket uses uniform bucket-level access. What should you do?

**A)** Run: `gsutil acl ch -u AllUsers:READ gs://bucket/object.pdf`

**B)** Run: `gsutil iam ch allUsers:objectViewer gs://bucket`

**C)** Disable uniform bucket-level access and set object ACL

**D)** Create a signed URL with long expiration

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Uniform bucket-level access means IAM-only (no ACLs)
  - Must grant IAM permission at bucket level
  - `allUsers:objectViewer` makes all objects in bucket public
  - Follows the uniform access model

Make specific bucket public (uniform access):
```bash
# Grant read access to all users for entire bucket
gsutil iam ch allUsers:objectViewer gs://my-bucket
```

**Important:** With uniform bucket-level access, you can't make just ONE object public - all objects in the bucket become public.

If you need just one object public, options:
1. Use signed URLs (temporary access)
2. Create a separate bucket for public content
3. Disable uniform access (not recommended)

- Option A is incorrect because:
  - Bucket uses uniform bucket-level access (ACLs are disabled)
  - ACL commands won't work
  - Would get an error about uniform access being enabled

- Option C is incorrect because:
  - Disabling uniform access reduces security
  - Goes against best practices
  - Not recommended just to make one object public
  - Better alternatives exist

- Option D is incorrect because:
  - While this works, it's not making the object "publicly accessible"
  - Signed URLs are temporary and require a URL
  - Doesn't align with "anyone can download it" requirement
  - Best for time-limited sharing, not permanent public access

**Uniform Bucket-Level Access:**
- Recommended by Google
- Simpler permission model (IAM only)
- Better for compliance and auditing
- Cannot set object-level ACLs

To make select objects public with uniform access:
```bash
# Best practice: create separate public bucket
gsutil mb gs://my-public-bucket
gsutil iam ch allUsers:objectViewer gs://my-public-bucket
gsutil cp gs://my-private-bucket/file.pdf gs://my-public-bucket/
```

---

## Question 4
You have a bucket with object versioning enabled. A critical file was accidentally deleted 2 days ago. How can you restore it?

**A)** Recover from deleted items in Cloud Console

**B)** List non-current versions and copy the deleted version to restore it

**C)** Contact Google Support to restore the file

**D)** The file is permanently deleted and cannot be recovered

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Versioning preserves deleted objects as non-current versions
  - "Deleting" actually creates a delete marker
  - Previous version is still accessible
  - Can be copied to restore

Restore deleted object:
```bash
# List all versions including deleted
gsutil ls -a gs://my-bucket/important-file.txt

# Output shows:
# gs://my-bucket/important-file.txt#1634567890123456 (LIVE - delete marker)
# gs://my-bucket/important-file.txt#1634567880123456

# Copy the old version to restore
gsutil cp gs://my-bucket/important-file.txt#1634567880123456 gs://my-bucket/important-file.txt

# Or restore by removing the delete marker
gsutil rm gs://my-bucket/important-file.txt#1634567890123456
```

View object history:
```bash
# List all versions with details
gsutil ls -la gs://my-bucket/important-file.txt

# See versioning status  
gsutil versioning get gs://my-bucket
```

- Option A is incorrect because:
  - Cloud Storage doesn't have a "Deleted Items" folder like email
  - No built-in recovery UI for versioned objects
  - Must use gsutil or API

- Option C is incorrect because:
  - Google Support cannot restore deleted objects
  - You have the tools to restore yourself
  - It's the customer's responsibility

- Option D is incorrect because:
  - With versioning enabled, deleted objects are preserved
  - Only permanently deleted if:
    - Versioning was NOT enabled
    - Version was explicitly deleted
    - Lifecycle policy deleted old versions

**Versioning Behavior:**
- "Delete" creates a delete marker (object appears deleted)
- Previous versions remain and can be restored
- To permanently delete, must delete specific version

Enable versioning:
```bash
gsutil versioning set on gs://my-bucket
```

Cost consideration: Versioning stores ALL versions, increasing storage costs. Use lifecycle policies to manage old versions:
```json
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {
        "isLive": false,
        "numNewerVersions": 3
      }
    }]
  }
}
```

---

## Question 5
You need to automatically transition objects in a bucket from Standard to Nearline storage after 30 days, then to Archive after 365 days. How should you configure this?

**A)** Create two lifecycle rules: one for Standard→Nearline at 30 days, another for Nearline→Archive at 365 days

**B)** Create one lifecycle rule with multiple conditions

**C)** Manually move objects every month using a cron job

**D)** Use Cloud Scheduler to run gsutil commands

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Lifecycle rules can define storage class transitions
  - Age is counted from object creation time
  - Multiple rules can coexist
  - Automatic execution by Google

Create lifecycle configuration:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "NEARLINE"
        },
        "condition": {
          "age": 30,
          "matchesStorageClass": ["STANDARD"]
        }
      },
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "ARCHIVE"
        },
        "condition": {
          "age": 365,
          "matchesStorageClass": ["NEARLINE", "STANDARD"]
        }
      }
    ]
  }
}
```

Apply lifecycle policy:
```bash
gsutil lifecycle set lifecycle.json gs://my-bucket
```

Verification:
```bash
# View current lifecycle policy
gsutil lifecycle get gs://my-bucket
```

Transition timeline:
- Day 0: Object created in Standard
- Day 30: Auto-transition to Nearline
- Day 365: Auto-transition to Archive

- Option B is incorrect because:
  - While you could attempt one rule, it wouldn't achieve the desired transitions
  - Can't have multiple storage class transition actions in one rule
  - Need separate rules for each transition

- Option C is incorrect because:
  - Manual process is error-prone
  - Operational overhead
  - Lifecycle rules are designed for this exact use case
  - No cost benefit, just more work

- Option D is incorrect because:
  - Unnecessary complexity
  - Lifecycle rules are the native solution
  - Would require scripting and scheduling
  - Higher operational overhead

**Lifecycle Rule Conditions:**
- age: Days since object creation
- createdBefore: Specific date
- isLive: true/false (for versioned objects)
- matchesStorageClass: Current storage class
- numNewerVersions: Number of newer versions

**Lifecycle Rule Actions:**
- Delete: Delete object
- SetStorageClass: Change storage class
- AbortIncompleteMultipartUpload: Clean up failed uploads

---

## Question 6
Your application uploads 10,000 small files (10KB each) per minute to Cloud Storage. The uploads are very slow. What can you do to improve performance?

**A)** Use parallel uploads with `gsutil -m`

**B)** Increase the size of each file before uploading

**C)** Use a faster machine type for upload

**D)** Compress all files into a single archive

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `-m` flag enables parallel (multi-threaded) uploads
  - Dramatically improves throughput for many small files
  - Utilizes network bandwidth efficiently
  - gsutil's built-in optimization

Parallel uploads:
```bash
# Upload many files in parallel
gsutil -m cp -r /local/folder/* gs://my-bucket/

# Configure parallel threads (default is typically 4-10)
gsutil -m -o "GSUtil:parallel_thread_count=20" cp -r /local/folder gs://my-bucket/
```

Performance comparison (10,000 files):
- Sequential (`gsutil cp`): ~30-60 minutes
- Parallel (`gsutil -m`): ~3-5 minutes
- 10-20x faster!

Additional optimizations:
```bash
# Combine parallel uploads with process parallelism
gsutil -m -o "GSUtil:parallel_thread_count=20" -o "GSUtil:parallel_process_count=4" cp -r /data gs://bucket/
```

- Option B is incorrect because:
  - May not be feasible (application design constraint)
  - Doesn't address the core issue (sequential uploads)
  - Changes application logic

- Option C is incorrect because:
  - Usually not a CPU bottleneck
  - Network or API rate limit is the constraint
  - Wasted compute resources

- Option D is incorrect because:
  - Defeats the purpose if files need to be accessed individually
  - Application may need individual file access
  - Compression/decompression overhead
  - Not addressing the actual bottleneck

**Additional Tips:**
- Use JSON API instead of XML for better performance
- Consider batching requests if using API directly
- Monitor with Cloud Monitoring for bottlenecks

Check upload configuration:
```bash
# View current gsutil config
gsutil version -l
```

---

## Question 7
You need to copy 5TB of data from an S3 bucket in AWS to Cloud Storage. What is the most efficient method?

**A)** Download to local machine, then upload to Cloud Storage using gsutil

**B)** Use Storage Transfer Service

**C)** Write a script to stream data from S3 to Cloud Storage

**D)** Use Transfer Appliance

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Storage Transfer Service is designed for cloud-to-cloud transfers
  - Direct transfer from S3 to Cloud Storage
  - No egress from S3 to your network (stays in cloud backbone)
  - Scheduled, managed, and monitored by Google
  - Free service (you only pay for storage)

Setup Storage Transfer:
```bash
# Create transfer job (simplified - typically done via Console)
# 1. Go to Cloud Console > Storage Transfer Service
# 2. Create Transfer Job
# 3. Source: Amazon S3
# 4. Provide AWS credentials (access key, secret key)
# 5. Specify S3 bucket and GCS bucket
# 6. Schedule (one-time or recurring)

# Via gcloud (requires JSON config)
gcloud transfer jobs create s3://my-s3-bucket gs://my-gcs-bucket \
  --source-creds-file=aws-creds.json \
  --name=s3-to-gcs-transfer
```

Benefits:
- Automatic retry on failures
- Parallel transfers
- Incremental transfers (only changed files)
- Scheduled transfers
- Detailed logs and monitoring

- Option A is incorrect because:
  - Downloads to local machine (egress charges from AWS)
  - Network bandwidth constraints
  - Two-step process (slow and expensive)
  - Wastes local storage

- Option C is incorrect because:
  - Custom development required
  - Error handling and retry logic needed
  - Still involves egress from AWS
  - Storage Transfer Service is the managed solution

- Option D is incorrect because:
  - Transfer Appliance is for on-premises data
  - Requires physical shipping
  - Designed for 100+ TB
  - Overkill for cloud-to-cloud transfer

**Storage Transfer Service Use Cases:**
- AWS S3 → Cloud Storage
- Azure Blob → Cloud Storage
- Cloud Storage → Cloud Storage (cross-region)
- HTTP/HTTPS → Cloud Storage
- On-premises → Cloud Storage (with agent)

Cost consideration:
- AWS egress fees apply (data out of S3)
- GCS ingress is free
- Storage Transfer Service is free

---

## Question 8
You have a Cloud Storage bucket that needs to be accessed by users from multiple countries. Users are experiencing slow download speeds. What can you do to improve performance?

**A)** Create a multi-region bucket

**B)** Enable Cloud CDN with the bucket as a backend

**C)** Use regional buckets in each country

**D)** Increase bucket storage class to Standard

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Cloud CDN caches content at edge locations globally
  - Dramatically reduces latency for global users
  - Offloads traffic from origin bucket
  - Reduces egress costs (cached content served from edge)

Setup Cloud CDN with Cloud Storage:
```bash
# 1. Create backend bucket
gcloud compute backend-buckets create my-backend-bucket \
  --gcs-bucket-name=my-bucket \
  --enable-cdn

# 2. Create URL map
gcloud compute url-maps create my-cdn-map \
  --default-backend-bucket=my-backend-bucket

# 3. Create target HTTP(S) proxy
gcloud compute target-http-proxies create my-cdn-proxy \
  --url-map=my-cdn-map

# 4. Create global forwarding rule
gcloud compute forwarding-rules create my-cdn-rule \
  --global \
  --target-http-proxy=my-cdn-proxy \
  --ports=80

# 5. Set cache headers on objects
gsutil setmeta -h "Cache-Control:public, max-age=3600" gs://my-bucket/image.jpg
```

Performance improvement:
- First request: ~200-500ms (from origin)
- Cached requests: ~20-50ms (from edge)
- 10-20x faster for global users!

- Option A is incorrect because:
  - Multi-region provides geo-redundancy, not edge caching
  - Still served from one of two data centers
  - Doesn't solve latency for distant users
  - More expensive than CDN

- Option C is incorrect because:
  - Operational complexity (multiple buckets to manage)
  - Data synchronization challenges
  - Higher storage costs (multiple copies)
  - Cloud CDN is the proper solution

- Option D is incorrect because:
  - Storage class doesn't affect download performance
  - All storage classes have same access latency
  - Storage class is about cost, not performance

**Cloud CDN Benefits:**
- Global edge network (140+ locations)
- Automatic caching
- Reduced origin load
- Lower egress costs (cache hits are cheaper)
- Integrated with Cloud Load Balancing

Set cache headers:
```bash
# Set cache duration
gsutil setmeta -h "Cache-Control:public, max-age=86400" gs://bucket/file.pdf

# Disable caching
gsutil setmeta -h "Cache-Control:no-cache" gs://bucket/dynamic.json
```

---

## Question 9
You need to allow your on-premises application to access Cloud Storage without using the internet. What should you do?

**A)** Use Cloud VPN to create a private connection

**B)** Use Private Google Access

**C)** Use Cloud Interconnect with VPC peering

**D)** Download all data to on-premises storage

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Cloud Interconnect provides private, dedicated connection to Google Cloud
  - Can access Cloud Storage via internal IP addresses
  - Doesn't traverse the public internet
  - Lower latency and more secure

For external access (from on-premises):
```bash
# 1. Set up Cloud Interconnect (Dedicated or Partner)
# 2. Configure VPC routes

# Access Cloud Storage via private endpoint
# Use: storage.googleapis.com via private routing
```

Note: The question is somewhat ambiguous. Let me clarify options:

- **Option A** could also be correct depending on interpretation:
  - Cloud VPN creates encrypted tunnel to GCP
  - Traffic goes through VPN, not public internet
  - Cheaper than Interconnect but lower bandwidth

Setup with VPN:
```bash
# Create VPN tunnel
gcloud compute vpn-tunnels create my-tunnel \
  --peer-address=ON_PREM_IP \
  --shared-secret=SECRET \
  --target-vpn-gateway=my-vpn-gateway

# Configure routes to use VPN for Google APIs
```

- Option B is incorrect because:
  - Private Google Access is for resources within GCP (VMs without external IPs)
  - Not for on-premises access
  - Different use case

- Option D is incorrect because:
  - Defeats the purpose of cloud storage
  - No real-time access
  - Operational overhead

**Best Answer: A or C depending on requirements**

For exam purposes, if you see "without using the internet" from on-premises:
- **Cloud VPN** - Encrypted tunnel, uses internet infrastructure but traffic is private
- **Cloud Interconnect** - Dedicated physical connection, doesn't use internet at all

If the question emphasizes "dedicated" or "high bandwidth," choose Interconnect.
If it emphasizes "secure" or "cost-effective," choose VPN.

Given the exact wording "without using the internet," the most technically accurate answer is **C (Cloud Interconnect)**.

---

## Question 10
You need to configure lifecycle management to delete objects older than 30 days but only if they match a specific prefix "logs/2024/ ". How should you configure the lifecycle rule?

**A)**
```json
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {
        "age": 30,
        "matchesPrefix": ["logs/2024/"]
      }
    }]
  }
}
```

**B)**
```json
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {
        "age": 30
      },
      "filter": {
        "prefix": "logs/2024/"
      }
    }]
  }
}
```

**C)**
```json
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {
        "age": 30,
        "matchesPattern": "logs/2024/**"
      }
    }]
  }
}
```

**D)**
```json
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {
        "age": 30
      },
      "matchesPrefix": ["logs/2024/"]
    }]
  }
}
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `matchesPrefix` is a valid condition field
  - Takes an array of prefixes
  - Combined with `age` condition
  - Correct JSON structure

Apply lifecycle policy:
```bash
# Save as lifecycle.json and apply
gsutil lifecycle set lifecycle.json gs://my-bucket
```

This will delete objects matching:
- Path starts with "logs/2024/"
- AND object is older than 30 days

Examples:
- `gs://bucket/logs/2024/jan/app.log` (30+ days) → Deleted ✓
- `gs://bucket/logs/2024/feb/error.log` (30+ days) → Deleted ✓
- `gs://bucket/logs/2024/mar/info.log` (10 days) → Kept (not old enough)
- `gs://bucket/logs/2023/dec/old.log` (100 days) → Kept (different prefix)

- Option B is incorrect because:
  - `filter` is not a valid top-level lifecycle rule field
  - Prefix matching must be inside `condition`

- Option C is incorrect because:
  - `matchesPattern` doesn't exist in lifecycle rules
  - `matchesPrefix` is the correct field name

- Option D is incorrect because:
  - `matchesPrefix` is inside `condition`, not at rule level
  - Incorrect JSON structure

**Additional Lifecycle Conditions:**
```json
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {
        "age": 30,
        "matchesPrefix": ["logs/2024/", "temp/"],
        "matchesSuffix": [".tmp", ".log"],
        "createdBefore": "2024-12-31",
        "numNewerVersions": 3
      }
    }]
  }
}
```

Verify lifecycle policy:
```bash
# View current policy
gsutil lifecycle get gs://my-bucket

# Test with dry-run (if available)
# Note: There's no dry-run for lifecycle, monitor with Cloud Logging
```

---

## Question 11
You need to grant a user access to download objects from a specific bucket, but only for the next 4 hours. What should you do?

**A)** Grant `roles/storage.objectViewer` with an IAM condition that expires in 4 hours

**B)** Create a signed URL with 4-hour expiration

**C)** Create a temporary service account that expires in 4 hours

**D)** Grant access and set a calendar reminder to revoke it

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Signed URLs provide time-limited access to specific objects
  - No IAM policy changes needed
  - Can specify exact expiration time
  - Revocable by deleting service account key
  - Easy to generate and share

Generate signed URL:
```bash
# Create signed URL valid for 4 hours
gsutil signurl -d 4h keyfile.json gs://my-bucket/file.pdf

# Output:
# https://storage.googleapis.com/my-bucket/file.pdf?X-Goog-Algorithm=...&X-Goog-Expires=14400...

# For multiple files
gsutil signurl -d 4h keyfile.json gs://my-bucket/*.pdf
```

Using Python:
```python
from google.cloud import storage
from datetime import timedelta

def generate_signed_url(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=4),
        method="GET"
    )
    
    return url

url = generate_signed_url("my-bucket", "file.pdf")
print(f"Signed URL: {url}")
```

- Option A is incorrect because:
  - IAM conditions would work but are overkill for this use case
  - Requires IAM policy modification
  - Grants access to entire bucket
  - More appropriate for recurring scheduled access

- Option C is incorrect because:
  - Service accounts don't have built-in expiration
  - More complex than needed
  - Requires IAM management

- Option D is incorrect because:
  - Manual process prone to error
  - User might forget to revoke
  - Not automated or reliable

**Signed URL Use Cases:**
- Temporary downloads for external users
- Time-limited uploads
- Sharing sensitive files
- Anonymous access to private objects

Signed URL for uploads:
```bash
# Allow uploads for 1 hour
gsutil signurl -m PUT -d 1h -c application/pdf keyfile.json gs://bucket/upload.pdf
```

**Security:**
- Signed URLs can't be revoked directly (they're cryptographically signed)
- To revoke: delete the service account key used to sign
- Use shortest practical expiration time

---

## Question 12
Your organization requires all data in Cloud Storage to be encrypted with customer-managed encryption keys (CMEK) stored in Cloud KMS. How should you configure this?

**A)** Enable default encryption on the bucket using a Cloud KMS key

**B)** Encrypt each file locally before uploading

**C)** Use client-side encryption libraries

**D)** Enable server-side encryption with customer-supplied keys (CSEK)

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - CMEK integration is built into Cloud Storage
  - Keys managed in Cloud KMS
  - Automatic encryption/decryption
  - Can set as bucket default
  - Meets compliance requirements

Setup CMEK:
```bash
# 1. Create KMS key ring and key
gcloud kms keyrings create my-keyring \
  --location=us-central1

gcloud kms keys create my-storage-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --purpose=encryption

# 2. Grant Cloud Storage service account access to the Cloud KMS key
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")

gcloud kms keys add-iam-policy-binding my-storage-key \
  --location=us-central1 \
  --keyring=my-keyring \
  --member=serviceAccount:service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com \
  --role=roles/cloudkms.cryptoKeyEncrypterDecrypter

# 3. Set default CMEK for bucket
gsutil kms encryption \
  -k projects/PROJECT_ID/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-storage-key \
  gs://my-bucket

# 4. Upload objects (automatically encrypted with CMEK)
gsutil cp file.txt gs://my-bucket/
```

Verify encryption:
```bash
# Check bucket default encryption
gsutil kms encryption gs://my-bucket

# Check object encryption
gsutil stat gs://my-bucket/file.txt | grep "KMS key"
```

- Option B is incorrect because:
  - Manual process for every file
  - Operational overhead
  - Doesn't meet "managed encryption keys" requirement
  - Built-in CMEK is easier

- Option C is incorrect because:
  - Client-side encryption is different from CMEK
  - More complex implementation
  - You manage the encryption/decryption
  - CMEK is the recommended approach

- Option D is incorrect because:
  - CSEK (Customer-Supplied Encryption Keys) requires you to provide the key with each request
  - Keys are not stored in Cloud KMS
  - More complex to manage
  - CMEK is better for key management

**Encryption Options:**
1. **Default (GMEK)**: Google-managed keys (automatic, no config)
2. **CMEK**: Customer-managed keys in Cloud KMS (you control rotation/access)
3. **CSEK**: Customer-supplied keys (you provide key with each request)

**CMEK Benefits:**
- Keys managed in Cloud KMS
- Audit logging of key usage
- Automatic rotation policies
- Centralized access control
- Compliance (some regulations require CMEK)

---

## Question 13
You have a bucket with thousands of objects. You need to find all objects that were created in January 2024. What is the most efficient way?

**A)** Use `gsutil ls -l` and manually filter the output

**B)** Use `gsutil ls` with a filter: `gsutil ls -l gs://bucket/** | grep "2024-01"`

**C)** Use Cloud Asset Inventory to query object metadata

**D)** List all objects via API and filter programmatically

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - `gsutil ls -l` shows detailed info including creation time
  - `grep` filters output efficiently
  - Simple single command
  - Works for thousands of objects

List and filter objects:
```bash
# Find objects created in January 2024
gsutil ls -l gs://my-bucket/** | grep "2024-01"

# More specific filtering by day
gsutil ls -l gs://my-bucket/** | grep "2024-01-15"

# Save to file for analysis
gsutil ls -l gs://my-bucket/** | grep "2024-01" > january-objects.txt

# Extract just object names
gsutil ls -l gs://my-bucket/** | grep "2024-01" | awk '{print $3}'
```

For more complex queries, use JSON output:
```bash
# Get JSON output for advanced filtering
gsutil ls -L -b gs://my-bucket > bucket-objects.json

# Or use Python script for complex filtering
```

- Option A is incorrect because:
  - "Manually filter" is inefficient and error-prone
  - Doesn't leverage command-line tools
  - Time-consuming

- Option C is incorrect because:
  - Cloud Asset Inventory is for tracking GCP resources, not objects
  - Overkill for simple date filtering
  - More complex setup

- Option D is incorrect because:
  - While this works, it requires custom code
  - More complex than command-line filtering
  - Unnecessary for simple date filtering

**Advanced Object Listing:**
```bash
# List with full metadata
gsutil ls -L gs://bucket/object.txt

# List recursively with size and timestamp
gsutil ls -lR gs://bucket/

# List only object names (no details)
gsutil ls gs://bucket/**

# Count objects
gsutil ls gs://bucket/** | wc -l

# Find large objects (> 1GB)
gsutil ls -l gs://bucket/** | awk '$1 > 1000000000 {print $3, $1}'
```

---

## Question 14
You need to ensure that objects in your bucket cannot be deleted or modified for 7 years to meet regulatory compliance. What should you do?

**A)** Create a bucket retention policy and lock it

**B)** Set object lifecycle to prevent deletion for 7 years

**C)** Use IAM to remove delete permissions from all users

**D)** Enable versioning to preserve deleted objects

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Retention policies prevent deletion/modification until retention period expires
  - Locking makes the policy irreversible (meets compliance)
  - Applies to all objects in bucket
  - Cannot be bypassed, even by project owners

Configure retention policy:
```bash
# Set 7-year (2555 days) retention policy
gsutil retention set 2555d gs://my-compliance-bucket

# Verify retention policy
gsutil retention get gs://my-compliance-bucket

# Lock the retention policy (IRREVERSIBLE!)
# WARNING: This cannot be undone!
gsutil retention lock gs://my-compliance-bucket

# Confirm by typing the bucket name when prompted
```

What retention policy does:
- Objects cannot be deleted until retention period expires
- Objects cannot be overwritten
- Retention period cannot be reduced (if locked)
- Policy cannot be removed (if locked)

Check object retention:
```bash
# View object retention status
gsutil stat gs://my-compliance-bucket/document.pdf
```

- Option B is incorrect because:
  - Lifecycle policies delete objects, they don't prevent deletion
  - Can be modified or removed
  - Not designed for compliance/immutability

- Option C is incorrect because:
  - IAM permissions can be changed
  - Project owners can modify IAM
  - Not a compliance-grade solution

- Option D is incorrect because:
  - Versioning preserves deleted objects but doesn't prevent deletion
  - Old versions can still be deleted
  - Not sufficient for compliance

**Retention vs. Hold:**
- **Retention Policy**: Time-based, applies to all objects, can be locked
- **Object Hold**: Object-specific, manual, can be released anytime

Set object hold:
```bash
# Temporary hold (prevents deletion)
gsutil retention temp set gs://bucket/file.pdf

# Event-based hold
gsutil retention event set gs://bucket/file.pdf

# Release hold
gsutil retention temp release gs://bucket/file.pdf
```

**Compliance Use Cases:**
- Financial records (SEC, FINRA)
- Healthcare data (HIPAA)
- Legal documents
- Government records

---

## Question 15
You have a multi-regional bucket in "us" location. You need to move it to a regional bucket in "us-central1" to reduce costs. What is the most efficient method?

**A)** Use `gsutil mv` to move all objects

**B)** Create a new regional bucket and use `gsutil rsync`

**C)** Change the bucket location in Cloud Console

**D)** Use Storage Transfer Service to migrate objects

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Cannot change bucket location after creation
  - Must create new bucket and copy data
  - `gsutil rsync` efficiently synchronizes buckets
  - Can verify data before deleting source

Migration steps:
```bash
# 1. Create new regional bucket
gsutil mb -c STANDARD -l us-central1 gs://new-regional-bucket

# 2. Copy all objects (parallel transfer)
gsutil -m rsync -r gs://old-multi-region-bucket gs://new-regional-bucket

# Verify copy completed
gsutil -m rsync -r -n gs://old-multi-region-bucket gs://new-regional-bucket
# -n = dry run, should show no differences

# 3. Update application to use new bucket

# 4. Delete old bucket (after verification)
gsutil -m rm -r gs://old-multi-region-bucket
gsutil rb gs://old-multi-region-bucket
```

`gsutil rsync` benefits:
- Only copies new/changed objects (incremental)
- Parallel transfers (fast)
- Checksum verification
- Handles failures gracefully

- Option A is incorrect because:
  - `gsutil mv` between buckets is just copy + delete
  - Not more efficient than rsync
  - Doesn't sync, just moves

- Option C is incorrect because:
  - Cannot change bucket location after creation
  - Would need to delete and recreate (data loss)
  - Not possible in Cloud Console

- Option D is incorrect because:
  - Storage Transfer Service works but is overkill for same-project transfer
  - `gsutil rsync` is simpler for one-time migration
  - STS better for ongoing syncing or large-scale migrations

**Cost Comparison:**
- Multi-region (us): $0.026/GB/month
- Regional (us-central1): $0.020/GB/month
- Savings: ~23% on storage costs

**Immutable Bucket Properties:**
- Location (region/multi-region)
- Bucket name
- Project (cannot move buckets between projects)

**Can be changed:**
- Storage class (default)
- Labels
- Lifecycle policies
- IAM permissions
