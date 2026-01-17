# Settlement and Clearing System

## Overview

Settlement and clearing are the post-trade processes that ensure the actual exchange of securities and cash between buyers and sellers. Clearing validates and guarantees trades, while settlement completes the transfer. The system must handle millions of daily transactions, maintain regulatory compliance, manage counterparty risk, and ensure finality of settlement with zero errors.

## Settlement Lifecycle

### T+0: Trade Date
The day a trade is executed. Activities: trade capture from matching engine, trade validation (verify all required fields present), trade enrichment (add settlement instructions, account details), trade confirmation generation (send to both parties), exception identification (mismatches, invalid accounts). Trade status: Pending. Internal deadline: trade capture within 1 minute of execution. Trade blotter updated in real-time for operations team visibility.

### T+1: Trade Date Plus One
First business day after trade. Activities: trade matching (compare buyer and seller details), affirmation (both parties agree to trade details), allocation (for block trades split among multiple accounts), trade correction (amend errors before settlement), pre-settlement instructions (confirm delivery accounts and payment methods). Common issues: allocation mismatches (block trades), settlement location disagreements, SSI (Standard Settlement Instructions) errors. Matching rate target: > 99.5% by end of T+1.

### T+2: Settlement Date
Second business day after trade, actual settlement occurs. Activities: confirmation of available securities (seller has shares to deliver), confirmation of available funds (buyer has cash to pay), simultaneous delivery vs payment (DVP), securities transfer to buyer's custodian, cash transfer to seller's account, settlement confirmation messages, update of positions and balances. Settlement window: typically 9 AM - 5 PM exchange time zone. Settlement methods: DTC (Depository Trust Company), FedWire, SWIFT.

### Failed Trade Resolution
Settlement fails occur when: seller doesn't have securities (short fail), buyer lacks funds (money fail), incorrect settlement instructions, custodian reject, corporate action timing. Resolution procedures: identify fails within 30 minutes of settlement time, contact counterparty immediately, buy-in procedures for aged fails (typically after T+5), mandatory close-out rules for persistent fails (Reg SHO for short sales). Failed trade aging reports track unresolved issues. Fail fees may apply depending on security type and market.

## Clearing House Functions

### Central Counterparty (CCP)
CCP interposes itself between buyer and seller, becoming buyer to every seller and seller to every buyer. Benefits: eliminates counterparty risk (CCP guarantees settlement), enables netting (reduce settlement obligations), provides anonymity (parties don't know counterparty), simplifies settlement (one relationship vs many). Major CCPs: DTCC (US securities), LCH (derivatives), CME (futures), ICE (energy, credit derivatives). CCP becomes counterparty at: point of trade execution (exchange-traded), post-trade submission (OTC trades submitted for clearing).

### Novation Process
Legal substitution of original trade with two new trades: Original trade: A sells to B, becomes: A sells to CCP, CCP sells to B. Occurs immediately after trade execution for exchange trades. Requires: legal agreements (clearing membership), margin posting, default fund contributions, rules acceptance. Novation timestamp recorded for audit. Non-clearable trades (bilateral OTC) retain original counterparty exposure.

### Netting
Reduce number of settlements by offsetting obligations. Bilateral netting: between two parties (buy 100 AAPL, sell 50 AAPL = net 50 buy). Multilateral netting: CCP nets all members (A owes B owes C owes A cycles simplified). Payment netting: net cash obligations (one payment instead of many). Securities netting: net security deliveries. Netting benefits: reduces settlement volume by 95%, decreases operational risk, reduces funding needs, minimizes transaction costs. Netting calculation performed: continuously during T+0 and T+1, final netting at end of T+1.

### Guarantee Function
CCP guarantees settlement even if member defaults. Default management: use defaulting member's margin first, tap default fund (mutualized loss sharing), CCP capital contribution, assessment powers (call for more funds from surviving members), controlled unwind of defaulting member positions. Default fund sizing: stress-tested to cover largest member default, recalculated quarterly, member contributions proportional to risk. Historical default events rare but include: Lehman Brothers (2008), MF Global (2011).

## Settlement Methods

### Delivery versus Payment (DVP)
Simultaneous exchange of securities for cash, conditional linkage. Neither leg settles unless both settle. Prevents: payment without delivery, delivery without payment. DVP models: Model 1 (gross settlement, trade-by-trade), Model 2 (gross securities, net cash), Model 3 (net securities, net cash). US markets primarily use Model 3 through DTCC. DVP implemented through: linked messages in settlement system, conditional release of securities and cash, atomic database transactions, rollback capability if either leg fails.

### Free of Payment (FOP)
Securities transfer without corresponding cash movement. Use cases: reorganizations (mergers, stock swaps), internal transfers (between accounts at same firm), pledge/collateral movements, return of borrowed securities (stock loan), error corrections. Higher operational risk: no offsetting cash validation, requires additional controls. FOP requires: explicit authorization, documented reason, supervisor approval, separate reconciliation process.

### Receipt versus Payment (RVP)
Buyer's perspective of DVP, receiving securities while paying cash. Terminology difference only, mechanically identical to DVP. Settlement instructions specify DVP (seller view) or RVP (buyer view). Systems must handle both terms equivalently.

### Continuous Net Settlement (CNS)
DTCC's system for equities and corporate bonds. Mechanism: accumulates all day's trades, nets to single position per member per security, settles net amount on T+2. Advantages: minimal movement of securities (most remain with DTCC), reduced transaction costs, automated good-til-cancel handling of unsettled positions. All US equity exchange trades automatically enter CNS unless specifically excluded.

## Settlement Instruction Management

### Standard Settlement Instructions (SSI)
Pre-agreed standing instructions between counterparties. Contains: custodian bank information, account numbers, settlement location, payment methods, contact information. SSI database: industry utilities (SWIFT, DTCC Directories), firm internal SSI database, third-party vendors. SSI validation before trade submission prevents settlement failures. SSI updates: communicated via SWIFT messages, effective dates specified, version control maintained.

### Settlement Instruction Matching
Compare buyer and seller instructions for agreement on: security identifier (CUSIP, ISIN, SEDOL), quantity, price, settlement date, settlement location (which depository), cash amounts including accrued interest. Matching occurs: on trade date (target: within 1 hour), overnight batch processing, continuous during T+1. Mismatches create exceptions requiring: investigation (who has error), correction (amend instruction), resubmission (to matching system), escalation (if parties disagree).

### SWIFT Messaging
Standard messaging for cross-border settlements. Message types: MT 540 (receive free), MT 541 (deliver free), MT 542 (deliver against payment), MT 543 (receive against payment), MT 544 (receive confirmation), MT 545 (deliver confirmation), MT 548 (settlement status). Message fields: transaction reference, quantity and security, settlement date, parties involved, cash amount and currency. ISO 20022 migration underway (XML-based, richer data).

### Local Market Practices
Each market has unique settlement conventions: settlement cycles (T+2 in US, T+0 in China A-shares), settlement currencies, business day calendars (local holidays), cut-off times, stamping requirements, tax withholding rules, registration procedures. System must handle: currency conversion for cross-border trades, withholding tax calculations, calendar adjustments for multi-market trades, local regulatory reporting.

## Corporate Actions Processing

### Dividend Payments
Cash dividends: record date determines shareholders of record, payment date (typically 2 weeks after record), entitlement calculation (shares owned × dividend per share), withholding tax application (varies by holder jurisdiction), payment to account. Stock dividends: additional shares instead of cash, adjust cost basis for tax purposes. Special dividends: one-time payments (mergers, asset sales). System must: identify entitled positions as of record date, calculate gross entitlement, apply tax withholding, credit/debit accounts, generate statements, adjust cost basis.

### Stock Splits
Forward split: increase share count, decrease price proportionally (e.g., 2-for-1 doubles shares, halves price). Reverse split: decrease share count, increase price (e.g., 1-for-10). Split processing: effective date (usually after market close), position quantity adjustment, price adjustment, option contract adjustments (strike and multiplier), historical data adjustment, fractional share handling (cash in lieu or rounding). Pre-split notification required for client notification and system preparation.

### Mergers and Acquisitions
Stock-for-stock: exchange shares of acquired company for shares of acquirer at specified ratio. Cash-for-stock: shareholders receive cash for their shares. Mixed consideration: combination of cash and stock. Processing: record date establishes shareholders, election deadline (if choice offered), proration if oversubscribed, entitlement calculation, deliver new securities/cash, remove old security from positions, tax reporting (cost basis, gain/loss). Voluntary actions require: election instructions from clients, election aggregation, submission to agent, receipt of proceeds.

### Rights Offerings
Existing shareholders given right to buy additional shares at discount. Subscription rights: tradeable instruments with value, exercise period (typically 2-4 weeks), subscription price (discount to market), oversubscription option (buy unsubscribed shares). Processing: credit rights to entitled shareholders, facilitate rights trading during exercise period, accept exercise instructions, collect subscription payments, deliver new shares, expire unexercised rights. Client communication critical to prevent value loss.

### Tender Offers and Proxies
Tender offers: acquirer offers to buy shares at premium, shareholders decide whether to tender, proration if oversubscribed. Proxy voting: annual meetings, board elections, merger approvals, shareholder proposals. System requirements: notification to clients (email, portal, mail), instruction collection, deadline monitoring, submission to agent, receipt of proceeds (tender), vote confirmation (proxy), regulatory reporting.

## Risk Management in Settlement

### Settlement Risk
Risk that counterparty defaults between trade and settlement. Principal risk: full value of transaction at risk (in non-DVP settlements). Replacement risk: cost to replace position if counterparty defaults. Mitigation: central clearing (CCP guarantee), DVP (simultaneous exchange), prefunding requirements, counterparty limits, settlement guarantee funds. Measurement: presettlement exposure (potential loss before settlement), settlement exposure (actual amounts in settlement).

### Liquidity Risk in Settlement
Risk of insufficient cash or securities to meet obligations. Causes: unexpected failures to receive, larger than expected settlements, timing mismatches, market disruptions. Management: intraday credit facilities, securities lending arrangements, cash pooling arrangements, settlement priorities (critical first), contingency funding plans. Central banks provide: discount window access, intraday overdrafts (for depository institutions), emergency liquidity facilities.

### Fails Management
Active management of settlement failures: categorize fails (fail to receive vs fail to deliver), prioritize resolution (age, value, counterparty), allocate available inventory (partial deliveries), buy-in procedures (force purchase), client communication (explain delays), regulatory reporting (fails statistics, aged fails). Fails tracking: fail date, fail reason, counterparty contact, resolution attempts, estimated resolution, client impact. Internal fails (one client fails, another waits) require: careful allocation, fairness procedures, communication to waiting client.

### Collateral Optimization
Efficient use of collateral across obligations: collateral types accepted (cash, government securities, corporate bonds, equities), haircuts applied (security type, credit rating, liquidity), collateral substitution (upgrade/downgrade), collateral transformation (borrow high-quality, post lower-quality), collateral pooling (aggregate across positions), automated optimization algorithms. Benefits: reduce cash drag, improve returns, minimize opportunity cost, maintain relationships with multiple counterparties.

## Reconciliation and Control

### Trade Matching and Comparison
Daily reconciliation: internal trade records vs exchange reports, internal records vs custodian reports, internal records vs clearing house reports. Key fields compared: trade ID, symbol, quantity, price, trade date, settlement date, counterparty. Breaks investigated: pricing differences (corporate actions, currency), quantity mismatches (allocations), missing trades (data feed issues), duplicate trades (message replay). Reconciliation must complete before settlement to prevent errors.

### Position Reconciliation
Compare positions across systems: trading system (real-time), settlement system (T+2 positions), custodian (actual holdings), general ledger (accounting). Reconciliation timing: end-of-day (critical), intraday (risk monitoring), post-settlement (confirm completeness). Break categories: timing differences (in-flight settlements), corporate actions (not yet processed), errors (data entry, system bugs), fraud (unauthorized activity). Reconciliation tolerance: zero tolerance for large breaks (> $10K), small breaks (<$100) may be auto-adjusted.

### Cash Reconciliation
Daily cash position verification: bank balances vs internal records, expected settlements vs actual, fees and charges vs agreements, foreign exchange adjustments vs rates used. Cash movements: trade settlements, dividend receipts, interest charges, wire transfers, fee debits. Reconciliation challenges: timing (same-day vs next-day value), multi-currency accounts, correspondent banking chains, fee transparency. Unidentified receipts require: investigation (who sent, why), contact originator, return if unmatched, regulatory reporting if suspicious.

### Nostro Reconciliation
For firms with custody accounts worldwide: nostro accounts (our account at their bank), automatic matching with bank statements, breaks investigation, claim for errors, interest verification. High volume requires: automated reconciliation tools, exception-based management, STP (straight-through processing) goals > 95%. Delays in resolution create: funding uncertainty, interest exposure, operational risk.

## Technology Infrastructure

### Settlement System Architecture
Core components: trade capture interface, trade validation engine, settlement instruction generator, matching platform, settlement queue manager, accounting interface, reporting engine. Database requirements: transactional consistency (ACID), high availability (99.99%), audit trail (immutable log), encryption at rest and transit. Integration points: trading platforms, clearing houses, custodians, banks, general ledger, regulatory reporting.

### Message Processing
High-volume message handling: SWIFT messages (MT and ISO 20022), FIX messages, exchange proprietary formats, internal APIs. Message flow: receipt, validation, enrichment, routing, acknowledgment, retry logic, error handling, archival. Processing patterns: real-time for trade messages, batch for settlements, event-driven for exceptions. Message queuing (Kafka, RabbitMQ) for: reliability, ordering guarantees, replay capability, load buffering.

### Straight-Through Processing (STP)
End-to-end automation without manual intervention. STP metrics: percentage of trades settling without touch (target > 95%), average touches per trade, cycle time from trade to settlement. STP enablers: data quality (accurate trade capture), SSI database (validated counterparty details), auto-matching (confirmation without phone calls), exception automation (rules-based resolution), integration (seamless system communication). STP benefits: reduced errors, lower costs, faster settlement, scalability.

### Disaster Recovery
Settlement systems are critical infrastructure requiring: RPO (Recovery Point Objective) = 0 (no data loss), RTO (Recovery Time Objective) < 4 hours. DR strategy: synchronous replication to DR site, automated failover procedures, regular DR testing (quarterly), documented runbooks, trained backup staff. Settlement cannot be delayed: regulatory and contractual obligations, market confidence, client expectations, cascading settlement dependencies.

## Regulatory Requirements

### Settlement Discipline Regime (CSDR)
European regulation imposing: mandatory buy-ins for settlement fails (after specified periods), cash penalties for late settlement (daily penalties increase over time), reporting of settlement fails, settlement efficiency targets. Systems must: track fail aging, calculate penalties automatically, execute buy-ins, report to regulators, maintain evidence of efforts to settle. Significant IT investment required for compliance.

### Depository Trust Company (DTCC) Rules
US settlement through DTC (Depository Trust Company): participants must maintain minimum net capital, daily settlement obligations must be met, default fund contributions required, operational standards for system connectivity, business continuity requirements. DTC monitors: participant financial health, settlement fails, system usage, risk indicators. DTC can: increase margin requirements, restrict participant activity, invoke default procedures.

### Securities Exchange Act Rule 15c3-3
Customer protection rule requiring: segregation of customer securities, reserve formula for customer cash, possession or control of securities (physical or book-entry), periodic verification of locations, deficiency resolution within one business day. Impact on settlement: must track customer vs proprietary positions, maintain segregated accounts, restrict use of customer securities, prove control through documentation.

### Global Securities Financing Regulation
Regulations affecting securities lending and collateral: SFTR (Securities Financing Transactions Regulation) in Europe, Dodd-Frank in US, Basel III capital and liquidity rules. Requirements: transaction reporting (all SFTs reported to trade repositories), transparency (aggregated data published), risk mitigation (haircuts, margin), capital treatment (exposure calculation). Settlement systems must: identify SFTs, capture regulatory fields, report to repositories, apply specific settlement procedures.

---

**Document Version**: 1.0  
**Last Updated**: January 17, 2026  
**Status**: Complete
