# Stock Exchange and Broker System - System Design

## Overview
A stock exchange and broker system is a highly complex, mission-critical platform that facilitates the buying and selling of securities, processing millions of orders per day with microsecond-level latency. This document details the complete system architecture from order entry to settlement, handling institutional and retail traders globally.

## Executive Summary

### Scale & Performance
- **Daily Order Volume**: 500 million+ orders/day
- **Peak Throughput**: 1.2 million orders/second
- **Matching Engine Latency**: <50 microseconds (one-way)
- **Market Data Updates**: 10 million messages/second (peak)
- **Uptime**: 99.999% (5.26 minutes downtime/year)
- **Users**: 50 million+ retail traders, 10,000+ institutional clients

### Core Trading Functions

#### Order Management
```
Trader → FIX Gateway → Order Service → Validation → Matching Engine → Execution
```
- Supports 15+ order types (Market, Limit, Stop, Iceberg, etc.)
- Multi-channel access (FIX 4.4/5.0, REST API, WebSocket, Mobile)
- Real-time order status updates (<5ms notification)
- Complete audit trail with nanosecond timestamps

#### Matching Engine
```
Buy Orders + Sell Orders → Price-Time Priority Algorithm → Trades
```
- **Latency**: 30-50 microseconds (median), 100 microseconds (p99)
- **Algorithm**: Price-Time Priority (FIFO within price level)
- **Technology**: FPGA-accelerated matching + C++ deterministic engine
- **Throughput**: 1.2 million orders/second per symbol

#### Market Data Distribution
- **Level 1**: Best bid/ask (10,000 updates/second/symbol)
- **Level 2**: Full order book depth (20 levels)
- **Trade Ticks**: Every execution with price, size, time
- **Distribution**: UDP multicast + WebSocket + Kafka streams

## 1. System Scope & Architecture Tiers

### 1.1 Trading Platform (Core Exchange)

**Order Entry & Routing**
```
Client → TLS 1.3 Encrypted Connection → API Gateway → Order Service
├── Order Validation (balance, price limits, quantity)
├── Risk Check (margin, exposure, position limits)
└── Routing to Matching Engine (FIX 5.0 SP2)
```

**Technology Stack:**
- **Order Gateway**: C++ with Boost.Asio (async I/O), DPDK (kernel bypass)
- **Message Protocol**: FIX 5.0 SP2, Google Protocol Buffers (internal)
- **Network**: 100 Gbps InfiniBand, <5 microsecond network latency
- **Hardware**: Dell PowerEdge R750 (128 cores, 512GB RAM, NVMe SSDs)

**Performance Characteristics:**
- Order validation: <10 microseconds
- Risk check: <20 microseconds (in-memory cache lookup)
- End-to-end latency (gateway to matching engine): <100 microseconds

### 1.2 Matching Engine (Heart of Exchange)

**Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│             Matching Engine Cluster                          │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Primary FPGA  │  │  Hot Standby   │  │  Cold Backup │  │
│  │  Matching Core │◄─┤  FPGA Node     │◄─┤  C++ Engine  │  │
│  │  (Active)      │  │  (Ready)       │  │  (Failover)  │  │
│  └────────┬───────┘  └────────────────┘  └──────────────┘  │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  In-Memory Order Book (Per Symbol)                   │  │
│  │  - Buy Orders: Red-Black Tree (sorted by price DESC) │  │
│  │  - Sell Orders: Red-Black Tree (sorted by price ASC) │  │
│  │  - Time Priority: FIFO queue per price level         │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**FPGA Implementation:**
- **Hardware**: Xilinx Alveo U280 Data Center Accelerator Card
- **Clock Speed**: 250 MHz
- **Latency**: 4 clock cycles = 16 nanoseconds (logic only)
- **End-to-end**: 30-50 microseconds (including I/O)
- **Capacity**: 100,000 price levels per symbol, 5,000 symbols

**Why FPGA?**
1. **Deterministic Latency**: No OS jitter, no garbage collection
2. **Parallel Processing**: Match multiple symbols simultaneously
3. **Low Power**: 75W vs 250W for equivalent CPU cluster
4. **Compliance**: Timestamping at hardware level (nanosecond precision)

### 1.3 Market Data Distribution

**Multi-Tier Distribution Architecture**:
```
Matching Engine → Order Book Updates
         │
         ├──────► UDP Multicast (Institutional, Co-located)
         │        - Protocol: Binary (custom)
         │        - Latency: <100 microseconds
         │        - Bandwidth: 40 Gbps dedicated
         │
         ├──────► Kafka Cluster (Retail, API consumers)
         │        - Topics: trades, quotes, depth
         │        - Throughput: 10M messages/sec
         │        - Latency: 2-5 milliseconds
         │
         ├──────► WebSocket Server (Web/Mobile apps)
         │        - Protocol: JSON over WSS
         │        - Latency: 10-50 milliseconds
         │        - Connections: 5 million concurrent
         │
         └──────► Redis Cache (Historical queries)
                  - Data: Last 1 hour tick data
                  - Access: <1 millisecond
                  - Memory: 2TB cluster (sharded)
```

**Data Formats**:

*Level 1 (Top of Book)*:
```json
{
  "symbol": "AAPL",
  "bid": 175.25,
  "bidSize": 500,
  "ask": 175.27,
  "askSize": 800,
  "last": 175.26,
  "volume": 45678900,
  "timestamp": 1642435678123456789
}
```

*Level 2 (Full Depth)*:
```json
{
  "symbol": "AAPL",
  "bids": [
    [175.25, 500, 12],   // [price, size, num_orders]
    [175.24, 1200, 8],
    [175.23, 800, 15]
  ],
  "asks": [
    [175.27, 800, 9],
    [175.28, 600, 11],
    [175.29, 1500, 7]
  ]
}
```

## 2. Technology Stack (Production Environment)

### 2.1 Core Trading Infrastructure

**Matching Engine**:
- **Primary**: Custom FPGA (Xilinx Alveo U280) + C++ microservices
- **Language**: C++20, VHDL (for FPGA logic)
- **Libraries**: Boost (networking), Folly (Facebook), abseil-cpp (Google)
- **Serialization**: FlatBuffers, Cap'n Proto (zero-copy)

**Order Management System**:
- **Language**: Java 17 (Spring Boot 3.2), Kotlin
- **Framework**: Spring Cloud, Resilience4j, Reactor (reactive streams)
- **Caching**: Aerospike (sub-millisecond), Redis (session state)
- **Message Queue**: Apache Kafka 3.5 (persistent queue), RabbitMQ (RPC)

**Market Data Platform**:
- **Streaming**: Apache Kafka, Apache Pulsar, NATS Streaming
- **Real-time**: WebSocket (Spring WebFlux), Server-Sent Events
- **Storage**: TimescaleDB (time-series), ClickHouse (analytics)

### 2.2 Data Persistence Layer

**Databases (Polyglot Persistence)**:
```
┌────────────────────────────────────────────────────────────────┐
│                     Data Storage Architecture                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PostgreSQL 15 (Primary OLTP Database)                         │
│  ├── Accounts, Users, Broker Profiles                          │
│  ├── Configuration, Reference Data                             │
│  └── Settlement Records                                        │
│  Hardware: 3-node cluster, 128 vCPU, 512GB RAM, NVMe SSD      │
│  Performance: 150,000 TPS (read+write), <5ms p99 latency      │
│  Cost: $15,000/month (AWS RDS or self-managed)                │
│                                                                 │
│  Apache Cassandra 4.1 (Order Book & Trade Storage)            │
│  ├── Active Orders (TTL: 24 hours)                            │
│  ├── Trade History (hot: 90 days, warm: 7 years)              │
│  └── Audit Logs                                                │
│  Hardware: 12-node cluster, 64 vCPU, 256GB RAM, 10TB NVMe     │
│  Performance: 500,000 writes/sec, <2ms p99 write latency      │
│  Replication: RF=3, Quorum consistency                         │
│  Cost: $25,000/month                                           │
│                                                                 │
│  TimescaleDB 2.x (Market Data Time Series)                    │
│  ├── OHLCV (1min, 5min, 1hour, daily bars)                    │
│  ├── Tick Data (compressed hypertables)                        │
│  └── Aggregated Statistics                                     │
│  Hardware: 4-node cluster, 64 vCPU, 256GB RAM, 20TB SSD       │
│  Compression: 95% (columnar compression)                       │
│  Retention: 10 years (compressed), real-time queries           │
│  Cost: $8,000/month                                            │
│                                                                 │
│  Redis Enterprise 7.x (Caching & Session State)               │
│  ├── User Sessions (JWT tokens, preferences)                   │
│  ├── Hot Data (top 1000 symbols, current prices)              │
│  └── Rate Limiting Counters                                    │
│  Hardware: 6-node cluster, 32 vCPU, 256GB RAM                 │
│  Performance: 10 million ops/sec, <1ms latency                │
│  Cost: $6,000/month                                            │
│                                                                 │
│  MongoDB 6.x (Document Store)                                  │
│  ├── User Preferences, Watchlists                             │
│  ├── Unstructured Reports                                      │
│  └── Compliance Documents                                      │
│  Cost: $4,000/month                                            │
│                                                                 │
│  AWS S3 / MinIO (Object Storage)                              │
│  ├── Trade Reports (CSV, PDF)                                  │
│  ├── Audit Logs (archived after 90 days)                       │
│  ├── Database Backups                                          │
│  └── Regulatory Compliance Archives (7-10 years)               │
│  Storage: 500TB, Lifecycle: Glacier after 1 year              │
│  Cost: $10,000/month (storage) + $2,000 (requests)            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
Total Database Cost: ~$70,000/month
```

### 2.3 Cloud & Infrastructure

**AWS Services (Primary Cloud Provider)**:
- **Compute**: EC2 (c7g.16xlarge for matching engine, m7g for services)
- **Containers**: EKS 1.28 (Kubernetes), Fargate (serverless containers)
- **Networking**: VPC (multi-AZ), Direct Connect (10 Gbps dedicated), PrivateLink
- **Load Balancing**: ALB (application), NLB (TCP for FIX protocol)
- **Storage**: EBS io2 (provisioned IOPS: 64,000 IOPS), EFS (shared file system)
- **Security**: KMS (encryption), Secrets Manager, GuardDuty, CloudHSM
- **Monitoring**: CloudWatch, X-Ray (distributed tracing), VPC Flow Logs

**Multi-Region Setup**:
```
Primary Region: us-east-1 (N. Virginia)
├── 3 Availability Zones
├── All services deployed
├── Active-Active for read APIs
└── Active-Passive for matching engine

Secondary Region: eu-west-1 (Ireland) 
├── Full replica (hot standby)
├── <50ms replication lag
└── Failover time: <5 minutes

DR Region: ap-southeast-1 (Singapore)
└── Cold standby (cost optimization)
```

**Cost Breakdown (Monthly)**:
- EC2 Instances: $45,000 (50x c7g.16xlarge + 200x m7g.2xlarge)
- EKS/Fargate: $12,000
- Data Transfer: $25,000 (cross-AZ, egress to clients)
- Load Balancers: $3,000
- EBS/EFS Storage: $8,000
- Direct Connect: $10,000
- **Total Infrastructure**: ~$103,000/month

## 3. Key User Journeys & Workflows

### 3.1 Retail Trader - Market Order Placement

**Flow**:
```
1. Trader logs in → OAuth 2.0 + MFA
2. Checks portfolio → Redis cache (< 5ms)
3. Views live quotes → WebSocket feed (20ms updates)
4. Places market order:
   - "Buy 100 shares of AAPL at market"
5. Order validation:
   - Account balance check: PostgreSQL (3ms)
   - Buying power calculation: Redis (1ms)
   - Order limit validation: In-memory rules (<0.5ms)
6. Risk check:
   - Position limit: OK (within 5,000 shares limit)
   - Day trading limit: OK (3 of 5 round trips used)
   - Margin requirement: OK (50% margin available)
7. Order routing → Matching engine
8. Execution:
   - Matched at $175.26 (100 shares)
   - Latency: 127 microseconds (order entry to execution)
9. Confirmation:
   - WebSocket notification (instant)
   - Email confirmation (within 1 second)
   - SMS alert (optional, within 5 seconds)
10. Settlement:
    - Trade recorded in Cassandra
    - Position updated in real-time (Redis + PostgreSQL)
    - Settlement scheduled for T+2
```

**Performance SLA**:
- Login: <500ms
- Portfolio load: <100ms
- Quote updates: 20-50ms latency
- Order acknowledgment: <10ms
- Execution notification: <50ms

### 3.2 Institutional Trader - Algorithmic Trading

**Flow**:
```
1. Algo connects → FIX 5.0 SP2 protocol
2. Authentication → API key + IP whitelist
3. Sends parent order:
   - "Buy 1,000,000 shares of MSFT, VWAP algo, 9:30 AM - 4:00 PM"
4. Order Management System (OMS):
   - Validates order
   - Allocates to VWAP algo engine
5. Algo execution:
   - Slices parent order into 200 child orders
   - Monitors market volume (real-time VWAP calculation)
   - Sends child orders every 2-3 minutes
6. Execution tracking:
   - Average execution price: $380.15
   - Target VWAP: $380.12
   - Performance: -0.008% vs VWAP (within tolerance)
7. Post-trade analytics:
   - Stored in ClickHouse
   - Available via REST API for TCA (Transaction Cost Analysis)
```

**Technology Stack for Algos**:
- **Algo Engine**: C++ (QuickFIX, Boost)
- **Market Data**: Direct UDP multicast feed
- **Risk Limits**: Pre-trade checks (<10 microseconds)
- **Execution Venue**: Smart order routing (4 venues)

### 3.3 Market Maker - Liquidity Provision

**Flow**:
```
1. Market maker co-located → 10 Gbps fiber, <5 microsecond latency
2. Sends continuous two-sided quotes:
   - Bid: $175.25 (size: 1,000)
   - Ask: $175.27 (size: 1,000)
   - Spread: 2 cents
3. Quote updates: 50,000+ per second (all symbols combined)
4. Gets filled:
   - Incoming aggressive buy order: 500 shares at $175.27
   - Market maker's ask gets executed
5. Immediately re-quotes:
   - New ask: $175.28 (size: 1,000)
   - Latency from fill to re-quote: <100 microseconds
6. End-of-day P&L:
   - Total trades: 1.2 million
   - Gross profit: $45,000 (spread capture)
   - Exchange fees: $12,000
   - Net profit: $33,000
```

**Market Maker Infrastructure**:
- **Co-location**: Rack space in exchange data center
- **Hardware**: FPGA NICs, kernel bypass networking (DPDK)
- **Latency**: <5 microseconds (network), <50 microseconds (end-to-end)
- **Cost**: $50,000/month (co-location + infrastructure)
- **FR3.6**: Corporate actions and announcements

#### FR4: Risk Management
- **FR4.1**: Pre-trade risk checks (margin, position limits, exposure)
- **FR4.2**: Real-time position tracking
- **FR4.3**: Margin calculations (Initial, Maintenance, Variation)
- **FR4.4**: Automated margin calls and liquidation
- **FR4.5**: Risk reporting and dashboards
- **FR4.6**: Counterparty risk assessment

#### FR5: Settlement and Clearing
- **FR5.1**: T+2 settlement cycle management
- **FR5.2**: Trade matching and confirmation
- **FR5.3**: Corporate actions processing
- **FR5.4**: Dividend and interest payments
- **FR5.5**: Failed trade management
- **FR5.6**: Integration with central clearing houses

#### FR6: Compliance and Reporting
- **FR6.1**: KYC/AML verification
- **FR6.2**: Real-time trade surveillance
- **FR6.3**: Market abuse detection (wash trades, spoofing, layering)
- **FR6.4**: Regulatory reporting (CAT, OATS, MiFID II)
- **FR6.5**: Audit trail for all transactions
- **FR6.6**: Best execution reporting

#### FR7: Account Management
- **FR7.1**: Multi-tier account structure (Admin, Broker, Trader, Investor)
- **FR7.2**: Portfolio management and valuation
- **FR7.3**: Cash and margin account management
- **FR7.4**: Tax lot accounting
- **FR7.5**: Statement generation
- **FR7.6**: Fee and commission calculations

## Technical Requirements

### Performance Requirements
- **Latency**: 
  - Order acknowledgment: < 1ms (99th percentile)
  - Trade execution: < 500 microseconds
  - Market data publication: < 100 microseconds
- **Throughput**: 
  - 10 million orders per second
  - 1 million trades per second
  - 100,000 concurrent connections
- **Data Volume**:
  - 100 TB historical market data
  - 10 million new records per day

### Availability and Reliability
- **Uptime**: 99.999% (5.26 minutes downtime per year)
- **Recovery Time Objective (RTO)**: < 5 minutes
- **Recovery Point Objective (RPO)**: Zero data loss
- **Disaster Recovery**: Active-active multi-region setup

### Scalability
- **Horizontal Scaling**: Auto-scaling for API and market data services
- **Vertical Scaling**: High-performance matching engine on dedicated hardware
- **Geographic Scaling**: Multi-region deployment with data replication

### Security Requirements
- **Authentication**: Multi-factor authentication (MFA)
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS 1.3 for data in transit, AES-256 for data at rest
- **Network Security**: DDoS protection, WAF, network segmentation
- **Compliance**: SOC 2, ISO 27001, PCI DSS
- **Audit**: Complete audit trail with tamper-proof logging

### Data Consistency
- **ACID Compliance**: All financial transactions must be ACID compliant
- **Idempotency**: All APIs must be idempotent
- **Exactly-Once Semantics**: No duplicate trades or orders
- **Strong Consistency**: Critical paths use synchronous replication


## 4. Performance Requirements & SLAs

### 4.1 Latency Requirements

```
┌────────────────────────────────────────────────────────────────┐
│                     Latency Budget (Microseconds)               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Component                        │ Target   │ p50 │ p95 │ p99│
│  ─────────────────────────────────┼──────────┼─────┼─────┼────│
│  Network (client to gateway)      │   500    │ 450 │ 800 │ 1.2ms
│  TLS termination                  │    50    │  42 │  65 │  85│
│  API Gateway routing              │    20    │  15 │  28 │  35│
│  Order validation                 │    10    │   8 │  14 │  18│
│  Risk check (in-memory)           │    20    │  12 │  25 │  32│
│  Kafka publish (async)            │     5    │   4 │   7 │  12│
│  Matching engine                  │    50    │  35 │  68 │  95│
│  Market data publish (UDP)        │    10    │   7 │  12 │  18│
│  Execution confirmation           │    30    │  22 │  38 │  55│
│  ─────────────────────────────────┼──────────┼─────┼─────┼────│
│  TOTAL (one-way)                  │   695    │ 595 │1,057│1,390│
│  ─────────────────────────────────┴──────────┴─────┴─────┴────│
│                                                                 │
│  Target: < 1 millisecond (p95)                                 │
│  Current: 1.057 milliseconds (p95) ✅                           │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Why These Numbers Matter**:
- **High-Frequency Trading (HFT)**: Microseconds = profit/loss
- **Market Makers**: Need to update quotes faster than competitors
- **Retail Traders**: Perceived performance and user experience
- **Regulatory**: Order timestamps must be accurate to nanoseconds

### 4.2 Throughput Requirements

**Peak Trading Hours (9:30 AM - 10:30 AM ET)**:
- **Orders/second**: 1.2 million (sustained), 2.5 million (burst)
- **Trades/second**: 400,000 (sustained), 800,000 (burst)
- **Market Data Updates**: 10 million messages/second
- **WebSocket Connections**: 5 million concurrent
- **API Requests**: 500,000 requests/second (read-heavy)

**Daily Totals**:
- Orders: 500 million
- Trades: 150 million
- Market Data Messages: 50 billion
- Data Transfer: 200 TB/day

### 4.3 Availability & Reliability

**Uptime SLA**: 99.999% (5.26 minutes downtime/year)

**Availability Breakdown**:
```
Component                    │ Availability │ Allowed Downtime/Year
────────────────────────────┼──────────────┼──────────────────────
Matching Engine              │  99.9999%    │   31.5 seconds
Order Gateway                │  99.999%     │   5.26 minutes
Market Data Feed             │  99.99%      │   52.6 minutes
Web/Mobile API               │  99.95%      │   4.38 hours
Reporting System             │  99.9%       │   8.76 hours
```

**Disaster Recovery**:
- **RTO (Recovery Time Objective)**: 5 minutes
- **RPO (Recovery Point Objective)**: 0 seconds (zero data loss)
- **Backup Frequency**: Continuous replication + hourly snapshots
- **Geographic Redundancy**: 3 regions (active-active for reads, active-passive for writes)

### 4.4 Security Requirements

**Authentication**:
- **Protocol**: OAuth 2.0 + JWT tokens
- **MFA**: Required for accounts > $100,000
- **Session**: 15-minute timeout, refresh token (7 days)
- **API Keys**: RSA 4096-bit, rotated every 90 days

**Encryption**:
- **In-Transit**: TLS 1.3, AES-256-GCM
- **At-Rest**: AES-256, AWS KMS (customer-managed keys)
- **Database**: Transparent Data Encryption (TDE)

**Compliance**:
- **Regulatory**: SEC Rule 17a-4 (WORM storage), MiFID II (EU)
- **Audit Logs**: Immutable, 10-year retention
- **Trade Reporting**: T+1 reporting to regulators
- **Surveillance**: Real-time market manipulation detection

**Penetration Testing**:
- **Frequency**: Quarterly (external), monthly (internal)
- **Bug Bounty**: $50,000 max payout for critical vulnerabilities
- **Certifications**: SOC 2 Type II, ISO 27001, PCI DSS (for payments)

## 5. Cost Structure (Annual)

```
┌────────────────────────────────────────────────────────────────┐
│                     Annual Cost Breakdown                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Infrastructure & Cloud                        $1,236,000      │
│  ├── AWS/Cloud Services (EC2, EKS, etc.)        $1,000,000     │
│  ├── Direct Connect & Networking                   $120,000    │
│  └── CloudFront CDN                                 $116,000    │
│                                                                 │
│  Data Storage & Databases                        $840,000      │
│  ├── PostgreSQL, Cassandra, TimescaleDB            $600,000    │
│  ├── Redis, MongoDB                                 $120,000    │
│  └── S3/Glacier (long-term archives)                $120,000    │
│                                                                 │
│  Market Data Feeds (External)                    $500,000      │
│  ├── Real-time prices (Bloomberg, Refinitiv)       $300,000    │
│  └── Reference data, corporate actions              $200,000    │
│                                                                 │
│  Security & Compliance                           $750,000      │
│  ├── DDoS protection, WAF                          $150,000    │
│  ├── Security audits, pen testing                  $200,000    │
│  ├── Compliance consulting                         $250,000    │
│  └── Insurance (cyber, E&O)                        $150,000    │
│                                                                 │
│  Licensing & Software                            $400,000      │
│  ├── Database licenses (enterprise)                $200,000    │
│  ├── Monitoring tools (DataDog, Splunk)            $120,000    │
│  └── Development tools                              $80,000    │
│                                                                 │
│  Personnel (Engineering & Ops)                 $5,000,000      │
│  ├── Engineers (20 FTEs @ $180k avg)             $3,600,000    │
│  ├── DevOps/SRE (8 FTEs @ $160k avg)             $1,280,000    │
│  └── Security team (2 FTEs @ $200k avg)             $400,000    │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│  TOTAL ANNUAL COST                             $8,726,000      │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  Revenue (for context):                                        │
│  ├── Transaction fees ($0.005/trade × 150M trades/day         │
│  │   × 252 trading days) = $189M/year                         │
│  ├── Market data subscriptions = $50M/year                     │
│  └── Total Revenue: ~$239M/year                                │
│                                                                 │
│  Profit Margin: ~96% (highly profitable after scale)          │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## 6. Design Principles & Trade-offs

### 6.1 CAP Theorem Trade-offs

**Matching Engine**: CP (Consistency + Partition Tolerance)
- **Why**: Cannot have two different prices for the same order
- **Implication**: Brief unavailability during network partition (fail-safe)
- **Mitigation**: Hot standby with <5 second failover

**Market Data Distribution**: AP (Availability + Partition Tolerance)
- **Why**: Slightly stale data acceptable vs no data
- **Implication**: Eventually consistent (milliseconds)
- **Mitigation**: Sequence numbers for client-side ordering

**User Session State**: AP (Availability + Partition Tolerance)
- **Why**: User experience over perfect consistency
- **Implication**: Redis cluster with async replication
- **Mitigation**: Session reconciliation on login

### 6.2 Performance vs. Cost

**FPGA vs. Software Matching Engine**:
- **FPGA**: $500K hardware, <50μs latency, 1.2M orders/sec
- **Software (C++)**: $50K servers, <500μs latency, 800K orders/sec
- **Decision**: FPGA for competitive advantage (worth 10x cost)

**Database Choice**:
- **PostgreSQL**: $15K/month, strong consistency, ACID
- **Cassandra**: $25K/month, eventual consistency, massive scale
- **Decision**: Both (polyglot persistence) for optimal performance per use case

### 6.3 Build vs. Buy

**Built In-House**:
- Matching engine (competitive advantage)
- Order management system (custom requirements)
- Risk engine (proprietary algorithms)

**Purchased/SaaS**:
- Market data (Bloomberg, Refinitiv) - $500K/year vs $5M to build
- Monitoring (DataDog) - $120K/year vs $500K to build
- Identity (AWS Cognito) - $50K/year vs $200K to build


## 7. Key Success Metrics

### 7.1 Performance KPIs

```
┌────────────────────────────────────────────────────────────────┐
│                     Performance Metrics                         │
├────────────────────────────────────────────────────────────────┤
│  Metric                         │ Target  │ Current │  Status  │
│  ───────────────────────────────┼─────────┼─────────┼─────────│
│  Order-to-Trade Latency (p99)   │ <1ms    │ 1.4ms   │    ✅    │
│  Market Data Latency (p99)      │ <100μs  │  85μs   │    ✅    │
│  System Uptime                  │ 99.999% │ 99.997% │    ⚠️    │
│  Order Success Rate             │ 99.99%  │ 99.991% │    ✅    │
│  API Response Time (p95)        │ <50ms   │  42ms   │    ✅    │
│  WebSocket Message Rate         │ 10M/s   │ 9.2M/s  │    ✅    │
│  Database Write Latency (p95)   │ <5ms    │  3.8ms  │    ✅    │
│  Cache Hit Rate                 │ >95%    │  97.2%  │    ✅    │
└────────────────────────────────────────────────────────────────┘
```

### 7.2 Business KPIs

- **Daily Trading Volume**: $12 billion (target: $10 billion) ✅
- **Active Traders**: 1.2 million (target: 1 million) ✅
- **Order Fill Rate**: 96.5% (target: >95%) ✅
- **Customer NPS**: 58 (target: >50) ✅
- **Regulatory Violations**: 0 (target: 0) ✅
- **Market Share**: 8.5% of US equities trading

### 7.3 Operational KPIs

- **MTTD (Mean Time to Detect)**: 45 seconds (target: <1 min) ✅
- **MTTR (Mean Time to Resolve)**: 12 minutes (target: <15 min) ✅
- **Deployment Frequency**: 8 deployments/week ✅
- **Change Failure Rate**: 3.2% (target: <5%) ✅
- **On-call Incidents**: 2.1/week (target: <3/week) ✅

## Next Documents

This overview provides the foundation for understanding the stock exchange system. Continue to:

1. **[High-Level Architecture](./02-high-level-architecture.md)** - Complete system architecture with component interactions
2. **[Matching Engine Deep Dive](./03-matching-engine-deep-dive.md)** - FPGA implementation, algorithms, performance optimization
3. **[Order Management System](./04-order-management-system.md)** - Order lifecycle, validation, routing
4. **[Market Data Distribution](./05-market-data-distribution.md)** - Real-time data feeds, protocols, distribution strategies
5. **[Risk Management System](./06-risk-management-system.md)** - Pre-trade checks, margin calculations, exposure monitoring

---

**Key Technologies Summary**:
- **Languages**: C++20, Java 17, Kotlin, VHDL (FPGA)
- **Frameworks**: Spring Boot 3.2, Spring Cloud, Reactor, Boost, Folly
- **Databases**: PostgreSQL 15, Cassandra 4.1, TimescaleDB, Redis 7, MongoDB 6
- **Messaging**: Apache Kafka 3.5, RabbitMQ, UDP multicast
- **Cloud**: AWS (EKS, EC2, RDS, ElastiCache, Direct Connect)
- **Monitoring**: Prometheus, Grafana, DataDog, Jaeger, ELK Stack
- **Hardware**: Xilinx Alveo U280 FPGAs, Dell PowerEdge R750 servers

---

**Document Version**: 2.0 (Netflix-style format)  
**Last Updated**: January 17, 2026  
**Status**: Production
