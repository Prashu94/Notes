# PostgreSQL Complete Guide - Hands-On Exercises

## 🏦 Industry Use Case: NeoBank Digital Banking Platform

All exercises use a unified **FinTech Banking Platform** (NeoBank) as the industry context, providing realistic scenarios covering:
- Personal & Business Banking
- Investment Services  
- Lending & Credit
- Analytics & Reporting
- Compliance & Audit

---

## 📚 Exercise Index

| Part | Topics Covered | Exercises | Difficulty Range |
|------|---------------|-----------|------------------|
| [Setup](00-exercise-setup.md) | Database Foundation | 1 | 🟢 |
| [Part 1](01-fundamentals-exercises.md) | SQL Basics, Data Types | 6 | 🟢-🟡 |
| [Part 2](02-database-design-exercises.md) | Normalization, Constraints, Indexes, Views | 4 | 🟡-🔴 |
| [Part 3](03-advanced-querying-exercises.md) | Joins, Window Functions, CTEs, Aggregation | 5 | 🟡-🔴 |
| [Part 4](04-data-manipulation-exercises.md) | Transactions, Procedures, Triggers, Import/Export | 4 | 🟡-🔴 |
| [Part 5](05-performance-optimization-exercises.md) | Query Plans, Index Optimization, Partitioning, Vacuum | 5 | 🔴-⚫ |
| [Part 6](06-advanced-features-exercises.md) | Full-Text Search, JSON, Arrays, Extensions, FDW | 5 | 🟡-🔴 |
| [Part 7](07-security-exercises.md) | RBAC, Row-Level Security, Encryption, Audit | 4 | 🟡-🔴 |
| [Part 8](08-administration-exercises.md) | Configuration, Backup, Replication, Monitoring | 4 | 🔴-⚫ |
| [Part 9](09-special-topics-exercises.md) | Python/Node.js, Connection Pooling, MVCC | 4 | 🟡-🔴 |
| [Part 10](10-advanced-administration-exercises.md) | Tablespaces, Multi-Tenancy, Logical Replication, PITR | 5 | 🔴-⚫ |
| [Part 11](11-practical-applications-exercises.md) | Design Patterns, Migration, Troubleshooting | 4 | 🟡-⚫ |

---

## 🎯 Difficulty Levels

- 🟢 **Beginner** - Basic concepts, straightforward implementation
- 🟡 **Intermediate** - Requires understanding of multiple concepts
- 🔴 **Advanced** - Complex scenarios, production-level patterns
- ⚫ **Expert** - Deep internals knowledge, enterprise-grade solutions

---

## 🚀 Quick Start

### 1. Database Setup
```bash
# Create the NeoBank database
createdb neobank

# Run the setup script
psql -d neobank -f 00-exercise-setup.sql
```

### 2. Recommended Learning Path

**Week 1-2: Foundations**
- Complete Part 1: Fundamentals
- Complete Part 2: Database Design

**Week 3-4: Core Skills**
- Complete Part 3: Advanced Querying
- Complete Part 4: Data Manipulation

**Week 5-6: Performance**
- Complete Part 5: Performance Optimization
- Complete Part 6: Advanced Features

**Week 7-8: Operations**
- Complete Part 7: Security
- Complete Part 8: Administration

**Week 9-10: Expert Level**
- Complete Part 9: Special Topics
- Complete Part 10: Advanced Administration
- Complete Part 11: Practical Applications

---

## 📋 Prerequisites

- PostgreSQL 14+ installed
- Basic SQL knowledge
- Command-line familiarity
- Text editor or IDE (VS Code recommended)

### Required Extensions
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS tablefunc;
```

---

## 🏗️ NeoBank Schema Overview

```
banking/
├── customers          -- Customer profiles
├── accounts           -- Bank accounts
├── transactions       -- Financial transactions
├── transfers          -- Inter-account transfers
└── cards              -- Debit/Credit cards

lending/
├── loans              -- Loan records
├── loan_payments      -- Payment schedules
├── collateral         -- Loan collateral
└── credit_scores      -- Customer credit data

investments/
├── portfolios         -- Investment portfolios
├── holdings           -- Current holdings
└── market_data        -- Stock/Bond prices

analytics/
├── daily_summaries    -- Aggregated metrics
├── customer_segments  -- ML-based segments
└── fraud_scores       -- Real-time fraud detection

audit/
├── change_log         -- All data changes
├── access_log         -- Data access records
└── security_events    -- Security incidents
```

---

## 💡 Exercise Format

Each exercise follows this structure:

### Scenario
Real-world business problem from the banking domain.

### Requirements
Specific tasks and acceptance criteria.

### Solution
Complete, production-ready SQL code with:
- Step-by-step implementation
- Inline comments explaining key concepts
- Error handling and edge cases
- Performance considerations

### Practice Challenges
Additional problems to reinforce learning (solutions not provided).

---

## 🔗 Related Resources

- [PostgreSQL Complete Guide](../README.md) - Main documentation
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Wiki](https://wiki.postgresql.org/)

---

## 📝 Contributing

Found an issue or have suggestions? Please:
1. Open an issue describing the problem
2. Fork and submit a pull request
3. Follow the existing exercise format

---

**Happy Learning! 🐘**
