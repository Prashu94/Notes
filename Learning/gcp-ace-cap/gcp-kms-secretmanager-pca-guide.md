# Google Cloud KMS & Secret Manager - Professional Cloud Architect (PCA) Comprehensive Guide

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Design Decisions & Trade-offs](#design-decisions--trade-offs)
3. [Enterprise Key Management Architecture](#enterprise-key-management-architecture)
4. [Advanced Encryption Patterns](#advanced-encryption-patterns)
5. [Secret Management at Scale](#secret-management-at-scale)
6. [Compliance & Governance](#compliance--governance)
7. [High Availability & Disaster Recovery](#high-availability--disaster-recovery)
8. [Security Architecture](#security-architecture)
9. [Cost Optimization](#cost-optimization)
10. [Integration Patterns](#integration-patterns)
11. [PCA Exam Tips](#pca-exam-tips)

---

## Architectural Overview

Cloud KMS and Secret Manager form the foundation of Google Cloud's cryptographic services, providing centralized key and secret management with enterprise-grade security, compliance, and operational controls.

### Cloud KMS Architecture

```
Organization
├── Folder (dev, staging, prod)
│   └── Project
│       └── Key Ring (regional, e.g., us-central1)
│           └── Crypto Keys
│               ├── Key Version 1 (disabled)
│               ├── Key Version 2 (primary)
│               └── Key Version 3 (enabled)
```

**Core Components:**
- **Key Management Service:** Manages cryptographic keys lifecycle
- **Hardware Security Modules (HSM):** FIPS 140-2 Level 3 certified
- **External Key Manager (EKM):** Keys hosted outside GCP
- **Cloud HSM:** Dedicated HSM instances

### Secret Manager Architecture

```
Project
└── Secrets (global resource)
    ├── Secret A
    │   └── Versions (immutable)
    │       ├── Version 1 (destroyed)
    │       ├── Version 2 (disabled)
    │       └── Version 3 (enabled)
    └── Replication Strategy
        ├── Automatic (multi-region)
        └── User-Managed (specific regions)
```

**Key Features:**
- **Versioning:** Immutable secret versions with lifecycle management
- **Replication:** Automatic or user-managed across regions
- **Audit Logging:** Complete access trail
- **IAM Integration:** Fine-grained access control

### Encryption Hierarchy

```
Root of Trust (Google KMS)
└── KMS Key Encryption Key (KEK)
    └── Data Encryption Key (DEK)
        └── Encrypted Data
```

**Envelope Encryption:**
1. DEK encrypts actual data (fast, local)
2. KEK encrypts DEK (stored in KMS)
3. Encrypted DEK stored with data
4. For decryption: Decrypt DEK with KEK, then decrypt data

---

## Design Decisions & Trade-offs

### Protection Level Comparison

| Protection | Implementation | Latency | Cost | Security | Use Case |
|-----------|----------------|---------|------|----------|----------|
| **Software** | Software keys | 10-50ms | $ | Standard | General encryption |
| **HSM** | Cloud HSM (shared) | 50-100ms | $$ | FIPS 140-2 L3 | Compliance, sensitive data |
| **External (EKM)** | Customer HSM | 100-500ms | $$$ | Customer-controlled | Regulatory, sovereignty |
| **Cloud HSM** | Dedicated HSM | 20-80ms | $$$$ | FIPS 140-2 L3, isolated | Ultra-high security |

### Key Type Selection

**Symmetric Keys (AES-256):**
- **Use for:** Bulk data encryption (default for most cases)
- **Performance:** Fast (hardware accelerated)
- **Key size:** 256 bits
- **Cost:** Low

**Asymmetric Encryption Keys (RSA):**
- **Use for:** Public-key encryption, key exchange
- **Algorithms:** RSA 2048/3072/4096, EC P256/P384
- **Performance:** Slower than symmetric
- **Cost:** Higher

**Asymmetric Signing Keys:**
- **Use for:** Digital signatures, code signing
- **Algorithms:** RSA-PSS, ECDSA, EdDSA
- **Verification:** Fast (public key)
- **Cost:** Medium

**MAC Keys (HMAC):**
- **Use for:** Message authentication codes
- **Algorithms:** HMAC-SHA256
- **Performance:** Very fast
- **Cost:** Low

### Secret Manager Replication Strategy

**Automatic Replication:**
```
Secret replicated globally
├── All regions (high availability)
├── Cost: Higher (multiple replicas)
└── Use: Global apps, maximum availability
```

**User-Managed Replication:**
```
Secret in specific regions
├── us-central1 (primary)
├── us-east1 (secondary)
├── Cost: Lower (controlled replicas)
└── Use: Data residency, compliance, cost optimization
```

**Decision Matrix:**
```
Global app? → Yes → Automatic replication
Data residency requirements? → Yes → User-managed replication
Cost-sensitive? → Yes → User-managed replication (minimum regions)
Maximum availability? → Yes → Automatic replication
```

---

## Enterprise Key Management Architecture

### Multi-Project Key Strategy

**Centralized Key Management:**
```
Organization
├── security-project (KMS keys)
│   ├── prod-keyring
│   │   ├── database-encryption-key
│   │   ├── storage-encryption-key
│   │   └── backup-encryption-key
│   └── dev-keyring
│       └── test-encryption-key
├── app-project-1 (uses keys from security-project)
└── app-project-2 (uses keys from security-project)
```

**Benefits:**
- Centralized key governance
- Separation of duties (security team manages keys)
- Simplified auditing
- Cross-project encryption

**Implementation:**
```bash
# Grant project 1 access to key in security project
gcloud kms keys add-iam-policy-binding database-key \
    --project=security-project \
    --location=us-central1 \
    --keyring=prod-keyring \
    --member=serviceAccount:compute@app-project-1.iam.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyEncrypterDecrypter
```

### Key Hierarchy Pattern

**Root Key → Domain Keys → Application Keys:**
```
root-keyring (organization-level)
├── domain-key-finance
│   ├── app-key-accounting
│   ├── app-key-payroll
│   └── app-key-reporting
└── domain-key-engineering
    ├── app-key-production
    ├── app-key-staging
    └── app-key-development
```

### Key Rotation Strategy

**Automatic Rotation (Recommended):**
```bash
# Set rotation period (90 days recommended)
gcloud kms keys update my-key \
    --location=us-central1 \
    --keyring=my-keyring \
    --rotation-period=90d \
    --next-rotation-time=2024-12-01T00:00:00Z
```

**Manual Rotation (for External Keys):**
```bash
# Create new version
gcloud kms keys versions create \
    --location=us-central1 \
    --keyring=my-keyring \
    --key=my-key

# Set as primary
gcloud kms keys set-primary-version my-key \
    --location=us-central1 \
    --keyring=my-keyring \
    --version=2
```

**Rotation Best Practices:**
- Symmetric keys: 90 days
- Asymmetric keys: 1 year
- External keys: Quarterly
- High-risk keys: 30 days

### Key Versioning Strategy

```
Key: database-encryption-key
├── Version 1 (created: 2024-01-01, disabled)
├── Version 2 (created: 2024-04-01, enabled, decryption only)
├── Version 3 (created: 2024-07-01, primary, encrypt + decrypt)
└── Version 4 (created: 2024-10-01, enabled, decryption only)
```

**Version Lifecycle:**
1. **Primary:** Used for new encryption operations
2. **Enabled:** Can decrypt, but not encrypt
3. **Disabled:** Cannot be used (can be re-enabled)
4. **Scheduled for destruction:** 24 hours to cancel
5. **Destroyed:** Permanently deleted (irreversible)

---

## Advanced Encryption Patterns

### Envelope Encryption Implementation

**Architecture:**
```
Application
├── Generate Data Encryption Key (DEK) locally
├── Encrypt data with DEK (AES-256-GCM)
├── Encrypt DEK with KMS Key Encryption Key (KEK)
├── Store encrypted DEK with encrypted data
└── For decryption:
    ├── Decrypt DEK with KMS
    └── Decrypt data with DEK
```

**Python Implementation:**
```python
from google.cloud import kms
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_with_envelope(plaintext: bytes, kek_path: str) -> dict:
    """Encrypt data using envelope encryption."""
    
    # Generate Data Encryption Key (DEK)
    dek = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(dek)
    nonce = os.urandom(12)
    
    # Encrypt data with DEK
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # Encrypt DEK with KMS KEK
    kms_client = kms.KeyManagementServiceClient()
    encrypt_response = kms_client.encrypt(
        request={'name': kek_path, 'plaintext': dek}
    )
    encrypted_dek = encrypt_response.ciphertext
    
    return {
        'ciphertext': ciphertext,
        'encrypted_dek': encrypted_dek,
        'nonce': nonce
    }

def decrypt_with_envelope(encrypted_data: dict, kek_path: str) -> bytes:
    """Decrypt data using envelope encryption."""
    
    # Decrypt DEK with KMS
    kms_client = kms.KeyManagementServiceClient()
    decrypt_response = kms_client.decrypt(
        request={'name': kek_path, 'ciphertext': encrypted_data['encrypted_dek']}
    )
    dek = decrypt_response.plaintext
    
    # Decrypt data with DEK
    aesgcm = AESGCM(dek)
    plaintext = aesgcm.decrypt(
        encrypted_data['nonce'],
        encrypted_data['ciphertext'],
        None
    )
    
    return plaintext
```

### Client-Side Field-Level Encryption

**Use Case:** Encrypt specific fields before storing in database

```python
from google.cloud import kms, firestore

class FieldEncryption:
    def __init__(self, kms_key_path: str):
        self.kms_client = kms.KeyManagementServiceClient()
        self.key_path = kms_key_path
        
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a single field."""
        response = self.kms_client.encrypt(
            request={
                'name': self.key_path,
                'plaintext': plaintext.encode('utf-8')
            }
        )
        return response.ciphertext.hex()
    
    def decrypt_field(self, ciphertext_hex: str) -> str:
        """Decrypt a single field."""
        ciphertext = bytes.fromhex(ciphertext_hex)
        response = self.kms_client.decrypt(
            request={
                'name': self.key_path,
                'ciphertext': ciphertext
            }
        )
        return response.plaintext.decode('utf-8')

# Usage
db = firestore.Client()
encryptor = FieldEncryption('projects/.../locations/.../keyRings/.../cryptoKeys/...')

# Store encrypted data
user_data = {
    'name': 'Alice',  # Plaintext
    'email': encryptor.encrypt_field('alice@example.com'),  # Encrypted
    'ssn': encryptor.encrypt_field('123-45-6789'),  # Encrypted
}
db.collection('users').document('user123').set(user_data)

# Retrieve and decrypt
doc = db.collection('users').document('user123').get()
data = doc.to_dict()
data['email'] = encryptor.decrypt_field(data['email'])
data['ssn'] = encryptor.decrypt_field(data['ssn'])
```

### External Key Manager (EKM) Pattern

**Architecture:**
```
GCP Services
├── Compute Engine
├── Cloud Storage
└── BigQuery
    ↓ (encryption request)
Cloud KMS EKM Key
    ↓ (forwards to external)
Customer HSM (on-premises or partner)
    ↓ (encryption operation)
Returns result
```

**Setup External Key:**
```bash
# Create EKM connection
gcloud kms ekmconnections create my-ekm-connection \
    --location=us-central1 \
    --hostname=ekm.example.com \
    --certificate-path=ekm-cert.pem

# Create EKM key
gcloud kms keys create my-ekm-key \
    --location=us-central1 \
    --keyring=my-keyring \
    --purpose=encryption \
    --protection-level=external \
    --ekm-connection-key-path="projects/.../ekmConnections/my-ekm-connection/cryptoKeyVersions/1"
```

**Use Cases:**
- Regulatory requirements (data sovereignty)
- Customer-controlled key management
- Bring Your Own Key (BYOK)
- Hybrid cloud scenarios

---

## Secret Management at Scale

### Secret Organization Strategy

**By Environment:**
```
production-secrets/
├── database-password-prod
├── api-key-prod
└── ssl-certificate-prod

staging-secrets/
├── database-password-staging
└── api-key-staging

development-secrets/
├── database-password-dev
└── api-key-dev
```

**By Service:**
```
auth-service-secrets/
├── jwt-signing-key
├── oauth-client-secret
└── session-encryption-key

payment-service-secrets/
├── stripe-api-key
├── paypal-client-secret
└── payment-encryption-key
```

**Using Labels:**
```bash
gcloud secrets create database-password \
    --replication-policy=automatic \
    --labels=environment=production,service=backend,tier=critical
```

### Secret Rotation Automation

**Automated Rotation with Cloud Functions:**
```python
import functions_framework
from google.cloud import secretmanager, sqladmin
import random
import string

@functions_framework.cloud_event
def rotate_database_password(cloud_event):
    """Rotate database password on schedule."""
    
    # Generate new password
    new_password = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(32)
    )
    
    # Update database password
    sql_client = sqladmin.SQLAdmin()
    user_update_request = {
        'name': 'app-user',
        'password': new_password
    }
    sql_client.users().update(
        project='my-project',
        instance='my-instance',
        body=user_update_request
    ).execute()
    
    # Store new password in Secret Manager
    sm_client = secretmanager.SecretManagerServiceClient()
    parent = sm_client.secret_path('my-project', 'database-password')
    sm_client.add_secret_version(
        request={
            'parent': parent,
            'payload': {'data': new_password.encode('utf-8')}
        }
    )
    
    print(f'Rotated password, new version created')

# Deploy with Cloud Scheduler
# gcloud scheduler jobs create pubsub rotate-db-password \
#     --schedule="0 0 1 * *" \  # Monthly
#     --topic=rotate-passwords \
#     --message-body='{"secret": "database-password"}'
```

### Secret Version Management

**Blue-Green Secret Deployment:**
```python
def deploy_new_secret_version(secret_id: str, new_value: str):
    """Deploy new secret version with gradual rollout."""
    client = secretmanager.SecretManagerServiceClient()
    parent = client.secret_path('my-project', secret_id)
    
    # Add new version
    response = client.add_secret_version(
        request={
            'parent': parent,
            'payload': {'data': new_value.encode('utf-8')}
        }
    )
    new_version = response.name.split('/')[-1]
    
    print(f'Created version {new_version}')
    
    # Test new version (application code uses new version)
    # If tests pass after monitoring period, disable old version
    # If tests fail, destroy new version and rollback
    
    return new_version

def rollback_secret_version(secret_id: str, target_version: str):
    """Rollback to previous secret version."""
    client = secretmanager.SecretManagerServiceClient()
    
    # Get current version
    name = client.secret_version_path('my-project', secret_id, 'latest')
    current_version = client.get_secret_version(request={'name': name})
    
    # Disable current version
    client.disable_secret_version(request={'name': current_version.name})
    
    # Enable target version
    target_name = client.secret_version_path('my-project', secret_id, target_version)
    client.enable_secret_version(request={'name': target_name})
    
    print(f'Rolled back to version {target_version}')
```

### Secret Caching Strategy

**Application-Level Caching:**
```python
import time
from google.cloud import secretmanager
from typing import Dict, Tuple

class SecretCache:
    """Cache secrets with TTL to reduce Secret Manager calls."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, Tuple[str, float]] = {}
        self.ttl = ttl_seconds
        self.client = secretmanager.SecretManagerServiceClient()
    
    def get_secret(self, secret_id: str, project_id: str) -> str:
        """Get secret with caching."""
        cache_key = f"{project_id}/{secret_id}"
        
        # Check cache
        if cache_key in self.cache:
            value, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return value  # Cache hit
        
        # Cache miss - fetch from Secret Manager
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = self.client.access_secret_version(request={'name': name})
        value = response.payload.data.decode('utf-8')
        
        # Update cache
        self.cache[cache_key] = (value, time.time())
        
        return value
    
    def invalidate(self, secret_id: str, project_id: str):
        """Invalidate cache entry (call after rotation)."""
        cache_key = f"{project_id}/{secret_id}"
        self.cache.pop(cache_key, None)

# Usage
cache = SecretCache(ttl_seconds=300)  # 5 minute cache
db_password = cache.get_secret('database-password', 'my-project')
```

---

## Compliance & Governance

### Compliance Frameworks

| Framework | KMS Requirement | Secret Manager Requirement |
|-----------|----------------|---------------------------|
| **PCI-DSS** | HSM keys for cardholder data | Encrypted secrets, access logs |
| **HIPAA** | CMEK for PHI, key rotation | Encrypted PHI, audit trail |
| **GDPR** | Encryption at rest/transit | Secure credential storage |
| **SOC 2** | Key management controls | Secret access controls |
| **FedRAMP** | FIPS 140-2 Level 3 (HSM) | Government-grade security |

### Key Management Policy

**Organization Policy Example:**
```yaml
name: organizations/123456/policies/kms-policy
spec:
  rules:
  - enforce: true
    conditions:
    - key: resource.type
      values: ["cloudkms.googleapis.com/CryptoKey"]
    values:
      allowedValues:
      - projects/security-project/*  # Only central project
  
  - enforce: true
    conditions:
    - key: resource.protectionLevel
      values: ["HSM"]  # Force HSM for production
```

**Enforce with Organization Policy:**
```bash
gcloud org-policies set-policy kms-policy.yaml \
    --organization=123456
```

### Audit Logging & Monitoring

**Enable Data Access Logs:**
```bash
# Enable KMS audit logging
gcloud projects get-iam-policy PROJECT_ID \
    --flatten="auditConfigs[]" \
    --format="json" > iam-policy.json

# Add KMS audit config
{
  "auditConfigs": [
    {
      "service": "cloudkms.googleapis.com",
      "auditLogConfigs": [
        {"logType": "ADMIN_READ"},
        {"logType": "DATA_READ"},
        {"logType": "DATA_WRITE"}
      ]
    }
  ]
}

# Apply policy
gcloud projects set-iam-policy PROJECT_ID iam-policy.json
```

**Monitor Key Usage:**
```bash
# Query Cloud Logging for key operations
gcloud logging read '
  resource.type="cloudkms_cryptokey"
  AND protoPayload.methodName="Decrypt"
  AND timestamp>="2024-11-01T00:00:00Z"
' --limit=100 --format=json
```

**Alert on Suspicious Activity:**
```bash
# Create alert policy for unauthorized access attempts
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="KMS Unauthorized Access" \
    --condition-display-name="Failed KMS Operations" \
    --condition-threshold-value=5 \
    --condition-threshold-duration=300s \
    --condition-filter='
      resource.type="cloudkms_cryptokey"
      AND protoPayload.status.code!=0
    '
```

### Separation of Duties

**Role Segregation:**
```
Security Team:
└── roles/cloudkms.admin (create/manage keys)

Operations Team:
└── roles/cloudkms.cryptoKeyEncrypterDecrypter (use keys)

Audit Team:
└── roles/cloudkms.viewer (view metadata only)

Applications:
└── roles/cloudkms.cryptoKeyEncrypterDecrypter (specific keys only)
```

**Implementation:**
```bash
# Security team manages keys
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=group:security-team@company.com \
    --role=roles/cloudkms.admin

# App only uses specific key
gcloud kms keys add-iam-policy-binding app-key \
    --location=us-central1 \
    --keyring=prod-keyring \
    --member=serviceAccount:app@project.iam.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyEncrypterDecrypter
```

---

## High Availability & Disaster Recovery

### Multi-Region Key Strategy

**Regional Keys for Regional Data:**
```
us-central1-keyring/
└── us-data-encryption-key (encrypts US data)

europe-west1-keyring/
└── eu-data-encryption-key (encrypts EU data)

asia-northeast1-keyring/
└── asia-data-encryption-key (encrypts Asia data)
```

**Global Key for Global Data:**
```
global-keyring/ (multi-region)
└── global-encryption-key
```

**Note:** KMS keys cannot be moved between locations after creation!

### Secret Manager HA Architecture

**Automatic Replication (Maximum Availability):**
```bash
gcloud secrets create critical-secret \
    --replication-policy=automatic \
    --data-file=secret.txt
```
- Replicated to all regions
- Survives regional outages
- 99.99% availability SLA

**User-Managed Replication (Data Residency):**
```bash
gcloud secrets create eu-only-secret \
    --replication-policy=user-managed \
    --locations=europe-west1,europe-west4 \
    --data-file=secret.txt
```
- Data stays in specified regions
- Survives single region failure
- Lower cost

### Disaster Recovery Procedures

**Key Backup Strategy:**
```bash
# Export public key (asymmetric keys only)
gcloud kms keys versions get-public-key 1 \
    --location=us-central1 \
    --keyring=my-keyring \
    --key=my-signing-key \
    --output-file=public-key.pem

# Backup key metadata
gcloud kms keys describe my-key \
    --location=us-central1 \
    --keyring=my-keyring \
    --format=json > key-metadata.json
```

**Secret Backup Strategy:**
```bash
# Backup all secrets in project
for secret in $(gcloud secrets list --format="value(name)"); do
    gcloud secrets versions access latest --secret=$secret > backups/${secret}.txt
done

# Store backups in encrypted Cloud Storage
gsutil -m cp -r backups/ gs://backup-bucket/secrets-$(date +%Y%m%d)/
```

**DR Runbook:**
1. **Key Loss (Scheduled Destruction):**
   - Cancel destruction within 24 hours
   - `gcloud kms keys versions restore`
   
2. **Regional Outage:**
   - KMS: Keys in other regions unaffected
   - Secrets: Automatic failover to other replicas
   
3. **Project Deletion:**
   - 30-day retention period
   - Restore project within window
   - Keys and secrets restored automatically

---

## Security Architecture

### Defense-in-Depth for Key Management

**Layer 1: Network Security**
```
VPC Service Controls Perimeter
├── Restricted Services: cloudkms.googleapis.com, secretmanager.googleapis.com
├── Ingress Rules: Only from approved networks
└── Egress Rules: Prevent data exfiltration
```

**Layer 2: Identity & Access**
```
IAM Hierarchy
├── Organization: Admin only
├── Folder: Security team
├── Project: Operations team
└── Key/Secret: Application service accounts (least privilege)
```

**Layer 3: Audit & Monitoring**
```
Cloud Logging + Cloud Monitoring
├── All key operations logged
├── Alerts on anomalies
└── SIEM integration
```

### VPC Service Controls for KMS

**Create Service Perimeter:**
```bash
# Create access policy
gcloud access-context-manager policies create \
    --organization=ORG_ID \
    --title="KMS Security Policy"

# Create perimeter
gcloud access-context-manager perimeters create kms-perimeter \
    --policy=POLICY_ID \
    --title="KMS Restricted Access" \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=cloudkms.googleapis.com,secretmanager.googleapis.com \
    --enable-vpc-accessible-services \
    --vpc-allowed-services=cloudkms.googleapis.com,secretmanager.googleapis.com
```

**Benefits:**
- Prevent key/secret access from unauthorized networks
- Data exfiltration protection
- Compliance (HIPAA, PCI-DSS)

### Workload Identity for GKE

**Secure Secret Access from GKE:**
```yaml
# Kubernetes Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: default
  annotations:
    iam.gke.io/gcp-service-account: app@project.iam.gserviceaccount.com

---
# Pod using Workload Identity
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  serviceAccountName: app-sa
  containers:
  - name: app
    image: gcr.io/project/app:latest
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: database-password
          key: password
```

**Setup Workload Identity:**
```bash
# Bind Kubernetes SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding \
    app@project.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="serviceAccount:project.svc.id.goog[default/app-sa]"

# Grant Secret Manager access
gcloud secrets add-iam-policy-binding database-password \
    --member=serviceAccount:app@project.iam.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor
```

---

## Cost Optimization

### KMS Cost Model

**Operations:**
- Key operations (encrypt/decrypt): $0.03 per 10,000 operations
- Key versions: $0.06 per key version per month
- HSM operations: $1.00 per 10,000 operations
- HSM key versions: $2.50 per key version per month
- External operations: $3.00 per 10,000 operations

**Optimization Strategies:**

**1. Minimize Key Versions:**
```bash
# Destroy old key versions after grace period
gcloud kms keys versions list --key=my-key \
    --location=us-central1 \
    --keyring=my-keyring \
    --filter="state=ENABLED AND createTime<'2024-01-01'" \
    --format="value(name)" | while read version; do
    gcloud kms keys versions destroy $version
done
```

**2. Use Envelope Encryption:**
```
Instead of: Encrypt each file with KMS (1M files = 1M KMS calls)
Use: Encrypt each file with DEK, encrypt 1 DEK with KMS (1M files = 1 KMS call)
Savings: 99.9999% reduction in KMS calls
```

**3. Cache KMS Results:**
```python
# Cache encrypted DEK (don't re-encrypt same DEK)
from functools import lru_cache

@lru_cache(maxsize=100)
def get_encrypted_dek(dek_id: str) -> bytes:
    # Encrypt DEK once, cache result
    return kms_client.encrypt(...)
```

### Secret Manager Cost Model

**Storage:**
- Secret versions: $0.06 per version per month
- Active versions: Full cost
- Disabled versions: Still charged

**Access:**
- Access operations: $0.03 per 10,000 operations
- Replication: Included in storage cost

**Optimization Strategies:**

**1. Delete Old Secret Versions:**
```bash
# Keep only last 5 versions
for secret in $(gcloud secrets list --format="value(name)"); do
    versions=$(gcloud secrets versions list $secret \
        --filter="state=ENABLED OR state=DISABLED" \
        --sort-by=~createTime \
        --format="value(name)" | tail -n +6)
    
    for version in $versions; do
        gcloud secrets versions destroy $version --secret=$secret
    done
done
```

**2. Use User-Managed Replication:**
```bash
# Automatic: Replicated to all regions (~20 regions)
# User-managed: Replicate to 2 regions
# Savings: 90% storage cost reduction
gcloud secrets create cost-optimized \
    --replication-policy=user-managed \
    --locations=us-central1,us-east1  # Only 2 regions
```

**3. Cache Secrets at Application Layer:**
```python
# Reduce Secret Manager access operations
# Cache secrets for 5 minutes (TTL)
# 1 read per 5 min = 288 reads/day vs 1 read per request = 86,400 reads/day
# Savings: 99.7% reduction in access costs
```

---

## Integration Patterns

### CI/CD Pipeline Integration

**GitHub Actions with Secret Manager:**
```yaml
name: Deploy
on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - id: auth
      uses: google-github-actions/auth@v1
      with:
        credentials_json: '${{ secrets.GCP_SA_KEY }}'
    
    - id: secrets
      uses: google-github-actions/get-secretmanager-secrets@v1
      with:
        secrets: |-
          DATABASE_URL:project-id/database-url
          API_KEY:project-id/api-key
    
    - name: Deploy
      env:
        DATABASE_URL: '${{ steps.secrets.outputs.DATABASE_URL }}'
        API_KEY: '${{ steps.secrets.outputs.API_KEY }}'
      run: |
        # Deploy with secrets
        ./deploy.sh
```

### Terraform with KMS & Secret Manager

```hcl
# KMS Key
resource "google_kms_key_ring" "keyring" {
  name     = "prod-keyring"
  location = "us-central1"
}

resource "google_kms_crypto_key" "key" {
  name     = "database-key"
  key_ring = google_kms_key_ring.keyring.id
  
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# Secret Manager Secret
resource "google_secret_manager_secret" "db_password" {
  secret_id = "database-password"
  
  replication {
    user_managed {
      replicas {
        location = "us-central1"
      }
      replicas {
        location = "us-east1"
      }
    }
  }
}

resource "google_secret_manager_secret_version" "db_password_v1" {
  secret = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Grant access
resource "google_secret_manager_secret_iam_member" "app_access" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:app@project.iam.gserviceaccount.com"
}
```

### Multi-Cloud Key Management

**Unified Key Management Across Clouds:**
```python
class UnifiedKeyManager:
    """Abstract key operations across GCP KMS and AWS KMS."""
    
    def __init__(self, provider: str):
        self.provider = provider
        if provider == 'gcp':
            from google.cloud import kms
            self.client = kms.KeyManagementServiceClient()
        elif provider == 'aws':
            import boto3
            self.client = boto3.client('kms')
    
    def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        if self.provider == 'gcp':
            response = self.client.encrypt(
                request={'name': key_id, 'plaintext': plaintext}
            )
            return response.ciphertext
        elif self.provider == 'aws':
            response = self.client.encrypt(
                KeyId=key_id, Plaintext=plaintext
            )
            return response['CiphertextBlob']
    
    def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        if self.provider == 'gcp':
            response = self.client.decrypt(
                request={'name': key_id, 'ciphertext': ciphertext}
            )
            return response.plaintext
        elif self.provider == 'aws':
            response = self.client.decrypt(
                KeyId=key_id, CiphertextBlob=ciphertext
            )
            return response['Plaintext']
```

---

## PCA Exam Tips

### Key Architectural Patterns

1. **Centralized Key Management:**
   - Use dedicated security project for KMS keys
   - Grant cross-project access via IAM
   - Simplifies governance and auditing

2. **Envelope Encryption:**
   - Use for bulk data encryption (cost-effective)
   - DEK encrypts data locally (fast)
   - KEK (KMS) encrypts DEK (secure)

3. **Key Rotation:**
   - Automatic: 90 days for symmetric keys
   - Manual: For external/asymmetric keys
   - Old versions remain for decryption

4. **Protection Levels:**
   - Software: General use (cost-effective)
   - HSM: Compliance, sensitive data (FIPS 140-2 L3)
   - External: Regulatory requirements, data sovereignty

5. **Secret Replication:**
   - Automatic: Global apps, maximum availability
   - User-managed: Data residency, cost optimization

6. **Separation of Duties:**
   - Security team: Create/manage keys
   - Ops team: Use keys
   - Audit team: View-only access

7. **Cost Optimization:**
   - Use envelope encryption (reduce KMS calls)
   - Delete old key/secret versions
   - Use user-managed replication (fewer replicas)
   - Cache secrets at application layer

### Common Exam Scenarios

**Scenario 1:** Need FIPS 140-2 Level 3 compliance for encryption
- **Answer:** Use HSM-backed KMS keys (`--protection-level=hsm`)

**Scenario 2:** Encrypt Cloud Storage bucket with customer-managed keys
- **Answer:** Create KMS key, grant Cloud Storage service account encrypterDecrypter role, enable CMEK on bucket

**Scenario 3:** Automatically rotate database passwords every 30 days
- **Answer:** Cloud Function triggered by Cloud Scheduler, updates password in database and Secret Manager

**Scenario 4:** Secrets must stay in EU for GDPR compliance
- **Answer:** User-managed replication with EU regions only

**Scenario 5:** Minimize KMS costs for encrypting 1M files
- **Answer:** Use envelope encryption (encrypt files with DEK, encrypt 1 DEK with KMS)

**Scenario 6:** Central security team manages keys, apps use them across projects
- **Answer:** Centralized key management (keys in security project, grant IAM access to app service accounts)

**Scenario 7:** Need to bring your own encryption keys from on-premises HSM
- **Answer:** Use External Key Manager (EKM) to integrate external HSM

**Scenario 8:** Secure secret access from GKE pods
- **Answer:** Use Workload Identity to bind Kubernetes SA to GCP SA with Secret Manager access

### Decision Trees

**Protection Level Selection:**
```
Regulatory compliance (HIPAA, PCI-DSS)? → Yes → HSM
Customer controls keys? → Yes → External (EKM)
Cost-sensitive? → Yes → Software
Default → Software
```

**Secret Replication:**
```
Global application? → Yes → Automatic replication
Data residency required? → Yes → User-managed (specific regions)
Cost-sensitive? → Yes → User-managed (minimum regions)
Default → Automatic
```

**Key Type Selection:**
```
Bulk data encryption? → Yes → Symmetric (AES-256)
Digital signatures? → Yes → Asymmetric signing (RSA/ECDSA)
Public-key encryption? → Yes → Asymmetric encryption (RSA)
Message authentication? → Yes → MAC (HMAC)
```

---

## Additional Resources

- [Cloud KMS Documentation](https://cloud.google.com/kms/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Key Management Best Practices](https://cloud.google.com/kms/docs/key-management-best-practices)
- [Envelope Encryption Guide](https://cloud.google.com/kms/docs/envelope-encryption)
- [CMEK Integration Guide](https://cloud.google.com/kms/docs/cmek)
- [Compliance and Certifications](https://cloud.google.com/security/compliance)

---

**Last Updated:** November 2025  
**Exam:** Google Professional Cloud Architect (PCA)
