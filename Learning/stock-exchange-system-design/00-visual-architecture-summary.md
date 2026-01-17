# Stock Exchange System - Visual Architecture Summary

## Complete System Overview

```mermaid
graph TB
    subgraph "Trading Clients"
        WebApp[Web Trading App<br/>React + TypeScript]
        MobileApp[Mobile App<br/>iOS/Android]
        Institution[Institutional Clients<br/>FIX Protocol]
        API[Third-party APIs<br/>REST/WebSocket]
    end

    subgraph "AWS Global Infrastructure"
        Route53[Route 53<br/>GeoDNS]
        CloudFront[CloudFront CDN<br/>DDoS Protection]
        WAF[AWS WAF]
    end

    subgraph "Application Layer - Spring Boot Microservices on EKS"
        direction LR
        Gateway[API Gateway<br/>Spring Cloud Gateway<br/>Rate Limiting]
        
        subgraph "Trading Domain"
            OrderSvc[Order Service<br/>@SpringBootApplication<br/>Kafka Producer]
            TradeSvc[Trade Service<br/>@SpringBootApplication<br/>Settlement]
            MatchEngine[Matching Engine<br/>C++ FPGA<br/>< 500μs latency]
        end
        
        subgraph "Risk Domain"
            RiskSvc[Risk Service<br/>@SpringBootApplication<br/>Pre-trade Checks]
            PositionSvc[Position Service<br/>Real-time P&L]
        end
        
        subgraph "Market Data"
            MDSvc[Market Data Service<br/>Spring WebFlux<br/>Reactive Streams]
        end
        
        subgraph "Support"
            AccountSvc[Account Service<br/>KYC/Onboarding]
            ComplianceSvc[Compliance<br/>Trade Surveillance]
            SettlementSvc[Settlement<br/>T+2 Cycle]
        end
    end

    subgraph "Event Streaming - Amazon MSK"
        Kafka[Apache Kafka<br/>9 Brokers<br/>100+ Partitions<br/>TLS + IAM Auth]
    end

    subgraph "Data Layer - Polyglot Persistence"
        PostgreSQL[(RDS PostgreSQL<br/>Multi-AZ<br/>Trade Data<br/>ACID)]
        Cassandra[(Cassandra<br/>Order Data<br/>High Write)]
        Redis[(ElastiCache Redis<br/>Cluster Mode<br/>Cache & Session)]
        TimescaleDB[(TimescaleDB<br/>Market Data<br/>Time-Series)]
        S3[(S3<br/>Audit Logs<br/>Compliance)]
    end

    subgraph "Observability - Full Stack Monitoring"
        Prometheus[Prometheus<br/>Metrics]
        Grafana[Grafana<br/>Dashboards]
        Jaeger[Jaeger<br/>Tracing]
        ELK[ELK Stack<br/>Logs]
        CloudWatch[CloudWatch<br/>AWS Metrics]
    end

    WebApp --> Route53
    MobileApp --> Route53
    Institution --> Route53
    API --> Route53

    Route53 --> CloudFront
    CloudFront --> WAF
    WAF --> Gateway

    Gateway --> OrderSvc
    Gateway --> AccountSvc
    Gateway --> MDSvc

    OrderSvc --> Kafka
    OrderSvc --> RiskSvc
    OrderSvc --> Cassandra
    OrderSvc --> Redis

    RiskSvc --> Redis
    RiskSvc --> PositionSvc

    Kafka --> MatchEngine
    MatchEngine --> Kafka

    Kafka --> TradeSvc
    TradeSvc --> PostgreSQL
    TradeSvc --> SettlementSvc

    MDSvc --> TimescaleDB
    MDSvc --> Redis

    ComplianceSvc --> S3
    ComplianceSvc --> PostgreSQL

    OrderSvc -.->|Metrics| Prometheus
    TradeSvc -.->|Metrics| Prometheus
    RiskSvc -.->|Metrics| Prometheus
    Prometheus --> Grafana

    OrderSvc -.->|Traces| Jaeger
    TradeSvc -.->|Traces| Jaeger

    OrderSvc -.->|Logs| ELK
    TradeSvc -.->|Logs| ELK

    Gateway -.->|Metrics| CloudWatch
    PostgreSQL -.->|Metrics| CloudWatch
    Kafka -.->|Metrics| CloudWatch

    style WebApp fill:#e1f5ff
    style OrderSvc fill:#90EE90
    style TradeSvc fill:#90EE90
    style RiskSvc fill:#90EE90
    style MatchEngine fill:#FFD700
    style Kafka fill:#231F20,color:#fff
    style PostgreSQL fill:#336791,color:#fff
    style Redis fill:#DC382D,color:#fff
```

## Spring Boot Order Service Architecture

```mermaid
graph TB
    subgraph "Order Service Pod - Spring Boot 3.2"
        Controller[OrderController<br/>@RestController<br/>REST Endpoints]
        Service[OrderService<br/>@Service<br/>Business Logic]
        
        subgraph "Data Access Layer"
            JPARepo[OrderRepository<br/>Spring Data JPA]
            CassandraRepo[OrderCassandraRepository<br/>Spring Data Cassandra]
            RedisRepo[OrderCacheRepository<br/>Spring Data Redis]
        end
        
        subgraph "Integration Layer"
            KafkaProducer[OrderKafkaProducer<br/>@KafkaTemplate]
            FeignClient[RiskServiceClient<br/>@FeignClient<br/>Circuit Breaker]
        end
        
        subgraph "Cross-Cutting Concerns"
            Security[Spring Security<br/>JWT Validation]
            Resilience[Resilience4j<br/>Circuit Breaker<br/>Retry<br/>Rate Limiter]
            Actuator[Spring Boot Actuator<br/>Health<br/>Metrics<br/>Prometheus]
            Tracing[Spring Cloud Sleuth<br/>Distributed Tracing]
        end
    end

    Controller --> Service
    Service --> JPARepo
    Service --> CassandraRepo
    Service --> RedisRepo
    Service --> KafkaProducer
    Service --> FeignClient

    Controller --> Security
    Service --> Resilience
    Service --> Actuator
    Service --> Tracing

    JPARepo --> PostgreSQL[(PostgreSQL)]
    CassandraRepo --> Cassandra[(Cassandra)]
    RedisRepo --> Redis[(Redis)]
    KafkaProducer --> Kafka[Kafka Topic]
    FeignClient --> RiskService[Risk Service]

    style Controller fill:#90EE90
    style Service fill:#87CEEB
    style Resilience fill:#FFD700
```

## AWS EKS Deployment Architecture

```mermaid
graph TB
    subgraph "AWS Region - us-east-1"
        subgraph "Availability Zone 1a"
            ALB1[ALB<br/>Target Groups]
            EKS1[EKS Nodes<br/>c6i.4xlarge]
            RDS1[RDS Primary<br/>db.r6i.4xlarge]
            Redis1[Redis Primary]
        end

        subgraph "Availability Zone 1b"
            ALB2[ALB Standby]
            EKS2[EKS Nodes<br/>c6i.4xlarge]
            RDS2[RDS Standby<br/>Sync Replica]
            Redis2[Redis Replica]
        end

        subgraph "Availability Zone 1c"
            EKS3[EKS Nodes<br/>c6i.4xlarge]
            MSK[MSK Kafka<br/>3 Brokers]
        end

        subgraph "EKS Control Plane - Managed"
            APIServer[Kubernetes API]
            Scheduler[Scheduler]
            etcd[etcd]
        end
    end

    ALB1 --> EKS1
    ALB1 --> EKS2
    ALB1 --> EKS3
    ALB2 --> EKS1
    ALB2 --> EKS2
    ALB2 --> EKS3

    EKS1 --> RDS1
    EKS2 --> RDS1
    EKS3 --> RDS1

    EKS1 --> Redis1
    EKS2 --> Redis2
    EKS3 --> Redis1

    EKS1 --> MSK
    EKS2 --> MSK
    EKS3 --> MSK

    RDS1 -.->|Sync Replication| RDS2
    Redis1 -.->|Async Replication| Redis2

    APIServer --> Scheduler
    APIServer --> etcd
    Scheduler --> EKS1
    Scheduler --> EKS2
    Scheduler --> EKS3

    style ALB1 fill:#FF9900
    style RDS1 fill:#527FFF
    style MSK fill:#231F20,color:#fff
    style Redis1 fill:#DC382D,color:#fff
```

## Data Flow - Order to Trade Execution

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant ALB as Application<br/>Load Balancer
    participant Gateway as Spring Cloud<br/>Gateway
    participant Order as Order Service<br/>(Spring Boot)
    participant Risk as Risk Service<br/>(Spring Boot)
    participant Kafka
    participant Match as Matching<br/>Engine
    participant Trade as Trade Service<br/>(Spring Boot)
    participant DB as PostgreSQL

    Client->>ALB: POST /api/v1/orders
    ALB->>Gateway: Forward Request
    Gateway->>Gateway: JWT Validation<br/>Rate Limiting
    Gateway->>Order: Route to Pod
    
    Note over Order: Validation & Idempotency
    Order->>Order: Generate Order ID<br/>Validate Format
    Order->>Risk: Pre-Trade Risk Check<br/>@CircuitBreaker
    Risk-->>Order: Approved ✓
    
    Note over Order: Persist Order
    Order->>DB: Save Order (Cassandra)
    Order->>Kafka: Publish order-validated
    Order-->>Client: 202 Accepted<br/>{orderId, status}
    
    Note over Kafka,Match: Async Processing
    Kafka->>Match: Consume Order Event
    Match->>Match: Match Against Book
    Match->>Kafka: Publish trade-executed
    
    Kafka->>Trade: Consume Trade Event
    Trade->>DB: Save Trade Record
    Trade->>Kafka: Publish trade-confirmed
    
    Kafka->>Order: Update Order Status
    Order->>DB: Update Order FILLED
```

## Technology Stack Visualization

```mermaid
mindmap
  root((Stock Exchange<br/>Platform))
    Backend
      Spring Boot 3.2
        Spring Data JPA
        Spring Data Cassandra
        Spring Data Redis
        Spring Kafka
        Spring Security
        Spring WebFlux
      Java 21
        Virtual Threads
        Records
        Pattern Matching
      Resilience4j
        Circuit Breaker
        Retry
        Rate Limiter
    Cloud Infrastructure
      AWS EKS
        Kubernetes 1.28
        Node Groups
        Auto Scaling
        IRSA
      Compute
        EC2 c6i/m6i
        Fargate
      Networking
        VPC
        ALB/NLB
        Route 53
        CloudFront
    Databases
      PostgreSQL 15
        RDS Multi-AZ
        Read Replicas
      Cassandra 4.x
        Multi-DC
        Tunable Consistency
      Redis 7
        Cluster Mode
        Pub/Sub
      TimescaleDB
        Hypertables
        Continuous Aggregates
    Messaging
      Apache Kafka 3.5
        MSK Managed
        100 Partitions
        TLS + IAM
      Event Sourcing
      CQRS
    Observability
      Prometheus
        Micrometer
        Spring Actuator
      Grafana
        Dashboards
        Alerts
      Jaeger
        Distributed Tracing
        OpenTelemetry
      ELK Stack
        Elasticsearch
        Logstash
        Kibana
    Security
      OAuth2 + JWT
      Spring Security
      AWS IAM
      KMS Encryption
      Secrets Manager
    IaC
      Terraform
        AWS Provider
        Modules
      Helm Charts
      Kustomize
```

## Deployment Pipeline

```mermaid
graph LR
    subgraph "Source"
        GitHub[GitHub<br/>Repository]
    end

    subgraph "Build"
        Maven[Maven Build<br/>spring-boot:build-image]
        Test[Unit & Integration<br/>Tests]
        Scan[Security Scan<br/>Trivy/Snyk]
    end

    subgraph "Artifact"
        ECR[Amazon ECR<br/>Container Registry]
    end

    subgraph "Deploy"
        Terraform[Terraform Apply<br/>Infrastructure]
        Helm[Helm Deploy<br/>Kubernetes]
        Smoke[Smoke Tests<br/>Health Checks]
    end

    subgraph "Monitor"
        Prometheus[Prometheus<br/>Metrics]
        CloudWatch[CloudWatch<br/>Alarms]
    end

    GitHub -->|Webhook| Maven
    Maven --> Test
    Test --> Scan
    Scan -->|Push Image| ECR
    
    ECR --> Terraform
    Terraform --> Helm
    Helm --> Smoke
    
    Smoke -->|Success| Prometheus
    Smoke -->|Success| CloudWatch

    style GitHub fill:#181717,color:#fff
    style Maven fill:#C71A36,color:#fff
    style ECR fill:#FF9900
    style Helm fill:#0F1689,color:#fff
```

## Performance Characteristics

| Component | Latency Target | Throughput Target | Availability |
|-----------|---------------|-------------------|--------------|
| Order Acknowledgment | < 1ms (p99) | 10M orders/sec | 99.999% |
| Matching Engine | < 500μs | 1M matches/sec | 99.999% |
| Market Data Pub | < 100μs | 100M msg/sec | 99.99% |
| Risk Check | < 500μs | 10M checks/sec | 99.99% |
| REST API | < 50ms (p95) | 1M req/sec | 99.9% |
| Database Write | < 10ms (p99) | 100K writes/sec | 99.99% |

## Cost Optimization (Monthly)

```mermaid
pie title AWS Monthly Cost Breakdown (Production)
    "EKS Compute (EC2)" : 35000
    "RDS PostgreSQL" : 12000
    "ElastiCache Redis" : 8000
    "MSK Kafka" : 15000
    "Data Transfer" : 10000
    "Storage (S3/EBS)" : 5000
    "Load Balancers" : 3000
    "Other Services" : 7000
```

**Total Monthly Cost**: ~$95,000 USD
- **Daily**: ~$3,167
- **Annual**: ~$1.14M

**Cost Optimization Strategies**:
- Use Savings Plans (40% discount on compute)
- Reserved Instances for steady-state workloads
- Spot Instances for batch processing (90% discount)
- S3 Intelligent-Tiering for logs
- Right-size instances based on metrics
- Delete unused snapshots and AMIs

---

**Document Version**: 1.0  
**Last Updated**: January 17, 2026  
**Purpose**: Visual summary of complete stock exchange architecture
