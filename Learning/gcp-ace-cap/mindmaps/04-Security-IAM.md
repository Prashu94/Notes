# GCP Security & IAM - Detailed Mindmap & Design

## 1. Identity & Access Management (IAM)
*   **Core Concepts**
    *   **Principal (Who)**:
        *   *Google Account*: Individual user (`user@gmail.com`).
        *   *Service Account*: Application identity (`app@project.iam...`).
        *   *Google Group*: Collection of users (`admins@example.com`). **Best Practice**: Assign roles to groups, not users.
        *   *Cloud Identity / Workspace Domain*: Org-level management.
        *   *allUsers*: Public (Unauthenticated).
        *   *allAuthenticatedUsers*: Any Google account.
    *   **Role (What)**:
        *   *Primitive (Basic)*: Owner, Editor, Viewer. **Avoid in production**. Too broad.
        *   *Predefined*: Granular, managed by Google (e.g., `roles/storage.objectViewer`).
        *   *Custom*: User-defined permissions. (Note: Cannot be used at Folder level).
    *   **Resource (Which)**: Org -> Folder -> Project -> Resource.
    *   **Policy**: Collection of bindings (Principal + Role).
*   **Inheritance**
    *   Policies flow down.
    *   Child policy cannot *deny* what parent allows (Allow policies are additive).
    *   *Deny Policies*: Advanced feature to explicitly deny access.

## 2. Service Accounts (SA)
*   **Types**
    *   *User-managed*: Created by you.
    *   *Default*: Created by services (Compute Engine, App Engine). Often have Editor role (Security Risk!).
    *   *Service Agents*: Google-managed (e.g., `service-PROJECT_NUM@...`).
*   **Keys**
    *   *Google-managed*: Rotated automatically. Used internally.
    *   *User-managed*: JSON/P12 files. **Security Risk**. Avoid downloading. Use Workload Identity instead.
*   **Scopes vs. IAM**
    *   *Access Scopes*: Legacy method for VMs. "Allow API access".
    *   *Best Practice*: Set Scopes to `cloud-platform` (Allow all) and use IAM to restrict access.

## 3. Security Services
*   **Cloud Armor**
    *   WAF (Web Application Firewall).
    *   DDoS protection (L3/L4/L7).
    *   IP Allow/Deny lists.
    *   Geo-blocking.
    *   SQL Injection / XSS protection.
    *   *Target*: Global HTTP(S) Load Balancer.
*   **Identity-Aware Proxy (IAP)**
    *   **Zero Trust Access**.
    *   *Web Apps*: Authenticate users before they reach your app. No VPN needed.
    *   *VM Access*: SSH/RDP without public IP.
        *   Firewall Rule: Allow ingress from `35.235.240.0/20`.
        *   Role: `roles/iap.tunnelResourceAccessor`.
*   **Cloud KMS (Key Management Service)**
    *   **CMEK (Customer Managed Encryption Keys)**: You manage key rotation/lifecycle. Google uses it to encrypt data.
    *   **CSEK (Customer Supplied Encryption Keys)**: You hold the key. Google never sees it.
    *   **Key Hierarchy**: Key Ring (Location) -> Key -> Key Version.
    *   **Rotation**: Automatic (Symmetric) or Manual.
*   **Secret Manager**
    *   Store sensitive data (API keys, DB passwords, Certs).
    *   Versioning.
    *   IAM access control.
    *   *Best Practice*: Mount as volume in Cloud Run/GKE or access via API.

## 4. Organization Policies
*   **Constraint based**: "What can be done" (vs IAM "Who can do it").
*   **Common Constraints**:
    *   `constraints/compute.vmExternalIpAccess`: Prevent Public IPs.
    *   `constraints/iam.disableServiceAccountKeyCreation`: Prevent key downloads.
    *   `constraints/gcp.resourceLocations`: Restrict regions (e.g., EU only).
    *   `constraints/compute.trustedImageProjects`: Restrict image sources.

---

## 🧠 Design Decision Guide: Security

### Access Control Strategy
1.  **User Access**:
    *   Group users in Google Groups.
    *   Assign Predefined Roles to Groups.
    *   Use Custom Roles if Predefined are too broad.
2.  **App Access**:
    *   Create dedicated Service Account per app.
    *   Grant least privilege.
    *   Use Workload Identity for GKE/External apps.
3.  **VM Access**:
    *   No Public IPs.
    *   Use IAP for SSH/RDP.
    *   OS Login for granular user management.

### Encryption Choice
1.  **Default**: Google-managed keys (No effort).
2.  **Compliance/Control**: CMEK (Cloud KMS). You control rotation/destruction.
3.  **Paranoid/Strict Regs**: CSEK (You keep the key).

### 🔑 Key Exam Rules
1.  **"SSH without Public IP"** -> **IAP**.
2.  **"Prevent Public IPs"** -> **Org Policy**.
3.  **"WAF" or "SQL Injection"** -> **Cloud Armor**.
4.  **"Store API Key"** -> **Secret Manager**.
5.  **"Manage Encryption Keys"** -> **Cloud KMS (CMEK)**.
6.  **"Least Privilege"** -> **Predefined/Custom Roles** (Not Primitive).
