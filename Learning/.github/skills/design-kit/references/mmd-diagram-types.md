# Mermaid Diagram Types Reference

All diagrams are written in Mermaid syntax and saved as `.mmd` files.

## Supported Diagram Types

### 1. Sequence Diagram
```mermaid
sequenceDiagram
  autonumber
  actor User
  participant API as Order API
  participant DB as PostgreSQL
  participant MQ as Kafka

  User->>API: POST /orders
  API->>DB: INSERT order
  DB-->>API: order_id
  API->>MQ: publish OrderCreated
  API-->>User: 201 { order_id }
```
**Use for**: workflows, API interactions, event flows.

### 2. C4 Context Diagram
```mermaid
C4Context
  title System Context
  Person(user, "Customer", "Places orders")
  System(app, "Order System", "Manages orders")
  System_Ext(payment, "Payment Gateway", "Processes payments")
  Rel(user, app, "Places order")
  Rel(app, payment, "Charges card", "HTTPS")
```
**Use for**: system overview, stakeholder view.

### 3. C4 Component Diagram
```mermaid
C4Component
  title Components
  Container(api, "Order API", "Spring Boot", "REST API")
  Container(worker, "Order Worker", "Spring Batch", "Async jobs")
  ContainerDb(db, "Orders DB", "PostgreSQL", "Relational data")
  ContainerQueue(queue, "Event Bus", "Kafka", "Async events")
  Rel(api, db, "R/W")
  Rel(api, queue, "Publishes")
  Rel(worker, queue, "Consumes")
```
**Use for**: service architecture.

### 4. Entity Relationship Diagram
```mermaid
erDiagram
  CUSTOMER {
    uuid id PK
    string email UK
    string name
  }
  ORDER {
    uuid id PK
    uuid customer_id FK
    string status
    decimal total
  }
  CUSTOMER ||--o{ ORDER : "places"
  ORDER ||--|{ ORDER_ITEM : "contains"
```
**Use for**: data model, database design.

### 5. Flowchart (Business Logic)
```mermaid
flowchart TD
  A([Start]) --> B{Order Valid?}
  B -- Yes --> C[Reserve Stock]
  B -- No --> D[Return Error]
  C --> E{Payment OK?}
  E -- Yes --> F[Confirm Order]
  E -- No --> G[Release Stock]
  F --> H([End: Success])
  G --> D
```
**Use for**: business rule flows, decision trees.

### 6. State Diagram
```mermaid
stateDiagram-v2
  [*] --> Pending
  Pending --> Confirmed: payment_success
  Pending --> Cancelled: cancel | timeout
  Confirmed --> Shipped: ship
  Shipped --> Delivered: delivered
  Delivered --> [*]
  Cancelled --> [*]
```
**Use for**: entity lifecycle, order states, workflow states.

### 7. Deployment Diagram (Graph)
```mermaid
graph TB
  subgraph K8s["Kubernetes Cluster"]
    subgraph Ingress
      LB[NGINX Ingress]
    end
    subgraph Services
      SVC1[order-service:3 replicas]
      SVC2[inventory-service:2 replicas]
    end
    subgraph Storage
      DB[(PostgreSQL)]
      CACHE[(Redis)]
    end
  end
  USER([Browser]) --> LB
  LB --> SVC1
  SVC1 --> DB & CACHE
  SVC1 --> SVC2
```
**Use for**: infrastructure, deployment topology.

### 8. Class Diagram
```mermaid
classDiagram
  class Order {
    +UUID id
    +String status
    +Decimal total
    +confirm()
    +cancel()
  }
  class OrderItem {
    +UUID id
    +int quantity
    +Decimal price
  }
  Order "1" --> "*" OrderItem : contains
```
**Use for**: domain model, OOP relationships.

## Naming Convention
| Diagram | File Name |
|---------|----------|
| Architecture context | `architecture.mmd` |
| Components | `components.mmd` |
| Sequence for WF-NNN | `seq-wf-001.mmd` |
| ER diagram | `er-diagram.mmd` |
| Deployment | `deployment.mmd` |
| State machine | `state-<entity>.mmd` |
| Flowchart | `flow-<rule-or-process>.mmd` |
