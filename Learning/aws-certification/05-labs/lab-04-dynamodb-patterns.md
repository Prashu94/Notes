# Lab 04 — DynamoDB access patterns

SAA task 3.3 and DVA skills 1.3. On-demand capacity so a forgotten table does not bill provisioned RCUs all month. Still delete it.

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
```

## 1. Table and a sparse GSI

Partition key `pk`, sort key `sk`. The GSI keys are `gsi1pk` and `gsi1sk`. Items that omit those attributes do not appear in the index. That is a sparse index, and it is how you avoid projecting the whole table into a second bill.

```bash
aws dynamodb create-table \
  --table-name lab04-orders \
  --attribute-definitions \
    AttributeName=pk,AttributeType=S \
    AttributeName=sk,AttributeType=S \
    AttributeName=gsi1pk,AttributeType=S \
    AttributeName=gsi1sk,AttributeType=S \
  --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
  --global-secondary-indexes '[{
    "IndexName": "status-index",
    "KeySchema": [
      {"AttributeName": "gsi1pk", "KeyType": "HASH"},
      {"AttributeName": "gsi1sk", "KeyType": "RANGE"}
    ],
    "Projection": {"ProjectionType": "INCLUDE", "NonKeyAttributes": ["total"]}
  }]' \
  --billing-mode PAY_PER_REQUEST

aws dynamodb wait table-exists --table-name lab04-orders
```

## 2. Writes

```bash
aws dynamodb put-item --table-name lab04-orders --item '{
  "pk": {"S": "CUST#ada"},
  "sk": {"S": "ORDER#1001"},
  "gsi1pk": {"S": "STATUS#OPEN"},
  "gsi1sk": {"S": "2026-10-11#1001"},
  "total": {"N": "42"},
  "status": {"S": "OPEN"}
}'

aws dynamodb put-item --table-name lab04-orders --item '{
  "pk": {"S": "CUST#ada"},
  "sk": {"S": "ORDER#1002"},
  "total": {"N": "9"},
  "status": {"S": "PAID"}
}'

aws dynamodb put-item --table-name lab04-orders \
  --condition-expression "attribute_not_exists(pk)" \
  --item '{"pk":{"S":"CUST#ada"},"sk":{"S":"ORDER#1001"},"total":{"N":"42"}}'
```

The third call fails with `ConditionalCheckFailedException`. That is the idempotent put. A retried order does not create a second row. Your handler treats that exception as success when the business action already landed.

## 3. Query, then a scan that lies about cost

```bash
aws dynamodb query --table-name lab04-orders \
  --key-condition-expression "pk = :p AND begins_with(sk, :s)" \
  --expression-attribute-values '{":p":{"S":"CUST#ada"},":s":{"S":"ORDER#"}}' \
  --return-consumed-capacity TOTAL

aws dynamodb query --table-name lab04-orders --index-name status-index \
  --key-condition-expression "gsi1pk = :s" \
  --expression-attribute-values '{":s":{"S":"STATUS#OPEN"}}' \
  --return-consumed-capacity TOTAL

aws dynamodb scan --table-name lab04-orders \
  --filter-expression "status = :s" \
  --expression-attribute-values '{":s":{"S":"OPEN"}}' \
  --return-consumed-capacity TOTAL
```

The query reads Ada's orders. The GSI query reads open orders, and ORDER#1002 is absent because it has no GSI keys. The scan may return one item and still show consumed capacity for every item it read. The filter hid rows. It did not reduce the read. That sentence is the exam.

A `begins_with` on a partition key is illegal. `begins_with` belongs on the sort key. If you need "all customers in tenant 7", the partition key starts with the tenant id. It is not a filter after a scan.

## 4. A hot key, on paper

`STATUS#OPEN` is a convenient GSI key and a bad one at write volume, because every open order in the table lands on one partition of the index. Production writes shard that key (`STATUS#OPEN#0` through `#N`) or query by a key you already have, such as the customer id. The lab table has two items, so you will not see the throttle. You are supposed to recognize the shape.

## Cleanup

```bash
aws dynamodb delete-table --table-name lab04-orders
```
