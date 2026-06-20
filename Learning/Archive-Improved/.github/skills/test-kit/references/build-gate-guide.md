# Build Gate Guide

## What is the Build Gate?

The build gate is a mandatory quality checkpoint before tests run. It ensures:
1. All services compile without errors (hard gate)
2. All story implementations are present (soft gate)
3. No cloud-specific dependencies block local testing (enforced)

## Gate Levels

| Level | Condition | Action |
|-------|-----------|--------|
| PASS | All services compile + all stories have test placeholders | Proceed to test execution |
| PARTIAL | Some services compile, others NEEDS_REVIEW | Warn user, test what passes |
| FAIL | No services compile | Block — must fix before proceeding |
| CLOUD_SKIP | Cloud services needed but mocked | Log, continue with mocks |

## Gate Check Procedure

```
1. Read aikit/outputs/dev/build-report.md
2. For each service:
   a. Re-run compile check (mvn compile / npm run build / etc.)
   b. Record PASS or FAIL
3. If any FAIL:
   a. Show error details
   b. Ask user: "Fix and retry?" or "Proceed with passing services?"
4. Check story coverage:
   a. Every US-NNN in stories.md → test-cases/US-NNN/ directory exists?
   b. List missing test directories
5. Output gate-report.md
```

## Gate Report Format

```markdown
# Build Gate Report
**Module**: <module-id>
**Date**: <ISO date>
**Verdict**: ✅ PASS | ⚠️ PARTIAL | ❌ FAIL

## Service Compilation
| Service | Status | Command | Issue |
|---------|--------|---------|-------|
| order-service | ✅ PASS | mvn compile | — |
| inventory-service | ✅ PASS | npm run build | — |
| payment-service | ⚠️ REVIEW | mvn compile | Missing AWS SDK mock |

## Story Test Coverage
| Story | Test Dir | Status |
|-------|----------|--------|
| US-001 | test-cases/US-001 | ✅ Present |
| US-002 | test-cases/US-002 | ✅ Present |
| US-003 | test-cases/US-003 | ❌ Missing |

## Recommendations
- Fix payment-service compilation before cloud deployment
- Add test cases for US-003

## Gate Decision
Proceeding with tests for: order-service, inventory-service
Skipping: payment-service (blocked stories: none)
```

## Skipping Failed Services

If a service fails the gate:
- Do NOT block the entire test run
- Run tests for all passing services
- Mark failing service's stories as BLOCKED in test-report.md
- Report clearly to user after test-kit completes
