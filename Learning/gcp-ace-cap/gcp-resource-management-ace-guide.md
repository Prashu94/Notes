# Google Cloud Resource Management - Associate Cloud Engineer (ACE) Guide

## Table of Contents
1. [Overview](#overview)
2. [Resource Hierarchy](#resource-hierarchy)
3. [Organizations](#organizations)
4. [Folders](#folders)
5. [Projects](#projects)
6. [Organizational Policies](#organizational-policies)
7. [Cloud Asset Inventory](#cloud-asset-inventory)
8. [Quotas and Limits](#quotas-and-limits)
9. [API Management](#api-management)
10. [Labels and Tags](#labels-and-tags)
11. [Best Practices](#best-practices)
12. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

Google Cloud resource management provides a hierarchical structure to organize and manage your cloud resources. Understanding this hierarchy is fundamental to implementing proper access control, cost tracking, and governance.

**Key Benefits:**
- **Centralized management** of resources across your organization
- **Inheritance** of IAM policies and organizational policies
- **Cost allocation** and tracking
- **Compliance** enforcement through policies

---

## Resource Hierarchy

### Hierarchy Structure

```
Organization (example.com)
│
├── Folder: Production
│   ├── Project: web-app-prod
│   │   ├── Compute Engine VMs
│   │   ├── Cloud Storage Buckets
│   │   └── Cloud SQL Instances
│   │
│   └── Project: api-backend-prod
│       ├── GKE Clusters
│       └── Cloud Functions
│
├── Folder: Development
│   ├── Project: dev-sandbox-1
│   └── Project: dev-sandbox-2
│
└── Folder: Shared Services
    └── Project: shared-networking
        ├── VPCs (Shared VPC Host)
        └── Cloud DNS Zones
```

### Hierarchy Levels

**1. Organization (Top Level)**
- Root node of the hierarchy
- Tied to a Google Workspace or Cloud Identity domain
- one organization per company/domain
- Format: `organizations/123456789012`

**2. Folders (Optional, Middle Level)**
- Group projects by department, team, or environment
- Can be nested (max 10 levels deep)
- Format: `folders/123456789012`

**3. Projects (Required)**
- Base-level organizing entity
- Contains all GCP resources
- Unique project ID and number
- Format: `projects/my-project-id`

**4. Resources (Lowest Level)**
- Actual GCP services (VMs, buckets, databases)
- Always belong to a project

### Hierarchy Inheritance

**Policy Inheritance Rules:**
```
Organization Policy (Least restrictive)
    ↓ (inherited by)
Folder Policy
    ↓ (inherited by)
Project Policy
    ↓ (inherited by)
Resource Policy (Most specific)
```

**Key Principles:**
- Policies are **additive** - child inherits parent's permissions
- Child **cannot remove** access granted at parent level
- Child **can add** more permissions
- Effective policy = Union of all policies from resource to organization

---

## Organizations

### What is an Organization?

The organization resource is the root node of the Google Cloud resource hierarchy. It represents your company and provides centralized control.

**Requirements:**
- Google Workspace or Cloud Identity account
- Super Admin must enable organization resource

### Create Organization

**Automatic Creation:**
When you create a Google Workspace or Cloud Identity domain, GCP automatically creates an organization resource.

**Find Your Organization:**
```bash
# List organizations you have access to
gcloud organizations list

# Get organization details
gcloud organizations describe ORGANIZATION_ID
```

### Organization Roles

**Key Roles:**

| Role | Permissions | Use Case |
|------|------------|----------|
| `roles/resourcemanager.organizationAdmin` | Full control of organization | Senior IT leadership |
| `roles/resourcemanager.organizationViewer` | View organization structure | Auditors, read-only access |
| `roles/resourcemanager.folderAdmin` | Create/manage folders | IT administrators |
| `roles/resourcemanager.projectCreator` | Create projects | Team leads, developers |
| `roles/billing.admin` | Manage billing accounts | Finance team |

**Grant Organization Admin:**
```bash
gcloud organizations add-iam-policy-binding ORGANIZATION_ID \
  --member=user:admin@example.com \
  --role=roles/resourcemanager.organizationAdmin
```

### Organization Settings

**View Organization:**
```bash
gcloud organizations describe ORGANIZATION_ID
```

**Example Output:**
```yaml
name: organizations/123456789012
displayName: example.com
directoryCustomerId: C012abc34
creationTime: '2020-01-15T10:30:00.000Z'
lifecycleState: ACTIVE
```

---

## Folders

### What are Folders?

Folders provide an additional grouping mechanism between organizations and projects. They're useful for reflecting business structure.

**Common Folder Structures:**

**By Environment:**
```
Organization
├── Production
├── Staging
└── Development
```

**By Department:**
```
Organization
├── Engineering
├── Marketing
├── Finance
└── HR
```

**By Product/Team:**
```
Organization
├── Product-A
│   ├── Production
│   └── Development
└── Product-B
    ├── Production
    └── Development
```

### Create Folders

**Top-level Folder:**
```bash
# Create folder under organization
gcloud resource-manager folders create \
  --display-name=Production \
  --organization=ORGANIZATION_ID
```

**Nested Folder:**
```bash
# Create folder under another folder
gcloud resource-manager folders create \
  --display-name=Engineering \
  --folder=PARENT_FOLDER_ID
```

### Manage Folders

**List Folders:**
```bash
# List folders under organization
gcloud resource-manager folders list \
  --organization=ORGANIZATION_ID

# List folders under a folder
gcloud resource-manager folders list \
  --folder=FOLDER_ID
```

**Get Folder Details:**
```bash
gcloud resource-manager folders describe FOLDER_ID
```

**Move Folder:**
```bash
gcloud resource-manager folders move FOLDER_ID \
  --folder=NEW_PARENT_FOLDER_ID
```

**Delete Folder:**
```bash
# Folder must be empty (no projects or subfolders)
gcloud resource-manager folders delete FOLDER_ID
```

### Folder IAM

**Grant Folder Access:**
```bash
gcloud resource-manager folders add-iam-policy-binding FOLDER_ID \
  --member=user:developer@example.com \
  --role=roles/viewer
```

**View Folder IAM Policy:**
```bash
gcloud resource-manager folders get-iam-policy FOLDER_ID
```

---

## Projects

### What is a Project?

A project is the base-level organizing entity in GCP. All resources must belong to a project.

**Project Identifiers:**
- **Project Name:** Human-readable display name (can be changed)
- **Project ID:** Globally unique identifier (permanent, cannot be changed)
- **Project Number:** Automatically assigned number (used by GCP internally)

**Example:**
```
Project Name:    My Web Application
Project ID:      my-web-app-prod-2024
Project Number:  123456789012
```

### Create Projects

**Under Organization:**
```bash
gcloud projects create my-project-123 \
  --name="My Project" \
  --organization=ORGANIZATION_ID \
  --labels=environment=production,team=engineering
```

**Under Folder:**
```bash
gcloud projects create my-project-123 \
  --name="My Project" \
  --folder=FOLDER_ID
```

**Set Default Project:**
```bash
# Set for current session
gcloud config set project my-project-123

# Verify
gcloud config get-value project
```

### Manage Projects

**List Projects:**
```bash
# List all projects you have access to
gcloud projects list

# Filter by folder
gcloud projects list --filter="parent.id=FOLDER_ID"

# Filter by label
gcloud projects list --filter="labels.environment=production"
```

**Get Project Details:**
```bash
gcloud projects describe my-project-123
```

**Update Project:**
```bash
# Update name
gcloud projects update my-project-123 \
  --name="New Project Name"

# Add labels
gcloud projects update my-project-123 \
  --update-labels=cost-center=12345,owner=john
```

**Move Project:**
```bash
# Move to different folder
gcloud projects move my-project-123 \
  --folder=NEW_FOLDER_ID

# Move to organization (remove from folder)
gcloud projects move my-project-123 \
  --organization=ORGANIZATION_ID
```

**Delete Project:**
```bash
# Soft delete (can be restored within 30 days)
gcloud projects delete my-project-123

# List deleted projects
gcloud projects list --filter="lifecycleState=DELETE_REQUESTED"

# Restore deleted project
gcloud projects undelete my-project-123
```

### Project IAM

**Grant Project Access:**
```bash
gcloud projects add-iam-policy-binding my-project-123 \
  --member=user:developer@example.com \
  --role=roles/editor
```

**View Project IAM Policy:**
```bash
gcloud projects get-iam-policy my-project-123
```

---

## Organizational Policies

### What are Organizational Policies?

Organizational policies provide centralized control over your organization's cloud resources. They allow you to set restrictions on how resources can be configured.

**Use Cases:**
- Restrict which regions resources can be created in
- Disable creation of external IP addresses
- Require encryption on Cloud Storage buckets
- Enforce uniform bucket-level access

### Policy Types

**1. List Constraints:**
Allow or deny specific values.

**Example:** Restrict allowed regions
```
Policy: constraints/gcp.resourceLocations
Allowed Values: us-central1, us-east1
```

**2. Boolean Constraints:**
Enable or disable a feature.

**Example:** Disable VM serial port access
```
Policy: constraints/compute.disableSerialPortAccess
Value: True
```

### Common Organizational Policies

**Compute Engine:**
- `constraints/compute.disableSerialPortAccess` - Disable serial port
- `constraints/compute.vmExternalIpAccess` - Restrict external IPs
- `constraints/compute.requireShieldedVm` - Require Shielded VMs
- `constraints/compute.requireOsLogin` - Require OS Login

**Storage:**
- `constraints/storage.uniformBucketLevelAccess` - Enforce uniform access
- `constraints/storage.publicAccessPrevention` - Prevent public access

**Resource Locations:**
- `constraints/gcp.resourceLocations` - Restrict resource locations

**IAM:**
- `constraints/iam.disableServiceAccountKeyCreation` - Prevent SA key downloads
- `constraints/iam.automaticIamGrantsForDefaultServiceAccounts` - Control default SA permissions

### Set Organizational Policies

**Create Policy File (policy.yaml):**
```yaml
name: organizations/ORGANIZATION_ID/policies/gcp.resourceLocations
spec:
  rules:
    - values:
        allowedValues:
          - in:us-locations
          - in:europe-locations
```

**Apply Policy:**
```bash
gcloud org-policies set-policy policy.yaml
```

**Using gcloud directly:**

**Restrict Resource Locations:**
```bash
gcloud org-policies set-policy - <<EOF
name: organizations/ORGANIZATION_ID/policies/gcp.resourceLocations
spec:
  rules:
    - values:
        allowedValues:
          - us-central1
          - us-east1
EOF
```

**Disable Serial Port Access:**
```bash
gcloud org-policies set-policy - <<EOF
name: organizations/ORGANIZATION_ID/policies/compute.disableSerialPortAccess
spec:
  rules:
    - enforce: true
EOF
```

**Prevent Service Account Key Creation:**
```bash
gcloud org-policies set-policy - <<EOF
name: organizations/ORGANIZATION_ID/policies/iam.disableServiceAccountKeyCreation
spec:
  rules:
    - enforce: true
EOF
```

### View Organizational Policies

**List All Policies:**
```bash
gcloud org-policies list --organization=ORGANIZATION_ID
```

**View Specific Policy:**
```bash
gcloud org-policies describe gcp.resourceLocations \
  --organization=ORGANIZATION_ID
```

**Check Effective Policy (inheritance):**
```bash
# Check what policy applies to a project
gcloud org-policies describe gcp.resourceLocations \
  --project=my-project-123 \
  --effective
```

### Delete/Reset Policies

**Delete Policy:**
```bash
gcloud org-policies delete gcp.resourceLocations \
  --organization=ORGANIZATION_ID
```

---

## Cloud Asset Inventory

### What is Cloud Asset Inventory?

Cloud Asset Inventory provides a historical view of your GCP resources and IAM policies. It helps with:
- **Compliance auditing**
- **Security analysis**
- **Resource tracking**
- **Change management**

### Export Assets

**Export to Cloud Storage:**
```bash
gcloud asset export \
  --organization=ORGANIZATION_ID \
  --content-type=resource \
  --output-path=gs://my-bucket/assets.json
```

**Export IAM Policies:**
```bash
gcloud asset export \
  --project=my-project-123 \
  --content-type=iam-policy \
  --output-path=gs://my-bucket/iam-policies.json
```

**Export Specific Resource Types:**
```bash
gcloud asset export \
  --project=my-project-123 \
  --asset-types=compute.googleapis.com/Instance,storage.googleapis.com/Bucket \
  --output-path=gs://my-bucket/compute-storage.json
```

### Search Assets

**Search for Resources:**
```bash
# Find all VMs
gcloud asset search-all-resources \
  --scope=organizations/ORGANIZATION_ID \
  --asset-types=compute.googleapis.com/Instance

# Find resources by label
gcloud asset search-all-resources \
  --scope=projects/my-project-123 \
  --query="labels.environment=production"

# Find resources in specific location
gcloud asset search-all-resources \
  --scope=projects/my-project-123 \
  --query="location:us-central1"
```

**Search IAM Policies:**
```bash
# Find who has specific role
gcloud asset search-all-iam-policies \
  --scope=organizations/ORGANIZATION_ID \
  --query="policy:roles/owner"

# Find permissions for specific user
gcloud asset search-all-iam-policies \
  --scope=organizations/ORGANIZATION_ID \
  --query="policy:user:admin@example.com"
```

### Asset Feed (Real-time Notifications)

**Create Asset Feed:**
```bash
gcloud asset feeds create my-feed \
  --project=my-project-123 \
  --asset-types=compute.googleapis.com/Instance \
  --content-type=resource \
  --pubsub-topic=projects/my-project-123/topics/asset-changes
```

**Use Case:** Get notified when VMs are created/deleted

---

## Quotas and Limits

### What are Quotas?

Quotas prevent unintended resource consumption and limit API requests. There are two types:

**1. Rate Quotas:** Limit requests over time (e.g., 1000 API calls per minute)
**2. Allocation Quotas:** Limit resource count (e.g., 24 CPUs per region)

### View Quotas

**List All Quotas:**
```bash
gcloud compute project-info describe --project=my-project-123
```

**View Specific Service Quotas:**
```bash
# Compute Engine quotas
gcloud compute regions describe us-central1

# Example output shows quotas:
# - CPUS: 24 (per region)
# - IN_USE_ADDRESSES: 8 (static IPs)
# - INSTANCES: 100 (VM instances)
```

**Console Method:**
1. Go to **IAM & Admin** → **Quotas**
2. Filter by service, region, or quota name
3. View current usage vs limit

### Common Quotas

**Compute Engine (per region):**
- CPUs: 24
- Persistent Disk SSD (GB): 500
- In-use IP addresses: 8
- VM Instances: 100

**Cloud Storage:**
- Bucket creation/deletion: 1 every 2 seconds
- Object writes: No quota (unlimited)

**BigQuery:**
- Concurrent queries: 100
- Slots: 2000 (on-demand)

### Request Quota Increase

**Via Console:**
1. **IAM & Admin** → **Quotas**
2. Select the quota
3. Click **Edit Quotas**
4. Enter new limit
5. Provide justification
6. Submit request

**Via gcloud:**
```bash
# Note: Must use Console for quota increase requests
# gcloud can only view quotas, not modify them
```

**Best Practices:**
- Request increases **before** you need them (can take 2-3 days)
- Provide clear business justification
- Start with reasonable increases

---

## API Management

### Enable APIs

**Why Enable APIs?**
By default, most GCP APIs are disabled. You must enable them before use.

**Enable API:**
```bash
# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# Enable multiple APIs
gcloud services enable \
  compute.googleapis.com \
  storage.googleapis.com \
  sqladmin.googleapis.com
```

**Common APIs:**
```bash
# Compute Engine
compute.googleapis.com

# Cloud Storage
storage.googleapis.com

# Cloud SQL
sqladmin.googleapis.com

# GKE
container.googleapis.com

# Cloud Functions
cloudfunctions.googleapis.com

# Cloud Run
run.googleapis.com

# BigQuery
bigquery.googleapis.com

# Pub/Sub
pubsub.googleapis.com
```

### Manage APIs

**List Enabled APIs:**
```bash
gcloud services list --enabled
```

**List Available APIs:**
```bash
gcloud services list --available
```

**Disable API:**
```bash
# Warning: This will break resources using the API!
gcloud services disable compute.googleapis.com
```

**Check if API is Enabled:**
```bash
gcloud services list --enabled --filter="name:compute.googleapis.com"
```

---

## Labels and Tags

### Labels

Labels are key-value pairs attached to resources for organization and cost tracking.

**Label Characteristics:**
- Maximum 64 labels per resource
- Keys and values are case-sensitive
- Keys: 1-63 characters
- Values: 0-63 characters

**Common Label Use Cases:**
```
environment: production | staging | development
team: engineering | marketing | finance
cost-center: 12345
owner: john-doe
application: web-app | mobile-api
version: v1 | v2
```

**Add Labels to Resources:**

**VM Instance:**
```bash
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --labels=environment=production,team=engineering,owner=john
```

**Update Labels:**
```bash
gcloud compute instances update my-vm \
  --zone=us-central1-a \
  --update-labels=cost-center=12345,version=v2
```

**Cloud Storage Bucket:**
```bash
gsutil label set labels.json gs://my-bucket

# labels.json:
{
  "environment": "production",
  "team": "data-engineering"
}
```

**Project Labels:**
```bash
gcloud projects update my-project-123 \
  --update-labels=environment=prod,cost-center=engineering
```

### Tags (Network Tags)

Network tags are used for firewall rules and routes. Different from labels!

**Add Network Tag to VM:**
```bash
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --tags=web-server,https-server

# Then use in firewall rule
gcloud compute firewall-rules create allow-https \
  --allow=tcp:443 \
  --target-tags=https-server
```

### Filter Resources by Labels

**List VMs with specific label:**
```bash
gcloud compute instances list \
  --filter="labels.environment=production"
```

**List projects by label:**
```bash
gcloud projects list \
  --filter="labels.team=engineering"
```

---

## Best Practices

### 1. Resource Hierarchy Design

**✅ Good Structure:**
```
Organization
├── Shared Services (networking, security)
├── Production (critical workloads)
├── Staging (pre-production testing)
└── Development (developer sandboxes)
```

**❌ Avoid:**
- Flat structure (all projects under organization)
- Too many nesting levels (hard to manage)

### 2. Project Organization

**Single Project per Environment:**
```
my-app-prod
my-app-staging
my-app-dev
```

**Benefits:**
- Clear separation
- Independent billing
- Different IAM policies
- Easy to delete dev/staging

### 3. Naming Conventions

**Projects:**
```
[team]-[app]-[environment]-[region]
Examples:
  eng-webapp-prod-us
  marketing-analytics-dev
```

**Folders:**
```
[Department/Team/Environment]
Examples:
  Production
  Engineering-Team-A
  Shared-Services
```

### 4. Use Labels Consistently

**Standard Label Set:**
```yaml
environment: prod | staging | dev
team: engineering | marketing | finance
cost-center: 12345
owner: john-doe
application: web-app
managed-by: terraform | manual
```

### 5. Organizational Policy Strategy

**Start Restrictive:**
- Set policies at organization level
- Relax for specific folders/projects as needed

**Example:**
```
Organization: Restrict to US regions only
  ↓
Production Folder: Enforce Shielded VMs
  ↓
Dev Folder: Allow all (more permissive)
```

### 6. Quota Management

- **Monitor** quota usage regularly
- **Request increases** proactively
- **Set up alerts** for quota thresholds
- **Use multiple projects** to distribute quotas

### 7. API Management

- Enable only **necessary APIs**
- Disable unused APIs to reduce attack surface
- Use **VPC Service Controls** for sensitive APIs

---

## ACE Exam Tips

### 1. Resource Hierarchy

**Key Concept:**
```
Organization → Folders → Projects → Resources
```

**Remember:**
- Policies **inherit** from parent to child
- Child **cannot remove** parent's permissions
- Child **can add** more permissions

### 2. Organizational Policies vs IAM

| Feature | Organizational Policies | IAM |
|---------|------------------------|-----|
| Purpose | **What** can be done | **Who** can do it |
| Example | "VMs must be in US" | "Alice can create VMs" |
| Scope | Restrict configurations | Grant permissions |

### 3. Project Identifiers

**Know the Difference:**
- **Project Name:** Display name (changeable)
- **Project ID:** Unique identifier (permanent)
- **Project Number:** Auto-assigned (used internally)

### 4. Common gcloud Commands

```bash
# List organizations
gcloud organizations list

# Create folder
gcloud resource-manager folders create --display-name=NAME --organization=ORG_ID

# Create project
gcloud projects create PROJECT_ID --folder=FOLDER_ID

# Set org policy
gcloud org-policies set-policy policy.yaml

# Enable API
gcloud services enable compute.googleapis.com

# View quotas
gcloud compute project-info describe

# Search assets
gcloud asset search-all-resources --scope=organizations/ORG_ID
```

### 5. Quotas

**Two Types:**
- **Rate Quotas:** API calls per minute/second
- **Allocation Quotas:** Resource limits (CPUs, IPs)

**Increase Method:** Console → IAM & Admin → Quotas

### 6. Labels vs Tags

- **Labels:** Metadata for organization/billing (key-value pairs)
- **Tags (Network):** Used for firewall rules and routes

### 7. API Enablement

**Remember:** Most APIs are **disabled by default**. Must enable before use.

Common error: "API not enabled" → Solution: `gcloud services enable [API]`

### 8. Cloud Asset Inventory

**Use Cases:**
- Audit resource changes
- Search for specific resources
- Track IAM policy changes
- Compliance reporting

### 9. Folder Depth Limit

Maximum folder nesting: **10 levels**

### 10. Exam Scenarios

**Scenario:** "Restrict all projects to only create resources in US regions"
**Solution:** Set organizational policy `constraints/gcp.resourceLocations` at organization level

**Scenario:** "Developer needs to create VMs but quota exceeded"
**Solution:** Request quota increase via IAM & Admin → Quotas

**Scenario:** "Track all changes to Cloud Storage buckets"
**Solution:** Use Cloud Asset Inventory with asset feed to Pub/Sub

---

## Quick Reference

### Key Commands Cheat Sheet

```bash
# Organizations
gcloud organizations list
gcloud organizations describe ORG_ID

# Folders
gcloud resource-manager folders create --display-name=NAME --organization=ORG_ID
gcloud resource-manager folders list --organization=ORG_ID
gcloud resource-manager folders describe FOLDER_ID

# Projects
gcloud projects create PROJECT_ID --folder=FOLDER_ID
gcloud projects list
gcloud projects describe PROJECT_ID
gcloud projects delete PROJECT_ID

# Organizational Policies
gcloud org-policies list --organization=ORG_ID
gcloud org-policies describe POLICY --organization=ORG_ID
gcloud org-policies set-policy policy.yaml

# APIs
gcloud services enable API_NAME
gcloud services list --enabled
gcloud services disable API_NAME

# Cloud Asset Inventory
gcloud asset search-all-resources --scope=organizations/ORG_ID
gcloud asset search-all-iam-policies --scope=projects/PROJECT_ID
gcloud asset export --project=PROJECT_ID --output-path=gs://bucket/file.json

# Labels
gcloud compute instances update VM --update-labels=key=value
gcloud projects update PROJECT_ID --update-labels=env=prod
```

---

**End of Guide** - You're now ready to manage Google Cloud resources like a pro! 🚀
