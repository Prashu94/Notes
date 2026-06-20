# Tech Stack Selection Guide

## Decision Framework

When selecting technology, consider:
1. **Team expertise** — existing skills reduce ramp-up
2. **Ecosystem maturity** — libraries, community, LTS support
3. **Integration requirements** — must-have connectors
4. **Scalability profile** — expected load and growth
5. **Cross-module consistency** — check `cross-cutting.yaml` for existing choices in the project

## Backend Framework Comparison

| Framework | Language | Best For | Avoid When |
|-----------|----------|----------|-----------|
| Spring Boot | Java | Enterprise, complex domain | Small/simple services |
| FastAPI | Python | ML integration, rapid APIs | High concurrency (use with Uvicorn+async) |
| NestJS | TypeScript | Node.js structured apps | Pure JS preference |
| Express.js | JavaScript | Lightweight/flexible | Large teams needing structure |
| Django REST | Python | Data-heavy, admin-heavy | High-performance APIs |
| .NET | C# | Microsoft stack, Windows | Cross-platform simplicity |

## Database Selection

| Database | Type | Best For | Avoid When |
|----------|------|----------|-----------|
| PostgreSQL | Relational | Complex queries, JSONB, extensions | Extreme write scale |
| MySQL | Relational | Read-heavy, standard OLTP | Complex JSON, full-text |
| MSSQL | Relational | Microsoft ecosystem | Open-source preference |
| MongoDB | Document | Flexible schema, hierarchical | Complex relationships |
| DynamoDB | Key-Value | Extreme scale, AWS-native | Complex queries |
| Redis | In-memory | Cache, sessions, pub-sub | Durability-critical primary store |

## Frontend Framework Comparison

| Framework | Best For | Learning Curve | MFE Support |
|-----------|----------|---------------|-------------|
| React | Flexibility, large ecosystem | Medium | Module Federation (webpack 5) |
| Angular | Enterprise, structured, typed | High | Module Federation |
| Vue.js | Simplicity, progressive | Low | Vite Federation |

## Microfrontend Architecture Decision

Choose MFE when:
- Multiple teams own different UI sections
- Independent deployment of UI modules is required
- Feature teams are large (5+ per section)

Stay with SPA when:
- Single team
- Simpler deployment
- Low UI complexity

## UI Library Pairing

| Frontend | Recommended Libraries |
|----------|-----------------------|
| React | Material-UI (MUI), Ant Design, Shadcn/ui, Chakra UI |
| Angular | Angular Material, PrimeNG, NGX-Bootstrap |
| Vue | Vuetify, Element Plus, PrimeVue |

## Cloud Provider Selection

| Provider | Best For | Key Services |
|----------|----------|-------------|
| AWS | Widest service portfolio, mature | EKS, RDS, SQS, Lambda, ALB |
| GCP | Data/ML heavy workloads | GKE, Cloud SQL, Pub/Sub, BigQuery |
| Azure | Microsoft/enterprise workloads | AKS, Azure SQL, Service Bus |
| None | On-premise / dev-only | Docker Compose, bare Kubernetes |
