# Google Cloud IAM - ACE Practice Questions

## Question 1
You need to grant a developer the ability to create and manage Compute Engine instances but not to create or manage networks. Which predefined role should you assign?

**A)** `roles/compute.admin`

**B)** `roles/compute.instanceAdmin.v1`

**C)** `roles/compute.networkAdmin`

**D)** `roles/editor`

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - `roles/compute.instanceAdmin.v1` grants full control over instances
  - Does NOT include network administration permissions
  - Follows principle of least privilege
  - Specific to instance management

Permissions included:
- Create, delete, start, stop instances
- Attach/detach disks
- Manage instance metadata
- Does NOT include: Create/modify VPC, subnets, firewall rules

Grant the role:
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:developer@example.com \
  --role=roles/compute.instanceAdmin.v1
```

- Option A is incorrect because:
  - `roles/compute.admin` includes FULL Compute Engine permissions
  - Includes network administration
  - Too broad for the requirement

- Option C is incorrect because:
  - `roles/compute.networkAdmin` is for network management only
  - Doesn't include instance management permissions

- Option D is incorrect because:
  - `roles/editor` is a basic role with permissions across ALL GCP services
  - Way too broad
  - Should be avoided in production

---

## Question 2
You have a service account that needs to be used by a Compute Engine instance to read objects from Cloud Storage. The service account should have no other permissions. What should you do?

**A)** Grant `roles/storage.admin` to the service account

**B)** Grant `roles/storage.objectViewer` to the service account at the project level

**C)** Grant `roles/storage.objectViewer` to the service account at the bucket level

**D)** Grant `roles/viewer` to the service account

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - `roles/storage.objectViewer` allows read-only access to objects
  - Granting at bucket level follows least privilege (only specific bucket access)
  - No unnecessary permissions granted
  - Most secure and precise approach

Implementation:
```bash
# Create service account
gcloud iam service-accounts create storage-reader \
  --display-name="Storage Reader"

# Grant role at bucket level
gsutil iam ch serviceAccount:storage-reader@PROJECT_ID.iam.gserviceaccount.com:roles/storage.objectViewer \
  gs://my-bucket

# Attach to instance
gcloud compute instances create my-vm \
  --service-account=storage-reader@PROJECT_ID.iam.gserviceaccount.com \
  --scopes=cloud-platform
```

- Option A is incorrect because:
  - `roles/storage.admin` grants full control (create, delete buckets and objects)
  - Too broad - violates least privilege
  - Includes write and admin permissions

- Option B is incorrect because:
  - While the role is correct, project-level is too broad
  - Grants access to ALL buckets in the project
  - Bucket-level is more precise

- Option D is incorrect because:
  - `roles/viewer` is a basic role with read access to ALL project resources
  - Too broad and not specific to storage
  - Basic roles should be avoided

**Best Practice:** Always grant roles at the most specific resource level possible.

---

## Question 3
A contractor needs temporary access to view (not modify) resources in your GCP project. The access should automatically expire after 30 days. What should you do?

**A)** Grant `roles/viewer` and manually remove it after 30 days

**B)** Create a custom role that expires after 30 days

**C)** Use IAM conditions to grant `roles/viewer` with a time-based expiration

**D)** Grant `roles/browser` for 30 days

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - IAM conditions allow time-based access control
  - Access automatically expires (no manual intervention)
  - Follows security best practices
  - Audit trail maintained

Implementation:
```bash
# Calculate expiration date (30 days from now)
EXPIRY_DATE=$(date -u -d "+30 days" +"%Y-%m-%dT%H:%M:%SZ")

# Grant role with expiration condition
gcloud projects add-iam-policy-binding my-project \
  --member=user:contractor@example.com \
  --role=roles/viewer \
  --condition="expression=request.time < timestamp('${EXPIRY_DATE}'),title=Expires in 30 days,description=Temporary contractor access"
```

Or using a specific date:
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:contractor@example.com \
  --role=roles/viewer \
  --condition='expression=request.time < timestamp("2025-12-31T23:59:59Z"),title=Contractor Access Expires Dec 31'
```

- Option A is incorrect because:
  - Requires manual revocation
  - Risk of forgetting to remove access
  - No automation
  - Prone to human error

- Option B is incorrect because:
  - Custom roles don't have expiration feature
  - Roles define permissions, not access duration
  - Conditions control when roles are effective

- Option D is incorrect because:
  - `roles/browser` allows browsing the resource hierarchy but limited viewing
  - Still requires manual removal
  - `roles/viewer` is the standard read-only role

**IAM Conditions** support:
- Time-based restrictions (before/after date)
- Resource-based restrictions (specific resources)
- Request-based restrictions (IP address, device)

---

## Question 4
You need to allow your application running on Google Kubernetes Engine to access Cloud SQL. The application should not use a service account key file. What is the recommended approach?

**A)** Download a service account key and mount it as a Kubernetes secret

**B)** Use Workload Identity to bind a Kubernetes service account to a GCP service account

**C)** Use the default Compute Engine service account

**D)** Embed credentials directly in the application code

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Workload Identity is the recommended way to access GCP services from GKE
  - No service account keys needed
  - Kubernetes pods use GCP service accounts securely
  - Follows Google's security best practices
  - Easy permission management through IAM

Implementation:
```bash
# Enable Workload Identity on cluster
gcloud container clusters update my-cluster \
  --workload-pool=PROJECT_ID.svc.id.goog

# Create GCP service account
gcloud iam service-accounts create cloudsql-accessor

# Grant Cloud SQL permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:cloudsql-accessor@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/cloudsql.client

# Create Kubernetes service account
kubectl create serviceaccount k8s-sa -n default

# Bind Kubernetes SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  cloudsql-accessor@PROJECT_ID.iam.gserviceaccount.com \
  --member=serviceAccount:PROJECT_ID.svc.id.goog[default/k8s-sa] \
  --role=roles/iam.workloadIdentityUser

# Annotate Kubernetes SA
kubectl annotate serviceaccount k8s-sa \
  iam.gke.io/gcp-service-account=cloudsql-accessor@PROJECT_ID.iam.gserviceaccount.com
```

- Option A is incorrect because:
  - Storing service account keys in Kubernetes secrets is a security risk
  - Keys can be compromised
  - Google recommends avoiding key files
  - Key rotation is manual

- Option C is incorrect because:
  - Default Compute Engine SA has broad permissions
  - Violates least privilege
  - Shared across multiple workloads
  - Hard to audit specific access

- Option D is incorrect because:
  - Embedding credentials in code is a severe security violation
  - Credentials can be exposed in version control
  - No way to rotate without code changes
  - Major security risk

**Workload Identity** eliminates the need for service account keys in GKE.

---

## Question 5
You need to create a custom IAM role that allows users to list and start Compute Engine instances but not stop or delete them. Which permissions should you include?

**A)** `compute.instances.*`

**B)** `compute.instances.list`, `compute.instances.get`, `compute.instances.start`, `compute.zones.list`

**C)** `compute.instances.list`, `compute.instances.start`

**D)** `compute.*`

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - `compute.instances.list` - Required to list instances
  - `compute.instances.get` - Required to view instance details
  - `compute.instances.start` - Required to start instances
  - `compute.zones.list` - Required to list zones (needed for console UI)
  - Includes all necessary permissions without extra privileges

Create the custom role:
```bash
gcloud iam roles create instanceStarter \
  --project=my-project \
  --title="Instance Starter" \
  --description="Can list and start instances only" \
  --permissions=compute.instances.list,compute.instances.get,compute.instances.start,compute.zones.list \
  --stage=GA
```

Or using YAML:
```yaml
title: "Instance Starter"
description: "Can list and start instances"
stage: "GA"
includedPermissions:
- compute.instances.list
- compute.instances.get
- compute.instances.start
- compute.zones.list
```

```bash
gcloud iam roles create instanceStarter --project=my-project --file=role.yaml
```

Grant the role:
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:operator@example.com \
  --role=projects/my-project/roles/instanceStarter
```

- Option A is incorrect because:
  - `compute.instances.*` includes ALL instance permissions
  - Includes stop, delete, create, etc.
  - Too broad for the requirement

- Option C is incorrect because:
  - Missing `compute.instances.get` (needed to view details)
  - Missing `compute.zones.list` (needed for listing instances by zone)
  - UI may not work properly

- Option D is incorrect because:
  - `compute.*` includes ALL Compute Engine permissions
  - Way too broad
  - Includes network, disk, and all other permissions

**Testing Permissions:**
```bash
# Test if user has permission
gcloud projects get-iam-policy my-project \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:operator@example.com"
```

---

## Question 6
Your team uses Google Groups for access management. A new engineer joined and needs the same Cloud Storage access as the rest of the team. What should you do?

**A)** Grant the engineer the same IAM role as individual team members

**B)** Add the engineer to the Google Group that has the Cloud Storage permissions

**C)** Create a new service account for the engineer

**D)** Share a service account key with the engineer

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Google Groups simplify permission management
  - One-time role grant to group, add/remove users as needed
  - No IAM policy changes required when team changes
  - Follows best practices for team access management
  - Easier to audit (group membership vs individual permissions)

Implementation:
```bash
# Initial setup (done once)
gcloud projects add-iam-policy-binding my-project \
  --member=group:storage-team@example.com \
  --role=roles/storage.objectAdmin

# Add new engineer to group (in Google Groups admin or workspace)
# No IAM policy changes needed!
```

Benefits:
1. Centralized access control
2. Easy onboarding/offboarding
3. Consistent permissions across team
4. Reduced IAM policy complexity

- Option A is incorrect because:
  - Creates individual policy bindings
  - Harder to manage as team grows
  - Duplicates permission configuration
  - More complex to audit

- Option C is incorrect because:
  - Service accounts are for applications, not users
  - Engineers should use their user accounts
  - Violates identity management best practices

- Option D is incorrect because:
  - Sharing service account keys is a security violation
  - Service accounts are not for individual users
  - No individual audit trail

**Best Practice:** Always use Google Groups for team access management.

---

## Question 7
You need to grant a service account the ability to impersonate (act as) another service account. Which role should you grant?

**A)** `roles/iam.serviceAccountUser`

**B)** `roles/iam.serviceAccountAdmin`

**C)** `roles/iam.serviceAccountKeyAdmin`

**D)** `roles/iam.serviceAccountTokenCreator`

**Correct Answer:** D

**Explanation:**
- Option D is correct because:
  - `roles/iam.serviceAccountTokenCreator` allows creating short-lived credentials for a service account
  - Enables service account impersonation
  - Can generate access tokens as the target service account
  - Used for workload identity federation and service account chaining

Implementation:
```bash
# Grant permission to impersonate target-sa
gcloud iam service-accounts add-iam-policy-binding \
  target-sa@project-id.iam.gserviceaccount.com \
  --member=serviceAccount:source-sa@project-id.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountTokenCreator

# Now source-sa can impersonate target-sa
gcloud auth print-access-token \
  --impersonate-service-account=target-sa@project-id.iam.gserviceaccount.com
```

Alternative using user impersonation:
```bash
# Allow user to impersonate service account
gcloud iam service-accounts add-iam-policy-binding \
  my-sa@project-id.iam.gserviceaccount.com \
  --member=user:admin@example.com \
  --role=roles/iam.serviceAccountTokenCreator
```

- Option A is incorrect because:
  - `roles/iam.serviceAccountUser` is for using a service account with resources (e.g., attaching to a VM)
  - Does NOT allow impersonation or token creation
  - Different use case

- Option B is incorrect because:
  - `roles/iam.serviceAccountAdmin` is for managing service accounts (create, delete, update)
  - Does NOT grant impersonation rights
  - Administrative permissions only

- Option C is incorrect because:
  - `roles/iam.serviceAccountKeyAdmin` is for managing service account keys
  - Does NOT allow impersonation
  - Key management only

**Key Differences:**
- `serviceAccountUser`: Use SA with resources (VMs, Cloud Run, etc.)
- `serviceAccountTokenCreator`: Impersonate SA, create tokens
- `serviceAccountAdmin`: Manage SA lifecycle
- `serviceAccountKeyAdmin`: Manage SA keys

---

## Question 8
Your organization policy requires that all GCP resources must be created under specific folders. How can you enforce that users cannot create projects at the organization level?

**A)** Remove the `resourcemanager.projects.create` permission from users at the organization level

**B)** Use an organization policy constraint to restrict project creation to specific folders

**C)** Create a custom IAM role without project creation permissions

**D)** Document the requirement and train users

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Organization policies provide centralized governance
  - Can enforce project creation locations
  - Cannot be bypassed by users
  - Applies to all users regardless of IAM permissions

Implementation:
```yaml
# Create organization policy to restrict project creation
# policy.yaml
name: organizations/ORGANIZATION_ID/policies/resourcemanager.projects.create
spec:
  rules:
    - values:
        deniedValues:
          - "organizations/ORGANIZATION_ID"
        allowedValues:
          - "folders/FOLDER_ID_1"
          - "folders/FOLDER_ID_2"
```

Apply policy:
```bash
gcloud resource-manager org-policies set-policy policy.yaml
```

Alternative using constraints:
```bash
# Deny project creation at org level
gcloud resource-manager org-policies deny \
  resourcemanager.projects.create \
  --organization=ORGANIZATION_ID

# Allow at specific folder
gcloud resource-manager org-policies allow \
  resourcemanager.projects.create \
  --folder=FOLDER_ID
```

- Option A is incorrect because:
  - This would prevent project creation entirely
  - Doesn't allow creation in specific folders
  - IAM permissions alone can't enforce location constraints

- Option C is incorrect because:
  - Custom roles control what users can do, not where
  - Doesn't enforce folder restrictions
  - Users with proper permissions could still create projects anywhere

- Option D is incorrect because:
  - No technical enforcement
  - Relies on user compliance
  - Not scalable or reliable

**Organization Policies** enforce allowed/denied values and parent resource constraints.

---

## Question 9
You need to view all the roles that have been granted to a specific user across all projects in your organization. What should you do?

**A)** Run `gcloud projects get-iam-policy` for each project and filter for the user

**B)** Use Cloud Asset Inventory to search for IAM policy bindings for the user

**C)** Check the user's profile in Cloud Console

**D)** Contact Google Support

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Cloud Asset Inventory maintains a searchable inventory of all GCP resources and IAM policies
  - Can query across all projects in the organization
  - Efficient single query instead of iterating through projects
  - Provides historical data

Implementation:
```bash
# Query all IAM policies for a specific user
gcloud asset search-all-iam-policies \
  --scope=organizations/ORGANIZATION_ID \
  --query="policy:user:alice@example.com"

# More specific - show only bindings
gcloud asset search-all-iam-policies \
  --scope=organizations/ORGANIZATION_ID \
  --query="policy:user:alice@example.com" \
  --format="table(resource, policy.bindings.role)"
```

Example output:
```
RESOURCE                    ROLE
projects/project-a          roles/editor
projects/project-b          roles/storage.admin
folders/123456              roles/viewer
```

Alternative using `gcloud asset analyze-iam-policy`:
```bash
gcloud asset analyze-iam-policy \
  --organization=ORGANIZATION_ID \
  --identity=user:alice@example.com \
  --full-resource-name
```

- Option A is incorrect because:
  - Requires iterating through all projects
  - Inefficient and time-consuming
  - Doesn't check folder or organization-level permissions
  - Manual and error-prone

- Option C is incorrect because:
  - Cloud Console user profile doesn't show comprehensive role assignments
  - Limited visibility across all projects
  - Doesn't provide organization-wide view

- Option D is incorrect because:
  - This is something you can do yourself with Cloud Asset Inventory
  - No need to contact support
  - Support would use the same tools

**Cloud Asset Inventory** is the recommended tool for IAM policy auditing and analysis.

---

## Question 10
A team needs access to production resources only from the office network (IP range: 203.0.113.0/24). How can you enforce this?

**A)** Use VPC firewall rules to restrict access

**B)** Use IAM conditions with IP address restrictions

**C)** Configure Cloud Armor security policies

**D)** Use VPN to connect to GCP

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - IAM conditions support IP address-based restrictions
  - Enforces access control at the IAM level
  - Works for all GCP services (not just network traffic)
  - Centralized policy management

Implementation:
```bash
# Grant role only from specific IP range
gcloud projects add-iam-policy-binding my-project \
  --member=user:developer@example.com \
  --role=roles/editor \
  --condition='expression=origin.ip=="203.0.113.0/24",title=Office IP only,description=Access only from office network'

# Multiple IP ranges
gcloud projects add-iam-policy-binding my-project \
  --member=group:prod-team@example.com \
  --role=roles/editor \
  --condition='expression=origin.ip=="203.0.113.0/24" || origin.ip=="198.51.100.0/24",title=Office and VPN access'
```

IAM Condition with multiple criteria:
```bash
# Office IP + business hours only
gcloud projects add-iam-policy-binding my-project \
  --member=user:contractor@example.com \
  --role=roles/viewer \
  --condition='expression=origin.ip=="203.0.113.0/24" && request.time.getHours("America/New_York") >= 9 && request.time.getHours("America/New_York") < 17,title=Office hours and IP'
```

- Option A is incorrect because:
  - VPC firewall rules control network traffic, not IAM permissions
  - Doesn't restrict API access via gcloud, Console, or SDKs
  - Only affects network connectivity
  - Complementary but not sufficient

- Option C is incorrect because:
  - Cloud Armor is for DDoS protection and WAF rules for load balancers
  - Doesn't control IAM permissions
  - Different use case (protecting web applications)

- Option D is incorrect because:
  - VPN enables connectivity but doesn't enforce access control
  - Additional infrastructure
  - Doesn't prevent access from other IPs if credentials are compromised

**IAM Conditions** for origin.ip:
- Support CIDR notation
- Can combine with other conditions (time, resource, request attributes)
- Evaluated for every API request

---

## Question 11
You need to audit all changes made to IAM policies in your project over the last 90 days. What should you use?

**A)** Cloud Monitoring metrics

**B)** Cloud Audit Logs

**C)** Cloud Asset Inventory

**D)** Access Transparency logs

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Cloud Audit Logs automatically record all IAM policy changes
  - Admin Activity logs capture policy modifications
  - Retained for 400 days by default
  - Provides who, what, when, and from where

Query IAM changes:
```bash
# View IAM policy changes in last 90 days
gcloud logging read \
  'protoPayload.methodName="SetIamPolicy" AND
   timestamp>="2024-01-01T00:00:00Z"' \
  --limit=100 \
  --format=json
```

In Cloud Console:
1. Navigate to **Logging > Logs Explorer**
2. Query:
```
protoPayload.methodName="SetIamPolicy"
OR protoPayload.methodName="SetIamPolicyRequest"
timestamp >= "2024-01-01T00:00:00Z"
```

Common IAM audit log entries:
- `SetIamPolicy` - Policy changes
- `google.iam.admin.v1.CreateServiceAccount` - Service account creation
- `google.iam.admin.v1.DeleteServiceAccount` - Service account deletion
- `google.iam.admin.v1.CreateServiceAccountKey` - Key creation

Export for analysis:
```bash
# Export IAM changes to Cloud Storage
gcloud logging sinks create iam-audit-sink \
  storage.googleapis.com/my-audit-bucket \
  --log-filter='protoPayload.methodName:"SetIamPolicy"'
```

- Option A is incorrect because:
  - Cloud Monitoring tracks metrics (CPU, memory, etc.)
  - Doesn't record audit events or policy changes
  - Wrong tool for the job

- Option C is incorrect because:
  - Cloud Asset Inventory shows current state and history of resources
  - Useful for "what" but not detailed "who/when/where"
  - Audit Logs provide more detailed change tracking

- Option D is incorrect because:
  - Access Transparency logs show Google employee access to your data
  - Not for user-initiated IAM changes
  - Different purpose (third-party access auditing)

**Types of Cloud Audit Logs:**
1. **Admin Activity** - Resource modifications (free, always enabled, 400-day retention)
2. **Data Access** - Data reads/writes (must enable, charges apply)
3. **System Event** - Google system events (free)
4. **Policy Denied** - Permission denied events (must enable)

---

## Question 12
You need to grant a user temporary access to assume administrative privileges only when required. How can you implement this with minimal operational overhead?

**A)** Grant the admin role permanently but trust the user to use it responsibly

**B)** Use IAM conditions to grant admin role only during business hours

**C)** Implement a custom workflow with Cloud Functions to temporarily grant/revoke roles

**D)** Use just-in-time (JIT) access with Privileged Access Manager

**Correct Answer:** D

**Explanation:**
- Option D is correct because:
  - Privileged Access Manager (PAM) provides just-in-time privileged access
  - Users request access, admin approves, auto-expires
  - Built-in workflow and approval process
  - Audit trail of all privileged access
  - Minimal operational overhead (managed service)

Note: If PAM is not available in your exam context, Option C would be the alternative approach.

Implementation concept:
```bash
# Create entitled access grant (PAM)
gcloud pam entitlements create admin-access \
  --location=global \
  --project=my-project \
  --max-request-duration=2h \
  --approval-workflow=manual \
  --privileged-access="roles/owner"

# User requests access (for 1 hour)
gcloud pam grants create \
  --entitlement=admin-access \
  --requested-duration=1h \
  --justification="Emergency production issue"
```

- Option A is incorrect because:
  - Standing privileged access is a security risk
  - Violates principle of least privilege
  - No time-bound access
  - Not in line with security best practices

- Option B is incorrect because:
  - Business hours restriction doesn't help if emergency access is needed outside hours
  - Still provides standing access during business hours
  - Not true "only when required"

- Option C is incorrect because:
  - Requires custom development and maintenance
  - Operational overhead for building/maintaining the workflow
  - Manual approval process needs to be implemented
  - PAM is the managed solution for this

**Zero Standing Privileges (ZSP)** is the security model where users have no permanent elevated access.

---

## Question 13
Which of the following statements about IAM roles is TRUE?

**A)** Custom roles can be created at the project, folder, or organization level

**B)** Basic roles (Owner, Editor, Viewer) are the recommended way to grant access in production

**C)** Predefined roles cannot be modified

**D)** Service accounts can only be granted service account roles, not other roles

**Correct Answer:** Both A and C

Expected exam answer: **C**

**Explanation:**
- Option C is correct because:
  - Predefined roles are managed by Google
  - Cannot be modified by users
  - Google updates them as new features are added
  - Read-only from user perspective

- Option A is also correct:
  - Custom roles can be created at project level
  - Can be created at organization level (usable by all projects)
  - Cannot be created at folder level in all regions/configurations

However, since the question asks for THE true statement (singular), let's clarify:

- Option B is incorrect because:
  - Basic roles are too broad
  - Should use predefined or custom roles in production
  - Basic roles are legacy and discouraged

- Option D is incorrect because:
  - Service accounts can be granted any role
  - Same roles as users can have
  - No restriction to specific "service account roles"

**Custom Role Creation:**
```bash
# Project-level custom role
gcloud iam roles create myCustomRole --project=my-project --file=role.yaml

# Organization-level custom role (usable across all projects)
gcloud iam roles create myCustomRole --organization=ORG_ID --file=role.yaml
```

**Best answer for exam: C** (Predefined roles cannot be modified)

---

## Question 14
You need to grant a third-party auditor read-only access review your security configuration but not view any data. Which role should you assign?

**A)** `roles/viewer`

**B)** `roles/iam.securityReviewer`

**C)** `roles/iam.roleViewer`

**D)** `roles/security.reviewer`

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - `roles/iam.securityReviewer` provides read access to all IAM policies and security-related configurations
  - Can view roles, permissions, policies, service accounts
  - Cannot view application data
  - Designed specifically for security audits

Permissions included:
- View IAM policies
- View service accounts and keys
- View security-related configurations
- View organization policies
- View firewall rules
- Does NOT include data access

Grant the role:
```bash
gcloud projects add-iam-policy-binding my-project \
  --member=user:auditor@thirdparty.com \
  --role=roles/iam.securityReviewer
```

- Option A is incorrect because:
  - `roles/viewer` provides read access to ALL resources including data
  - Can view actual data in databases, storage, etc.
  - Too broad for security audit

- Option C is incorrect because:
  - `roles/iam.roleViewer` only allows viewing role definitions
  - Doesn't provide access to policies or security configurations
  - Too narrow

- Option D is incorrect because:
  - `roles/security.reviewer` doesn't exist
  - Not a valid GCP role

**Security Reviewer Use Case:** External auditors, compliance teams, security consultants

---

## Question 15
Your organization requires that all service account keys be rotated every 90 days. How can you identify service account keys that are older than 90 days?

**A)** Use Cloud Monitoring to create an alert

**B)** Use the following gcloud command:
```bash
gcloud iam service-accounts keys list \
  --iam-account=SA_EMAIL \
  --filter="validAfterTime<-P90D" \
  --format="table(name,validAfterTime)"
```

**C)** Check the IAM & Admin section in Cloud Console

**D)** Use Cloud Asset Inventory to export all service accounts

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - `gcloud iam service-accounts keys list` shows all keys for a service account
  - `--filter="validAfterTime<-P90D"` filters keys created more than 90 days ago
  - `-P90D` is ISO 8601 duration format (90 days in the past)
  - Provides exact information needed

Complete automation example:
```bash
# List all service accounts
gcloud iam service-accounts list --format="value(email)" > /tmp/sa-list.txt

# Check each service account for old keys
while read SA_EMAIL; do
  echo "Checking $SA_EMAIL..."
  gcloud iam service-accounts keys list \
    --iam-account=$SA_EMAIL \
    --filter="validAfterTime<-P90D AND keyType=USER_MANAGED" \
    --format="table(name,validAfterTime)"
done < /tmp/sa-list.txt
```

Create alert for old keys:
```bash
# Export findings to Cloud Asset Inventory
# Then create Cloud Monitoring alert based on key age
```

- Option A is incorrect because:
  - Cloud Monitoring doesn't have built-in metrics for service account key age
  - Would require custom metrics or scripting
  - Not the direct approach

- Option C is incorrect because:
  - Cloud Console shows keys but doesn't filter by age easily
  - Manual process
  - Not scalable for many service accounts

- Option D is incorrect because:
  - Cloud Asset Inventory shows service accounts but not detailed key information
  - Doesn't provide key age filtering
  - Wrong tool for this specific task

**Best Practice:**
- Prefer alternatives to service account keys (Workload Identity, impersonation)
- If keys are necessary, rotate regularly
- Use system-managed keys when possible
- Monitor key usage with Cloud Logging

Check key usage:
```bash
# View service account key usage in audit logs
gcloud logging read \
  'protoPayload.authenticationInfo.serviceAccountKeyName!="" AND
   timestamp>="2024-01-01T00:00:00Z"' \
  --limit=50
```
