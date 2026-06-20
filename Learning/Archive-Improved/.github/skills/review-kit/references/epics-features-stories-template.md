# Epics, Features, and Stories Template

## Hierarchy

```
EPIC
  └── FEATURE
        └── USER STORY
              └── TASK (added during sprint planning)
```

## Epic Template

```markdown
## EPIC-NNN: <Name>
**Domain**: <Business domain — e.g., Order Management, Authentication>
**Goal**: <One sentence: what business problem this epic solves>
**Scope**:
  - In: <what is included>
  - Out: <what is excluded>
**Priority**: Critical | High | Medium | Low
**Effort**: XS (1-3 pts) | S (5-8) | M (13-21) | L (34-55) | XL (55+)
**BRD References**: FR-NNN, WF-NNN
**Definition of Done**:
- All features delivered and tested
- Acceptance criteria verified
- Documentation updated
```

## Feature Template

```markdown
### FEAT-NNN: <Name>
**Epic**: EPIC-NNN — <Epic Name>
**Description**: <What users can do with this feature>
**Priority**: Must Have | Should Have | Could Have | Won't Have
**Total Story Points**: <sum of child stories>
**BRD References**: FR-NNN, BR-NNN
**Acceptance Criteria**:
- [ ] <specific, testable criterion>
- [ ] <specific, testable criterion>
**Dependencies**: FEAT-NNN (must be done first)
```

## Story Template

```markdown
#### US-NNN: <Title (active verb: "Create", "View", "Manage")>
**Feature**: FEAT-NNN  **Epic**: EPIC-NNN
**Story**: As a <role>, I want to <action> so that <value>
**Story Points**: 1 | 2 | 3 | 5 | 8 | 13
**Priority**: Critical | High | Medium | Low

**Acceptance Criteria**:
```gherkin
Scenario: <happy path>
  Given <initial state>
  When <user/system action>
  Then <observable outcome>
  And <additional outcome>

Scenario: <alternate/edge case>
  Given ...
  When ...
  Then ...

Scenario: <error case>
  Given ...
  When ...
  Then ...
```

**References**: FR-NNN, BR-NNN, WF-NNN
**API Endpoints**: POST /api/v1/resource
**UI Components**: <ComponentName>
**Database Changes**: <table/collection affected>
**Events Emitted**: <EventName>
**Blocked By**: US-NNN
**Blocks**: US-NNN
**Dev Notes**: <implementation hints>
**Test Notes**: <additional test scenarios>
```

## Numbering Convention

- Epics: EPIC-001, EPIC-002 ...
- Features: FEAT-001, FEAT-002 ...
- Stories: US-001, US-002 ...
- Tasks: T-001 (added during sprint)

## Story Point Reference

| Points | Complexity | Typical Time |
|--------|-----------|-------------|
| 1 | Trivial config/copy change | < 1 hr |
| 2 | Simple CRUD | 1-2 hrs |
| 3 | CRUD + validation + unit tests | Half day |
| 5 | Feature with integration | 1 day |
| 8 | Complex feature, multiple layers | 2-3 days |
| 13 | Complex + unknowns | Should be split |
