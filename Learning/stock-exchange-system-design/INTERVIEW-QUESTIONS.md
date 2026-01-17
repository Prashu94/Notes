# Stock Exchange System Design - Interview Questions

## Overview

This document contains comprehensive interview questions based on the stock exchange system design documentation. Questions are organized by difficulty level and topic area.

---

## Table of Contents

1. [System Design & Architecture](#system-design--architecture)
2. [Matching Engine & Low Latency](#matching-engine--low-latency)
3. [Microservices & Spring Boot](#microservices--spring-boot)
4. [Databases & Data Management](#databases--data-management)
5. [Cloud Infrastructure & AWS](#cloud-infrastructure--aws)
6. [Performance & Scalability](#performance--scalability)
7. [Security & Compliance](#security--compliance)
8. [Operational Excellence](#operational-excellence)
9. [Behavioral & Scenario-Based](#behavioral--scenario-based)

---

## System Design & Architecture

### Junior Level (1-3 years)

**Q1: What are the core components of a stock exchange system?**
- Expected: Order Management, Matching Engine, Market Data, Risk Management, Settlement
- Follow-up: How do these components communicate with each other?

**Q2: What is the difference between Level 1 and Level 2 market data?**
- Expected: Level 1 = best bid/ask only, Level 2 = full order book depth (20+ levels)
- Follow-up: Which one would you use for a retail trading app and why?

**Q3: Explain the order lifecycle from submission to execution.**
- Expected: Submission → Validation → Risk Check → Routing → Matching → Execution → Confirmation → Settlement
- Follow-up: What happens if the risk check fails?

**Q4: What is the difference between a Market Order and a Limit Order?**
- Expected: Market = execute at current best price, Limit = execute only at specified price or better
- Follow-up: Which one has guaranteed execution but uncertain price?

**Q5: What does T+2 settlement mean?**
- Expected: Trade settles 2 business days after trade date (funds/securities transfer)
- Follow-up: Why not T+0 (instant settlement)?

### Mid Level (3-6 years)

**Q6: Design the high-level architecture for a stock exchange handling 500 million orders per day.**
- Expected: 
  - Multi-tier architecture (API Gateway → Services → Matching Engine → Data Layer)
  - Event-driven with Kafka for order/trade events
  - Polyglot persistence (PostgreSQL, Cassandra, Redis, TimescaleDB)
  - FPGA for matching engine
  - Multi-region deployment with failover
- Follow-up: How would you handle peak trading hours (10x normal load at market open)?

**Q7: Explain the CAP theorem and how it applies to different components in a stock exchange.**
- Expected:
  - Matching Engine: CP (Consistency + Partition tolerance) - can't have two different prices
  - Market Data: AP (Availability + Partition tolerance) - slightly stale data acceptable
  - User Sessions: AP - user experience over perfect consistency
- Follow-up: What's your strategy for handling network partitions?

**Q8: How would you implement idempotency for order submissions?**
- Expected:
  - Client-generated Order ID (UUID)
  - Redis/Cassandra deduplication cache with TTL
  - Check cache before processing order
  - Idempotency key in API headers
- Follow-up: What's the appropriate TTL for the deduplication cache?

**Q9: Design an API Gateway for the stock exchange system.**
- Expected:
  - Authentication (OAuth 2.0 + JWT)
  - Rate limiting (Redis-based token bucket)
  - Request routing to microservices
  - Circuit breaker pattern
  - SSL/TLS termination
- Follow-up: How many requests per second should the gateway handle?

**Q10: How do you ensure exactly-once semantics for trade confirmations?**
- Expected:
  - Kafka idempotent producer
  - Transactional outbox pattern
  - Database + Kafka transaction coordination
  - Consumer with deduplication logic
- Follow-up: What happens if Kafka is down?

### Senior Level (6+ years)

**Q11: You need to reduce order-to-trade latency from 5ms to <1ms. Walk through your optimization strategy.**
- Expected:
  - FPGA for matching engine (30-50μs vs 500μs software)
  - Kernel bypass networking (DPDK) - save 20-30μs
  - Co-location for market makers
  - Zero-copy serialization (FlatBuffers, Cap'n Proto)
  - CPU pinning, NUMA awareness
  - In-memory risk checks (Aerospike)
  - Latency budget breakdown per component
- Follow-up: What's the cost-benefit analysis of FPGA vs software optimization?

**Q12: Design a disaster recovery strategy with RTO of 5 minutes and RPO of 0 seconds.**
- Expected:
  - Multi-region active-passive deployment
  - Synchronous replication for matching engine state
  - Continuous WAL shipping for databases
  - Automated failover with health checks
  - Pre-warmed standby instances
  - Runbook automation
- Follow-up: How do you test DR without impacting production?

**Q13: The matching engine needs to handle 1.2 million orders/second. How do you architect it?**
- Expected:
  - FPGA-based matching core
  - Symbol partitioning (hash-based sharding)
  - In-memory order book (Red-Black tree)
  - Lock-free data structures
  - Parallel processing per symbol
  - Hot-standby FPGA failover
  - Hardware timestamping
- Follow-up: How do you handle corporate actions (splits, dividends)?

**Q14: Design a market surveillance system to detect manipulation (spoofing, layering, wash trading).**
- Expected:
  - Real-time stream processing (Kafka Streams, Flink)
  - Pattern detection algorithms
  - Machine learning models for anomaly detection
  - Time-series analysis (order cancellation ratios)
  - Alert generation with severity levels
  - Investigation workflow
- Follow-up: How do you reduce false positives?

**Q15: Your system needs to comply with SEC Rule 17a-4 (WORM storage, 7-year retention). How do you implement this?**
- Expected:
  - Immutable audit logs (append-only)
  - S3 Object Lock or Glacier Vault Lock
  - Compliance mode (can't be deleted by anyone)
  - Legal hold capability
  - Cryptographic hashing for tamper detection
  - Regular compliance audits
- Follow-up: How do you handle GDPR right-to-deletion conflicts?

---

## Matching Engine & Low Latency

### Junior Level

**Q16: What is Price-Time Priority matching algorithm?**
- Expected: Orders matched by best price first, then FIFO within same price level
- Follow-up: What's an alternative algorithm?

**Q17: Explain what an order book is.**
- Expected: Data structure showing all buy/sell orders for a symbol at different price levels
- Follow-up: How would you represent it in code?

**Q18: What causes latency in an order matching system?**
- Expected: Network delay, serialization, database writes, OS context switches, GC pauses
- Follow-up: Which one is the biggest contributor?

### Mid Level

**Q19: Implement an in-memory order book supporting add, cancel, and match operations.**
- Expected:
```java
class OrderBook {
    TreeMap<BigDecimal, Queue<Order>> buyOrders;  // Price DESC
    TreeMap<BigDecimal, Queue<Order>> sellOrders; // Price ASC
    
    void addOrder(Order order) { /* ... */ }
    void cancelOrder(String orderId) { /* ... */ }
    Trade matchOrder(Order order) { /* ... */ }
    BBO getBestBidOffer() { /* ... */ }
}
```
- Follow-up: What's the time complexity of each operation?

**Q20: How would you implement partial fills for large orders?**
- Expected:
  - Track remaining quantity in Order object
  - Match in chunks against opposite side
  - Generate multiple Trade objects
  - Update order status (PartiallyFilled vs Filled)
  - Send interim notifications
- Follow-up: How do you ensure atomicity of partial fills?

**Q21: Explain the trade-offs between FPGA and software-based matching engines.**
- Expected:
  - **FPGA**: 30-50μs latency, deterministic, low power (75W), expensive ($500K), hard to modify
  - **Software**: 500μs latency, flexible, cheaper ($50K), easier to update, GC pauses
- Follow-up: When would you choose one over the other?

**Q22: Design a sequencer for timestamping orders with nanosecond precision.**
- Expected:
  - Hardware timestamping (NIC-level)
  - GPS/PTP time synchronization
  - Monotonic sequence numbers
  - Lamport clock for ordering
  - Store in order metadata
- Follow-up: How do you handle clock drift?

### Senior Level

**Q23: You're seeing 99th percentile latency spikes from 50μs to 500μs. How do you debug this?**
- Expected:
  - Check GC logs (young/old gen pauses)
  - CPU affinity and NUMA analysis
  - Network packet loss/retransmissions
  - Disk I/O (even with in-memory)
  - OS scheduler preemption
  - Lock contention analysis
  - Latency percentile histograms (HdrHistogram)
- Follow-up: Show me the actual commands/tools you'd use.

**Q24: Design a lock-free order book implementation.**
- Expected:
  - Compare-and-swap (CAS) operations
  - Lock-free queue (LMAX Disruptor pattern)
  - RCU (Read-Copy-Update) for order book
  - Version numbers for consistency
  - Memory barriers and volatile semantics
- Follow-up: What are the pitfalls of lock-free data structures?

**Q25: Implement FPGA-based matching engine logic in VHDL/Verilog.**
- Expected:
  - FSM (Finite State Machine) for order processing
  - Pipeline stages (parse → validate → match → output)
  - FIFO queues for buffering
  - Clock domain crossing
  - Resource utilization (LUTs, BRAMs)
- Follow-up: How do you verify correctness of FPGA logic?

---

## Microservices & Spring Boot

### Junior Level

**Q26: What are the benefits of microservices architecture for a stock exchange?**
- Expected: Independent scaling, fault isolation, technology freedom, team autonomy
- Follow-up: What are the drawbacks?

**Q27: Explain the difference between REST and WebSocket for real-time market data.**
- Expected:
  - REST: Request-response, polling overhead, HTTP overhead
  - WebSocket: Persistent connection, bidirectional, low overhead, push-based
- Follow-up: When would you use Server-Sent Events (SSE) instead?

**Q28: What is Spring Boot Actuator and how would you use it?**
- Expected: Production-ready features (health checks, metrics, env info)
- Follow-up: Which endpoints would you expose for a trading system?

### Mid Level

**Q29: Implement a Spring Boot order service with proper error handling and validation.**
```java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {
    
    @PostMapping
    @CircuitBreaker(name = "orderService", fallbackMethod = "placeOrderFallback")
    public ResponseEntity<OrderResponse> placeOrder(
            @Valid @RequestBody OrderRequest request) {
        // Implementation
    }
    
    public ResponseEntity<OrderResponse> placeOrderFallback(
            OrderRequest request, Exception e) {
        // Fallback logic
    }
}
```
- Follow-up: How do you handle validation errors vs business logic errors?

**Q30: How would you implement circuit breaker pattern with Resilience4j?**
- Expected:
```yaml
resilience4j:
  circuitbreaker:
    instances:
      orderService:
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
        sliding-window-size: 10
        minimum-number-of-calls: 5
```
- Follow-up: When would the circuit breaker open?

**Q31: Design a Kafka consumer for processing trade events with exactly-once semantics.**
- Expected:
  - Enable `enable.idempotence=true`
  - Transactional producer/consumer
  - Offset management
  - Retry logic with DLQ
  - Consumer group management
- Follow-up: How do you handle consumer lag?

**Q32: Implement caching strategy for stock prices using Redis.**
- Expected:
```java
@Cacheable(value = "stockPrices", key = "#symbol")
public BigDecimal getStockPrice(String symbol) {
    return priceRepository.findBySymbol(symbol);
}

@CacheEvict(value = "stockPrices", key = "#symbol")
public void updatePrice(String symbol, BigDecimal price) {
    // Update price
}
```
- Follow-up: What's the appropriate TTL for price cache?

**Q33: How do you implement distributed tracing across microservices?**
- Expected:
  - OpenTelemetry or Zipkin
  - Trace ID propagation via HTTP headers
  - Span creation for each service
  - Context propagation through Kafka
  - Jaeger for visualization
- Follow-up: What's the performance overhead of tracing?

### Senior Level

**Q34: Design a Spring Cloud Gateway configuration for 1 million requests/second.**
- Expected:
  - WebFlux (non-blocking)
  - Connection pooling tuning
  - Rate limiting with Redis
  - Circuit breaker per route
  - Request/response size limits
  - Netty tuning (worker threads, buffers)
  - Load balancing strategies
- Follow-up: How do you handle gateway failure?

**Q35: Implement saga pattern for order placement with compensation logic.**
- Expected:
  - Choreography vs Orchestration
  - Event-driven saga with Kafka
  - Compensation transactions
  - State machine for saga steps
  - Timeout handling
  - Idempotency for each step
- Follow-up: What happens if compensation fails?

**Q36: Your Spring Boot services are consuming 8GB memory each. How do you optimize?**
- Expected:
  - JVM heap tuning (-Xmx, -Xms)
  - GC algorithm selection (G1GC vs ZGC)
  - Connection pool sizing
  - ThreadPool tuning
  - Spring Boot actuator metrics
  - Heap dump analysis
  - Native image compilation (GraalVM)
- Follow-up: Show me the JVM flags you'd use.

---

## Databases & Data Management

### Junior Level

**Q37: Why use multiple databases (polyglot persistence) in a stock exchange?**
- Expected:
  - PostgreSQL for ACID transactions (accounts)
  - Cassandra for high write throughput (orders)
  - Redis for caching (hot data)
  - TimescaleDB for time-series (market data)
- Follow-up: What are the operational challenges?

**Q38: What is eventual consistency and where would you use it?**
- Expected: Data becomes consistent over time, acceptable for non-critical reads
- Follow-up: Give an example where it's NOT acceptable.

**Q39: Explain the difference between OLTP and OLAP databases.**
- Expected:
  - OLTP: Transactional, row-based, low latency (PostgreSQL)
  - OLAP: Analytical, columnar, batch queries (ClickHouse)
- Follow-up: Which one for trade reporting?

### Mid Level

**Q40: Design the database schema for orders and trades.**
```sql
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL,  -- BUY/SELL
    quantity BIGINT NOT NULL,
    price DECIMAL(18,6),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_account_symbol (account_id, symbol),
    INDEX idx_status_created (status, created_at)
);

CREATE TABLE trades (
    trade_id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    quantity BIGINT NOT NULL,
    price DECIMAL(18,6) NOT NULL,
    trade_time TIMESTAMP NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
```
- Follow-up: How do you partition this for 150 million trades/day?

**Q41: How would you implement event sourcing for order lifecycle?**
- Expected:
  - Store all events (OrderCreated, OrderValidated, OrderMatched, OrderFilled)
  - Append-only event log
  - Rebuild state by replaying events
  - Snapshots for performance
  - Kafka as event store
- Follow-up: How do you handle schema evolution?

**Q42: Design a database archival strategy for 7-year trade data retention.**
- Expected:
  - Hot (90 days): PostgreSQL/Cassandra (fast queries)
  - Warm (1 year): Compressed tables, slower storage
  - Cold (7 years): S3 Glacier, Parquet format
  - Lifecycle policies
  - Restore mechanism
- Follow-up: How do you query across hot/warm/cold tiers?

**Q43: Implement optimistic locking for account balance updates.**
```java
@Entity
public class Account {
    @Id
    private UUID id;
    private BigDecimal balance;
    
    @Version
    private Long version;
}

// In service
@Transactional
public void updateBalance(UUID accountId, BigDecimal amount) {
    Account account = accountRepo.findById(accountId);
    account.setBalance(account.getBalance().add(amount));
    accountRepo.save(account);  // Version check
}
```
- Follow-up: What happens on version conflict?

### Senior Level

**Q44: Your Cassandra cluster is experiencing high read latency. How do you troubleshoot and fix it?**
- Expected:
  - Check compaction status
  - Analyze partition sizes (tombstones)
  - Review read repair settings
  - Check consistency level (QUORUM vs ONE)
  - GC pressure on nodes
  - Disk I/O utilization
  - Add read replicas
  - Materialized views for common queries
- Follow-up: When would you consider re-sharding?

**Q45: Design a CQRS implementation for order management.**
- Expected:
  - **Command side**: Write to event store (Kafka), PostgreSQL for current state
  - **Query side**: Read models in Redis, Elasticsearch, materialized views
  - Event handlers to update read models
  - Eventual consistency acceptable for queries
  - Snapshot mechanism
- Follow-up: How do you handle query-side lag?

**Q46: Implement a time-series compression strategy for tick data (1TB/day).**
- Expected:
  - Delta encoding for prices
  - Run-length encoding for timestamps
  - Columnar format (Parquet, ORC)
  - TimescaleDB hypertables with compression
  - 95%+ compression ratio achievable
  - Partition by time (daily chunks)
- Follow-up: What's the query performance trade-off?

---

## Cloud Infrastructure & AWS

### Junior Level

**Q47: What AWS services would you use for a stock exchange system?**
- Expected: EKS, RDS, ElastiCache, MSK, S3, CloudWatch
- Follow-up: Why EKS over ECS?

**Q48: Explain the difference between ALB and NLB.**
- Expected:
  - ALB: Layer 7 (HTTP/S), path-based routing, SSL termination
  - NLB: Layer 4 (TCP), ultra-low latency, static IP
- Follow-up: Which one for FIX protocol?

**Q49: What is a VPC and why do you need it?**
- Expected: Virtual Private Cloud, network isolation, security, subnets
- Follow-up: Explain public vs private subnet.

### Mid Level

**Q50: Design a multi-AZ deployment for 99.99% availability.**
- Expected:
  - 3 availability zones
  - RDS Multi-AZ for automatic failover
  - EKS node groups across AZs
  - ALB with cross-zone load balancing
  - Redis cluster mode
  - Multi-AZ MSK cluster
- Follow-up: What's the failover time for each component?

**Q51: How would you implement auto-scaling for order processing services?**
- Expected:
  - Kubernetes HPA (Horizontal Pod Autoscaler)
  - Metrics: CPU, memory, custom metrics (order queue depth)
  - Scale-up: add pods (1-2 minutes)
  - Scale-down: graceful shutdown (drain connections)
  - Cluster autoscaler for nodes
- Follow-up: What's the cost of over-provisioning?

**Q52: Design a CI/CD pipeline for deploying to EKS.**
- Expected:
  - GitHub Actions / GitLab CI
  - Build Docker image
  - Push to ECR
  - Helm chart update
  - ArgoCD GitOps deployment
  - Blue-green or canary deployment
  - Automated testing (smoke tests)
- Follow-up: How do you rollback a bad deployment?

**Q53: Implement Terraform for provisioning AWS infrastructure.**
```hcl
module "vpc" {
  source = "./modules/vpc"
  cidr_block = "10.0.0.0/16"
  azs = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

module "eks" {
  source = "./modules/eks"
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
}

module "rds" {
  source = "./modules/rds"
  instance_class = "db.r6i.4xlarge"
  multi_az = true
}
```
- Follow-up: How do you manage state file securely?

### Senior Level

**Q54: Your AWS bill is $150K/month. How do you optimize to reduce by 30%?**
- Expected:
  - Spot instances for non-critical workloads (70% savings)
  - Savings Plans / Reserved Instances
  - Right-size instances (unused capacity)
  - S3 Intelligent-Tiering
  - RDS instance optimization
  - Data transfer costs (use CloudFront)
  - Delete unused EBS volumes
  - Cost allocation tags
- Follow-up: Show me the cost breakdown analysis.

**Q55: Design a disaster recovery strategy across AWS regions with 5-minute RTO.**
- Expected:
  - Active-passive multi-region
  - Cross-region RDS replication
  - S3 cross-region replication
  - Route 53 health checks and failover
  - Warm standby EKS cluster
  - Database WAL shipping
  - Automated failover scripts
  - Regular DR drills
- Follow-up: What's the monthly cost of DR setup?

**Q56: Implement network architecture for <5μs latency between co-located services.**
- Expected:
  - EC2 placement groups (cluster placement)
  - Enhanced networking (SR-IOV)
  - Elastic Network Adapter (ENA)
  - Jumbo frames (MTU 9000)
  - Direct Connect for co-location
  - DPDK for kernel bypass
- Follow-up: What's the incremental cost?

---

## Performance & Scalability

### Junior Level

**Q57: What is latency vs throughput?**
- Expected:
  - Latency: Time to complete one operation
  - Throughput: Number of operations per second
- Follow-up: Can you have high throughput with high latency?

**Q58: Explain the difference between vertical and horizontal scaling.**
- Expected:
  - Vertical: Bigger machine (more CPU/RAM)
  - Horizontal: More machines
- Follow-up: Which one for stateless order services?

**Q59: What is caching and why is it important?**
- Expected: Store frequently accessed data in fast memory, reduce database load
- Follow-up: What data would you cache in a stock exchange?

### Mid Level

**Q60: Implement a multi-level caching strategy.**
- Expected:
```
L1: In-memory (Caffeine) - <1μs
L2: Redis (distributed) - <1ms  
L3: PostgreSQL read replica - <5ms
```
- Follow-up: How do you handle cache invalidation?

**Q61: Design a load balancing strategy for 1 million concurrent WebSocket connections.**
- Expected:
  - ALB with WebSocket support
  - Sticky sessions (source IP affinity)
  - Connection pooling
  - Horizontal scaling (50+ instances)
  - Each instance handles 20K connections
  - Health checks and auto-recovery
- Follow-up: What happens during instance replacement?

**Q62: How would you implement rate limiting for API requests?**
- Expected:
  - Token bucket algorithm
  - Redis for distributed counter
  - Per-user and per-IP limits
  - Different tiers (retail: 1K req/min, institutional: 100K req/min)
  - Exponential backoff on 429 errors
- Follow-up: How do you prevent abuse?

**Q63: Optimize a database query taking 5 seconds to return trade history.**
```sql
-- Before
SELECT * FROM trades 
WHERE account_id = ? 
ORDER BY trade_time DESC 
LIMIT 100;

-- After
SELECT trade_id, symbol, quantity, price, trade_time 
FROM trades 
WHERE account_id = ? 
  AND trade_time > NOW() - INTERVAL '90 days'
ORDER BY trade_time DESC 
LIMIT 100;

-- Add index
CREATE INDEX idx_account_time ON trades(account_id, trade_time DESC);
```
- Follow-up: What if the query is still slow?

### Senior Level

**Q64: Your system is hitting 1.2M orders/sec but you need to support 2M. What do you do?**
- Expected:
  - Profile bottlenecks (CPU, network, database)
  - Horizontal scaling (add more matching engine shards)
  - Symbol partitioning optimization
  - Lock-free data structures
  - FPGA upgrade (higher clock speed)
  - Batch processing where possible
  - Async processing for non-critical path
- Follow-up: Show me the capacity planning spreadsheet.

**Q65: Design a distributed rate limiter handling 10M req/sec.**
- Expected:
  - Redis Cluster with Lua scripts
  - Sliding window counter
  - Distributed token bucket
  - Pre-compute rate limits per user
  - Local cache with sync to Redis
  - Graceful degradation
- Follow-up: What's the false positive rate?

**Q66: Implement a connection pool optimization strategy for 100K concurrent database connections.**
- Expected:
  - HikariCP configuration tuning
  - Connection pool per service instance
  - Pool size = (CPU cores × 2) + effective_spindle_count
  - Connection timeout: 30s
  - Idle timeout: 10 minutes
  - Prepared statement cache
  - Read/write splitting
- Follow-up: Show me the actual HikariCP config.

---

## Security & Compliance

### Junior Level

**Q67: What is OAuth 2.0 and how does it work?**
- Expected: Authorization framework, access tokens, refresh tokens, client credentials
- Follow-up: Explain the difference between OAuth and OpenID Connect.

**Q68: Why do you need encryption at rest and in transit?**
- Expected: Protect data from unauthorized access during storage and transmission
- Follow-up: What encryption algorithm would you use?

**Q69: What is SQL injection and how do you prevent it?**
- Expected: Malicious SQL code in input, use parameterized queries/prepared statements
- Follow-up: Show me a vulnerable query and the fix.

### Mid Level

**Q70: Implement JWT-based authentication for trading APIs.**
```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                    HttpServletResponse response,
                                    FilterChain filterChain) {
        String token = extractToken(request);
        if (validateToken(token)) {
            Authentication auth = getAuthentication(token);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        filterChain.doFilter(request, response);
    }
}
```
- Follow-up: How do you handle token expiration and refresh?

**Q71: Design a KYC/AML compliance system.**
- Expected:
  - Identity verification (Jumio, Onfido)
  - Document verification (passport, driver's license)
  - Address verification (utility bill)
  - Sanctions screening (OFAC, UN)
  - PEP (Politically Exposed Person) check
  - Continuous monitoring
  - Risk scoring
- Follow-up: How long should KYC verification take?

**Q72: Implement audit logging for all order operations.**
```java
@Aspect
@Component
public class AuditAspect {
    
    @Around("@annotation(Audited)")
    public Object auditMethod(ProceedingJoinPoint joinPoint) {
        String user = SecurityContextHolder.getContext().getAuthentication().getName();
        String method = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        
        auditLog.log(user, method, args, timestamp);
        
        Object result = joinPoint.proceed();
        return result;
    }
}
```
- Follow-up: How do you ensure logs are immutable?

**Q73: Design a DDoS protection strategy.**
- Expected:
  - AWS Shield Advanced
  - WAF with rate limiting rules
  - CloudFront for edge caching
  - API Gateway throttling
  - CAPTCHA for suspicious traffic
  - IP reputation filtering
  - Automatic scaling to absorb load
- Follow-up: What's the cost of AWS Shield Advanced?

### Senior Level

**Q74: You need to achieve PCI DSS Level 1 compliance. What's required?**
- Expected:
  - Network segmentation (DMZ)
  - Encryption of cardholder data
  - Access control (MFA, least privilege)
  - Vulnerability management
  - Security monitoring and testing
  - Information security policy
  - Quarterly PCI scans
  - Annual on-site assessment
- Follow-up: What's the audit cost and timeline?

**Q75: Design a zero-trust security architecture for microservices.**
- Expected:
  - Mutual TLS (mTLS) between all services
  - Service mesh (Istio) for policy enforcement
  - Identity-based access (SPIFFE/SPIRE)
  - No implicit trust based on network location
  - Continuous verification
  - Least privilege access
  - Encrypted everything
- Follow-up: What's the performance overhead?

**Q76: Implement a secrets management strategy for 100+ microservices.**
- Expected:
  - AWS Secrets Manager / HashiCorp Vault
  - Secrets rotation (every 90 days)
  - IAM roles for services (no hardcoded credentials)
  - Encryption at rest with KMS
  - Audit logging of secret access
  - Emergency break-glass procedure
  - Secret versioning
- Follow-up: How do you handle secret rotation without downtime?

---

## Operational Excellence

### Junior Level

**Q77: What metrics would you monitor for a stock exchange system?**
- Expected: Latency, throughput, error rate, CPU, memory, disk, network
- Follow-up: What's an acceptable error rate?

**Q78: Explain the difference between metrics, logs, and traces.**
- Expected:
  - Metrics: Aggregated numbers (CPU, latency)
  - Logs: Discrete events (errors, requests)
  - Traces: Request flow across services
- Follow-up: Which one helps debug a slow API?

**Q79: What is an SLO and how is it different from SLA?**
- Expected:
  - SLO: Service Level Objective (internal target)
  - SLA: Service Level Agreement (contractual)
- Follow-up: Give an example of each.

### Mid Level

**Q80: Design a monitoring dashboard for order processing.**
- Expected:
  - Order submission rate (orders/sec)
  - Order latency (p50, p95, p99)
  - Order success rate (%)
  - Error rate by type
  - Queue depth
  - Database connection pool usage
  - JVM heap usage
- Follow-up: What alert thresholds would you set?

**Q81: Implement distributed tracing for debugging a slow order placement.**
```java
@NewSpan("placeOrder")
public OrderResponse placeOrder(OrderRequest request) {
    Span span = tracer.currentSpan();
    span.tag("order.symbol", request.getSymbol());
    span.tag("order.quantity", request.getQuantity());
    
    // Call risk service
    Span riskSpan = tracer.nextSpan().name("checkRisk").start();
    riskService.checkRisk(request);
    riskSpan.finish();
    
    // Continue processing
}
```
- Follow-up: How do you find the slowest service in the chain?

**Q82: Design an alerting strategy with on-call rotation.**
- Expected:
  - PagerDuty / Opsgenie for alerts
  - Alert severity: P1 (immediate), P2 (30 min), P3 (next day)
  - Escalation policy
  - Runbooks for common issues
  - On-call rotation (weekly)
  - Alert fatigue prevention (deduplication)
  - Postmortem process
- Follow-up: How many P1 alerts per week is acceptable?

**Q83: Implement graceful shutdown for a Spring Boot service.**
```java
@Component
public class GracefulShutdown implements ApplicationListener<ContextClosedEvent> {
    
    @Override
    public void onApplicationEvent(ContextClosedEvent event) {
        log.info("Received shutdown signal");
        
        // Stop accepting new requests
        tomcat.pause();
        
        // Wait for in-flight requests (max 30 seconds)
        Thread.sleep(30000);
        
        // Close resources
        dataSource.close();
        kafkaProducer.close();
        
        log.info("Graceful shutdown complete");
    }
}
```
- Follow-up: What if shutdown takes longer than 30 seconds?

### Senior Level

**Q84: Design an SRE (Site Reliability Engineering) model for the stock exchange.**
- Expected:
  - Error budget: 99.99% uptime = 52 minutes/year
  - SLI (Service Level Indicators): latency, availability, error rate
  - SLO: Order latency <1ms (p95), Availability 99.99%
  - Toil reduction through automation
  - Incident response process
  - Postmortem culture
  - Capacity planning
- Follow-up: What happens when error budget is exhausted?

**Q85: You have 5 P1 incidents per week. How do you reduce them?**
- Expected:
  - Root cause analysis for each incident
  - Identify patterns (time, component, trigger)
  - Implement preventive measures
  - Chaos engineering to find weaknesses
  - Improve monitoring and alerting
  - Better testing (integration, load, chaos)
  - Knowledge sharing and runbooks
- Follow-up: Show me a sample postmortem document.

**Q86: Implement a chaos engineering strategy.**
- Expected:
  - Chaos Monkey (random instance termination)
  - Network latency injection (10-100ms)
  - Database connection pool exhaustion
  - Kafka broker failure
  - Regional failure simulation
  - Gradual rollout (dev → staging → prod)
  - Game days for practice
- Follow-up: How do you measure resilience improvement?

---

## Behavioral & Scenario-Based

### Mid Level

**Q87: Your matching engine has a bug that caused incorrect trade prices. How do you handle it?**
- Expected:
  - Immediately halt trading (circuit breaker)
  - Assess impact (how many trades affected)
  - Communicate with affected parties
  - Roll back incorrect trades
  - Root cause analysis
  - Implement fix and test thoroughly
  - Gradual rollout
  - Postmortem and prevention measures
- Follow-up: Who makes the decision to halt trading?

**Q88: You need to deploy a critical fix during market hours. Walk me through your process.**
- Expected:
  - Risk assessment (can it wait until market close?)
  - Blue-green or canary deployment
  - Deploy to 1% of traffic first
  - Monitor metrics closely
  - Gradual rollout (5%, 25%, 50%, 100%)
  - Rollback plan ready
  - Communication to stakeholders
- Follow-up: What if the fix makes things worse?

**Q89: Your database is at 90% capacity. What's your immediate action plan?**
- Expected:
  - Immediate: Scale up vertically (more storage)
  - Short-term: Archive old data, optimize queries
  - Medium-term: Implement data lifecycle policies
  - Long-term: Horizontal partitioning/sharding
  - Monitor growth rate
  - Capacity planning (quarterly reviews)
- Follow-up: How do you prevent this in the future?

### Senior Level

**Q90: The matching engine is down. Market is open. You have 5 minutes to decide. What do you do?**
- Expected:
  - Failover to hot standby (< 5 seconds)
  - If failover fails, halt trading immediately
  - Communicate to market participants
  - Root cause diagnosis in parallel
  - Bring up cold backup if needed
  - Resume trading only after verification
  - Incident report to regulators
- Follow-up: How do you ensure orders aren't lost during failover?

**Q91: A nation-state actor is attempting to breach your system. What's your incident response?**
- Expected:
  - Activate Security Incident Response Team
  - Isolate affected systems (network segmentation)
  - Preserve evidence (logs, memory dumps)
  - Contact law enforcement (FBI Cyber Division)
  - Notify regulators (SEC)
  - Threat intelligence analysis
  - Strengthen defenses
  - Legal counsel involvement
- Follow-up: When do you disclose to customers?

**Q92: Your cloud provider (AWS) has a major outage in us-east-1. Walk me through your actions.**
- Expected:
  - 0 min: Automated health checks detect failure
  - 2 min: Failover to eu-west-1 (hot standby) initiated
  - 5 min: Verify services operational in eu-west-1
  - 10 min: Communication to users (status page)
  - Continuous: Monitor AWS status page
  - Post-recovery: Failback process
  - Postmortem: Multi-cloud strategy evaluation
- Follow-up: What's the acceptable data loss (RPO)?

**Q93: You're asked to cut infrastructure costs by 50% without impacting performance. How?**
- Expected:
  - Challenge: Impossible without trade-offs, push back
  - Option 1: Reduce high availability (3 AZ → 2 AZ)
  - Option 2: Spot instances for non-critical workloads
  - Option 3: Reserved instances (3-year commitment)
  - Option 4: Auto-scaling more aggressive
  - Option 5: Cheaper instance types where possible
  - Realistic: 30% reduction achievable, not 50%
- Follow-up: What would you recommend and why?

**Q94: Your team is burning out with 24/7 on-call. How do you fix this?**
- Expected:
  - Reduce alert fatigue (tune thresholds)
  - Automate remediation (self-healing)
  - Runbook improvements
  - Follow-the-sun support (global team)
  - Proper staffing (hire more SREs)
  - Improve system reliability (fewer incidents)
  - On-call compensation
- Follow-up: What's an acceptable on-call load?

**Q95: Explain a time when you made a wrong architectural decision and how you fixed it.**
- Expected:
  - Situation: Chose MongoDB for order storage
  - Problem: Write throughput insufficient, consistency issues
  - Analysis: Should have used Cassandra
  - Solution: Gradual migration over 6 months
  - Learning: Validate assumptions with POC
  - Outcome: 10x write improvement
- Follow-up: How did you convince stakeholders to support the migration?

---

## Answer Key - Expected Proficiency Levels

### Question Difficulty Distribution
- **Junior (1-3 years)**: Q1-Q5, Q16-Q18, Q26-Q28, Q37-Q39, Q47-Q49, Q57-Q59, Q67-Q69, Q77-Q79
- **Mid (3-6 years)**: Q6-Q10, Q19-Q22, Q29-Q33, Q40-Q43, Q50-Q53, Q60-Q63, Q70-Q73, Q80-Q83, Q87-Q89
- **Senior (6+ years)**: Q11-Q15, Q23-Q25, Q34-Q36, Q44-Q46, Q54-Q56, Q64-Q66, Q74-Q76, Q84-Q86, Q90-Q95

### Key Topics Coverage
- System Design: 15 questions
- Matching Engine: 10 questions
- Microservices: 11 questions
- Databases: 10 questions
- Cloud/AWS: 10 questions
- Performance: 10 questions
- Security: 10 questions
- Operations: 10 questions
- Behavioral: 9 questions

---

**Total Questions**: 95
**Estimated Interview Time**: 
- Junior: 45-60 minutes (10-15 questions)
- Mid: 60-90 minutes (15-20 questions)
- Senior: 90-120 minutes (20-25 questions)

**Note**: These questions are based on the stock exchange system design documentation and reflect real-world scenarios encountered in building high-frequency trading systems. Adjust difficulty based on candidate's experience and role requirements.
