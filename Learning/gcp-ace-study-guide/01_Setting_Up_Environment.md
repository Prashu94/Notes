# 01. Setting Up a Cloud Solution Environment (Masterclass Edition)

This domain covers approximately **23% of the ACE Exam**. It focuses on the foundation upon which all other services are built.

---

## 1.1 The Advanced Resource Hierarchy

The Google Cloud resource hierarchy provides a way to logically organize resources and manage access and configuration at scale.

### 1.1.1 Hierarchy Structure

```
┌─────────────────────────────────────────────────────────────┐
│                       ORGANIZATION                          │
│                    (company.com)                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        v                     v                     v
  ┌──────────┐          ┌──────────┐          ┌──────────┐
  │ FOLDER   │          │ FOLDER   │          │ FOLDER   │
  │(Finance) │          │(Eng)     │          │(Marketing)│
  └──────────┘          └──────────┘          └──────────┘
        │                     │
        │            ┌────────┼────────┐
        v            v        v        v
  ┌──────────┐  ┌────────┐ ┌────────┐ ┌────────┐
  │ PROJECT  │  │FOLDER  │ │FOLDER  │ │PROJECT │
  │(fin-prod)│  │(Prod)  │ │(Dev)   │ │(shared)│
  └──────────┘  └────────┘ └────────┘ └────────┘
                    │          │
                    v          v
               ┌────────┐ ┌────────┐
               │PROJECT │ │PROJECT │
               │(app-p) │ │(app-d) │
               └────────┘ └────────┘
```

### 1.1.2 The Organization Node

| Aspect | Details |
|--------|---------|
| **Creation** | Auto-created with Google Workspace or Cloud Identity |
| **Scope** | Root node, represents entire company |
| **Key Roles** | Organization Admin, Organization Policy Admin |
| **Purpose** | Central visibility, policy enforcement |

```bash
# List organization
gcloud organizations list

# Get organization ID
gcloud organizations describe ORGANIZATION_ID

# List folders in organization
gcloud resource-manager folders list --organization=ORGANIZATION_ID
```

### 1.1.3 Folders: Grouping and Isolation

| Feature | Details |
|---------|---------|
| **Nesting** | Up to 10 levels deep |
| **Inheritance** | IAM and Org Policies inherit down |
| **Use Cases** | Environment, department, compliance isolation |

```bash
# Create folder
gcloud resource-manager folders create \
    --display-name="Production" \
    --organization=ORGANIZATION_ID

# Create nested folder
gcloud resource-manager folders create \
    --display-name="Web Apps" \
    --folder=PARENT_FOLDER_ID

# Move project to folder
gcloud projects move PROJECT_ID --folder=FOLDER_ID
```

### 1.1.4 Projects: The Application Container

| Identifier | Uniqueness | Mutable | Example |
|------------|------------|---------|---------|
| **Project ID** | Global | ❌ No | `my-app-prod-99` |
| **Project Name** | Non-unique | ✅ Yes | "Production Web App" |
| **Project Number** | Global | ❌ No | `123456789` |

```bash
# Create project
gcloud projects create my-new-project \
    --name="My New Project" \
    --folder=FOLDER_ID

# Set default project
gcloud config set project my-new-project

# List all projects
gcloud projects list

# Delete project (30-day grace period)
gcloud projects delete PROJECT_ID

# Undelete project (within 30 days)
gcloud projects undelete PROJECT_ID
```

### 1.1.5 Organization Policy Service (Deep Dive)

| Constraint Type | Description | Example |
|-----------------|-------------|---------|
| **List** | Allow/deny specific values | Allowed regions |
| **Boolean** | Enable/disable features | Disable serial port |

```bash
# List available constraints
gcloud org-policies list-constraints --organization=ORGANIZATION_ID

# Set organization policy (boolean)
gcloud resource-manager org-policies set-policy policy.yaml \
    --organization=ORGANIZATION_ID

# policy.yaml for disabling VM serial port access
# constraint: constraints/compute.disableSerialPortAccess
# booleanPolicy:
#   enforced: true

# Set list constraint for allowed regions
cat > region-policy.yaml << EOF
constraint: constraints/gcp.resourceLocations
listPolicy:
  allowedValues:
    - in:us-locations
    - in:eu-locations
EOF

gcloud resource-manager org-policies set-policy region-policy.yaml \
    --project=my-project
```

#### Common Organization Policy Constraints

| Constraint | Purpose |
|------------|---------|
| `compute.vmExternalIpAccess` | Control external IPs on VMs |
| `compute.restrictSharedVpcSubnetworks` | Limit shared VPC usage |
| `iam.allowedPolicyMemberDomains` | Restrict IAM to specific domains |
| `compute.trustedImageProjects` | Limit VM image sources |
| `storage.uniformBucketLevelAccess` | Enforce uniform bucket access |
| `sql.restrictPublicIp` | Prevent public Cloud SQL |

---

## 1.2 Managing Billing and Costs

### 1.2.1 Billing Account Types

| Type | Payment | Use Case |
|------|---------|----------|
| **Self-serve** | Credit card, bank account | Most organizations |
| **Invoiced** | Monthly invoice | Large enterprises |

### 1.2.2 Billing IAM Roles

| Role | Permissions |
|------|-------------|
| `billing.creator` | Create new billing accounts |
| `billing.admin` | Full control (payment, linking) |
| `billing.user` | Link projects to billing account |
| `billing.viewer` | View spend only |
| `billing.projectManager` | Link/unlink projects for specific account |

```bash
# List billing accounts
gcloud billing accounts list

# Link project to billing account
gcloud billing projects link PROJECT_ID \
    --billing-account=BILLING_ACCOUNT_ID

# Check project billing info
gcloud billing projects describe PROJECT_ID
```

### 1.2.3 Budgets and Alerts

| Budget Type | Description |
|-------------|-------------|
| **Specified Amount** | Fixed dollar amount |
| **Last Month's Spend** | Dynamic based on previous month |

| Alert Threshold | Trigger |
|-----------------|---------|
| **Actual** | When actual spend reaches % |
| **Forecasted** | When forecasted spend reaches % |

```bash
# Create budget via gcloud
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="Monthly Budget" \
    --budget-amount=1000USD \
    --threshold-rules=threshold-percent=0.5,spend-basis=current-spend \
    --threshold-rules=threshold-percent=0.9,spend-basis=current-spend \
    --threshold-rules=threshold-percent=1.0,spend-basis=forecasted-spend \
    --notifications-rule-pubsub-topic=projects/my-project/topics/budget-alerts
```

### 1.2.4 Programmatic Budget Response

```python
# Cloud Function to disable billing when budget exceeded
import google.cloud.billing.v1 as billing
import base64
import json

def budget_alert_handler(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    message = json.loads(pubsub_message)
    
    cost_amount = message['costAmount']
    budget_amount = message['budgetAmount']
    
    if cost_amount > budget_amount:
        # Disable billing
        billing_client = billing.CloudBillingClient()
        billing_client.update_project_billing_info(
            name=f"projects/{message['budgetDisplayName']}",
            project_billing_info={"billing_account_name": ""}
        )
```

### 1.2.5 Billing Export to BigQuery

| Export Type | Content | Latency |
|-------------|---------|---------|
| **Standard** | Per-service costs | ~24 hours |
| **Detailed** | Resource-level costs + labels | ~24 hours |
| **Pricing** | Public pricing data | Daily |

```bash
# Enable detailed billing export
gcloud billing accounts export-billing-data \
    --billing-account=BILLING_ACCOUNT_ID \
    --dataset=billing_export \
    --table-prefix=gcp_billing \
    --export-type=standard

# Query billing data in BigQuery
bq query --use_legacy_sql=false '
SELECT
  service.description AS service,
  SUM(cost) AS total_cost,
  SUM(credits.amount) AS total_credits
FROM `project.billing_export.gcp_billing_export_v1_XXXXXX`
WHERE DATE(_PARTITIONTIME) = CURRENT_DATE()
GROUP BY service.description
ORDER BY total_cost DESC
'
```

### 1.2.6 Labels for Cost Allocation

```bash
# Add labels to resources
gcloud compute instances update my-vm \
    --zone=us-central1-a \
    --update-labels=env=prod,team=backend,cost-center=12345

# Query costs by label in BigQuery
bq query --use_legacy_sql=false '
SELECT
  labels.value AS team,
  SUM(cost) AS team_cost
FROM `project.billing_export.gcp_billing_export_v1_XXXXXX`,
  UNNEST(labels) AS labels
WHERE labels.key = "team"
GROUP BY team
ORDER BY team_cost DESC
'
```

---

## 1.3 The Google Cloud CLI (gcloud) - Professional Usage

### 1.3.1 Configuration Management

Manage multiple environments/projects with configurations.

```bash
# Create new configuration
gcloud config configurations create work-prod
gcloud config set account admin@company.com
gcloud config set project company-prod
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a

# Create another configuration
gcloud config configurations create work-dev
gcloud config set account admin@company.com
gcloud config set project company-dev

# Switch configurations
gcloud config configurations activate work-prod

# List configurations
gcloud config configurations list

# View current configuration
gcloud config list

# Override configuration for single command
gcloud compute instances list --project=other-project
```

### 1.3.2 Common gcloud Commands

```bash
# Authentication
gcloud auth login                          # User account
gcloud auth application-default login      # Application default credentials
gcloud auth activate-service-account \     # Service account
    --key-file=key.json

# Project management
gcloud projects list
gcloud projects create PROJECT_ID
gcloud config set project PROJECT_ID

# Compute
gcloud compute instances list
gcloud compute instances create my-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium

# Storage
gcloud storage buckets create gs://my-bucket
gcloud storage cp file.txt gs://my-bucket/

# IAM
gcloud projects get-iam-policy PROJECT_ID
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="user:email@example.com" \
    --role="roles/viewer"
```

### 1.3.3 Output Formatting

```bash
# Different output formats
gcloud compute instances list --format=json
gcloud compute instances list --format=yaml
gcloud compute instances list --format="table(name,zone,status)"
gcloud compute instances list --format="value(name)"
gcloud compute instances list --format="csv(name,zone)"

# Filter results
gcloud compute instances list --filter="zone:us-central1-a"
gcloud compute instances list --filter="status=RUNNING"
gcloud compute instances list --filter="name~'^web-'"

# Combine filter and format
gcloud compute instances list \
    --filter="zone:us-central1-* AND status=RUNNING" \
    --format="table(name,networkInterfaces[0].accessConfigs[0].natIP)"
```

### 1.3.4 Component Management

```bash
# List installed components
gcloud components list

# Install additional components
gcloud components install kubectl
gcloud components install docker-credential-gcr
gcloud components install beta

# Update all components
gcloud components update

# Use beta/alpha commands
gcloud beta compute instances list
gcloud alpha services list
```
*   `gcloud components install [ID]`: Add new tools.

### 1.3.3 Output Formatting (The CLI Power User)
For automation, raw text is bad.
*   `--format=json`: Output as JSON for scripts like `jq`.
*   `--format="table(name, zone, status)"`: Custom table columns.
*   `--filter="status=RUNNING"`: Server-side filtering (much faster than client-side `grep`).
*   **The "Execution" example**:
    ```bash
    # Stop all VMs in a specific zone that are currently running
    gcloud compute instances stop \
        $(gcloud compute instances list --filter="zone:us-central1-a AND status:RUNNING" --format="value(name)")
    ```

### 1.3.4 Cloud Shell: The "Ephemeral Admin Desk"
*   **What is it?**: A Debian-based VM with 5GB persistent `$HOME`.
*   **What's inside?**: All gcloud tools, Python, Java, Go, Docker, Terraform, and a built-in code editor (Theia).
*   **Safe Mode**: If configurations mess up, launch with `?cloudshell_safemode=true`.
*   **Ephemeral Nature**: The VM is deleted after 20 mins of inactivity. Only data in `$HOME` is saved.

---

## 1.4 Setting Up Cloud Identity
For the exam, know that Google Cloud needs an identity provider.
*   **Cloud Identity Free/Premium**: Allows managing users/groups if you don't use Google Workspace.
*   **External Sync**: Using **Google Cloud Directory Sync (GCDS)** to sync users from On-Premises Active Directory to Google Cloud Identity.
*   **Authentication**: Users log in with corporate credentials via **SSO (SAML 2.0)**.
