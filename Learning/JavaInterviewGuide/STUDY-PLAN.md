# Study Plan — Senior Java Fullstack Interviews

## Reality check

You are being hired as someone who can:

- Own a Spring Boot microservice in production
- Reason about Kafka + SQL consistency
- Read a React/TypeScript PR
- Ship on Azure with Helm + Terraform
- Debug Linux at 2 a.m.
- Use AI tools without shipping garbage

Depth beats breadth. Cover **P0** fully, then P1, then P2.

---

## Priority (mapped to how often these JDs mention them)

| Priority | Topics | Why |
|----------|--------|-----|
| **P0** | Java Core, Multithreading, Spring Boot, SQL/Oracle, Kafka, Microservices | Every Java role |
| **P1** | Hibernate, REST, EDA, React+TS, Azure, Design Patterns | Fullstack / 8+ year roles |
| **P2** | Helm, Terraform, Linux, CI/CD, MQ, Azure Functions | Platform + cloud filter |
| **P3** | AI-assisted tools, J2EE leftovers, Sybase | Differentiator / older estates |

---

## 14-day sprint (if you have two weeks)

| Day | Morning (questions, 90 min) | Afternoon (exercises, 90 min) | Night (15 min) |
|-----|-----------------------------|-------------------------------|----------------|
| 1 | Java Core 1–25 | JVM/GC + collections drills | Recite GC types |
| 2 | Java Core 26–50 | Streams / equals-hashCode | One war story |
| 3 | Multithreading 1–25 | Executor + deadlock lab | Happens-before |
| 4 | Multithreading 26–50 + Design Patterns 1–20 | Virtual threads + patterns | Draw thread dump |
| 5 | Spring Boot 1–30 | Transaction + security lab | Propagation table |
| 6 | Spring Boot 31–50 + Hibernate 1–25 | N+1 + 2nd-level cache | Session vs persistence context |
| 7 | **Mock: Java + Spring** | Hibernate 26–50 + SQL 1–20 | Rest |
| 8 | SQL/PLSQL 21–50 | Explain plan + deadlock SQL | Isolation levels |
| 9 | Kafka 1–30 | Consumer group lab | Offset / EOS |
| 10 | Kafka 31–50 + EDA + MQ | Outbox pattern | Dual-write problem |
| 11 | Microservices + REST | Saga + API versioning | Circuit breaker |
| 12 | React + TypeScript | Hooks + TS generics | Component design |
| 13 | Azure + Helm + Terraform + Linux | Deploy mental model | kubectl + tf state |
| 14 | CI/CD + AI tools + Fullstack designs | Full mock (90 min) | Sleep |

---

## 28-day track (recommended)

**Week 1 — Java internals:** Core, Multithreading, Design Patterns  
**Week 2 — Backend:** Spring Boot, Hibernate, SQL/Oracle/PLSQL  
**Week 3 — Distributed:** Microservices, REST, Kafka, MQ, EDA  
**Week 4 — Fullstack + platform:** React/TS, Azure, Helm, Terraform, Linux, CI/CD, AI, system design

Daily rhythm:

1. 10 questions out loud (no notes)
2. 1 exercise typed from memory
3. 1 “what would fail in production?” note

---

## How to self-score a question

Give yourself 0–3:

- 0: definition only or wrong
- 1: correct surface answer
- 2: internals + one trade-off
- 3: internals + production failure + how you would prove it

Senior bar: average **2.2+** on P0 topics.

---

## Mock interview scripts (use with a friend or voice recorder)

### Screen (45 min)

1. Java equals/hashCode + ConcurrentHashMap
2. Spring transaction propagation + lazy loading
3. Kafka consumer lag
4. SQL index that made things worse
5. “Tell me about a production incident”

### Onsite loop (4×45)

1. Coding: concurrent + collections
2. Spring/Hibernate deep dive
3. System design: order service + Kafka + React admin
4. Platform: Azure + Helm rollback + Terraform state lock

### Bar-raiser (30 min)

“We have duplicate payments after a Kafka rebalance. Walk the room.”

Use topic 09 Q36–Q45 and topic 11 outbox exercise.

---

## STAR stories to prepare (write them in your notes)

You need 6 stories, 90 seconds each:

1. Performance (GC, N+1, slow query, Kafka lag)
2. Data incident (duplicate, lost update, poison message)
3. Design you owned (service split, saga, CQRS)
4. Migration (Java 8→17, monolith→services, Oracle upgrade)
5. Cloud/platform (AKS outage, Terraform drift, Helm rollback)
6. Mentoring / AI tools (how you raised the bar without lowering quality)
