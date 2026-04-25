# Permit to Work & Safety Management System
## Business Requirements Document — Draft v1.2
### Client: Meridian Energy Corp | Project: SafeWork Digital | Date: March 2026

---

## 1. Executive Summary

Meridian Energy Corp's current Permit to Work (PTW) process is paper-based across all five assets. Field supervisors complete physical paper forms, route them manually for signatures, and retain physical copies in site offices. This creates significant risks: permits can be lost, approvals cannot be verified remotely, simultaneous operations (SIMOPS) conflicts are not automatically detected, and the company cannot demonstrate to the Health and Safety Executive (HSE) and Bureau of Safety and Environmental Enforcement (BSEE) that safe systems of work are consistently applied.

The SafeWork Digital system will fully digitise the PTW lifecycle, introduce an automated SIMOPS conflict detection engine, manage safety-critical certificates, and provide an HSE-auditable digital trail of all work authorisation activities.

---

## 2. Business Objectives

1. Eliminate paper-based permit handling and achieve zero paper permits by end of Q3 2026.
2. Reduce permit issue time from an average of 45 minutes (paper) to under 10 minutes (digital).
3. Automatically detect 100% of SIMOPS conflicts before work commences.
4. Enable real-time visibility of all open permits to the Offshore Installation Manager (OIM) / Onshore Area Authority.
5. Generate audit-ready compliance reports within 2 hours of an inspection request.
6. Achieve zero instances of expired permits remaining "open" in the system.

---

## 3. Scope

### 3.1 In Scope
- Full digital Permit to Work lifecycle: application, risk assessment, approval, issue, suspension, reinstatement, and closure
- Simultaneous Operations (SIMOPS) conflict detection
- Safety certificate management: isolation certificates, confined space certificates, hot work certificates, radiography certificates, diving supervision certificates
- Competency register integration (read-only from HR system)
- Toolbox talk and pre-job safety meeting records
- Incident near-miss logging linked to permit activities
- Daily work handover log
- BSEE and UK HSE statutory audit export
- Mobile application for field permit use (work site tablet / ATEX-rated device)

### 3.2 Out of Scope
- HR system or competency framework management
- Emergency response / Muster management (covered by separate MUSTER system)
- Environmental monitoring

---

## 4. Permit Types

| Permit Type | Code | High Risk? | Mandatory Certificates |
|------------|------|-----------|----------------------|
| Cold Work | CW | No | None unless isolation required |
| Hot Work | HW | Yes | Hot Work Certificate, Isolation Certificate (if applicable) |
| Confined Space Entry | CS | Yes | Confined Space Certificate, Gas Test Certificate, Isolation Certificate |
| Electrical Isolation | EI | Yes | Isolation Certificate, Electrical Safety Certificate |
| Lifting Operations | LO | No | Lifting Plan (>1 tonne requires Appointed Person sign-off) |
| Excavation | EX | Yes | Ground Disturbance Certificate |
| Diving / Subsea | DV | Yes | Diving Supervision Certificate, Simultaneous Operations Plan |
| Radiography | RG | Yes | Radiography Certificate, Area Exclusion Certificate |
| Pressure Testing | PT | Yes | Pressure Test Plan, Isolation Certificate |
| Line Break | LB | Yes | Isolation Certificate, Gas Free Certificate |

---

## 5. Stakeholder Roles and Permission Matrix

| Role | Create Permit | Approve (Level 1) | Approve (Level 2 - High Risk) | Issue | Suspend/Reinstate | Close | View All |
|------|--------------|--------------------|-------------------------------|-------|-------------------|-------|----------|
| Performing Authority (PA) | ✓ | | | | ✓(own) | ✓(own) | |
| Area Authority (AA) | | ✓ | | ✓ | ✓ | ✓ | ✓(area) |
| Offshore Installation Manager (OIM) | | | ✓ | ✓ | ✓ | ✓ | ✓ |
| Isolation Authority | | | | | | | Certificate only |
| Safety Officer | | ✓(review) | ✓(review) | | | | ✓ |
| HSE Manager | | | | | | | ✓ |
| System Administrator | | | | | | | ✓ |

---

## 6. Functional Requirements

### 6.1 Permit Lifecycle

**FR-001**: A Performing Authority (PA) must be able to create a new permit application from any device (desktop browser or ATEX tablet). The application form must capture:
- Work location (platform/field, module, equipment tag number from equipment register)
- Work description (freetext, minimum 20 characters)
- Planned start and end datetime
- Permit type (from defined list)
- Number of workers
- Work party company (direct employee or contractor, with contractor company name)
- List of tools and equipment to be used
- Energy sources present (electrical, pressure, thermal, chemical, gravity, radiation)
- Task-specific hazard identification checklist (pre-populated per permit type, editable)
- Required PPE checklist (pre-populated, editable)
- Isolation requirements (if any) — cross-reference to isolation register

**FR-002**: The system must enforce mandatory fields per permit type. Submission of an incomplete permit application must be blocked with field-level validation messages.

**FR-003**: On permit submission, the system must:
  1. Assign a unique permit number in format: `[LOCATION]-[TYPE]-[YEAR]-[SEQUENCE]` (e.g., `ALPHA-HW-2026-0342`)
  2. Route the permit to the appropriate Area Authority based on the work location mapping table
  3. Send a push notification and email to the assigned Area Authority

**FR-004**: The Area Authority must be able to:
  - Approve the permit (adding any conditions as freetext)
  - Reject the permit (mandatory rejection reason)
  - Request clarification from the PA (system holds permit in "Clarification Required" status)
  - Escalate to OIM for high-risk permit types

**FR-005**: For all high-risk permit types (HW, CS, EI, EX, DV, RG, PT, LB), two-level approval is mandatory:
  - Level 1: Area Authority
  - Level 2: OIM (or Deputy OIM if OIM is unavailable — system must check delegation record)

**FR-006**: Approved permits can only be "Issued" (work authorised to commence) by the Area Authority or OIM. Issue action must require the issuer to confirm they have physically briefed the Performing Authority.

**FR-007**: Permits must have a maximum validity period enforced by the system. Default validity:
  - Day shift: 06:00–18:00 local time
  - Night shift: 18:00–06:00 local time
  - Extended permits (max 7 days): require OIM approval; only for permit types CW, LO

**FR-008**: At shift handover, all active permits must be countersigned by the incoming Area Authority. The system shall present a "Handover Dashboard" listing all permits requiring countersignature. Outgoing AA cannot log off while any permit in their area lacks incoming countersignature.

**FR-009**: The system shall automatically suspend all active permits and trigger an emergency notification when:
  - A Platform Emergency Alarm (input from emergency system API) is received
  - A manual "Emergency Suspend All" action is performed by OIM

**FR-010**: A PA must close a permit by completing a closure checklist (site cleared, tools accounted for, area left safe) and capturing a closure digital signature. Permits not closed within 2 hours of their expiry time must alert the responsible AA.

### 6.2 SIMOPS Conflict Detection Engine

**FR-011**: When a permit is submitted, the system must evaluate conflicts against all currently active and approved-pending-issue permits at the same location. A conflict exists when:
  - Two permits involve hot work within 15 metres of each other simultaneously
  - A pressure test permit overlaps geographically with any other live permit in the same module
  - A confined space permit is active and a permit involving harmful gas release or pressure work is active in the same drain/vent system area
  - A diving/subsea operation is active and any lifting operation is planned over the diving spread
  - Radiography is active and any other permit is active within the designated exclusion radius

**FR-012**: Conflict detection must be based on equipment location hierarchy: Platform → Module → Area → Equipment Tag. The equipment register must be imported and maintained within the system.

**FR-013**: A detected conflict must:
  - Block permit approval until resolved
  - Display a conflict summary to the Area Authority and OIM
  - Require OIM to explicitly acknowledge and accept risk before the conflicting permit can be approved (creates a SIMOPS record)

**FR-014**: Approved SIMOPS plans must be accessible to all Performing Authorities involved in the conflicting permits.

### 6.3 Safety Certificate Management

**FR-015**: Each safety certificate type has its own digital form with mandatory fields. Certificate types must be maintained in a configurable library by HSE Manager.

**FR-016**: Certificates must be linked to their parent permit. A certificate cannot exist without a parent permit.

**FR-017**: Isolation certificates must integrate with the Isolation Register to verify that each nominated isolation point has been physically signed off by the Isolation Authority before the certificate can be finalised.

**FR-018**: Gas test certificates require the digital entry of gas detector serial number, calibration date (must be within 6-month validity period — validated against calibration register), and test results (gas readings in % LEL, PPM H2S, O2 %). Readings outside safe limits must block certificate finalisation.

**FR-019**: All certificate signatory roles must be verified against the competency register (read from HR system at login). If a user attempts to sign a certificate for a role they are not competent for, the signature must be blocked with a message showing the required competency and the user's current competency status.

### 6.4 Incident / Near Miss Management

**FR-020**: Any user (not just PA) must be able to report a near miss or unsafe condition directly from the PTW system. Report must capture: location, description, immediate action taken, optional photo upload (max 5 photos, 5 MB each).

**FR-021**: Reported near misses must:
  - Receive an auto-generated reference number: `NM-[YEAR]-[SEQUENCE]`
  - Be immediately visible to the Safety Officer and HSE Manager
  - Be assigned to an investigator by the Safety Officer within 24 hours
  - Be closed with corrective actions within 30 days (system escalates to HSE Manager if overdue)

**FR-022**: If a near miss is associated with an active permit, the permit must be automatically flagged for review before it can be reinstated.

### 6.5 Toolbox Talk Records

**FR-023**: Before a permit can be issued, the Performing Authority must complete a digital toolbox talk record confirming:
  - All workers present and signed the permit (digital signatures, name + employee/contractor ID)
  - All workers understand the hazards and controls
  - Emergency procedures briefed
  - PPE confirmed in use

**FR-024**: Workers without digital devices must be listed by name and ID number; their signature block is marked "Physical signature on paper — retained by PA". At least 80% of workers on a permit must have digital signatures for paperless operation reporting.

### 6.6 Dashboards and Reporting

**FR-025**: The OIM Dashboard (real-time) must display:
  - Total open permits by type and by area
  - Permits expiring within the next 2 hours (highlighted red)
  - Active SIMOPS situations
  - Unacknowledged near misses > 24 hours old
  - Countersignature required count (for shift handover)

**FR-026**: Compliance reporting package must include:
  - Weekly permit statistics (issued, closed, expired, suspended)
  - Monthly SIMOPS register
  - Monthly near-miss summary with corrective action closure rate
  - Annual permit type breakdown per asset

**FR-027**: A full permit history for any permit number must be reconstructable from the audit log, showing every status change, every signature, every system event, and every edit, with timestamps and user identities.

---

## 7. Non-Functional Requirements

### 7.1 Performance

**NFR-001**: Permit form must load within 3 seconds on a 4G connection (minimum 20 Mbps) for offshore tablet users.

**NFR-002**: SIMOPS conflict detection must return results within 5 seconds of permit submission.

**NFR-003**: The system must support 200 concurrent users (across all five assets simultaneously).

### 7.2 Availability

**NFR-004**: System availability: 99.9% uptime. The PTW system is safety-critical — planned maintenance windows require BSEE notification and must not occur during active operations.

**NFR-005**: The mobile / tablet application must support offline permit creation and gas test entry. Offline data must sync within 60 seconds of network restoration. The system must clearly indicate "OFFLINE MODE" on the device.

**NFR-006**: The OIM Dashboard must continue to function and display last-known data even if the backend is unreachable, with a visible "DATA STALE" indicator showing time since last refresh.

### 7.3 Security

**NFR-007**: All permit and certificate actions (approval, signature, issue, suspension, closure) require re-authentication (PIN entry minimum, biometric preferred on ATEX tablets) to confirm the identity of the acting user.

**NFR-008**: Each digital signature must be a non-repudiable, timestamped record bound to the user's AAD identity.

**NFR-009**: Permits and certificates are immutable once closed. No deletion is permitted. Corrections require an amendment workflow with dual approval.

**NFR-010**: All data must be stored within the EU or specified regional data sovereignty boundaries as per Meridian's cloud policy (Azure West Europe primary, Azure North Europe DR).

### 7.4 Regulatory Compliance

**NFR-011**: The system's audit trail must meet the requirements of:
  - UK HSE Human and Organisational Factors guidance for PTW systems
  - BSEE SEMS II (30 CFR Part 250, Subpart S) §250.1930 — Safe Work Practices
  - ISO 45001:2018 Section 8.1.3 (Management of Change)

**NFR-012**: All audit log entries must be tamper-evident (cryptographic hash chain or equivalent).

---

## 8. Business Rules

**BR-001**: A Performing Authority may not approve, issue, or countersign their own permit. The PA who created the permit and the AA who approves it must be different individuals.

**BR-002**: A permit cannot be renewed more than twice. After two renewals, the permit must be formally closed and a new permit application submitted.

**BR-003**: Hot work permits are invalid if wind speed exceeds 25 knots at the work location (automated weather feed input). The system must suspend automatically upon receiving wind speed threshold breach.

**BR-004**: A person may not hold more than 5 active permits as Performing Authority simultaneously. On attempting to create a 6th, the system must warn and require supervisor override.

**BR-005**: All permits for a location must be suspended before any emergency depressurisation or blowdown operation. Suspension must be recorded as "Emergency Blowdown" category — not manual suspension.

**BR-006**: Gas tests must be repeated every 4 hours for confined space entry permits while work is ongoing. System must alert the Performing Authority 30 minutes before a gas test re-test is due.

**BR-007**: No permit shall be issued to a contractor company that is not on the Approved Vendor List (integration with SAP Vendor Master — read-only).

---

## 9. Integration Requirements

| System | Direction | Method | Purpose |
|--------|-----------|--------|---------|
| Azure Active Directory | Inbound | SAML 2.0 | Authentication and user identity |
| HR Competency System (Oracle HCM) | Inbound | REST API | Competency verification at signature |
| Equipment Register (IBM Maximo) | Inbound | REST API (daily sync) | Location hierarchy and equipment tags |
| Calibration Register (in-house Access DB) | Inbound | CSV daily export | Detector calibration validity |
| Emergency Alarm System (Tyco IQ) | Inbound | Webhook / TCP event | Platform emergency signal |
| Weather Station API (WNI) | Inbound | REST API, 10-min refresh | Wind speed at offshore platforms |
| SAP Vendor Master | Inbound | RFC BAPI (daily sync) | Approved contractor company list |
| Company Document Management (SharePoint) | Outbound | Graph API | Archive closed permit PDFs |
| BSEE / HSE Audit Export | Outbound | Structured PDF + CSV | Regulatory inspection package |

---

## 10. Acceptance Criteria

| ID | Criterion |
|----|-----------|
| AC-001 | A Hot Work permit from creation to issue takes ≤ 10 minutes end-to-end in UAT with trained users |
| AC-002 | SIMOPS engine detects all 15 seeded conflict scenarios in the test script without false negatives |
| AC-003 | Offline mode allows full permit creation and gas test entry; data syncs within 60 seconds on network restore |
| AC-004 | Platform emergency API signal suspends all 50 seeded active permits within 10 seconds in load test |
| AC-005 | Competency verification correctly blocks all 8 seeded "unauthorised signature" scenarios |
| AC-006 | Audit report for a 3-month period (simulated data) is generated within 2 minutes |
| AC-007 | Digital signatures are non-repudiable — successfully verified by external forensics tool in audit test |

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| AA | Area Authority — supervisor responsible for a geographic area of the facility |
| ATEX | Atmosphères Explosibles — European equipment certification for use in explosive gas atmospheres |
| BSEE | Bureau of Safety and Environmental Enforcement (US Federal regulator for offshore) |
| GOR | Gas-to-Oil Ratio |
| HSE | Health and Safety Executive (UK regulator) or Health, Safety and Environment (department) |
| LEL | Lower Explosive Limit — expressed as % of flammable gas concentration in air |
| OIM | Offshore Installation Manager — highest authority on an offshore platform |
| PA | Performing Authority — the person responsible for executing the permitted work |
| PPE | Personal Protective Equipment |
| PTW | Permit to Work — a formal documented system to control hazardous work |
| SCADA | Supervisory Control and Data Acquisition |
| SEMS | Safety and Environmental Management System (BSEE regulatory framework) |
| SIMOPS | Simultaneous Operations — concurrent activities that may interfere with each other |
| WHP | Wellhead Pressure |
