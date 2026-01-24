# Part 3: Advanced Querying Exercises

## Topics Covered
- Advanced SELECT Queries (Chapter 11)
- Joins and Subqueries (Chapter 12)
- Window Functions (Chapter 13)
- Common Table Expressions (Chapter 14)
- Aggregation and Grouping (Chapter 15)

---

## Sample Data Setup

First, let's ensure we have rich data to work with:

```sql
-- Generate more realistic transaction data
INSERT INTO banking.transactions (
    idempotency_key, reference_number, account_id, transaction_type,
    transaction_status, amount, channel, description, merchant_name,
    category, transaction_date, balance_after
)
SELECT 
    'TXN-' || gen_random_uuid()::text,
    'REF-' || TO_CHAR(d, 'YYYYMMDD') || '-' || LPAD(seq::text, 5, '0'),
    a.account_id,
    (ARRAY['deposit', 'withdrawal', 'card_purchase', 'transfer_out', 'atm_withdrawal'])[1 + floor(random() * 5)]::banking.transaction_type,
    'completed',
    CASE 
        WHEN random() < 0.3 THEN round((random() * 500 + 50)::numeric, 2)
        ELSE -round((random() * 200 + 10)::numeric, 2)
    END,
    (ARRAY['mobile_app', 'web', 'atm', 'branch'])[1 + floor(random() * 4)]::banking.transaction_channel,
    (ARRAY['Grocery Store', 'Gas Station', 'Online Purchase', 'Restaurant', 'Utility Bill', 'Transfer', 'ATM Withdrawal', 'Direct Deposit'])[1 + floor(random() * 8)],
    (ARRAY['Walmart', 'Shell', 'Amazon', 'Starbucks', 'Electric Co', NULL, NULL, 'Employer Inc'])[1 + floor(random() * 8)],
    (ARRAY['groceries', 'transportation', 'shopping', 'dining', 'utilities', 'transfer', 'cash', 'income'])[1 + floor(random() * 8)],
    d::date,
    NULL
FROM banking.accounts a
CROSS JOIN generate_series('2025-01-01'::date, '2026-01-23'::date, '1 day'::interval) d
CROSS JOIN generate_series(1, 3) seq
WHERE a.account_status = 'active'
  AND random() < 0.4  -- Not every day has transactions
ON CONFLICT DO NOTHING;

-- Update balance_after (simplified - in reality would be calculated properly)
WITH running_balance AS (
    SELECT 
        transaction_id,
        transaction_date,
        SUM(amount) OVER (
            PARTITION BY account_id 
            ORDER BY transaction_date, initiated_at
        ) + 5000 AS calculated_balance
    FROM banking.transactions
)
UPDATE banking.transactions t
SET balance_after = rb.calculated_balance
FROM running_balance rb
WHERE t.transaction_id = rb.transaction_id
  AND t.transaction_date = rb.transaction_date;
```

---

## Exercise 3.1: Complex Joins for Customer 360 View 🟡

### Scenario
The customer service team needs a comprehensive "Customer 360" view that shows everything about a customer in a single query - accounts, recent transactions, loans, and risk indicators.

### Requirements
1. Show customer details
2. List all accounts with balances
3. Show last 5 transactions per account
4. Include active loan information
5. Calculate risk indicators

### Solution

```sql
-- Customer 360 View Query
WITH customer_accounts AS (
    SELECT 
        c.customer_id,
        c.customer_number,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email,
        c.phone_primary,
        c.customer_status,
        c.kyc_status,
        c.risk_score AS customer_risk_score,
        c.created_at AS member_since,
        
        jsonb_agg(
            jsonb_build_object(
                'account_number', a.account_number,
                'account_type', a.account_type,
                'status', a.account_status,
                'current_balance', a.current_balance,
                'available_balance', a.available_balance
            ) ORDER BY a.is_primary DESC, a.account_type
        ) FILTER (WHERE a.account_id IS NOT NULL) AS accounts
    FROM banking.customers c
    LEFT JOIN banking.accounts a ON c.customer_id = a.customer_id
    WHERE c.customer_number = 'CUST-2026-00001'  -- Parameter
    GROUP BY c.customer_id
),

recent_transactions AS (
    SELECT 
        c.customer_id,
        jsonb_agg(
            jsonb_build_object(
                'account', a.account_number,
                'date', t.transaction_date,
                'type', t.transaction_type,
                'amount', t.amount,
                'description', t.description,
                'merchant', t.merchant_name
            ) ORDER BY t.transaction_date DESC, t.initiated_at DESC
        ) AS recent_transactions
    FROM banking.customers c
    JOIN banking.accounts a ON c.customer_id = a.customer_id
    JOIN LATERAL (
        SELECT *
        FROM banking.transactions t
        WHERE t.account_id = a.account_id
        ORDER BY t.transaction_date DESC, t.initiated_at DESC
        LIMIT 5
    ) t ON TRUE
    WHERE c.customer_number = 'CUST-2026-00001'
    GROUP BY c.customer_id
),

customer_loans AS (
    SELECT 
        c.customer_id,
        jsonb_agg(
            jsonb_build_object(
                'loan_number', l.loan_number,
                'type', lt.loan_type_code,
                'status', ls.status_code,
                'principal_balance', l.principal_balance,
                'monthly_payment', l.monthly_payment,
                'next_payment_date', l.next_payment_date,
                'days_past_due', l.days_past_due
            )
        ) FILTER (WHERE l.loan_id IS NOT NULL) AS loans
    FROM banking.customers c
    LEFT JOIN lending.loans l ON c.customer_id = l.customer_id
    LEFT JOIN lending.loan_types lt ON l.loan_type_id = lt.loan_type_id
    LEFT JOIN lending.loan_statuses ls ON l.status_id = ls.status_id
    WHERE c.customer_number = 'CUST-2026-00001'
    GROUP BY c.customer_id
),

risk_indicators AS (
    SELECT 
        c.customer_id,
        jsonb_build_object(
            'total_deposits', SUM(a.current_balance) FILTER (WHERE a.current_balance > 0),
            'total_debt', ABS(COALESCE(SUM(l.principal_balance), 0)),
            'debt_to_deposit_ratio', ROUND(
                COALESCE(SUM(l.principal_balance), 0) / 
                NULLIF(SUM(a.current_balance) FILTER (WHERE a.current_balance > 0), 0) * 100, 2
            ),
            'overdraft_count_30d', (
                SELECT COUNT(*) 
                FROM banking.transactions t2 
                JOIN banking.accounts a2 ON t2.account_id = a2.account_id
                WHERE a2.customer_id = c.customer_id 
                  AND t2.balance_after < 0
                  AND t2.transaction_date >= CURRENT_DATE - 30
            ),
            'avg_daily_spend', (
                SELECT ROUND(AVG(daily_spend)::numeric, 2)
                FROM (
                    SELECT ABS(SUM(t3.amount)) as daily_spend
                    FROM banking.transactions t3
                    JOIN banking.accounts a3 ON t3.account_id = a3.account_id
                    WHERE a3.customer_id = c.customer_id
                      AND t3.amount < 0
                      AND t3.transaction_date >= CURRENT_DATE - 30
                    GROUP BY t3.transaction_date
                ) daily
            )
        ) AS risk_indicators
    FROM banking.customers c
    LEFT JOIN banking.accounts a ON c.customer_id = a.customer_id
    LEFT JOIN lending.loans l ON c.customer_id = l.customer_id
    WHERE c.customer_number = 'CUST-2026-00001'
    GROUP BY c.customer_id
)

SELECT 
    ca.customer_number,
    ca.customer_name,
    ca.email,
    ca.phone_primary,
    ca.customer_status,
    ca.kyc_status,
    ca.customer_risk_score,
    ca.member_since,
    COALESCE(ca.accounts, '[]'::jsonb) AS accounts,
    COALESCE(rt.recent_transactions, '[]'::jsonb) AS recent_transactions,
    COALESCE(cl.loans, '[]'::jsonb) AS loans,
    COALESCE(ri.risk_indicators, '{}'::jsonb) AS risk_indicators
FROM customer_accounts ca
LEFT JOIN recent_transactions rt ON ca.customer_id = rt.customer_id
LEFT JOIN customer_loans cl ON ca.customer_id = cl.customer_id
LEFT JOIN risk_indicators ri ON ca.customer_id = ri.customer_id;
```

---

## Exercise 3.2: Window Functions for Transaction Analytics 🟡

### Scenario
Build a transaction analytics report showing running balances, transaction rankings, and spending patterns using window functions.

### Requirements
1. Running balance after each transaction
2. Rank transactions by amount within each month
3. Calculate moving average of spending
4. Identify the largest transaction per category
5. Show cumulative spending by category

### Solution

```sql
-- 1. Running balance with window function
SELECT 
    t.transaction_date,
    t.reference_number,
    t.transaction_type,
    t.amount,
    SUM(t.amount) OVER (
        PARTITION BY t.account_id 
        ORDER BY t.transaction_date, t.initiated_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_balance,
    a.account_number
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
WHERE a.account_number = 'ACC2026-00001-CHK'
  AND t.transaction_date >= '2026-01-01'
ORDER BY t.transaction_date, t.initiated_at;

-- 2. Rank transactions by amount within each month
WITH monthly_ranked AS (
    SELECT 
        t.transaction_date,
        t.reference_number,
        t.amount,
        t.description,
        DATE_TRUNC('month', t.transaction_date) AS month,
        RANK() OVER (
            PARTITION BY DATE_TRUNC('month', t.transaction_date)
            ORDER BY ABS(t.amount) DESC
        ) AS amount_rank,
        DENSE_RANK() OVER (
            PARTITION BY DATE_TRUNC('month', t.transaction_date)
            ORDER BY ABS(t.amount) DESC
        ) AS dense_amount_rank
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE a.account_number = 'ACC2026-00001-CHK'
      AND t.transaction_date >= '2025-10-01'
)
SELECT * FROM monthly_ranked
WHERE amount_rank <= 5
ORDER BY month DESC, amount_rank;

-- 3. 7-day moving average of spending
SELECT 
    t.transaction_date,
    SUM(t.amount) FILTER (WHERE t.amount < 0) AS daily_spending,
    ROUND(
        AVG(SUM(t.amount) FILTER (WHERE t.amount < 0)) OVER (
            ORDER BY t.transaction_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )::numeric, 2
    ) AS moving_avg_7d,
    ROUND(
        AVG(SUM(t.amount) FILTER (WHERE t.amount < 0)) OVER (
            ORDER BY t.transaction_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )::numeric, 2
    ) AS moving_avg_30d
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
WHERE c.customer_number = 'CUST-2026-00001'
  AND t.transaction_date >= '2025-12-01'
GROUP BY t.transaction_date
ORDER BY t.transaction_date;

-- 4. Largest transaction per category (DISTINCT ON approach)
SELECT DISTINCT ON (t.category)
    t.category,
    t.transaction_date,
    t.amount,
    t.description,
    t.merchant_name
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
WHERE a.customer_id = (
    SELECT customer_id FROM banking.customers WHERE customer_number = 'CUST-2026-00001'
)
AND t.category IS NOT NULL
ORDER BY t.category, ABS(t.amount) DESC;

-- Alternative using window functions
WITH ranked_by_category AS (
    SELECT 
        t.*,
        ROW_NUMBER() OVER (
            PARTITION BY t.category 
            ORDER BY ABS(t.amount) DESC
        ) AS rn
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = (
        SELECT customer_id FROM banking.customers WHERE customer_number = 'CUST-2026-00001'
    )
    AND t.category IS NOT NULL
)
SELECT 
    category,
    transaction_date,
    amount,
    description,
    merchant_name
FROM ranked_by_category
WHERE rn = 1
ORDER BY ABS(amount) DESC;

-- 5. Cumulative spending by category over time
SELECT 
    t.transaction_date,
    t.category,
    t.amount,
    SUM(t.amount) OVER (
        PARTITION BY t.category
        ORDER BY t.transaction_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_category_spending,
    SUM(t.amount) OVER (
        ORDER BY t.transaction_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_total
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
WHERE a.customer_id = (
    SELECT customer_id FROM banking.customers WHERE customer_number = 'CUST-2026-00001'
)
AND t.amount < 0
AND t.category IS NOT NULL
AND t.transaction_date >= '2026-01-01'
ORDER BY t.transaction_date, t.category;

-- 6. Comprehensive transaction analytics dashboard
SELECT 
    t.transaction_date,
    t.reference_number,
    t.transaction_type::text,
    t.amount,
    t.description,
    t.category,
    
    -- Running totals
    SUM(t.amount) OVER w_running AS running_balance,
    SUM(t.amount) FILTER (WHERE t.amount > 0) OVER w_running AS cumulative_credits,
    SUM(t.amount) FILTER (WHERE t.amount < 0) OVER w_running AS cumulative_debits,
    
    -- Rankings
    ROW_NUMBER() OVER w_date AS txn_number_today,
    RANK() OVER (ORDER BY ABS(t.amount) DESC) AS amount_rank_overall,
    
    -- Percentile
    PERCENT_RANK() OVER (ORDER BY ABS(t.amount)) AS amount_percentile,
    NTILE(4) OVER (ORDER BY ABS(t.amount)) AS amount_quartile,
    
    -- Comparisons
    t.amount - LAG(t.amount) OVER w_running AS diff_from_previous,
    t.amount - FIRST_VALUE(t.amount) OVER w_date AS diff_from_first_today,
    
    -- Category stats
    COUNT(*) OVER (PARTITION BY t.category) AS category_txn_count,
    SUM(t.amount) OVER (PARTITION BY t.category) AS category_total,
    ROUND(
        t.amount / NULLIF(SUM(t.amount) OVER (PARTITION BY t.category), 0) * 100, 
        2
    ) AS pct_of_category

FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
WHERE a.account_number = 'ACC2026-00001-CHK'
  AND t.transaction_date >= '2026-01-01'
WINDOW 
    w_running AS (ORDER BY t.transaction_date, t.initiated_at),
    w_date AS (PARTITION BY t.transaction_date ORDER BY t.initiated_at)
ORDER BY t.transaction_date DESC, t.initiated_at DESC
LIMIT 50;
```

---

## Exercise 3.3: CTEs for Loan Payment Scheduling 🟡

### Scenario
Create a loan amortization schedule using recursive CTEs. Given a loan, generate the complete payment schedule showing principal, interest, and balance for each payment.

### Requirements
1. Generate complete payment schedule
2. Calculate principal and interest breakdown per payment
3. Show running totals
4. Handle early payoff scenarios

### Solution

```sql
-- Loan Amortization Schedule using Recursive CTE
WITH RECURSIVE loan_params AS (
    -- Get loan parameters
    SELECT 
        l.loan_id,
        l.loan_number,
        l.principal_amount,
        l.interest_rate / 12 AS monthly_rate,  -- Convert annual to monthly
        l.term_months,
        l.monthly_payment,
        l.disbursement_date,
        l.first_payment_date
    FROM lending.loans l
    WHERE l.loan_number = 'LOAN-2026-00001'  -- Parameter
),

amortization_schedule AS (
    -- Base case: Payment 1
    SELECT 
        lp.loan_id,
        lp.loan_number,
        1 AS payment_number,
        lp.first_payment_date AS payment_date,
        lp.monthly_payment AS payment_amount,
        ROUND(lp.principal_amount * lp.monthly_rate, 2) AS interest_portion,
        ROUND(lp.monthly_payment - (lp.principal_amount * lp.monthly_rate), 2) AS principal_portion,
        ROUND(lp.principal_amount - (lp.monthly_payment - (lp.principal_amount * lp.monthly_rate)), 2) AS remaining_balance,
        lp.monthly_rate,
        lp.term_months,
        lp.monthly_payment AS base_payment
    FROM loan_params lp
    
    UNION ALL
    
    -- Recursive case: Subsequent payments
    SELECT 
        a.loan_id,
        a.loan_number,
        a.payment_number + 1,
        (a.payment_date + INTERVAL '1 month')::DATE,
        CASE 
            WHEN a.payment_number + 1 = a.term_months 
            THEN a.remaining_balance + ROUND(a.remaining_balance * a.monthly_rate, 2)  -- Final payment
            ELSE a.base_payment
        END,
        ROUND(a.remaining_balance * a.monthly_rate, 2),
        CASE 
            WHEN a.payment_number + 1 = a.term_months 
            THEN a.remaining_balance  -- Final payment pays off balance
            ELSE ROUND(a.base_payment - (a.remaining_balance * a.monthly_rate), 2)
        END,
        CASE 
            WHEN a.payment_number + 1 = a.term_months 
            THEN 0  -- Paid off
            ELSE ROUND(a.remaining_balance - (a.base_payment - (a.remaining_balance * a.monthly_rate)), 2)
        END,
        a.monthly_rate,
        a.term_months,
        a.base_payment
    FROM amortization_schedule a
    WHERE a.payment_number < a.term_months
      AND a.remaining_balance > 0
)

SELECT 
    loan_number,
    payment_number,
    payment_date,
    TO_CHAR(payment_amount, 'FM$999,999.00') AS payment,
    TO_CHAR(principal_portion, 'FM$999,999.00') AS principal,
    TO_CHAR(interest_portion, 'FM$999,999.00') AS interest,
    TO_CHAR(remaining_balance, 'FM$999,999,999.00') AS remaining_balance,
    
    -- Running totals
    TO_CHAR(SUM(principal_portion) OVER (ORDER BY payment_number), 'FM$999,999,999.00') AS total_principal_paid,
    TO_CHAR(SUM(interest_portion) OVER (ORDER BY payment_number), 'FM$999,999,999.00') AS total_interest_paid,
    
    -- Progress percentage
    ROUND(
        SUM(principal_portion) OVER (ORDER BY payment_number) / 
        SUM(principal_portion) OVER () * 100, 
        1
    ) AS percent_complete

FROM amortization_schedule
ORDER BY payment_number;

-- Early payoff analysis
WITH RECURSIVE loan_params AS (
    SELECT 
        10000.00 AS principal,
        0.08 / 12 AS monthly_rate,
        36 AS term_months,
        313.36 AS monthly_payment  -- Standard payment
),

-- Standard schedule
standard_schedule AS (
    SELECT 
        1 AS payment_number,
        lp.monthly_payment AS payment_amount,
        ROUND(lp.principal * lp.monthly_rate, 2) AS interest,
        ROUND(lp.monthly_payment - (lp.principal * lp.monthly_rate), 2) AS principal_paid,
        ROUND(lp.principal - (lp.monthly_payment - (lp.principal * lp.monthly_rate)), 2) AS balance,
        lp.monthly_rate,
        lp.term_months,
        lp.monthly_payment AS base_payment
    FROM loan_params lp
    
    UNION ALL
    
    SELECT 
        s.payment_number + 1,
        s.base_payment,
        ROUND(s.balance * s.monthly_rate, 2),
        ROUND(s.base_payment - (s.balance * s.monthly_rate), 2),
        GREATEST(0, ROUND(s.balance - (s.base_payment - (s.balance * s.monthly_rate)), 2)),
        s.monthly_rate,
        s.term_months,
        s.base_payment
    FROM standard_schedule s
    WHERE s.payment_number < s.term_months AND s.balance > 0
),

-- Extra payment schedule (extra $100/month)
extra_schedule AS (
    SELECT 
        1 AS payment_number,
        lp.monthly_payment + 100 AS payment_amount,
        ROUND(lp.principal * lp.monthly_rate, 2) AS interest,
        ROUND(lp.monthly_payment + 100 - (lp.principal * lp.monthly_rate), 2) AS principal_paid,
        ROUND(lp.principal - (lp.monthly_payment + 100 - (lp.principal * lp.monthly_rate)), 2) AS balance,
        lp.monthly_rate,
        lp.monthly_payment AS base_payment
    FROM loan_params lp
    
    UNION ALL
    
    SELECT 
        s.payment_number + 1,
        CASE WHEN s.balance < s.base_payment + 100 THEN s.balance + ROUND(s.balance * s.monthly_rate, 2) ELSE s.base_payment + 100 END,
        ROUND(s.balance * s.monthly_rate, 2),
        CASE WHEN s.balance < s.base_payment + 100 THEN s.balance ELSE ROUND(s.base_payment + 100 - (s.balance * s.monthly_rate), 2) END,
        GREATEST(0, ROUND(s.balance - (s.base_payment + 100 - (s.balance * s.monthly_rate)), 2)),
        s.monthly_rate,
        s.base_payment
    FROM extra_schedule s
    WHERE s.balance > 0
)

SELECT 
    'Standard' AS scenario,
    MAX(payment_number) AS total_payments,
    SUM(payment_amount) AS total_paid,
    SUM(interest) AS total_interest,
    NULL AS interest_saved,
    NULL AS payments_saved
FROM standard_schedule

UNION ALL

SELECT 
    'Extra $100/month',
    MAX(payment_number),
    SUM(payment_amount),
    SUM(interest),
    (SELECT SUM(interest) FROM standard_schedule) - SUM(interest),
    (SELECT MAX(payment_number) FROM standard_schedule) - MAX(payment_number)
FROM extra_schedule;
```

---

## Exercise 3.4: Aggregation for Financial Reporting 🟡

### Scenario
Generate monthly financial reports for the bank including account summaries, transaction volumes, and key metrics.

### Requirements
1. Monthly transaction summary by type
2. Account growth metrics
3. Revenue from fees and interest
4. Customer acquisition funnel

### Solution

```sql
-- 1. Monthly Transaction Summary
SELECT 
    DATE_TRUNC('month', t.transaction_date)::DATE AS month,
    t.transaction_type,
    COUNT(*) AS transaction_count,
    SUM(ABS(t.amount)) AS total_volume,
    AVG(ABS(t.amount))::NUMERIC(10,2) AS avg_amount,
    MIN(t.amount) AS min_amount,
    MAX(t.amount) AS max_amount,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(t.amount)) AS median_amount
FROM banking.transactions t
WHERE t.transaction_date >= DATE_TRUNC('year', CURRENT_DATE)
  AND t.transaction_status = 'completed'
GROUP BY DATE_TRUNC('month', t.transaction_date), t.transaction_type
ORDER BY month DESC, total_volume DESC;

-- 2. Monthly Metrics Dashboard
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', t.transaction_date)::DATE AS month,
        
        -- Transaction metrics
        COUNT(*) AS total_transactions,
        COUNT(DISTINCT t.account_id) AS active_accounts,
        
        -- Volume metrics
        SUM(t.amount) FILTER (WHERE t.amount > 0) AS total_deposits,
        SUM(ABS(t.amount)) FILTER (WHERE t.amount < 0) AS total_withdrawals,
        
        -- Fee revenue
        SUM(ABS(t.amount)) FILTER (WHERE t.transaction_type = 'fee') AS fee_revenue,
        
        -- Average balances
        AVG(t.balance_after) AS avg_balance,
        
        -- Channel breakdown
        COUNT(*) FILTER (WHERE t.channel = 'mobile_app') AS mobile_transactions,
        COUNT(*) FILTER (WHERE t.channel = 'web') AS web_transactions,
        COUNT(*) FILTER (WHERE t.channel = 'atm') AS atm_transactions,
        COUNT(*) FILTER (WHERE t.channel = 'branch') AS branch_transactions
        
    FROM banking.transactions t
    WHERE t.transaction_status = 'completed'
    GROUP BY DATE_TRUNC('month', t.transaction_date)
),

account_metrics AS (
    SELECT 
        DATE_TRUNC('month', a.opened_at)::DATE AS month,
        COUNT(*) AS new_accounts,
        SUM(a.current_balance) AS initial_deposits
    FROM banking.accounts a
    GROUP BY DATE_TRUNC('month', a.opened_at)
),

customer_metrics AS (
    SELECT 
        DATE_TRUNC('month', c.created_at)::DATE AS month,
        COUNT(*) AS new_customers,
        COUNT(*) FILTER (WHERE c.customer_status = 'active') AS activated_customers
    FROM banking.customers c
    GROUP BY DATE_TRUNC('month', c.created_at)
)

SELECT 
    mm.month,
    mm.total_transactions,
    mm.active_accounts,
    TO_CHAR(mm.total_deposits, 'FM$999,999,999.00') AS deposits,
    TO_CHAR(mm.total_withdrawals, 'FM$999,999,999.00') AS withdrawals,
    TO_CHAR(mm.fee_revenue, 'FM$999,999.00') AS fee_revenue,
    TO_CHAR(mm.avg_balance, 'FM$999,999.00') AS avg_balance,
    
    -- Channel percentages
    ROUND(mm.mobile_transactions::numeric / NULLIF(mm.total_transactions, 0) * 100, 1) AS mobile_pct,
    ROUND(mm.web_transactions::numeric / NULLIF(mm.total_transactions, 0) * 100, 1) AS web_pct,
    
    -- Growth metrics
    COALESCE(am.new_accounts, 0) AS new_accounts,
    COALESCE(cm.new_customers, 0) AS new_customers,
    
    -- Month-over-month changes
    mm.total_transactions - LAG(mm.total_transactions) OVER (ORDER BY mm.month) AS txn_mom_change,
    ROUND(
        (mm.total_transactions - LAG(mm.total_transactions) OVER (ORDER BY mm.month))::numeric / 
        NULLIF(LAG(mm.total_transactions) OVER (ORDER BY mm.month), 0) * 100, 
        1
    ) AS txn_mom_pct

FROM monthly_metrics mm
LEFT JOIN account_metrics am ON mm.month = am.month
LEFT JOIN customer_metrics cm ON mm.month = cm.month
ORDER BY mm.month DESC;

-- 3. Customer Cohort Analysis
WITH customer_cohorts AS (
    SELECT 
        c.customer_id,
        DATE_TRUNC('month', c.created_at)::DATE AS cohort_month,
        DATE_TRUNC('month', t.transaction_date)::DATE AS activity_month
    FROM banking.customers c
    JOIN banking.accounts a ON c.customer_id = a.customer_id
    JOIN banking.transactions t ON a.account_id = t.account_id
),

cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),

cohort_activity AS (
    SELECT 
        cohort_month,
        activity_month,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM customer_cohorts
    GROUP BY cohort_month, activity_month
)

SELECT 
    ca.cohort_month,
    cs.cohort_size,
    ca.activity_month,
    EXTRACT(MONTH FROM AGE(ca.activity_month, ca.cohort_month))::INT AS months_since_join,
    ca.active_customers,
    ROUND(ca.active_customers::numeric / cs.cohort_size * 100, 1) AS retention_rate
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
WHERE ca.activity_month >= ca.cohort_month
ORDER BY ca.cohort_month, ca.activity_month;

-- 4. Spending Category Analysis with GROUPING SETS
SELECT 
    COALESCE(c.category, 'ALL CATEGORIES') AS category,
    COALESCE(DATE_TRUNC('month', t.transaction_date)::DATE::TEXT, 'ALL MONTHS') AS month,
    COUNT(*) AS transaction_count,
    SUM(ABS(t.amount)) AS total_spent,
    AVG(ABS(t.amount))::NUMERIC(10,2) AS avg_spent,
    COUNT(DISTINCT t.account_id) AS unique_accounts,
    GROUPING(c.category, DATE_TRUNC('month', t.transaction_date)) AS grouping_level
FROM banking.transactions t
LEFT JOIN (
    SELECT transaction_id, transaction_date, category
    FROM banking.transactions
    WHERE category IS NOT NULL
) c ON t.transaction_id = c.transaction_id AND t.transaction_date = c.transaction_date
WHERE t.amount < 0
  AND t.transaction_date >= '2025-07-01'
GROUP BY GROUPING SETS (
    (c.category, DATE_TRUNC('month', t.transaction_date)),  -- Category by month
    (c.category),                                            -- Category totals
    (DATE_TRUNC('month', t.transaction_date)),              -- Monthly totals
    ()                                                        -- Grand total
)
ORDER BY 
    grouping_level,
    category NULLS LAST,
    month NULLS LAST;
```

---

## Exercise 3.5: Subqueries for Fraud Detection 🔴

### Scenario
Build fraud detection queries to identify suspicious transaction patterns.

### Requirements
1. Find accounts with unusual transaction frequency
2. Detect velocity attacks (many transactions in short time)
3. Identify geographic anomalies
4. Flag transactions significantly above customer average

### Solution

```sql
-- 1. Accounts with unusual transaction frequency (statistical anomaly)
WITH account_stats AS (
    SELECT 
        account_id,
        COUNT(*) AS txn_count,
        AVG(COUNT(*)) OVER () AS avg_txn_count,
        STDDEV(COUNT(*)) OVER () AS stddev_txn_count
    FROM banking.transactions
    WHERE transaction_date >= CURRENT_DATE - 30
    GROUP BY account_id
)
SELECT 
    a.account_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    s.txn_count,
    ROUND(s.avg_txn_count::numeric, 2) AS avg_txn_count,
    ROUND((s.txn_count - s.avg_txn_count) / NULLIF(s.stddev_txn_count, 0), 2) AS z_score,
    CASE 
        WHEN (s.txn_count - s.avg_txn_count) / NULLIF(s.stddev_txn_count, 0) > 3 THEN 'HIGH ALERT'
        WHEN (s.txn_count - s.avg_txn_count) / NULLIF(s.stddev_txn_count, 0) > 2 THEN 'MEDIUM ALERT'
        ELSE 'NORMAL'
    END AS alert_level
FROM account_stats s
JOIN banking.accounts a ON s.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
WHERE (s.txn_count - s.avg_txn_count) / NULLIF(s.stddev_txn_count, 0) > 2
ORDER BY z_score DESC;

-- 2. Velocity attack detection (many transactions in short window)
WITH transaction_windows AS (
    SELECT 
        t.account_id,
        t.transaction_id,
        t.transaction_date,
        t.initiated_at,
        t.amount,
        t.merchant_name,
        COUNT(*) OVER (
            PARTITION BY t.account_id 
            ORDER BY t.initiated_at 
            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
        ) AS txn_count_1h,
        SUM(ABS(t.amount)) OVER (
            PARTITION BY t.account_id 
            ORDER BY t.initiated_at 
            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
        ) AS amount_1h,
        COUNT(*) OVER (
            PARTITION BY t.account_id 
            ORDER BY t.initiated_at 
            RANGE BETWEEN INTERVAL '10 minutes' PRECEDING AND CURRENT ROW
        ) AS txn_count_10m
    FROM banking.transactions t
    WHERE t.transaction_date >= CURRENT_DATE - 7
)
SELECT 
    a.account_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    tw.transaction_date,
    tw.initiated_at,
    tw.amount,
    tw.merchant_name,
    tw.txn_count_1h AS transactions_last_hour,
    tw.amount_1h AS amount_last_hour,
    tw.txn_count_10m AS transactions_last_10min,
    CASE 
        WHEN tw.txn_count_10m > 5 THEN 'CRITICAL: Card testing suspected'
        WHEN tw.txn_count_1h > 20 THEN 'HIGH: Unusual velocity'
        WHEN tw.amount_1h > 5000 THEN 'MEDIUM: High volume'
        ELSE 'LOW'
    END AS risk_level
FROM transaction_windows tw
JOIN banking.accounts a ON tw.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
WHERE tw.txn_count_1h > 10 OR tw.txn_count_10m > 3
ORDER BY tw.initiated_at DESC;

-- 3. Geographic anomaly detection (impossible travel)
WITH location_sequences AS (
    SELECT 
        t.account_id,
        t.transaction_id,
        t.initiated_at,
        t.location_city,
        t.location_state,
        t.location_country,
        LAG(t.initiated_at) OVER w AS prev_time,
        LAG(t.location_city) OVER w AS prev_city,
        LAG(t.location_state) OVER w AS prev_state,
        LAG(t.location_country) OVER w AS prev_country,
        EXTRACT(EPOCH FROM (t.initiated_at - LAG(t.initiated_at) OVER w)) / 3600 AS hours_between
    FROM banking.transactions t
    WHERE t.location_city IS NOT NULL
      AND t.transaction_date >= CURRENT_DATE - 7
    WINDOW w AS (PARTITION BY t.account_id ORDER BY t.initiated_at)
)
SELECT 
    a.account_number,
    ls.initiated_at,
    ls.prev_city || ', ' || ls.prev_state AS previous_location,
    ls.location_city || ', ' || ls.location_state AS current_location,
    ROUND(ls.hours_between::numeric, 2) AS hours_between,
    'IMPOSSIBLE TRAVEL DETECTED' AS alert
FROM location_sequences ls
JOIN banking.accounts a ON ls.account_id = a.account_id
WHERE ls.prev_city IS NOT NULL
  AND ls.location_city != ls.prev_city
  AND ls.prev_state != ls.location_state
  AND ls.hours_between < 2  -- Less than 2 hours between different cities/states
ORDER BY ls.initiated_at DESC;

-- 4. Transactions above customer average (anomaly detection)
WITH customer_baselines AS (
    SELECT 
        a.customer_id,
        t.category,
        AVG(ABS(t.amount)) AS avg_amount,
        STDDEV(ABS(t.amount)) AS stddev_amount,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ABS(t.amount)) AS p95_amount
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE t.transaction_date >= CURRENT_DATE - 90
      AND t.amount < 0
    GROUP BY a.customer_id, t.category
    HAVING COUNT(*) >= 5  -- Minimum transactions for baseline
)
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    t.transaction_date,
    t.amount,
    t.merchant_name,
    t.category,
    cb.avg_amount AS customer_avg_for_category,
    cb.p95_amount AS customer_p95_for_category,
    ROUND((ABS(t.amount) - cb.avg_amount) / NULLIF(cb.stddev_amount, 0), 2) AS z_score,
    CASE 
        WHEN ABS(t.amount) > cb.p95_amount * 2 THEN 'CRITICAL'
        WHEN ABS(t.amount) > cb.p95_amount THEN 'HIGH'
        WHEN (ABS(t.amount) - cb.avg_amount) / NULLIF(cb.stddev_amount, 0) > 2 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS anomaly_level
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
JOIN customer_baselines cb ON a.customer_id = cb.customer_id 
    AND COALESCE(t.category, 'unknown') = COALESCE(cb.category, 'unknown')
WHERE t.transaction_date >= CURRENT_DATE - 7
  AND t.amount < 0
  AND (
    ABS(t.amount) > cb.p95_amount 
    OR (ABS(t.amount) - cb.avg_amount) / NULLIF(cb.stddev_amount, 0) > 2
  )
ORDER BY 
    CASE 
        WHEN ABS(t.amount) > cb.p95_amount * 2 THEN 1
        WHEN ABS(t.amount) > cb.p95_amount THEN 2
        ELSE 3
    END,
    t.initiated_at DESC;

-- 5. Comprehensive fraud scoring query
WITH fraud_indicators AS (
    SELECT 
        t.transaction_id,
        t.transaction_date,
        t.account_id,
        t.amount,
        t.merchant_name,
        
        -- Velocity indicators
        COUNT(*) OVER (
            PARTITION BY t.account_id 
            ORDER BY t.initiated_at 
            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
        ) AS txn_velocity_1h,
        
        -- Amount anomaly
        ABS(t.amount) / NULLIF(AVG(ABS(t.amount)) OVER (PARTITION BY t.account_id), 0) AS amount_ratio,
        
        -- Time of day (unusual hours)
        EXTRACT(HOUR FROM t.initiated_at) AS txn_hour,
        
        -- Round amount (common in fraud)
        CASE WHEN MOD(ABS(t.amount)::numeric, 100) = 0 THEN 1 ELSE 0 END AS round_amount_flag,
        
        -- Declined indicator (if we had it)
        CASE WHEN t.transaction_status = 'failed' THEN 1 ELSE 0 END AS declined_flag
        
    FROM banking.transactions t
    WHERE t.transaction_date >= CURRENT_DATE - 1
)
SELECT 
    fi.*,
    a.account_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    
    -- Calculate fraud score (0-100)
    LEAST(100, (
        CASE WHEN fi.txn_velocity_1h > 10 THEN 30 ELSE fi.txn_velocity_1h * 2 END +
        CASE WHEN fi.amount_ratio > 5 THEN 30 WHEN fi.amount_ratio > 2 THEN 15 ELSE 0 END +
        CASE WHEN fi.txn_hour BETWEEN 1 AND 5 THEN 15 ELSE 0 END +
        fi.round_amount_flag * 10 +
        fi.declined_flag * 20
    )) AS fraud_score
    
FROM fraud_indicators fi
JOIN banking.accounts a ON fi.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
ORDER BY fraud_score DESC
LIMIT 100;
```

---

## 🎯 Practice Challenges

### Challenge 3.1 🟡
Write a query to find customers who have increased their average transaction size by more than 50% month-over-month.

### Challenge 3.2 🔴
Create a query that identifies "churning" customers - those whose transaction frequency has dropped by more than 75% compared to their first 3 months.

### Challenge 3.3 🔴
Build a merchant category recommendation system using transaction history and collaborative filtering (customers who spent at X also spent at Y).

---

**Next: [Part 4 - Data Manipulation Exercises](04-data-manipulation-exercises.md)**
