# Google Cloud Security & IAM Guide (ACE - Associate Cloud Engineer)

## 1. Identity and Access Management (IAM) Fundamentals

### 1.1. The "Who", "What", and "Which"
IAM connects **Principals** (Who) to **Roles** (What permissions) on **Resources** (Which resource).

*   **Principals**:
    *   **Google Account**: `user@gmail.com`
    *   **Service Account**: `app-id@project-id.iam.gserviceaccount.com`
    *   **Google Group**: `admins@example.com` (Best practice for managing users at scale).
    *   **Cloud Identity / Workspace Domain**: `user@example.com`.
    *   **allUsers**: Anyone on the internet (Public).
    *   **allAuthenticatedUsers**: Anyone with a Google Account.

### 1.2. Roles
*   **Basic (Primitive) Roles**: (Avoid in production)
    *   `Owner`: Full access + Manage IAM.
    *   `Editor`: Edit resources + View.
    *   `Viewer`: Read-only.
*   **Predefined Roles**: Granular access managed by Google.
    *   `roles/compute.instanceAdmin.v1`: Full control of Compute Engine instances.
    *   `roles/storage.objectViewer`: Read-only access to GCS objects.
*   **Custom Roles**: User-defined collection of permissions.
    *   *Limitation*: Cannot be used on a Folder level (only Org or Project).

### 1.3. IAM Policy Hierarchy
Policies are inherited. A permission granted at the **Organization** level applies to all **Folders** and **Projects** below it.
*   **Allow Policies**: Additive. You cannot "deny" a permission granted at a higher level using a standard IAM Allow policy (Deny policies exist but are advanced).
*   **Best Practice**: Follow the **Principle of Least Privilege**.

---

## 2. Service Accounts (SA)

### 2.1. Types of Service Accounts
1.  **User-Managed**: Created by you.
    *   Format: `service-account-name@project-id.iam.gserviceaccount.com`
2.  **Default Service Accounts**: Created automatically by services (e.g., Compute Engine, App Engine).
    *   *Risk*: Often have the `Editor` role by default. **Recommendation**: Remove the Editor role and assign granular roles.
3.  **Service Agents**: Google-managed accounts used by Google services to interact with your resources.
    *   Format: `service-[PROJECT_NUMBER]@gcp-sa-[SERVICE].iam.gserviceaccount.com`

### 2.2. Managing Service Accounts (CLI)
```bash
# Create a Service Account
gcloud iam service-accounts create my-app-sa \
    --display-name "My App Service Account"

# Grant a Role to the SA (Binding it to a resource)
gcloud projects add-iam-policy-binding my-project-id \
    --member "serviceAccount:my-app-sa@my-project-id.iam.gserviceaccount.com" \
    --role "roles/storage.objectViewer"

# List Service Accounts
gcloud iam service-accounts list
```

### 2.3. Service Account Keys
*   **Managed Keys**: Rotated automatically by Google (used for internal GCP auth).
*   **User-Managed Keys**: JSON files downloaded to your machine.
    *   *Risk*: High security risk if leaked.
    *   *Best Practice*: Avoid if possible. Use **Workload Identity Federation** for external workloads.

```bash
# Create and download a key (Only if absolutely necessary)
gcloud iam service-accounts keys create key.json \
    --iam-account my-app-sa@my-project-id.iam.gserviceaccount.com
```

### 2.4. Service Account Impersonation
Allows a user (or another SA) to generate short-lived credentials for a Service Account without downloading a key.
*   **Required Role**: `roles/iam.serviceAccountTokenCreator`

```bash
# Run a command as the service account
gcloud compute instances list --impersonate-service-account=my-app-sa@my-project-id.iam.gserviceaccount.com
```

---

## 3. Organization Policies
Constraints applied to the resource hierarchy to restrict configuration.

*   **Difference from IAM**: IAM says "Who can do what". Org Policy says "What can be done" (regardless of who does it).
*   **Common Constraints**:
    *   `constraints/compute.vmExternalIpAccess`: Prevent VMs from having public IPs.
    *   `constraints/iam.disableServiceAccountKeyCreation`: Prevent creation of SA keys.
    *   `constraints/gcp.resourceLocations`: Restrict resource creation to specific regions (e.g., `europe-west1`).

```bash
# List available constraints
gcloud resource-manager org-policies list

# Describe a policy on a project
gcloud resource-manager org-policies describe constraints/compute.vmExternalIpAccess --project=my-project-id
```

---

## 4. Identity-Aware Proxy (IAP)

### 4.1. Overview
Controls access to cloud applications and VMs running on Google Cloud. verifies user identity and context of the request.

### 4.2. IAP for TCP (SSH/RDP)
Allows SSH access to VMs without assigning them external IP addresses.
*   **Requirement**: Firewall rule allowing ingress from `35.235.240.0/20` on port 22 (SSH) or 3389 (RDP).
*   **IAM Role**: `roles/iap.tunnelResourceAccessor`.

```bash
# Connect via IAP (Tunnel)
gcloud compute ssh my-vm --tunnel-through-iap
```

---

## 5. Cloud KMS & Secret Manager

### 5.1. Cloud Key Management Service (KMS)
*   **Google-Managed Keys**: Default encryption for all data at rest.
*   **Customer-Managed Encryption Keys (CMEK)**: You manage the key (rotation, destruction) in Cloud KMS, but Google services use it.
*   **Key Hierarchy**:
    *   **Key Ring**: Logical grouping of keys (Regional).
    *   **CryptoKey**: The actual key.
    *   **Key Version**: Specific version of the key material.

```bash
# Create a Key Ring
gcloud kms keyrings create my-keyring --location global

# Create a Key
gcloud kms keys create my-key --location global --keyring my-keyring --purpose encryption
```

### 5.2. Secret Manager
Securely stores API keys, passwords, and certificates.
*   **Features**: Versioning, IAM access control, Audit logging.
*   **Usage**: Application retrieves the secret at runtime via API.

```bash
# Create a secret
gcloud secrets create my-database-password --replication-policy="automatic"

# Add a secret version (the actual password)
echo -n "SuperSecret123" | gcloud secrets versions add my-database-password --data-file=-

# Access the secret
gcloud secrets versions access latest --secret="my-database-password"
```

---

## 6. ACE Exam Cheat Sheet

| Feature | Key Concept |
| :--- | :--- |
| **Service Account** | Identity for an application. Use `iam.serviceAccountUser` to attach it to a VM. |
| **Service Account Key** | Avoid downloading. If used, rotate regularly. |
| **Scopes** | Legacy access control for VMs. **Best Practice**: Set scopes to `cloud-platform` (full access) and use IAM to restrict. |
| **IAP** | "Zero Trust" access. Replaces VPN/Bastion for SSH/RDP. Needs firewall rule `35.235.240.0/20`. |
| **Directory Sync** | Sync users from AD/LDAP to Cloud Identity. One-way sync. |
| **Audit Logs** | `Admin Activity` (Always on, free), `Data Access` (Must enable, paid). |
