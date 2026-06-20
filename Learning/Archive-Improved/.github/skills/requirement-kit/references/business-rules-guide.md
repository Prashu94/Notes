# Business Rules Extraction Guide

## What is a Business Rule?

A business rule is a statement that defines or constrains some aspect of business behavior. It describes what the system MUST enforce — not how it does it.

## Categories

| Category | Description | Signal Words |
|----------|-------------|-------------|
| **Validation** | Input must meet criteria | "must be", "cannot be", "must not exceed" |
| **Calculation** | Derived values | "is calculated as", "equals", "based on" |
| **Constraint** | Absolute limits | "only if", "no more than", "at least" |
| **Policy** | Business decisions | "as per policy", "according to", "company rule" |
| **Authorization** | Access control | "only users with", "requires approval", "permitted to" |
| **State Transition** | When things change state | "transitions to", "becomes", "changes from" |

## Identification Signals

Scan for these patterns in requirements text:

- "The system shall..." → likely an FR, check if rule-driven
- "A [noun] must/shall/must not..." → Business Rule
- "If [condition] then [outcome]..." → Business Rule (Constraint or Policy)
- "The [noun] is calculated by..." → Business Rule (Calculation)
- "Only [role] can..." → Business Rule (Authorization)
- "Valid values are..." → Business Rule (Validation)
- "[Noun] cannot be changed after..." → Business Rule (State Transition)

## Quality Checklist

Each extracted business rule should be:
- [ ] Stated in present tense ("A user must have..." not "A user will have...")
- [ ] Technology-agnostic (no mention of DB columns, API endpoints)
- [ ] Testable (can write a test case for it)
- [ ] Uniquely numbered (BR-NNN)
- [ ] Traceable to source document/section

## Anti-Patterns to Avoid

- **UI rules in BRs**: "The button must be red" — this is a UI requirement, not a BR
- **Duplicates**: Normalize rules that say the same thing from different perspectives
- **Implementation rules**: "The cache must be invalidated when..." — this is a technical decision
- **Vague statements**: "The system should be fast" — this is an NFR, not a BR
