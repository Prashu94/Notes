# Technology Stack — Well Production Monitoring & Allocation
**Module**: well-production  
**Decided by**: AIKit — Review Kit (@review-clarifier, mode: tech-stack)  
**Date**: 2026-04-25  
**Cloud**: Azure (mandated — company standard, Azure West US 2)  

---

## Decision Summary

| Layer | Technology | Version / Tier | Rationale |
|-------|-----------|----------------|-----------|
| **Backend** | ASP.NET Core (.NET 8) | .NET 8 LTS | Azure-native, enterprise domain complexity, strong typing for financial/regulatory calculations, excellent Azure SDK support, RFC BAPI adapters via NWRFC |
| **Frontend** | React + TypeScript | React 18, TS 5.x | Large charting ecosystem, component flexibility, team expertise |
| **Mobile** | React Native (Expo managed) | Expo SDK 51+ | Code sharing with web (business logic), offline-first via WatermelonDB (SQLite), MDM deployment via Intune, iOS 17+ / Android 14+ |
| **Primary DB** | Azure Database for PostgreSQL Flexible Server | PostgreSQL 16 | Complex relational queries for allocation, well tests, downtime, regulatory records; JSONB for flexible metadata; excellent extension support |
| **Time-series DB** | Azure Data Explorer (ADX) | Standard tier | Purpose-built for 1-minute SCADA telemetry at 340-well scale (~5M rows/day); KQL query performance for dashboard aggregations |
| **Cache** | Azure Cache for Redis | Standard C1 | Dashboard KPI cache, session store, distributed lock for allocation calculation |
| **Ingestion bus** | Azure Event Hub | Standard tier | High-throughput SCADA ingestion pipeline (PI + DeltaV); partitioned by well ID |
| **Workflow bus** | Azure Service Bus | Standard tier | Well test approval notifications, allocation completion events, regulatory deadline reminders |
| **Auth** | Azure Active Directory | Enterprise SSO | SAML 2.0 SSO (mandated, NFR-004); groups mapped to WPMA RBAC roles |
| **Mobile offline** | WatermelonDB (SQLite) | Latest stable | Offline-first well test storage on device; sync via delta API on reconnect |
| **Charts** | Apache ECharts (echarts-for-react) | Latest stable | Time-series, decline curves, KPI tiles; client-side rendering; large dataset performance |
| **API style** | REST (JSON) + OpenAPI 3.0 | — | Standard industry practice; enables future third-party integrations |
| **Containerization** | Docker | — | All services containerized |
| **Orchestration** | Azure Kubernetes Service (AKS) | Latest stable | Hosts API, background workers, ingestion consumers; supports horizontal scaling |
| **API Gateway** | Azure API Management | Consumption tier | Rate limiting, SAML → JWT token exchange, versioning |
| **Secrets** | Azure Key Vault | Standard | PI API credentials, RRC OAuth client credentials, SAP connection strings |
| **Monitoring** | Azure Monitor + Application Insights | — | Distributed traces, performance metrics, alerts |
| **Blob storage** | Azure Blob Storage | Cool tier (audit archive) | BSEE/RRC submission files, audit log archive (years 3–7), type curve CSV uploads |
| **CI/CD** | Azure DevOps | — | Build pipelines, release pipelines, AKS deployment |

---

## Backend Detail

**Framework**: ASP.NET Core 8 (Minimal API + Controller hybrid — Minimal API for CRUD endpoints, Controllers for complex domain operations)  
**Language**: C# 12  
**Architecture pattern**: Modular Monolith with vertical slice architecture per domain module:
```
WellTrackPro/
  src/
    DataAcquisition/       ← PI/DeltaV polling, gap detection, manual entry
    AllocationEngine/      ← Calculation, finalization, retroactive corrections
    WellTestManagement/    ← Test records, approval workflows
    DowntimeAccounting/    ← Event logging, deferred production
    RegulatoryReporting/   ← MMS-146, RRC PR-2, submission, notifications
    Dashboards/            ← KPI aggregation, anomaly detection
    Foundation/            ← Auth, RBAC, audit, well master data, admin
    Infrastructure/        ← ADX client, Event Hub consumer, Service Bus, Redis, SAP adapter
```

**Key packages**:
- `Microsoft.Identity.Web` — Azure AD SAML/JWT validation
- `NetTopologySuite` — None needed; standard libraries for allocation math
- `Quartz.NET` — SCADA poll scheduler, daily ELT scheduler
- `MassTransit` (Service Bus) — Workflow event bus abstraction
- `FluentValidation` — Domain validation (well test rules, allocation rules)
- `Polly` — Resilience policies (retry, circuit breaker) for PI API, DeltaV, SAP calls
- `EPPlus` — Excel export for downtime reports
- `iTextSharp` / `QuestPDF` — PDF export
- `Kusto.Data` — Azure Data Explorer .NET SDK
- `Microsoft.Azure.EventHubs` / `Azure.Messaging.EventHubs` — Event Hub consumer

---

## Frontend Detail

**Framework**: React 18 + TypeScript 5  
**State management**: Zustand (lightweight, sufficient for SPA without Redux complexity)  
**Routing**: React Router v6  
**UI library**: Ant Design 5 (enterprise data-dense tables, forms, approval workflows, notifications)  
**Charts**: Apache ECharts via `echarts-for-react` (time-series, bar, line, decline curves)  
**Forms**: React Hook Form + Zod (type-safe validation)  
**API client**: TanStack Query (React Query v5) — server state caching, background refresh for dashboard KPIs  
**Auth**: `@azure/msal-react` (MSAL for Azure AD SSO, token management)  
**PWA**: Not applicable (native mobile app chosen for offline well test requirement)  
**Build**: Vite + TypeScript  
**Testing**: Vitest + React Testing Library  

---

## Mobile Detail

**Framework**: React Native (Expo Managed Workflow)  
**Target**: iOS 17+, Android 14+ (distributed via Intune MDM)  
**Offline storage**: WatermelonDB (SQLite-based, high-performance local DB) — stores well test drafts, pending submissions queue, reference data (well list, choke sizes)  
**Sync mechanism**: Delta sync API (`POST /api/v1/sync/well-tests`) — uploads queued submissions and receives reference data updates. Sync triggered on: app foreground + network available. Target: sync within 60 seconds of connectivity restore (AC-001)  
**Auth**: Expo `expo-auth-session` + MSAL Azure AD  
**Network detection**: `@react-native-community/netinfo`  
**Push notifications**: Azure Notification Hubs → React Native notifications (for well test approval status)  

---

## Database Schema Strategy

| Database | Schemas / Namespaces | Purpose |
|----------|---------------------|---------|
| PostgreSQL | `wells` | Well master, allocation groups, type curves |
| PostgreSQL | `well_tests` | Test records, approvals, rate history |
| PostgreSQL | `allocation` | Monthly allocation records, finalization state |
| PostgreSQL | `downtime` | Events, categories, deferred production |
| PostgreSQL | `regulatory` | Report records, amendments, submissions |
| PostgreSQL | `foundation` | Users, roles, audit_log (2-year hot) |
| ADX | `WellProduction` DB | Raw 1-minute SCADA tag readings |
| ADX | `WellProduction` DB | Daily aggregated production volumes |
| Blob Storage | `audit-archive` | Audit log cold storage (years 3–7) |
| Blob Storage | `regulatory-submissions` | Submitted SFTP files, RRC payloads |
| Blob Storage | `type-curves` | Well type curve CSV imports |

---

## Integration Architecture

```
PI Historian ──(PI Web API REST, 1-min)──► [Data Acquisition Service]
DeltaV       ──(OPC-UA, 1-min)──────────► [Data Acquisition Service]
                                                    │
                                          Azure Event Hub
                                                    │
                                          [Time-series Consumer]
                                                    ▼
                                          Azure Data Explorer (ADX)
                                          
[WPMA API] ◄──(SAML 2.0)──► Azure AD
[WPMA API] ──(RFC BAPI, daily batch)──► SAP PM
[WPMA API] ──(JDBC/ELT, daily)────────► Snowflake
[WPMA API] ──(SFTP/CSV, monthly)──────► BSEE eFAST Portal
[WPMA API] ──(REST OAuth2, monthly)───► Texas RRC v3.2 API
[WPMA API] ──(Service Bus events)─────► Email Notifications (Azure Communication Services)
```

---

## Non-Functional Fit Validation

| NFR | Technology Solution |
|-----|---------------------|
| NFR-001 (Dashboard < 10s) | KPIs pre-aggregated into Redis cache; ADX KQL queries for current-day totals; React Query background refresh |
| NFR-002 (Allocation < 90s) | Allocation calculation runs as background AKS job; parallelized per allocation group; Redis distributed lock prevents concurrent runs |
| NFR-003 (150 concurrent users) | AKS horizontal pod autoscaling; Azure API Management rate limits; CDN for static assets |
| NFR-004 (Azure AD SAML 2.0) | `Microsoft.Identity.Web` + Azure AD Enterprise App registration |
| NFR-005 (RBAC 7 roles) | Claims-based authorization via Azure AD groups → ASP.NET Core policy-based auth |
| NFR-006 (TLS 1.2+) | AKS ingress with TLS termination; Azure API Management enforces TLS minimum version |
| NFR-007 (Audit 7 years) | PostgreSQL `foundation.audit_log` (2yr hot) → Azure Blob Storage lifecycle policy (yr 3–7 cold) |
| NFR-008 (99.5% uptime) | AKS multi-replica deployments (min 2 pods); Rolling deployments; Azure PostgreSQL High Availability (zone-redundant) |
| NFR-009 (RTO 4h / RPO 1h) | Azure PostgreSQL point-in-time restore (PITR 1h); AKS deployment manifests in GitOps repo (DevOps) |
| NFR-010 (8h PI buffer) | Data Acquisition Service in-process queue + Azure Storage Queue fallback during ADX outages |

---

## Technology Decisions — Open Items

None. All technology decisions resolved based on requirements, clarifications, and Azure constraint.
