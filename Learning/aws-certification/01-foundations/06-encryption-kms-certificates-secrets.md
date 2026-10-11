# Encryption, KMS, certificates, and secrets

SAA 1.3. SAP 1.2 and 2.3. DVA 2.2 and 2.3. SAP-C03 adds ML-DSA and ML-KEM. Confirm key specs in the KMS guide on the day you study them. Identifiers moved during preview.

Official:

- https://docs.aws.amazon.com/kms/latest/developerguide/overview.html
- https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingEncryption.html
- https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html
- https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
- https://docs.aws.amazon.com/cloudhsm/latest/userguide/introduction.html

## Where encryption happens

| Layer | What protects it | Stem language |
| --- | --- | --- |
| In transit | TLS. ACM on ALB, CloudFront, API Gateway, NLB TLS listeners | "Encrypt on the wire" |
| At rest, service-managed | SSE-S3, RDS encryption with an AWS-managed key, DynamoDB default encryption | "Encrypt" with no key-policy requirement |
| At rest, customer managed | SSE-KMS with a CMK you own, EBS encryption with your key | "Disable the key and the data becomes unreadable", "key policy", "cross-account decrypt" |
| Client-side | You encrypt before the SDK sends | "AWS must never see plaintext", a customer-held key outside CloudHSM/KMS |
| Field-level | The application encrypts one attribute | PII in a column, the rest of the row is operational |

SSE-S3 uses keys S3 owns. There is no key policy you can edit and no CloudTrail KMS event for the data key. The moment the stem mentions a key administrator who is not the bucket administrator, you are on SSE-KMS.

## KMS keys

| Key | Who manages it | Rotation | Delete |
| --- | --- | --- | --- |
| AWS owned | AWS, shared across customers of that service | AWS | You cannot |
| AWS managed (`aws/s3`, `aws/ebs`) | AWS, in your account, dedicated to the service | About every year, on AWS's schedule | You cannot |
| Customer managed | You. Key policy, grants, aliases | Automatic once a year if you turn it on, or on-demand | Schedule 7–30 days. The waiting period is your undo |
| Multi-Region | A primary and replicas that share a key id. Encrypt in one Region, decrypt in another | Per primary | You coordinate replica deletion |
| Imported key material | You bring the bytes | You rotate by reimporting | Deleting the material is faster than deleting the key |
| CloudHSM-backed custom key store | KMS API, key material in a CloudHSM cluster you run | Operationally heavy | The stem says FIPS 140-2/3 Level 3 and single-tenant HSM |
| External key store | Key material stays in your HSM outside AWS | Heavier still | "Keys must not be stored in AWS" |

Symmetric `SYMMETRIC_DEFAULT` is the data-encryption key for S3, EBS, and RDS. Asymmetric keys sign or do public-key encrypt and are the wrong default for an S3 bucket.

Post-quantum, from the September 2026 SAP-C03 announcement: KMS supports ML-KEM (key encapsulation) and ML-DSA (signatures). These are the NIST FIPS 203 and FIPS 204 algorithms. Use them when the stem says post-quantum. Do not use them as the bucket default in a scenario that only says "encrypt the objects." Check `aws kms create-key help` for the current `--key-spec` values before you put one in a script.

```bash
KEY=$(aws kms create-key --description orders --key-usage ENCRYPT_DECRYPT \
  --key-spec SYMMETRIC_DEFAULT --query KeyMetadata.KeyId --output text)
aws kms enable-key-rotation --key-id "$KEY"
aws kms create-alias --alias-name alias/orders --target-key-id "$KEY"
aws kms encrypt --key-id alias/orders --plaintext fileb://secret.bin \
  --encryption-context purpose=orders --output text --query CiphertextBlob
```

The key policy is the root allow. An identity policy cannot grant `kms:Decrypt` if the key policy does not allow the account to use IAM policies (`Enable IAM User Permissions` is the standard statement that does this). Cross-account decrypt needs the key policy to name the other account and that account's identity policy to allow the action.

Encryption context is additional authenticated data. It is logged. It is not a secret. Decrypt must present the same context. Use it to bind a ciphertext to a tenant or a purpose.

Grants are temporary, delegable KMS permissions. Services use them so a principal can use a key without a permanent policy edit. You rarely write a grant by hand on the exam. You recognize one in a CloudTrail event.

## S3, EBS, RDS, DynamoDB

```bash
aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration '{
  "Rules": [{
    "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "alias/orders"},
    "BucketKeyEnabled": true
  }]
}'
aws s3api put-bucket-policy --bucket "$BUCKET" --policy file://deny-unencrypted.json
```

A bucket policy that denies `PutObject` when `s3:x-amz-server-side-encryption` is missing forces callers to encrypt. Default encryption covers callers who do not set the header. Use both when the stem is strict.

Bucket keys (`BucketKeyEnabled`) cut KMS request cost on SSE-KMS. They do not change who can decrypt.

EBS encryption by default is an account-Region setting. Snapshots of encrypted volumes are encrypted. Copying a snapshot to another Region can re-encrypt with a key in the destination. Sharing a snapshot shares access to the bits only if you also share the KMS key.

RDS encryption is chosen at create time. You cannot turn it on later in place. Snapshot, copy with encryption, restore. Read replicas of an encrypted instance are encrypted. Cross-Region replicas need a key in the destination Region.

DynamoDB encrypts at rest by default with an AWS owned key. Switch to a customer managed key when the stem wants a key policy. That switch has a table update. TTL and streams do not replace encryption.

## Certificates

| Need | Service |
| --- | --- |
| Public name on CloudFront | ACM in **us-east-1**. CloudFront will not see a cert in another Region |
| Public name on a regional ALB or API Gateway | ACM in the same Region as the load balancer |
| Private names for internal mTLS | AWS Private CA. Public ACM will not issue `db.internal` |
| Exportable private cert for a server that cannot use ACM integration | Private CA, then install the cert. ACM public certs are not exportable |
| Mutual TLS on API Gateway | A trust store you upload, often issued by Private CA |

ACM renews public DNS-validated certs by itself when the record remains. Email validation and privately imported certs are your renewal problem. Imported certs do not auto-renew.

## Secrets Manager and Parameter Store

| | Secrets Manager | Parameter Store |
| --- | --- | --- |
| Size | 64 KB secret string | Standard 4 KB, advanced larger |
| Rotation | Built in, Lambda rotation for RDS, Redshift, DocumentDB, and custom | You write it |
| Cross-Region | Replica secrets | Parameters are regional. You copy them |
| Cost | Per secret per month plus API | Standard parameters are free. Advanced and higher throughput cost |
| Stem | Database password, API key that rotates, multi-AZ RDS rotation | Config, AMI id, feature flag, a SecureString that rarely changes |

```bash
aws secretsmanager create-secret --name orders/db --secret-string '{"username":"app","password":"change-me"}'
aws secretsmanager rotate-secret --secret-id orders/db --rotation-lambda-arn "$FN" \
  --rotation-rules AutomaticallyAfterDays=30
aws ssm put-parameter --name /orders/log-level --value INFO --type String
aws ssm put-parameter --name /orders/license --value "$TOKEN" --type SecureString --key-id alias/orders
aws ssm get-parameter --name /orders/license --with-decryption
```

Lambda environment variables are visible to anyone who can `lambda:GetFunctionConfiguration`. A customer-managed key encrypts them at rest and requires `kms:Decrypt` on the execution role. Prefer Secrets Manager when the value rotates. DVA skill 2.3.2 is the KMS-on-env-var path. Skill 2.3.3 is the secret-service path.

## CloudHSM versus KMS

KMS is the default. CloudHSM is a cluster you patch the client for, that lives in one Region, that you scale yourself, that satisfies a rule that the key must live in a dedicated HSM. "We need encryption" is KMS. "The auditor requires FIPS 140-3 Level 3 in a dedicated module, and our PKCS#11 app already speaks CloudHSM" is CloudHSM. You can also point a KMS custom key store at CloudHSM if you want the KMS API and the dedicated module.

## Exercises

1. Objects must be unreadable within minutes of a security decision, by a person who cannot delete the objects. Which control?
2. A CloudFront distribution in front of an ALB. The ACM cert for the distribution was requested in `eu-west-1`. What fails?
3. A Lambda in account A reads SSE-KMS objects in account B. List every policy that must allow the read.
4. RDS was created unencrypted. The application must stay on RDS. How do you encrypt it?
5. The stem says post-quantum signatures on artifacts the company will still need to verify in 15 years. Which KMS algorithm family does the SAP-C03 announcement name?
6. A team stores the database password in SSM Parameter Store as a `String`. What is wrong, and when would you still refuse SecureString in favor of Secrets Manager?

## Answers

1. A customer managed KMS key, and you disable the key. Object Lock would stop deletion. It would not make the bytes unreadable. SSE-S3 gives you no key to disable.
2. CloudFront only uses ACM certs from us-east-1. Request the cert there and attach it. The ALB's own cert, if users also hit the ALB, stays in the ALB's Region.
3. Bucket policy in B allows the role. Identity policy on the role in A allows `s3:GetObject`. Key policy in B allows the role. Identity policy in A allows `kms:Decrypt`. The role is the Lambda execution role, not a key in the code.
4. Snapshot, copy the snapshot with encryption enabled, restore a new instance, cut the application over, retire the old instance. There is no in-place flag.
5. ML-DSA. ML-KEM is the encapsulation algorithm, used to establish keys, not the long-term signature algorithm.
6. A `String` is plaintext. `SecureString` encrypts with KMS. Secrets Manager still wins when the password must rotate on a schedule, replicate across Regions, or come from the RDS rotation integration.

## KMS, the calls

`GenerateDataKey` returns a plaintext data key and a ciphertext copy. The service encrypts the object with the plaintext key and stores the ciphertext key next to the object. `Decrypt` unwraps it. You almost never call `Encrypt` on a multi-gigabyte object. S3, EBS, and RDS call these for you when you choose SSE-KMS.

A key policy that does not trust the account means IAM policies in the account cannot grant use of the key. Leave an admin statement. Grants are a delegated, revocable permission used by services. Encryption context is a set of pairs that must match on decrypt. Use it so a key that encrypts a bucket cannot decrypt a different bucket's objects by mistake.

Rotation of a customer managed symmetric key creates new material for new encrypt operations. Old ciphertext still decrypts. Turning rotation on does not rewrite the bucket. Imported key material is your rotation problem. Asymmetric keys and HMAC keys do not use the same annual rotation switch. Disabling a key stops decrypt and is reversible. Scheduling deletion waits 7 to 30 days and then the ciphertext is unrecoverable. Disable first.

Multi-Region keys share a key id across Regions so the same ciphertext can be decrypted after a Regional failover. Use them when the stem requires that. Otherwise a key per Region is the smaller blast radius.

S3 bucket keys reduce KMS request volume. They do not change authorization.

## Certificates and secrets

Public ACM certificates attach to ALB, API Gateway, and CloudFront. CloudFront's certificate is in `us-east-1`. The ALB's certificate is in the ALB's Region. DNS validation is the one that renews without you copying files onto instances. Email validation is the one that expires when the mailbox is ignored. Public ACM certificates are not exported onto a random nginx except for the specific cases AWS documents (Nitro Enclaves and a few others). A server you manage uses Private CA or a certificate you install.

Private CA issues names public ACM will not: `app.corp.internal`. It is not free and it is not the default for a public website.

Secrets Manager stores a secret, rotates it with a Lambda, and can replicate it to another Region. RDS integration rotates the database password. The reader needs `secretsmanager:GetSecretValue` and `kms:Decrypt` if you used a customer managed key. Cache the value in the process until you are near expiry. Do not fetch it on every line, and do not cache it for a week.

Parameter Store `SecureString` is KMS-encrypted configuration that does not need rotation. Standard parameters are free and small. Advanced parameters cost and are larger. A `String` is plaintext. Do not put a password in one.

## More exercises

7. You disable a customer managed key used by an EBS volume. What happens to the instance, and how do you undo it?
8. SSE-S3, SSE-KMS, SSE-C. Which one lets you disable decryption without deleting the object, and which one means you must send the key on every GET?
9. A certificate on an ALB in `ap-southeast-2` and a certificate on CloudFront in front of it. How many ACM requests, in which Regions?
10. The secret rotates. The Lambda cached the password for the life of the environment. What breaks, and what do you change?
11. Two Regions must decrypt the same snapshot after failover. Multi-Region key or a snapshot copy that re-encrypts?

## Answers

7. New attaches and decrypts fail, so a reboot or a detach can leave the volume unreadable. Enable the key again. You did not delete it, so the data is still there. Deletion would have started a waiting period after which this undo does not exist.
8. SSE-KMS with a customer managed key can be disabled. SSE-C requires the client to send the key on every request, and AWS does not store that key. SSE-S3 gives you neither a key to disable nor a key to send.
9. Two. One in `ap-southeast-2` for the ALB. One in `us-east-1` for CloudFront. A single certificate in the ALB's Region will not attach to the distribution.
10. The next rotation invalidates the cached password and the function keeps using the old one until a cold start. Refresh on authentication failure, or cache with a TTL shorter than the rotation interval.
11. Either can work. A multi-Region key decrypts the same ciphertext in the second Region. A snapshot copy with a different key also works and is the smaller blast radius when you do not need one key id. The stem's "same ciphertext, no re-encrypt" sentence is the multi-Region key.
