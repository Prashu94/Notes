# Google Cloud IAM - Professional Cloud Architect (PCA) Comprehensive Guide

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Resource Hierarchy Design](#resource-hierarchy-design)
3. [Enterprise IAM Strategies](#enterprise-iam-strategies)
4. [Security Architecture](#security-architecture)
5. [Service Account Design Patterns](#service-account-design-patterns)
6. [Advanced Access Control](#advanced-access-control)
7. [Identity Federation](#identity-federation)
8. [Compliance & Governance](#compliance--governance)
9. [Migration & Hybrid Patterns](#migration--hybrid-patterns)
10. [PCA Exam Tips](#pca-exam-tips)

---

## Architectural Overview

For the Professional Cloud Architect exam, IAM is the foundation of security architecture. You must design IAM strategies that balance security, usability, scalability, and compliance requirements across complex organizational structures.

### IAM in Enterprise Architecture

**Core Principles:**
1. **Defense in Depth:** Multiple security layers
2. **Least Privilege:** Minimum necessary access
3. **Separation of Duties:** Prevent conflicts of interest
4. **Zero Trust:** Never trust, always verify
5. **Auditability:** Track all access and changes

---

## Resource Hierarchy Design

### Organization Structure Patterns

**Pattern 1: Environment-Based**
```
Organization (company.com)
├── Folder: Production
│   ├── Folder: North America
│   │   ├── Project: web-app-prod-na
│   │   └── Project: api-backend-prod-na
│   └── Folder: Europe
│       ├── Project: web-app-prod-eu
│       └── Project: api-backend-prod-eu
├── Folder: Staging
│   ├── Project: web-app-staging
│   └── Project: api-backend-staging
└── Folder: Development
    ├── Project: dev-team-a
    └── Project: dev-team-b
```

**Benefits:**
- Clear environment separation
- Different policies per environment
- Easy to apply strict controls to production

**Pattern 2: Business Unit Based**
```
Organization (company.com)
├── Folder: Finance
│   ├── Folder: Production
│   └── Folder: Development
├── Folder: Marketing
│   ├── Folder: Production
│   └── Folder: Development
└── Folder: Engineering
    ├── Folder: Production
    └── Folder: Development
```

**Benefits:**
- Aligns with business structure
- Clear cost attribution
- Business unit autonomy

**Pattern 3: Hybrid (Recommended)**
```
Organization (company.com)
├── Folder: Shared Services
│   ├── Project: networking-hub
│   ├── Project: security-tools
│   └── Project: logging-monitoring
├── Folder: Business Unit: Finance
│   ├── Folder: Production
│   │   ├── Project: finance-app-prod
│   │   └── Project: analytics-prod
│   ├── Folder: Staging
│   └── Folder: Development
└── Folder: Business Unit: Engineering
    ├── Folder: Production
    ├── Folder: Staging
    └── Folder: Development
```

**Benefits:**
- Combines business unit and environment separation
- Shared services for common infrastructure
- Flexible and scalable

### Policy Inheritance Strategy

**Organizational Level Policies:**
```bash
# Block external IP addresses organization-wide
gcloud resource-manager org-policies set-policy \
  --organization=ORGANIZATION_ID \
  compute.vmExternalIpAccess

# Require OS Login organization-wide
gcloud resource-manager org-policies set-policy \
  --organization=ORGANIZATION_ID \
  compute.requireOsLogin
```

**Folder Level Policies:**
```bash
# Production folder: Require production-ready machine types
gcloud resource-manager org-policies set-policy \
  --folder=FOLDER_ID \
  compute.vmExternalIpAccess

# Development folder: Allow more flexibility
gcloud resource-manager org-policies set-policy \
  --folder=DEV_FOLDER_ID \
  constraints/compute.vmExternalIpAccess \
  --action=ALLOW
```

---

## Enterprise IAM Strategies

### Role-Based Access Control (RBAC)

**Define Standard Roles by Job Function:**

**1. Platform Administrator:**
```yaml
Platform Admin:
  Organization Level:
    - roles/resourcemanager.organizationAdmin
    - roles/iam.organizationRoleAdmin
  Responsibilities:
    - Manage organization structure
    - Create folders and projects
    - Define organization policies
```

**2. Security Administrator:**
```yaml
Security Admin:
  Organization Level:
    - roles/iam.securityAdmin
    - roles/iam.securityReviewer
    - roles/logging.admin
  Responsibilities:
    - Audit IAM policies
    - Manage security controls
    - Review access logs
```

**3. Network Administrator:**
```yaml
Network Admin:
  Organization/Folder Level:
    - roles/compute.networkAdmin
    - roles/compute.securityAdmin
  Shared VPC Host Project:
    - roles/compute.xpnAdmin
  Responsibilities:
    - Manage VPC networks
    - Configure firewalls
    - Set up hybrid connectivity
```

**4. Developer (Production):**
```yaml
Production Developer:
  Project Level (Production):
    - roles/compute.viewer
    - roles/storage.objectViewer
    - roles/logging.viewer
  Responsibilities:
    - Read-only access to production
    - View logs for debugging
    - No write permissions
```

**5. Developer (Development):**
```yaml
Development Developer:
  Project Level (Dev/Staging):
    - roles/editor (with org policy restrictions)
    - roles/iam.serviceAccountUser
  Responsibilities:
    - Full dev/staging access
    - Deploy and test applications
    - Create resources
```

### Group-Based Management

**Create Hierarchical Groups:**
```
all-engineers@company.com
├── backend-engineers@company.com
│   ├── backend-senior@company.com
│   └── backend-junior@company.com
├── frontend-engineers@company.com
└── devops-engineers@company.com
    ├── devops-prod-access@company.com
    └── devops-staging-access@company.com
```

**Grant Roles to Groups:**
```bash
# Production read-only for all engineers
gcloud projects add-iam-policy-binding prod-project \
  --member=group:all-engineers@company.com \
  --role=roles/viewer

# DevOps production write access
gcloud projects add-iam-policy-binding prod-project \
  --member=group:devops-prod-access@company.com \
  --role=roles/editor \
  --condition='expression=resource.type != "cloudkms.googleapis.com/KeyRing",title=No KMS Access'
```

### Custom Role Design

**Create Granular Custom Roles:**

**Instance Operator (Start/Stop only):**
```yaml
title: "Instance Operator"
description: "Can start and stop instances but not create/delete"
stage: "GA"
includedPermissions:
- compute.instances.get
- compute.instances.list
- compute.instances.start
- compute.instances.stop
- compute.instances.reset
- compute.zones.get
- compute.zones.list
```

```bash
gcloud iam roles create instanceOperator \
  --organization=ORGANIZATION_ID \
  --file=instance-operator.yaml
```

**BigQuery Data Analyst:**
```yaml
title: "BigQuery Data Analyst"
description: "Run queries but cannot modify datasets"
stage: "GA"
includedPermissions:
- bigquery.jobs.create
- bigquery.jobs.get
- bigquery.jobs.list
- bigquery.tables.get
- bigquery.tables.list
- bigquery.tables.getData
- bigquery.datasets.get
```

---

## Security Architecture

### Multi-Layered Security Model

**Layer 1: Identity**
```
External Identity Provider (Okta, Azure AD)
    ↓
Workforce Identity Federation
    ↓
Cloud Identity / Google Workspace
    ↓
IAM Principals
```

**Layer 2: Access Control**
```
Organization Policies (Guardrails)
    ↓
IAM Roles (What they can do)
    ↓
IAM Conditions (When they can do it)
    ↓
VPC Service Controls (Where they can do it)
```

**Layer 3: Resource Protection**
```
Encryption (CMEK/CSEK)
    ↓
Private Endpoints (no public IPs)
    ↓
Firewall Rules
    ↓
Cloud Armor (DDoS protection)
```

### VPC Service Controls Integration

**Create Security Perimeter:**
```bash
# Create perimeter around sensitive projects
gcloud access-context-manager perimeters create prod-perimeter \
  --title="Production Environment Perimeter" \
  --resources=projects/PROJECT_NUMBER1,projects/PROJECT_NUMBER2 \
  --restricted-services=storage.googleapis.com,bigquery.googleapis.com \
  --policy=POLICY_ID
```

**Use Case:** Prevent data exfiltration from production projects

### IAM Deny Policies

**Prevent Specific Actions:**
```yaml
# Deny policy to prevent IAM privilege escalation
displayName: "Prevent Privilege Escalation"
rules:
  - denyRule:
      deniedPrincipals:
        - principalSet: //iam.googleapis.com/projects/PROJECT_ID/serviceAccounts/*
      deniedPermissions:
        - iam.googleapis.com/serviceAccounts.actAs
        - iam.googleapis.com/serviceAccounts.getAccessToken
      exceptionPrincipals:
        - principalSet: //iam.googleapis.com/projects/PROJECT_ID/serviceAccounts/trusted-sa@PROJECT_ID.iam.gserviceaccount.com
```

```bash
gcloud iam deny-policies create prevent-escalation \
  --attachment-point=cloudresourcemanager.googleapis.com/projects/PROJECT_ID \
  --attachment-point-type=cloudresourcemanager.googleapis.com/project \
  --deny-rules-file=deny-policy.yaml
```

---

## Service Account Design Patterns

### Pattern 1: One Service Account per Service

```
Application Architecture:
├── Web Tier (web-frontend-sa@project.iam.gserviceaccount.com)
│   Permissions: Cloud Storage (read static assets)
├── API Tier (api-backend-sa@project.iam.gserviceaccount.com)
│   Permissions: Cloud SQL, Pub/Sub, Cloud Storage
└── Worker Tier (worker-sa@project.iam.gserviceaccount.com)
    Permissions: Pub/Sub, BigQuery, Cloud Storage
```

**Benefits:**
- Granular permissions per service
- Easy to audit and troubleshoot
- Follows least privilege

### Pattern 2: Shared Service Account with Conditions

```bash
# Grant role with resource-specific condition
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:shared-sa@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectAdmin \
  --condition='expression=resource.name.startsWith("projects/_/buckets/app-data-"),title=App Data Buckets Only'
```

### Pattern 3: Service Account Impersonation

**Instead of downloading keys:**
```
Developer (user@example.com)
    ↓ Impersonates
Service Account (deploy-sa@project.iam.gserviceaccount.com)
    ↓ Has permissions
Deploy to Production
```

**Setup:**
```bash
# Allow developer to impersonate service account
gcloud iam service-accounts add-iam-policy-binding \
  deploy-sa@project.iam.gserviceaccount.com \
  --member=user:developer@example.com \
  --role=roles/iam.serviceAccountTokenCreator
```

**Use:**
```bash
gcloud compute instances create my-vm \
  --impersonate-service-account=deploy-sa@project.iam.gserviceaccount.com
```

### Pattern 4: Workload Identity (GKE)

**Map Kubernetes Service Account to GCP Service Account:**
```bash
# Create GCP service account
gcloud iam service-accounts create gke-app-sa

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:gke-app-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer

# Allow K8s SA to act as GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  gke-app-sa@PROJECT_ID.iam.gserviceaccount.com \
  --member=serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/K8S_SA] \
  --role=roles/iam.workloadIdentityUser
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: default
  annotations:
    iam.gke.io/gcp-service-account: gke-app-sa@PROJECT_ID.iam.gserviceaccount.com
```

**Benefits:**
- No service account keys
- Automatic credential rotation
- Pod-level identity

---

## Advanced Access Control

### IAM Conditions - Time-Based Access

**Business Hours Only:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:contractor@example.com \
  --role=roles/compute.instanceAdmin.v1 \
  --condition='
    expression=
      request.time.getHours("America/New_York") >= 9 &&
      request.time.getHours("America/New_York") <= 17 &&
      request.time.getDayOfWeek("America/New_York") >= 1 &&
      request.time.getDayOfWeek("America/New_York") <= 5,
    title=Business Hours Only (9-5 EST Mon-Fri)'
```

### IAM Conditions - Resource-Based Access

**Specific Resource Names:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:developer@example.com \
  --role=roles/compute.instanceAdmin.v1 \
  --condition='
    expression=
      resource.name.startsWith("projects/my-project/zones/us-central1-a/instances/dev-") ||
      resource.name.startsWith("projects/my-project/zones/us-central1-a/instances/test-"),
    title=Dev and Test Instances Only'
```

### IAM Conditions - IP-Based Access

**Restrict by IP Address:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:remote-admin@example.com \
  --role=roles/compute.admin \
  --condition='
    expression=
      origin.ip.equals("203.0.113.0/24") ||
      origin.ip.equals("198.51.100.5"),
    title=Access from Corporate Network Only'
```

### Context-Aware Access

**Use Access Context Manager:**
```bash
# Create access level
gcloud access-context-manager levels create corp_network \
  --title="Corporate Network" \
  --basic-level-spec=ip_subnetworks=203.0.113.0/24,198.51.100.0/24 \
  --policy=POLICY_ID

# Create perimeter with access level
gcloud access-context-manager perimeters create secure-perimeter \
  --resources=projects/PROJECT_NUMBER \
  --restricted-services=storage.googleapis.com \
  --access-levels=corp_network \
  --policy=POLICY_ID
```

---

## Identity Federation

### Workforce Identity Federation

**Connect External IdP (Okta, Azure AD):**

**Architecture:**
```
External IdP (Azure AD)
    ↓ SAML/OIDC
Workforce Identity Pool
    ↓ Mapped Attributes
IAM Principals
    ↓
GCP Resources
```

**Setup:**
```bash
# Create workforce identity pool
gcloud iam workforce-pools create my-workforce-pool \
  --organization=ORGANIZATION_ID \
  --location=global \
  --display-name="Company Workforce Pool"

# Create workforce identity provider (OIDC)
gcloud iam workforce-pools providers create-oidc azure-ad-provider \
  --workforce-pool=my-workforce-pool \
  --location=global \
  --issuer-uri=https://login.microsoftonline.com/TENANT_ID/v2.0 \
  --client-id=CLIENT_ID \
  --attribute-mapping="google.subject=assertion.sub,google.groups=assertion.groups" \
  --display-name="Azure AD Provider"
```

**Benefits:**
- Single sign-on (SSO)
- Centralized identity management
- No need to create Google Accounts

### Workload Identity Federation

**Connect External Workloads (AWS, Azure, On-Prem):**

**Architecture:**
```
External Workload (AWS Lambda)
    ↓ OIDC Token
Workload Identity Pool
    ↓ Attribute Mapping
Service Account
    ↓
GCP Resources
```

**Setup:**
```bash
# Create workload identity pool
gcloud iam workload-identity-pools create aws-pool \
  --location=global \
  --display-name="AWS Workload Pool"

# Create AWS provider
gcloud iam workload-identity-pools providers create-aws aws-provider \
  --workload-identity-pool=aws-pool \
  --location=global \
  --account-id=AWS_ACCOUNT_ID \
  --attribute-mapping="google.subject=assertion.arn,attribute.aws_role=assertion.arn.extract('assumed-role/{role}/')"

# Grant service account access
gcloud iam service-accounts add-iam-policy-binding \
  my-sa@my-project.iam.gserviceaccount.com \
  --member=principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/aws-pool/attribute.aws_role/MyLambdaRole \
  --role=roles/iam.workloadIdentityUser
```

**Use Case:** AWS Lambda accessing Cloud Storage without service account keys

---

## Compliance & Governance

### Compliance Frameworks

**HIPAA Compliance Architecture:**
```
Organization Policy:
├── Require CMEK for all data
├── Restrict data to specific regions
├── Enable audit logging
└── Require VPC Service Controls

IAM Configuration:
├── Separate PHI access group
├── Time-limited access
├── Multi-factor authentication required
└── Break-glass emergency access

Audit & Monitoring:
├── Cloud Audit Logs → BigQuery
├── Alert on IAM changes
├── Regular access reviews
└── Compliance reports
```

**PCI-DSS Compliance:**
```
Cardholder Data Environment (CDE):
├── Isolated projects
├── VPC Service Controls perimeter
├── No external IPs
├── Encrypted with CMEK
└── Strict IAM policies

Access Control:
├── Least privilege roles
├── Quarterly access reviews
├── Service account key rotation
└── Audit logs retention (1 year)
```

### Organization Policy Constraints

**Restrict Resource Locations:**
```yaml
# Allow only US and EU
constraint: constraints/gcp.resourceLocations
listPolicy:
  allowedValues:
    - in:us-locations
    - in:eu-locations
```

```bash
gcloud resource-manager org-policies set-policy \
  --organization=ORGANIZATION_ID \
  location-policy.yaml
```

**Restrict Service Account Key Creation:**
```bash
gcloud resource-manager org-policies set-policy \
  --organization=ORGANIZATION_ID \
  constraints/iam.disableServiceAccountKeyCreation
```

**Require OS Login:**
```bash
gcloud resource-manager org-policies set-policy \
  --organization=ORGANIZATION_ID \
  constraints/compute.requireOsLogin
```

### Access Transparency & Approval

**Access Transparency:**
- Logs showing Google admin actions
- Required for compliance (HIPAA, PCI-DSS)

**Access Approval:**
- Require approval before Google support accesses data
- Set up approval groups

```bash
# Enable Access Approval
gcloud access-approval settings update \
  --organization=ORGANIZATION_ID \
  --enrolled_services=all \
  --notification_emails=security-team@example.com
```

---

## Migration & Hybrid Patterns

### Lift-and-Shift IAM Strategy

**Phase 1: Discovery**
- Map on-prem users to GCP roles
- Identify service accounts
- Document access requirements

**Phase 2: Migration**
```
On-Prem AD/LDAP
    ↓ Sync via Cloud Identity
Google Cloud Identity
    ↓ GCDS (Google Cloud Directory Sync)
GCP IAM
```

**Phase 3: Hybrid Operation**
- Federate identities
- Maintain single source of truth (on-prem AD)
- Gradual transition to cloud-native identity

### Hybrid Cloud IAM

**Architecture:**
```
Corporate Network
├── On-Prem Workloads
│   ↓ Private Connectivity (Interconnect/VPN)
│   └── Shared VPC (GCP)
├── Identity Federation
│   ↓ SAML/OIDC
│   └── Workforce Identity Pool
└── Centralized Logging
    └── Cloud Logging + On-Prem SIEM
```

---

## PCA Exam Tips

### 1. Resource Hierarchy Design
- **Organization:** Root (use organization policies)
- **Folders:** Group projects (env, business unit)
- **Projects:** Billing boundary, isolation unit
- **Resources:** Inherit policies from ancestors

### 2. IAM vs Organization Policies
- **IAM:** WHO can do WHAT
- **Org Policies:** WHAT can be done (constraints/guardrails)
- **Use Both:** IAM for access, Org Policy for compliance

### 3. Service Account Best Practices
- **One SA per service** (preferred)
- **Avoid keys** (use impersonation or Workload Identity)
- **Rotate keys** if must use (90 days max)
- **Audit regularly** (Policy Analyzer)

### 4. Custom Roles
- **When:** Predefined roles too broad
- **Where:** Organization or project level
- **Maintenance:** Higher overhead than predefined
- **Limit:** 300 per organization

### 5. IAM Conditions
- **Time-based:** Expiration, business hours
- **Resource-based:** Specific resource names/types
- **Request-based:** IP address, device type
- **Version 3 policy required**

### 6. Identity Federation
- **Workforce:** Human users (Okta, Azure AD)
- **Workload:** Applications (AWS, Azure, on-prem)
- **Benefits:** No Google Accounts, SSO, centralized management

### 7. VPC Service Controls
- **Purpose:** Prevent data exfiltration
- **Perimeter:** Group projects with sensitive data
- **Restricted Services:** Specify which APIs
- **Access Levels:** Control who can access (IP, device)

### 8. Compliance Patterns
- **Audit Logs:** Enable for all admin/data access
- **Retention:** Store logs long-term (BigQuery)
- **Alerts:** Real-time notification on sensitive changes
- **Access Reviews:** Quarterly or more frequent

### 9. Break-Glass Access
- **Emergency:** Highly privileged account
- **Secure:** Offline, multi-person access
- **Alert:** Immediate notification on use
- **Audit:** Detailed logging

### 10. Policy Analyzer
- **Who has access:** List all principals with access to resource
- **What can they do:** List all permissions
- **Unused permissions:** Identify over-privileged accounts
- **Recommender:** Suggest role changes

### 11. Separation of Duties
- **Platform Admin:** Manage structure (no data access)
- **Security Admin:** Manage security (audit only)
- **Data Admin:** Manage data (no infrastructure)
- **Developer:** Build apps (no production access)

### 12. Multi-Tenancy Patterns
- **Project per Tenant:** Strong isolation, high overhead
- **Resource per Tenant:** Shared project, IAM separation
- **Data per Tenant:** Shared resources, data-level isolation

### 13. Common Exam Scenarios
- "Restrict data to specific regions" → **Organization Policy**
- "Temporary contractor access" → **IAM Conditions (expiration)**
- "Application on AWS accessing GCP" → **Workload Identity Federation**
- "Single Sign-On for employees" → **Workforce Identity Federation**
- "Prevent privilege escalation" → **Deny Policies**
- "Audit who has access" → **Policy Analyzer**

### 14. Cost Optimization
- Regular access reviews (remove unused)
- Delete unused service accounts
- Use groups (easier management)
- Automate with Policy Intelligence

### 15. Security Best Practices
- **Never** use basic roles in production
- **Always** use groups (not individual users)
- **Enable** audit logging
- **Review** permissions quarterly
- **Rotate** service account keys
- **Prefer** impersonation over keys
