# Lab 03 — S3 encryption, public access block, lifecycle

SAA tasks 1.3 and 3.1. One bucket. No static website. No object you would mind deleting.

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
BUCKET="cert-lab03-${ACCOUNT}"
```

`us-east-1` is the one Region where `create-bucket` does not take a location constraint. In any other Region add `--create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION`.

## 1. Create it locked

```bash
aws s3api create-bucket --bucket "$BUCKET" --region us-east-1

aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3api put-bucket-versioning --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration '{
  "Rules": [{
    "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"},
    "BucketKeyEnabled": true
  }]
}'

aws s3api put-bucket-policy --bucket "$BUCKET" --policy "{
  \"Version\": \"2012-10-17\",
  \"Statement\": [{
    \"Sid\": \"DenyInsecureTransport\",
    \"Effect\": \"Deny\",
    \"Principal\": \"*\",
    \"Action\": \"s3:*\",
    \"Resource\": [\"arn:aws:s3:::${BUCKET}\", \"arn:aws:s3:::${BUCKET}/*\"],
    \"Condition\": {\"Bool\": {\"aws:SecureTransport\": \"false\"}}
  }]
}"
```

`BlockPublicPolicy=true` rejects a policy that would make the bucket public. The transport deny is not a public grant, so it is accepted. If a later policy put fails, that block is why.

## 2. Put, overwrite, see versions

```bash
echo v1 > /tmp/lab03.txt
aws s3api put-object --bucket "$BUCKET" --key notes/lab03.txt --body /tmp/lab03.txt
echo v2 > /tmp/lab03.txt
aws s3api put-object --bucket "$BUCKET" --key notes/lab03.txt --body /tmp/lab03.txt
aws s3api list-object-versions --bucket "$BUCKET" --prefix notes/lab03.txt \
  --query 'Versions[].{id:VersionId,latest:IsLatest,size:Size}'
aws s3api head-object --bucket "$BUCKET" --key notes/lab03.txt \
  --query '{sse:ServerSideEncryption,bucketkey:BucketKeyEnabled}'
```

`ServerSideEncryption` is `AES256`. You did not pass an encryption header. Default encryption applied. That is SSE-S3. On the exam, SSE-KMS is the answer when they name a key policy, a grant, or CloudTrail data events on the key. SSE-S3 is the answer when they only say "encrypted at rest" and nobody needs to administer the key.

## 3. Lifecycle

STANDARD_IA has a 30-day minimum. A transition at day 1 is a console error and an exam trap.

```bash
aws s3api put-bucket-lifecycle-configuration --bucket "$BUCKET" --lifecycle-configuration '{
  "Rules": [{
    "ID": "notes-tier-and-expire-old",
    "Status": "Enabled",
    "Filter": {"Prefix": "notes/"},
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},
      {"Days": 90, "StorageClass": "GLACIER"}
    ],
    "NoncurrentVersionExpiration": {"NoncurrentDays": 30},
    "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}
  }]
}'
aws s3api get-bucket-lifecycle-configuration --bucket "$BUCKET"
```

Glacier retrieval is minutes to hours. If the stem says the object is read within milliseconds, the lifecycle target is wrong and Intelligent-Tiering or Standard is the storage class. Intelligent-Tiering is the "unknown access pattern" answer. Glacier is the "once a year, retrieval delay is acceptable" answer.

Aborting incomplete multipart uploads is the orphaned-parts bill. Versioning without a noncurrent expiration is the other orphaned bill.

## 4. What you do not enable for practice

Object Lock can only be turned on at bucket creation, and in compliance mode you cannot delete the object until the retention ends. Do not add it to this bucket. On the exam, Object Lock compliance is the answer for "a regulator says nobody, including root, may delete this for seven years." Governance mode allows a privileged user to bypass.

A customer managed KMS key is the right production choice when you need a key policy. It is the wrong lab default: `ScheduleKeyDeletion` and a bucket you forgot will strand the objects. If you want to see the deny, add a second statement that denies `s3:PutObject` when `s3:x-amz-server-side-encryption` is not `aws:kms`, then watch a put without that header fail. Remove the statement before cleanup.

## Cleanup

Versioned buckets do not delete while versions or delete markers remain.

```bash
aws s3api delete-objects --bucket "$BUCKET" --delete "$(aws s3api list-object-versions --bucket "$BUCKET" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json)"
aws s3api delete-objects --bucket "$BUCKET" --delete "$(aws s3api list-object-versions --bucket "$BUCKET" \
  --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' --output json)"
aws s3api delete-bucket --bucket "$BUCKET"
rm -f /tmp/lab03.txt
```

If `delete-objects` complains about an empty Objects list, there was nothing left. Run `delete-bucket` anyway.
