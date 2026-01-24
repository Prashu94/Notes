# Chapter 4: Documents and BSON

## Table of Contents
- [Understanding BSON](#understanding-bson)
- [Document Structure](#document-structure)
- [BSON Data Types](#bson-data-types)
- [The _id Field and ObjectId](#the-_id-field-and-objectid)
- [Working with Documents](#working-with-documents)
- [Document Size Limits](#document-size-limits)
- [Best Practices](#best-practices)
- [Summary](#summary)

---

## Understanding BSON

### What is BSON?

BSON (Binary JSON) is a binary-encoded serialization format used by MongoDB to store documents and make remote procedure calls.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      JSON vs BSON                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  JSON (Text-based)                  BSON (Binary)                   │
│  ┌─────────────────────────┐       ┌─────────────────────────┐     │
│  │ {                       │       │ \x27\x00\x00\x00         │     │
│  │   "name": "John",       │  →    │ \x02name\x00\x05\x00... │     │
│  │   "age": 30             │       │ \x10age\x00\x1e\x00...  │     │
│  │ }                       │       │ \x00                     │     │
│  └─────────────────────────┘       └─────────────────────────┘     │
│                                                                     │
│  Characteristics:                   Characteristics:                │
│  • Human-readable                   • Machine-readable              │
│  • Text encoding (UTF-8)            • Binary encoding               │
│  • Limited data types               • Extended data types           │
│  • Slower to parse                  • Faster to parse               │
│  • Less storage efficient           • More storage efficient        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### BSON Advantages

| Feature | Benefit |
|---------|---------|
| **Binary Format** | Faster parsing and traversal |
| **Type Information** | Richer data type support |
| **Lightweight** | Efficient space utilization |
| **Traversable** | Can skip to specific fields |
| **Efficient Encoding** | Optimized for common operations |

### BSON vs JSON Comparison

```javascript
// JSON - Text-based
{
  "name": "Alice",
  "age": 25,
  "birthdate": "1998-06-15T00:00:00Z",  // String representation
  "balance": 1234.56                      // Number (no distinction)
}

// BSON - Type-aware (conceptual representation)
{
  "name": String("Alice"),
  "age": Int32(25),
  "birthdate": Date("1998-06-15T00:00:00Z"),  // Native Date type
  "balance": Double(1234.56)                   // Explicit double type
}
```

---

## Document Structure

### Basic Document Anatomy

```javascript
// A MongoDB document
{
  // System field - unique identifier (automatically created)
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  
  // String field
  "name": "Product Name",
  
  // Numeric fields
  "price": 99.99,
  "quantity": 100,
  
  // Boolean field
  "inStock": true,
  
  // Null field
  "discount": null,
  
  // Array field
  "tags": ["electronics", "gadgets", "sale"],
  
  // Embedded document (sub-document)
  "manufacturer": {
    "name": "TechCorp",
    "country": "USA",
    "contact": {
      "email": "info@techcorp.com",
      "phone": "+1-555-0100"
    }
  },
  
  // Array of embedded documents
  "reviews": [
    { "user": "user1", "rating": 5, "comment": "Excellent!" },
    { "user": "user2", "rating": 4, "comment": "Good product" }
  ],
  
  // Date field
  "createdAt": ISODate("2024-01-15T10:30:00Z"),
  
  // Binary data
  "thumbnail": BinData(0, "base64EncodedData...")
}
```

### Document Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Document Structure                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Document (Top Level)                                               │
│  │                                                                  │
│  ├── _id: ObjectId                                                 │
│  │                                                                  │
│  ├── field1: "string value"                                        │
│  │                                                                  │
│  ├── field2: 123 (number)                                          │
│  │                                                                  │
│  ├── field3: [ ... ] (array)                                       │
│  │   ├── element[0]                                                │
│  │   ├── element[1]                                                │
│  │   └── element[2]                                                │
│  │                                                                  │
│  └── field4: { ... } (embedded document)                           │
│      ├── subfield1: value                                          │
│      ├── subfield2: value                                          │
│      └── nested: { ... } (nested document)                         │
│          ├── deep1: value                                          │
│          └── deep2: value                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Field Names Rules

```javascript
// Valid field names
{
  "name": "value",              // Standard alphanumeric
  "user_name": "value",         // Underscore allowed
  "firstName": "value",         // camelCase (recommended)
  "field123": "value",          // Numbers allowed (not first char ideally)
  "my-field": "value",          // Hyphen allowed
  "field.sub": "value",         // Dot allowed (but avoid for queries)
  "$customOp": "value"          // $ prefix (for internal use)
}

// Field name restrictions:
// 1. Cannot contain null character (\0)
// 2. Top-level fields cannot start with $ (reserved for operators)
// 3. Top-level fields cannot contain . (dot) - used for nested access
// 4. _id is reserved for the primary key
// 5. Case-sensitive: "Name" and "name" are different fields
```

---

## BSON Data Types

### Complete BSON Type Reference

| Type | Number | Alias | Description |
|------|--------|-------|-------------|
| Double | 1 | "double" | 64-bit floating point |
| String | 2 | "string" | UTF-8 string |
| Object | 3 | "object" | Embedded document |
| Array | 4 | "array" | Array of values |
| Binary data | 5 | "binData" | Binary data |
| Undefined | 6 | "undefined" | Deprecated |
| ObjectId | 7 | "objectId" | 12-byte unique ID |
| Boolean | 8 | "bool" | true/false |
| Date | 9 | "date" | UTC datetime |
| Null | 10 | "null" | Null value |
| Regular Expression | 11 | "regex" | Regular expression |
| DBPointer | 12 | "dbPointer" | Deprecated |
| JavaScript | 13 | "javascript" | JavaScript code |
| Symbol | 14 | "symbol" | Deprecated |
| JavaScript with scope | 15 | "javascriptWithScope" | Deprecated |
| 32-bit integer | 16 | "int" | 32-bit integer |
| Timestamp | 17 | "timestamp" | Internal timestamp |
| 64-bit integer | 18 | "long" | 64-bit integer |
| Decimal128 | 19 | "decimal" | 128-bit decimal |
| Min key | -1 | "minKey" | Lowest BSON value |
| Max key | 127 | "maxKey" | Highest BSON value |

### Working with Data Types

```javascript
// String
db.types.insertOne({
  name: "Sample String",
  description: "UTF-8 encoded text with special chars: é, ü, 中文"
});

// Numbers
db.types.insertOne({
  // JavaScript numbers are doubles by default
  price: 99.99,                    // Double
  
  // Use NumberInt for 32-bit integer
  quantity: NumberInt(100),        // Int32
  
  // Use NumberLong for 64-bit integer
  viewCount: NumberLong("9999999999"),  // Int64
  
  // Use NumberDecimal for precise decimal
  balance: NumberDecimal("1234.56789")  // Decimal128
});

// Boolean
db.types.insertOne({
  isActive: true,
  isDeleted: false
});

// Date
db.types.insertOne({
  createdAt: new Date(),                    // Current UTC time
  specificDate: ISODate("2024-06-15"),      // Specific date
  timestamp: new Date("2024-06-15T10:30:00Z")
});

// Array
db.types.insertOne({
  tags: ["mongodb", "database", "nosql"],
  scores: [85, 90, 78, 92],
  mixed: ["string", 123, true, null]
});

// Embedded Document
db.types.insertOne({
  address: {
    street: "123 Main St",
    city: "New York",
    zip: "10001"
  }
});

// ObjectId
db.types.insertOne({
  relatedDoc: ObjectId("507f1f77bcf86cd799439011")
});

// Binary Data
db.types.insertOne({
  // Binary subtypes: 0 (generic), 3 (old UUID), 4 (UUID), 5 (MD5)
  data: BinData(0, "SGVsbG8gV29ybGQ="),  // Base64 encoded
  uuid: UUID("550e8400-e29b-41d4-a716-446655440000")
});

// Null
db.types.insertOne({
  middleName: null,
  deletedAt: null
});

// Regular Expression
db.types.insertOne({
  pattern: /^user_\d+$/i,
  // Or using RegExp constructor
  altPattern: new RegExp("^product", "i")
});

// Timestamp (internal use for replication)
db.types.insertOne({
  ts: Timestamp(1234567890, 1)  // seconds, increment
});

// Min/Max Key (for sharding boundaries)
db.types.insertOne({
  minBoundary: MinKey(),
  maxBoundary: MaxKey()
});
```

### Type Checking

```javascript
// Find documents by type
db.collection.find({ field: { $type: "string" } })
db.collection.find({ field: { $type: 2 } })  // Using type number

// Multiple types
db.collection.find({ 
  field: { $type: ["string", "null"] } 
})

// Check if field exists and is not null
db.collection.find({ 
  field: { $exists: true, $ne: null } 
})

// Find documents where number is integer
db.collection.find({
  $expr: {
    $eq: [{ $type: "$numField" }, "int"]
  }
})
```

### Type Conversion

```javascript
// Using aggregation pipeline for type conversion
db.collection.aggregate([
  {
    $addFields: {
      // Convert to string
      priceStr: { $toString: "$price" },
      
      // Convert to integer
      qtyInt: { $toInt: "$quantity" },
      
      // Convert to double
      amountDouble: { $toDouble: "$amount" },
      
      // Convert to date
      dateConverted: { $toDate: "$dateString" },
      
      // Convert to ObjectId
      refId: { $toObjectId: "$refIdString" },
      
      // Convert to boolean
      isActive: { $toBool: "$activeFlag" },
      
      // Convert with $convert (more control)
      converted: {
        $convert: {
          input: "$value",
          to: "decimal",
          onError: NumberDecimal("0"),
          onNull: NumberDecimal("0")
        }
      }
    }
  }
])
```

---

## The _id Field and ObjectId

### Understanding ObjectId

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ObjectId Structure (12 bytes)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  507f1f77bcf86cd799439011                                          │
│  ├────────┬────────┬──────┬──────┤                                 │
│  │   4    │   5    │  3   │  3   │  (bytes)                        │
│  │ bytes  │ bytes  │bytes │bytes │                                 │
│  ├────────┼────────┼──────┼──────┤                                 │
│  │  507f  │ 1f77bc │ f86c │ d799 │                                 │
│  │  1f77  │        │  d7  │ 4390 │                                 │
│  │        │        │      │  11  │                                 │
│  ├────────┼────────┼──────┼──────┤                                 │
│  │ Time-  │ Random │ Counter     │                                 │
│  │ stamp  │ Value  │ (starts    │                                 │
│  │ (Unix) │(unique)│ random)    │                                 │
│  └────────┴────────┴──────┴──────┘                                 │
│                                                                     │
│  Pre-MongoDB 3.4:                                                   │
│  │ 4 bytes │ 3 bytes   │ 2 bytes │ 3 bytes    │                    │
│  │ timestamp│ machine ID│ proc ID │ counter    │                    │
│                                                                     │
│  MongoDB 3.4+:                                                      │
│  │ 4 bytes │ 5 bytes        │ 3 bytes         │                    │
│  │ timestamp│ random value   │ counter         │                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Working with ObjectId

```javascript
// Create new ObjectId
const newId = new ObjectId();
console.log(newId);  // ObjectId("507f1f77bcf86cd799439011")

// Create from string
const fromString = ObjectId("507f1f77bcf86cd799439011");

// Extract timestamp
const id = ObjectId("507f1f77bcf86cd799439011");
const timestamp = id.getTimestamp();
console.log(timestamp);  // ISODate("2012-10-17T20:46:22Z")

// Compare ObjectIds
const id1 = ObjectId("507f1f77bcf86cd799439011");
const id2 = ObjectId("507f1f77bcf86cd799439012");
id1.equals(id2);  // false

// Convert to string
const idStr = id.toString();
// or
const idStr2 = id.str;

// Check if valid ObjectId
ObjectId.isValid("507f1f77bcf86cd799439011");  // true
ObjectId.isValid("invalid");  // false

// Create ObjectId from timestamp
const dateId = ObjectId.fromDate(new Date("2024-01-01"));
```

### Custom _id Fields

```javascript
// Using custom _id (any unique value)

// String _id
db.users.insertOne({
  _id: "user_john_doe",
  name: "John Doe"
});

// Integer _id
db.products.insertOne({
  _id: 12345,
  name: "Product"
});

// Compound _id
db.events.insertOne({
  _id: {
    userId: "user123",
    eventType: "login",
    date: ISODate("2024-01-15")
  },
  details: { ip: "192.168.1.1" }
});

// UUID _id
db.sessions.insertOne({
  _id: UUID("550e8400-e29b-41d4-a716-446655440000"),
  data: {}
});
```

### Querying by _id

```javascript
// Find by ObjectId
db.collection.findOne({ _id: ObjectId("507f1f77bcf86cd799439011") })

// Find by custom string _id
db.users.findOne({ _id: "user_john_doe" })

// Find by compound _id
db.events.findOne({
  "_id.userId": "user123",
  "_id.eventType": "login"
})

// Find documents created after a date using ObjectId
const startId = ObjectId.fromDate(new Date("2024-01-01"));
db.collection.find({ _id: { $gte: startId } })
```

---

## Working with Documents

### Accessing Nested Fields

```javascript
// Document structure
{
  "_id": 1,
  "user": {
    "name": {
      "first": "John",
      "last": "Doe"
    },
    "contact": {
      "email": "john@example.com",
      "phone": "+1-555-0100"
    }
  },
  "orders": [
    { "id": "ord1", "total": 100, "items": ["a", "b"] },
    { "id": "ord2", "total": 200, "items": ["c", "d", "e"] }
  ]
}

// Dot notation for nested fields
db.customers.find({ "user.name.first": "John" })

// Access array elements by index
db.customers.find({ "orders.0.total": 100 })

// Query array elements
db.customers.find({ "orders.total": { $gt: 150 } })

// Access nested array elements
db.customers.find({ "orders.items": "c" })
```

### Document Update Patterns

```javascript
// Update nested field
db.customers.updateOne(
  { _id: 1 },
  { $set: { "user.contact.email": "newemail@example.com" } }
)

// Update array element by index
db.customers.updateOne(
  { _id: 1 },
  { $set: { "orders.0.total": 150 } }
)

// Update matching array element ($ positional)
db.customers.updateOne(
  { _id: 1, "orders.id": "ord1" },
  { $set: { "orders.$.total": 175 } }
)

// Update all matching array elements ($[])
db.customers.updateOne(
  { _id: 1 },
  { $inc: { "orders.$[].total": 10 } }  // Add 10 to all orders
)

// Update filtered array elements ($[identifier])
db.customers.updateOne(
  { _id: 1 },
  { $set: { "orders.$[elem].status": "shipped" } },
  { arrayFilters: [{ "elem.total": { $gt: 100 } }] }
)
```

### Document Comparison

```javascript
// Documents are compared field by field
db.collection.find({
  address: {
    street: "123 Main St",
    city: "NYC",
    zip: "10001"
  }
})
// This matches EXACT document structure and order!

// Better approach - query individual fields
db.collection.find({
  "address.street": "123 Main St",
  "address.city": "NYC"
})
```

---

## Document Size Limits

### Size Constraints

| Constraint | Limit |
|------------|-------|
| Maximum document size | 16 MB |
| Maximum nesting depth | 100 levels |
| Maximum number of indexed fields | No specific limit |
| Maximum index key size | 1024 bytes (default) |

### Handling Large Data

```javascript
// Check document size
Object.bsonsize(db.collection.findOne({ _id: 1 }))

// Or using aggregation
db.collection.aggregate([
  { $match: { _id: 1 } },
  { $project: { size: { $bsonSize: "$$ROOT" } } }
])

// Find documents approaching size limit
db.collection.aggregate([
  {
    $project: {
      size: { $bsonSize: "$$ROOT" }
    }
  },
  { $match: { size: { $gt: 10000000 } } },  // > 10MB
  { $sort: { size: -1 } }
])
```

### GridFS for Large Files

```javascript
// GridFS splits files into chunks (default 255KB)
// Store file
const bucket = new GridFSBucket(db);
const uploadStream = bucket.openUploadStream('largefile.pdf');
fs.createReadStream('./largefile.pdf').pipe(uploadStream);

// Retrieve file
const downloadStream = bucket.openDownloadStreamByName('largefile.pdf');
downloadStream.pipe(fs.createWriteStream('./downloaded.pdf'));

// GridFS collections:
// - fs.files (metadata)
// - fs.chunks (file data)
```

### Strategies for Large Documents

```javascript
// 1. Subset Pattern - Store only relevant data
{
  "_id": 1,
  "productId": "prod123",
  "recentReviews": [  // Only last 10 reviews
    { "user": "u1", "rating": 5 },
    { "user": "u2", "rating": 4 }
  ],
  "totalReviews": 1500,
  "averageRating": 4.5
}

// 2. Bucket Pattern - Group time-series data
{
  "sensorId": "sensor001",
  "date": ISODate("2024-01-15"),
  "readings": [  // 1 document per day instead of per reading
    { "time": "00:00", "value": 23.5 },
    { "time": "00:01", "value": 23.6 },
    // ...up to 1440 readings
  ],
  "count": 1440
}

// 3. Extended Reference - Store essential data inline
{
  "_id": "order123",
  "customer": {  // Essential info embedded
    "_id": "cust456",
    "name": "John Doe",
    "email": "john@example.com"
    // Full customer details in separate collection
  },
  "total": 500
}
```

---

## Best Practices

### Document Design Guidelines

```javascript
// ✅ DO: Use meaningful field names
{
  "firstName": "John",
  "lastName": "Doe",
  "emailAddress": "john@example.com"
}

// ❌ DON'T: Use abbreviated/cryptic names (harder to maintain)
{
  "fn": "John",
  "ln": "Doe",
  "e": "john@example.com"
}

// ✅ DO: Use consistent naming conventions
{
  "createdAt": ISODate("..."),
  "updatedAt": ISODate("..."),
  "isActive": true
}

// ❌ DON'T: Mix naming conventions
{
  "created_at": ISODate("..."),
  "UpdatedAt": ISODate("..."),
  "active": true
}

// ✅ DO: Use appropriate data types
{
  "price": NumberDecimal("99.99"),  // Precise decimal
  "quantity": NumberInt(100),        // Integer
  "createdAt": ISODate("2024-01-15") // Native date
}

// ❌ DON'T: Store everything as strings
{
  "price": "99.99",      // String - loses numeric operations
  "quantity": "100",     // String
  "createdAt": "2024-01-15"  // String - loses date operations
}
```

### Array Management

```javascript
// ✅ DO: Keep arrays bounded
{
  "recentOrders": [/* last 10 orders */],
  "totalOrders": 150
}

// ❌ DON'T: Allow unbounded array growth
{
  "allOrders": [/* thousands of orders */]  // Document size issue
}

// ✅ DO: Use $slice to limit array size on push
db.users.updateOne(
  { _id: 1 },
  {
    $push: {
      recentActivity: {
        $each: [{ action: "login", time: new Date() }],
        $slice: -100  // Keep last 100 entries
      }
    }
  }
)
```

### Null and Missing Fields

```javascript
// Distinguish between null, missing, and empty

// Field is null - explicitly set
{ "middleName": null }

// Field is missing - not present
{ "firstName": "John" }  // middleName not present

// Field is empty string
{ "middleName": "" }

// Field is empty array
{ "tags": [] }

// Query differences:
db.users.find({ middleName: null })       // Matches null and missing
db.users.find({ middleName: { $exists: true, $eq: null } })  // Only null
db.users.find({ middleName: { $exists: false } })  // Only missing
```

### Schema Evolution

```javascript
// Use versioning for schema changes
{
  "_id": 1,
  "schemaVersion": 2,
  "name": "John Doe",
  // New fields in version 2
  "profile": {
    "bio": "Developer",
    "avatar": "url"
  }
}

// Migration helper
db.users.find({ schemaVersion: { $lt: 2 } }).forEach(doc => {
  db.users.updateOne(
    { _id: doc._id },
    {
      $set: {
        schemaVersion: 2,
        profile: {
          bio: "",
          avatar: null
        }
      }
    }
  );
});
```

---

## Summary

### Key Concepts

1. **BSON** is MongoDB's binary JSON format with extended data types
2. **Documents** are flexible, schema-free data structures
3. **ObjectId** is the default unique identifier with embedded timestamp
4. **Data types** include strings, numbers, dates, arrays, and embedded documents
5. **Maximum document size** is 16 MB

### BSON Type Summary

| Category | Types |
|----------|-------|
| **Text** | String |
| **Numeric** | Double, Int32, Int64, Decimal128 |
| **Date/Time** | Date, Timestamp |
| **Binary** | BinData, ObjectId, UUID |
| **Boolean/Null** | Boolean, Null |
| **Composite** | Object, Array |
| **Special** | Regex, MinKey, MaxKey |

### What's Next?

In the next chapter, we'll explore Databases and Collections, understanding how MongoDB organizes data at a higher level.

---

## Practice Questions

1. What are the main differences between JSON and BSON?
2. How is an ObjectId structured, and what information does it contain?
3. What is the maximum document size in MongoDB?
4. When should you use NumberDecimal instead of Double?
5. How do you access nested document fields in queries?
6. What are the rules for field names in MongoDB documents?
7. How can you query for documents where a field is null vs missing?
8. What strategies can you use for documents approaching the size limit?

---

## Hands-On Exercises

### Exercise 1: Working with Data Types

```javascript
// Create a collection with various BSON types
db.dataTypes.insertOne({
  stringField: "Hello World",
  intField: NumberInt(42),
  longField: NumberLong("9999999999999"),
  doubleField: 3.14159,
  decimalField: NumberDecimal("123.456789"),
  boolField: true,
  dateField: new Date(),
  arrayField: [1, "two", { three: 3 }],
  objectField: { nested: { deep: "value" } },
  nullField: null,
  binaryField: BinData(0, "SGVsbG8="),
  objectIdField: new ObjectId()
});

// Query by type
db.dataTypes.find({ stringField: { $type: "string" } })
```

### Exercise 2: ObjectId Operations

```javascript
// Create documents with ObjectIds
for (let i = 0; i < 10; i++) {
  db.test.insertOne({ data: "item " + i });
}

// Find documents created in the last hour
const oneHourAgo = new Date(Date.now() - 3600000);
const hourId = ObjectId.fromDate(oneHourAgo);
db.test.find({ _id: { $gte: hourId } })

// Extract timestamps from ObjectIds
db.test.find().forEach(doc => {
  print(doc._id + " created at: " + doc._id.getTimestamp());
});
```

### Exercise 3: Nested Document Operations

```javascript
// Create a complex document
db.orders.insertOne({
  orderId: "ORD001",
  customer: {
    name: { first: "John", last: "Doe" },
    contact: { email: "john@example.com", phone: "+1-555-0100" }
  },
  items: [
    { sku: "ITEM1", name: "Widget", quantity: 2, price: 25.00 },
    { sku: "ITEM2", name: "Gadget", quantity: 1, price: 50.00 }
  ],
  shipping: {
    address: { street: "123 Main St", city: "NYC", zip: "10001" }
  }
});

// Practice queries:
// 1. Find by customer's first name
// 2. Update customer's email
// 3. Add a new item to the order
// 4. Update quantity of a specific item
// 5. Calculate total order value using aggregation
```

---

[← Previous: MongoDB Architecture](03-mongodb-architecture.md) | [Next: Databases and Collections →](05-databases-and-collections.md)
