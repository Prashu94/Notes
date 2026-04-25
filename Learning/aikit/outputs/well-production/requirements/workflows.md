# Workflows — Well Production Monitoring & Allocation System
**Module**: well-production  
**Extracted by**: AIKit — Requirement Kit  
**Date**: 2026-04-25  
**Total Workflows**: 8

---

## Workflow Index

| ID | Name | Type | Actors |
|----|------|------|--------|
| WF-001 | Real-time SCADA Data Ingestion | System | PI System, DeltaV, WPMA |
| WF-002 | Manual Production Data Entry | User | Field Operator |
| WF-003 | Well Test Submission and Approval | Collaborative | Field Operator, Production Engineer, Lead Production Engineer |
| WF-004 | Monthly Production Allocation and Finalisation | Collaborative | System, Production Engineer, Lead Engineer, Production Accountant |
| WF-005 | Downtime Event Logging and Loss Accounting | User | Field Operator, Production Engineer |
| WF-006 | Regulatory Report Generation and Submission | Collaborative | System, Regulatory Affairs Analyst, VP Operations |
| WF-007 | Retroactive Allocation Correction | Collaborative | Production Engineer, Lead Production Engineer, Production Accountant |
| WF-008 | Production Anomaly Alert Handling | System + User | System, Production Engineer, Reservoir Engineer |

---

## WF-001: Real-time SCADA Data Ingestion

**Type**: System Workflow  
**Trigger**: Scheduled poll timer fires (default: every 1 minute, configurable)  
**Actor(s)**: WPMA Data Acquisition Service, OSIsoft PI Historian (REST), Emerson DeltaV (OPC-UA, Bravo platform)  
**Pre-conditions**: PI Web API endpoint is reachable; DeltaV OPC-UA server is running  

**Main Flow**:
1. `[ASYNC]` Ingestion scheduler fires at configured interval
2. System polls PI Web API for all configured well-level tags: WHP_TBG, WHP_CSG, choke position, flowline temperature, separator inlet P/T, separator oil/gas/water outlet flow rates
3. System polls DeltaV OPC-UA server for Bravo platform tags
4. System validates each tag reading — checks for null, out-of-range, and timestamp freshness
5. `< Is data gap detected? >`
   - 5a. **No gap**: Store readings to time-series store; update real-time dashboard
   - 5b. **Gap ≤ 15 min**: Continue normal processing; no flag
   - 5c. **Gap 15 min – 4 hours**: Back-fill with last-known-good value; flag reading as ESTIMATED (BR-007)
   - 5d. **Gap > 4 hours**: Create "Communication Loss" event; flag well as PENDING REVIEW; block allocation for well until manual approval (BR-008)
6. Write buffered data to local 8-hour buffer store (NFR-010)
7. Emit real-time event to dashboard service

**Post-conditions**: All available tag readings stored; data gaps classified and flagged  
**Business Rules**: BR-007, BR-008  
**Related Workflows**: WF-004 (allocation reads ingested data)

---

## WF-002: Manual Production Data Entry

**Type**: User Workflow  
**Trigger**: Field Operator logs into system to enter daily gauge readings for non-SCADA wells  
**Actor(s)**: Field Operator  
**Pre-conditions**: Well is in the manual-entry well list (~40 Permian wells); current date has no existing entry for the well  

**Main Flow**:
1. Field Operator opens manual data entry screen
2. System displays list of wells assigned to the operator requiring entries for the current date
3. Operator selects well and enters values: separator oil/gas/water flow rates, wellhead pressure, choke size
4. System validates required fields; rejects incomplete submissions
5. Operator submits entry
6. System stores data with "ESTIMATED" flag on all values (BR-015)
7. System makes data available for allocation engine with flag visible in all downstream reports

**Post-conditions**: Manual readings recorded, flagged "ESTIMATED"; available for allocation  
**Alternate Flows**:
  - Alt-1: **LACT Tank Gauge Entry** — Operator enters daily dip reading at 06:00 local time once per 24h cycle for LACT reconciliation (FR-004)  
**Business Rules**: BR-015  
**Related Workflows**: WF-004

---

## WF-003: Well Test Submission and Approval

**Type**: Collaborative Workflow  
**Trigger**: A scheduled well test is due OR Production Engineer requests an unscheduled test  
**Actor(s)**: Field Operator, Production Engineer, Lead Production Engineer  
**Pre-conditions**: Well is in producing or test-ready state; mobile form available (offline-capable for Permian field)  

**Main Flow**:
1. Field Operator opens well test form on mobile device (works offline — AC-001)
2. Operator enters test record: test date, test duration, choke size, separator gauge readings (oil/gas/water), stabilisation confirmation
3. System validates minimum test duration: ≥ 6h for oil producers, ≥ 4h for gas wells (BR-012); rejects if below threshold
4. Operator submits form (syncs within 60 seconds on connectivity restore for Permian field)
5. System auto-calculates test rates (BOPD, MMSCFD, BWPD) and GOR/WC (FR-011)
6. System sends well test for Level 1 approval to responsible Production Engineer
7. `< Does test rate deviate > 20% from previous approved test? >` (BR-013)
   - 7a. **No**: Level 1 approval sufficient; Production Engineer reviews and approves
   - 7b. **Yes**: Level 2 approval required; notification sent to Lead Production Engineer
8. Level 1 approver — Production Engineer reviews calculated rates; approves or rejects with comments
9. `< Level 2 required? >`
   - 9a. **No**: Proceed to Step 10
   - 9b. **Yes**: Lead Production Engineer reviews; approves or escalates; may request re-test
10. System marks well test as APPROVED
11. `[ASYNC]` System updates well test ratios in allocation engine within 24 hours (BR-009)
12. System records new test validity period: 30 days (oil) or 60 days (gas injector) (BR-016)

**Post-conditions**: Approved well test stored; allocation ratios scheduled for update; test validity timer starts  
**Alternate Flows**:
  - Alt-2: **Rejection** — Engineer rejects test; Operator notified; new test must be submitted  
**Exception Flows**:
  - Exc-1: **Offline Sync Failure** — If offline entry cannot sync within 60 seconds, system retries with exponential backoff; operator notified if sync fails after 5 attempts  
**Business Rules**: BR-009, BR-012, BR-013, BR-016  
**Related Workflows**: WF-004

---

## WF-004: Monthly Production Allocation and Finalisation

**Type**: Collaborative Workflow  
**Trigger**: Last day of the calendar month passes midnight, OR Production Engineer manually initiates allocation  
**Actor(s)**: WPMA Allocation Engine (System), Production Engineer, Production Accountant  
**Pre-conditions**: All daily production data for the month ingested or manually entered; all well tests for the period on record  

**Main Flow**:
1. System initiates monthly allocation calculation for each allocation group
2. For each well in each allocation group:
   - Apply allocation methodology selected for the group (default: well test ratio)
   - Calculate: `Well_i = (Well_i_Test_Rate / Σ_Test_Rates) × Measured_Sep_Volume` (FR-005)
3. System performs pre-finalisation validation checks (BR-011):
   - `< Any well with missing or expired well test? >` → Block if Yes
   - `< Total allocated vs. measured difference > ±0.5%? >` → Block if Yes
   - `< Any unresolved Communication Loss / data gap event? >` → Block if Yes
4. `< All checks pass? >`
   - 4a. **No**: System flags blockers; sends notification to Production Engineer with details; workflow paused
   - 4b. **Yes**: System generates draft monthly allocation report  
5. Production Engineer reviews draft allocations; can override individual well allocations with reason and approval
6. Production Engineer submits for Production Accountant certification
7. Production Accountant reviews; certifies monthly allocations
8. System finalises allocations; locks the period against further changes
9. Allocation report made available for regulatory reporting and Snowflake export (FR-018, NFR integrations)

**Post-conditions**: Monthly allocations finalised, locked, and available for downstream use  
**Alternate Flows**:
  - Alt-3: **Allocation methodology override** — Engineer switches individual allocation point from well test ratio to back-allocation method (FR-007)  
**Exception Flows**:
  - Exc-2: **VP Override on expired test** — VP Operations provides written approval logged in system to allow finalisation with expired test (BR-004)  
**Business Rules**: BR-004, BR-005, BR-009, BR-011, BR-016  
**Related Workflows**: WF-003, WF-006, WF-007

---

## WF-005: Downtime Event Logging and Loss Accounting

**Type**: User Workflow  
**Trigger**: A well shuts in, trips, or is taken offline; Field Operator or Production Engineer initiates log  
**Actor(s)**: Field Operator, Production Engineer  
**Pre-conditions**: Well exists in system; current approved test rate on record  

**Main Flow**:
1. Field Operator or Production Engineer opens downtime event entry screen
2. User enters: well ID, start datetime, downtime category and sub-category, freetext comment
3. `< Category is "Unclassified"? >` → Require non-empty freetext comment (BR-018)
4. User can enter end datetime or mark as "ongoing"
5. System validates required fields; rejects if mandatory fields missing
6. System calculates estimated production loss (deferred production) using approved test rate active at time of event: `Deferred_BBL = Test_Rate_BOPD × Hours_Down / 24` (BR-017)
7. System stores event; updates on-stream efficiency KPIs on dashboard (FR-022)
8. Production Engineer reviews event record; updates category if mislabelled
9. When well returns to production, Operator closes event with actual end datetime
10. System recalculates final deferred production values

**Post-conditions**: Downtime event recorded; deferred production calculated; dashboard KPIs updated  
**Business Rules**: BR-017, BR-018  
**Related Workflows**: WF-004 (deferred production feeds monthly report)

---

## WF-006: Regulatory Report Generation and Submission

**Type**: Collaborative Workflow  
**Trigger**: End of calendar month; Monthly allocations finalised  
**Actor(s)**: WPMA Report Engine (System), Regulatory Affairs Analyst, VP Operations  
**Pre-conditions**: Monthly allocations finalised and locked for the period; BSEE/RRC credentials configured  

**Main Flow**:
1. System auto-populates BSEE Form MMS-146 for each offshore lease from finalised allocations (FR-018)
2. System generates Texas RRC PR-2 Purchaser Report for all Texas onshore wells (FR-020), mapped to RRC v3.2 schema
3. System sends notification to Regulatory Affairs Analyst: "Reports ready for review"
4. `< Current date ≥ 5th of the following month and report not yet submitted? >`
   - 4a. At **10 days before 15th deadline**: System sends email alert to Regulatory Affairs Analyst + VP Operations (FR-019)
   - 4b. At **3 days before 15th deadline**: System sends second email alert (FR-019)
5. Regulatory Affairs Analyst opens report, reviews data, validates totals
6. `< Discrepancy found? >`
   - 6a. **Yes**: Returns to Production Engineer for correction; allocation period may require correction via WF-007
   - 6b. **No**: Proceeds to submission
7. Regulatory Affairs Analyst submits BSEE report via SFTP to eFAST portal; submits RRC PR-2 via RRC REST API v3.2
8. System locks report record against further edits (BR-014)
9. System records submission timestamp, confirmation reference number

**Post-conditions**: Reports submitted to BSEE and RRC; records locked; submission logged  
**Alternate Flows**:
  - Alt-4: **Amendment Required** — Analyst initiates amendment; system creates new versioned amendment record with justification (BR-014)  
**Business Rules**: BR-014, BR-019  
**Related Workflows**: WF-004, WF-007

---

## WF-007: Retroactive Allocation Correction

**Type**: Collaborative Workflow  
**Trigger**: Production Engineer identifies an allocation error in a prior period (up to 90 days prior)  
**Actor(s)**: Production Engineer, Lead Production Engineer, Production Accountant  
**Pre-conditions**: The period to be corrected has not been older than 90 days from today; original allocations on record  

**Main Flow**:
1. Production Engineer opens retroactive correction screen and selects the period and well(s) to correct
2. System checks: `< Correction target period > 30 days old? >` (BR-006)
3. `< Period ≤ 30 days old? >`
   - 3a. **Yes (≤30 days)**: Lead Production Engineer approval only required; proceed to Step 4
   - 3b. **No (>30 days)**: Dual approval required — Lead Production Engineer AND Production Accountant; proceed to Step 5
4. Engineer enters corrected values, change reason; submits for Level 1 approval
5. `< Dual approval required? >`
   - 5a. **No**: Lead Production Engineer reviews and approves
   - 5b. **Yes**: Lead Production Engineer approves AND Production Accountant countersigns
6. System recalculates allocations for selected period
7. System logs: correction details, change reason, approver identities, timestamps (BR-010)
8. System marks original period as AMENDED; new allocations become authoritative
9. If the period was previously submitted for regulatory reporting, flags for amendment report (WF-006, Alt-4)

**Post-conditions**: Retroactive correction applied; change log complete; downstream reports updated or flagged  
**Exception Flows**:
  - Exc-3: **Period > 90 days** — System rejects; user must contact System Administrator for manual override  
**Business Rules**: BR-006, BR-010  
**Related Workflows**: WF-004, WF-006

---

## WF-008: Production Anomaly Alert Handling

**Type**: System + User Workflow  
**Trigger**: Automated monitoring engine detects threshold breach  
**Actor(s)**: WPMA Monitoring Service (System), Production Engineer, Reservoir Engineer  
**Pre-conditions**: Well has an approved test rate; real-time data pipeline is active  

**Main Flow**:
1. `[ASYNC]` Monitoring service continuously evaluates real-time well data against thresholds
2. `< Alert condition detected? >`
   - Condition A — Over-rate alert: Well > 15% above approved test rate for 3 consecutive days (BR-001) → Notify Production Engineer
   - Condition B — High Water Cut: WC > 95% for oil producer (BR-002) → Create "High Water Cut" event, notify Reservoir Engineer
   - Condition C — GOR breach: GOR > 125% of approved reservoir GOR (BR-003) → Trigger GOR review workflow, notify Reservoir Engineer; block closure without Reservoir Engineer note
3. Relevant engineer receives notification (email + in-app)
4. Engineer opens alert detail view; reviews well data, trend curves (FR-024)
5. Engineer documents investigation notes
6. `< Action required? >`
   - 6a. **Over-rate**: Engineer may initiate a new well test via WF-003 or update choke setting
   - 6b. **High WC**: Reservoir Engineer reviews; may trigger workover consideration (logged via WF-005)
   - 6c. **GOR Breach**: Reservoir Engineer adds mandatory closure note; workflow closed
7. Alert closed with resolution status and notes; recorded in audit trail

**Post-conditions**: Alert acknowledged and resolved; action taken and logged  
**Business Rules**: BR-001, BR-002, BR-003  
**Related Workflows**: WF-003, WF-005
