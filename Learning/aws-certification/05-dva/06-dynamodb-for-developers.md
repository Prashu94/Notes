# DynamoDB for developers

DVA skills 1.3.1 through 1.3.8. Schema design as a profession is out of scope. Reading a key and predicting a query is in scope.

Official: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html

## Keys

Partition key: high cardinality. `USER#123` is fine. `STATUS#OPEN` is a hot key. Sort key: the range inside that partition. `ORDER#2026-10-11T...` lets you query a user's orders by time.

GSI: another access pattern, its own capacity, eventually consistent. LSI: same partition key, different sort, created with the table. Sparse index: only items that have the attribute appear. That is how "all open orders" stays small if most items omit the attribute.

## Calls

| Call | When |
| --- | --- |
| GetItem | One key. `ConsistentRead=True` after a write you must see |
| Query | Key condition on one partition. `Limit` is page size, not a SQL limit of matches after a filter |
| Scan | Almost never in the request path |
| PutItem with a condition | Create once |
| UpdateItem | Change attributes without replacing the item |
| TransactWriteItems | Up to 100 items, one Region, all or nothing |
| BatchWriteItem | Bulk. Unprocessed keys must be retried. Not a transaction |

A `FilterExpression` runs after the read. You pay for the read. It does not fix a bad key.

```python
table.query(
    KeyConditionExpression="pk = :u AND begins_with(sk, :p)",
    ExpressionAttributeValues={":u": "USER#123", ":p": "ORDER#"},
)
table.update_item(
    Key={"pk": "USER#123", "sk": "ORDER#1"},
    UpdateExpression="SET #s = :s",
    ConditionExpression="#s = :expected",
    ExpressionAttributeNames={"#s": "status"},
    ExpressionAttributeValues={":s": "PAID", ":expected": "NEW"},
)
```

## Capacity

On-demand for unknown traffic. Provisioned plus auto scaling for a flat load. A throttle on one key with spare table capacity is a hot partition, not a reason to double the table. TTL removes expired items eventually. It is not a second-accurate delete and it is not a backup. PITR is the backup.

Streams plus Lambda is the "when this row changes" trigger. It is not a queue you poll.

## Multi-tenant

`pk` starts with the tenant id taken from the token. IAM condition `dynamodb:LeadingKeys` if the caller has AWS credentials. If only your service role talks to the table, the code must enforce the prefix. The role can read everything. The code is the control.

## Exercise

The query uses `pk = OPEN` and a filter on `userId`. Users say their own orders are slow and the table throttles. What is wrong with the key, and what is the query after you fix it?

Answer: `OPEN` is one partition for every user. Put the user id in the partition key and the order id or time in the sort key. Query that partition. The filter goes away because the key already scopes the user.

## Keys, indexes, and the calls

`GetItem` is one item and the cheapest read when you have both keys. `Query` is one partition and a sort-key condition. `Scan` reads and then filters. A filter expression never reduces RCUs. `begins_with` belongs on the sort key.

A GSI is another key you pay for on every write that includes its attributes. Sparse indexes omit items that lack the attribute. An LSI shares the table's partition key and must be created with the table. Transactions are atomic across items, up to 100 actions, and cost more than a plain write. `BatchWriteItem` is 25 independent writes, not a transaction.

Items max out at 400 KB. The large blob goes to S3. TTL deletes expired items eventually and is not a precise compliance delete. PITR is off until you enable it. Streams are the change log Lambda consumes. Global tables replicate asynchronously. A consistent read does not cross Regions.

`dynamodb:LeadingKeys` scopes a caller who holds AWS credentials to a tenant prefix. If only your service role talks to the table, the code must enforce the prefix. The role can read everything.

## More exercises

2. `BatchWriteItem` of a payment and an order. One item fails. What state can you be in, and which API avoids it?
3. A GSI on `status` with partition value `OPEN`. Writes to open orders throttle. The base table looks fine. Why?
4. The condition is `attribute_not_exists(pk)`. The second request throws `ConditionalCheckFailedException`. What does a correct consumer do?
5. You need "all orders for a user in the last day" and "the single order by id." Which key is which?

## Answers

2. The payment can exist without the order, or the reverse. `BatchWriteItem` is not atomic. `TransactWriteItems` commits both or neither.
3. The index partition for `OPEN` is one hot key. Every open-order write hits it. Fix the index key or stop indexing a low-cardinality status as a partition key. Raising the table's on-demand mode does not split that partition.
4. Treat it as success if the item existing means the order was already written. Delete the queue message. Do not retry forever. Do not create a second row.
5. Partition key user id, sort key a time or an order id, for the range query. A GSI or the same table with the order id as the key for the single-order lookup. One table can serve both if the key design says so. A scan with a filter serves neither cheaply.
