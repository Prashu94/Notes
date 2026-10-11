# Lab 10 — Terraform bucket

## Goal

One resource, a plan, an apply, a destroy. Remote state is commented so the lab works before you have a state bucket. For anything you keep, move state to Cloud Storage.

## Steps

```bash
mkdir -p /tmp/lab-tf && cd /tmp/lab-tf
cat > main.tf << EOF
terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}
provider "google" {
  project = "$PROJECT_ID"
  region  = "$REGION"
}
resource "google_storage_bucket" "lab" {
  name                        = "${PROJECT_ID}-tf-lab"
  location                    = "$REGION"
  uniform_bucket_level_access = true
  force_destroy               = true
}
EOF

terraform init
terraform plan -out=tfplan
terraform apply tfplan
gcloud storage buckets describe "gs://${PROJECT_ID}-tf-lab" --format="value(name)"
terraform destroy -auto-approve
```

## Check

The bucket exists after apply and is gone after destroy. You can explain why `force_destroy` would be dangerous on a real data lake (it deletes objects). Remove it in any real stack.
