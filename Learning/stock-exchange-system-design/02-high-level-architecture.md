# High-Level Architecture - Stock Exchange and Broker System

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [System Architecture Diagram](#system-architecture-diagram)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)
7. [Network Architecture](#network-architecture)
8. [Integration Points](#integration-points)

## Architecture Overview

The stock exchange and broker system follows a **microservices architecture** with the following key principles:

### Architectural Principles

1. **Domain-Driven Design (DDD)**
   - Bounded contexts for Trading, Risk, Settlement, Compliance
   - Aggregate roots for Order, Trade, Account, Position
   - Domain events for inter-service communication

2. **Event-Driven Architecture (EDA)**
   - Event sourcing for order and trade history
   - CQRS (Command Query Responsibility Segregation)
   - Event streaming for real-time market data

3. **Microservices Architecture**
   - Service autonomy and independence
   - Polyglot persistence (different databases for different services)
   - API gateway pattern for external access
   - Service mesh for internal communication

4. **High-Performance Computing**
   - FPGA-based matching engine for ultra-low latency
   - In-memory data grids for hot data
   - Co-location for market participants
   - Kernel bypass networking (DPDK)

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL INTERFACES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Web UI  │  Mobile App  │  Trading Terminal  │  FIX Gateway  │  REST API    │
└────┬─────┴──────┬────────┴─────────┬─────────┴───────┬──────┴──────┬───────┘
     │            │                  │                 │             │
     └────────────┴──────────────────┴─────────────────┴─────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │     API Gateway / Load Balancer │
                    │  (NGINX, Kong, AWS ALB)         │
                    └────────────────┬────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  Authentication &   │  │   Authorization &   │  │    Rate Limiting    │
│  Identity Service   │  │   RBAC Service      │  │    & Throttling     │
│  (OAuth2, JWT)      │  │   (Casbin, OPA)     │  │    (Redis)          │
└──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
           │                        │                         │
           └────────────────────────┼─────────────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │     Service Mesh (Istio)       │
                    │  - Service Discovery           │
                    │  - Load Balancing              │
                    │  - Circuit Breaking            │
                    │  - Retry Logic                 │
                    └───────────────┬────────────────┘
                                    │
        ┌───────────────────────────┼────────────────────────────┐
        │                           │                            │
        ▼                           ▼                            ▼
┌──────────────────┐    ┌──────────────────┐      ┌──────────────────┐
│  Order Service   │    │  Matching Engine │      │ Market Data Svc  │
│  - Order Entry   │◄───┤  (ULTRA LOW      │─────►│ - Level 1/2 Data │
│  - Validation    │    │   LATENCY FPGA)  │      │ - Trade Ticks    │
│  - Routing       │    │  - Price-Time    │      │ - Order Book     │
│  - Modification  │    │  - Priority      │      │ - Statistics     │
└────────┬─────────┘    └────────┬─────────┘      └────────┬─────────┘
         │                       │                         │
         │                       │                         │
         ▼                       ▼                         ▼
┌──────────────────┐    ┌──────────────────┐      ┌──────────────────┐
│  Risk Service    │    │  Trade Service   │      │  Position Svc    │
│  - Pre-trade     │◄───┤  - Execution     │─────►│  - Real-time     │
│  - Margin Calc   │    │  - Confirmation  │      │  - P&L           │
│  - Exposure      │    │  - Allocation    │      │  - Valuation     │
└────────┬─────────┘    └────────┬─────────┘      └────────┬─────────┘
         │                       │                         │
         │                       ▼                         │
         │              ┌──────────────────┐              │
         │              │ Settlement Svc   │              │
         └─────────────►│ - T+2 Cycle      │◄─────────────┘
                        │ - Clearing       │
                        │ - DVP            │
                        └────────┬─────────┘
                                 │
                 ┌───────────────┼────────────────┐
                 ▼               ▼                ▼
        ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
        │ Account Svc │  │ Portfolio   │  │ Reporting   │
        │ - KYC/AML   │  │ Service     │  │ Service     │
        │ - Onboard   │  │ - Holdings  │  │ - Analytics │
        └─────────────┘  └─────────────┘  └─────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          EVENT STREAMING LAYER                               │
│         Apache Kafka Cluster (Multi-DC, 100+ partitions)                    │
│  Topics: orders, trades, positions, market-data, risk-events, settlements   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA PERSISTENCE LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  TimescaleDB  │  Redis      │  MongoDB    │  S3/MinIO       │
│  (Trades)    │  (Time Series)│  (Cache)    │  (Documents)│  (Archives)     │
│  Cassandra   │  Elasticsearch│  InfluxDB   │  ClickHouse │  Aerospike      │
│  (Orders)    │  (Search)     │  (Metrics)  │  (Analytics)│  (Hot Cache)    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUPPORTING SERVICES LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Surveillance  │  Compliance  │  Notification │  Audit      │  Backup       │
│  Service       │  Service     │  Service      │  Service    │  Service      │
│  (Anti-fraud)  │  (Reporting) │  (Email/SMS)  │  (Logging)  │  (Recovery)   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING & OBSERVABILITY LAYER                          │
│  Prometheus │ Grafana │ Jaeger │ ELK Stack │ PagerDuty │ DataDog           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Gateway Layer
**Technology**: Kong, NGINX, AWS API Gateway, Traefik

**Responsibilities**:
- Request routing and load balancing
- SSL/TLS termination
- Rate limiting and throttling
- Request/response transformation
- API versioning
- Authentication/Authorization enforcement
- Circuit breaking
- Request/response caching

**Configuration**:
```yaml
api_gateway:
  instances: 10
  rate_limits:
    - path: /api/orders
      limit: 1000 req/sec/user
    - path: /api/marketdata
      limit: 10000 req/sec/user
  timeout:
    read: 5s
    write: 5s
    connection: 10s
  circuit_breaker:
    threshold: 50%
    timeout: 30s
```

### 2. Order Service
**Technology**: Go, Rust, C++

**Responsibilities**:
- Order validation (price, quantity, account balance)
- Order normalization and enrichment
- Order routing to matching engine
- Order lifecycle management (new, partial fill, filled, cancelled)
- Order modification and cancellation
- Bulk order processing

**Key Features**:
- Idempotency keys for duplicate prevention
- Pre-trade risk checks integration
- Order queue management with priority
- Support for all order types (Market, Limit, Stop, etc.)

**Performance Characteristics**:
- Latency: < 100 microseconds (p99)
- Throughput: 10M orders/sec
- Availability: 99.999%

### 3. Matching Engine (Core)
**Technology**: FPGA + C++/Rust

**Responsibilities**:
- Order matching based on price-time priority
- Order book maintenance
- Trade generation
- Market data publication
- Circuit breaker implementation

**Matching Algorithms**:
1. **Price-Time Priority (FIFO)**
   - Best price gets priority
   - Same price: First-In-First-Out

2. **Pro-Rata**
   - Orders at same price share fills proportionally

3. **Size Pro-Rata**
   - Larger orders get priority at same price

**Technical Implementation**:
```
Hardware: FPGA (Xilinx Ultrascale+)
Memory: 128GB DDR4 ECC
Network: 100Gbps RDMA
Latency: < 500 nanoseconds (FPGA)
Throughput: 10M orders/sec
Order Book Depth: 10,000 levels
```

**Order Book Structure**:
```go
type OrderBook struct {
    Symbol string
    BuyOrders  *PriorityQueue  // Max heap by price, then time
    SellOrders *PriorityQueue  // Min heap by price, then time
    LastTrade  Trade
    BBO        BestBidOffer
}
```

### 4. Market Data Service
**Technology**: Go, Rust, Kafka Streams

**Responsibilities**:
- Real-time market data distribution
- Level 1 data (BBO - Best Bid/Offer)
- Level 2 data (Full order book depth)
- Trade ticks and time & sales
- Market statistics (OHLCV, VWAP)
- Historical data queries

**Data Distribution**:
- **WebSocket**: For web/mobile clients
- **Multicast UDP**: For low-latency institutional clients
- **FIX**: For broker connections
- **gRPC Streaming**: For internal services

**Market Data Hierarchy**:
```
Level 1: Best Bid, Best Ask, Last Trade, Volume
Level 2: Full Order Book (10 levels each side)
Level 3: Individual Order IDs and quantities
```

### 5. Risk Management Service
**Technology**: Python (NumPy, Pandas), C++

**Responsibilities**:
- Pre-trade risk checks
- Real-time position tracking
- Margin calculations (Initial, Maintenance, Variation)
- Exposure limits enforcement
- Portfolio VaR (Value at Risk) calculation
- Stress testing

**Risk Models**:
```python
# Pre-trade Risk Check
def pre_trade_risk_check(order, account):
    checks = [
        check_buying_power(account, order),
        check_position_limits(account, order),
        check_concentration_risk(account, order),
        check_regulatory_limits(account, order),
        check_credit_limits(account, order)
    ]
    return all(checks)

# Margin Calculation
def calculate_margin(position, volatility, confidence=0.99):
    # SPAN-based margin
    price_scan_range = volatility * sqrt(252)
    initial_margin = position.value * price_scan_range
    maintenance_margin = initial_margin * 0.75
    return initial_margin, maintenance_margin
```

### 6. Trade Service
**Technology**: Java (Spring Boot), Kotlin

**Responsibilities**:
- Trade confirmation
- Trade allocation (for block trades)
- Trade reporting
- Trade cancellation/correction
- Give-up and take-up processing
- Average price calculation

### 7. Settlement Service
**Technology**: Java, PostgreSQL

**Responsibilities**:
- T+2 settlement cycle management
- Trade netting and consolidation
- DVP (Delivery vs Payment) processing
- Corporate actions processing
- Failed trade management
- Integration with clearing houses (DTCC, NSCC)

**Settlement Workflow**:
```
T+0: Trade Date
  - Trade capture
  - Trade confirmation
  - Allocation

T+1: Trade Date + 1
  - Trade matching
  - Affirmation
  - Pre-settlement checks

T+2: Settlement Date
  - Funds transfer
  - Securities transfer
  - Settlement confirmation
  - Reconciliation
```

### 8. Account Service
**Technology**: Node.js, PostgreSQL

**Responsibilities**:
- User registration and KYC
- Account management (cash, margin)
- Document management
- AML checks
- Accreditation verification

### 9. Portfolio Service
**Technology**: Python (Pandas), PostgreSQL

**Responsibilities**:
- Real-time portfolio valuation
- Holdings management
- P&L calculation (realized, unrealized)
- Performance attribution
- Tax lot tracking
- Corporate actions adjustment

### 10. Compliance & Surveillance Service
**Technology**: Python (ML models), Elasticsearch

**Responsibilities**:
- Real-time trade surveillance
- Market manipulation detection (wash trades, spoofing, layering)
- Best execution monitoring
- Regulatory reporting (CAT, OATS, MiFID II)
- Audit trail management
- Alert generation

**Surveillance Patterns**:
```python
# Wash Trade Detection
def detect_wash_trades(trades, threshold=0.9):
    for t1 in trades:
        for t2 in trades:
            if (t1.buyer == t2.seller and 
                t1.seller == t2.buyer and
                abs(t1.price - t2.price) / t1.price < threshold and
                abs(t1.time - t2.time) < timedelta(minutes=5)):
                return Alert("Potential Wash Trade", [t1, t2])

# Layering Detection
def detect_layering(orders, threshold=10):
    if len([o for o in orders if o.side == 'BUY']) > threshold:
        subsequent_sell = find_subsequent_sell(orders)
        if subsequent_sell:
            return Alert("Potential Layering", orders)
```

## Data Flow

### Order Placement Flow
```
1. Client → API Gateway → Order Service
2. Order Service → Risk Service (Pre-trade check)
3. Order Service → Matching Engine
4. Matching Engine → Match Algorithm
5. If Match:
   a. Matching Engine → Trade Service (Trade generation)
   b. Trade Service → Position Service (Update positions)
   c. Trade Service → Kafka (Trade event)
   d. Trade Service → Client (Trade confirmation)
6. If No Match:
   a. Matching Engine → Order Book (Add to book)
   b. Matching Engine → Market Data Service (Update order book)
   c. Market Data Service → Kafka (Market data update)
```

### Market Data Publication Flow
```
1. Matching Engine → Market Data Service (Order book update)
2. Market Data Service → Kafka (Publish event)
3. Kafka → Consumer Groups:
   a. WebSocket Server → Web/Mobile Clients
   b. FIX Gateway → Institutional Clients
   c. Multicast Server → Co-located Clients
   d. Historical Data Service → TimescaleDB
4. Cache Layer (Redis) → Update cached data
```

### Settlement Flow
```
T+0:
1. Trade Service → Settlement Service (Trade capture)
2. Settlement Service → Kafka (Settlement event)
3. Settlement Service → PostgreSQL (Store trade)

T+1:
4. Settlement Service → CCP (Central Counterparty) for matching
5. CCP → Settlement Service (Affirmation)
6. Settlement Service → Risk Service (Collateral check)

T+2:
7. Settlement Service → Payment System (Fund transfer)
8. Payment System → Custodian (Securities transfer)
9. Custodian → Settlement Service (Confirmation)
10. Settlement Service → Account Service (Update balances)
11. Settlement Service → Portfolio Service (Update holdings)
```

## Technology Stack

### Programming Languages
- **C++/Rust**: Matching engine, low-latency components
- **Go**: High-throughput services (Order, Market Data)
- **Java/Kotlin**: Business logic services (Trade, Settlement)
- **Python**: Risk analytics, ML-based surveillance
- **Node.js**: Real-time communication services
- **TypeScript**: Web frontend

### Databases
- **PostgreSQL**: Transactional data (accounts, trades)
- **Cassandra**: High-write throughput (orders, events)
- **TimescaleDB**: Time-series data (market data, metrics)
- **Redis**: Caching, session management, real-time data
- **MongoDB**: Document storage (compliance docs, reports)
- **ClickHouse**: Analytics and reporting
- **Elasticsearch**: Full-text search, audit logs

### Message Brokers
- **Apache Kafka**: Event streaming (100k+ msg/sec)
- **RabbitMQ**: Task queues, async processing
- **Redis Pub/Sub**: Real-time notifications

### Cloud Infrastructure (AWS)
- **Compute**: EC2 (C6i, C6gn), ECS, EKS, Lambda
- **Storage**: S3, EBS, EFS
- **Database**: RDS, DynamoDB, ElastiCache, DocumentDB
- **Networking**: VPC, Direct Connect, Route 53, CloudFront
- **Security**: IAM, KMS, Secrets Manager, WAF
- **Monitoring**: CloudWatch, X-Ray

### Alternative Cloud Providers
- **GCP**: Compute Engine, GKE, Cloud SQL, BigQuery
- **Azure**: VMs, AKS, Cosmos DB, Azure SQL

### Observability
- **Metrics**: Prometheus, InfluxDB
- **Visualization**: Grafana, Kibana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana), Fluentd
- **Tracing**: Jaeger, Zipkin, OpenTelemetry
- **APM**: DataDog, New Relic, Dynatrace
- **Alerting**: PagerDuty, Opsgenie

### Infrastructure as Code
- **Terraform**: Multi-cloud infrastructure provisioning
- **Ansible**: Configuration management
- **Helm**: Kubernetes package management
- **ArgoCD**: GitOps continuous delivery

### CI/CD
- **Jenkins**: Build automation
- **GitLab CI/CD**: Source control and pipelines
- **Spinnaker**: Multi-cloud deployment
- **GitHub Actions**: Workflow automation

## Deployment Architecture

### Multi-Region Active-Active

```
Region 1 (Primary): US-East-1
├── Availability Zone 1a
│   ├── API Gateway (3 instances)
│   ├── Order Service (5 instances)
│   ├── Matching Engine (1 FPGA)
│   ├── Market Data Service (3 instances)
│   └── PostgreSQL Primary
├── Availability Zone 1b
│   ├── API Gateway (3 instances)
│   ├── Order Service (5 instances)
│   ├── Matching Engine (1 FPGA - standby)
│   ├── Market Data Service (3 instances)
│   └── PostgreSQL Replica
└── Availability Zone 1c
    ├── API Gateway (3 instances)
    ├── Trade Service (3 instances)
    ├── Risk Service (3 instances)
    └── Redis Cluster (3 nodes)

Region 2 (DR): US-West-2
├── Same setup as Region 1
└── Cross-region replication from Region 1

Co-Location Facility (Optional)
├── Matching Engine (FPGA)
├── Market Data Multicast
└── Direct connections for HFT firms
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: order-service
            topologyKey: kubernetes.io/hostname
      containers:
      - name: order-service
        image: stock-exchange/order-service:v1.2.3
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        env:
        - name: KAFKA_BROKERS
          value: "kafka-1:9092,kafka-2:9092,kafka-3:9092"
        - name: POSTGRES_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
```

## Network Architecture

### Network Segmentation

```
┌─────────────────────────────────────────────────────────────┐
│                       Internet                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                  ┌──────▼──────┐
                  │   AWS WAF    │
                  │   CloudFront │
                  └──────┬──────┘
                         │
            ┌────────────▼─────────────┐
            │   Public Subnet          │
            │   - NAT Gateway          │
            │   - Bastion Host         │
            │   - Load Balancer        │
            └────────────┬─────────────┘
                         │
            ┌────────────▼─────────────┐
            │   DMZ Subnet             │
            │   - API Gateway          │
            │   - WAF                  │
            └────────────┬─────────────┘
                         │
            ┌────────────▼─────────────┐
            │   Application Subnet     │
            │   - Microservices (EKS)  │
            │   - Service Mesh         │
            └────────────┬─────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ Data    │   │ Cache   │   │ Message │
    │ Subnet  │   │ Subnet  │   │ Subnet  │
    │ - RDS   │   │ - Redis │   │ - Kafka │
    │ - Cassan│   │ - Memcac│   │ - Rabbit│
    └─────────┘   └─────────┘   └─────────┘

    ┌──────────────────────────────────────┐
    │   Management & Monitoring Subnet     │
    │   - Prometheus                       │
    │   - Grafana                          │
    │   - ELK Stack                        │
    └──────────────────────────────────────┘
```

### Network Specifications
- **VPC CIDR**: 10.0.0.0/16
- **Subnets**: /24 per subnet (254 hosts)
- **Inter-service Communication**: Private network (10 Gbps)
- **External Communication**: Public load balancer with TLS
- **Co-location Link**: Dedicated 100 Gbps fiber with RDMA

## Integration Points

### External Integrations

1. **Regulatory Bodies**
   - SEC: CAT reporting
   - FINRA: OATS reporting
   - MiFID II: Transaction reporting

2. **Clearing Houses**
   - DTCC (Depository Trust & Clearing Corporation)
   - NSCC (National Securities Clearing Corporation)
   - OCC (Options Clearing Corporation)

3. **Market Data Providers**
   - Bloomberg
   - Reuters
   - ICE Data Services

4. **Banks & Custodians**
   - ACH transfers
   - Wire transfers
   - Securities custody

5. **Third-party Services**
   - KYC/AML: Jumio, Onfido
   - Identity Verification: Plaid, Yodlee
   - Payment Processing: Stripe, Plaid
   - SMS/Email: Twilio, SendGrid

### Internal Integrations

```
┌────────────────────┐
│  API Gateway       │
└────────┬───────────┘
         │
         │ REST/gRPC
         │
         ▼
┌────────────────────┐      ┌────────────────────┐
│  Order Service     │◄────►│  Risk Service      │
└────────┬───────────┘      └────────────────────┘
         │
         │ Kafka Events
         │
         ▼
┌────────────────────┐      ┌────────────────────┐
│  Matching Engine   │─────►│  Market Data Svc   │
└────────┬───────────┘      └────────────────────┘
         │
         │ gRPC Stream
         │
         ▼
┌────────────────────┐      ┌────────────────────┐
│  Trade Service     │◄────►│  Position Service  │
└────────┬───────────┘      └───────────┬────────┘
         │                              │
         │ Async (Kafka)                │
         │                              │
         ▼                              ▼
┌────────────────────┐      ┌────────────────────┐
│  Settlement Svc    │◄────►│  Portfolio Service │
└────────────────────┘      └────────────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: January 15, 2026  
**Status**: Draft
