# Google Cloud IAM - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Principals (Members)](#principals-members)
4. [Roles](#roles)
5. [Permissions](#permissions)
6. [Policy Management](#policy-management)
7. [Service Accounts](#service-accounts)
8. [Best Practices](#best-practices)
9. [Common IAM Tasks](#common-iam-tasks)
10. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

Identity and Access Management (IAM) is Google Cloud's unified system for managing who (identity) has what access (role) to which resources. IAM enables you to grant granular access to specific Google Cloud resources and prevents unwanted access to other resources.

**Key Characteristics:**
- **Fine-grained Access Control:** Grant specific permissions to resources
- **Resource Hierarchy:** Policies inherited from parent to child
- **Centralized Management:** Manage access across all GCP services
- **Audit Logging:** Track all IAM changes

---

## Core Concepts

### IAM Model: WHO + WHAT + WHICH

**WHO (Principal):** Identity requesting access
- Google Account (user@gmail.com)
- Service Account (sa@project.iam.gserviceaccount.com)
- Google Group (group@googlegroups.com)
- Cloud Identity domain

**WHAT (Role):** Collection of permissions
- Predefined roles (managed by Google)
- Custom roles (created by you)
- Basic roles (Owner, Editor, Viewer - legacy)

**WHICH (Resource):** GCP resource being accessed
- Organization
- Folder
- Project
- Service-specific resources (VM, bucket, etc.)

### Resource Hierarchy

```
Organization (example.com)
├── Folder (Production)
│   ├── Project (web-app-prod)
│   │   ├── Compute Engine VMs
│   │   └── Cloud Storage Buckets
│   └── Project (api-backend-prod)
└── Folder (Development)
    └── Project (dev-sandbox)
```

**Policy Inheritance:**
- Policies set at higher levels are inherited by descendants
- Child policies cannot remove access granted at parent level
- Effective policy = Union of all policies from resource to organization

---

## Principals (Members)

### Google Account
Individual user with a Google Account:
```
user:alice@example.com
```

**Use Case:** Employees, contractors with individual access needs

### Service Account
Identity for applications/VMs:
```
serviceAccount:my-sa@my-project.iam.gserviceaccount.com
```

**Use Case:** Applications, VMs, automated processes

### Google Group
Collection of Google Accounts and service accounts:
```
group:developers@example.com
```

**Use Case:** Manage permissions for teams
**Benefits:** Add/remove users without changing IAM policies

### Google Workspace/Cloud Identity Domain
All users in a domain:
```
domain:example.com
```

**Use Case:** Organization-wide policies

### AllUsers & AllAuthenticatedUsers
Special identifiers:
```
allUsers  # Anyone on the internet (public)
allAuthenticatedUsers  # Anyone with a Google Account
```

**Use Case:** Public websites, open datasets

---

## Roles

### Basic Roles (Primitive Roles)
**Legacy roles - avoid in production!**

| Role | Permissions | Use Case |
|------|------------|----------|
| **Owner** | Full control, billing, IAM management | Project administrators (use sparingly) |
| **Editor** | Modify resources, no IAM/billing | Developers (testing only) |
| **Viewer** | Read-only access | Read-only users (testing only) |

**Why Avoid?**
- Too broad (violates least privilege)
- Hard to audit
- Difficult to track who has what access

### Predefined Roles
**Curated collections of permissions for specific jobs**

**Examples by Service:**

**Compute Engine:**
- `roles/compute.admin` - Full control of Compute Engine
- `roles/compute.instanceAdmin.v1` - Manage instances
- `roles/compute.networkAdmin` - Manage networking
- `roles/compute.viewer` - Read-only access

**Cloud Storage:**
- `roles/storage.admin` - Full control of buckets/objects
- `roles/storage.objectAdmin` - Manage objects
- `roles/storage.objectCreator` - Create objects
- `roles/storage.objectViewer` - View objects

**IAM:**
- `roles/iam.serviceAccountAdmin` - Manage service accounts
- `roles/iam.serviceAccountUser` - Use service accounts
- `roles/iam.roleAdmin` - Manage custom roles
- `roles/iam.securityReviewer` - View IAM policies

**Project:**
- `roles/resourcemanager.projectCreator` - Create projects
- `roles/resourcemanager.projectDeleter` - Delete projects
- `roles/resourcemanager.projectIamAdmin` - Manage project IAM

### Custom Roles
**Create roles with specific permissions**

**When to Use:**
- Need more granular control than predefined roles
- Want to follow principle of least privilege
- Have specific job functions not covered by predefined roles

**Create Custom Role:**
```bash
gcloud iam roles create myCustomRole \
  --project=my-project \
  --title="My Custom Role" \
  --description="Custom role for specific task" \
  --permissions=compute.instances.list,compute.instances.get,compute.instances.start,compute.instances.stop \
  --stage=GA
```

**From YAML:**
```yaml
title: "My Custom Role"
description: "Custom role for instance management"
stage: "GA"
includedPermissions:
- compute.instances.list
- compute.instances.get
- compute.instances.start
- compute.instances.stop
```

```bash
gcloud iam roles create myCustomRole --project=my-project --file=role.yaml
```

**List Custom Roles:**
```bash
gcloud iam roles list --project=my-project
```

**Update Custom Role:**
```bash
gcloud iam roles update myCustomRole \
  --project=my-project \
  --add-permissions=compute.instances.reset
```

**Delete Custom Role:**
```bash
gcloud iam roles delete myCustomRole --project=my-project
```

---

## Permissions

### Permission Format
```
service.resource.verb
```

**Examples:**
- `compute.instances.create` - Create Compute Engine instances
- `storage.buckets.delete` - Delete Cloud Storage buckets
- `iam.serviceAccounts.actAs` - Act as a service account

### Viewing Permissions

**List permissions in a role:**
```bash
gcloud iam roles describe roles/compute.instanceAdmin.v1
```

**Test permissions:**
```bash
gcloud projects get-iam-policy my-project \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:alice@example.com"
```

---

## Policy Management

### IAM Policy Structure

```json
{
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": [
        "user:alice@example.com",
        "group:developers@example.com",
        "serviceAccount:my-sa@project.iam.gserviceaccount.com"
      ]
    },
    {
      "role": "roles/compute.admin",
      "members": [
        "user:bob@example.com"
      ],
      "condition": {
        "title": "Expires in 2025",
        "expression": "request.time < timestamp('2025-12-31T23:59:59Z')"
      }
    }
  ],
  "etag": "BwXd8...",
  "version": 3
}
```

### Grant IAM Role

**Project Level:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:alice@example.com \
  --role=roles/storage.admin
```

**Service Account:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:my-sa@my-project.iam.gserviceaccount.com \
  --role=roles/compute.instanceAdmin.v1
```

**Group:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=group:developers@example.com \
  --role=roles/container.developer
```

### Remove IAM Role

```bash
gcloud projects remove-iam-policy-binding my-project \
  --member=user:alice@example.com \
  --role=roles/storage.admin
```

### View IAM Policy

**Project:**
```bash
gcloud projects get-iam-policy my-project
```

**Specific Resource (Bucket):**
```bash
gsutil iam get gs://my-bucket
```

**Specific Resource (Instance):**
```bash
gcloud compute instances get-iam-policy instance-name --zone=us-central1-a
```

### IAM Conditions

**Grant role with expiration:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:temp-contractor@example.com \
  --role=roles/viewer \
  --condition='expression=request.time < timestamp("2025-12-31T23:59:59Z"),title=Temporary Access'
```

**Grant role for specific resource:**
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:alice@example.com \
  --role=roles/compute.instanceAdmin.v1 \
  --condition='expression=resource.name.startsWith("projects/my-project/zones/us-central1-a/instances/dev-"),title=Dev Instances Only'
```

---

## Service Accounts

### What is a Service Account?

A service account is a special type of account used by applications, VMs, or services (not people) to interact with Google Cloud APIs.

**Format:**
```
<account-id>@<project-id>.iam.gserviceaccount.com
```

### Types of Service Accounts

**User-Managed:**
- Created by you
- You control lifecycle
- Example: `my-app@my-project.iam.gserviceaccount.com`

**Default Service Accounts:**
- Automatically created by GCP
- Examples:
  - Compute Engine: `<project-number>-compute@developer.gserviceaccount.com`
  - App Engine: `<project-id>@appspot.gserviceaccount.com`

### Create Service Account

```bash
gcloud iam service-accounts create my-service-account \
  --display-name="My Service Account" \
  --description="Service account for my application"
```

### Grant Roles to Service Account

```bash
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:my-service-account@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer
```

### List Service Accounts

```bash
gcloud iam service-accounts list
```

### Delete Service Account

```bash
gcloud iam service-accounts delete my-service-account@my-project.iam.gserviceaccount.com
```

### Service Account Keys

**Create Key (JSON):**
```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=my-service-account@my-project.iam.gserviceaccount.com
```

**List Keys:**
```bash
gcloud iam service-accounts keys list \
  --iam-account=my-service-account@my-project.iam.gserviceaccount.com
```

**Delete Key:**
```bash
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=my-service-account@my-project.iam.gserviceaccount.com
```

### Impersonation

**Allow user to act as service account:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
  my-service-account@my-project.iam.gserviceaccount.com \
  --member=user:alice@example.com \
  --role=roles/iam.serviceAccountUser
```

**Use service account in gcloud:**
```bash
gcloud compute instances create my-vm \
  --service-account=my-service-account@my-project.iam.gserviceaccount.com \
  --scopes=cloud-platform
```

---

## Best Practices

### 1. Principle of Least Privilege
Grant minimum permissions needed to perform a task.

**Bad:**
```bash
# Granting Owner role for a developer
gcloud projects add-iam-policy-binding my-project \
  --member=user:dev@example.com \
  --role=roles/owner
```

**Good:**
```bash
# Grant specific role for instance management
gcloud projects add-iam-policy-binding my-project \
  --member=user:dev@example.com \
  --role=roles/compute.instanceAdmin.v1
```

### 2. Use Groups for User Management

**Bad:** Grant roles to individual users
```bash
gcloud projects add-iam-policy-binding my-project --member=user:alice@example.com --role=roles/viewer
gcloud projects add-iam-policy-binding my-project --member=user:bob@example.com --role=roles/viewer
gcloud projects add-iam-policy-binding my-project --member=user:charlie@example.com --role=roles/viewer
```

**Good:** Grant role to group
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=group:viewers@example.com \
  --role=roles/viewer
```

### 3. Avoid Basic Roles in Production
Use predefined or custom roles instead.

### 4. Regularly Audit IAM Policies

```bash
# Get current IAM policy
gcloud projects get-iam-policy my-project > policy.json

# Review who has Owner/Editor roles
gcloud projects get-iam-policy my-project \
  --flatten="bindings[].members" \
  --filter="bindings.role:(roles/owner OR roles/editor)"
```

### 5. Rotate Service Account Keys

```bash
# List keys older than 90 days
gcloud iam service-accounts keys list \
  --iam-account=my-sa@my-project.iam.gserviceaccount.com \
  --filter="validAfterTime<-P90D"
```

### 6. Use Service Account Impersonation
Instead of downloading keys, use impersonation.

---

## Common IAM Tasks

### Grant Developer Access

```bash
# Grant necessary roles for development
gcloud projects add-iam-policy-binding my-project \
  --member=user:developer@example.com \
  --role=roles/compute.instanceAdmin.v1

gcloud projects add-iam-policy-binding my-project \
  --member=user:developer@example.com \
  --role=roles/storage.admin
```

### Grant Read-Only Access

```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:auditor@example.com \
  --role=roles/viewer
```

### Create Service Account for Application

```bash
# Create service account
gcloud iam service-accounts create app-backend \
  --display-name="Backend Application"

# Grant permissions
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:app-backend@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer

# Use in Compute Engine
gcloud compute instances create my-vm \
  --service-account=app-backend@my-project.iam.gserviceaccount.com \
  --scopes=cloud-platform
```

### Temporary Access

```bash
# Grant access for 30 days
gcloud projects add-iam-policy-binding my-project \
  --member=user:contractor@example.com \
  --role=roles/viewer \
  --condition='expression=request.time < timestamp("2025-01-31T23:59:59Z"),title=Contractor Access Expires Jan 31'
```

---

## ACE Exam Tips

### 1. IAM Hierarchy
Remember: **Organization > Folder > Project > Resources**
- Policies inherit from parent to child
- Child cannot restrict what parent grants

### 2. Role Types
- **Basic Roles:** Owner, Editor, Viewer (avoid in production)
- **Predefined Roles:** Service-specific (e.g., `roles/compute.admin`)
- **Custom Roles:** Your own combinations of permissions

### 3. Service Accounts
- **Default:** Automatically created (Compute Engine, App Engine)
- **User-Managed:** You create and manage
- **Keys:** Avoid downloading; use impersonation instead

### 4. Common Commands
```bash
# Grant role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=MEMBER --role=ROLE

# Remove role
gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member=MEMBER --role=ROLE

# View policy
gcloud projects get-iam-policy PROJECT_ID

# Create service account
gcloud iam service-accounts create SA_NAME
```

### 5. Principle of Least Privilege
Always grant minimum permissions required. Use predefined roles when possible.

### 6. Policy Binding Components
- **Member:** Who (user, serviceAccount, group, domain)
- **Role:** What permissions (roles/...)
- **Resource:** Where (project, bucket, instance)

### 7. Service Account Use Cases
- **VM Identity:** VMs access GCP APIs
- **Application Identity:** Apps running outside GCP
- **CI/CD:** Automated deployments

### 8. Groups
Use Google Groups to simplify management. Add/remove users from group instead of changing IAM policies.

### 9. IAM Conditions
Can add conditions to role bindings:
- Time-based (expiration)
- Resource-based (specific resources)
- Request-based (IP address, device)

### 10. Audit Logging
Cloud Audit Logs automatically track IAM changes:
- Admin Activity: Role grants/revokes
- Data Access: Reading IAM policies (must enable)
