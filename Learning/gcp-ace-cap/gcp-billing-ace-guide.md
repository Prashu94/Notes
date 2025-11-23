# Google Cloud Billing - Associate Cloud Engineer (ACE) Guide

## Table of Contents
1. [Overview](#overview)
2. [Billing Account Types](#billing-account-types)
3. [Billing Account Setup](#billing-account-setup)
4. [Linking Projects to Billing](#linking-projects-to-billing)
5. [Budgets and Alerts](#budgets-and-alerts)
6. [Cost Management](#cost-management)
7. [Billing Export](#billing-export)
8. [Cost Optimization Strategies](#cost-optimization-strategies)
9. [Billing Reports](#billing-reports)
10. [Committed Use Discounts](#committed-use-discounts)
11. [Best Practices](#best-practices)
12. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

Google Cloud Billing manages how you pay for Google Cloud services. Understanding billing is essential for cost control and is approximately **23%** of the ACE exam (part of "Setting up a cloud solution environment").

**Key Concepts:**
- **Billing Account:** Defines who pays for resources
- **Payments Profile:** Stores payment methods
- **Projects:** Must be linked to billing account to use paid services
- **Budgets:** Set spending limits and alerts
- **Exports:** Export detailed billing data for analysis

---

## Billing Account Types

### 1. Self-Serve (Online) Billing Account

**Characteristics:**
- Automatic payments via credit card or bank account
- Pay-as-you-go pricing
- Suitable for most users and small-to-medium businesses

**Creation:**
- Created through Google Cloud Console
- Requires valid payment method

### 2. Invoiced (Offline) Billing Account

**Characteristics:**
- Monthly or quarterly invoicing
- Payment via check or wire transfer
- Requires credit approval from Google
- Suitable for large enterprises

**Requirements:**
- Must meet eligibility criteria
- Contact Google Cloud sales

### 3. Free Trial Billing Account

**Characteristics:**
- $300 credit for 90 days
- No automatic charge after trial ends
- Limited to one per user/organization

**Restrictions:**
- Cannot have more than 8 cores running simultaneously
- Cannot add GPUs
- Cannot upgrade to paid account without manual action

---

## Billing Account Setup

### Create Billing Account

**Via Console:**
1. Go to **Billing** → **Account Management**
2. Click **Create Account**
3. Choose billing country
4. Fill in business/individual information
5. Add payment method
6. Accept terms and conditions

**Via gcloud (View Only):**
```bash
# List billing accounts
gcloud billing accounts list

# Get account details
gcloud billing accounts describe BILLING_ACCOUNT_ID
```

**Note:** Cannot create billing accounts via gcloud, must use Console or API.

### Billing Account Roles

**Key IAM Roles:**

| Role | Permissions | Use Case |
|------|-------------|----------|
| `roles/billing.admin` | Full billing control | Finance team leads |
| `roles/billing.user` | Link/unlink projects | Project managers |
| `roles/billing.viewer` | View billing data | Finance analysts, auditors |
| `roles/billing.creator` | Create new billing accounts | IT administrators |
| `roles/billing.costsManager` | Manage budgets and exports | Cost optimization team |

**Grant Billing Roles:**
```bash
# Grant billing admin
gcloud billing accounts add-iam-policy-binding BILLING_ACCOUNT_ID \
  --member=user:finance@example.com \
  --role=roles/billing.admin

# Grant billing user (can link projects)
gcloud billing accounts add-iam-policy-binding BILLING_ACCOUNT_ID \
  --member=user:pm@example.com \
  --role=roles/billing.user

# Grant billing viewer
gcloud billing accounts add-iam-policy-binding BILLING_ACCOUNT_ID \
  --member=user:analyst@example.com \
  --role=roles/billing.viewer
```

**View Billing IAM Policy:**
```bash
gcloud billing accounts get-iam-policy BILLING_ACCOUNT_ID
```

---

## Linking Projects to Billing

### Why Link Projects?

**Without Billing Account:**
- Can only use free-tier services
- Cannot create billable resources (VMs, databases, etc.)
- Project remains in "trial" mode

**With Billing Account:**
- Full access to all GCP services
- Pay for resource usage
- Can set budgets and alerts

### Link Project to Billing

**Via Console:**
1. Go to **Billing** → **Account Management**
2. Click on billing account
3. Go to **Linked Projects** tab
4. Click **Link Project**
5. Select project from dropdown
6. Click **Set Account**

**Via gcloud:**
```bash
# Link project to billing account
gcloud billing projects link my-project-123 \
  --billing-account=BILLING_ACCOUNT_ID

# Verify linkage
gcloud billing projects describe my-project-123
```

**Example Output:**
```yaml
billingAccountName: billingAccounts/01ABC2-34DEF5-67GHI8
billingEnabled: true
name: projects/my-project-123/billingInfo
projectId: my-project-123
```

### Unlink Project from Billing

**Warning:** This disables all billable services in the project!

```bash
# Unlink project
gcloud billing projects unlink my-project-123
```

**Effect:**
- All running VMs will **stop**
- Databases will become **inaccessible**
- Data is **retained** for 30 days
- Can re-link to restore access

### Check Project Billing Status

**Via gcloud:**
```bash
# Get billing info for project
gcloud billing projects describe my-project-123

# List all projects linked to billing account
gcloud billing projects list \
  --billing-account=BILLING_ACCOUNT_ID
```

---

## Budgets and Alerts

### What are Budgets?

Budgets help you track spending and get notified when costs approach or exceed limits. They do **NOT** stop billing automatically.

**Budget Components:**
- **Budget Amount:** Target spending limit (monthly, quarterly, or custom)
- **Threshold Rules:** Percentage triggers (e.g., 50%, 90%, 100%)
- **Notifications:** Email alerts to stakeholders
- **Optional:** Pub/Sub notifications for automation

### Create Budget

**Via Console:**
1. Go to **Billing** → **Budgets & alerts**
2. Click **Create Budget**
3. **Scope:** Select projects or products
4. **Amount:** Set budget amount
5. **Thresholds:** Set alert percentages
6. **Notifications:** Add email recipients
7. Click **Finish**

**Via gcloud:**
```bash
# Create budget
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Monthly Budget - Production" \
  --budget-amount=5000 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

**Create Budget for Specific Projects:**
```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Project Budget" \
  --budget-amount=1000 \
  --filter-projects=projects/my-project-123 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100 \
  --all-updates-rule-monitoring-notification-channels=projects/my-project-123/notificationChannels/CHANNEL_ID
```

### Budget Threshold Rules

**Common Thresholds:**
- **50%:** Early warning, time to review
- **80%:** Action needed, optimize costs
- **100%:** Budget exceeded, immediate review
- **110%:** Overspending, critical alert

**Forecast-based Alerts:**
Alert when **forecasted** spend will exceed budget
```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Forecast Budget" \
  --budget-amount=5000 \
  --threshold-rule=percent=100,basis=FORECASTED_SPEND
```

### Budget Notifications

**Email Notifications:**
- Sent to billing admins by default
- Can add additional recipients

**Pub/Sub Notifications (for automation):**
```bash
# Create Pub/Sub topic first
gcloud pubsub topics create budget-alerts

# Create budget with Pub/Sub notification
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Automated Budget" \
  --budget-amount=5000 \
  --threshold-rule=percent=100 \
  --all-updates-rule-pubsub-topic=projects/my-project/topics/budget-alerts
```

**Use Case:** Trigger Cloud Function to:
- Send Slack notifications
- Shut down non-production resources
- Create incident tickets

### Manage Budgets

**List Budgets:**
```bash
gcloud billing budgets list \
  --billing-account=BILLING_ACCOUNT_ID
```

**View Budget Details:**
```bash
gcloud billing budgets describe BUDGET_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

**Update Budget:**
```bash
gcloud billing budgets update BUDGET_ID \
  --billing-account=BILLING_ACCOUNT_ID \
  --budget-amount=8000
```

**Delete Budget:**
```bash
gcloud billing budgets delete BUDGET_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

---

## Cost Management

### Understanding Your Bill

**Cost Components:**
```
Total Cost = 
  Compute Costs +
  Storage Costs +
  Network Egress +
  API Requests +
  Licensing +
  Support
```

### Cost Breakdown by Service

**Common Cost Drivers:**

**1. Compute (Usually Highest):**
- Compute Engine VMs
- GKE clusters
- Cloud Run
- App Engine

**2. Storage:**
- Cloud Storage
- Persistent Disks
- Cloud SQL storage

**3. Networking:**
- Internet egress (most expensive)
- Cross-region traffic
- Load Balancer usage

**4. Data Processing:**
- BigQuery queries
- Dataflow jobs
- Dataproc clusters

### View Costs

**Via Console:**
1. **Billing** → **Reports**
2. Filter by:
   - Time range
   - Projects
   - Services
   - SKUs (Stock Keeping Units)
   - Labels

**Via gcloud (limited):**
```bash
# View billing account
gcloud billing accounts describe BILLING_ACCOUNT_ID
```

**Note:** Most cost analysis done via Console or BigQuery exports

### Cost Allocation with Labels

**Use Labels for Cost Tracking:**
```bash
# Label VMs for cost allocation
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --labels=cost-center=engineering,project=web-app,environment=prod

# Label projects
gcloud projects update my-project-123 \
  --update-labels=team=data,cost-center=analytics
```

**Benefits:**
- Track costs by team/department
- Identify expensive projects
- Allocate costs to business units

---

## Billing Export

### What is Billing Export?

Billing export automatically sends detailed billing data to:
- **BigQuery:** For SQL analysis
- **Cloud Storage:** For file-based analysis (CSV/JSON)

**Benefits:**
- Granular cost analysis
- Custom reporting
- Historical trends
- Programmatic access

### Export to BigQuery

**Why BigQuery?**
- Query costs with SQL
- Join with other data (labels, metadata)
- Create custom dashboards
- Analyze trends over time

**Setup BigQuery Export:**

**Via Console:**
1. Go to **Billing** → **Billing Export**
2. Select **BigQuery Export** tab
3. Click **Edit Settings**
4. Choose:
   - **Standard usage cost:** Daily aggregated costs
   - **Detailed usage cost:** Every SKU (more granular)
   - **Pricing:** Pricing information
5. Select project and dataset
6. Click **Save**

**Via gcloud:**
```bash
# Enable BigQuery export (requires API call, not direct gcloud command)
# Must use Console or Terraform
```

**Dataset Structure:**
```
my-project-123
└── billing_dataset
    ├── gcp_billing_export_v1_BILLING_ACCOUNT_ID (Daily usage)
    └── gcp_billing_export_resource_v1_BILLING_ACCOUNT_ID (Detailed)
```

### Query Billing Data in BigQuery

**Total Cost by Project:**
```sql
SELECT
  project.id AS project_id,
  SUM(cost) AS total_cost
FROM `my-project.billing_dataset.gcp_billing_export_v1_*`
WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
GROUP BY project_id
ORDER BY total_cost DESC;
```

**Cost by Service:**
```sql
SELECT
  service.description AS service,
  SUM(cost) AS total_cost
FROM `my-project.billing_dataset.gcp_billing_export_v1_*`
WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
GROUP BY service
ORDER BY total_cost DESC;
```

**Cost by Label:**
```sql
SELECT
  label.value AS team,
  SUM(cost) AS total_cost
FROM `my-project.billing_dataset.gcp_billing_export_v1_*`,
  UNNEST(labels) AS label
WHERE label.key = 'team'
  AND _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
GROUP BY team
ORDER BY total_cost DESC;
```

**Daily Cost Trend:**
```sql
SELECT
  DATE(usage_start_time) AS date,
  SUM(cost) AS daily_cost
FROM `my-project.billing_dataset.gcp_billing_export_v1_*`
WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20240131'
GROUP BY date
ORDER BY date;
```

### Export to Cloud Storage

**Setup Cloud Storage Export:**

**Via Console:**
1. **Billing** → **Billing Export**
2. Select **File Export** tab
3. Choose format (CSV or JSON)
4. Select bucket: `gs://my-billing-bucket`
5. Click **Save**

**File Structure:**
```
gs://my-billing-bucket/
├── BILLING_ACCOUNT_ID_2024-01-01.csv
├── BILLING_ACCOUNT_ID_2024-01-02.csv
└── BILLING_ACCOUNT_ID_2024-01-03.csv
```

**Use Cases:**
- Import into Excel/Google Sheets
- Custom ETL pipelines
- Offline analysis

---

## Cost Optimization Strategies

### 1. Right-Sizing Resources

**Problem:** Over-provisioned VMs waste money

**Solution:**
```bash
# Use Cloud Monitoring recommendations
# Console: Compute Engine → VM instances → View recommendations

# Switch to smaller machine type
gcloud compute instances set-machine-type my-vm \
  --zone=us-central1-a \
  --machine-type=n1-standard-2
```

### 2. Use Preemptible/Spot VMs

**Savings:** Up to 80% off

**Create Spot VM:**
```bash
gcloud compute instances create my-spot-vm \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --provisioning-model=SPOT \
  --instance-termination-action=DELETE
```

**Use Cases:**
- Batch processing
- CI/CD workers
- Fault-tolerant applications

### 3. Committed Use Discounts (CUDs)

**Savings:** 25-52% off

**Types:**
- 1-year commitment: ~25% discount
- 3-year commitment: ~52% discount

**Create Commitment:**
```bash
gcloud compute commitments create my-commitment \
  --region=us-central1 \
  --plan=twelve-month \
  --resources=VCPU=16,memory=64GB
```

### 4. Sustained Use Discounts (Automatic)

**Automatic Discounts:**
- No commitment needed
- Up to 30% off for VMs running >25% of month
- Applied automatically

**Example:**
- Run VM for entire month → ~30% discount
- Run VM for 50% of month → ~15% discount

### 5. Stop Unused Resources

**Stop VMs (not delete):**
```bash
# Stop VM (keeps disk, stops compute charges)
gcloud compute instances stop my-vm --zone=us-central1-a

# Start later
gcloud compute instances start my-vm --zone=us-central1-a
```

**Schedule VM start/stop:**
Use Cloud Scheduler + Cloud Functions to auto-stop dev VMs at night

### 6. Cloud Storage Lifecycle Management

**Automatically move to cheaper storage classes:**
```bash
# Create lifecycle policy
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
EOF

# Apply to bucket
gsutil lifecycle set lifecycle.json gs://my-bucket
```

**Cost Difference:**
- Standard: $0.020/GB/month
- Nearline: $0.010/GB/month (>30 days)
- Coldline: $0.004/GB/month (>90 days)
- Archive: $0.0012/GB/month (>365 days)

### 7. Optimize Network Costs

**Expensive:**
- Internet egress: $0.12/GB
- Cross-region: $0.01-0.02/GB

**Strategies:**
- Use Cloud CDN (cheaper than egress)
- Keep resources in same region
- Use Cloud Storage for static content

### 8. Delete Unused Resources

**Common Waste:**
- Orphaned persistent disks
- Unused static IPs
- Old snapshots
- Unused load balancers

**Find Orphaned Disks:**
```bash
# List unattached disks
gcloud compute disks list --filter="-users:*"

# Delete orphaned disk
gcloud compute disks delete DISK_NAME --zone=ZONE
```

**Find Unused IPs:**
```bash
# List unused static IPs
gcloud compute addresses list --filter="status:RESERVED"

# Delete unused IP
gcloud compute addresses delete IP_NAME --region=REGION
```

---

## Billing Reports

### Cost Reports

**Access Reports:**
1. **Billing** → **Reports**
2. View costs by:
   - Time period
   - Project
   - Service
   - SKU
   - Region
   - Label

**Key Metrics:**
- Total spend
- Trend (vs previous period)
- Top projects/services
- Forecast

### Cost Table Report

**Detailed Breakdown:**
1. **Billing** → **Cost Table**
2. Group by: Project, Service, SKU, etc.
3. Export to CSV for offline analysis

### Pricing Calculator

**Estimate Costs Before Deploying:**
1. Go to [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator)
2. Add services
3. Configure specifications
4. Get monthly estimate

---

## Committed Use Discounts

### What are CUDs?

Committed Use Discounts provide significant savings in exchange for a 1-year or 3-year commitment.

**Types:**

**1. Compute Engine CUD:**
- Commit to vCPU and memory
- Regional or zonal
- Savings: 25-52%

**2. Cloud SQL CUD:**
- Commit to vCPU and memory
- Savings: 25-52%

### Purchase CUD

**Via Console:**
1. **Compute Engine** → **Committed Use Discounts**
2. Click **Purchase Commitment**
3. Choose:
   - Region
   - Term (1 or 3 years)
   - Resources (vCPUs, memory)
4. Review savings estimate
5. Click **Purchase**

**Via gcloud:**
```bash
gcloud compute commitments create my-commitment \
  --region=us-central1 \
  --plan=twelve-month \
  --resources=VCPU=32,memory=128GB
```

**View Commitments:**
```bash
gcloud compute commitments list
```

### CUD Best Practices

**1. Analyze Usage First:**
- Review 30-day usage patterns
- Identify consistent baseline

**2. Start Small:**
- Commit to baseline usage
- Add more as needed

**3. Use Recommendations:**
- Console shows recommended commitments
- Based on historical usage

---

## Best Practices

### 1. Billing Account Structure

**Single Billing Account:**
- Small organizations
- Simple cost tracking

**Multiple Billing Accounts:**
- Separate dev/prod billing
- Departmental chargebacks
- Different payment sources

### 2. Set Up Budgets Immediately

**Minimum Budgets:**
- Overall account budget
- Per-project budgets
- Environment-specific budgets (prod/dev)

### 3. Use Labels Religiously

**Standard Label Set:**
```yaml
cost-center: engineering | marketing | finance
environment: prod | staging | dev
team: team-a | team-b
project: project-name
owner: john-doe
```

### 4. Enable Billing Exports

**Export to BigQuery on Day 1:**
- Historical data for analysis
- Trend identification
- Custom reports

### 5. Regular Cost Reviews

**Weekly:**
- Check budget alerts
- Review anomalies

**Monthly:**
- Analyze trends
- Identify optimization opportunities
- Review commitments

### 6. Automate Cost Controls

**Use Pub/Sub + Cloud Functions:**
- Auto-stop dev VMs at night
- Alert on anomalies
- Enforce tagging policies

### 7. Least Privilege for Billing

**Restrict Access:**
- billing.admin: Finance only
- billing.user: Project managers
- billing.viewer: Everyone else

---

## ACE Exam Tips

### 1. Billing Account Roles

**Know the Difference:**

| Role | Can Link Projects? | Can View Costs? | Can Create Budgets? |
|------|-------------------|-----------------|---------------------|
| billing.admin | ✅ | ✅ | ✅ |
| billing.user | ✅ | ❌ | ❌ |
| billing.viewer | ❌ | ✅ | ❌ |
| billing.costsManager | ❌ | ✅ | ✅ |

### 2. Project Linking

**Key Concept:**
- Project MUST be linked to billing account to use paid services
- Unlinking project **stops** all billable services
- Data retained for 30 days after unlinking

### 3. Budgets Do NOT Stop Billing

**Important:** Budgets only send **alerts**, they don't prevent overspending.

To stop billing: Must unlink project or delete resources

### 4. Common Commands

```bash
# List billing accounts
gcloud billing accounts list

# Link project to billing
gcloud billing projects link PROJECT_ID --billing-account=ACCOUNT_ID

# Unlink project
gcloud billing projects unlink PROJECT_ID

# Create budget
gcloud billing budgets create --billing-account=ACCOUNT_ID --budget-amount=5000

# List budgets
gcloud billing budgets list --billing-account=ACCOUNT_ID
```

### 5. Budget Thresholds

**Standard Thresholds:**
- 50% - Early warning
- 90% - Action needed
- 100% - Budget exceeded

Can also use **forecasted spend** for proactive alerts

### 6. Billing Export Destinations

**Two Options:**
- **BigQuery:** SQL analysis, dashboards
- **Cloud Storage:** CSV/JSON files

Most common: BigQuery for analysis

### 7. Cost Optimization Strategies

**ACE Exam Favorites:**
- **Preemptible VMs:** Up to 80% savings
- **Committed Use Discounts:** 25-52% savings
- **Sustained Use Discounts:** Automatic, up to 30%
- **Right-sizing:** Use smaller VMs
- **Storage lifecycle:** Move to cheaper classes

### 8. Exam Scenarios

**Scenario:** "Finance team needs to view costs but not modify billing"
**Solution:** Grant `roles/billing.viewer`

**Scenario:** "Project manager needs to link new project to billing"
**Solution:** Grant `roles/billing.user`

**Scenario:** "Get notified when spending reaches 80% of budget"
**Solution:** Create budget with threshold rule at 80%

**Scenario:** "Export billing data for analysis in BigQuery"
**Solution:** Enable BigQuery billing export

**Scenario:** "Reduce costs for batch processing workloads"
**Solution:** Use Spot/Preemptible VMs

### 9. Free Tier vs Free Trial

**Free Tier:**
- Always-free limits
- E.g., 1 f1-micro VM per month in us-region
- No expiration

**Free Trial:**
- $300 credit
- 90 days
- One per user/org

### 10. Billing Alerts

**Alert Methods:**
- **Email:** Default, sent to billing admins
- **Pub/Sub:** For automation, trigger Cloud Functions
- **Monitoring:** Create custom dashboards

---

## Quick Reference

### Key Commands

```bash
# Billing Accounts
gcloud billing accounts list
gcloud billing accounts describe ACCOUNT_ID
gcloud billing accounts get-iam-policy ACCOUNT_ID
gcloud billing accounts add-iam-policy-binding ACCOUNT_ID --member=USER --role=ROLE

# Project Linking
gcloud billing projects link PROJECT_ID --billing-account=ACCOUNT_ID
gcloud billing projects unlink PROJECT_ID
gcloud billing projects describe PROJECT_ID
gcloud billing projects list --billing-account=ACCOUNT_ID

# Budgets
gcloud billing budgets create --billing-account=ACCOUNT_ID --budget-amount=AMOUNT
gcloud billing budgets list --billing-account=ACCOUNT_ID
gcloud billing budgets describe BUDGET_ID --billing-account=ACCOUNT_ID
gcloud billing budgets delete BUDGET_ID --billing-account=ACCOUNT_ID

# Committed Use Discounts
gcloud compute commitments create NAME --region=REGION --plan=PLAN --resources=RESOURCES
gcloud compute commitments list
```

---

**End of Guide** - Master billing to control costs and ace the exam! 💰
