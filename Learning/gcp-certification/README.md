# Google Cloud certification study pack

English study material for two exams:

- **Associate Cloud Engineer (ACE)** — deploy, secure, and operate solutions.
- **Professional Cloud Architect (PCA)** — design solutions against business constraints, the Well-Architected Framework, and four official case studies.

Written against the exam guides current as of October 2026. Google can change product names and objectives at any time. Before you book a seat, re-read:

- [Associate Cloud Engineer exam guide](https://cloud.google.com/certification/guides/cloud-engineer)
- [Professional Cloud Architect exam guide](https://cloud.google.com/learn/certification/guides/professional-cloud-architect)
- [Google Cloud documentation home](https://docs.cloud.google.com/docs)

This pack is original study notes. It is not a copy of Google’s documentation. Commands are the ones you actually run. Official docs remain the source of truth for flags that change.

## How the folder is organized

| Path | What it is |
| --- | --- |
| `00-start-here/` | Exam facts, full objective lists, 12-week plan |
| `01-foundations/` | Hierarchy, IAM, billing, CLI, regions, quotas |
| `02-services/` | Every product family. Files `01`–`16` are the map and the commands. Files `17`–`23` are the mechanism those chapters shortened: disks and MIGs, private GKE, Cloud Run settings, HA VPN and firewalls, storage and BigQuery behavior, IAM deny and VPC Service Controls, and the AI path. |
| `03-ace/` | ACE section walkthrough, hands-on drills, practice exam |
| `04-pca/` | Well-Architected Framework, design method, case studies, practice exam |
| `05-labs/` | End-to-end labs you can run in a project |
| `06-reference/` | Decision trees, command index, traps |

## Product names used on the current exams

The certification pages say the exams were updated for branding. Use these names. Older notes that only say the legacy name will miss items.

| Say this | Older name you will still see |
| --- | --- |
| Cloud Run functions | Cloud Functions (2nd gen is Cloud Run functions; 1st gen was Cloud Functions) |
| Gemini Enterprise Agent Platform | Much of what study notes still call Vertex AI |
| Agent Platform Pipelines | Vertex AI Pipelines |
| Sensitive Data Protection | Cloud DLP |
| GKE Enterprise | Anthos |
| Managed Service for Apache Airflow | Cloud Composer |
| Looker Studio | Data Studio |
| Artifact Registry | Container Registry (shut down) |
| Infrastructure Manager / Terraform | Deployment Manager (legacy) |

The ACE exam guide text fetched in October 2026 still prints “Cloud Functions” in a few bullets. The PCA guide prints “Cloud Run functions”. Learn the product as **Cloud Run functions**, and recognize **Cloud Functions** when an older stem uses it.

## Exam logistics

| | Associate Cloud Engineer | Professional Cloud Architect |
| --- | --- | --- |
| Length | 2 hours | 2 hours |
| Questions | 50–60 multiple choice and multiple select | 50–60 multiple choice and multiple select |
| Fee | 125 USD plus tax | 200 USD plus tax |
| Languages | English, Japanese, Spanish, Portuguese | English, Japanese |
| Validity | 3 years | 2 years |
| Recommended experience | 6+ months hands-on | 3+ years industry, including 1+ year designing on Google Cloud |
| Case studies | None | 2 of 4 on every sitting; 20–30% of the exam |
| Prerequisite | None | None |

Google does not publish a numeric passing score. Do not study toward a made-up 70%.

Renewal (if you already hold the cert and are inside the renewal window): a shorter renewal exam, or designated Google Skills courses. The PCA renewal exam is about generative AI (one case study, about 90–100% of that shorter sitting). This pack prepares you for the **standard** exams. The AI chapters also cover what the renewal sitting emphasizes.

## Suggested order

Follow `00-start-here/00-complete-reading-order.md`. That is the full guide in order. Files `02-services/01` through `16` are the map. Files `17` through `26` are the detail. Do not stop at the map.

1. Read `00-start-here/02-ace-exam-blueprint.md` and `03-pca-exam-blueprint.md` so you know what is scored.
2. Do foundations, then every file in `02-services/` in the reading-order list. Do the exercises before you read the answers.
3. Run the labs in `05-labs/` in a real project or in the free tier. Reading commands is not the same as typing them.
4. ACE candidates: `03-ace/` then the ACE practice exam. Sit ACE before PCA if IAM, VPC, and `gcloud` are not weekly work.
5. PCA candidates: `04-pca/` after the service chapters. Read the four official case-study PDFs on the exam guide page. The notes here teach how to answer them. They do not replace the PDFs.
6. Use `06-reference/decision-trees.md` in the last week. That is where most wrong answers come from.

## What “do not miss a topic” means in this pack

`02-services/16-full-product-catalog.md` walks the October 2026 documentation catalog: every technology area on [docs.cloud.google.com/docs](https://docs.cloud.google.com/docs), with exam weight (must know, should recognize, or out of scope for these two exams) and the command or console path. Industry-only products that never appear on ACE or PCA are listed so you can see they are out of scope, not forgotten.
