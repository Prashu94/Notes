# gcloud, Cloud Shell, and the tools the exams name

ACE uses the CLI throughout sections 3 and 4. PCA section 5.2 names Cloud Shell Editor, Cloud Code, Cloud Shell Terminal, `gcloud`, `gsutil`, `bq`, emulators, Terraform, and API client libraries.

## Install and initialize

On a laptop:

```bash
# Google Cloud CLI. Cloud Shell already has it.
gcloud version
gcloud init
gcloud auth login
gcloud auth application-default login   # libraries pick this up
gcloud components update
gcloud components install kubectl beta gke-gcloud-auth-plugin
```

Configuration:

```bash
gcloud config configurations create lab
gcloud config configurations activate lab
gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
gcloud config set compute/zone "$ZONE"
gcloud config set account "ada@example.com"
gcloud config list
```

Impersonation for a single command, which is the short-lived credential pattern:

```bash
gcloud compute instances list \
  --impersonate-service-account="$SA_EMAIL"
```

## Command shape

```text
gcloud GROUP SUBGROUP ACTION [NAME] [--flags]
```

Patterns you will reuse:

```bash
gcloud GROUP list
gcloud GROUP describe NAME
gcloud GROUP delete NAME
gcloud GROUP list --filter="status=RUNNING" --format="table(name,zone)"
gcloud topic formats
gcloud help compute instances create
```

`--format` values that show up in operations work: `json`, `yaml`, `table`, `value`, `csv`.

```bash
gcloud compute instances list --format="value(name)"
gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)"
```

## Cloud Shell

- Browser terminal on a temporary VM, 5 GB persistent `$HOME`.
- Tools already present: `gcloud`, `kubectl`, `bq`, Terraform, language SDKs, Docker (with limits).
- Credentials are your user (or the identity you set). The machine is ephemeral. Do not store the only copy of data there.
- **Cloud Shell Editor** is the IDE in the same environment. **Cloud Code** is the plugin for VS Code and JetBrains that talks to Cloud Run, GKE, and Secrets. PCA 5.2 lists all three. Pick Cloud Shell when the stem says “no local install”. Pick Cloud Code when the stem says the developer’s existing IDE.
- **Cloud Workstations** is a managed dev environment when the team needs a locked-down, admin-provisioned workstation. It is a PCA recognition topic, not the default “run a command” answer. Cloud Shell is.

```bash
# Open a session is a console action. Inside it:
echo "$GOOGLE_CLOUD_PROJECT"
gcloud config get-value project
```

## gsutil and gcloud storage

`gsutil` is still on the PCA exam guide. New scripts should prefer `gcloud storage`, which speaks the same ideas.

```bash
# Upload and download
gsutil cp local.txt gs://BUCKET/path/local.txt
gsutil -m cp -r ./dir gs://BUCKET/dir
gsutil rsync -r ./dir gs://BUCKET/dir
gcloud storage cp local.txt gs://BUCKET/path/local.txt
gcloud storage rsync ./dir gs://BUCKET/dir --recursive

# IAM on a bucket
gcloud storage buckets add-iam-policy-binding gs://BUCKET \
  --member="group:analysts@example.com" \
  --role="roles/storage.objectViewer"

# Signed URL (temporary access without IAM for that person)
gcloud storage sign-url gs://BUCKET/path/object \
  --duration=10m \
  --impersonate-service-account="$SA_EMAIL"
```

## bq

```bash
bq ls
bq ls --project_id="$PROJECT_ID" dataset_name
bq query --use_legacy_sql=false \
  'SELECT name, SUM(number) c FROM `bigquery-public-data.usa_names.usa_1910_current`
   GROUP BY name ORDER BY c DESC LIMIT 5'
bq load --source_format=CSV --autodetect \
  dataset.table gs://BUCKET/file.csv
bq extract --destination_format=CSV \
  dataset.table gs://BUCKET/out-*.csv
bq show --format=prettyjson dataset.table
```

## kubectl

```bash
gcloud components install gke-gcloud-auth-plugin
gcloud container clusters get-credentials CLUSTER --region="$REGION"
kubectl config current-context
kubectl get nodes,pods,svc -A
kubectl apply -f manifest.yaml
kubectl logs DEPLOY/NAME
kubectl exec -it POD -- -- sh
```

## Emulators (PCA 5.2)

Local emulators exist so tests do not bill a real instance and do not need production data. The exam list is Bigtable, Spanner, Pub/Sub, and Firestore. Datastore mode is the same Firestore emulator family. You start them with `gcloud beta emulators`.

```bash
gcloud components install cloud-firestore-emulator pubsub-emulator bigtable \
  cloud-spanner-emulator
gcloud beta emulators firestore start --host-port=localhost:8080
gcloud beta emulators pubsub start --host-port=localhost:8085
# In another shell, export the env the client libraries read:
$(gcloud beta emulators pubsub env-init)
```

When the stem says “integration tests on a laptop without a live project”, the answer is the emulator, not a shared dev project.

## API client libraries

Server code should use the client library for the language, Application Default Credentials, and retries. Do not embed API keys in source for Google Cloud APIs that support ADC. Enable the API, call it as the attached service account, and use the library’s idempotency and retry.

Direct REST is acceptable. The exam phrase “Google API client libraries” means the supported libraries, not a hand-rolled curl with a key in the repo.

## Terraform and the other IaC tools (ACE 3.6, PCA 5.2)

Terraform is the tool both exams expect you to recognize. Infrastructure Manager runs Terraform for you inside Google Cloud. Config Connector manages Google Cloud resources as Kubernetes objects. Helm packages Kubernetes manifests. Cloud Foundation Toolkit is a set of reference Terraform modules. Deployment Manager is legacy. Pulumi, Ansible, and CDK for Terraform appear in the docs catalog. Know they exist. Do not pick them over Terraform unless the stem says the team already standardized on them.

```bash
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

A minimal pattern:

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "state_example" {
  name                        = "${var.project_id}-assets"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}
```

Store remote state in a Cloud Storage bucket with versioning, not on a laptop. Locking matters when more than one person applies.

## Exercises

1. A developer has no laptop install and must run `bq`. Where do they work?
2. CI logs show a JSON key committed last year. What replaces it for GitHub Actions?
3. Unit tests need Pub/Sub and must not create a topic in the prod project. What do you start?
4. Name the three CLI tools PCA section 5.2 lists, and one job each.

### Answers

1. Cloud Shell Terminal (or Cloud Shell Editor). `bq` is preinstalled.
2. Workload Identity Federation to a service account. Delete the key.
3. The Pub/Sub emulator, then point the test at the emulator host.
4. `gcloud` for the platform, `gsutil` for object upload and bucket operations, `bq` for BigQuery jobs and SQL.
