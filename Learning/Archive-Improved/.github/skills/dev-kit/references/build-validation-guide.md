# Build Validation Guide

## Principle: Local Build First

The dev-kit must produce code that builds successfully in a local developer environment.
Cloud services (S3, SQS, RDS, etc.) must NOT be required for compilation.

## Build Environment Assumptions

- Docker + Docker Compose available for local dependencies (DB, cache, broker)
- JDK 21 for Spring Boot
- Python 3.11+ for FastAPI/Django
- Node.js 20 LTS for NestJS/Express/React/Angular
- .NET 8 SDK for .NET

## Local Dev Dependency Stack (docker-compose.yml)

Every generated service must include a `docker-compose.yml`:

```yaml
# docker-compose.yml — local dev dependencies
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-mydb}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASS:-postgres}
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    ports:
      - "9092:9092"
```

## Auto-Fix Decision Table

| Build Error Type | Can Auto-Fix? | Fix Strategy |
|-----------------|--------------|-------------|
| Missing import (clear class name) | YES | Add import statement |
| Type mismatch (DTO ↔ entity) | YES | Fix type to match db-schema |
| Method signature mismatch | YES | Fix call site |
| Missing method implementation | YES | Add stub |
| Missing dependency (Maven/package.json) | YES | Add to pom.xml / package.json |
| Compilation semantic error | SOMETIMES | Fix if clear |
| Runtime logic error | NO — log and flag |
| Cloud SDK authentication error | NO — add placeholder + env var |

## Maximum Retry Protocol

```
attempt 1: run build → read errors → apply fixes
attempt 2: run build → read errors → apply fixes
attempt 3: run build → read errors → apply fixes (last chance)
if still failing: mark service as NEEDS_REVIEW in build-report.md
```

Never block the pipeline on a single failing service.
Continue generating other services and pages, mark the failing one for manual review.

## Build Report Template

See `dev-buildcheck.agent.md` for the full report format.
Summary line format for `build-report.md`:
```
| order-service | ✅ PASS | 1 attempt | mvn clean compile |
| payment-service | ⚠️ NEEDS REVIEW | 3 attempts | Cloud SDK auth error |
```
