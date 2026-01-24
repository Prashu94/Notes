# PostgreSQL Hands-On Exercises - Setup

## Industry Use Case: NeoBank - A Digital Banking Platform

Throughout these exercises, you'll build and work with the database for **NeoBank**, a modern digital banking platform that offers:

- **Personal Banking**: Checking/savings accounts, transfers, bill payments
- **Investment Services**: Stock trading, mutual funds, portfolio management
- **Lending**: Personal loans, credit cards, mortgages
- **Business Banking**: Business accounts, payroll, invoicing
- **Analytics**: Spending insights, fraud detection, customer analytics

## Why This Use Case?

FinTech/Banking is ideal for learning PostgreSQL because it requires:
- **ACID compliance** for financial transactions
- **Complex queries** for reporting and analytics
- **High performance** for real-time operations
- **Strong security** with audit trails
- **Data integrity** with strict constraints
- **Scalability** for millions of transactions

## Database Setup

### Step 1: Create the Database

```sql
-- Connect as superuser
-- Create dedicated database
CREATE DATABASE neobank
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Connect to neobank
\c neobank
```

### Step 2: Create Schemas

```sql
-- Core banking operations
CREATE SCHEMA banking;

-- Investment and trading
CREATE SCHEMA investments;

-- Lending products
CREATE SCHEMA lending;

-- Analytics and reporting
CREATE SCHEMA analytics;

-- Audit and compliance
CREATE SCHEMA audit;

-- Set default search path
SET search_path TO banking, investments, lending, analytics, audit, public;
```

### Step 3: Create Application Roles

```sql
-- Application roles
CREATE ROLE neobank_admin WITH LOGIN PASSWORD 'admin_secure_pwd';
CREATE ROLE neobank_app WITH LOGIN PASSWORD 'app_secure_pwd';
CREATE ROLE neobank_readonly WITH LOGIN PASSWORD 'readonly_pwd';
CREATE ROLE neobank_analyst WITH LOGIN PASSWORD 'analyst_pwd';

-- Grant schema access
GRANT ALL ON SCHEMA banking, investments, lending, analytics, audit TO neobank_admin;
GRANT USAGE ON SCHEMA banking, investments, lending TO neobank_app;
GRANT USAGE ON SCHEMA banking, analytics TO neobank_readonly, neobank_analyst;
```

## Core Domain Tables (Reference)

These tables will be built progressively through the exercises:

```
banking.customers          - Customer profiles and KYC data
banking.accounts           - Bank accounts (checking, savings, etc.)
banking.transactions       - All financial transactions
banking.transfers          - Money transfers between accounts
banking.cards              - Debit/credit cards

investments.portfolios     - Investment portfolios
investments.holdings       - Stock/fund holdings
investments.trades         - Buy/sell orders
investments.market_data    - Stock prices and market info

lending.loans              - Loan applications and details
lending.payments           - Loan payments
lending.credit_scores      - Customer credit information

analytics.spending_categories - Spending categorization
analytics.customer_segments   - Customer segmentation
analytics.daily_summaries     - Aggregated daily metrics

audit.activity_log         - All user activities
audit.data_changes         - Change data capture
```

## Exercise Difficulty Levels

- 🟢 **Beginner**: Basic concepts, straightforward solutions
- 🟡 **Intermediate**: Requires combining multiple concepts
- 🔴 **Advanced**: Complex scenarios, optimization required
- ⚫ **Expert**: Production-grade, edge cases, performance critical

## How to Use These Exercises

1. **Read the scenario** - Understand the business requirement
2. **Try it yourself** - Attempt before looking at solutions
3. **Compare solutions** - Check your approach vs provided solution
4. **Experiment** - Modify and extend the exercises
5. **Measure** - Use EXPLAIN ANALYZE to understand performance

---

**Ready? Let's start building NeoBank!**
