# Business Requirements Document (BRD)
**Module**: well-production  
**Version**: 1.0  
**Date**: 2026-04-25  
**Prepared By**: AIKit — Requirement Kit  
**Status**: Draft  
**Client**: Meridian Energy Corp  
**Project**: WellTrack Pro  

---

## 1. Executive Summary

Meridian Energy Corp operates 340 active wells across three offshore platforms (Alpha, Bravo, Charlie) and two onshore fields (Permian Basin West, Gulf Coast South). The current production reporting process relies on manual data entry into disparate spreadsheets, causing 4–6 hour reporting delays, frequent hydrocarbon allocation errors, and regulatory non-compliance.

The Well Production Monitoring & Allocation (WPMA) system — **WellTrack Pro** — will provide real-time production data acquisition from SCADA/DCS systems, automated hydrocarbon allocation, well test management, production performance dashboards, downtime loss accounting, and automated regulatory report generation and submission for both BSEE (offshore) and Texas RRC (onshore) authorities.

This is a greenfield system hosted on Azure, replacing 14 Excel-based production trackers with a single authoritative data and reporting platform.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|---------------|
| BO-001 | Reduce production reporting cycle time | From 6 hours → under 15 minutes (AC-002) |
| BO-002 | Achieve high-accuracy hydrocarbon allocation | 99.5% accuracy across commingled wells |
| BO-003 | Automate statutory regulatory submissions | Zero manual form preparation for BSEE and RRC Texas |
| BO-004 | Enable rapid anomaly detection | Underperforming well identified within 30 minutes of occurrence (FR-022, WF-008) |
| BO-005 | Consolidate production data management | Replace 14 Excel trackers with one system |

---

## 3. Scope

### 3.1 In Scope

- Real-time data ingestion from PI OSIsoft (REST) and Emerson DeltaV OPC-UA
- Manual data entry for ~40 non-SCADA Permian Basin wells (offline-first mobile support)
- Daily, monthly, and annual production allocation: oil, gas, water, condensate
- Three allocation methodologies: well test ratio, back-allocation, VFM stub
- Well test management with two-level approval workflow and offline mobile form
- Downtime event capture, categorisation, and deferred production calculation
- Production dashboards with real-time KPIs (on-stream efficiency, top wells, decline curves)
- BSEE Form MMS-146 auto-population and SFTP submission to eFAST portal
- Texas RRC PR-2 Purchaser Report generation via RRC REST API v3.2
- Integration with SAP PM (well maintenance correlation, daily batch)
- Integration with Snowflake Data Warehouse (daily ELT)
- RBAC via Azure Active Directory (SAML 2.0 SSO)
- Full audit trail with 7-year retention

### 3.2 Out of Scope

- Reservoir simulation or reservoir modelling
- Drilling planning and well design
- Financial accounting or revenue/royalty allocation
- Virtual Flow Metering (VFM) implementation (API stub only in initial release)

---

## 4. Stakeholders

| Role | Department | Responsibility |
|------|-------------|----------------|
| Product Owner | Operations Leadership | Final decisions on scope and priorities |
| Business Analyst | Operations | Requirements Definition |
| Architect | IT | Technical design and integration |
| Production Engineer | Operations | Primary daily user; well monitoring and approval workflows |
| Field Operator | Field Operations | Well test submission, gauge entry, downtime logging |
| Production Accountant | Finance | Monthly allocation review and certification |
| Regulatory Affairs Analyst | HSE | BSEE and RRC report submission |
| Reservoir Engineer | Subsurface | Production trend analysis; GOR/WC alert review |
| IT Operations | IT | Integration health, system availability |
| VP Operations | Leadership | Monthly report approval; exception authorisations |
| QA | IT / Operations | Verification and parallel-run testing |

---

## 5. Functional Requirements

### 5.1 Data Acquisition

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-001 | Continuously poll PI OSIsoft historian for well-level tags (WHP_TBG, WHP_CSG, choke position, flowline temperature, separator inlet P/T, oil/gas/water outlet rates) at configurable intervals (default 1 minute) via PI Web API (REST) | Must Have | §5.1 |
| FR-002 | Manual data entry for ~40 non-SCADA Permian wells; entries flagged "ESTIMATED" in all reports | Must Have | §5.1, BR-015 |
| FR-003 | Detect and classify data gaps: < 15 min (normal), 15 min–4h (back-fill last known good + ESTIMATED flag), > 4h (Communication Loss event; block allocation pending manual review) | Must Have | §5.1, BR-007, BR-008 |
| FR-004 | Accept daily LACT tank gauge dip readings (once per 24h cycle at 06:00 local time) for custody transfer reconciliation | Must Have | §5.1 |

### 5.2 Allocation Engine

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-005 | Allocate separator volumes to commingled wells using well test ratio method: `Well_i = (Test_i / ΣTest) × Sep_Vol` | Must Have | §5.2 |
| FR-006 | Update well test ratios in engine within 24 hours of Production Engineer approval | Must Have | §5.2, BR-009 |
| FR-007 | Support 3 allocation methodologies per point: (1) well test ratio [default], (2) back-allocation from metered streams, (3) VFM [stub API, future] | Must Have | §5.2 |
| FR-008 | Retroactive allocation recalculation up to 90 days prior; log change reason, approver, timestamp | Must Have | §5.2, BR-010 |
| FR-009 | Block monthly allocation finalisation if: missing/expired well test, allocation vs. measured diff > ±0.5%, unresolved data gap event | Must Have | §5.2, BR-011 |

### 5.3 Well Test Management

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-010 | Field operator submits well test: date, duration (≥6h oil / ≥4h gas), choke size, separator readings, stabilisation confirmation | Must Have | §5.3, BR-012 |
| FR-011 | Auto-calculate test rates (BOPD, MMSCFD, BWPD) and GOR/WC on submission | Must Have | §5.3 |
| FR-012 | Offline-first mobile-responsive well test form for iOS 17+ / Android 14+; syncs within 60 seconds on connectivity restore | Must Have | §5.3, AC-001 |
| FR-013 | Two-level approval: L1 Production Engineer; L2 Lead Production Engineer required when rate deviation > 20% from prior test | Must Have | §5.3, BR-013 |

### 5.4 Downtime & Loss Accounting

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-014 | Log downtime events: well ID, start/end datetimes, category, sub-category, system-calculated production loss, freetext comment | Must Have | §5.4 |
| FR-015 | 8 downtime categories: Mechanical failure, Process upset, Planned maintenance, Well intervention, Third-party constraint, Regulatory/environmental, Weather/force majeure, Unclassified (comment required) | Must Have | §5.4, BR-018 |
| FR-016 | Calculate deferred production (BBL and MMSCF) per event using approved test rate at time of event | Must Have | §5.4, BR-017 |
| FR-017 | Monthly downtime report exportable as Excel (.xlsx) and PDF; summarised by well, category, platform/field | Should Have | §5.4 |

### 5.5 Regulatory Reporting

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-018 | Auto-populate BSEE Form MMS-146 (Monthly Production Report) per offshore lease from finalised allocations (April 2025 schema) | Must Have | §5.5 |
| FR-019 | Email notifications to Regulatory Affairs Analyst and VP Operations 10 days and 3 days before BSEE 15th-of-month deadline if report not submitted | Must Have | §5.5, BR-019 |
| FR-020 | Generate Texas RRC PR-2 Purchaser Report for Texas onshore wells; map to RRC Oil and Gas Division electronic filing schema v3.2 | Must Have | §5.5 |
| FR-021 | Lock regulatory reports after submission; amendments create new versioned record with justification | Must Have | §5.5, BR-014 |

### 5.6 Dashboards and Reporting

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-022 | Real-time dashboard KPIs: total field production (BOPD/MMSCFD/BWPD 24h), on-stream efficiency (% per field + total), top 5 wells by production, top 5 by deferred production (current month), well count by status | Must Have | §5.6, NFR-001 |
| FR-023 | All dashboard charts export to PNG; underlying data export to CSV | Should Have | §5.6 |
| FR-024 | Well-level decline curve view: historical production overlaid with approved type curve | Should Have | §5.6 |

---

## 6. Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-001 | Performance | Dashboard KPI refresh on page open | < 10 seconds |
| NFR-002 | Performance | Full-month allocation recalculation (31 days, 340 wells) | < 90 seconds |
| NFR-003 | Performance | Concurrent users without degradation | 150 users; page load < 3 seconds |
| NFR-004 | Security | Authentication | Azure AD SAML 2.0 SSO; no local accounts |
| NFR-005 | Security | Role-based access control | 7 roles: Field Operator, Production Engineer, Lead Engineer, Production Accountant, Regulatory Analyst, Read-Only, System Administrator |
| NFR-006 | Security | Data in transit encryption | TLS 1.2 or higher |
| NFR-007 | Security / Compliance | Audit trail retention | 7 years minimum |
| NFR-008 | Availability | System uptime | 99.5% monthly (max 4h planned maintenance, off-peak) |
| NFR-009 | Disaster Recovery | RTO / RPO | RTO: 4 hours / RPO: 1 hour |
| NFR-010 | Resilience | PI ingestion local buffer | 8 hours buffering during outages; replay on restore |

---

## 7. Business Rules

See [business-rules.md](./business-rules.md) for the complete list of 19 classified and traceable rules.

Key rules summary:

| ID | Rule Summary | Category |
|----|-------------|----------|
| BR-001 | Well > 15% above test rate for 3 consecutive days → alert Production Engineer | Constraint |
| BR-002 | WC > 95% for oil producer → High Water Cut event + Reservoir Engineer notification | State Transition |
| BR-003 | GOR > 125% of approved reservoir GOR → review workflow; must have Reservoir Engineer note to close | State Transition |
| BR-004 | Allocation finalisation requires all well tests within validity; exceptions need VP Operations sign-off | Authorization |
| BR-007 | Data gap 15 min–4 hours → back-fill with last-known-good + ESTIMATED flag | Policy |
| BR-009 | Well test ratios must be updated in allocation engine within 24 hours of approval | Constraint |
| BR-011 | Three blocking conditions for monthly allocation finalisation | Constraint |
| BR-013 | Two-level approval for well tests; L2 mandatory for > 20% rate deviation from prior test | Authorization |
| BR-014 | Submitted regulatory reports locked; amendments versioned with mandatory justification | State Transition |

---

## 8. Workflows

See [workflows.md](./workflows.md) for detailed workflow definitions.

Key workflows summary:

| ID | Workflow Name | Actors |
|----|--------------|--------|
| WF-001 | Real-time SCADA Data Ingestion | System (PI, DeltaV, WPMA) |
| WF-002 | Manual Production Data Entry | Field Operator |
| WF-003 | Well Test Submission and Approval | Field Operator, Production Engineer, Lead Engineer |
| WF-004 | Monthly Production Allocation and Finalisation | System, Production Engineer, Production Accountant |
| WF-005 | Downtime Event Logging and Loss Accounting | Field Operator, Production Engineer |
| WF-006 | Regulatory Report Generation and Submission | System, Regulatory Affairs Analyst, VP Operations |
| WF-007 | Retroactive Allocation Correction | Production Engineer, Lead Engineer, Production Accountant |
| WF-008 | Production Anomaly Alert Handling | System, Production Engineer, Reservoir Engineer |

---

## 9. Data Requirements

### 9.1 Key Entities

| Entity | Description | Key Attributes |
|--------|-------------|----------------|
| Well | Physical production well | Well ID, Name, Platform/Field, Status, Commodity Type |
| Allocation Group | Group of commingled wells sharing a separator | Group ID, Measurement Point, Methodology |
| Production Reading | Time-series tag value from SCADA / manual entry | Well ID, Tag Name, Value, Timestamp, Source (SCADA/MANUAL), Quality Flag |
| Well Test | Periodic production test record | Well ID, Test Date, Duration, Oil/Gas/Water Rates, GOR/WC, Status, Validity Expiry |
| Allocation Record | Monthly well-level allocated volumes | Well ID, Period, Oil/Gas/Water/Condensate Volumes, Method, Approval Status |
| Downtime Event | Shut-in or production loss event | Well ID, Start/End, Category, Sub-Category, Deferred BBL/MMSCF |
| Regulatory Report | BSEE MMS-146 or RRC PR-2 | Lease/Well, Period, Volumes, Submission Status, Submission Timestamp, Version |
| Audit Log Entry | Immutable record of every data change | Entity Type, Entity ID, User, Action, Old Value, New Value, Timestamp |

### 9.2 Data Retention

| Data Type | Online Retention | Archive | Authority |
|-----------|-----------------|---------|-----------|
| Real-time tag data (1-minute intervals) | 2 years | 10 years cold storage | Operational |
| Daily/monthly aggregated production | 25 years | — | Regulatory |
| Regulatory submission records | Permanent | — | BSEE / RRC |
| Audit log entries | 7 years minimum | — | Company policy |

---

## 10. Integration Requirements

| System | Direction | Protocol | Frequency | Owner |
|--------|-----------|----------|-----------|-------|
| OSIsoft PI Historian | Inbound | PI Web API REST | 1-minute poll | IT Ops |
| Emerson DeltaV (Bravo platform) | Inbound | OPC-UA | 1-minute poll | IT Ops |
| SAP PM (maintenance) | Inbound / Outbound | RFC BAPI | Daily batch | IT Ops |
| Azure Active Directory | Inbound | SAML 2.0 | On-demand (auth) | IT Ops |
| BSEE eFAST Portal | Outbound | SFTP / CSV | Monthly | Regulatory |
| Texas RRC Electronic Filing | Outbound | REST API (RRC v3.2) | Monthly | Regulatory |
| Snowflake Data Warehouse | Outbound | JDBC / Scheduled ELT | Daily | IT Ops |

---

## 11. Assumptions and Constraints

| ID | Statement |
|----|-----------|
| ASM-001 | PI OSIsoft licenses already in place; WPMA consumes the existing PI Web API endpoint without additional licensing cost |
| ASM-002 | Initial release targets Chrome 120+ and Edge 120+; Internet Explorer is not supported |
| ASM-003 | Mobile well test form supports iOS 17+ and Android 14+ only |
| ASM-004 | Permian Basin field has no on-site server; all processing runs on Azure West US 2 |
| ASM-005 | BSEE Form MMS-146 schema is frozen at the April 2025 revision for the initial release |
| CONS-001 | Cloud platform is Azure (company standard); solution must leverage Azure services where possible |

---

## 12. High-Level Acceptance Criteria

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-001 | Field operator logs a well test offline; data syncs within 60 seconds of connectivity restoring | End-to-end test in Permian field conditions |
| AC-002 | Monthly allocation report for all 340 wells available within 15 minutes of month-end midnight | Performance / load test |
| AC-003 | BSEE MMS-146 report matches manually-calculated values within ±0.5% for 3 consecutive months of parallel run | Parallel run comparison |
| AC-004 | 150 concurrent users access dashboards simultaneously with < 3 second load time | Load test |
| AC-005 | Audit trail captures 100% of production and allocation changes during the test period | Audit completeness test |

---

## 13. Risks and Dependencies

| ID | Risk / Dependency | Impact | Mitigation |
|----|------------------|--------|------------|
| RISK-001 | PI Web API endpoint downtime during ingestion | Production data gaps, allocation delays | 8-hour local buffer (NFR-010); gap detection and back-fill (BR-007/008) |
| RISK-002 | Intermittent 4G connectivity in Permian Basin field | Well test data loss from mobile | Offline-first mobile app with sync-on-reconnect (FR-012) |
| RISK-003 | BSEE MMS-146 or RRC v3.2 schema change post-release | Regulatory submission failure | Schema version frozen at April 2025 for initial release (ASM-005); schema updatability required as non-functional |
| RISK-004 | SAP PM RFC BAPI interface unavailable | Loss of maintenance correlation context | Graceful degradation; WPMA functions independently when SAP unavailable |
| RISK-005 | AAD SAML federation not configured for all roles | Users unable to authenticate | IT Ops to configure AAD groups for all 7 RBAC roles prior to go-live |

---

*Document generated by AIKit Requirement Kit on 2026-04-25. Source: well-production-requirements.md.*
