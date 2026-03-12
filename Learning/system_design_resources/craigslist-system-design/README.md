# Craigslist System Design

> A comprehensive system design for a Craigslist-like classified advertisements platform, architected on **Google Cloud Platform (GCP)**.

---

## Table of Contents

| # | Section | File |
|---|---------|------|
| 1 | Functional & Non-Functional Requirements | [01-requirements.md](01-requirements.md) |
| 2 | Traffic Estimation & Data Calculations | [02-traffic-estimation.md](02-traffic-estimation.md) |
| 3 | API Design | [03-api-design.md](03-api-design.md) |
| 4 | Database Design | [04-database-design.md](04-database-design.md) |
| 5 | High-Level Architecture (GCP) | [05-high-level-architecture.md](05-high-level-architecture.md) |
| 6 | Detailed Component Design | [06-detailed-components.md](06-detailed-components.md) |
| 7 | Trade-off Discussion | [07-tradeoffs.md](07-tradeoffs.md) |
| 8 | Failure Scenario Discussion | [08-failure-scenarios.md](08-failure-scenarios.md) |
| 9 | Sequence Diagrams & Request Flows | [09-sequence-diagrams.md](09-sequence-diagrams.md) |

---

## System at a Glance

### What is Craigslist?
Craigslist is a **classified advertisements platform** where users can post and browse listings across categories:
- Housing (rentals, sales)
- Jobs
- For Sale (goods, furniture, electronics)
- Services
- Community (events, activities)
- Personal ads

### Key Design Goals
- Handle **50M+ monthly active users**
- Support **1M+ new listings/day**
- Enable **full-text geo-aware search** across 700+ cities
- Serve **read-heavy** workloads (read:write ≈ 100:1)
- Ensure **high availability** (99.99% uptime target)

---

## GCP Architecture Overview

```
Users → Cloud Armor → Cloud Load Balancing → Cloud CDN
                                          ↓
                              API Gateway (Apigee)
                                          ↓
                   ┌──────────────────────────────────────┐
                   │         GKE (Microservices)           │
                   │  User  │ Listing │ Search │ Notify   │
                   └──────────────────────────────────────┘
                        ↓           ↓         ↓
              Cloud SQL (PostgreSQL) │  Elasticsearch
              Cloud Spanner          │  Memorystore (Redis)
              Cloud Storage (Images) │  Cloud Pub/Sub
              BigQuery (Analytics)   │  Cloud Tasks
```

---

## Key GCP Services Used

| Layer | GCP Service | Purpose |
|-------|-------------|---------|
| Edge | Cloud Armor | DDoS/WAF protection |
| Edge | Cloud CDN | Static assets, listing images |
| Networking | Cloud Load Balancing | Global L7 load balancing |
| API | Apigee API Gateway | API management, rate limiting |
| Compute | Google Kubernetes Engine (GKE) | Microservices orchestration |
| Auth | Firebase Authentication | User auth, OAuth |
| Database | Cloud SQL (PostgreSQL) | Users, listings metadata |
| Database | Cloud Spanner | Global listings, transactions |
| Cache | Memorystore (Redis) | Session cache, hot listings |
| Search | Elasticsearch on GCE | Full-text + geo search |
| Storage | Cloud Storage | Images, attachments |
| Messaging | Cloud Pub/Sub | Event streaming, notifications |
| Tasks | Cloud Tasks | Async jobs, email queue |
| Analytics | BigQuery | Search analytics, reporting |
| Monitoring | Cloud Monitoring + Logging | Observability |
| Secrets | Secret Manager | API keys, credentials |

---

## How to Use This Design

1. Start with **Requirements** to understand scope
2. Use **Traffic Estimation** to justify design choices
3. Review **API Design** for interface contracts
4. Study **Database Design** for data modeling
5. Understand **Architecture** for component relationships
6. Deep dive **Components** for implementation details
7. Examine **Trade-offs** for decision rationale
8. Prepare for **Failure Scenarios** in interviews

---

*Designed for interview preparation and learning purposes. Architecture targets Google Cloud Platform.*
