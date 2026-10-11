# Security and operations deep dive

Read foundations, chapter 10, and chapter 11 first. This file is IAM conditions, deny policies, Workload Identity Federation, VPC Service Controls, supply chain, and alerting.

## How a request is allowed

The effective permission is the union of allow bindings from the resource up through project, folder, and organization, minus any deny that matches. A deny wins over an allow. Organization policy can still block the operation even when IAM allows it. VPC Service Controls can block it even when IAM and org policy allow it. You debug in that order: IAM, then org policy, then the perimeter, then the VPC firewall if it is a packet not an API call.

## Conditions

A condition is CEL on one binding. It narrows that binding. It does not create a deny for everyone else.

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="group:devs@example.com" \
  --role="roles/compute.instanceAdmin.v1" \
  --condition='expression=request.time.getHours("Europe/London") >= 9 && request.time.getHours("Europe/London") < 17,title=office-hours'
```

Resource conditions (`resource.name.startsWith(...)`) limit a role to a bucket prefix or a dataset. Use them when you cannot split projects yet. Splitting projects is still cleaner.

## Deny policies

Deny policies attach to a project, folder, or organization. They list principals and permissions that are denied even if some other binding allows them.

Use a deny when the stem says “this group must never be able to delete KMS keys, even if someone later grants them admin”. An allow you simply do not grant is weaker, because a later Owner binding would add it back.

```bash
# The IAM v2 deny API is easier in the console or as a policy file.
# Know that deny overrides allow, and that it is not an organization policy.
gcloud iam policies list --attachment-point="cloudresourcemanager.googleapis.com/projects/${PROJECT_ID}"
```

## Service account role matrix

| Role on the service account resource | Lets the member |
| --- | --- |
| `iam.serviceAccountUser` | Attach the account to a VM or to Cloud Run, and act as it for some calls |
| `iam.serviceAccountTokenCreator` | Mint access tokens and identity tokens (impersonation) |
| `iam.serviceAccountKeyAdmin` | Create and delete JSON keys. Almost never grant. |
| `iam.serviceAccountAdmin` | Create accounts and set their policy. Powerful. |

The roles the service account itself has (on the project or the bucket) are what the code can do. The roles on the service account resource are who can use that identity. Questions swap these. Read “who can deploy as this account” as a binding on the service account. Read “what the code can read” as a binding for the service account on the data.

Disabled service accounts fail calls. Deleting one that is still attached breaks the workload. Disable first.

## Workload Identity Federation for GitHub

No downloaded key. A pool trusts GitHub’s OIDC token. An attribute condition restricts the repository. A binding lets that principal impersonate one service account.

```bash
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

gcloud iam workload-identity-pools create github \
  --location=global --project="$PROJECT_ID"

gcloud iam workload-identity-pools providers create-oidc github \
  --location=global --workload-identity-pool=github \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='my-org/my-repo'"

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/attribute.repository/my-org/my-repo"
```

The GitHub action then uses the Google auth action with that pool provider. If the stem says AWS or Azure calling Google, the same pool exists with a different provider. The idea is identical: the foreign token becomes a short-lived Google token.

Workforce identity pools are for people (an external IdP), not for CI. Do not mix the two names.

## VPC Service Controls

A perimeter lists projects and services (`storage.googleapis.com`, `bigquery.googleapis.com`). Calls that copy data from a project inside the perimeter to a project outside are blocked even if IAM allows them. Ingress and egress rules punch the specific holes (a Cloud Build project, a partner).

Access Context Manager holds access levels: IP range, device policy, required member. A perimeter can require an access level so that even an allowed identity must come from the corporate IP.

```bash
gcloud access-context-manager policies list --organization="$ORG_ID"

gcloud access-context-manager levels create corp-ip \
  --policy=POLICY_ID \
  --basic-level-spec=level.yaml

# Perimeter creation is a YAML or the console.
# You should be able to say: projects, restricted services, access level, ingress rule.
gcloud access-context-manager perimeters list --policy=POLICY_ID
```

Dry-run perimeters log what would have been blocked. Use dry-run before enforcement in production. The exam likes that sequence.

A blocked call shows up in the audit log as a VPC Service Controls denial. IAM will look correct. That is the diagnostic clue.

## IAP for applications

IAP in front of an HTTPS backend checks Google identity and `roles/iap.httpsResourceAccessor` before the request hits the VM or Cloud Run. The app does not implement login. SSH IAP is the TCP feature. They share a product name and not much else.

Chrome Enterprise Premium is the broader zero-trust product (device trust, context) the PCA guide lists next to IAP. Pick it when the stem goes beyond “put IAP on this one backend” into device posture for the company.

## Supply chain sequence

1. Cloud Build trigger on the repository, private pool if the source is on the VPC.
2. Build service account can push to Artifact Registry and nothing else it does not need.
3. On-demand scanning or automatic scanning on the repository.
4. An attestor signs only if the scan passed and the build came from the main branch. The attestation is a note on the image.
5. Binary Authorization enforcement on the GKE cluster and on Cloud Run.
6. Cloud Deploy promotes the digest, not the tag `:latest`.

`:latest` is the wrong production reference because it moves. A digest is immutable.

```bash
gcloud artifacts docker images describe \
  "${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/web@sha256:DIGEST"
```

## Audit logs you enable

Admin Activity is already on. Data Access is not, except BigQuery’s data access which is on.

Enable Data Access per service when you must record reads (`storage.objects.get`, secret access). The volume is the cost. A stem that says “record every object read” is Data Access plus a sink. A stem that says “who changed the firewall” is Admin Activity, already there.

```bash
# Data Access is a project IAM policy audit config, not a logging sink.
# In the console: IAM, Audit Logs, select the service, enable Data Read.
gcloud projects get-iam-policy "$PROJECT_ID" --format=json | head
```

Log buckets:

| Bucket | You control retention? | Locked? |
| --- | --- | --- |
| `_Required` | No. Long, fixed. Admin Activity lives here. | Yes |
| `_Default` | Yes | Until you lock it |
| User bucket | Yes | You can lock a retention period |

A locked bucket retention cannot be shortened. That is the compliance answer, similar to a Cloud Storage retention lock. A sink to BigQuery is still what you want for SQL. A sink to Cloud Storage is what you want for cheap years-long bytes.

Log Analytics on a bucket lets you query logs with SQL without a sink. Use it for recent investigation. Use a sink when another team owns the warehouse or the retention must outlive the bucket you might delete.

## Alerting that matches section 6

An alerting policy has:

- A condition (threshold or absence) on a metric, aligned over a window
- A duration the condition must stay true (stops one-spike pages)
- A notification channel that is not email-only
- Documentation in the policy (what to do)

Alert on symptoms: request error ratio, latency, uptime check failure, replication lag, disk full, backup age. CPU is a diagnostic, not a page, unless the service actually falls over at a known CPU.

```bash
gcloud monitoring channels list
gcloud monitoring policies list

# Uptime from outside
gcloud monitoring uptime create api-check \
  --resource-type=uptime-url \
  --resource-labels=host=api.example.com,project_id="$PROJECT_ID" \
  --protocol=https --path=/healthz --period=60 --timeout=10
```

An SLO is a target on an SLI over a window (28 or 30 days is typical). A burn-rate alert pages when you are consuming the error budget too fast, and tickets when you are consuming it slowly. One threshold on CPU does not do this.

Absence alerts (“metric stopped arriving”) catch a collector that died. A threshold alert stays green if the Ops Agent is dead and no data arrives. Pair them for VMs.

## Incident habits the architect exam accepts

- One commander, a log, a customer update cadence
- Rollback first if the last change lines up with the start time
- Cloud Trace for “which hop got slow”, logs for that hop, Profiler if the hop is CPU inside one process
- Connectivity Tests for “the firewall or route is the bug”
- A written review with actions, not a new slide of the architecture

Chaos and penetration tests are authorized and scoped. A load test is how you prove the performance pillar. Running any of the three against production without a window and a backout fails the operational-excellence question even if the tool is correct.

## Personalized Service Health

The public status page is global. Personalized Service Health is what affects your project. Use both. An alert on “Google said the product is down in your region” belongs in the on-call channel next to your own uptime check.

## Exercises

1. A binding grants Editor. A deny policy denies `compute.instances.delete` for that group. Can they delete a VM?
2. GitHub still has a JSON key and also a workload identity pool. What do you do with the key?
3. IAM allows `bq extract` to a bucket in another project. The call fails with a perimeter error. What is working as designed?
4. You enabled a log sink to BigQuery and no rows appear. What identity did you forget?
5. CPU alerts page 40 times a day and the real outage had no page. What do you change?

### Answers

1. No. Deny wins.
2. Delete the key after the federation path is proven. Leaving both keeps the long-lived secret.
3. VPC Service Controls. Fix with an ingress or egress rule if the extract is legitimate, not with a broader IAM role.
4. The sink writer identity needs permission to write the destination. The sink existing is not the grant.
5. Replace CPU paging with an SLO or error-rate and latency alert on a real channel. Keep CPU on a dashboard.
