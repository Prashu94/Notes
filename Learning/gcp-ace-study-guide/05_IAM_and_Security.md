# 05. IAM and Security (Masterclass Edition)

IAM (Identity and Access Management) is the security backbone of Google Cloud. It defines **Who** (Identity) can do **What** (Role) on **Which** Resource.

---

## 5.1 Advanced IAM Concepts

### 5.1.1 The IAM Member Types (The "Who")

| Member Type | Format | Use Case |
|-------------|--------|----------|
| **Google Account** | `user:alice@example.com` | Individual users |
| **Service Account** | `serviceAccount:sa@project.iam.gserviceaccount.com` | Applications, VMs |
| **Google Group** | `group:team@example.com` | Teams (recommended) |
| **Domain** | `domain:example.com` | All users in domain |
| **allUsers** | `allUsers` | Anonymous public access |
| **allAuthenticatedUsers** | `allAuthenticatedUsers` | Any Google account |

**Best Practice**: Always assign roles to **Groups**, not individual users.

```bash
# Add IAM binding to a group
gcloud projects add-iam-policy-binding my-project \
    --member="group:developers@example.com" \
    --role="roles/storage.objectViewer"

# List IAM policy
gcloud projects get-iam-policy my-project --format=json
```

### 5.1.2 IAM Role Types (The "What")

| Role Type | Granularity | Management | Use Case |
|-----------|-------------|------------|----------|
| **Basic** | Very broad | Google | Avoid in production |
| **Predefined** | Fine-grained | Google | Most use cases |
| **Custom** | Precise | You | Specific requirements |

#### Basic Roles (Legacy - Avoid)

| Role | Permissions |
|------|-------------|
| `roles/viewer` | Read-only across all services |
| `roles/editor` | Read + Write (no IAM changes) |
| `roles/owner` | Full control including IAM |

#### Common Predefined Roles

| Category | Role | Permissions |
|----------|------|-------------|
| **Storage** | `roles/storage.objectViewer` | Read objects |
| **Storage** | `roles/storage.objectCreator` | Create objects (no read) |
| **Storage** | `roles/storage.objectAdmin` | Full object control |
| **Compute** | `roles/compute.instanceAdmin.v1` | Manage VMs |
| **Compute** | `roles/compute.networkAdmin` | Manage networks |
| **BigQuery** | `roles/bigquery.dataViewer` | Query data |
| **BigQuery** | `roles/bigquery.jobUser` | Run jobs |

```bash
# List all predefined roles
gcloud iam roles list --filter="name:roles/storage*"

# Describe a role to see permissions
gcloud iam roles describe roles/storage.objectAdmin
```

#### Custom Roles

```bash
# Create custom role from YAML
cat > custom-role.yaml << EOF
title: "Custom Storage Reader"
description: "Read storage objects and list buckets"
stage: "GA"
includedPermissions:
- storage.buckets.list
- storage.objects.get
- storage.objects.list
EOF

gcloud iam roles create customStorageReader \
    --project=my-project \
    --file=custom-role.yaml

# Update custom role
gcloud iam roles update customStorageReader \
    --project=my-project \
    --add-permissions=storage.buckets.get
```

**Custom Role Constraints**:
*   Can only be created at **Organization** or **Project** level (not Folder)
*   Some permissions cannot be included in custom roles
*   Must manage updates when Google adds new permissions

### 5.1.3 IAM Policy Hierarchy & Inheritance

```
Organization Policy                    ─┐
    │                                   │  Permissions
    ├── Folder Policy                   │  ACCUMULATE
    │       │                           │  (Union)
    │       └── Project Policy          │
    │               │                  ─┘
    │               └── Resource Policy
```

**Key Points**:
*   Policies are **additive** - child resources inherit parent permissions
*   Cannot remove permissions granted at higher level
*   Use **IAM Conditions** to restrict access

### 5.1.4 IAM Conditions

Add time-based or resource-based conditions to bindings.

```bash
# Grant access only during business hours
gcloud projects add-iam-policy-binding my-project \
    --member="user:contractor@example.com" \
    --role="roles/compute.instanceAdmin.v1" \
    --condition='expression=request.time.getHours("America/New_York") >= 9 && request.time.getHours("America/New_York") <= 17,title=business-hours'

# Grant access only to specific resource names
gcloud projects add-iam-policy-binding my-project \
    --member="group:dev-team@example.com" \
    --role="roles/compute.instanceAdmin.v1" \
    --condition='expression=resource.name.startsWith("projects/my-project/zones/us-central1-a/instances/dev-"),title=dev-instances-only'
```

### 5.1.5 IAM Recommender

ML-based tool that analyzes actual usage patterns to recommend least-privilege roles.

```bash
# List IAM recommendations
gcloud recommender recommendations list \
    --project=my-project \
    --location=global \
    --recommender=google.iam.policy.Recommender

# Apply a recommendation
gcloud recommender recommendations mark-claimed RECOMMENDATION_ID \
    --project=my-project \
    --location=global \
    --recommender=google.iam.policy.Recommender
```

---

## 5.2 Service Accounts (The "Robot" Identity)

### 5.2.1 Service Account Types

| Type | Created By | Default Permissions | Recommendation |
|------|------------|---------------------|----------------|
| **User-Managed** | You | None | Use for your applications |
| **Default (Compute)** | Google | `roles/editor` (broad) | Disable or restrict |
| **Default (App Engine)** | Google | `roles/editor` (broad) | Disable or restrict |
| **Google-Managed** | Google | Specific to service | Do not modify |

```bash
# Create a service account
gcloud iam service-accounts create my-app-sa \
    --display-name="My Application Service Account" \
    --description="SA for backend services"

# Grant roles to service account
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:my-app-sa@my-project.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Disable default Compute Engine SA
gcloud iam service-accounts disable \
    PROJECT_NUMBER-compute@developer.gserviceaccount.com
```

### 5.2.2 Service Account Authentication Methods

| Method | Security | Use Case |
|--------|----------|----------|
| **Attached SA** | ✅ High | VMs, Cloud Run, GKE |
| **Impersonation** | ✅ High | CI/CD, developers |
| **Workload Identity Federation** | ✅ Highest | Multi-cloud, external |
| **Service Account Keys** | ⚠️ Low | Legacy (avoid) |

#### Attached Service Accounts

```bash
# Create VM with specific service account
gcloud compute instances create my-vm \
    --zone=us-central1-a \
    --service-account=my-app-sa@my-project.iam.gserviceaccount.com \
    --scopes=cloud-platform

# Deploy Cloud Run with service account
gcloud run deploy my-service \
    --image=gcr.io/my-project/my-image \
    --service-account=my-app-sa@my-project.iam.gserviceaccount.com
```

#### Service Account Impersonation

```bash
# Grant impersonation permission
gcloud iam service-accounts add-iam-policy-binding \
    my-app-sa@my-project.iam.gserviceaccount.com \
    --member="user:developer@example.com" \
    --role="roles/iam.serviceAccountTokenCreator"

# Impersonate SA using gcloud
gcloud config set auth/impersonate_service_account \
    my-app-sa@my-project.iam.gserviceaccount.com

# Run command as the service account
gcloud storage ls gs://my-bucket --impersonate-service-account=my-app-sa@my-project.iam.gserviceaccount.com
```

#### Workload Identity Federation

Allow external identities (AWS, Azure, GitHub Actions, OIDC) to access GCP without keys.

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create github-pool \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Add GitHub OIDC provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
    --location="global" \
    --workload-identity-pool=github-pool \
    --display-name="GitHub Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"

# Allow GitHub repo to impersonate SA
gcloud iam service-accounts add-iam-policy-binding \
    my-deploy-sa@my-project.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/my-org/my-repo"
```

### 5.2.3 Service Account Key Best Practices

**If you must use keys** (legacy systems):

| Practice | Implementation |
|----------|----------------|
| **Rotate regularly** | Set up automated rotation |
| **Limit key count** | Max 2 keys per SA |
| **Monitor usage** | Enable Cloud Audit Logs |
| **Restrict permissions** | Minimum required roles |
| **Secure storage** | Secret Manager, KMS |

```bash
# Create key (avoid if possible)
gcloud iam service-accounts keys create key.json \
    --iam-account=my-app-sa@my-project.iam.gserviceaccount.com

# List keys (check for old keys)
gcloud iam service-accounts keys list \
    --iam-account=my-app-sa@my-project.iam.gserviceaccount.com

# Delete old key
gcloud iam service-accounts keys delete KEY_ID \
    --iam-account=my-app-sa@my-project.iam.gserviceaccount.com
```

---

## 5.3 Advanced Security Tools

### 5.3.1 Identity-Aware Proxy (IAP)

Zero-trust access to applications and VMs without VPN.

| Feature | Description |
|---------|-------------|
| **Context-Aware Access** | Device security, location, time |
| **TCP Forwarding** | SSH/RDP without public IP |
| **Application Access** | Web apps behind HTTPS LB |
| **IAM Integration** | `roles/iap.tunnelResourceAccessor` |

```bash
# Enable IAP for SSH/RDP
# First, create firewall rule for IAP IP range
gcloud compute firewall-rules create allow-iap-ssh \
    --network=my-vpc \
    --direction=INGRESS \
    --priority=1000 \
    --action=ALLOW \
    --rules=tcp:22,tcp:3389 \
    --source-ranges=35.235.240.0/20 \
    --target-tags=iap-enabled

# Grant IAP tunnel access
gcloud projects add-iam-policy-binding my-project \
    --member="user:developer@example.com" \
    --role="roles/iap.tunnelResourceAccessor"

# SSH through IAP tunnel
gcloud compute ssh my-vm --zone=us-central1-a --tunnel-through-iap

# Enable IAP for App Engine/Cloud Run
gcloud iap web enable \
    --resource-type=app-engine \
    --oauth2-client-id=CLIENT_ID \
    --oauth2-client-secret=CLIENT_SECRET
```

### 5.3.2 Cloud Armor (WAF + DDoS)

Web Application Firewall integrated with HTTP(S) Load Balancer.

| Feature | Description |
|---------|-------------|
| **IP Allowlist/Denylist** | Control access by IP/CIDR |
| **Geo-based Filtering** | Block/allow by country |
| **OWASP Rules** | Pre-configured WAF rules |
| **Custom Rules** | CEL expressions |
| **Adaptive Protection** | ML-based anomaly detection |
| **Bot Management** | reCAPTCHA Enterprise |

```bash
# Create security policy
gcloud compute security-policies create web-policy

# Block specific country
gcloud compute security-policies rules create 1000 \
    --security-policy=web-policy \
    --expression="origin.region_code == 'CN'" \
    --action=deny-403

# Block SQL injection
gcloud compute security-policies rules create 2000 \
    --security-policy=web-policy \
    --expression="evaluatePreconfiguredWaf('sqli-v33-stable')" \
    --action=deny-403

# Rate limiting
gcloud compute security-policies rules create 3000 \
    --security-policy=web-policy \
    --expression="true" \
    --action=rate-based-ban \
    --rate-limit-threshold-count=1000 \
    --rate-limit-threshold-interval-sec=60 \
    --ban-duration-sec=300

# Attach to backend service
gcloud compute backend-services update my-backend \
    --security-policy=web-policy --global
```

### 5.3.3 Encryption at Rest

| Type | Key Management | Rotation | Use Case |
|------|----------------|----------|----------|
| **Google-Managed** | Google | Automatic | Default, most workloads |
| **CMEK** | Cloud KMS (you manage) | You control | Compliance, audit |
| **CSEK** | You provide | You manage | Maximum control |

#### Cloud KMS (Key Management Service)

```bash
# Create key ring
gcloud kms keyrings create my-keyring \
    --location=us-central1

# Create encryption key
gcloud kms keys create my-key \
    --keyring=my-keyring \
    --location=us-central1 \
    --purpose=encryption \
    --rotation-period=90d \
    --next-rotation-time="2024-06-01T00:00:00Z"

# Create BigQuery dataset with CMEK
bq mk --dataset \
    --default_kms_key=projects/my-project/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key \
    my_dataset

# Create Cloud Storage bucket with CMEK
gcloud storage buckets create gs://my-cmek-bucket \
    --location=us-central1 \
    --default-encryption-key=projects/my-project/locations/us-central1/keyRings/my-keyring/cryptoKeys/my-key
```

#### CSEK (Customer-Supplied Keys)

```bash
# Encrypt a disk with your own key (base64-encoded 256-bit key)
gcloud compute disks create my-disk \
    --zone=us-central1-a \
    --csek-key-file=key-file.json

# key-file.json format:
# [{"uri": "https://www.googleapis.com/compute/v1/projects/PROJECT/zones/ZONE/disks/DISK",
#   "key": "BASE64_ENCODED_KEY",
#   "key-type": "raw"}]
```

### 5.3.4 Secret Manager

Centralized secret storage with versioning and access control.

```bash
# Create a secret
gcloud secrets create db-password --replication-policy="automatic"

# Add secret version
echo -n "my-super-secret-password" | \
    gcloud secrets versions add db-password --data-file=-

# Grant access to secret
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:my-app-sa@my-project.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Access secret in code (Python)
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
name = "projects/my-project/secrets/db-password/versions/latest"
response = client.access_secret_version(request={"name": name})
password = response.payload.data.decode("UTF-8")
```

### 5.3.5 VPC Service Controls

Create security perimeters around sensitive data to prevent exfiltration.

```bash
# Create access policy (org-level)
gcloud access-context-manager policies create \
    --organization=123456789 \
    --title="My Access Policy"

# Create access level (who can access)
gcloud access-context-manager levels create trusted-users \
    --title="Trusted Users" \
    --policy=POLICY_ID \
    --basic-level-spec="ipSubnetworks: ['203.0.113.0/24'],requiredAccessLevels: [],members: ['user:admin@example.com']"

# Create service perimeter
gcloud access-context-manager perimeters create secure-perimeter \
    --policy=POLICY_ID \
    --title="Secure Data Perimeter" \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=storage.googleapis.com,bigquery.googleapis.com \
    --access-levels=accessPolicies/POLICY_ID/accessLevels/trusted-users
```

---

## 5.4 Audit Logging

### 5.4.1 Audit Log Types

| Log Type | Content | Enabled By | Cost |
|----------|---------|------------|------|
| **Admin Activity** | Config changes (create, delete, update) | Always | Free |
| **Data Access** | Data reads/writes | Manual | Charged |
| **System Event** | Google-initiated actions | Always | Free |
| **Policy Denied** | IAM denials | Always | Free |

```bash
# View Admin Activity logs
gcloud logging read 'logName="projects/my-project/logs/cloudaudit.googleapis.com%2Factivity"' \
    --limit=10 \
    --format=json

# Enable Data Access logs for BigQuery
gcloud projects get-iam-policy my-project --format=json > policy.json
# Edit policy.json to add auditConfigs
# {
#   "auditConfigs": [
#     {
#       "service": "bigquery.googleapis.com",
#       "auditLogConfigs": [
#         {"logType": "DATA_READ"},
#         {"logType": "DATA_WRITE"}
#       ]
#     }
#   ]
# }
gcloud projects set-iam-policy my-project policy.json

# Enable Data Access logs via gcloud
gcloud projects set-iam-policy my-project <(
  gcloud projects get-iam-policy my-project --format=json | \
  jq '.auditConfigs = [{"service": "allServices", "auditLogConfigs": [{"logType": "ADMIN_READ"}, {"logType": "DATA_READ"}, {"logType": "DATA_WRITE"}]}]'
)
```

### 5.4.2 Log Export and Analysis

```bash
# Create log sink to BigQuery
gcloud logging sinks create audit-sink \
    bigquery.googleapis.com/projects/my-project/datasets/audit_logs \
    --log-filter='logName:"cloudaudit.googleapis.com"'

# Create log sink to Cloud Storage
gcloud logging sinks create storage-sink \
    storage.googleapis.com/my-audit-bucket \
    --log-filter='resource.type="gce_instance"'
```

---

## 5.5 Organization Policies

Centralized constraints applied across your organization.

### 5.5.1 Common Organization Policy Constraints

| Constraint | Effect |
|------------|--------|
| `compute.vmExternalIpAccess` | Control which VMs can have external IPs |
| `compute.restrictSharedVpcSubnetworks` | Limit which subnets can be shared |
| `iam.allowedPolicyMemberDomains` | Restrict IAM members to specific domains |
| `compute.trustedImageProjects` | Only allow images from specific projects |
| `storage.uniformBucketLevelAccess` | Enforce uniform bucket access |
| `compute.skipDefaultNetworkCreation` | Don't create default network |
| `sql.restrictPublicIp` | Prevent public IPs on Cloud SQL |

```bash
# Set organization policy to deny external IPs
gcloud resource-manager org-policies set-policy \
    --organization=123456789 \
    policy.yaml

# policy.yaml
# constraint: constraints/compute.vmExternalIpAccess
# listPolicy:
#   allValues: DENY

# Allow external IPs only for specific VMs
# constraint: constraints/compute.vmExternalIpAccess
# listPolicy:
#   allowedValues:
#   - projects/my-project/zones/us-central1-a/instances/bastion-vm

# Restrict IAM members to company domain only
gcloud resource-manager org-policies set-policy \
    --organization=123456789 << EOF
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - C0xxxxxxx  # Cloud Identity/Workspace customer ID
EOF
```

---

## 5.6 Security Best Practices Checklist

### Identity & Access
- [ ] Use **Groups** for role assignments (never individual users)
- [ ] Enforce **Least Privilege** using IAM Recommender
- [ ] Implement **IAM Conditions** for time/resource-based access
- [ ] Enable **Organization Policy** constraints
- [ ] Disable or restrict **Default Service Accounts**

### Service Accounts
- [ ] Use **Workload Identity Federation** for external access
- [ ] Use **Service Account Impersonation** instead of keys
- [ ] Rotate or delete **Service Account Keys** if they exist
- [ ] Bind SAs to resources (VMs, Cloud Run) instead of using keys

### Network Security
- [ ] Use **Private Google Access** for internal-only VMs
- [ ] Enable **VPC Flow Logs** for monitoring
- [ ] Implement **Hierarchical Firewall Policies**
- [ ] Use **IAP** for SSH/RDP access
- [ ] Deploy **Cloud Armor** for public-facing apps

### Data Protection
- [ ] Use **CMEK** for sensitive data requiring audit
- [ ] Enable **Data Access Logs** for sensitive resources
- [ ] Implement **VPC Service Controls** for data perimeters
- [ ] Store secrets in **Secret Manager**

### Organizational
- [ ] Use **Folders** for environment isolation (Prod/Dev/Test)
- [ ] Implement **Resource Hierarchy** best practices
- [ ] Enable **Security Command Center** for threat detection
- [ ] Set up **Alerting Policies** for security events
