# Java Interview Guide — Senior Fullstack (10+ years)

A comprehensive, production-oriented interview prep kit mapped to real job evaluations:

| Role | Experience | Stack they will grill you on |
|------|------------|------------------------------|
| Java Fullstack | 8–15 | Java, Spring Boot, ReactJS, Hibernate, SQL, Kafka, Cloud, Helm, Terraform, Linux |
| Java + Spring Boot | 8–10 | Java, Spring Boot, Hibernate, SQL, Kafka + React, Helm, Terraform, Linux |
| Java + Spring Boot | 8–10 | Java, Spring Boot, Microservices, SQL, Kafka, Cloud, Helm, Terraform |
| Java Fullstack + TypeScript | 8–10 | Java, ReactJS, TypeScript, Kafka, Cloud, Helm, Terraform, any DB |
| Java Fullstack | 8+ / 5+ | Java, Spring Boot, React, REST, Kafka, Microservices, EDA, Azure Functions, Azure, CI/CD, AI tools |
| Java Multithreading | 5–8 | Java multithreading, Kafka/MQ, AI tools |
| Java | 5–8 | Java, Oracle/Sybase/SQL, MQ/Kafka, Azure |
| Java + Spring Boot | 5–8 | Java, Spring Boot, Microservices, Oracle PL/SQL, Kafka, Azure, AI tools |
| Java + Spring Boot | 8–19 | Java, J2EE, Spring Boot, Design Patterns |

**Target bar:** Staff/Senior (10+ years). Answers emphasize internals, trade-offs, failure modes, and what you would do in production — not textbook definitions.

**What’s inside:** 19 topics × **~55–85 Q&A each** (1,054+ questions) with senior-level answers, follow-up model answers, scenario probes, plus **181-pattern catalog** for design patterns, and **33 practical exercises** per topic (Basic → Hard).

**Content status:** see [EXPANSION-STATUS.md](./EXPANSION-STATUS.md).

---

## How to use this guide

1. Read **[STUDY-PLAN.md](./STUDY-PLAN.md)** and pick a 2-week or 4-week track.
2. For each topic: questions first (cover answers), then exercises (type the code, do not just read).
3. Practice **out loud**. Senior interviews grade communication and decision-making as much as correctness.
4. After each topic, write a 3-minute “war story” (incident, design choice, or migration) you can tell.
5. Keep **[CHEATSHEET.md](./CHEATSHEET.md)** nearby. Map a recruiter JD with **[JD-MAP.md](./JD-MAP.md)**.

Each topic folder contains:

- `questions.md` — senior Q&A (**expanded format**: short answer + internals + production + pitfalls + **follow-up model answers** + scenario probes — see [ANSWER-FORMAT.md](./ANSWER-FORMAT.md))
- `pattern-catalog.md` — **03-design-patterns only:** 181 scenario Q&A from [java-design-patterns.com](https://java-design-patterns.com/patterns/)
- `exercises.md` — **33 drills per topic** (12 Basic → 12 Intermediate → 9 Hard) with full solutions

---

## Topic map

| # | Folder | What interviewers probe |
|---|--------|-------------------------|
| 01 | [java-core](./01-java-core/) | JVM, GC, memory, collections, generics, Java 8–21, J2EE leftovers |
| 02 | [multithreading](./02-multithreading/) | Happens-before, locks, executors, virtual threads, concurrency bugs |
| 03 | [design-patterns](./03-design-patterns/) | GoF + Spring/cloud patterns; **[181-pattern catalog](./03-design-patterns/pattern-catalog.md)** from [java-design-patterns.com](https://java-design-patterns.com/patterns/) |
| 04 | [spring-boot](./04-spring-boot/) | Auto-config, AOP, transactions, security, actuators, internals |
| 05 | [hibernate-jpa](./05-hibernate-jpa/) | Sessions, N+1, caching, dirty checking, locking, migrations |
| 06 | [microservices](./06-microservices/) | Boundaries, sagas, resilience, service mesh, observability |
| 07 | [rest-api](./07-rest-api/) | Contract design, versioning, idempotency, OpenAPI, errors |
| 08 | [sql-oracle-plsql](./08-sql-oracle-plsql/) | Indexing, plans, isolation, PL/SQL, Oracle/Sybase specifics |
| 09 | [kafka](./09-kafka/) | Partitions, consumer groups, EOS, compaction, ops |
| 10 | [messaging-mq](./10-messaging-mq/) | JMS, Rabbit/IBM MQ, vs Kafka, transactional outbox |
| 11 | [event-driven-architecture](./11-event-driven-architecture/) | EDA, CQRS, choreography vs orchestration, dual write |
| 12 | [react-typescript](./12-react-typescript/) | Hooks, concurrent React, TS types, performance, state |
| 13 | [azure-cloud](./13-azure-cloud/) | AKS, Functions, App Service, Identity, networking, cost |
| 14 | [helm-kubernetes](./14-helm-kubernetes/) | Charts, values, hooks, K8s primitives, troubleshooting |
| 15 | [terraform](./15-terraform/) | State, modules, providers, drift, Azure patterns |
| 16 | [linux](./16-linux/) | Process, network, disk, logs — commands you will type in a war room |
| 17 | [ci-cd](./17-ci-cd/) | Pipelines, GitOps, quality gates, secrets, rollback |
| 18 | [ai-assisted-tools](./18-ai-assisted-tools/) | Copilot/Cursor in SDLC, review, risk, how seniors use AI |
| 19 | [fullstack-system-design](./19-fullstack-system-design/) | End-to-end designs that stitch the stack together |

---

## Interview scoring they actually use

Senior panels typically score:

1. **Depth** — can you go one layer below the API (JVM, Kafka log, Hibernate session, K8s kubelet)?
2. **Judgment** — trade-offs, “it depends”, and when you would *not* use a tool.
3. **Production** — incidents, SLOs, rollback, data repair, on-call.
4. **Ownership** — design, code, tests, deploy, observe, cost.
5. **Communication** — structured answers (context → options → decision → risk).

Use this answer shape:

```
Context → Options → Trade-offs → Decision → Failure modes → How I would verify
```

---

## Quick start this weekend

If you only have 2 days before a screen:

1. Java Core Q1–20 + Multithreading Q1–25
2. Spring Boot Q1–30 + Hibernate N+1 / transactions
3. Kafka consumer groups + exactly-once
4. One fullstack design from topic 19
5. Linux commands + Terraform state + Helm upgrade rollback

Good luck. Treat every question as a design conversation, not a flashcard.
