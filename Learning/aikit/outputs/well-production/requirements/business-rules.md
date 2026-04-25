# Business Rules — Well Production Monitoring & Allocation System
**Module**: well-production  
**Extracted by**: AIKit — Requirement Kit  
**Date**: 2026-04-25  
**Total Rules**: 18  

---

## Classification Key

| Category | Code | Description |
|----------|------|-------------|
| Calculation | CALC | A value that is derived by formula |
| Constraint | CONS | An absolute limit or condition that must be enforced |
| Validation | VALID | Input must meet specific criteria before processing |
| Policy | POL | Business decision or company policy |
| Authorization | AUTH | Access or approval rights |
| State Transition | STATE | Conditions triggering a change in status or state |

---

## Business Rules

### Data Acquisition Rules

| ID | Rule | Category | Priority | Source |
|----|------|----------|----------|--------|
| BR-007 | A data gap between 15 minutes and 4 hours must be back-filled using the last-known-good value and flagged as estimated. | POLICY | Must Enforce | FR-003 |
| BR-008 | A data gap exceeding 4 hours must be classified as a "Communication Loss" event. Allocation for the affected well cannot proceed until the gap has been manually reviewed and approved. | CONSTRAINT | Must Enforce | FR-003 |
| BR-015 | Any production value entered manually (non-SCADA wells) must carry an "ESTIMATED" flag visible in all reports and exports. | VALIDATION | Must Enforce | FR-002 |

### Allocation Engine Rules

| ID | Rule | Category | Priority | Source |
|----|------|----------|----------|--------|
| BR-005 | Production volumes are reported as gross liquids at separator conditions (pre-shrinkage). Stock tank volumes (post-shrinkage) must also be stored and reported separately. | POLICY | Must Enforce | Section 7, BRD |
| BR-009 | Well test ratios must be updated in the allocation engine within 24 hours of the well test being approved by the responsible Production Engineer. | CONSTRAINT | Must Enforce | FR-006 |
| BR-010 | Retroactive allocation recalculations are permitted for up to 90 days prior to the current date. Every retroactive change must be logged with: change reason, approver identity, and timestamp. | CONSTRAINT | Must Enforce | FR-008 |
| BR-006 | Any retroactive allocation change applied to a period older than 30 days requires dual approval: Lead Production Engineer AND Production Accountant. | AUTHORIZATION | Must Enforce | Section 7, BRD |
| BR-011 | Monthly allocation finalisation must be blocked if any of the following conditions exist: (a) any well in the allocation group has a missing or expired well test; (b) total allocated volume differs from total measured volume by more than ±0.5%; (c) any unresolved data gap event exists in the allocation period. | CONSTRAINT | Must Enforce | FR-009 |
| BR-004 | Allocations cannot be finalised unless all well tests are within their validity period (30 days for oil producers, 60 days for gas injectors). Exceptions require written approval from VP Operations, logged in the system. | AUTHORIZATION | Must Enforce | Section 7, BRD |

### Well Test Rules

| ID | Rule | Category | Priority | Source |
|----|------|----------|----------|--------|
| BR-012 | A well test must meet the minimum duration requirement before it can be submitted: 6 hours for oil producers, 4 hours for gas wells. Tests below these durations must be rejected. | VALIDATION | Must Enforce | FR-010 |
| BR-016 | Well test validity periods: oil producer tests expire after 30 days; gas injector tests expire after 60 days. An expired test must prevent allocation finalisation. | CONSTRAINT | Must Enforce | FR-009, BR-004 |
| BR-013 | Well test approval requires two levels: Level 1 — Production Engineer. Level 2 — Lead Production Engineer. Level 2 approval is mandatory when the submitted test rate deviates more than 20% from the immediately preceding approved test rate. | AUTHORIZATION | Must Enforce | FR-013 |

### Production Monitoring Rules

| ID | Rule | Category | Priority | Source |
|----|------|----------|----------|--------|
| BR-001 | A well producing above its approved test rate by more than 15% for three consecutive days must automatically generate an alert to the responsible Production Engineer. | CONSTRAINT | Must Enforce | Section 7, BRD |
| BR-002 | Water cut (WC) exceeding 95% for any oil producer must trigger an automatic "High Water Cut" event and notify the Reservoir Engineer. | STATE TRANSITION | Must Enforce | Section 7, BRD |
| BR-003 | A gas-to-oil ratio (GOR) exceeding the approved reservoir GOR by 25% must trigger a review workflow. The review cannot be closed without a documented note from the Reservoir Engineer. | STATE TRANSITION | Must Enforce | Section 7, BRD |

### Downtime Rules

| ID | Rule | Category | Priority | Source |
|----|------|----------|----------|--------|
| BR-017 | Deferred production for a downtime event is calculated using the approved well test rate that was active at the time of the event, in both BBL (oil) and MMSCF (gas). | CALCULATION | Must Enforce | FR-016 |
| BR-018 | Downtime events categorised as "Unclassified" must require a freetext comment before the record can be saved. | VALIDATION | Must Enforce | FR-015 |

### Regulatory Reporting Rules

| ID | Rule | Category | Priority | Source |
|----|------|----------|----------|--------|
| BR-014 | Once a regulatory report is submitted to BSEE or Texas RRC, it must be locked against further editing. Any required amendment must create a new amendment record with an incremented version number and a mandatory justification field. | STATE TRANSITION | Must Enforce | FR-021 |
| BR-019 | The system must send automatic email notifications to the Regulatory Affairs Analyst and VP Operations 10 days and 3 days before the BSEE 15th-of-month submission deadline, if the report for the period has not yet been submitted. | POLICY | Must Enforce | FR-019 |

---

## Business Rule Dependency Map

```
BR-012 (test min duration) ──► BR-013 (test approval) ──► BR-009 (update ratio within 24h)
                                                                  │
              BR-016 (test validity) ──────────────────────────────┤
                                                                  ▼
              BR-008 (data gap >4h) ──────────────────────► BR-011 (block finalisation)
              BR-004 (valid test required) ────────────────────────┘
                      │
              BR-006 (retro >30 days: dual approval) ◄─── BR-010 (retro up to 90 days)

BR-001 (over-rate alert) ─────────────────────────────────► Production Engineer notification
BR-002 (high WC event) ───────────────────────────────────► Reservoir Engineer notification
BR-003 (GOR breach review) ───────────────────────────────► Reservoir Engineer review workflow
BR-014 (lock submitted reports) ─────────────────────────► Amendment versioning
```

---

## Traceability Matrix

| BR ID | FR / NFR | BRD Section |
|-------|----------|-------------|
| BR-001 | — | Section 7 |
| BR-002 | — | Section 7 |
| BR-003 | — | Section 7 |
| BR-004 | FR-009 | Section 7 |
| BR-005 | — | Section 7 |
| BR-006 | FR-008 | Section 7 |
| BR-007 | FR-003 | Section 5.1 |
| BR-008 | FR-003 | Section 5.1 |
| BR-009 | FR-006 | Section 5.2 |
| BR-010 | FR-008 | Section 5.2 |
| BR-011 | FR-009 | Section 5.2 |
| BR-012 | FR-010 | Section 5.3 |
| BR-013 | FR-013 | Section 5.3 |
| BR-014 | FR-021 | Section 5.5 |
| BR-015 | FR-002 | Section 5.1 |
| BR-016 | FR-009 | Section 5.3 |
| BR-017 | FR-016 | Section 5.4 |
| BR-018 | FR-015 | Section 5.4 |
| BR-019 | FR-019 | Section 5.5 |
