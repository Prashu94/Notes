# Order Management System (OMS)

## Overview

The Order Management System is the primary interface between traders and the exchange. It handles order lifecycle from submission through execution, modification, and cancellation. The OMS must maintain state consistency, ensure idempotency, perform validation, and integrate with risk management systems.

## Core Responsibilities

### Order Lifecycle Management
The OMS tracks orders through multiple states: Pending → Validated → Routed → Accepted → Partially Filled → Filled → Cancelled → Rejected. Each state transition triggers events and updates to downstream systems. State machines ensure atomic transitions and prevent invalid state changes.

### Order Validation
Multi-layer validation occurs at submission: syntax validation (required fields, data types), semantic validation (price tick size, lot size), business rules (market hours, circuit breakers), and risk checks (buying power, position limits). Validation failures result in immediate rejection with descriptive error codes.

### Idempotency and Deduplication
Every order includes a client-generated idempotency key (UUID). The system maintains a cache (Redis) of recent order IDs with TTL of 24 hours. Duplicate submissions return the original order status without creating new orders. This prevents accidental double-orders during network retries.

### Order Routing
Intelligent order routing selects optimal execution venues based on: symbol availability, order type support, liquidity depth, maker-taker fees, latency requirements, and regulatory constraints. Smart order routing (SOR) algorithms split large orders across multiple venues for best execution.

## Architecture Components

### Order Gateway
Acts as the entry point for all order traffic. Handles protocol translation (FIX, REST, WebSocket, gRPC), authentication token validation, rate limiting per user/API key, request logging, and load distribution. Multiple gateway instances behind load balancers provide horizontal scalability and failover capability.

### Order Validator Service
Stateless microservice performing synchronous validation. Maintains reference data cache (symbols, tick sizes, trading hours) refreshed every minute. Implements circuit breaker pattern when calling external services. Validation rules are configuration-driven and externalized for rapid updates without code deployment.

### Order Router Service
Determines execution destination using routing tables and algorithms. Considers: symbol-to-venue mapping, order characteristics (size, urgency), current market conditions (spread, depth), and cost optimization. Maintains connection pools to multiple execution venues with health monitoring.

### Order State Manager
Central repository of order state using event sourcing pattern. All state changes are events stored in Kafka with compaction. Maintains materialized views in PostgreSQL for querying. Provides strong consistency guarantees through optimistic locking and version numbering.

### Order Book Service (Shadow Book)
Maintains local copy of exchange order book for each symbol. Receives real-time updates from matching engine via multicast or Kafka. Used for price improvement logic, fill estimation, and client-facing order book displays. Implements conflict-free replicated data types (CRDTs) for eventual consistency across replicas.

## Order Types Support

### Market Orders
Execute immediately at best available price. No price limit specified. Guaranteed fill (unless insufficient liquidity). Risk of slippage in volatile markets. Typically used when speed is priority over price.

### Limit Orders
Execute only at specified price or better. May remain unfilled if price not reached. Provides price certainty but no execution guarantee. Most common order type, representing 70-80% of all orders.

### Stop Orders
Trigger when market price reaches stop price. Becomes market order upon trigger. Used for: stop-loss (limit downside), breakout trading (momentum entry). Stop price monitored by OMS, not exchange (exchange only sees resulting market order).

### Stop-Limit Orders
Combines stop and limit functionality. Triggers at stop price but executes as limit order. Provides both trigger control and price protection. Risk of non-execution if price gaps through limit after trigger.

### Iceberg Orders (Hidden Quantity)
Display only portion of total quantity. Refreshes displayed quantity as filled. Reduces market impact for large orders. Implementation requires tracking visible vs total quantity and automatic replenishment logic.

### Fill-or-Kill (FOK)
Execute entire quantity immediately or cancel completely. No partial fills allowed. Used when position must be established atomically. Requires matching engine support for atomic execution check.

### Immediate-or-Cancel (IOC)
Execute immediately whatever quantity available, cancel remainder. Allows partial fills but no resting on book. Used for quick liquidity probes or avoiding stale orders.

### Good-Till-Cancelled (GTC)
Remains active until filled or explicitly cancelled. Persists across trading sessions. Requires daily revalidation of account status and symbol eligibility.

### Good-Till-Date (GTD)
Active until specified date/time. Automatic cancellation at expiry. Used for conditional strategies or planned exits.

### Day Orders
Automatically expire at market close. Most common time-in-force. Prevents unintended overnight positions.

## Order Modification and Cancellation

### Modification Strategies
Price-only modifications: Maintain time priority if reducing price (buy) or increasing price (sell). Lose priority if improving limit price. Quantity modifications: Increases lose time priority. Decreases maintain priority for remaining quantity.

### Cancel-Replace Protocol
Standard FIX approach: send cancel request for original order, wait for confirmation, then submit replacement. Maintains atomicity through transaction IDs linking cancel and replace. Fallback to original order if replace rejected.

### Mass Cancellation
Cancel all orders for: specific symbol, specific side (buy/sell), entire account, specific strategy ID. Implemented as batched operations with transaction boundaries. Critical for risk management in emergency situations.

### Amendment Rejection Handling
If modification rejected (order already filled, order not found, price out of bounds), system reverts to original order state. Client receives rejection notice with reason code. Audit trail captures all attempted modifications.

## Integration Points

### Risk Management Integration
Pre-trade risk check is synchronous operation before order routing. Checks: available buying power, position limits, concentration limits, regulatory limits (Reg T), gross exposure limits. Risk rejection prevents order from reaching exchange.

### Position Management Integration
Real-time position updates on every fill. Calculates: net position, average entry price, unrealized P&L, realized P&L, cost basis. Position updates trigger risk recalculation and margin requirement adjustments.

### Market Data Integration
OMS subscribes to: last trade price, best bid/offer, order book depth (L2), trade volume. Used for: stop order monitoring, market-if-touched orders, price validation, fill estimation display.

### Trade Management Integration
Upon execution confirmation from exchange, OMS: updates order status, publishes trade event to Kafka, triggers position update, generates client notification, logs to audit trail, triggers settlement process.

## Performance Characteristics

### Latency Requirements
Order submission to validation: < 1ms. Validation to routing: < 2ms. Routing to exchange: < 5ms. Total order submission to exchange acknowledgment: < 10ms (p95), < 20ms (p99).

### Throughput Requirements
Handle 100,000 orders per second sustained, 500,000 orders per second peak (market open). Process 50,000 modifications per second. Execute 10,000 cancellations per second. Support 1 million concurrent active orders across all symbols.

### Data Volume
Store 100 million orders per day. Retain order history for 7 years (regulatory requirement). Each order record ~2KB with all audit fields. Daily storage requirement: 200GB compressed.

## State Management and Recovery

### Event Sourcing Pattern
Every order operation (submit, modify, cancel, fill) is an immutable event. Events stored in Kafka with infinite retention (compaction enabled). Current state derived by replaying events. Enables: complete audit trail, point-in-time reconstruction, multiple materialized views.

### Snapshotting Strategy
Periodic snapshots of order state taken every 10,000 events or 5 minutes. Snapshots stored in PostgreSQL and S3. Recovery process: load latest snapshot, replay events since snapshot. Reduces recovery time from hours to minutes.

### Write-Ahead Logging
Critical operations logged to WAL before execution. WAL persisted to durable storage (SSD RAID 10). Enables crash recovery with RPO of seconds. WAL entries include: timestamp, sequence number, operation type, full order details, checksum.

### State Replication
Active-active replication across multiple data centers. Conflict resolution using last-write-wins with vector clocks. Cross-region latency typically 50-100ms. Prioritizes availability over consistency for reads, strong consistency for writes.

## Order Matching Priority

### Price Priority
Better price always executes first. Buy orders: higher price has priority. Sell orders: lower price has priority. Price improvement against current market is automatic.

### Time Priority
At same price level, earlier orders execute first. Timestamp precision: microseconds (exchange) to milliseconds (OMS). Clock synchronization via PTP critical for fairness. Exchange timestamp is authoritative, not client submission time.

### Display Priority (Some Markets)
Displayed orders may have priority over hidden orders at same price-time. Encourages market transparency and liquidity provision. Implementation varies by exchange and instrument type.

### Pro-Rata Matching
Alternative to price-time: fills allocated proportionally to order size. Used in some futures markets. Encourages larger orders and deeper liquidity. May include minimum allocation threshold.

## Order Book Display and Market Depth

### Level 1 (Top of Book)
Best bid price and quantity, best ask price and quantity, last trade price and size, trade timestamp. Updated on every order book change. Most lightweight data feed. Sufficient for basic trading decisions.

### Level 2 (Market Depth)
Full order book showing multiple price levels (typically 10-20 levels each side). Shows total quantity at each price level. Does not show individual order details. Updated on every book change. Essential for liquidity analysis.

### Level 3 (Full Depth)
Complete order book with individual order IDs and quantities. Market maker view, not typically available to public. Shows exact queue position. Required for sophisticated market making algorithms.

### Aggregated View
Combines orders at same price level into single entry. Shows total quantity and order count. Reduces bandwidth and processing requirements. Standard view for most retail investors.

## Regulatory Compliance

### Order Audit Trail (CAT)
Consolidated Audit Trail captures: order receipt time (microsecond precision), order routing decisions, order modifications, execution details, customer account information, trading desk information. Required by SEC for all US equity and options trades.

### Best Execution Requirements
Document routing decisions and execution quality. Quarterly reports comparing execution prices to NBBO (National Best Bid Offer). Track: price improvement percentage, fill rates, speed of execution, effective spread costs.

### Market Access Rules
Pre-trade risk checks mandated by SEC Rule 15c3-5. Maximum order size limits, credit limits, duplicate order prevention, market disruption prevention, regulatory halt compliance.

### Order Tagging
Tag orders with: customer type (retail, institutional, market maker), order capacity (principal, agency), algorithmic indicator, short sale indicator. Tags used for regulatory reporting and market surveillance.

## Error Handling and Circuit Breakers

### Order Rejection Handling
Rejections categorized: syntax errors (immediate), risk checks (pre-trade), exchange rejections (post-routing). Each rejection has specific error code and human-readable message. Automatic retry only for transient network errors.

### Circuit Breakers
Trading halts triggered by: rapid price movements (>10% in 5 minutes), order book imbalance (>90% one side), system capacity issues, regulatory halt. Halt procedures: pause new orders, allow cancellations only, publish halt notification, maintain order book state.

### Kill Switch
Emergency stop for: rogue algorithm detection, risk limit breach, operational error, regulatory order. Activated via: automated triggers, manual admin action, exchange directive. Actions: cancel all pending orders, reject new submissions, close out positions if required.

### Throttling and Rate Limiting
Per-user limits: 100 orders/second, 1000 orders/minute. Per-API key limits: custom based on client tier. Burst allowance: 2x normal rate for 10 seconds. Exceeded limits result in: temporary rejection, exponential backoff requirement, possible account restriction.

## Technology Stack Recommendations

### Programming Languages
Core OMS logic: Java (Spring Boot) or Go for performance and concurrency. State management: Rust for memory safety. Gateway services: Go for high throughput. Event processing: Kotlin for DSL capabilities.

### Databases
Transactional data: PostgreSQL with JSONB for flexible schema. Event store: Apache Kafka for event sourcing. Order cache: Redis with persistence for fast access. Time-series data: TimescaleDB for historical analysis. Search: Elasticsearch for order history queries.

### Message Brokers
Primary: Apache Kafka for event streaming, guaranteed ordering per partition. Secondary: RabbitMQ for task queues and async operations. Redis Pub/Sub for real-time notifications.

### Caching Strategy
L1 Cache: In-memory (Caffeine for Java) with 10-second TTL. L2 Cache: Redis cluster with LRU eviction. Cache-aside pattern for order lookups. Write-through for reference data updates.

### API Gateway
Kong or AWS API Gateway for external traffic. Envoy for internal service mesh. Features: authentication, rate limiting, request transformation, response caching, circuit breaking.

---

**Document Version**: 1.0  
**Last Updated**: January 17, 2026  
**Status**: Complete
