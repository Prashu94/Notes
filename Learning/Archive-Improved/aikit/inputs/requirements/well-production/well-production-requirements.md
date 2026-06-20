# Well Production Monitoring & Allocation System
## Business Requirements Document — Draft v1.0
### Client: Meridian Energy Corp | Project: WellTrack Pro | Date: March 2026

---

## 1. Executive Summary

Meridian Energy Corp operates 340 active wells across three offshore platforms (Alpha, Bravo, Charlie) and two onshore fields (Permian Basin West, Gulf Coast South). The current production reporting process relies on manual data entry from field operators into disparate spreadsheets, resulting in 4–6 hour delays in production visibility, frequent allocation errors, and regulatory reporting non-compliance.

The Well Production Monitoring & Allocation (WPMA) system must provide real-time production data acquisition, automated hydrocarbon allocation, production forecasting, and regulatory reporting across all assets.

---

## 2. Business Objectives

1. Reduce production reporting cycle from 6 hours to under 15 minutes.
2. Achieve 99.5% accuracy in hydrocarbon allocation across commingled wells.
3. Automate monthly regulatory submissions to BSEE (offshore) and RRC Texas (onshore).
4. Enable production engineers to identify underperforming wells within 30 minutes of anomaly occurrence.
5. Replace 14 existing Excel-based production trackers with a single source of truth.

---

## 3. Scope

### 3.1 In Scope
- Real-time data ingestion from SCADA and DCS systems (PI System, Emerson DeltaV)
- Daily, monthly, and annual production allocation by well, reservoir, and commodity (oil, gas, water, condensate)
- Production performance dashboards and KPI tracking
- Well test management and utilisation calculations
- Regulatory report generation: BSEE Form MMS-146, PR-2 (Texas RRC)
- Downtime event capture and loss accounting
- Integration with SAP PM for well maintenance correlation

### 3.2 Out of Scope
- Reservoir simulation or modelling
- Drilling planning
- Financial accounting or revenue allocation

---

## 4. Stakeholders

| Role | Department | Responsibility |
|------|-----------|----------------|
| Production Engineer | Operations | Primary user — monitors well performance daily |
| Field Operator | Field Operations | Enters gauge readings, reports downtime events |
| Production Accountant | Finance | Reviews and certifies monthly allocations |
| Regulatory Affairs Analyst | HSE | Submits statutory reports to BSEE and RRC |
| Reservoir Engineer | Subsurface | Analyses production trends, updates well models |
| IT Operations | IT | Manages integrations and system availability |
| VP Operations | Leadership | Approves monthly production reports |

---

## 5. Functional Requirements

### 5.1 Data Acquisition

**FR-001**: The system shall continuously poll the PI OSIsoft historian for the following well-level tags at configurable intervals (default: 1 minute):
- Wellhead tubing pressure (WHP_TBG)
- Wellhead casing pressure (WHP_CSG)
- Choke position / bean size
- Flowline temperature
- Separator inlet pressure and temperature
- Separator oil, gas, and water outlet flow rates

**FR-002**: The system shall support manual data entry for wells not connected to SCADA (approximately 40 wells on the onshore Permian field). Manual entries must carry an "ESTIMATED" flag visible in all reports.

**FR-003**: The system shall detect and flag data gaps exceeding 15 minutes as a "Communication Loss" event. Gaps between 15 minutes and 4 hours shall be back-filled using last-known-good value. Gaps exceeding 4 hours require manual review and approval before allocation can proceed.

**FR-004**: The system shall accept daily tank gauge dip readings for lease automatic custody transfer (LACT) reconciliation. Tank gauge readings are entered once per 24-hour cycle at 06:00 local time.

### 5.2 Allocation Engine

**FR-005**: The system shall allocate measured separator volumes to individual commingled wells using the well test ratio method. The allocation formula is:

  Well_i Allocation = (Well_i_Test_Rate / Sum_of_All_Test_Rates) × Measured_Separator_Volume

**FR-006**: Well test ratios must be updated within 24 hours of a well test being approved by the responsible Production Engineer.

**FR-007**: The system shall support three allocation methodologies selectable per allocation point:
  1. Well test ratio (default)
  2. Back-allocation from metered streams
  3. Virtual flow metering (future phase — stub API only in initial release)

**FR-008**: The system shall recalculate allocations retroactively when well test ratios are updated, for up to 90 days prior. Retroactive changes must be logged with change reason, approver identity, and timestamp.

**FR-009**: The system shall prevent finalisation of monthly allocations if:
  - Any well in the allocation group has a missing or expired well test (well test validity period: 30 days for oil producers, 60 days for gas injectors)
  - Total allocated volume differs from measured total by more than ±0.5%
  - Any unresolved data gap event exists in the period

### 5.3 Well Test Management

**FR-010**: Field operators shall be able to submit a well test record containing: test date, test duration (minimum 6 hours for oil wells, 4 hours for gas wells), choke size, separator gauge readings for oil/gas/water, and stabilisation confirmation tick-box.

**FR-011**: The system shall automatically calculate test rates (in BOPD, MMSCFD, BWPD) and GOR/WC upon test submission.

**FR-012**: A mobile-responsive form must be available for field operators to submit well tests from the field. The form must work offline and sync when connectivity is restored (offline-first design required for the Permian Basin field where 4G coverage is intermittent).

**FR-013**: Well tests require two-level approval: Level 1 — Production Engineer; Level 2 — Lead Production Engineer (required when test rate deviates >20% from the previous test).

### 5.4 Downtime & Loss Accounting

**FR-014**: Operators must be able to log downtime events with: well ID, start datetime, end datetime (or "ongoing"), downtime category (see Appendix A), sub-category, estimated production loss (system-calculated from last good test rate), and freetext comment.

**FR-015**: Downtime categories (Appendix A):
  - Mechanical failure (pump, compressor, wellhead equipment)
  - Process upset (separator trip, pipeline overpressure)
  - Planned maintenance
  - Well intervention / workover
  - Third-party constraint (pipeline, gas plant, power)
  - Regulatory / environmental
  - Weather / force majeure
  - Unclassified (requires comment)

**FR-016**: The system shall calculate deferred production (in BBL and MMSCF) for each downtime event using the approved well test rate at time of event.

**FR-017**: The monthly downtime report must be exportable as Excel (.xlsx) and PDF, summarised by well, category, and platform/field.

### 5.5 Regulatory Reporting

**FR-018**: The system shall auto-populate BSEE Form MMS-146 (Monthly Production Report) for each offshore lease, pulling data from finalised monthly allocations.

**FR-019**: BSEE submissions are due by the 15th of the following month. The system must issue email notifications to the Regulatory Affairs Analyst and VP Operations 10 days and 3 days before the deadline if a report is not yet submitted.

**FR-020**: The system shall generate a Texas RRC PR-2 (Purchaser Report) for all onshore wells in Texas. PR-2 data must map to RRC Oil and Gas Division electronic filing schema v3.2.

**FR-021**: Once a regulatory report is submitted, it must be locked against further edits. Any required amendment must create a new amendment record with version number and justification.

### 5.6 Dashboards and Reporting

**FR-022**: The production dashboard must display the following KPIs in real-time:
  - Total field production (BOPD, MMSCFD, BWPD) — current 24h period
  - On-stream efficiency (%) per platform/field and total fleet
  - Top 5 wells by production rate
  - Top 5 wells by deferred production (current month)
  - Current total well count by status (producing, shut-in, injection, workover)

**FR-023**: All charts in dashboards must support data export to PNG and underlying data export to CSV.

**FR-024**: The system must provide a well-level decline curve view showing historical production overlaid with the approved type curve for the well.

---

## 6. Non-Functional Requirements

### 6.1 Performance

**NFR-001**: Dashboard KPIs must refresh within 10 seconds of a user opening the page.

**NFR-002**: Allocation recalculation for a full month (31 days, up to 340 wells) must complete within 90 seconds.

**NFR-003**: The system must support 150 concurrent users without degrading response times beyond 3 seconds for standard page loads.

### 6.2 Security

**NFR-004**: The system must authenticate via the company's existing Azure Active Directory (AAD) using SAML 2.0 SSO. No local username/password accounts.

**NFR-005**: Role-based access control (RBAC) must be enforced. Roles: Field Operator, Production Engineer, Lead Engineer, Production Accountant, Regulatory Analyst, Read-Only, System Administrator.

**NFR-006**: All production data transmitted over the network must be encrypted using TLS 1.2 or higher.

**NFR-007**: Audit trail: every data modification (allocation change, well test approval, downtime edit) must log the user, timestamp, old value, and new value. Audit records must be retained for 7 years.

### 6.3 Availability and Disaster Recovery

**NFR-008**: System availability: 99.5% uptime measured monthly, excluding planned maintenance windows (maximum 4 hours per month, scheduled off-peak).

**NFR-009**: Recovery Time Objective (RTO): 4 hours. Recovery Point Objective (RPO): 1 hour.

**NFR-010**: The PI data ingestion pipeline must buffer data locally for up to 8 hours during system outages and replay without gaps upon restoration.

### 6.4 Integrations

| System | Direction | Method | Frequency |
|--------|-----------|--------|-----------|
| OSIsoft PI Historian | Inbound | PI Web API (REST) | 1-minute poll |
| Emerson DeltaV (Bravo platform) | Inbound | OPC-UA | 1-minute poll |
| SAP PM | Inbound/Outbound | RFC BAPI | Daily batch |
| Azure Active Directory | Inbound | SAML 2.0 | On-demand (authentication) |
| BSEE eFAST Portal | Outbound | SFTP / CSV | Monthly |
| Texas RRC Electronic Filing | Outbound | REST API (RRC v3.2) | Monthly |
| Company Data Warehouse (Snowflake) | Outbound | JDBC / scheduled ELT | Daily |

---

## 7. Business Rules

**BR-001**: A well producing above its approved test rate by more than 15% for three consecutive days must generate an automatic alert to the responsible Production Engineer.

**BR-002**: Water cut (WC) exceeding 95% for any oil producer must trigger an automatic "High Water Cut" event and notify the Reservoir Engineer.

**BR-003**: Gas-to-oil ratio (GOR) exceeding the approved reservoir GOR by 25% must trigger review workflow and cannot be closed without a Reservoir Engineer note.

**BR-004**: Allocations cannot be finalised unless all well tests are within their validity period (30 days oil, 60 days gas injector). Exceptions require VP Operations written approval, logged in the system.

**BR-005**: Production volumes reported are gross liquids at separator conditions (pre-shrinkage). Stock tank volumes (post-shrinkage) must also be stored and reported separately.

**BR-006**: Any retroactive allocation change over 30 days old requires dual approval: Lead Production Engineer + Production Accountant.

---

## 8. Data Retention Requirements

- Real-time tag data (1-minute): retained for 2 years online, archived to cold storage for 10 years
- Daily and monthly aggregated production: retained for 25 years (regulatory requirement)
- Regulatory submission records: permanent retention
- Audit log entries: 7 years minimum

---

## 9. Assumptions and Constraints

1. PI System (OSIsoft) licenses are already in place. WPMA will consume the existing PI Web API endpoint.
2. The initial release targets Chrome 120+ and Edge 120+ browsers. Internet Explorer is not supported.
3. Mobile support (well test entry offline-first) is limited to iOS 17+ and Android 14+.
4. The Permian Basin onshore field does not have a site server — all processing is cloud-hosted (Azure West US 2).
5. BSEE Form MMS-146 schema version is frozen at the April 2025 revision for the initial release.

---

## 10. Acceptance Criteria (High Level)

| ID | Criterion |
|----|-----------|
| AC-001 | Field operator can log a well test from a mobile device with no network and it syncs within 60 seconds of connectivity restoring |
| AC-002 | Monthly allocation report for all 340 wells is available within 15 minutes of the last day of month midnight |
| AC-003 | BSEE MMS-146 report matches manually calculated values within ±0.5% for 3 consecutive months of parallel run |
| AC-004 | All 150 concurrent users can access dashboards simultaneously with < 3 second load time |
| AC-005 | Audit trail captures 100% of production and allocation changes in the test period |
