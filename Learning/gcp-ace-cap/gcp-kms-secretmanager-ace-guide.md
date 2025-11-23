# Google Cloud KMS & Secret Manager - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Cloud KMS Fundamentals](#cloud-kms-fundamentals)
3. [Secret Manager Fundamentals](#secret-manager-fundamentals)
4. [Creating & Managing Keys](#creating--managing-keys)
5. [Creating & Managing Secrets](#creating--managing-secrets)
6. [Encryption Operations](#encryption-operations)
7. [Access Control & IAM](#access-control--iam)
8. [Best Practices](#best-practices)
9. [Integration Examples](#integration-examples)
10. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

### Cloud KMS (Key Management Service)

**Cloud KMS** is a fully managed service for creating, using, rotating, and destroying cryptographic keys:
- **Symmetric** and **asymmetric** encryption keys
- **Hardware Security Module (HSM)** backed keys
- **Automatic key rotation**
- **Centralized key management**
- Integration with GCP services (Cloud Storage, Compute Engine, etc.)

### Secret Manager

**Secret Manager** is a secure service for storing API keys, passwords, certificates, and other sensitive data:
- **Versioned secrets** (multiple versions per secret)
- **Automatic replication** (regional or multi-regional)
- **Audit logging** for all access
- **IAM-based access control**
- Integration with Cloud Functions, Compute Engine, GKE

### Key Differences

| Feature | Cloud KMS | Secret Manager |
|---------|-----------|----------------|
| **Purpose** | Encrypt/decrypt data | Store sensitive strings |
| **Use Case** | Encryption keys, signing | API keys, passwords, certificates |
| **Data Type** | Binary keys | Text/binary secrets |
| **Operations** | Encrypt, decrypt, sign | Store, retrieve versions |
| **Rotation** | Automatic (keys) | Manual (secrets) |

### When to Use Each

**Cloud KMS:**
- Encrypt data at rest (CMEK for Cloud Storage, Compute Engine)
- Sign/verify digital signatures
- Manage encryption keys
- Comply with key management regulations

**Secret Manager:**
- Store API keys, OAuth tokens
- Manage database passwords
- Store SSL/TLS certificates
- Application configuration secrets

---

## Cloud KMS Fundamentals

### Core Concepts

```
Organization/Project
└── Key Ring (location-bound, e.g., us-central1)
    └── Key (e.g., my-encryption-key)
        └── Key Version (1, 2, 3...)
            └── Cryptographic material
```

### Key Components

**Key Ring:**
- Container for keys in a specific location
- Cannot be deleted (only keys can be disabled/destroyed)
- Named resource (e.g., `my-key-ring`)

**Key:**
- Cryptographic key with multiple versions
- Purpose: Encryption/decryption or signing/verification
- Rotation schedule (optional)

**Key Version:**
- Specific cryptographic material
- Primary version used for new operations
- Old versions available for decryption

### Key Types

| Type | Algorithm | Use Case |
|------|-----------|----------|
| **Symmetric** | AES-256 | Bulk encryption (default) |
| **Asymmetric Encryption** | RSA 2048/3072/4096 | Public-key encryption |
| **Asymmetric Signing** | RSA/EC (ECDSA) | Digital signatures |
| **MAC** | HMAC-SHA256 | Message authentication |

### Protection Levels

| Level | Description | Cost | Security |
|-------|-------------|------|----------|
| **Software** | Software-based keys | Low | Standard |
| **HSM** | Hardware Security Module | Medium | High (FIPS 140-2 Level 3) |
| **External** | Keys stored outside GCP | High | Customer-controlled |

---

## Secret Manager Fundamentals

### Core Concepts

```
Project
└── Secret (e.g., database-password)
    └── Version 1 (older)
    └── Version 2 (current, enabled)
    └── Version 3 (latest)
```

### Secret Components

**Secret:**
- Named container for secret versions
- Replication policy (automatic or user-managed)
- Labels for organization

**Secret Version:**
- Immutable payload (text or binary)
- State: Enabled, Disabled, or Destroyed
- Can be accessed by version number or alias ("latest")

### Replication Options

**Automatic Replication:**
```
Secret replicated to all regions automatically
└── Region 1 (replica)
└── Region 2 (replica)
└── Region 3 (replica)
```
- **Use for:** High availability, global apps
- **Cost:** Standard pricing

**User-Managed Replication:**
```
Secret replicated to specified regions only
└── us-central1 (replica)
└── us-east1 (replica)
```
- **Use for:** Data residency, cost optimization
- **Cost:** Lower (fewer replicas)

---

## Creating & Managing Keys

### Creating Key Rings

**Console:**
1. Navigate to **Security** > **Key Management**
2. Click **Create Key Ring**
3. Enter name (e.g., `my-key-ring`)
4. Select location (e.g., `us-central1`)
5. Click **Create**

**gcloud:**
```bash
# Create key ring in us-central1
gcloud kms keyrings create my-key-ring \
    --location=us-central1
```

### Creating Keys

**Symmetric Encryption Key:**
```bash
gcloud kms keys create my-encryption-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --purpose=encryption
```

**HSM-Backed Key:**
```bash
gcloud kms keys create my-hsm-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --purpose=encryption \
    --protection-level=hsm
```

**Asymmetric Signing Key:**
```bash
gcloud kms keys create my-signing-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --purpose=asymmetric-signing \
    --default-algorithm=rsa-sign-pkcs1-4096-sha512
```

### Key Rotation

**Automatic Rotation:**
```bash
# Enable automatic rotation (every 90 days)
gcloud kms keys update my-encryption-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --rotation-period=90d \
    --next-rotation-time=2024-12-01T00:00:00Z
```

**Manual Rotation:**
```bash
# Create new key version (becomes primary)
gcloud kms keys versions create \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-encryption-key

# Set specific version as primary
gcloud kms keys set-primary-version my-encryption-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --version=2
```

### Disabling and Destroying Keys

**Disable Key Version:**
```bash
# Disable (can be re-enabled)
gcloud kms keys versions disable 1 \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-encryption-key
```

**Schedule Destruction:**
```bash
# Schedule for destruction (24 hours minimum, 30 days recommended)
gcloud kms keys versions destroy 1 \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-encryption-key
```

**Note:** Key destruction is irreversible after the scheduled time!

---

## Creating & Managing Secrets

### Creating Secrets

**Console:**
1. Navigate to **Security** > **Secret Manager**
2. Click **Create Secret**
3. Enter name (e.g., `database-password`)
4. Enter secret value
5. Choose replication (automatic or user-managed)
6. Click **Create Secret**

**gcloud:**
```bash
# Create secret with automatic replication
echo -n "my-secret-password" | gcloud secrets create database-password \
    --data-file=- \
    --replication-policy="automatic"

# Create secret with user-managed replication
echo -n "my-api-key" | gcloud secrets create api-key \
    --data-file=- \
    --replication-policy="user-managed" \
    --locations="us-central1,us-east1"
```

**From File:**
```bash
# Store certificate from file
gcloud secrets create ssl-certificate \
    --data-file=./certificate.pem \
    --replication-policy="automatic"
```

### Adding Secret Versions

```bash
# Add new version
echo -n "new-password-v2" | gcloud secrets versions add database-password \
    --data-file=-

# List versions
gcloud secrets versions list database-password
```

### Accessing Secrets

**Get Latest Version:**
```bash
gcloud secrets versions access latest --secret=database-password
```

**Get Specific Version:**
```bash
gcloud secrets versions access 3 --secret=database-password
```

**Save to File:**
```bash
gcloud secrets versions access latest \
    --secret=ssl-certificate > certificate.pem
```

### Managing Secret Versions

**Disable Version:**
```bash
gcloud secrets versions disable 1 --secret=database-password
```

**Enable Version:**
```bash
gcloud secrets versions enable 1 --secret=database-password
```

**Destroy Version:**
```bash
gcloud secrets versions destroy 1 --secret=database-password
```

**Delete Entire Secret:**
```bash
gcloud secrets delete database-password
```

---

## Encryption Operations

### Encrypting Data

**Encrypt String:**
```bash
# Encrypt plaintext
echo -n "sensitive data" | gcloud kms encrypt \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-encryption-key \
    --plaintext-file=- \
    --ciphertext-file=encrypted.bin
```

**Encrypt File:**
```bash
gcloud kms encrypt \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-encryption-key \
    --plaintext-file=plaintext.txt \
    --ciphertext-file=ciphertext.bin
```

### Decrypting Data

```bash
# Decrypt to stdout
gcloud kms decrypt \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-encryption-key \
    --ciphertext-file=ciphertext.bin \
    --plaintext-file=-

# Decrypt to file
gcloud kms decrypt \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-encryption-key \
    --ciphertext-file=ciphertext.bin \
    --plaintext-file=decrypted.txt
```

### Signing and Verification (Asymmetric Keys)

**Create Signature:**
```bash
# Create signature for file
gcloud kms asymmetric-sign \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-signing-key \
    --version=1 \
    --digest-algorithm=sha512 \
    --input-file=document.pdf \
    --signature-file=signature.bin
```

**Verify Signature:**
```bash
# Verify signature
gcloud kms asymmetric-verify \
    --location=us-central1 \
    --keyring=my-key-ring \
    --key=my-signing-key \
    --version=1 \
    --digest-algorithm=sha512 \
    --input-file=document.pdf \
    --signature-file=signature.bin
```

---

## Access Control & IAM

### KMS IAM Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **roles/cloudkms.admin** | Full access to KMS | Administrators |
| **roles/cloudkms.cryptoKeyEncrypter** | Encrypt only | Applications encrypting data |
| **roles/cloudkms.cryptoKeyDecrypter** | Decrypt only | Applications decrypting data |
| **roles/cloudkms.cryptoKeyEncrypterDecrypter** | Encrypt and decrypt | Full encryption operations |
| **roles/cloudkms.signer** | Sign data | Digital signature applications |
| **roles/cloudkms.signerVerifier** | Sign and verify | Signing and verification |
| **roles/cloudkms.viewer** | View keys (no operations) | Auditors |

### Granting KMS Access

**Grant Encrypt Permission:**
```bash
gcloud kms keys add-iam-policy-binding my-encryption-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --member=serviceAccount:app@project.iam.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyEncrypter
```

**Grant Decrypt Permission:**
```bash
gcloud kms keys add-iam-policy-binding my-encryption-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --member=serviceAccount:app@project.iam.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyDecrypter
```

### Secret Manager IAM Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **roles/secretmanager.admin** | Full access | Administrators |
| **roles/secretmanager.secretAccessor** | Read secret values | Applications reading secrets |
| **roles/secretmanager.secretVersionAdder** | Add new versions | CI/CD pipelines |
| **roles/secretmanager.viewer** | View metadata (no values) | Auditors |

### Granting Secret Access

**Grant Read Access:**
```bash
gcloud secrets add-iam-policy-binding database-password \
    --member=serviceAccount:app@project.iam.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor
```

**Grant Version Management:**
```bash
gcloud secrets add-iam-policy-binding api-key \
    --member=serviceAccount:deploy@project.iam.gserviceaccount.com \
    --role=roles/secretmanager.secretVersionAdder
```

---

## Best Practices

### KMS Best Practices

1. **Use Separate Keys for Different Purposes:**
   - One key for Cloud Storage encryption
   - Another key for Compute Engine disk encryption
   - Separate keys per environment (dev, staging, prod)

2. **Enable Automatic Rotation:**
   ```bash
   gcloud kms keys update my-key \
       --location=us-central1 \
       --keyring=my-key-ring \
       --rotation-period=90d
   ```

3. **Use HSM for Highly Sensitive Data:**
   - Financial data, healthcare records
   - Compliance requirements (PCI-DSS, HIPAA)

4. **Implement Least Privilege:**
   - Separate encrypt/decrypt permissions
   - Grant only necessary roles

5. **Monitor Key Usage:**
   - Enable Cloud Audit Logs
   - Set up alerts for unusual activity

### Secret Manager Best Practices

1. **Use Version Labels:**
   ```bash
   gcloud secrets versions add database-password \
       --data-file=- \
       --labels=environment=production,version=v2
   ```

2. **Rotate Secrets Regularly:**
   - Database passwords: Every 90 days
   - API keys: When compromised or annually
   - Certificates: Before expiration

3. **Use User-Managed Replication for Sensitive Data:**
   ```bash
   gcloud secrets create highly-sensitive \
       --data-file=secret.txt \
       --replication-policy="user-managed" \
       --locations="us-central1"  # Only one region
   ```

4. **Never Hardcode Secrets:**
   ```python
   # ❌ Bad
   PASSWORD = "my-secret-password"
   
   # ✅ Good
   from google.cloud import secretmanager
   client = secretmanager.SecretManagerServiceClient()
   name = f"projects/{project_id}/secrets/database-password/versions/latest"
   response = client.access_secret_version(request={"name": name})
   PASSWORD = response.payload.data.decode('UTF-8')
   ```

5. **Implement Secret Expiration Policy:**
   - Add metadata about expiration dates
   - Automate rotation with Cloud Functions

---

## Integration Examples

### Cloud Storage with CMEK

**Create Bucket with Customer-Managed Encryption:**
```bash
# Grant Cloud Storage service account access to key
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")

gcloud kms keys add-iam-policy-binding my-encryption-key \
    --location=us-central1 \
    --keyring=my-key-ring \
    --member=serviceAccount:service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyEncrypterDecrypter

# Create bucket with CMEK
gsutil mb -l us-central1 gs://my-encrypted-bucket

gsutil kms authorize \
    -k projects/PROJECT_ID/locations/us-central1/keyRings/my-key-ring/cryptoKeys/my-encryption-key

gsutil kms encryption \
    -k projects/PROJECT_ID/locations/us-central1/keyRings/my-key-ring/cryptoKeys/my-encryption-key \
    gs://my-encrypted-bucket
```

### Compute Engine with CMEK

**Create Disk Encrypted with CMEK:**
```bash
gcloud compute disks create my-encrypted-disk \
    --size=100GB \
    --zone=us-central1-a \
    --kms-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-key-ring/cryptoKeys/my-encryption-key
```

### Cloud Functions with Secret Manager

**Python Example:**
```python
from google.cloud import secretmanager

def access_secret():
    client = secretmanager.SecretManagerServiceClient()
    project_id = "my-project"
    secret_id = "database-password"
    
    # Access latest version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    
    secret_value = response.payload.data.decode('UTF-8')
    return secret_value

# Use in Cloud Function
def my_function(request):
    db_password = access_secret()
    # Connect to database using password
    return "Connected successfully"
```

**Node.js Example:**
```javascript
const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');

async function accessSecret() {
  const client = new SecretManagerServiceClient();
  const projectId = 'my-project';
  const secretId = 'api-key';
  
  const name = `projects/${projectId}/secrets/${secretId}/versions/latest`;
  const [version] = await client.accessSecretVersion({ name });
  
  const secretValue = version.payload.data.toString();
  return secretValue;
}

// Use in Cloud Function
exports.myFunction = async (req, res) => {
  const apiKey = await accessSecret();
  // Use API key
  res.send('Success');
};
```

### GKE with Secret Manager

**Mount Secret as Volume:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  serviceAccountName: app-sa
  volumes:
  - name: database-password
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "database-secret-provider"
  containers:
  - name: app
    image: gcr.io/my-project/app:latest
    volumeMounts:
    - name: database-password
      mountPath: "/etc/secrets"
      readOnly: true
```

---

## ACE Exam Tips

### Key Concepts to Remember

1. **KMS vs Secret Manager:**
   - KMS: Encryption keys, automatic rotation
   - Secret Manager: API keys, passwords, manual rotation

2. **Key Rotation:**
   - KMS: Automatic (configure rotation period)
   - Secret Manager: Manual (add new versions)

3. **Protection Levels:**
   - Software: Standard, lower cost
   - HSM: FIPS 140-2 Level 3, compliance

4. **IAM Roles:**
   - **cryptoKeyEncrypter:** Encrypt only
   - **cryptoKeyDecrypter:** Decrypt only
   - **secretAccessor:** Read secret values

5. **CMEK (Customer-Managed Encryption Keys):**
   - Use KMS keys for Cloud Storage, Compute Engine
   - Service account needs cryptoKeyEncrypterDecrypter role

6. **Secret Replication:**
   - Automatic: All regions (high availability)
   - User-managed: Specific regions (data residency)

7. **Key Deletion:**
   - Key rings cannot be deleted
   - Keys can be disabled or scheduled for destruction
   - Destruction is irreversible (24 hours minimum)

### Common Exam Scenarios

**Scenario 1:** Need to encrypt Cloud Storage bucket with customer-managed keys
- **Answer:** Create KMS key, grant Cloud Storage service account access, enable CMEK on bucket

**Scenario 2:** Store database password securely for Cloud Function
- **Answer:** Use Secret Manager, grant secretAccessor role to Cloud Function service account

**Scenario 3:** Automatically rotate encryption keys every 90 days
- **Answer:** Configure KMS key with `--rotation-period=90d`

**Scenario 4:** Comply with FIPS 140-2 Level 3 for encryption
- **Answer:** Create HSM-backed KMS key (`--protection-level=hsm`)

**Scenario 5:** Application needs encrypt permission but not decrypt
- **Answer:** Grant `roles/cloudkms.cryptoKeyEncrypter` role

**Scenario 6:** Secret must stay in EU for compliance
- **Answer:** Create secret with user-managed replication in EU regions only

### Essential Commands

```bash
# KMS - Create key ring
gcloud kms keyrings create KEYRING --location=LOCATION

# KMS - Create encryption key
gcloud kms keys create KEY --location=LOCATION --keyring=KEYRING --purpose=encryption

# KMS - Enable rotation
gcloud kms keys update KEY --location=LOCATION --keyring=KEYRING --rotation-period=90d

# KMS - Encrypt file
gcloud kms encrypt --location=LOCATION --keyring=KEYRING --key=KEY \
    --plaintext-file=FILE --ciphertext-file=ENCRYPTED

# Secret Manager - Create secret
echo -n "secret-value" | gcloud secrets create SECRET --data-file=-

# Secret Manager - Access secret
gcloud secrets versions access latest --secret=SECRET

# Grant KMS access
gcloud kms keys add-iam-policy-binding KEY --location=LOCATION --keyring=KEYRING \
    --member=serviceAccount:SA --role=roles/cloudkms.cryptoKeyEncrypterDecrypter

# Grant Secret access
gcloud secrets add-iam-policy-binding SECRET \
    --member=serviceAccount:SA --role=roles/secretmanager.secretAccessor
```

---

## Additional Resources

- [Cloud KMS Documentation](https://cloud.google.com/kms/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Encryption at Rest](https://cloud.google.com/security/encryption-at-rest)
- [Key Management Best Practices](https://cloud.google.com/kms/docs/key-management-best-practices)
- [Secret Manager Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)

---

**Last Updated:** November 2025  
**Exam:** Google Associate Cloud Engineer (ACE)
