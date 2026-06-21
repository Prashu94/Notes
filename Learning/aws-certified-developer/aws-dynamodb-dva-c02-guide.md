# Amazon DynamoDB — DVA-C02 Developer Guide

Focus on **key design, SDK operations, consistency, indexes, and application patterns** — the developer perspective, not infrastructure provisioning.

**Official docs:** [DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)

---

## Core Concepts for Developers

### Table Structure

```
Table
├── Primary Key (required)
│   ├── Partition Key (PK) — hash key
│   └── Sort Key (SK) — optional range key
├── Attributes — name/value pairs (schemaless)
├── GSIs — alternate query patterns (up to 20)
└── LSIs — same PK, different SK (up to 5, must define at creation)
```

### Capacity Modes

| Mode | Billing | Use when |
|------|---------|----------|
| **On-demand** | Per request | Unpredictable traffic, new apps |
| **Provisioned** | Per RCU/WCU per hour | Predictable, cost-optimize at scale |
| **Auto Scaling** | Provisioned + scaling policy | Predictable with variation |

**Exam default for variable serverless apps:** On-demand.

---

## SDK Operations

### Read Operations

```python
table = dynamodb.Table('Orders')

# GetItem — single item by exact key
item = table.get_item(Key={'PK': 'user123', 'SK': 'ORDER#001'})

# Query — items with same PK, optional SK condition
response = table.query(
    KeyConditionExpression=Key('PK').eq('user123') & Key('SK').begins_with('ORDER#')
)

# Scan — AVOID in production (reads entire table)
response = table.scan(FilterExpression=Attr('status').eq('pending'))
```

### Write Operations

```python
# PutItem — create or replace entire item
table.put_item(Item={'PK': 'user123', 'SK': 'PROFILE', 'name': 'Alice'})

# UpdateItem — update specific attributes
table.update_item(
    Key={'PK': 'user123', 'SK': 'PROFILE'},
    UpdateExpression='SET #n = :name',
    ExpressionAttributeNames={'#n': 'name'},
    ExpressionAttributeValues={':name': 'Bob'}
)

# DeleteItem
table.delete_item(Key={'PK': 'user123', 'SK': 'PROFILE'})

# Conditional write — optimistic locking
table.put_item(
    Item={...},
    ConditionExpression='attribute_not_exists(PK)'  # Only if not exists
)
```

### Batch and Transaction

```python
# BatchGetItem — up to 100 items, 16 MB
response = dynamodb.batch_get_item(
    RequestItems={'Orders': {'Keys': [{'PK': 'u1', 'SK': 'O1'}, {'PK': 'u1', 'SK': 'O2'}]}}
)

# TransactWriteItems — all-or-nothing, up to 25 items
dynamodb.transact_write_items(TransactItems=[
    {'Put': {'TableName': 'Orders', 'Item': {...}}},
    {'Update': {'TableName': 'Inventory', 'Key': {...}, 'UpdateExpression': 'SET qty = qty - :1', ...}}
])
```

---

## Consistency Models

| Read type | Consistency | RCU cost | Use when |
|-----------|-------------|----------|----------|
| Default read | Eventually consistent | 1 RCU (4 KB) | Most reads |
| `ConsistentRead=True` | Strongly consistent | 2 RCU (4 KB) | Must read latest write |
| GSI read | Eventually consistent only | Separate capacity | Alternate access pattern |
| Transaction read | Strongly consistent | 2x RCU | Within transaction |

> **Exam trap:** GSI does NOT support strongly consistent reads — only eventually consistent.

---

## Index Design

### When to Use GSI vs LSI

| | GSI | LSI |
|--|-----|-----|
| **When to create** | Anytime | Only at table creation |
| **PK** | Different from table | Same as table |
| **SK** | Optional | Required (different from table SK) |
| **Capacity** | Separate RCU/WCU | Shares table capacity |
| **Consistency** | Eventually only | Strongly consistent option |
| **Max count** | 20 | 5 |

### GSI Example — Query by Email

```
Table PK: userId          GSI "EmailIndex" PK: email
Table SK: metadata        GSI SK: userId

Query email index:
table.query(
    IndexName='EmailIndex',
    KeyConditionExpression=Key('email').eq('alice@example.com')
)
```

---

## DynamoDB Streams (Developer Use)

```python
# Stream record in Lambda event
for record in event['Records']:
    event_name = record['eventName']  # INSERT, MODIFY, REMOVE
    new_image = record['dynamodb'].get('NewImage')
    old_image = record['dynamodb'].get('OldImage')
```

**Stream view types:**
- `KEYS_ONLY` — only key attributes
- `NEW_IMAGE` — item after change
- `OLD_IMAGE` — item before change
- `NEW_AND_OLD_IMAGES` — both (most flexible, highest cost)

---

## TTL (Time to Live)

```python
table.put_item(Item={
    'sessionId': 'abc',
    'data': {...},
    'ttl': int(time.time()) + 86400  # Unix epoch — auto-delete within 48 hrs
})
```

Enable TTL on the `ttl` attribute in table settings. Free — no WCU consumed for deletes.

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `ProvisionedThroughputExceededException` | Throttled | On-demand mode or increase capacity |
| `ConditionalCheckFailedException` | Condition not met | Expected for optimistic locking |
| `ValidationException` | Bad key/query | Check key schema and expressions |
| `ItemCollectionSizeLimitExceededException` | > 10 GB per PK+SK | Redesign partition key |

**Retry throttling with exponential backoff** — boto3 adaptive retry mode handles this automatically.

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Query users by email (PK is userId) | Create GSI with email as PK |
| Prevent duplicate item creation | `ConditionExpression: attribute_not_exists(PK)` |
| Read latest write after update | `ConsistentRead=True` on primary table |
| Auto-delete expired sessions | TTL attribute |
| Atomic transfer between accounts | `transact_write_items` |
| Hot partition on popular item | Write sharding or redesign partition key |
| Cache reads for microsecond latency | DAX |
| React to table changes | DynamoDB Streams → Lambda |

---

## Related Guides

- [Concepts Deep Dive — DynamoDB](CONCEPTS-DEEP-DIVE.md#dynamodb-for-application-developers)
- [Domain 1](domain-01-development-with-aws-services.md)
