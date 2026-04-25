# Requirement Clarifications — Well Production Monitoring & Allocation
**Module**: well-production  
**Conducted by**: AIKit — Review Kit (@review-clarifier)  
**Date**: 2026-04-25  
**Mode**: Automated BA/Architect Requirement Clarification  

---

## Category A — Architecture & Deployment

**Q-A1**: Should the system be built as microservices or a modular monolith, given it is a greenfield system with a single delivery team?  
**Resolution**: **Modular monolith** with internal domain module boundaries (DataAcquisition, AllocationEngine, WellTest, Downtime, RegulatoryReporting, Dashboards, Foundation). This reduces operational complexity for the initial release team. Modules are decomposed into independently deployable services only if load or team growth demands it. The API layer is RESTful (HTTP/JSON) with async event-driven patterns for ingestion and notifications.

**Q-A2**: Is Azure Kubernetes Service (AKS) the target deployment platform, or Azure App Service?  
**Resolution**: **AKS** — the system requires background workers (SCADA poll scheduler, allocation calculation runner, offline sync processor, notification dispatcher) which benefit from sidecar containers and Kubernetes scheduling. AKS on Azure West US 2.

**Q-A3**: Does "8-hour local buffer during PI outages" mean buffering on the cloud-hosted ingest service, or a local edge device buffer at the platform/field?  
**Resolution**: The buffer is on the **cloud-hosted Data Acquisition Service** (in-memory + Azure Storage fallback) since Permian Basin has no site server (ASM-004). For the offshore platforms, the PI Historian itself provides buffering; WPMA's 8-hour buffer applies to the cloud ingestion service recovering from its own transient faults.

---

## Category B — Data & Storage

**Q-B1**: Should 1-minute SCADA tag data (340 wells × ~10 tags × 1-minute) be stored in PostgreSQL or a dedicated time-series store?  
**Resolution**: **Azure Data Explorer (ADX)** for all raw time-series tag data (SCADA readings). PostgreSQL (Azure Database for PostgreSQL Flexible Server) for all transactional data: well tests, allocations, downtime events, regulatory reports, user/role records, audit log. This separation prevents PostgreSQL from handling time-series write load (~5M rows/day online, 2-year retention).

**Q-B2**: Is the "Snowflake ELT export" for raw tag data or aggregated production data?  
**Resolution**: **Daily aggregated production data only** (daily well-level volumes, allocations, downtime summaries) — not raw 1-minute tag data. Raw tag data stays in ADX. This keeps Snowflake export manageable (~340 rows/well/day).

**Q-B3**: Is the stock tank volume (post-shrinkage, BR-005) stored separately in every allocation record, or only in the monthly export?  
**Resolution**: Both gross separator volumes **and** stock tank barrel (STB) equivalents must be stored on every allocation record. The shrinkage factor per well/reservoir is configured in Well Master Data and applied at allocation calculation time.

**Q-B4**: For LACT tank gauge readings (FR-004) — is this an independent volume measurement that replaces the separator-based allocation, or a reconciliation check?  
**Resolution**: **Reconciliation check only**. Separator-based allocation is the primary method. LACT dip readings provide the custody transfer (fiscal) volume. If the LACT volume differs from the separator total by more than ±1% (configurable), the system raises a "LACT Discrepancy" alert. No automatic adjustment; engineer must investigate.

---

## Category C — Functional Behaviour

**Q-C1**: What is the formula for "on-stream efficiency" (OSE) shown in the dashboard (FR-022)?  
**Resolution**: `OSE (%) = (Actual_Production_Hours / Total_Hours_in_Period) × 100` per well. Field/platform OSE is the production-weighted average across all wells in scope. "Actual production hours" = total hours in period minus downtime hours.

**Q-C2**: For the "top 5 wells by deferred production" KPI (FR-022), is this month-to-date or rolling 30 days?  
**Resolution**: **Month-to-date** (calendar month, current period). The dashboard also provides a toggle to switch to rolling 30-day view.

**Q-C3**: FR-009 blocks finalization if allocation vs. measured diff > ±0.5%. Is this enforced at the individual separator level or at field total level?  
**Resolution**: **Individual separator/allocation group level**. Each allocation group (separator) must reconcile within ±0.5% before the group can be marked finalized. Overall field finalization requires all allocation groups finalized.

**Q-C4**: Can a Field Operator view other operators' downtime events, or only their own assigned wells?  
**Resolution**: Field Operators see **only wells assigned to them** (by platform/field). Production Engineers and above see all wells in their asset scope. Admins see everything. This is enforced via RBAC + asset scope filtering.

**Q-C5**: When a well test is rejected (WF-003 Alt-2), must the operator start a completely new test record, or can they edit and resubmit the same record?  
**Resolution**: The original test record is **immutable once submitted**. Rejection creates a new test request linked to the original (parent reference). This preserves audit trail integrity.

**Q-C6**: The "decline curve view" (FR-024) — does the system maintain the type curve, or is it imported from an external source?  
**Resolution**: The type curve is **imported from the reservoir model** (CSV import per well) and stored in WPMA. The Reservoir Engineer uploads/updates type curves via the well administration screen. WPMA does not compute type curves.

**Q-C7**: Does the VFM stub API (FR-007, Method 3) need to expose a real endpoint or just be a disabled option in the UI?  
**Resolution**: **Real stub endpoint**: `POST /api/v1/allocation/vfm` that returns `501 Not Implemented` with a JSON body indicating "Virtual Flow Metering not yet implemented — scheduled for Phase 2." The UI shows the option as greyed-out with tooltip "Coming in Phase 2."

---

## Category D — Integrations

**Q-D1**: For SAP PM integration — what specific data objects flow in each direction?  
**Resolution**:  
- **Inbound (SAP PM → WPMA)**: Maintenance notifications (PM01) and work orders (PM02) for wellhead equipment; workover and intervention order numbers; planned maintenance schedule. Batch daily at 02:00 UTC.  
- **Outbound (WPMA → SAP PM)**: Downtime event records (when category = "Planned maintenance" or "Well intervention") as PM functional location notifications. Daily batch at 03:00 UTC.

**Q-D2**: For BSEE eFAST SFTP upload — is the file a specific CSV format, or a structured XML/JSON?  
**Resolution**: BSEE eFAST accepts **CSV with fixed column layout** per MMS-146 April 2025 specification. The file is placed in the SFTP drop folder; eFAST processes it asynchronously and emails a confirmation. WPMA must store the SFTP transfer confirmation reference.

**Q-D3**: Texas RRC v3.2 REST API — is authentication token-based or certificate-based?  
**Resolution**: The RRC API uses **OAuth 2.0 client credentials** (client ID + secret stored in Azure Key Vault). Token is cached and refreshed before expiry.

---

## Category E — Security & Compliance

**Q-E1**: Are the 7 RBAC roles mutually exclusive, or can a user hold multiple roles?  
**Resolution**: Users **may hold multiple roles** (e.g., a Lead Engineer may also have the Production Engineer role). Permissions are additive (union). System Administrator role is always exclusive — it cannot be combined with operational roles.

**Q-E2**: Audit log (NFR-007) — does the 7-year retention apply to the primary PostgreSQL store, or is it archived to cold storage?  
**Resolution**: Audit log stays in PostgreSQL for **2 years** (hot), then moves to **Azure Blob Storage (cold)** for years 3–7. The application's audit log query UI shows up to 2 years. Older records are retrievable via a separate admin export tool. Both tiers count toward the 7-year retention commitment.

**Q-E3**: Is there a requirement for data residency (all data must stay in Azure West US 2)?  
**Resolution**: **Yes** — confirmed per ASM-004. All data stores must reside in Azure West US 2 region. Backup and disaster recovery replication may use Azure West US 3 as the paired region.

---

## Category F — UI/UX

**Q-F1**: Should the production dashboard be the default landing page after login, or a module selector?  
**Resolution**: The **production KPI dashboard** is the default landing page for Production Engineers, Lead Engineers, and VP Operations. Field Operators land on the **Well Test / Data Entry** screen. Regulatory Analysts land on the **Regulatory Reports** screen.

**Q-F2**: The offline mobile app (FR-012) — should it be a native app distributed via MDM, or a Progressive Web App (PWA)?  
**Resolution**: **React Native app** distributed via company MDM (Intune) to iOS and Android devices. PWA was considered but rejected because PWA offline storage limits are insufficient for month-to-date well test history. The app targets iOS 17+ and Android 14+ per ASM-003.

**Q-F3**: Are charts in the dashboard rendered on the server (SSR) or client-side?  
**Resolution**: **Client-side rendering** using Apache ECharts (React wrapper). The API delivers pre-aggregated data; charts render entirely in browser. This keeps API payloads small and allows interactive drill-down without round trips.

---

*All clarifications resolved by AIKit Review Kit. No open items remain.*
