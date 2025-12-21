# Chapter 05: Security & Compliance by Design

Security is not an afterthought; it must be built into the architecture. Google Cloud uses a "Defense in Depth" approach with multiple layers of security.

> **IAM Definition**: "IAM is a tool to manage fine-grained authorization for Google Cloud. In other words, it lets you control who can do what on which resources."
>
> — [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs/overview)

## 🔐 Identity & Access Management (IAM)

### Core Concepts

```
┌─────────────────────────────────────────────────────────────────┐
│                      IAM Components                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WHO (Principal)     +    WHAT (Role)    =    Allow Policy      │
│                                                                  │
│  • Google Account        • Predefined         Attached to a     │
│  • Service Account       • Custom             Resource          │
│  • Google Group          • Basic                                 │
│  • Cloud Identity                                                │
│  • Workforce Identity                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Principal Types

| Type | Description | Use Case |
| :--- | :--- | :--- |
| **Google Account** | Individual user identity | Employee access |
| **Service Account** | Identity for applications/workloads | App-to-app authentication |
| **Google Group** | Collection of accounts | Team access management |
| **Cloud Identity Domain** | All users in organization | Organization-wide policies |
| **Workforce Identity** | External IdP users | Federation with corporate IdP |
| **Workload Identity** | External workloads | Cross-cloud, on-prem apps |

### Role Types

| Type | Description | Example |
| :--- | :--- | :--- |
| **Basic** | Highly permissive (Owner, Editor, Viewer) | Avoid in production |
| **Predefined** | Google-managed, service-specific | `roles/storage.objectViewer` |
| **Custom** | User-defined permissions | Least privilege implementation |

**Example: Custom Role**
```bash
# Create a custom role with minimal permissions
gcloud iam roles create customStorageReader \
    --project=my-project \
    --title="Custom Storage Reader" \
    --description="Read storage objects and list buckets only" \
    --permissions=storage.objects.get,storage.objects.list,storage.buckets.list \
    --stage=GA

# Grant custom role to a user
gcloud projects add-iam-policy-binding my-project \
    --member="user:alice@example.com" \
    --role="projects/my-project/roles/customStorageReader"
```

### Best Practices for IAM

1. **Least Privilege**: Grant only minimum necessary permissions
2. **Use Groups**: Manage access via Google Groups, not individual users
3. **Service Accounts for Workloads**: Never use user accounts for applications
4. **Avoid Basic Roles**: Use predefined or custom roles instead
5. **Regular Audits**: Use IAM Recommender to identify excess permissions

### Service Accounts

> **Key Concept**: "Service accounts are identities for workloads. You use these principal types when managing your workloads' access to Google Cloud resources."

| Type | Description |
| :--- | :--- |
| **User-managed** | Created by you, fully controllable |
| **Default** | Auto-created for some services (avoid using) |
| **Google-managed** | Created and managed by Google services |

**Example: Service Account with Workload Identity**
```bash
# Create a service account
gcloud iam service-accounts create app-service-account \
    --display-name="Application Service Account"

# Grant required permissions
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:app-service-account@my-project.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# For GKE: Set up Workload Identity
gcloud container clusters update my-cluster \
    --workload-pool=my-project.svc.id.goog

# Bind Kubernetes SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding \
    app-service-account@my-project.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:my-project.svc.id.goog[default/my-k8s-sa]"
```

### IAM Conditions

Apply context-aware access control:

```bash
# Grant access only during business hours
gcloud projects add-iam-policy-binding my-project \
    --member="user:developer@example.com" \
    --role="roles/compute.admin" \
    --condition='expression=request.time.getHours("America/Los_Angeles") >= 9 && request.time.getHours("America/Los_Angeles") <= 17,title=business-hours-only'

# Grant access to specific resources by name
gcloud projects add-iam-policy-binding my-project \
    --member="user:developer@example.com" \
    --role="roles/compute.instanceAdmin" \
    --condition='expression=resource.name.startsWith("projects/my-project/zones/us-central1-a/instances/dev-"),title=dev-instances-only'
```

## 🛡️ Network Security & Isolation

### Defense in Depth Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Security Layers (Outside → Inside)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. EDGE: Cloud Armor (WAF, DDoS)                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 2. PERIMETER: VPC Service Controls                      │    │
│  │    (Prevents data exfiltration)                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 3. NETWORK: VPC Firewall Rules                          │    │
│  │    (Ingress/Egress control)                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 4. IDENTITY: IAM + Identity-Aware Proxy                 │    │
│  │    (Zero Trust access)                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 5. DATA: Encryption (at rest, in transit)               │    │
│  │    Cloud KMS, Cloud HSM, DLP                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### VPC Service Controls

Create security perimeters around Google Cloud resources to prevent data exfiltration.

```bash
# Create an access policy (organization level)
gcloud access-context-manager policies create \
    --organization=123456789 \
    --title="Corporate Access Policy"

# Create an access level for trusted networks
gcloud access-context-manager levels create trusted-corp-network \
    --title="Corporate Network" \
    --policy=POLICY_ID \
    --basic-level-spec=corp-network.yaml

# corp-network.yaml content:
# conditions:
#   - ipSubnetworks:
#       - 203.0.113.0/24
#       - 198.51.100.0/24

# Create a service perimeter
gcloud access-context-manager perimeters create secure-data-perimeter \
    --policy=POLICY_ID \
    --title="Secure Data Perimeter" \
    --resources=projects/12345,projects/67890 \
    --restricted-services=storage.googleapis.com,bigquery.googleapis.com \
    --access-levels=accessPolicies/POLICY_ID/accessLevels/trusted-corp-network
```

### Firewall Rules

| Rule Type | Scope | Use Case |
| :--- | :--- | :--- |
| **VPC Firewall Rules** | Single VPC | Basic ingress/egress control |
| **Hierarchical Firewall Policies** | Org/Folder | Enforce rules across projects |
| **Network Firewall Policies** | Global/Regional | Advanced rules with Tags |

**Example: Hierarchical Firewall Policy**
```bash
# Create a firewall policy at organization level
gcloud compute firewall-policies create corp-firewall-policy \
    --organization=123456789 \
    --short-name=corp-policy \
    --description="Corporate-wide firewall policy"

# Add rule to block all SSH except from bastion
gcloud compute firewall-policies rules create 1000 \
    --firewall-policy=corp-policy \
    --organization=123456789 \
    --direction=INGRESS \
    --action=deny \
    --layer4-configs=tcp:22 \
    --description="Block SSH by default"

gcloud compute firewall-policies rules create 900 \
    --firewall-policy=corp-policy \
    --organization=123456789 \
    --direction=INGRESS \
    --action=allow \
    --layer4-configs=tcp:22 \
    --src-ip-ranges=10.0.1.0/24 \
    --description="Allow SSH from bastion subnet"

# Associate policy with organization
gcloud compute firewall-policies associations create \
    --firewall-policy=corp-policy \
    --organization=123456789
```

## 📜 Compliance & Data Privacy

### Compliance Framework Mapping

| Framework | Key Requirements | Google Cloud Controls |
| :--- | :--- | :--- |
| **HIPAA** | PHI protection, audit trails | VPC SC, Cloud Audit Logs, BAA |
| **PCI-DSS** | Cardholder data security | VPC SC, CMEK, Cloud Armor |
| **GDPR** | Data residency, right to deletion | Regional storage, Data deletion |
| **SOC 2** | Security, availability, processing | Security Command Center |
| **FedRAMP** | US government requirements | Assured Workloads |

### Cloud DLP (Data Loss Prevention)

Automatically discover, classify, and protect sensitive data.

**Example: DLP Inspection and De-identification**
```python
from google.cloud import dlp_v2

def inspect_content(project_id, content):
    """Inspect content for sensitive data."""
    dlp = dlp_v2.DlpServiceClient()
    
    # Configure inspection
    inspect_config = {
        "info_types": [
            {"name": "CREDIT_CARD_NUMBER"},
            {"name": "EMAIL_ADDRESS"},
            {"name": "PHONE_NUMBER"},
            {"name": "US_SOCIAL_SECURITY_NUMBER"},
        ],
        "min_likelihood": dlp_v2.Likelihood.LIKELY,
        "include_quote": True,
    }
    
    # Inspect content
    item = {"value": content}
    response = dlp.inspect_content(
        request={
            "parent": f"projects/{project_id}",
            "inspect_config": inspect_config,
            "item": item,
        }
    )
    
    for finding in response.result.findings:
        print(f"Found: {finding.info_type.name}")
        print(f"  Quote: {finding.quote}")
        print(f"  Likelihood: {finding.likelihood.name}")

def deidentify_content(project_id, content):
    """De-identify sensitive content."""
    dlp = dlp_v2.DlpServiceClient()
    
    # Configure de-identification
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "info_types": [{"name": "EMAIL_ADDRESS"}],
                    "primitive_transformation": {
                        "replace_config": {
                            "new_value": {"string_value": "[EMAIL_REDACTED]"}
                        }
                    }
                },
                {
                    "info_types": [{"name": "CREDIT_CARD_NUMBER"}],
                    "primitive_transformation": {
                        "crypto_hash_config": {
                            "crypto_key": {
                                "transient": {"name": "my-key"}
                            }
                        }
                    }
                }
            ]
        }
    }
    
    response = dlp.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": {"value": content},
        }
    )
    
    return response.item.value
```

### Assured Workloads

Deploy compliant workloads with pre-configured guardrails.

```bash
# Create an Assured Workloads environment
gcloud assured workloads create \
    --organization=123456789 \
    --location=us-central1 \
    --display-name="HIPAA Workload" \
    --compliance-regime=HIPAA \
    --billing-account=012345-ABCDEF-012345 \
    --provisioned-resources-parent=folders/987654321
```

## 🔑 Key Management

### Encryption Options Comparison

| Option | Key Storage | Key Management | Use Case |
| :--- | :--- | :--- | :--- |
| **Google-managed** | Google | Google | Default, most workloads |
| **CMEK** | Cloud KMS | Customer | Control over key lifecycle |
| **CSEK** | Customer | Customer | Highest control, you provide key |
| **Cloud HSM** | FIPS 140-2 L3 HSM | Customer | Regulatory requirements |
| **EKM** | External KMS | Customer | Hold your own key (HYOK) |

**Example: Cloud KMS with Automatic Rotation**
```bash
# Create a key ring
gcloud kms keyrings create my-keyring \
    --location=us-central1

# Create a key with automatic rotation
gcloud kms keys create my-key \
    --keyring=my-keyring \
    --location=us-central1 \
    --purpose=encryption \
    --rotation-period=90d \
    --next-rotation-time=$(date -u -d "+90 days" +%Y-%m-%dT%H:%M:%SZ)

# Create a key with HSM protection
gcloud kms keys create my-hsm-key \
    --keyring=my-keyring \
    --location=us-central1 \
    --purpose=encryption \
    --protection-level=hsm

# Grant service account access to use the key
gcloud kms keys add-iam-policy-binding my-key \
    --keyring=my-keyring \
    --location=us-central1 \
    --member="serviceAccount:my-sa@my-project.iam.gserviceaccount.com" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

## 🏛️ Governance

### Organization Policy Service

Enforce constraints across your Google Cloud resources.

**Common Organization Policies**:
```bash
# Restrict VM external IP addresses
gcloud resource-manager org-policies set-policy \
    --organization=123456789 \
    external-ip-policy.yaml

# external-ip-policy.yaml
# constraint: constraints/compute.vmExternalIpAccess
# listPolicy:
#   allValues: DENY

# Restrict resource locations
gcloud resource-manager org-policies set-policy \
    --organization=123456789 \
    location-policy.yaml

# location-policy.yaml
# constraint: constraints/gcp.resourceLocations
# listPolicy:
#   allowedValues:
#     - in:us-locations
#     - in:eu-locations

# Disable service account key creation
gcloud resource-manager org-policies enable-enforce \
    constraints/iam.disableServiceAccountKeyCreation \
    --organization=123456789

# Require uniform bucket-level access
gcloud resource-manager org-policies enable-enforce \
    constraints/storage.uniformBucketLevelAccess \
    --organization=123456789
```

### Security Command Center

Centralized security and risk management.

**Features**:
- **Security Health Analytics**: Automatic vulnerability detection
- **Event Threat Detection**: Real-time threat detection
- **Container Threat Detection**: GKE runtime security
- **Web Security Scanner**: OWASP vulnerability scanning

```bash
# Enable Security Command Center
gcloud services enable securitycenter.googleapis.com

# List findings
gcloud scc findings list organizations/123456789 \
    --source=organizations/123456789/sources/- \
    --filter='state="ACTIVE" AND severity="HIGH"'

# Update finding state
gcloud scc findings update organizations/123456789/sources/12345/findings/FINDING_ID \
    --state=INACTIVE
```

### Cloud Audit Logs

| Log Type | Enabled By | Contains |
| :--- | :--- | :--- |
| **Admin Activity** | Default (can't disable) | API calls that modify resources |
| **Data Access** | Must enable | API calls that read data |
| **System Events** | Default | Google system actions |
| **Policy Denied** | Default | Security policy violations |

**Example: Enable Data Access Logs**
```bash
# Enable data access logs for specific services
gcloud projects get-iam-policy my-project --format=json > policy.json

# Add to policy.json:
# "auditConfigs": [
#   {
#     "service": "bigquery.googleapis.com",
#     "auditLogConfigs": [
#       {"logType": "ADMIN_READ"},
#       {"logType": "DATA_READ"},
#       {"logType": "DATA_WRITE"}
#     ]
#   }
# ]

gcloud projects set-iam-policy my-project policy.json
```

---

📚 **Documentation Links**:
- [IAM Documentation](https://cloud.google.com/iam/docs)
- [VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs)
- [Cloud DLP Documentation](https://cloud.google.com/dlp/docs)
- [Cloud KMS Documentation](https://cloud.google.com/kms/docs)
- [Security Command Center](https://cloud.google.com/security-command-center/docs)
- [Organization Policy Service](https://cloud.google.com/resource-manager/docs/organization-policy/overview)
- [Cloud Audit Logs](https://cloud.google.com/logging/docs/audit)

---
[Next Chapter: Operations & SRE](06_Operations_Reliability_and_SRE.md)
