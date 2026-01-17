# Market Data Distribution System

## Overview

The Market Data Distribution System is responsible for real-time dissemination of trading information including prices, volumes, order book depth, and trade executions. It must handle massive throughput (millions of updates per second), maintain microsecond-level latency, ensure data consistency, and support various client types from retail to high-frequency traders.

## Data Hierarchy and Types

### Level 1 Data (Top of Book)
Contains the most essential market information: best bid price and quantity, best ask price and quantity, last traded price, last trade size, cumulative daily volume, trade timestamp. Updated on every top-of-book change or trade. Consumed by: retail investors, basic charting applications, mobile apps. Bandwidth requirement: ~10 updates/second per symbol. Latency requirement: < 100ms for retail acceptable.

### Level 2 Data (Market Depth)
Provides deeper market visibility with 10-20 price levels on each side of the order book. Shows aggregated quantity at each price level (not individual orders). Includes order count at each level. Updated on any book change at displayed levels. Consumed by: active traders, institutional desks, algorithmic systems. Bandwidth: ~100 updates/second per symbol during active trading. Latency requirement: < 10ms for institutional.

### Level 3 Data (Full Depth of Market)
Complete order book with individual order identification. Shows every order's ID, price, quantity, timestamp, and order type. Allows queue position calculation. Restricted access (exchange members, market makers only). Consumed by: market makers, high-frequency trading firms. Bandwidth: ~1000 updates/second per symbol. Latency requirement: < 1ms using co-location.

### Time and Sales (Trade Ticks)
Sequential feed of every executed trade showing: trade ID, timestamp (microsecond precision), price, quantity, buyer/seller indicators, trade conditions (opening, closing, odd-lot). Required for: VWAP calculations, liquidity analysis, market replay, regulatory reporting. Guaranteed ordering critical for audit purposes.

### Market Statistics
Aggregated market information calculated in real-time: OHLC (Open, High, Low, Close) for multiple timeframes, VWAP (Volume-Weighted Average Price), total daily volume, number of trades, 52-week high/low, market capitalization changes. Updated continuously during trading session. Used for: market summary displays, alert triggers, index calculations.

### Reference Data
Static and slowly-changing information: symbol master (ISIN, ticker, exchange), corporate actions (splits, dividends, mergers), trading schedules and holidays, tick size and lot size rules, circuit breaker levels, margin requirements. Updated outside trading hours or with advance notice. Cached aggressively with daily refresh.

### Index Data
Real-time index values (S&P 500, NASDAQ-100, etc.) calculated from constituent prices. Includes: current index value, net change, percentage change, constituent contributions. Calculation frequency: every second or on constituent trade. Critical for: index funds, ETF arbitrage, derivatives pricing.

### Options Chain Data
Complete snapshot of all option contracts for an underlying: strike prices, expiration dates, implied volatility, bid/ask spreads, Greeks (delta, gamma, theta, vega), open interest, volume. Updated on underlying price change or option trade. High cardinality (thousands of contracts per underlying).

## Distribution Protocols and Mechanisms

### Multicast UDP
Lowest latency distribution method for co-located clients. One-to-many efficient distribution. No acknowledgment or retransmission (fire-and-forget). Requires gap detection and recovery mechanism. Typical latency: 10-50 microseconds. Used for: Level 2/3 feeds to HFT firms. Network setup: dedicated multicast VLAN, IGMP snooping, PIM routing. Packet loss handling: sequence numbers, gap detection, TCP recovery channel.

### TCP Streaming
Reliable ordered delivery with acknowledgment. Point-to-point connections requiring connection management. Higher latency than multicast (~100-500 microseconds) but guaranteed delivery. Implements flow control and congestion avoidance. Used for: institutional clients, medium-latency applications. Connection pooling and keep-alive mechanisms essential.

### WebSocket
Full-duplex communication over HTTP/HTTPS. Browser-compatible for web applications. Supports binary (more efficient) or text (JSON) encoding. Built-in ping/pong for connection health. Used for: retail web trading platforms, mobile apps. Latency: 1-50ms depending on network. Auto-reconnection logic required on client side.

### gRPC Streaming
High-performance RPC framework with Protocol Buffers. Server streaming for market data feeds. Multiplexed connections over HTTP/2. Built-in flow control and error handling. Used for: internal microservices, modern APIs. Supports bidirectional streaming for subscriptions.

### REST API with Polling
Request-response pattern, client pulls data periodically. Simple to implement but inefficient for real-time data. Introduces latency (equal to polling interval). Used for: historical data queries, snapshot requests, low-frequency updates. Rate limiting essential to prevent server overload.

### FIX Protocol
Financial Information eXchange protocol, industry standard. Tag-value message format (human-readable but verbose). FIX 4.2, 4.4, and 5.0 versions supported. Used for: broker connections, institutional clients, legacy systems. Message types: MarketDataSnapshotFullRefresh, MarketDataIncrementalRefresh.

## Architecture Components

### Matching Engine Integration
Market data originates from matching engine as orders are matched or book updated. Engine publishes events to internal high-speed bus (shared memory or RDMA). Events include: order add/modify/cancel, trade execution, book level changes. Guaranteed ordering per symbol through partitioning. Publication latency: < 1 microsecond from engine to market data service.

### Market Data Gateway
Receives raw events from matching engine and normalizes into standard formats. Performs event filtering (only publish relevant updates). Enriches data with reference information. Manages sequence numbering for gap detection. Implements conflation (merge multiple updates within time window to reduce message count). Multiple gateway instances for redundancy with active-active configuration.

### Distribution Tier
Handles protocol-specific distribution to end clients. Separate services for each protocol (multicast, WebSocket, FIX). Manages client connections and subscriptions. Implements entitlement checking (verify client authorized for requested data). Performs bandwidth throttling per client tier (professional, retail, free tier). Maintains connection state and health monitoring.

### Historical Data Service
Stores and serves historical market data for analysis and backtesting. Ingests real-time feed into time-series database (TimescaleDB, InfluxDB). Provides APIs for querying: OHLCV bars, tick data, order book snapshots at specific times. Implements data retention policies (tick data for 1 year, bars for 10 years). Compression strategies reduce storage costs by 90%.

### Caching Layer
Multi-tier caching strategy reduces database load. L1: In-memory cache in distribution service (last value, order book snapshot). L2: Redis cluster for shared caching across services. L3: CDN for static/semi-static data (reference data, daily bars). Cache invalidation on data updates with pub/sub notifications. TTL varies by data type (1 second for prices, 1 day for reference data).

### Replay Service
Enables market replay for: algorithm backtesting, dispute resolution, audit requirements, trading simulation. Maintains complete message archive with microsecond timestamps. Provides time-travel queries (reconstruct market state at any point in time). Supports variable speed replay (1x, 10x, 1000x). Critical for debugging trading algorithms.

## Data Encoding and Compression

### Binary Encoding
More efficient than text-based formats. Protocol Buffers: Google's language-neutral serialization (50-80% size reduction vs JSON). Apache Avro: schema evolution support. FlatBuffers: zero-copy deserialization for ultra-low latency. MessagePack: binary JSON replacement. Choice depends on: latency requirements, schema stability, language support.

### Compression Strategies
Snapshot compression: Delta encoding (store difference from previous value). Order book: only send changes, not full book. Price encoding: integer representation (multiply by 10000, store as long). Timestamp: offset from base time. Batch compression: gzip for historical data, lz4 for real-time (faster). Compression ratio: 70-90% for market data.

### Conflation
Combines multiple updates into single message when client can't keep up. Strategies: Last-value conflation (send only most recent value), Aggregate conflation (sum volumes, min/max prices). Configurable per client based on subscription tier. Trade-off: reduced bandwidth vs information loss. Never conflate trade ticks (every trade must be delivered).

### Subscription Management
Clients subscribe to specific: symbols (AAPL, GOOGL), data types (L1, L2, trades), fields (price only, volume only). Wildcard subscriptions (all symbols in index). Dynamic add/remove subscriptions without reconnection. Subscription entitlement verification against client permissions. Subscription limits per connection (e.g., 500 symbols max for retail).

## Performance Optimization Techniques

### Partitioning Strategy
Partition symbols across multiple distribution nodes for horizontal scaling. Hash-based partitioning (symbol hash modulo node count) or range-based (A-M on node1, N-Z on node2). Each partition independent, no cross-partition coordination needed. Allows linear scalability (add nodes to increase capacity). Rebalancing strategy when adding/removing nodes.

### Multicast Groups
Separate multicast groups for: high-volume symbols (SPY, QQQ), medium-volume symbols, low-volume symbols. Clients subscribe only to groups containing their symbols of interest. Reduces bandwidth by avoiding irrelevant data. Multicast address assignment strategy avoids collisions.

### Zero-Copy Techniques
Avoid memory copies in data path using: memory-mapped files, shared memory between processes, sendfile() system call for disk to network, RDMA for network to network. Reduces CPU usage and latency by eliminating copy overhead. Requires careful buffer management to prevent corruption.

### Kernel Bypass Networking
DPDK (Data Plane Development Kit) bypasses kernel network stack. Polls network interface directly from user space. Eliminates context switches and interrupt handling overhead. Achieves 10-40 Gbps throughput with sub-microsecond latency. Requires dedicated CPU cores for polling threads. Appropriate for ultra-low latency feeds only.

### CPU Affinity and NUMA Awareness
Pin critical threads to specific CPU cores avoiding context switches. Place memory allocations on same NUMA node as processing threads. Disable hyper-threading for latency-sensitive threads. Isolate cores from kernel scheduler (isolcpus boot parameter). Use dedicated high-performance cores (avoid power-saving cores).

## Failover and High Availability

### Active-Active Distribution
Multiple distribution nodes serving same data simultaneously. Clients connect to nearest/fastest node. Each node receives full data feed from matching engine. No failover delay (client simply reconnects). Load distributed across nodes. Geographic distribution for global access.

### Sequencing and Gap Detection
Every message tagged with monotonically increasing sequence number per symbol. Client detects gaps in sequence. Gap recovery via: dedicated TCP recovery channel, retransmission request with range, snapshot request to rebuild state. Sequence numbers stored in persistent storage for recovery across restarts.

### Heartbeat Mechanism
Periodic heartbeat messages (every second) indicate channel liveness. Absence of heartbeat triggers reconnection logic. Heartbeat includes: sequence number, timestamp, channel status. Client-side watchdog timer monitors heartbeat arrival. Server-side tracks client heartbeat responses for connection health.

### State Synchronization
Upon reconnection, client requests snapshot of current state. Snapshot includes: order book state, last trade information, sequence number, timestamp. Client resumes incremental updates from snapshot sequence. Atomic snapshot generation prevents inconsistent state. Snapshot versioning for concurrent snapshot requests.

## Regulatory Compliance

### Market Data Reporting
SIP (Securities Information Processor) reporting for US equities: all trades and quotes reported to consolidated tape. FINRA reporting requirements for OTC trades. MiFID II transparency requirements for European markets. Reporting latency requirements: < 1 second for most markets. Message format: FIX, OUCH, or exchange-specific protocols.

### Timestamp Accuracy
Regulatory requirement for microsecond-level timestamp accuracy. Business clocks synchronized to UTC via GPS or PTP. Timestamp applied at: order receipt, routing decision, execution, market data publication. Clock drift monitoring and adjustment. Annual calibration and certification.

### Fair Access
Market data must be provided on fair and non-discriminatory terms. Tiered pricing allowed but same tier receives same data simultaneously. No exclusive arrangements providing data advantage. Latency cannot vary within same tier. Co-location space allocation on fair basis.

### Historical Archive
Regulatory requirement to retain market data for 3-7 years depending on jurisdiction. Archive must be: immutable (no retroactive changes), accessible (query capability), complete (no gaps), auditable (access logs). Storage format: write-once-read-many (WORM), compliance-grade storage, geographic redundancy.

## Monitoring and Alerting

### Latency Monitoring
Measure end-to-end latency from: matching engine publication to client receipt. Percentile tracking (p50, p95, p99, p99.9). Alert on latency degradation (threshold: > 2x baseline). Per-client latency SLA monitoring. Latency heatmaps by symbol and time of day.

### Throughput Monitoring
Messages per second by: protocol, client tier, symbol. Peak throughput during market events (earnings, open/close). Capacity utilization percentage. Trend analysis to predict capacity needs. Auto-scaling triggers based on throughput.

### Data Quality Monitoring
Detect anomalies: price spikes, volume spikes, stale data, sequence gaps, duplicate messages. Cross-validation against other data sources. Statistical models for expected price movements. Alert trading desk on anomalies for investigation.

### Connection Monitoring
Track: active connections, connection attempts, authentication failures, disconnections, reconnection frequency. Client health scoring based on connection stability. Identify problematic clients causing excessive reconnections. Network path monitoring for packet loss and latency.

## Client Tier Differentiation

### Professional Tier
Lowest latency feeds (multicast, co-location). Full order book depth (Level 3). No conflation or throttling. Highest bandwidth allocation. Premium pricing. SLA guarantees (99.99% uptime, < 1ms latency).

### Retail Tier
WebSocket or REST API access. Level 1 or Level 2 data. Conflation during high load. Moderate throttling (100 updates/second). Affordable pricing. Best-effort service.

### Free/Delayed Tier
15-minute delayed data. Snapshot updates only (no real-time streaming). Strict rate limiting. Suitable for casual investors or educational purposes. No SLA guarantees.

### Internal Systems Tier
Lowest latency internal feeds for: risk management, position tracking, P&L calculation, compliance surveillance. Direct shared-memory or RDMA connections. No encryption overhead. Guaranteed delivery with synchronous acknowledgment.

## Technology Stack

### Message Brokers
Apache Kafka: high-throughput event streaming, message persistence, replay capability. Pulsar: multi-tenancy, geo-replication, tiered storage. NATS: lightweight, high-performance pub/sub. RedPanda: Kafka-compatible with lower latency.

### Time-Series Databases
TimescaleDB: PostgreSQL extension, SQL querying, mature ecosystem. InfluxDB: purpose-built for time-series, high write throughput. ClickHouse: columnar storage, excellent for analytics queries. QuestDB: microsecond precision, high-frequency data.

### Caching
Redis: in-memory key-value store, pub/sub capability, clustering. Aerospike: hybrid memory/SSD, microsecond latency, high throughput. Hazelcast: distributed in-memory data grid, compute co-location.

### Protocols and Serialization
Protocol Buffers: efficient binary serialization, schema evolution. Apache Avro: data serialization with schema registry. FlatBuffers: zero-copy deserialization. Cap'n Proto: similar to FlatBuffers, RPC support.

---

**Document Version**: 1.0  
**Last Updated**: January 17, 2026  
**Status**: Complete
