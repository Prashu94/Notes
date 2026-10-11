# Case studies

The standard Professional Cloud Architect exam uses **2 of these 4** companies. Case-study questions are **20–30%** of the sitting. The PDF is on a split screen. Read the official PDFs linked from the exam guide before exam week. This file is a way to practice decisions. It is not a substitute for the PDFs, and it does not reproduce them.

Retired and **not** on the current exam: Mountkirk Games, TerramEarth, Helicopter Racing League, Dress4Win. Do not spend the last week on those names.

For each company, mark up the official PDF with four highlighter colors: availability number, data that cannot move, identity, and anything that says “must not” or “keep existing”. Those marks decide more questions than the product list.

## How to answer a case-study item

1. Find the sentence in the PDF that the option would violate.
2. If none, pick the smallest option that meets the number they printed.
3. Name the pillar if two options survive.

## EHR Healthcare

What to remember from the public exam material: a SaaS electronic health record company serving clinics, hospitals, and insurers. They are leaving colocation under time pressure. Customer-facing availability is discussed as a regional target in the 99.9% class, not as “five nines everywhere”. Insurer integrations are legacy and are not all free to move. Containerized applications matter. They want faster, safer releases and monitoring that people actually see. Health-record privacy applies.

Architecture you can defend:

| Need | Choice | Pillar |
| --- | --- | --- |
| Customer-facing containers, zone loss | Regional GKE | Reliability at the stated target |
| Same policy on clusters that remain outside Google Cloud | GKE Enterprise (Config Sync, Policy Controller) | Operational excellence and security |
| Relational data that is MySQL or SQL Server shaped, one region | Cloud SQL HA, private IP | Reliability without overbuying Spanner |
| Insurer links that stay put | HA VPN or Partner/Dedicated Interconnect sized to the traffic, plus the existing interface | Reliability and the “do not migrate this” constraint |
| New partners onboard quickly | Apigee in front of a stable API | Business requirement |
| PHI | Services covered by the BAA, VPC Service Controls, CMEK where policy requires, audit logs exported, no public database | Security and compliance |
| Bad releases caused by hand deploys | Terraform and Cloud Deploy, small rollouts, rollback | Operational excellence |
| Alerts that were missed | SLO alerts to an on-call channel, not email only | Operational excellence |
| Logs kept for an investigation | Sinks to BigQuery or Cloud Storage with retention | Compliance |

Reject: multi-region Spanner “because healthcare sounds important”, public IPs on databases, a big-bang cutover the week the lease ends, and shutting down the insurer interface because it is old.

## Cymbal Retail

What to remember: a fast-growing online retailer with a large catalog. The transformation is three tracks, not a free redesign. One track enriches the catalog with generative AI (images, text, documents) and keeps a **human review** step. One track is conversational shopping and product discovery. One track modernizes the current stack and is explicit about cost. Expect existing relational databases and a document-shaped catalog in the PDF. Read the cost numbers in the PDF and do not beat them with a more expensive design that the stem did not ask for.

Architecture you can defend:

| Need | Choice | Pillar |
| --- | --- | --- |
| Catalog enrichment | Document AI, Vision, and a Gemini model for text. Write results back only after review. | The case’s own process constraint |
| Human in the loop | A queue (Cloud Tasks or Pub/Sub) of drafts, an internal UI on Cloud Run, no auto-publish | Operational excellence and the written process |
| Conversational commerce | Conversational Agents plus search over the catalog (Vertex AI Search / Agent Search) | The business requirement |
| Product system of record | The database that matches the existing engine (Cloud SQL if it is MySQL or SQL Server). Do not move the catalog to BigQuery. | Reliability and cost |
| Document-shaped product data | Firestore, or the MongoDB-compatible path if the PDF says MongoDB and they want to stay document-oriented | Data model |
| Cost track | Cloud Run where Kubernetes is not required, autoscaling, lifecycle on images, committed use only on the steady baseline | Cost |
| Card data or customer PII | Reduce what you store, Sensitive Data Protection, do not put PANs in prompts or logs | Security |

Reject: publishing model output straight to the live site, training a foundation model from scratch, and Spanner for a regional catalog because “retail is global” when the PDF did not require global writes.

## Altostrat Media

What to remember: a media company that already runs on Google Cloud. Expect an existing estate of GKE, BigQuery, Cloud Run, and Cloud Run functions, plus a large library of audio and video. Generative AI is for summarization, metadata, recommendations, support, and moderation. Moderation that affects the public should be explainable and auditable. Storage cost of a large archive matters.

Architecture you can defend:

| Need | Choice | Pillar |
| --- | --- | --- |
| Already on GKE and Cloud Run | Keep the split. Do not move every function onto GKE to “make it consistent”. | Cost and operational excellence |
| Transcode, metadata, recommendations as events | Cloud Run functions or Dataflow, triggered from object finalize or Pub/Sub | The existing pattern |
| Library cost | Cloud Storage with Autoclass or a lifecycle to colder classes. CDN or Media CDN for popular objects. | Cost and performance |
| Summaries and metadata | Gemini multimodal models plus Video Intelligence or Speech-to-Text where the structure is a known API | PCA 2.5, differentiate APIs |
| Support bot | Conversational Agents grounded on their own corpus, with sources | Security: retrieval filter |
| Moderation | A model endpoint plus logs of the decision. Explainable AI or logged features when the PDF asks for auditability. Human review for the borderline. | Security and compliance |
| Audience analytics | BigQuery, which they already have. Not the place you store the media bytes. | Data model |
| New training at real scale | AI Hypercomputer only if the PDF says they train large models. Calling a Gemini API is not a training cluster. | Cost |

Reject: Filestore as the global media library, a new data warehouse beside BigQuery, and a GPU pool that stays on because one model is called a few times an hour.

## KnightMotives Automotive

What to remember: a vehicle manufacturer, including electric, hybrid, and combustion lines, with autonomous driving in the story. Telemetry volume is high. They want a better in-vehicle and dealer experience, a path to monetize data without leaking it, and partner APIs. European data-protection constraints show up. Dealers should not need a hardware rollout to get a new tool. Hybrid plants and systems will not all move in one wave.

Architecture you can defend:

| Need | Choice | Pillar |
| --- | --- | --- |
| Telemetry ingest | Pub/Sub, then Dataflow, hot operational store in Bigtable, analytics in BigQuery | Performance and the data model |
| Autonomous model training | AI Hypercomputer with GPUs or TPUs, a reservation if the run is large | PCA 2.4 |
| In-vehicle or app inference | A deployed endpoint or a smaller Gemini/model path, not the training cluster | Cost |
| Dealer tools, no new dealer hardware | A web app on Cloud Run or App Engine behind IAP | Operational excellence |
| Partner and dealer APIs | Apigee, quotas, separate credentials per partner | Security |
| Data monetization | A governed BigQuery platform, Analytics Hub or a curated exchange, column security, no raw dump to a partner bucket | Security and compliance |
| EU residency | Resource-location organization policy, regional services, Assured Workloads when the PDF requires a controlled environment | Compliance |
| Factories that stay | GKE Enterprise for the clusters that move, Interconnect or HA VPN for the sites that stay | Migration plan |
| Identity | Workforce identity federation, not shared VM passwords | Security |

Reject: one global Cloud SQL for all telemetry, a public dealer VM with SSH on 0.0.0.0/0, and copying the full vehicle dataset to a partner project.

## Drill

Take one company. Set a 15-minute timer. From memory, write:

- The availability or process constraint
- The thing you will not migrate
- Compute, data, network, AI, and the operational control
- Two tempting answers you will reject

Then open the official PDF and mark what you invented that the PDF does not say. Inventing a constraint is how those questions are lost.
