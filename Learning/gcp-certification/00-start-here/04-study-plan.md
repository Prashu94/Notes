# Twelve-week plan

Hours assume a working engineer doing about 8–10 hours a week. Compress to 6 weeks by doing two weeks per week if you already operate Google Cloud daily. Do not compress by skipping labs.

ACE-only candidates can stop after week 8 and sit the exam, then continue 9–12 for PCA.

## Weeks 1–2 — Environment and identity

Read:

- `01-foundations/01-resource-hierarchy-iam-billing.md`
- `01-foundations/02-gcloud-and-cloud-shell.md`
- `01-foundations/03-regions-zones-quotas-pricing.md`
- `02-services/10-iam-security-compliance.md` (IAM, org policy, audit logs only)

Do lab 01 and lab 02.

You can: create a project under a folder, link billing, set a budget, enable an API, grant a predefined role to a group, create a service account and impersonate it, read a quota.

## Weeks 3–4 — Compute

Read:

- `02-services/01-compute-engine.md`
- `02-services/02-gke.md`
- `02-services/03-cloud-run-and-app-engine.md`

Do labs 03, 04, and 05.

You can: instance template plus regional MIG, private GKE Autopilot plus a Deployment, Cloud Run service with traffic split, Cloud Run function on a Pub/Sub event. You can say which of the four a stem wants.

## Week 5 — Networking

Read:

- `02-services/05-vpc-and-hybrid-networking.md`
- `02-services/06-load-balancing-dns-cdn-armor.md`

Do lab 06.

You can: custom-mode VPC, firewall with a service account, Cloud NAT, static IP, private services access, and pick global external Application Load Balancer versus internal passthrough.

## Week 6 — Storage and databases

Read:

- `02-services/07-cloud-storage-and-file.md`
- `02-services/08-databases.md`

Do labs 07 and 08.

You can: lifecycle a bucket, load a CSV into BigQuery, choose Cloud SQL versus AlloyDB versus Spanner versus Firestore versus Bigtable versus Memorystore from a one-paragraph stem.

## Week 7 — Data pipelines, CI/CD, operations

Read:

- `02-services/09-analytics-and-pipelines.md`
- `02-services/11-observability-and-operations.md`
- `02-services/12-cicd-iac-and-deployment.md`
- `02-services/15-integration-apis-and-eventing.md`

Do labs 09 and 10.

## Week 8 — ACE exam week

Read `03-ace/` end to end. Sit `ace-practice-exam.md` closed-book. Review every miss against the service chapter. If you are only taking ACE, schedule the exam after a second pass of the decision trees.

## Weeks 9–10 — Architect design

Read:

- `04-pca/well-architected-framework.md`
- `04-pca/design-decisions.md`
- `02-services/13-ai-ml-and-gemini.md`
- `02-services/14-migration-hybrid-multicloud.md`
- `02-services/16-full-product-catalog.md` (recognition pass)

For each pillar, write three recommendations that would change an answer.

## Week 11 — Case studies

Open the four official PDFs from the exam guide. Then read `04-pca/case-studies.md` and redo each company in your own words: requirement, constraint, product, pillar, what you will not recommend.

Do `04-pca/pca-exercises.md`.

## Week 12 — PCA exam week

Sit `04-pca/pca-practice-exam.md`. Rebuild `06-reference/decision-trees.md` from memory. Schedule the exam only when you can explain a wrong option in one sentence.
