# How to use this pack

## What you are training

ACE checks whether you can **do** the platform task: the right `gcloud` shape, the right IAM role, the right firewall direction, the right storage class.

PCA checks whether you can **choose** under a written constraint and defend it with the Well-Architected Framework. Commands still matter, because section 5 scores `gcloud`, `gsutil`, `bq`, Terraform, and emulators. They are not the whole exam.

## Daily loop

1. Read one service chapter.
2. Cover the command blocks and rewrite them from memory.
3. Do the exercises at the end. Write the answer before you scroll to it.
4. In a project, run the matching lab once. Cloud Shell is enough for most of them.
5. Add one line to a personal error log: the constraint, the product you picked, why the other three were wrong.

## Command conventions used everywhere

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export ZONE="us-central1-a"
export BILLING_ACCOUNT="XXXXXX-XXXXXX-XXXXXX"

gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
gcloud config set compute/zone "$ZONE"
```

Placeholders in examples:

| Token | Meaning |
| --- | --- |
| `PROJECT_ID` | Project you are acting in |
| `ORG_ID` | Organization numeric ID |
| `REGION` / `ZONE` | Regional or zonal location |
| `NETWORK` | VPC name |
| `SA_EMAIL` | Service account email |

Prefer Cloud Shell. It already has `gcloud`, `kubectl`, `bq`, Terraform, and short-lived credentials. Do not download a service-account JSON key to practice IAM.

## Hands-on safety

- Use a project linked to a billing account you control, with a budget alert at a low amount.
- Delete resources at the end of each lab. Spot VMs, Autopilot clusters, Cloud SQL, and Spanner are the ones that surprise people on the bill.
- Do not put real personal data, card numbers, or health data in labs. Compliance questions are about design, not about uploading regulated data.

## What to skip

Industry products that the exam guides do not score (telecom subscriber insights, earth engine science workflows, and similar) are named in the product catalog with “out of scope” so you know they were considered. Do not spend exam week on them.

Retired PCA case studies are out of scope for the current standard exam. Patterns you learned from them (global HTTP(S) load balancing, Bigtable row keys, CDN for media) still show up as product questions. The company names do not.
