# Case studies

Every standard Professional Cloud Architect exam uses **2 of these 4** companies. Those questions are **20–30%** of the score. The official PDF stays on a split screen. Read the four PDFs linked from the exam guide in the week you book the exam. Numbers and “must not” sentences in the PDF beat this chapter if they differ. This chapter is the decision method and the architecture you can defend from the public shape of each case. It does not replace the PDF and it does not copy it.

Retired. Do not study these names for the current exam: Mountkirk Games, TerramEarth, Helicopter Racing League, Dress4Win.

## How to mark a PDF

Use four marks.

| Mark | You are hunting |
| --- | --- |
| Number | 99.9, RPO, RTO, a cost cap, a deadline, a retention period |
| Stay | A system, a team, or a site that must not move in this wave |
| Identity and data class | PHI, PCI, PII, EU, who may see it |
| Pain | What already failed: deploys, alerts, capacity, onboarding time |

Answer in this order: violate none of the marks, meet the number with the smallest design, then the pillar the question is about.

## EHR Healthcare

**What the case is.** A SaaS electronic health record company. Clinics, hospitals, and insurers. They are leaving colocation. One lease creates a deadline. Customer-facing availability is a regional target in the 99.9% class. Some insurer connections stay where they are. Applications are largely containers. Releases and monitoring have caused real outages. Health privacy applies. They want new insurer partners onboarded through a stable API, and they want CapEx to become OpEx.

**Landing zone**

| Need | Design | Why it is not the louder option |
| --- | --- | --- |
| Folders and projects | One folder for the regulated estate, projects split by env and by shared versus app | One project for everything fails separation of duties |
| Network | Shared VPC, custom mode, no default network | Peering does not give one firewall team |
| Connectivity to what stays | HA VPN, or Partner or Dedicated Interconnect if the PDF’s bandwidth is high. Two paths. Cloud Router BGP. DNS forwarding both ways. | A single tunnel, or the public internet for health payloads |
| Containers | Regional GKE. Autopilot unless they need DaemonSets or node SSH. | Zonal GKE, or a VM per customer |
| Clusters that remain outside Google Cloud | Attach them to a GKE Enterprise fleet. Config Sync and Policy Controller for the same constraints. | A different pipeline per site |
| Relational data that is still MySQL or SQL Server | Cloud SQL, regional HA, private IP, PITR, maintenance window | Spanner, unless the PDF requires global strong writes. It usually does not. |
| Partner API | Apigee in front of the stable interface. Quotas per insurer. | Giving each insurer a VPC peering |
| Privacy | Services that are in the BAA, CMEK if they must control keys, VPC Service Controls, Data Access or Admin Activity exported, no public database, no PHI in tickets | “Google is HIPAA so the bucket can be public” |
| Releases | Terraform for the landing zone. Cloud Build and Cloud Deploy for the app. Small rollout. Rollback. | Laptop kubectl |
| Alerts | SLO on availability and latency to an on-call channel | Email |
| Logs | Sink to a locked store in an audit project, retention as the PDF states | The default bucket only |
| Deadline | Rehost or replatform the customer-facing tier first. Do not rewrite the insurer link in the same weekend the lease ends. | A big-bang |

**Questions they ask, and the move**

| They ask | You answer |
| --- | --- |
| Raise availability | Add a zone (regional HA), not a second continent, unless the PDF says region loss |
| Speed up insurer onboarding | Apigee and a versioned API, not a new database |
| Stop outages from change | Pipeline, canary, Policy Controller, stop console edits |
| Who changed production | Admin Activity, exported |
| Connect the site that stays | Hybrid link sized to the traffic, private, redundant |
| Store images or documents | Cloud Storage with CMEK and a retention rule if the PDF has a retention number. Not the transactional database. |

## Cymbal Retail

**What the case is.** A fast-growing retailer with a large catalog. The transformation has tracks, not a blank page. One track generates or enriches catalog content and keeps a **human review** before publish. One track is conversational shopping and product discovery. One track modernizes the current stack and is explicit about cost. Expect an existing relational database and a document-shaped catalog. Read the cost and timeline numbers in the PDF and do not beat them.

**Landing zone**

| Need | Design | Why it is not the louder option |
| --- | --- | --- |
| Catalog system of record | The engine they already have, on Cloud SQL if it is MySQL or SQL Server. Private IP, HA if the PDF’s availability requires it. | BigQuery as the checkout database. Spanner if they are single-region and will not rewrite. |
| Document-shaped products | Firestore, or Firestore with MongoDB compatibility if the PDF says MongoDB and they want to stay document-oriented | Forcing a relational model in the same quarter as the cost cut |
| Enrichment | Document AI and Vision where the task is extract or label. A Gemini model where the task is prose. Write to a **draft** table. | Writing the model output straight to the live catalog |
| Human review | Pub/Sub or Cloud Tasks into a Cloud Run UI. Publish is a separate, audited step. | “The model is accurate enough” |
| Conversation and discovery | Conversational Agents, plus Agent Search or Vertex AI Search over the **approved** catalog only | Searching drafts, or a custom model trained from scratch |
| Web and API tier | Cloud Run if they do not need Kubernetes. GKE only if the PDF or the team standard requires the Kubernetes API. | A VM per service |
| Cost track | Scale to zero where cold start is acceptable, lifecycle or Autoclass on images, committed use only on the baseline you can measure, labels and a billing export | A GPU pool that stays hot for a batch that runs at night |
| Customer and card data | Store as little as possible. Tokenize or mask. Do not put PANs into prompts or logs. | Sending the warehouse to the model “for context” |
| Analytics | BigQuery on events and approved catalog snapshots. Not on the live checkout path. | Analysts querying the primary |

**Questions they ask, and the move**

| They ask | You answer |
| --- | --- |
| Generate descriptions | Gemini or a catalog model, then the review queue |
| Extract attributes from a supplier PDF | Document AI |
| A shopper asks for a product in a sentence | Conversational Agents plus search, grounded on the approved index |
| Cut cost without missing the availability number | Managed serverless or smaller baseline, not deleting HA |
| Keep a person in the loop | The draft path. Say it even if the other option is faster. |

## Altostrat Media

**What the case is.** A media company that is already on Google Cloud. Expect GKE, BigQuery, Cloud Run, and Cloud Run functions, plus a large library of audio and video. Generative AI is for summaries, metadata, recommendations, support, and moderation. Moderation that affects the public should be explainable and auditable. Storage cost of the archive matters. Do not redesign the estate they already run unless the PDF says that piece is failing.

**Landing zone**

| Need | Design | Why it is not the louder option |
| --- | --- | --- |
| Bytes of media | Cloud Storage. Standard or Autoclass for what is watched. Colder classes for the long tail. CDN or Media CDN for popular objects. | Filestore as the global library. A disk per title. |
| Already on GKE and Cloud Run | Keep the split. Functions or Cloud Run for an event. GKE for the service that needs the Kubernetes API. | Moving every function onto GKE “for consistency” |
| Transcode or metadata on upload | Eventarc or a bucket notification to Cloud Run functions or Dataflow | A permanent GPU VM |
| Summaries | Speech-to-Text or Video Intelligence for structure, a Gemini model for the prose, citations back to the asset id | One undifferentiated prompt with the whole file pasted in |
| Support bot | Conversational Agents grounded on their corpus, with a retrieval filter and sources | A bot that can read every internal bucket |
| Moderation | A model endpoint or a Gemini call, the decision logged, a person for the borderline, explainability when the PDF asks for an audit | A silent delete |
| Audience numbers | BigQuery, which they already have | A second warehouse |
| Training a large model | AI Hypercomputer only if the PDF says they train. Calling a hosted model is not a training cluster. | A reserved GPU “just in case” |
| Recommendations | The existing function path, or an endpoint with a traffic split if they are canarying a model | Rebuilding the app |

**Questions they ask, and the move**

| They ask | You answer |
| --- | --- |
| Cheaper archive, still opens quickly | A colder storage class or Autoclass. Archive is still millisecond access. Watch retrieval fees if they read it often. |
| New event-shaped work | Cloud Run functions, because that is already the pattern |
| Prove why a clip was blocked | Logs of the decision and the features or the citation. Not a bigger cluster. |
| Global viewers of a hot video | CDN in front of the bucket or the load balancer |

## KnightMotives Automotive

**What the case is.** A vehicle manufacturer. Electric, hybrid, and combustion lines, plus an autonomous program. Telemetry volume is high. They want a better driver and dealer experience, a way to share or sell data without leaking it, and partner APIs. European privacy and residency show up. Dealers should get new tools without a hardware rollout. Factories will not all move in one wave.

**Landing zone**

| Need | Design | Why it is not the louder option |
| --- | --- | --- |
| Telemetry ingest | Pub/Sub, then Dataflow. Hot operational reads and writes in Bigtable with a device-prefixed row key. Analytics in BigQuery. | Cloud SQL as the bus. A timestamp-first Bigtable key. |
| Training the driving model | AI Hypercomputer, GPUs or TPUs, a reservation if the run is large, Spot only for trials that can restart | The training job on the dealer-facing Cloud Run service |
| Inference in the app | A deployed endpoint or a smaller model, autoscaled, private | Leaving the training cluster on to serve |
| Dealer tool, no new PCs | Cloud Run or App Engine behind IAP, or a web app behind Identity-Aware Proxy | A VM in each dealership |
| Partner API | Apigee, a credential and a quota per partner | A shared service account password |
| Data product | Curated BigQuery datasets, column security, Analytics Hub or an approved exchange. Raw telemetry stays inside the perimeter. | A bucket with `allUsers`, or a weekly CSV to a partner |
| EU | Resource location organization policy, regional services, Assured Workloads if the PDF requires a controlled folder | A US multi-region bucket for EU vehicle data |
| Factories that stay | GKE Enterprise for clusters that move, Interconnect or HA VPN for sites that stay, DNS forwarding | Peering the plant into every project |
| Identity | Workforce identity, groups, no shared SSH | A jump box on the public internet |
| Dealer and vehicle PII | Sensitive Data Protection before a broad analyst group or a model sees free text | “It is only telemetry” |

**Questions they ask, and the move**

| They ask | You answer |
| --- | --- |
| Millions of small writes per minute | Pub/Sub and Bigtable, not a relational primary |
| A dealer in another country calls an API | Apigee and a private path if the data cannot cross the public internet. Residency still applies to where the data sits. |
| The plant stays for two years | Hybrid connectivity and a phased fleet. Do not block the customer app on the plant migration. |
| Monetize without giving the raw feed away | A governed dataset and an API. Not a replica of the lake. |

## Drill you should be able to do closed-book

Set a timer for 20 minutes per company. Write, without the PDF:

1. The availability or process constraint
2. The system you will not migrate
3. Compute, data, network, identity, AI, and the release path
4. Two answers you will reject and the sentence they violate

Then open the official PDF and strike every sentence you invented. An invented constraint is how these questions are lost.

## Sample case questions

**1.** EHR’s customer tier is 99.9% and an insurer system must stay in colocation. Which change is appropriate?

A. Multi-region Spanner and a cutover of the insurer system this week.
B. Regional HA for the customer tier, and a redundant private link to the system that stays.
C. One zonal VM and a snapshot.
D. BigQuery as the chart database of record.

Answer: B.

**2.** Cymbal wants generated catalog text. The case says a person approves it. Where does the model write?

A. The production table, immediately.
B. A draft queue, and publish is a separate step.
C. A public bucket.
D. The analyst’s laptop.

Answer: B.

**3.** Altostrat already processes uploads with Cloud Run functions. A new metadata task is the same shape. What do you extend?

A. A new GKE cluster per task.
B. The existing event path.
C. Filestore mounted on a VM.
D. A multi-region SQL Server.

Answer: B.

**4.** KnightMotives telemetry is a high-rate device stream. Which store is the operational path?

A. Bigtable, key starting with the device, with Pub/Sub in front.
B. One Cloud SQL instance.
C. A timestamp as the first Bigtable key component.
D. Firestore security rules as the ingest buffer.

Answer: A.
