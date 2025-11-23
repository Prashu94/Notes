# Google Cloud Security & IAM Guide (PCA - Professional Cloud Architect)

## 1. Identity Architecture & Design

### 1.1. Identity Sources & Synchronization
*   **Cloud Identity**: The IDaaS (Identity as a Service) layer. Required if you don't use Google Workspace.
*   **Google Cloud Directory Sync (GCDS)**:
    *   **Direction**: One-way sync from LDAP/Active Directory -> Google Cloud Identity.
    *   **Users & Groups**: Syncs users and groups. Does **not** sync passwords (passwords remain in AD).
*   **Single Sign-On (SSO)**:
    *   Use SAML 2.0 or OIDC.
    *   Google delegates authentication to the IdP (e.g., ADFS, Okta, Ping).
    *   **Flow**: User -> GCP Console -> Redirect to IdP -> Auth -> Redirect back with Token.

### 1.2. Workload Identity Federation (WIF)
The standard for authenticating **external workloads** (AWS, Azure, On-prem) to Google Cloud without Service Account Keys.
*   **Problem**: Long-lived Service Account keys are a security risk (leakage, rotation management).
*   **Solution**: Exchange external credentials (AWS role, OIDC token) for short-lived GCP tokens.
*   **Architecture**:
    1.  Create a **Workload Identity Pool**.
    2.  Add a **Provider** (AWS, OIDC, SAML).
    3.  Map external attributes (e.g., `aws.role`) to GCP attributes.
    4.  Grant IAM roles to the federated identity.

### 1.3. Service Account Best Practices
*   **Separation of Duties**: One SA per application/microservice.
*   **No Keys**: Use WIF or attached Service Accounts (Metadata server).
*   **Short-Lived Credentials**: Use `roles/iam.serviceAccountTokenCreator` to generate tokens only when needed.

---

## 2. Organization Policy & Hierarchy Design

### 2.1. Resource Hierarchy
*   **Organization**: Root node. Apply global policies here (e.g., "Domain Restricted Sharing").
*   **Folders**: Group projects by Department (HR, Eng) or Environment (Prod, Dev).
    *   *Design Pattern*: Apply restrictive policies at the `Prod` folder level.
*   **Projects**: Trust boundaries. Resources belong to projects.

### 2.2. Policy Inheritance & Evaluation
*   **Inheritance**: Child resources inherit constraints from parents.
*   **Hierarchy Evaluation**:
    *   **List Constraints**: Can `Union` (merge) or `Intersect`.
    *   **Boolean Constraints**: Child can override parent *unless* parent enforces "Deny" strictly (depends on policy type).
*   **Common Architectural Constraints**:
    *   `iam.allowedPolicyMemberDomains`: Restrict IAM grants to only your organization's domain (prevent granting access to `@gmail.com`).
    *   `compute.vmExternalIpAccess`: Deny all, allow only specific VMs via allowlist.
    *   `gcp.resourceLocations`: Enforce data residency (e.g., "Only create resources in `europe-west3`").

---

## 3. Data Protection & Encryption Strategy

### 3.1. Encryption Decision Matrix

| Requirement | Solution | Key Management |
| :--- | :--- | :--- |
| **Standard Compliance** | **Default Encryption** | Google manages everything. No overhead. |
| **Regulatory (PCI-DSS, HIPAA)** | **CMEK (Cloud KMS)** | You manage the key (create, rotate, disable). Google uses it. |
| **"Google cannot see data"** | **CSEK (Customer-Supplied)** | You hold the key. App sends key with data. Google never stores the key. |
| **Hardware Security** | **Cloud HSM** | Keys generated in FIPS 140-2 Level 3 HSMs. |
| **External Key Control** | **Cloud EKM** | Keys stored in external partner (Thales, Fortanix). High latency risk. |

### 3.2. Secret Management
*   **Secret Manager**:
    *   **Single Source of Truth**: Centralized storage for API keys, DB passwords.
    *   **Versioning**: Automatic versioning allows rotation and rollback.
    *   **Integration**: Native integration with Cloud Run, GKE, Cloud Functions (mount as volume or env var).
    *   **Anti-Pattern**: Storing secrets in code, environment variables (visible in dashboard), or GCS buckets.

---

## 4. Network Security (BeyondCorp)

### 4.1. Identity-Aware Proxy (IAP)
*   **Concept**: Shift access controls from the network perimeter (VPN) to the application layer (Identity).
*   **Context-Aware Access**:
    *   Define Access Levels (e.g., "User must be in Group X AND coming from Corp IP AND Device is Managed").
    *   Bind Access Level to IAP-protected resource.
*   **Use Cases**:
    *   Internal Corporate Apps (Intranet).
    *   SSH/RDP access to VMs (IAP TCP Forwarding).

### 4.2. VPC Service Controls (VPC-SC)
*   **Perimeter Security**: Prevents data exfiltration from Google APIs (Storage, BigQuery) to unauthorized networks/projects.
*   **Service Perimeter**: Defines a boundary around projects.
*   **Ingress/Egress Rules**: Allow communication between perimeters or from internet based on strict conditions.
*   **Scenario**: Prevent a user with `Storage Admin` permissions from copying data from `Corp-Prod-Bucket` to their personal `My-Gmail-Bucket`.

---

## 5. PCA Decision Scenarios

### Scenario 1: Multi-Cloud Auth
*   **Requirement**: App in AWS needs to write to BigQuery.
*   **Wrong Way**: Create SA key, save in AWS Secrets Manager.
*   **Right Way**: Configure **Workload Identity Federation**. Trust the AWS IAM Role.

### Scenario 2: Compliance & Key Control
*   **Requirement**: Financial data must be encrypted, and the company must be able to revoke access immediately.
*   **Solution**: Use **CMEK**. Revoking the key in Cloud KMS renders the data inaccessible (Crypto-shredding).

### Scenario 3: Developer Access to VMs
*   **Requirement**: Developers need SSH access to private VMs. No VPN allowed.
*   **Solution**: **IAP for TCP**. Grant `iap.tunnelResourceAccessor` role.

### Scenario 4: Preventing Public Buckets
*   **Requirement**: Ensure no developer can accidentally make a GCS bucket public.
*   **Solution**: Enforce Organization Policy `storage.uniformBucketLevelAccess` and `storage.publicAccessPrevention`.
