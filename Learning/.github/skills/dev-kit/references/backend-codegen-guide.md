# Backend Codegen Guide

## Code Quality Standards

Every generated backend file must meet these standards:

### Layered Architecture Contract

```
Controller (HTTP in) → Service (business logic) → Repository (data access) → Entity (DB model)
```

- **Controller**: ONLY HTTP concerns — validate input, call service, return response
- **Service**: ALL business logic and business rules — no HTTP types here
- **Repository**: ONLY database queries — no business logic
- **Entity**: ONLY JPA/ORM annotations and field definitions — no logic

### Business Rule Implementation

Each story references business rules (BR-NNN). Implement them in the **service layer**:

```java
// BR-002: Order quantity must not exceed available stock
public Order createOrder(CreateOrderRequest request) {
    int available = inventoryClient.getAvailableStock(request.getProductId());
    if (request.getQuantity() > available) {
        throw new InsufficientStockException(
            "Requested quantity %d exceeds available stock %d"
                .formatted(request.getQuantity(), available)
        );
    }
    // ... rest of logic
}
```

### Error Response Standard

All APIs must return consistent error responses:
```json
{
  "timestamp": "2026-04-25T10:00:00Z",
  "status": 400,
  "error": "Bad Request",
  "code": "INSUFFICIENT_STOCK",
  "message": "Requested quantity 10 exceeds available stock 5",
  "path": "/api/v1/orders",
  "traceId": "abc123"
}
```

### HTTP Status Code Guide

| Situation | Status |
|-----------|--------|
| Created successfully | 201 |
| Found | 200 |
| Not found | 404 |
| Validation error | 400 |
| Business rule violation | 422 |
| Auth required | 401 |
| Permission denied | 403 |
| Conflict (duplicate) | 409 |
| Server error | 500 |

### Pagination Standard

All list endpoints use `page` (0-based) and `size` parameters.
Return: `{ content: [], totalElements: N, totalPages: N, page: N, size: N }`

### Audit Fields

Every entity that represents business data must have:
```java
@Column(nullable = false, updatable = false)
private Instant createdAt;

@Column(nullable = false)
private Instant updatedAt;

private UUID createdBy;
```

### Security: Input Validation

Every controller endpoint accepting request body must validate:
- String lengths (use `@Size`, `@NotBlank`)
- Number ranges (use `@Min`, `@Max`)
- Required fields (use `@NotNull`)
- Email format (use `@Email`)
- Never trust user input for IDs that bypass ownership checks

### Environment Variable Pattern

```yaml
# application-local.yml — safe to commit
spring:
  datasource:
    url: ${DATABASE_URL:jdbc:postgresql://localhost:5432/mydb}
    username: ${DATABASE_USERNAME:postgres}
    password: ${DATABASE_PASSWORD:postgres}
```

```bash
# .env.example — safe to commit
DATABASE_URL=jdbc:postgresql://localhost:5432/mydb
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
# Cloud values (replace before deploying to cloud):
AWS_S3_BUCKET=  # TODO: set to actual S3 bucket
```

## Service-to-Service Communication

### Synchronous (REST client)
```java
// Use @FeignClient or RestTemplate/WebClient
// Always set timeouts
// Always handle 4xx/5xx responses
@FeignClient(name = "inventory-service", url = "${services.inventory-service.url}")
public interface InventoryClient {
    @GetMapping("/api/v1/stock/{productId}")
    StockResponse getStock(@PathVariable UUID productId);
}
```

### Asynchronous (Events)
```java
// Produce events AFTER successful DB commit (use @TransactionalEventListener)
// Always include correlationId / traceId in event payload
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void on(OrderCreatedEvent event) {
    kafkaTemplate.send("orders.created", event);
}
```
