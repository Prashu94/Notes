# Resource hierarchy, IAM, and billing

ACE sections 1 and 5. PCA sections 1.1, 3.1, and 4.2. Read this before any product chapter.

## Hierarchy

```
Organization
  └── Folder (optional, nestable)
        └── Project
              └── Resources (VMs, buckets, datasets, …)
```

- The **organization** resource exists when the account is tied to Cloud Identity or Google Workspace. It is the root of IAM and organization policy.
- **Folders** group projects by department, environment, or application. They are how you apply policy once and have it inherit.
- A **project** is the trust, billing, and API boundary. Resources live in a project. A project has a name, a globally unique project ID, and an immutable project number.
- **Resources** are the actual products. Some are global (VPC network), some regional (subnet, Cloud Run service), some zonal (a VM, a zonal disk).

IAM allow policies inherit downward. A role granted at the organization applies to folders, projects, and resources under it unless a lower policy is written in a way that does not include that binding. There is no implicit deny in IAM. Access is the union of bindings from the resource up to the organization. Deny policies (IAM deny) are the exception: a deny overrides an allow.

Organization policies constrain *what configuration is legal* (no external IPs, allowed locations, uniform bucket-level access). They are not IAM. A user can have Owner and still be blocked by an organization policy.

### Commands

```bash
# Who am I, and which project is active
gcloud auth list
gcloud config list
gcloud projects describe "$PROJECT_ID"

# Organization and folders
gcloud organizations list
gcloud resource-manager folders list --organization="$ORG_ID"
gcloud resource-manager folders create --display-name="prod" --organization="$ORG_ID"

# Project under a folder
gcloud projects create "$PROJECT_ID" --folder="$FOLDER_ID" --name="App prod"
gcloud projects list --filter="parent.id=$FOLDER_ID"

# Move a project
gcloud beta projects move "$PROJECT_ID" --folder="$FOLDER_ID"

# Enable an API (ACE 1.1). Do this before you create the product.
gcloud services enable compute.googleapis.com \
  container.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  bigquery.googleapis.com \
  pubsub.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudkms.googleapis.com \
  secretmanager.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com

gcloud services list --enabled
```

Cloud Identity users and groups are administered in the Admin console or via the Admin SDK, not by creating Google accounts inside a project. Exam preference: **grant roles to Google Groups**, then add people to groups. You do not edit fifty IAM bindings when someone changes team.

Automated user lifecycle is directory sync or SCIM from an identity provider into Cloud Identity, plus group membership. Manual is the Admin console.

## IAM

A binding is principal + role + optional condition, attached to a resource.

Principals:

| Principal | Identifier | Use |
| --- | --- | --- |
| Google account | `user:ada@example.com` | A person |
| Group | `group:app-admins@example.com` | Preferred |
| Domain | `domain:example.com` | Broad. Rarely least privilege |
| Service account | `serviceAccount:name@PROJECT_ID.iam.gserviceaccount.com` | Workload identity |
| Workforce / workload identity pool | federated principal | Human SSO or external workloads without keys |
| `allUsers` | anyone on the internet | Public. Dangerous |
| `allAuthenticatedUsers` | any signed-in Google account | Still very broad |

Roles:

| Kind | Examples | Exam stance |
| --- | --- | --- |
| Basic | Owner, Editor, Viewer | Avoid. Editor can change almost everything. Owner can change IAM and billing link. |
| Predefined | `roles/compute.instanceAdmin.v1`, `roles/storage.objectViewer` | Default answer |
| Custom | A role you define from permissions | When no predefined role is tight enough |

Custom roles are created in a project or an organization. They support launch stage and permissions you list. They do not include some permissions that are not custom-role eligible. You cannot grant a custom role a permission the API refuses.

Conditions restrict a binding (time of day, resource name prefix, request attribute). They do not replace organization policy.

```bash
# See the policy
gcloud projects get-iam-policy "$PROJECT_ID"

# Grant a predefined role to a group
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="group:sre@example.com" \
  --role="roles/monitoring.viewer"

# Remove it
gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
  --member="group:sre@example.com" \
  --role="roles/monitoring.viewer"

# Custom role in the project
gcloud iam roles create appDeployer --project="$PROJECT_ID" \
  --title="App deployer" \
  --permissions=run.services.update,run.services.get,artifactregistry.repositories.download \
  --stage=GA

gcloud iam roles describe appDeployer --project="$PROJECT_ID"
gcloud iam roles update appDeployer --project="$PROJECT_ID" --add-permissions=run.services.list
```

Separation of duties (PCA): the person who changes IAM is not the person who uses the powerful role. The person who administers KMS is not the person who reads the data the key protects. Implement that with different groups and different roles, not with a shared Owner.

## Service accounts

A service account is both a principal and a resource.

- **Who the workload runs as:** attach the service account to the VM, Cloud Run service, GKE workload, or function.
- **Who may use that identity:** IAM on the service account resource. Important roles:
  - `roles/iam.serviceAccountUser` — attach it to a resource, or act as it for some APIs.
  - `roles/iam.serviceAccountTokenCreator` — mint short-lived tokens (impersonation).
  - `roles/iam.serviceAccountKeyAdmin` — create keys. Do not grant this broadly.

Google-managed service accounts exist for the platform (`PROJECT_NUMBER-compute@developer.gserviceaccount.com` and product agents). Do not use the default Compute Engine service account with the broad Editor role. Create a dedicated account per workload.

User-managed keys (JSON files) are long-lived secrets. The exam wants **impersonation** or **Workload Identity Federation** or **attached service accounts**. Short-lived credentials come from `gcloud auth print-access-token` after impersonation, or from the metadata server inside the workload.

```bash
gcloud iam service-accounts create app-runner \
  --display-name="App runner"

SA_EMAIL="app-runner@${PROJECT_ID}.iam.gserviceaccount.com"

# Minimum permission the app needs, on the project or on the resource
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectViewer"

# Allow a human to impersonate it (short-lived). They do not get a key file.
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --member="user:ada@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"

gcloud auth print-access-token --impersonate-service-account="$SA_EMAIL"

# Attach to a VM at create time
gcloud compute instances create app-vm \
  --zone="$ZONE" \
  --service-account="$SA_EMAIL" \
  --scopes=https://www.googleapis.com/auth/cloud-platform

# List keys. The goal in production is an empty list of user-managed keys.
gcloud iam service-accounts keys list --iam-account="$SA_EMAIL"
```

Scopes on a VM are a second gate. `cloud-platform` plus IAM is the current pattern. A narrow scope can deny a call even when IAM allows it. The exam still mentions scopes as legacy. Prefer IAM.

OS Login (ACE 3.1) ties SSH to IAM (`roles/compute.osLogin` or `roles/compute.osAdminLogin`) instead of metadata SSH keys. Enable it on the project or the instance.

```bash
gcloud compute project-info add-metadata \
  --metadata enable-oslogin=TRUE
```

## Organization policy and related controls

```bash
gcloud resource-manager org-policies list --project="$PROJECT_ID"
gcloud resource-manager org-policies describe constraints/compute.vmExternalIpAccess \
  --project="$PROJECT_ID"
```

Constraints you should recognize:

| Constraint idea | What the stem is doing |
| --- | --- |
| `compute.vmExternalIpAccess` | Block public IPs on VMs |
| `compute.skipDefaultNetworkCreation` | No default VPC on new projects |
| `iam.allowedPolicyMemberDomains` | Only identities from your domains |
| `gcp.resourceLocations` | Data residency / allowed regions |
| `storage.uniformBucketLevelAccess` | Force uniform bucket IAM |
| `sql.restrictPublicIp` | No public IP on Cloud SQL |

Hierarchical firewall policies (PCA) sit above VPC firewall rules and can be attached at org or folder. Use them when a security team must enforce a deny that project admins cannot remove.

VPC Service Controls are perimeters around projects and APIs so data cannot be copied out to a personal project. They are not a replacement for IAM. You need both.

## Billing

A **billing account** pays for projects. A project has at most one open billing link. A billing account can pay for many projects. Cloud Billing IAM (`roles/billing.admin`, `roles/billing.user`, `roles/billing.viewer`) is separate from project IAM. Linking a project requires permission on both the project and the billing account.

```bash
gcloud billing accounts list
gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"
gcloud billing projects describe "$PROJECT_ID"

# Budgets are created in the console or via the Cloud Billing Budget API.
# An alert at 50/90/100 percent notifies. It does not disable billing.
```

Billing export:

- **BigQuery export** (standard usage, and the detailed export) is how you analyze cost by label, service, and SKU. This is the exam’s default “analyze spend” answer.
- **Pricing export** and **file export** exist. Do not pick them when the stem says SQL analysis.
- Labels on resources are what make the export useful. Agree a label schema (`env`, `app`, `owner`) before the bill is large.

Budgets can be connected to Pub/Sub. A function can then shut a project down. That automation is extra. The budget resource itself only notifies.

Quotas are not billing. A quota caps how many of a resource you may create in a project and region. Exceeding quota fails the API call. Request an increase in Quotas before a launch, not during the outage.

```bash
gcloud compute project-info describe --format="yaml(quotas)"
gcloud compute regions describe "$REGION" --format="yaml(quotas)"
```

Committed use discounts and sustained use discounts are cost answers, covered in the pricing chapter. They are not budgets.

## Audit logs

Cloud Audit Logs have four streams you must separate:

| Log | What it records | Default |
| --- | --- | --- |
| Admin Activity | Control-plane changes (`setIamPolicy`, create instance) | Always on, cannot disable |
| Data Access | Reads and writes of user data (`storage.objects.get`) | Off except BigQuery. You enable them. They can be large. |
| System Event | Google-driven system actions | Always on |
| Policy Denied | Requests denied by policy | Useful when debugging VPC Service Controls and IAM deny |

```bash
gcloud logging read \
  'logName:"clou_audit" AND protoPayload.methodName="SetIamPolicy"' \
  --project="$PROJECT_ID" --limit=20 --freshness=1d
```

Long-term retention is a log sink to BigQuery, Cloud Storage, or Pub/Sub. Log buckets have their own retention. Default `_Default` and `_Required` buckets are not an archive strategy for a seven-year regulation.

## Exercises

Write the answer, then check.

1. A new engineer needs to restart Compute Engine instances in one project and nothing else. Which role, granted to what principal?
2. A script in CI must deploy Cloud Run. The security team forbids JSON keys. What do you configure?
3. Finance wants a warning at 80% of monthly spend and a weekly cost breakdown by team. Which two products?
4. Developers keep creating VMs with public IPs. IAM changes did not stop it because they are Project Editors. What actually stops it?
5. An auditor asks for a record of who changed IAM last quarter, stored for three years. What log, and where do you send it?

### Answers

1. `roles/compute.instanceAdmin.v1` (or a narrower custom role) on a **group**, bound to that project. Not Editor.
2. A dedicated service account with only the deploy roles, and Workload Identity Federation from GitHub or GitLab (or impersonation from Cloud Build’s service account). No key file.
3. A Cloud Billing **budget** with an alert, and **BigQuery billing export** queried by label. The budget does not stop spend.
4. Organization policy `constraints/compute.vmExternalIpAccess` at folder or org. Optionally a hierarchical firewall is the wrong tool for “cannot create a public IP”; that is an org policy.
5. Admin Activity audit logs, exported with a sink to a locked Cloud Storage bucket or BigQuery dataset in a separate audit project, retention set to at least three years. Admin Activity is already on.
