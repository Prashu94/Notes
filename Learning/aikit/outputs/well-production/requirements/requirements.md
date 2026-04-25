# Requirements — Well Production Monitoring & Allocation System
**Module**: well-production  
**Source**: well-production-requirements.md  
**Parsed by**: AIKit — Requirement Kit  
**Date**: 2026-04-25  
**Status**: Parsed

---

## Module Summary

| Field | Value |
|-------|-------|
| Client | Meridian Energy Corp |
| Project | WellTrack Pro |
| Module Type | Greenfield |
| Asset Scope | 340 active wells — 3 offshore platforms (Alpha, Bravo, Charlie) + 2 onshore fields (Permian Basin West, Gulf Coast South) |
| Primary Problem | 4–6 hour production reporting delay, allocation errors, regulatory non-compliance |

---

## Section 1 — Business Objectives

| # | Objective | Measurable Target |
|---|-----------|-------------------|
| BO-001 | Reduce production reporting cycle | From 6 hours → under 15 minutes |
| BO-002 | Achieve hydrocarbon allocation accuracy across commingled wells | 99.5% accuracy |
| BO-003 | Automate monthly regulatory submissions | BSEE (offshore) and RRC Texas (onshore) |
| BO-004 | Enable rapid anomaly detection | Underperforming well identified within 30 minutes of anomaly |
| BO-005 | Replace spreadsheet-based trackers | 14 Excel trackers → single source of truth |

---

## Section 2 — Scope

### In Scope
- Real-time data ingestion from SCADA and DCS (PI System / Emerson DeltaV)
- Daily, monthly, annual production allocation by well, reservoir, commodity (oil, gas, water, condensate)
- Production performance dashboards and KPI tracking
- Well test management and utilisation calculations
- Regulatory report generation: BSEE Form MMS-146, Texas RRC PR-2
- Downtime event capture and loss accounting
- Integration with SAP PM for maintenance correlation

### Out of Scope
- Reservoir simulation or modelling
- Drilling planning
- Financial accounting or revenue allocation

---

## Section 3 — Stakeholders

| Role | Department | System Access Level | Primary Concern |
|------|-----------|---------------------|-----------------|
| Production Engineer | Operations | Full operational read/write | Daily well performance monitoring |
| Field Operator | Field Operations | Data entry + well test submission | Gauge entry, downtime logging |
| Production Accountant | Finance | Allocation review + certification | Monthly allocation accuracy |
| Regulatory Affairs Analyst | HSE | Regulatory reports | BSEE / RRC submission |
| Reservoir Engineer | Subsurface | Read + well model updates | Production trends, GOR/WC anomalies |
| IT Operations | IT | System administration | Integration health, availability |
| VP Operations | Leadership | Read + approval | Monthly report sign-off |

---

## Section 4 — Functional Requirements

### FR-4.1 Data Acquisition

| ID | Description | Priority | Notes |
|----|-------------|----------|-------|
| FR-001 | Continuously poll PI OSIsoft historian for well-level tags at configurable intervals (default 1 min): WHP_TBG, WHP_CSG, choke position, flowline temperature, separator inlet P/T, separator oil/gas/water outlet flow rates | Must Have | PI Web API (REST) |
| FR-002 | Manual data entry for ~40 non-SCADA Permian wells. Entries carry "ESTIMATED" flag in all reports | Must Have | Offline-capable entry |
| FR-003 | Detect and flag data gaps > 15 min as "Communication Loss." Back-fill 15 min–4 hours with last-known-good value. Gaps > 4 hours require manual review + approval before allocation | Must Have | See BR-007, BR-008 |
| FR-004 | Accept daily LACT tank gauge dip readings (once per 24h cycle at 06:00 local time) | Must Have | Custody transfer reconciliation |

### FR-4.2 Allocation Engine

| ID | Description | Priority | Notes |
|----|-------------|----------|-------|
| FR-005 | Allocate separator volumes to commingled wells via well test ratio method: `Well_i = (Well_i_Test_Rate / Σ_Test_Rates) × Sep_Volume` | Must Have | Primary allocation method |
| FR-006 | Update well test ratios within 24 hours of Production Engineer approval | Must Have | See BR-009 |
| FR-007 | Support three allocation methodologies per allocation point: (1) Well test ratio [default], (2) Back-allocation from metered streams, (3) Virtual flow metering [stub API, future phase] | Must Have | Method 3 stub only |
| FR-008 | Recalculate allocations retroactively up to 90 days when test ratios change. Log: change reason, approver, timestamp | Must Have | See BR-010 |
| FR-009 | Prevent monthly allocation finalisation if: missing/expired well test, total diff vs measured > ±0.5%, unresolved data gap events | Must Have | See BR-011 |

### FR-4.3 Well Test Management

| ID | Description | Priority | Notes |
|----|-------------|----------|-------|
| FR-010 | Field operators submit well test records: test date, duration (min 6h oil / 4h gas), choke size, separator gauge readings (oil/gas/water), stabilisation confirmation | Must Have | See BR-012 |
| FR-011 | Auto-calculate test rates (BOPD, MMSCFD, BWPD) and GOR/WC on submission | Must Have | Derived calculations |
| FR-012 | Mobile-responsive offline-first well test form for iOS 17+ / Android 14+. Syncs when connectivity restores. Required for Permian Basin field (intermittent 4G) | Must Have | AC-001: sync within 60 seconds |
| FR-013 | Two-level approval: L1 — Production Engineer; L2 — Lead Production Engineer (required when test rate deviates >20% from prior test) | Must Have | See BR-013 |

### FR-4.4 Downtime & Loss Accounting

| ID | Description | Priority | Notes |
|----|-------------|----------|-------|
| FR-014 | Log downtime events: well ID, start datetime, end datetime (or "ongoing"), category, sub-category, estimated production loss (system-calculated), freetext comment | Must Have | |
| FR-015 | Downtime categories: Mechanical failure, Process upset, Planned maintenance, Well intervention/workover, Third-party constraint, Regulatory/environmental, Weather/force majeure, Unclassified (comment required) | Must Have | 8 top-level categories |
| FR-016 | Calculate deferred production (BBL and MMSCF) per downtime event using approved test rate at time of event | Must Have | |
| FR-017 | Monthly downtime report exportable as Excel (.xlsx) and PDF; summarised by well, category, platform/field | Should Have | |

### FR-4.5 Regulatory Reporting

| ID | Description | Priority | Notes |
|----|-------------|----------|-------|
| FR-018 | Auto-populate BSEE Form MMS-146 (Monthly Production Report) per offshore lease from finalised monthly allocations | Must Have | April 2025 schema revision |
| FR-019 | Issue email notifications to Regulatory Affairs Analyst and VP Operations 10 days and 3 days before BSEE 15th-of-month deadline if report not yet submitted | Must Have | |
| FR-020 | Generate Texas RRC PR-2 (Purchaser Report) for all Texas onshore wells; map to RRC Oil and Gas Division electronic filing schema v3.2 | Must Have | |
| FR-021 | Lock regulatory reports after submission. Amendments create a new versioned amendment record with justification | Must Have | See BR-014 |

### FR-4.6 Dashboards and Reporting

| ID | Description | Priority | Notes |
|----|-------------|----------|-------|
| FR-022 | Real-time production dashboard KPIs: total field production (BOPD/MMSCFD/BWPD) current 24h, on-stream efficiency per platform/fleet, top 5 wells by production, top 5 wells by deferred production (current month), well count by status | Must Have | NFR-001: refresh < 10 seconds |
| FR-023 | All dashboard charts exportable to PNG; underlying data exportable to CSV | Should Have | |
| FR-024 | Well-level decline curve view: historical production overlaid with approved type curve | Should Have | |

---

## Section 5 — Non-Functional Requirements

### NFR-5.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | Dashboard KPI refresh on page open | < 10 seconds |
| NFR-002 | Full-month allocation recalculation (31 days, up to 340 wells) | < 90 seconds |
| NFR-003 | Concurrent user load | 150 users; page load < 3 seconds |

### NFR-5.2 Security

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-004 | Authentication via Azure Active Directory SAML 2.0 SSO | No local accounts |
| NFR-005 | RBAC enforced for all roles | Field Operator, Production Engineer, Lead Engineer, Production Accountant, Regulatory Analyst, Read-Only, System Administrator |
| NFR-006 | Data in transit encryption | TLS 1.2 or higher |
| NFR-007 | Audit trail for all data modifications (user, timestamp, old/new value) | Retained 7 years |

### NFR-5.3 Availability and DR

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-008 | System uptime | 99.5% monthly (max 4h planned maintenance, off-peak) |
| NFR-009 | Recovery Time Objective / Recovery Point Objective | RTO: 4h / RPO: 1h |
| NFR-010 | PI ingestion pipeline local buffer during outages | 8 hours; replay without gaps on restore |

### NFR-5.4 Integrations

| System | Direction | Method | Frequency |
|--------|-----------|--------|-----------|
| OSIsoft PI Historian | Inbound | PI Web API (REST) | 1-minute poll |
| Emerson DeltaV (Bravo platform) | Inbound | OPC-UA | 1-minute poll |
| SAP PM | Inbound/Outbound | RFC BAPI | Daily batch |
| Azure Active Directory | Inbound | SAML 2.0 | On-demand (auth) |
| BSEE eFAST Portal | Outbound | SFTP / CSV | Monthly |
| Texas RRC Electronic Filing | Outbound | REST API (RRC v3.2) | Monthly |
| Company Data Warehouse (Snowflake) | Outbound | JDBC / scheduled ELT | Daily |

---

## Section 6 — Data Retention

| Data Type | Online Retention | Archive |
|-----------|-----------------|---------|
| Real-time tag data (1-minute) | 2 years | 10 years cold storage |
| Daily/monthly aggregated production | 25 years | Regulatory requirement |
| Regulatory submission records | Permanent | — |
| Audit log entries | 7 years minimum | — |

---

## Section 7 — Assumptions and Constraints

| # | Statement |
|---|-----------|
| ASM-001 | PI System (OSIsoft) licenses already in place; WPMA consumes existing PI Web API endpoint |
| ASM-002 | Initial release targets Chrome 120+ and Edge 120+; Internet Explorer not supported |
| ASM-003 | Mobile support limited to iOS 17+ and Android 14+ |
| ASM-004 | Permian Basin field: no site server; all cloud-hosted on Azure West US 2 |
| ASM-005 | BSEE Form MMS-146 schema frozen at April 2025 revision for initial release |

---

## Section 8 — High-Level Acceptance Criteria

| ID | Criterion |
|----|-----------|
| AC-001 | Field operator logs a well test offline; syncs within 60 seconds on connectivity restore |
| AC-002 | Monthly allocation report for all 340 wells available within 15 minutes of month-end midnight |
| AC-003 | BSEE MMS-146 matches manually calculated values within ±0.5% for 3 consecutive months parallel run |
| AC-004 | 150 concurrent users access dashboards simultaneously with < 3 second load time |
| AC-005 | Audit trail captures 100% of production and allocation changes during test period |
