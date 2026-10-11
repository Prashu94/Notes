# CI/CD and Terraform deep dive

Read `12-cicd-iac-and-deployment.md` first. This file is the YAML and the order of operations that file only sketched.

## Who owns which change

| Change | Owner | Not the owner |
| --- | --- | --- |
| VPC, IAM, databases, buckets | Terraform in its own pipeline | The application Dockerfile |
| Image build and unit test | Cloud Build | A laptop |
| Image storage | Artifact Registry | Container Registry, which is retired |
| “Is this image allowed” | Binary Authorization | A wiki |
| Dev then prod rollout of a container | Cloud Deploy | Terraform applying a new image tag on every commit, if Cloud Deploy already exists |
| Kubernetes desired state pulled from git | Config Sync | A second person running `kubectl apply` |
| Cron | Cloud Scheduler | A VM crontab |

Two writers for one resource cause drift. Pick one.

## Cloud Build file

```yaml
steps:
  - id: test
    name: python:3.12-slim
    entrypoint: bash
    args: ["-c", "pip install -r requirements.txt && pytest"]
  - id: build
    name: gcr.io/cloud-builders/docker
    args:
      ["build", "-t", "${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/web:$SHORT_SHA", "."]
  - id: push
    name: gcr.io/cloud-builders/docker
    args: ["push", "${_REGION}-docker.pkg.dev/$PROJECT_ID/${_REPO}/web:$SHORT_SHA"]
substitutions:
  _REGION: us-central1
  _REPO: apps
options:
  logging: CLOUD_LOGGING_ONLY
serviceAccount: "projects/$PROJECT_ID/serviceAccounts/builder@${PROJECT_ID}.iam.gserviceaccount.com"
```

`$PROJECT_ID` and `$SHORT_SHA` are built-in substitutions. `_REGION` is yours because it starts with an underscore.

The build service account needs `roles/artifactregistry.writer` and `roles/logging.logWriter`. It does not need Owner. If the build must reach a private Git server or a private package mirror, use a private pool peered to the VPC. The default pool has no path into your private network.

```bash
gcloud builds submit --config=cloudbuild.yaml --region="$REGION"
gcloud builds triggers create github \
  --name=web --repo-owner=ORG --repo-name=web \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --region="$REGION" \
  --service-account="projects/${PROJECT_ID}/serviceAccounts/builder@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud builds list --region="$REGION" --limit=5
gcloud builds log BUILD_ID --region="$REGION"
```

Store the image by digest after the push. Tags move. Digests do not.

## Scanning and signing

```bash
gcloud artifacts repositories create apps \
  --repository-format=docker --location="$REGION"
gcloud artifacts docker images scan \
  "${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/web:${SHORT_SHA}"
gcloud artifacts docker images list-vulnerabilities \
  "${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/web:${SHORT_SHA}"
```

Scanning reports CVEs. It does not block a deploy. Blocking is Binary Authorization in enforcement mode, after an attestor has signed the digest. Dry-run only logs. The exam answer for “prevent” is enforcement.

A practical gate inside Cloud Build: fail the build when the scan finds a severity you do not accept, then sign. The signature is what the cluster checks. The scan is why you signed.

## Cloud Deploy

`clouddeploy.yaml` defines a pipeline and targets. A target is a Cloud Run service or a GKE cluster. A release pins images. Promotion moves the release to the next stage. A prod stage can require approval.

```yaml
apiVersion: deploy.cloud.google.com/v1
kind: DeliveryPipeline
metadata:
  name: web
serialPipeline:
  stages:
    - targetId: dev
    - targetId: prod
      profiles: []
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: dev
run:
  location: projects/PROJECT_ID/locations/us-central1
---
apiVersion: deploy.cloud.google.com/v1
kind: Target
metadata:
  name: prod
run:
  location: projects/PROJECT_ID/locations/us-central1
requireApproval: true
```

```bash
gcloud deploy apply --file=clouddeploy.yaml --region="$REGION"
gcloud deploy releases create rel-$SHORT_SHA \
  --delivery-pipeline=web --region="$REGION" \
  --images="web=${REGION}-docker.pkg.dev/${PROJECT_ID}/apps/web:${SHORT_SHA}"
gcloud deploy releases promote \
  --release=rel-$SHORT_SHA --delivery-pipeline=web \
  --region="$REGION" --to-target=prod
gcloud deploy rollouts approve ROLLOUT \
  --release=rel-$SHORT_SHA --delivery-pipeline=web --region="$REGION"
```

Canary and verify jobs are configured on the stage strategy. Use them when the stem says “send 10% then continue if the error rate stays low.” A standard strategy replaces the service. Rollback is promoting the previous release again, or rolling the rollout back.

GKE targets render Kubernetes manifests (skaffold or raw YAML). The same pipeline idea applies. Do not also have a person edit the deployment in the console.

## Terraform that will not embarrass you

```hcl
terraform {
  required_version = ">= 1.6.0"
  backend "gcs" {
    bucket = "PROJECT_ID-tf-state"
    prefix = "prod"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "assets" {
  name                        = "${var.project_id}-assets"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning {
    enabled = true
  }
}
```

Rules:

- One state file per environment. Prod state is not dev state.
- The state bucket has uniform access, versioning, and a retention or a tight IAM list. State contains secrets if you put secrets in resources. Prefer Secret Manager resources so the secret value is not in the plan output. Mark sensitive outputs.
- `terraform plan` is reviewed by a person or a policy check. `apply` runs in Cloud Build or Infrastructure Manager, not on two laptops.
- `prevent_destroy` on databases. `force_destroy` only on lab buckets.
- Import existing resources instead of creating a second copy.
- Modules from the Cloud Foundation Toolkit are a starting point for projects, folders, and networks. They are not mandatory.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform state list
```

Infrastructure Manager runs that apply as a Google Cloud deployment with a service account and a lock. Use it when the stem says “Terraform, but no self-hosted runner.”

```bash
gcloud infra-manager deployments apply projects/$PROJECT_ID/locations/$REGION/deployments/net \
  --service-account=projects/$PROJECT_ID/serviceAccounts/terraform@$PROJECT_ID.iam.gserviceaccount.com \
  --git-source-repo=REPO --git-source-directory=terraform --git-source-ref=main
```

Config Connector is the answer when the platform team wants `kubectl apply` to create a Pub/Sub topic or a bucket next to the workload. Helm is the answer when the unit is a Kubernetes package. Helm does not create the VPC.

Deployment Manager is legacy. Do not choose it for a new design. If a stem has an existing Deployment Manager deployment, the migration path is Terraform, not a second Deployment Manager stack.

## Test types the exam names

| Test | Proves | Where it runs |
| --- | --- | --- |
| Unit | A function, no cloud | Cloud Build, first step |
| Integration | The service plus Pub/Sub or Firestore | Emulators from PCA 5.2, or a sandbox project |
| Load | Latency at the SLO’s traffic | A test project, read Monitoring and Profiler |
| Security / penetration | Known holes, with written scope | A window, not a surprise against prod |
| Chaos | A zone or a dependency dies and the SLO holds | A game day |
| Policy | Terraform plan has no public IP, no `allUsers` | `gcloud` or a policy tool in the pipeline |

Load, chaos, and penetration are section 6.6. They are scheduled and reversible. “We should pentest prod right now with no scope” fails the pillar even though the activity is real.

## GitOps versus push

Config Sync pulls from git and reverts drift. That is the fleet answer. Cloud Deploy pushes a release into a target. Use push when you need approvals and a canary percentage. Use pull when every cluster, including one outside Google Cloud, must match the same repo. Using both without a rule means they fight. Typical split: Terraform and Cloud Deploy for Google Cloud infrastructure and the app release, Config Sync for cluster policy (NetworkPolicy, PodSecurity).

## Exercises

1. Why is `:latest` the wrong prod reference?
2. The build cannot clone an on-prem Git server. The trigger is on the default pool. What do you change?
3. Scanning found no new CVEs. An unsigned image still deployed. What is missing?
4. Two engineers apply the same state from laptops and one overwrites the other. What two changes?
5. Dev must deploy on every merge. Prod must wait for a person. Which Cloud Deploy field?

### Answers

1. The tag moves to a new build. A digest is the bytes you tested. Binary Authorization also binds to the digest.
2. A private pool with a VPC connection that can route to that Git server.
3. Binary Authorization in enforcement mode. Scanning does not block.
4. Remote state in Cloud Storage with locking, and a single pipeline that applies. Stop local applies.
5. `requireApproval: true` on the prod target.
