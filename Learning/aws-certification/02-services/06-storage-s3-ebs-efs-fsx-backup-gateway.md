# Storage: S3, EBS, EFS, FSx, Backup, Storage Gateway

SAA 1.3, 3.1, 4.1. SAP 2.5, 2.6, 4.3. DVA uses S3 as the object store in code, plus EBS and EFS when the app mounts them.

Official:

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
- https://docs.aws.amazon.com/ebs/latest/userguide/what-is-amazon-ebs.html
- https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html
- https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html
- https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html
- https://docs.aws.amazon.com/storagegateway/latest/tgw/WhatIsStorageGateway.html

## Object, block, file

| Access | Service |
| --- | --- |
| Put and get by key, HTTP, any amount | S3 |
| A disk for one instance, a database data directory | EBS |
| Scratch that can vanish when the instance stops | Instance store |
| Shared POSIX for Linux fleets | EFS |
| SMB and Windows ACLs | FSx for Windows File Server |
| Lustre for HPC and training | FSx for Lustre |
| NFS or SMB with NetApp features, SnapMirror | FSx for NetApp ONTAP |
| NFS with ZFS features | FSx for OpenZFS |
| A file interface in the data center that lands in S3 | File Gateway |
| Block in the data center cached to S3 | Volume Gateway |
| Tapes | Tape Gateway |

If the application can be changed to use the SDK, S3 is usually cheaper and more durable than a file system you keep mounted.

## S3 facts that answer questions

Strong read-after-write consistency for PUT and DELETE of objects, including overwrite PUT and delete. Listing is consistent too, in current S3. Do not answer "eventual consistency on overwrite" for new designs. That was the old model.

Durability of Standard and the Multi-AZ classes is eleven nines. Availability targets differ by class. One Zone-IA and Express One Zone and Directory buckets for S3 Express are one AZ. They lose a stem that says "AZ failure must not lose the object."

| Class | Retrieval | AZ | Exam sentence |
| --- | --- | --- | --- |
| Standard | Immediate | Multi-AZ | Hot data |
| Intelligent-Tiering | Immediate | Multi-AZ, with optional archive tiers you can turn on | Unknown access pattern |
| Standard-IA | Immediate, retrieval fee | Multi-AZ | Infrequent, still fast |
| One Zone-IA | Immediate | One | Cheaper, re-creatable data |
| Glacier Instant Retrieval | Milliseconds | Multi-AZ | Once a quarter, must be instant |
| Glacier Flexible Retrieval | Minutes to hours | Multi-AZ | Archives, restore window is acceptable |
| Glacier Deep Archive | Hours | Multi-AZ | Cheapest, compliance archives |
| Express One Zone | Single-digit ms | One | Extreme request rate in one AZ. A performance buy, not a cost buy |

Lifecycle rules transition and expire. They can abort incomplete multipart uploads, which is a silent bill. Intelligent-Tiering has a monitoring fee and a minimum storage duration. Tiny objects that turn over daily can cost more in Intelligent-Tiering than in Standard.

Versioning keeps every overwrite and delete marker. Required for replication and for Object Lock. MFA Delete is a versioning feature and is rare. Object Lock compliance mode cannot be overridden, even by root, during the retention. Governance mode can be overridden by a principal you grant. Legal hold is independent of the retention date.

Replication: CRR and SRR need versioning. RTC (replication time control) gives a 15-minute predictable window backed by an SLA. Replication does not copy existing objects unless you ask for batch replication. It does not replicate deletes unless you enable delete marker replication. A bucket in another account is the ransomware copy when the destination account's roles cannot be assumed by the source admins, combined with Object Lock.

Block Public Access at the account is the default you want. A bucket policy that grants `Principal: "*"` loses to the account-level block, which is why a stem says "the policy looks public but the object is not." Access points and Object Lambda access points give different applications different policies and transforms on one bucket. Multi-Region Access Points route to the nearest bucket. S3 on Outposts is the on-premises object store.

Presigned URLs grant time-limited upload or download with the signer's permissions. They are the answer for "let a user upload without an AWS account." They are not encryption and they are not a substitute for Block Public Access.

Transfer Acceleration uses edge locations for long-haul uploads. Multipart upload is how a big object actually goes. S3 Select is legacy. Athena is the SQL answer.

```bash
aws s3api create-bucket --bucket "$BUCKET" --region us-east-1
aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket "$BUCKET" --versioning-configuration Status=Enabled
aws s3api put-bucket-lifecycle-configuration --bucket "$BUCKET" --lifecycle-configuration file://life.json
aws s3 presign s3://"$BUCKET"/report.pdf --expires-in 3600
aws s3 cp big.bin s3://"$BUCKET"/incoming/big.bin
```

Requester Pays: the caller pays the transfer. Rare, and it is the answer when a shared dataset should bill the consumer.

## EBS

| Type | Use |
| --- | --- |
| gp3 | Default. IOPS and throughput are set, not bought by growing the disk |
| gp2 | Older. IOPS scale with size. The cost trap |
| io2 Block Express | Highest IOPS and durability. Multi-Attach within one AZ |
| st1 | Throughput HDD, sequential |
| sc1 | Cold HDD, cheapest block |
| Instance store | Ephemeral |

EBS volumes are AZ-scoped. To move: snapshot, then create a volume in the other AZ or copy the snapshot to another Region. Multi-Attach is for io1/io2 and a clustered file system that knows how to share a disk. It is not "attach one ext4 volume to two web servers."

Encryption by default. A snapshot is incremental and crashes consistent enough for many apps. A database still wants its own snapshot coordination or AWS Backup. Data Lifecycle Manager automates EBS snapshots. AWS Backup is the cross-service plan.

## EFS

Shared NFSv4. Mount targets in each AZ. General Purpose performance mode for almost everything. Max I/O is the legacy high-parallel mode.

Throughput: Elastic (default, you pay for what you use), Provisioned (a known baseline), Bursting (older). Storage classes: Standard and Infrequent Access, with lifecycle. EFS One Zone is one AZ and loses the Multi-AZ stem.

EFS is the answer for a fleet that must see the same files. It is not faster than EBS for a single-instance database.

## FSx

| Product | Protocol | Stem |
| --- | --- | --- |
| Windows File Server | SMB, AD, DFS | Lift a Windows share. Multi-AZ is an option |
| Lustre | Lustre, linked to S3 | HPC, ML training sets |
| NetApp ONTAP | NFS, SMB, iSCSI | Multi-protocol, snapshots, a NetApp team |
| OpenZFS | NFS | Linux snapshots and clones |

## AWS Backup

One plan, many services: EBS, RDS, Aurora, DynamoDB, EFS, FSx, S3, and others. A vault in another account, a vault lock (governance or compliance) for ransomware, and a copy action to a second Region. Backup is the answer when the stem lists more than one service and wants one retention policy. Native snapshots are the answer when it is only EBS or only RDS and they want the simplest thing.

PITR on DynamoDB and RDS is continuous. A daily snapshot's RPO is up to 24 hours. Match the RPO.

## Storage Gateway and the hybrid file pattern

File Gateway: NFS or SMB appliance, cache on premises, durable copy in S3. Volume Gateway stored: the full volume is on premises and asynchronously backed up. Volume Gateway cached: the hot set is on premises, the volume lives in S3. Tape Gateway: virtual tapes to S3 and Glacier.

DataSync is the online copy. Gateway is the ongoing protocol endpoint. Do not pick Gateway for a one-time migration of a file server if DataSync can finish it.

## Exercises

1. Access pattern is unknown. The CFO wants cost to follow access without a project to classify objects. Which S3 class?
2. A bucket must keep financial PDFs for seven years even if the root user is compromised. Which two features?
3. An EBS gp2 volume was grown to 2 TB only to buy IOPS. What do you change?
4. Two EC2 instances in different AZs must share a Linux home directory. EBS Multi-Attach or EFS?
5. RPO is 5 minutes for DynamoDB and RDS and EFS together, with one operational plan. Native snapshots per service, or AWS Backup?

## Answers

1. S3 Intelligent-Tiering. A lifecycle to Glacier is the answer when they know the age at which objects go cold.
2. Versioning plus Object Lock in compliance mode. A vault lock on Backup helps backups. The stem is about the PDFs themselves remaining undeletable.
3. gp3, set the IOPS and throughput you need, shrink the size to the data. Snapshot first.
4. EFS. Multi-Attach is one AZ and wants a cluster-aware file system. Two AZs means EFS.
5. AWS Backup with continuous backup or a plan whose RPO is inside 5 minutes for the services that support PITR, plus a copy rule. A nightly snapshot misses the RPO. Say so if a service in the list cannot do 5 minutes, and use that service's native continuous backup inside the same Backup plan where it is supported.

## S3, the mechanics the table skipped

Durability of Standard, Standard-IA, Intelligent-Tiering, Glacier classes other than One Zone, and the Multi-AZ story is "loss of one AZ is already in the design." One Zone-IA and S3 Express One Zone are one Availability Zone. They are cheaper or faster and they fail a stem that says the only copy must survive an AZ.

Consistency is read-after-write for new objects and strong for overwrites and deletes. You do not add a cache-busting design because you fear S3 will serve a stale object after a successful PUT. You do add CloudFront invalidation or a versioned object key, because CloudFront will serve the cached bytes.

| Class | Minimum storage duration that matters | Retrieval |
| --- | --- | --- |
| Standard | None | Milliseconds |
| Intelligent-Tiering | A monitoring fee per object. Small objects can cost more to monitor than to store | Milliseconds on the frequent tiers. Archive tiers inside Intelligent-Tiering are optional and slow |
| Standard-IA, One Zone-IA | 30 days | Milliseconds, plus a retrieval fee |
| Glacier Instant Retrieval | 90 days | Milliseconds |
| Glacier Flexible Retrieval | 90 days | Minutes to hours. Expedited, standard, bulk |
| Glacier Deep Archive | 180 days | Hours. The cheapest |

A lifecycle transition into IA before day 30 is the wasted minimum charge. A transition into Deep Archive for data read the next morning is the wrong class. Intelligent-Tiering is the unknown pattern. A lifecycle to a Glacier class is the known cold date.

Multipart upload is required as objects approach 5 GB and is the right way to send anything large. Parts can fail and be retried. Incomplete parts are billed until a lifecycle rule aborts them. The object is not visible until you complete the multipart upload. A crash halfway leaves parts, not an object.

Encryption:

| Header or default | What it is |
| --- | --- |
| Bucket default SSE-S3 (`AES256`) | Encrypts even when the client sends no header |
| `aws:kms` plus a key id | SSE-KMS. The key policy and `kms:Decrypt` apply. A bucket key cuts KMS request cost and does not change who can decrypt |
| `x-amz-server-side-encryption: aws:kms` required by a bucket policy | A put without that header is denied, which is stricter than a default |
| SSE-C | You send the key on every request. AWS does not store it. Easy to lose |
| Client-side | AWS stores ciphertext. S3 Select and some analytics cannot read it |

A default does not rewrite old objects. Copy the object onto itself with the new encryption arguments. Replication can copy to a bucket with a different key.

Block Public Access has four flags: block public ACLs, ignore public ACLs, block public policies, restrict public buckets. Set them on the account and on the bucket. A policy with `Principal: "*"` does not become a public object while the account block is on. The partner path is an explicit principal or a presigned URL. Presigned URLs are the credentials of the signer, time-limited, for a caller who has no AWS account. They are not a year-long integration.

Object Ownership "Bucket owner enforced" disables ACLs. New designs use it. An item about `AllUsers` on an ACL is the old world. The fix is still the block, plus stop using ACLs.

Versioning keeps every overwrite and every delete marker. Without a noncurrent expiration you pay forever, and you also keep the secret you overwrote, which is a security problem and a cost problem. MFA delete is a versioning feature that requires the root MFA to delete a version. It is rare and it is the "even a stolen IAM key cannot delete versions" answer. Object Lock is stronger and is the regulator answer.

Object Lock must be thought about at bucket creation for the exam story. Compliance mode cannot be shortened, including by root. Governance mode can be bypassed by a principal you explicitly allow. Legal hold is independent of the retention date. A lifecycle expiration does not delete a locked version. Do not enable compliance mode on a lab bucket.

Replication. CRR and SRR copy new objects asynchronously. Replication Time Control is the 15-minute RPO feature, and it is not on by default. Existing objects need a batch replication job. Delete markers and replica ownership are configuration. Replication is not a backup: if you delete the source and the delete replicates, the replica is gone too, unless you blocked delete replication. A backup vault or Object Lock in another account is the ransomware copy. CRR is the Regional availability copy.

Other S3 features that decide items:

| Feature | Stem |
| --- | --- |
| S3 Inventory | You need a list of billions of keys. `ListObjects` pagination is the wrong tool |
| Storage Lens | Which buckets are cold, unencrypted, or full of incomplete uploads |
| Access Points | Many teams share one bucket and each gets its own policy and endpoint |
| Multi-Region Access Point | A single global endpoint that routes to Regional buckets. Not a cache. CloudFront is still the cache |
| Object Lambda | Transform the bytes on the way out. Rare. Recognize it |
| Event notifications | To Lambda, SQS, SNS, or EventBridge. EventBridge when many teams react. SQS when the worker needs a backlog |
| Transfer Acceleration | Long-distance upload via the edge network. Costs extra. Useless in-Region |
| Requester Pays | Callers in other accounts pay the transfer |
| S3 Select | SQL on one object. Athena is SQL on the lake |

A gateway endpoint is the private path from a VPC. It is free of hourly charge and it is not an internet path.

## EBS

A volume is one Availability Zone. Snapshots are stored in S3 and can become a volume in another AZ. A snapshot is crash-consistent unless you quiesce the filesystem or use a backup-aware agent. Fast snapshot restore is a performance feature for the restore, not a durability feature.

| Type | What you set | Exam use |
| --- | --- | --- |
| gp3 | IOPS and throughput independent of size. Baseline is already enough for many apps | The cost and performance default. Replace gp2 that was grown to buy IOPS |
| gp2 | IOPS scale with size, plus burst credits | The legacy volume in the stem. The incident is burst-credit exhaustion, the same shape as a T instance |
| io2 / io2 Block Express | Provisioned IOPS, higher durability | The number is high and they named durability |
| st1 | Throughput HDD | Big sequential logs. Not a boot volume. Not a database |
| sc1 | Cold HDD | Colder sequential data. Cheaper. Still not a boot volume |

Encryption is set on the volume. A snapshot of an encrypted volume is encrypted with the same key. Sharing the snapshot across accounts means sharing the key. You cannot unencrypt by copying unless you copy through a path the docs allow. The usual exam path for "this volume is not encrypted" is snapshot, copy encrypted, create a volume, swap. Account-level "encrypt new EBS volumes by default" stops the next one. It does not rewrite the old one.

Multi-Attach is for io1 and io2 in a single AZ, and the filesystem must understand multiple writers. It is not shared storage across AZs. Two instances in two AZs is EFS or FSx, or S3.

Instance store is local to the host. It can be faster. It disappears when the instance stops, and it is not a snapshot story. The durable copy is elsewhere. A database whose only files are on instance store fails every resilience stem.

## EFS, stated as limits rather than adjectives

General Purpose is the latency mode you want. Max I/O is the older high-parallelism mode with higher latency. Elastic throughput is the default you pay as you use. Provisioned throughput is a known baseline. Bursting throughput runs out of credits the way gp2 does, and the symptom is a filesystem that is "randomly slow" in the afternoon.

Mount targets are per AZ. An instance mounts the target in its own AZ so you do not pay cross-AZ for the mount. The security group on the mount target must allow NFS from the instance security group. EFS is Multi-AZ with Standard storage. EFS One Zone is one AZ and loses the stem that says the share must survive an AZ.

EFS is not a database disk. It is a shared POSIX tree. It is slower than EBS for a single writer that does not need to share.

## FSx, which product

Windows File Server speaks SMB, joins AD, supports DFS and shadow copies. Multi-AZ is the availability option. SSD versus HDD is performance versus cost. This is the lift of `\\fileserver\share` when NTFS ACLs must remain.

Lustre is the HPC and training filesystem, usually linked to an S3 bucket so the dataset lives in S3 and the hot performance lives on Lustre. It is not a home directory.

ONTAP is NFS, SMB, and iSCSI, with snapshots and SnapMirror, for a team that already runs NetApp. OpenZFS is NFS with ZFS snapshots and clones. If the stem does not name NetApp or ZFS, the Linux answer is EFS and the Windows answer is FSx for Windows.

## Backup, Gateway, DataSync

AWS Backup is one plan across services, with a vault, a vault lock, and a copy to another Region or another account. Vault lock in compliance mode is the "even we cannot delete the recovery points early" control. Governance mode can be bypassed by a privileged user. Native snapshots remain right when the stem is one EBS volume and they want the fewest moving parts. PITR on RDS, Aurora, and DynamoDB is continuous. A daily backup plan has an RPO of up to 24 hours. Say that when they asked for five minutes.

File Gateway is an ongoing NFS or SMB appliance whose durable data is S3. Volume Gateway stored keeps the full volume on premises and backs it up. Volume Gateway cached keeps the hot set on premises. Tape Gateway is virtual tapes. DataSync is the copy with verification and a schedule. Gateway is the protocol endpoint you leave in place. Snow is the ship-a-device path when the link cannot finish. Transfer Family is SFTP into S3. Transfer Acceleration is not a migration appliance.

## Commands

```bash
aws s3api put-bucket-versioning --bucket "$BUCKET" --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"'"$KEY"'"},"BucketKeyEnabled":true}]}'
aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api copy-object --bucket "$BUCKET" --key notes.txt --copy-source "$BUCKET/notes.txt" \
  --server-side-encryption aws:kms --ssekms-key-id "$KEY" --metadata-directive COPY
aws ec2 create-volume --availability-zone us-east-1a --volume-type gp3 --size 200 --iops 12000 --throughput 250
aws ec2 create-snapshot --volume-id vol-xxxx --description before-encrypt
aws backup create-backup-plan --backup-plan file://plan.json
aws backup start-restore-job --recovery-point-arn "$ARN" --metadata file://meta.json --iam-role-arn "$ROLE"
```

`copy-object` onto the same key is how you re-encrypt in place. It creates a new version if versioning is on. It is not instantaneous for a huge object. Multipart copy is the large-object version.

## More exercises

6. A successful PUT is immediately GET, and the GET returns the old bytes. The client is CloudFront. Is this S3 consistency, and what do you change?
7. CRR is on. An attacker with a delete on the source key removes the object. Does the replica save you? What configuration would?
8. Two writers in one AZ must share an io2 volume with a cluster filesystem. Two writers in two AZs must share a home directory. Which feature for which?
9. The only copy of uploads is in S3 One Zone-IA because it was cheaper. The stem now says an AZ failure must not lose uploads. Which class?
10. A lifecycle moves objects to Standard-IA after one day. Why is that a bad rule even if the console accepts a version of it?
11. Ransomware deletes backups in the same account as the application. Name the vault feature and the account split.
12. File Gateway, DataSync, or Snow: 90 TB, a 50 Mbps link, users must keep using SMB against the same data after the copy, and the copy itself cannot wait on the link.

## Answers

6. No. S3 is strongly consistent. CloudFront cached the old object. Invalidate the path or use a new object key when the content changes. Lowering the cache TTL is the ongoing version.
7. Not if delete markers replicate, which is a common configuration. The replica deletes too. Block replication of deletes, and keep a versioned, Object Locked copy in another account that the application role cannot delete. CRR alone is not a backup.
8. Multi-Attach for the single-AZ io2 cluster filesystem. EFS for the two-AZ home directory. Multi-Attach does not cross AZs.
9. Standard, or Standard-IA if the access is infrequent and you still need Multi-AZ. One Zone-IA is allowed to die with the AZ. It is only correct for data you can recreate.
10. Standard-IA has a 30-day minimum storage duration. Moving on day 1 bills you as if the object stayed, or the transition is the wrong tool. Wait until day 30, or use Intelligent-Tiering if you do not actually know the pattern.
11. AWS Backup vault lock in compliance mode, in a vault that lives in a different account, with a vault policy the application account cannot change. A copy action sends recovery points there. A backup in the application account with the application admin is what ransomware deletes first.
12. Snow for the 90 TB, because 50 Mbps cannot finish it in a reasonable window. DataSync for the last delta if the source is still changing. File Gateway if users must keep an SMB mount whose durable store is S3. If they need the original NTFS ACLs unchanged, FSx for Windows is the landing zone instead of File Gateway, and Snow or DataSync still does the bulk move. The link is why Snow is in the answer at all.
