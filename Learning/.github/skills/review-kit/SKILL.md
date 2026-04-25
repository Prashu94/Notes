---
name: "review-kit"
description: "AIKit review and story generation skill. Use when conducting BA/architect requirement clarification, selecting tech stack, and generating Epics, Features, User Stories with BDD acceptance criteria. Invoked by review-kit agent. Prerequisite: requirement-kit completed."
argument-hint: "module=<module-id>"
---

# Review Kit Skill

Transforms requirement artifacts into actionable Agile work items and confirms technology decisions.

## When to Use
- After requirement-kit completes
- When BA/architect need to clarify requirements interactively
- When generating Epics, Features, Stories with acceptance criteria
- When selecting tech stack for the module

## Procedure

### Step 1 — Read Artifacts
From `aikit/config.yaml` paths, read:
- `requirements.md`, `BRD.md`, `business-rules.md`, `workflows.md`

### Step 2 — Clarification Session
Invoke `@review-clarifier` (mode: requirement-clarification).
Present questions category by category. Wait for user answers.
Write answers to `clarifications.md`.

### Step 3 — Tech Stack (ALWAYS interactive — user must choose)
**MANDATORY**: Always present tech stack options to the user for explicit selection, even if technology fields in config.yaml are already filled. Never auto-decide the tech stack.

Procedure:
1. Read `aikit/config.yaml` technology fields and the [Tech Stack Guide](./references/tech-stack-guide.md).
2. Present the user with a numbered menu of options for **each** of the following layers, one at a time. Wait for the user's answer before presenting the next layer:
   - **Backend framework**: e.g. Spring Boot / FastAPI / NestJS / Express.js / Django REST / ASP.NET Core — show pros/cons from the Tech Stack Guide for the top 3 most relevant to this module
   - **Frontend framework**: React / Angular / Vue.js — note MFE vs SPA recommendation
   - **Mobile** (if mobile requirement exists in BRD): React Native / Flutter / PWA / Native (Swift+Kotlin) — show offline capability comparison
   - **Primary database**: PostgreSQL / MySQL / MSSQL / MongoDB — focus on top 2–3 relevant choices
   - **Time-series / special store** (if high-frequency data ingestion exists): ADX / InfluxDB / TimescaleDB / none
   - **Cache**: Redis / Memcached / none
   - **Message broker** (if async/event-driven exists in BRD): Azure Service Bus / RabbitMQ / Kafka / AWS SQS / none
   - **Cloud / deployment**: Azure / AWS / GCP / on-premise
3. After each user answer, confirm the choice and acknowledge any implications (e.g., "Spring Boot chosen — SAP RFC BAPI integration will use the SAP JCo library").
4. Once all layers are answered, display a **full stack summary table** and ask the user: "Confirm this tech stack? (yes / edit [layer name])"
5. On confirmation, record all decisions in `tech-stack.md` and update `config.yaml` technology fields.

**Do NOT skip this step or infer choices silently. If the user has not answered, pause and ask.**

### Step 4 — Generate Epics
Invoke `@review-stories` (mode: generate-epics).
Write to `epics.md`. Aim for 3–7 epics per module.

### Step 5 — Generate Features (Queued)
Queue: all Epics. Batch: 2 epics per call.
Invoke `@review-stories` (mode: generate-features) per batch.
Append to `features.md`.

### Step 6 — Generate Stories (Queued)
Queue: all Features. Batch: 3 features per call.
Invoke `@review-stories` (mode: generate-stories) per batch.
Append to `stories.md`.

### Step 7 — Coverage Check
Every FR-NNN and WF-NNN must map to at least one story.
Report gaps.

### Step 8 — Complete
Update config.yaml, stage-tracker, audit.log.

## Reference Files
- [Epics, Features & Stories Template](./references/epics-features-stories-template.md)
- [Tech Stack Guide](./references/tech-stack-guide.md)
