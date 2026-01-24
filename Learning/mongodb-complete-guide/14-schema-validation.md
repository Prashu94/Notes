# Chapter 14: Schema Validation

## Table of Contents
- [Schema Validation Overview](#schema-validation-overview)
- [JSON Schema Validation](#json-schema-validation)
- [Validation Rules](#validation-rules)
- [Validation Actions and Levels](#validation-actions-and-levels)
- [Common Validation Patterns](#common-validation-patterns)
- [Modifying Validation Rules](#modifying-validation-rules)
- [Bypassing Validation](#bypassing-validation)
- [Best Practices](#best-practices)
- [Summary](#summary)

---

## Schema Validation Overview

MongoDB schema validation allows you to enforce document structure and data types at the database level, ensuring data integrity while maintaining flexibility.

### Why Use Schema Validation?

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Schema Validation Benefits                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✓ Data Integrity                                                  │
│    • Ensure required fields are present                            │
│    • Validate data types and formats                               │
│    • Enforce business rules at database level                      │
│                                                                     │
│  ✓ Flexibility                                                     │
│    • Allow additional fields not in schema                         │
│    • Warn vs reject invalid documents                              │
│    • Different strictness levels                                   │
│                                                                     │
│  ✓ Documentation                                                   │
│    • Schema serves as documentation                                │
│    • Clear expectations for data structure                         │
│                                                                     │
│  ✓ Defense in Depth                                                │
│    • Catches bugs that bypass application validation               │
│    • Protects against malformed data                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Validation Approaches

| Approach | Description |
|----------|-------------|
| **JSON Schema** | Standard JSON Schema validation (recommended) |
| **Query Operators** | MongoDB query expressions for validation |
| **Combined** | Mix of JSON Schema and query expressions |

---

## JSON Schema Validation

### Basic JSON Schema

```javascript
// Create collection with validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email", "createdAt"],
      properties: {
        name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 100,
          description: "must be a string and is required"
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "must be a valid email address"
        },
        age: {
          bsonType: "int",
          minimum: 0,
          maximum: 150,
          description: "must be an integer between 0 and 150"
        },
        createdAt: {
          bsonType: "date",
          description: "must be a date"
        }
      }
    }
  }
})

// Valid insert
db.users.insertOne({
  name: "John Doe",
  email: "john@example.com",
  age: NumberInt(30),
  createdAt: new Date()
})

// Invalid insert - will fail
db.users.insertOne({
  name: "",  // Too short
  email: "invalid-email",  // Invalid format
  age: 200  // Out of range
})
// Error: Document failed validation
```

### BSON Types

```javascript
// Available BSON types for validation
{
  $jsonSchema: {
    bsonType: "object",
    properties: {
      // String types
      text: { bsonType: "string" },
      
      // Numeric types
      integerNum: { bsonType: "int" },
      longNum: { bsonType: "long" },
      doubleNum: { bsonType: "double" },
      decimalNum: { bsonType: "decimal" },
      anyNumber: { bsonType: "number" },  // Any numeric type
      
      // Date/Time
      dateField: { bsonType: "date" },
      timestampField: { bsonType: "timestamp" },
      
      // Binary and Special
      binaryData: { bsonType: "binData" },
      objectIdField: { bsonType: "objectId" },
      boolField: { bsonType: "bool" },
      nullField: { bsonType: "null" },
      regexField: { bsonType: "regex" },
      
      // Complex types
      arrayField: { bsonType: "array" },
      objectField: { bsonType: "object" }
    }
  }
}
```

### Complete Schema Example

```javascript
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      title: "Product Validation",
      required: ["sku", "name", "price", "category"],
      properties: {
        _id: {
          bsonType: "objectId"
        },
        sku: {
          bsonType: "string",
          minLength: 3,
          maxLength: 20,
          pattern: "^[A-Z0-9-]+$",
          description: "SKU must be uppercase alphanumeric with dashes"
        },
        name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 200
        },
        description: {
          bsonType: "string",
          maxLength: 5000
        },
        price: {
          bsonType: "double",
          minimum: 0,
          exclusiveMinimum: false,
          description: "Price must be non-negative"
        },
        category: {
          enum: ["Electronics", "Clothing", "Books", "Home", "Other"],
          description: "Category must be from predefined list"
        },
        tags: {
          bsonType: "array",
          items: {
            bsonType: "string",
            maxLength: 50
          },
          maxItems: 10,
          uniqueItems: true
        },
        specifications: {
          bsonType: "object",
          additionalProperties: {
            bsonType: "string"
          }
        },
        inventory: {
          bsonType: "object",
          required: ["quantity"],
          properties: {
            quantity: {
              bsonType: "int",
              minimum: 0
            },
            warehouse: {
              bsonType: "string"
            },
            lastRestocked: {
              bsonType: "date"
            }
          }
        },
        isActive: {
          bsonType: "bool"
        },
        createdAt: {
          bsonType: "date"
        },
        updatedAt: {
          bsonType: "date"
        }
      },
      additionalProperties: false  // Reject unknown fields
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
```

---

## Validation Rules

### String Validation

```javascript
{
  $jsonSchema: {
    properties: {
      // Basic string
      name: {
        bsonType: "string"
      },
      
      // String with length constraints
      username: {
        bsonType: "string",
        minLength: 3,
        maxLength: 30
      },
      
      // String with pattern (regex)
      email: {
        bsonType: "string",
        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      },
      
      // Phone number pattern
      phone: {
        bsonType: "string",
        pattern: "^\\+?[1-9]\\d{1,14}$"
      },
      
      // URL pattern
      website: {
        bsonType: "string",
        pattern: "^https?://.+"
      },
      
      // Slug pattern
      slug: {
        bsonType: "string",
        pattern: "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      }
    }
  }
}
```

### Numeric Validation

```javascript
{
  $jsonSchema: {
    properties: {
      // Integer with range
      age: {
        bsonType: "int",
        minimum: 0,
        maximum: 150
      },
      
      // Price (double) with minimum
      price: {
        bsonType: "double",
        minimum: 0
      },
      
      // Quantity with exclusive minimum
      discount: {
        bsonType: "double",
        minimum: 0,
        maximum: 100,
        exclusiveMaximum: true  // Must be < 100
      },
      
      // Decimal for precise calculations
      taxRate: {
        bsonType: "decimal",
        minimum: Decimal128("0"),
        maximum: Decimal128("1")
      },
      
      // Multiple of constraint (e.g., cents)
      amount: {
        bsonType: "double",
        multipleOf: 0.01
      }
    }
  }
}
```

### Array Validation

```javascript
{
  $jsonSchema: {
    properties: {
      // Basic array
      items: {
        bsonType: "array"
      },
      
      // Array with item type
      tags: {
        bsonType: "array",
        items: {
          bsonType: "string",
          minLength: 1,
          maxLength: 50
        }
      },
      
      // Array with size constraints
      topProducts: {
        bsonType: "array",
        minItems: 1,
        maxItems: 10,
        uniqueItems: true
      },
      
      // Array of objects
      addresses: {
        bsonType: "array",
        items: {
          bsonType: "object",
          required: ["street", "city"],
          properties: {
            street: { bsonType: "string" },
            city: { bsonType: "string" },
            zipCode: { bsonType: "string" }
          }
        }
      },
      
      // Array with mixed types allowed
      mixedArray: {
        bsonType: "array",
        items: {
          oneOf: [
            { bsonType: "string" },
            { bsonType: "int" }
          ]
        }
      }
    }
  }
}
```

### Object (Subdocument) Validation

```javascript
{
  $jsonSchema: {
    properties: {
      // Nested object with required fields
      address: {
        bsonType: "object",
        required: ["street", "city", "country"],
        properties: {
          street: { bsonType: "string" },
          city: { bsonType: "string" },
          state: { bsonType: "string" },
          zipCode: { bsonType: "string" },
          country: { 
            bsonType: "string",
            enum: ["USA", "Canada", "UK", "Other"]
          }
        },
        additionalProperties: false
      },
      
      // Deeply nested object
      profile: {
        bsonType: "object",
        properties: {
          personal: {
            bsonType: "object",
            properties: {
              firstName: { bsonType: "string" },
              lastName: { bsonType: "string" }
            }
          },
          preferences: {
            bsonType: "object",
            properties: {
              theme: { enum: ["light", "dark"] },
              notifications: { bsonType: "bool" }
            }
          }
        }
      }
    }
  }
}
```

### Enum and Const

```javascript
{
  $jsonSchema: {
    properties: {
      // Enum - must be one of listed values
      status: {
        enum: ["pending", "active", "suspended", "deleted"]
      },
      
      // Enum with BSON type
      priority: {
        bsonType: "int",
        enum: [1, 2, 3, 4, 5]
      },
      
      // Const - must be exact value
      version: {
        const: 1
      },
      
      // Type with enum
      role: {
        bsonType: "string",
        enum: ["admin", "user", "guest"]
      }
    }
  }
}
```

---

## Validation Actions and Levels

### Validation Level

```javascript
// Strict: Validate all inserts and updates
db.createCollection("strictCollection", {
  validator: { $jsonSchema: { /* schema */ } },
  validationLevel: "strict"
})

// Moderate: Only validate documents that already match schema
db.createCollection("moderateCollection", {
  validator: { $jsonSchema: { /* schema */ } },
  validationLevel: "moderate"
})

// Off: Disable validation (keeps schema for documentation)
db.runCommand({
  collMod: "collection",
  validationLevel: "off"
})
```

### Validation Action

```javascript
// Error: Reject invalid documents (default)
db.createCollection("errorCollection", {
  validator: { $jsonSchema: { /* schema */ } },
  validationAction: "error"
})

// Warn: Accept document but log warning
db.createCollection("warnCollection", {
  validator: { $jsonSchema: { /* schema */ } },
  validationAction: "warn"
})
```

### Validation Behavior Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│              Validation Level + Action Behavior                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Level: STRICT                                                      │
│  ├── Action: ERROR  → All invalid documents rejected               │
│  └── Action: WARN   → All invalid documents accepted with warning  │
│                                                                     │
│  Level: MODERATE                                                    │
│  ├── If existing document MATCHES schema:                          │
│  │   ├── ERROR → Invalid updates rejected                          │
│  │   └── WARN  → Invalid updates accepted with warning             │
│  └── If existing document DOESN'T MATCH schema:                    │
│      └── No validation applied (document can be updated freely)    │
│                                                                     │
│  Level: OFF                                                         │
│  └── No validation applied                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Common Validation Patterns

### User Schema

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "passwordHash", "createdAt"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        passwordHash: {
          bsonType: "string",
          minLength: 60,
          maxLength: 60
        },
        profile: {
          bsonType: "object",
          properties: {
            firstName: { bsonType: "string", maxLength: 50 },
            lastName: { bsonType: "string", maxLength: 50 },
            avatar: { bsonType: "string" },
            bio: { bsonType: "string", maxLength: 500 }
          }
        },
        roles: {
          bsonType: "array",
          items: {
            enum: ["user", "admin", "moderator"]
          },
          uniqueItems: true
        },
        isActive: {
          bsonType: "bool"
        },
        lastLogin: {
          bsonType: "date"
        },
        createdAt: {
          bsonType: "date"
        }
      }
    }
  }
})
```

### Order Schema

```javascript
db.createCollection("orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["customerId", "items", "status", "createdAt"],
      properties: {
        customerId: {
          bsonType: "objectId"
        },
        orderNumber: {
          bsonType: "string",
          pattern: "^ORD-\\d{4}-\\d{6}$"
        },
        items: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["productId", "quantity", "price"],
            properties: {
              productId: { bsonType: "objectId" },
              name: { bsonType: "string" },
              quantity: { bsonType: "int", minimum: 1 },
              price: { bsonType: "double", minimum: 0 }
            }
          }
        },
        status: {
          enum: ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        },
        shippingAddress: {
          bsonType: "object",
          required: ["street", "city", "country"],
          properties: {
            street: { bsonType: "string" },
            city: { bsonType: "string" },
            state: { bsonType: "string" },
            zipCode: { bsonType: "string" },
            country: { bsonType: "string" }
          }
        },
        payment: {
          bsonType: "object",
          properties: {
            method: { enum: ["credit_card", "debit_card", "paypal", "bank_transfer"] },
            status: { enum: ["pending", "completed", "failed", "refunded"] },
            transactionId: { bsonType: "string" }
          }
        },
        subtotal: { bsonType: "double", minimum: 0 },
        tax: { bsonType: "double", minimum: 0 },
        shipping: { bsonType: "double", minimum: 0 },
        total: { bsonType: "double", minimum: 0 },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
})
```

### Using Query Operators for Validation

```javascript
// Combine $jsonSchema with query operators
db.createCollection("events", {
  validator: {
    $and: [
      // JSON Schema validation
      {
        $jsonSchema: {
          bsonType: "object",
          required: ["title", "startDate", "endDate"],
          properties: {
            title: { bsonType: "string" },
            startDate: { bsonType: "date" },
            endDate: { bsonType: "date" }
          }
        }
      },
      // Query expression: endDate must be after startDate
      {
        $expr: {
          $gt: ["$endDate", "$startDate"]
        }
      }
    ]
  }
})

// Complex business rule validation
db.createCollection("discounts", {
  validator: {
    $and: [
      {
        $jsonSchema: {
          bsonType: "object",
          required: ["type", "value"],
          properties: {
            type: { enum: ["percentage", "fixed"] },
            value: { bsonType: "double", minimum: 0 }
          }
        }
      },
      // If type is "percentage", value must be <= 100
      {
        $or: [
          { type: { $ne: "percentage" } },
          { value: { $lte: 100 } }
        ]
      }
    ]
  }
})
```

---

## Modifying Validation Rules

### Update Collection Validation

```javascript
// Get current validation rules
db.getCollectionInfos({ name: "products" })

// Modify validation using collMod
db.runCommand({
  collMod: "products",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["sku", "name", "price"],
      properties: {
        sku: { bsonType: "string" },
        name: { bsonType: "string" },
        price: { bsonType: "double", minimum: 0 },
        // New field
        brand: { bsonType: "string" }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
```

### Migration Strategy

```javascript
// Step 1: Add validation with "warn" action
db.runCommand({
  collMod: "products",
  validator: { $jsonSchema: newSchema },
  validationAction: "warn"  // Don't reject yet
})

// Step 2: Find invalid documents
db.products.find({
  $nor: [{ $jsonSchema: newSchema }]
})

// Step 3: Fix invalid documents
db.products.updateMany(
  { category: { $exists: false } },
  { $set: { category: "Other" } }
)

// Step 4: Switch to error action
db.runCommand({
  collMod: "products",
  validationAction: "error"
})
```

---

## Bypassing Validation

### Bypass Document Validation

```javascript
// For admin operations that need to bypass validation
db.products.insertOne(
  { name: "Test", price: -10 },  // Invalid price
  { bypassDocumentValidation: true }
)

// Update with bypass
db.products.updateOne(
  { sku: "TEST001" },
  { $set: { price: -10 } },
  { bypassDocumentValidation: true }
)

// Bulk write with bypass
db.products.bulkWrite(
  [
    { insertOne: { document: { name: "Test" } } }
  ],
  { bypassDocumentValidation: true }
)

// Note: Requires bypassDocumentValidation privilege
```

### When to Bypass

```
┌─────────────────────────────────────────────────────────────────────┐
│                 When to Bypass Validation                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✓ Appropriate:                                                    │
│  • Data migration from legacy systems                              │
│  • Emergency fixes by DBAs                                         │
│  • Importing historical data                                       │
│  • Schema evolution transitions                                    │
│                                                                     │
│  ✗ Avoid:                                                          │
│  • Regular application operations                                  │
│  • As workaround for validation issues                            │
│  • Without proper authorization                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### 1. Start Simple, Evolve

```javascript
// Start with basic validation
db.createCollection("items", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name"],
      properties: {
        name: { bsonType: "string" }
      }
    }
  }
})

// Add more rules as needed
db.runCommand({
  collMod: "items",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "category"],
      properties: {
        name: { bsonType: "string", maxLength: 200 },
        category: { enum: ["A", "B", "C"] }
      }
    }
  }
})
```

### 2. Use Descriptions

```javascript
{
  $jsonSchema: {
    properties: {
      email: {
        bsonType: "string",
        pattern: "^[^@]+@[^@]+\\.[^@]+$",
        description: "Must be a valid email address format"
      },
      age: {
        bsonType: "int",
        minimum: 18,
        maximum: 120,
        description: "Age must be between 18 and 120"
      }
    }
  }
}
```

### 3. Allow Flexibility Where Needed

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["type", "data"],
    properties: {
      type: { enum: ["user", "order", "product"] },
      // Strict for known fields
      createdAt: { bsonType: "date" },
      // Flexible for metadata
      metadata: {
        bsonType: "object"
        // No additionalProperties: false
        // Allows any structure
      }
    },
    additionalProperties: true  // Allow unknown top-level fields
  }
}
```

### 4. Validate at Multiple Levels

```javascript
// Application level (fast, user-friendly errors)
function validateUser(user) {
  if (!user.email) throw new Error("Email is required")
  if (!isValidEmail(user.email)) throw new Error("Invalid email format")
  // ... more validations
}

// Database level (safety net)
// Catches bugs that bypass application validation
```

### 5. Test Validation Rules

```javascript
// Test valid document
try {
  db.products.insertOne({
    sku: "TEST-001",
    name: "Test Product",
    price: 99.99,
    category: "Electronics"
  })
  print("Valid document: PASS")
} catch (e) {
  print("Valid document: FAIL - " + e.message)
}

// Test invalid documents
const invalidDocs = [
  { name: "No SKU", price: 99.99 },  // Missing required field
  { sku: "test", name: "X", price: 99 },  // Invalid SKU pattern
  { sku: "TEST-002", name: "X", price: -10 }  // Invalid price
]

invalidDocs.forEach((doc, i) => {
  try {
    db.products.insertOne(doc)
    print(`Invalid doc ${i}: FAIL - Should have been rejected`)
  } catch (e) {
    print(`Invalid doc ${i}: PASS - Correctly rejected`)
  }
})
```

---

## Summary

### Validation Features

| Feature | Description |
|---------|-------------|
| **$jsonSchema** | Standard JSON Schema validation |
| **bsonType** | Validate BSON data types |
| **required** | Specify mandatory fields |
| **enum** | Limit to specific values |
| **pattern** | Regex validation for strings |
| **minimum/maximum** | Range validation for numbers |

### Validation Levels

| Level | Behavior |
|-------|----------|
| **strict** | Validate all documents |
| **moderate** | Only validate matching documents |
| **off** | Disable validation |

### What's Next?

In the next chapter, we'll explore Schema Design Patterns for common application scenarios.

---

## Practice Questions

1. What's the difference between validationLevel "strict" and "moderate"?
2. How do you validate email addresses using JSON Schema?
3. When would you use validationAction "warn" vs "error"?
4. How do you add validation to an existing collection?
5. What are the BSON types available for validation?
6. How do you validate array contents?
7. When should you bypass document validation?
8. How do you combine $jsonSchema with query operators?

---

## Hands-On Exercises

### Exercise 1: Create Validated Collection

```javascript
// Create a "contacts" collection with validation
db.createCollection("contacts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email"],
      properties: {
        name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 100
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        phone: {
          bsonType: "string",
          pattern: "^[+]?[0-9]{10,15}$"
        },
        type: {
          enum: ["personal", "work", "other"]
        }
      }
    }
  },
  validationAction: "error"
})

// Test valid insert
db.contacts.insertOne({
  name: "John Doe",
  email: "john@example.com",
  phone: "+1234567890",
  type: "work"
})

// Test invalid inserts (should fail)
try {
  db.contacts.insertOne({ name: "No Email" })
} catch (e) {
  print("Correctly rejected: missing email")
}

try {
  db.contacts.insertOne({ name: "Bad Email", email: "not-an-email" })
} catch (e) {
  print("Correctly rejected: invalid email format")
}
```

### Exercise 2: E-commerce Product Validation

```javascript
// Create products collection with comprehensive validation
db.createCollection("shop_products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["sku", "name", "price", "category", "stock"],
      properties: {
        sku: {
          bsonType: "string",
          pattern: "^[A-Z]{3}-[0-9]{4}$",
          description: "Format: XXX-0000"
        },
        name: {
          bsonType: "string",
          minLength: 3,
          maxLength: 200
        },
        description: {
          bsonType: "string",
          maxLength: 2000
        },
        price: {
          bsonType: "double",
          minimum: 0.01
        },
        salePrice: {
          bsonType: "double",
          minimum: 0
        },
        category: {
          enum: ["Electronics", "Clothing", "Home", "Books", "Sports"]
        },
        stock: {
          bsonType: "int",
          minimum: 0
        },
        tags: {
          bsonType: "array",
          items: { bsonType: "string", maxLength: 30 },
          maxItems: 10,
          uniqueItems: true
        },
        dimensions: {
          bsonType: "object",
          properties: {
            length: { bsonType: "double", minimum: 0 },
            width: { bsonType: "double", minimum: 0 },
            height: { bsonType: "double", minimum: 0 },
            weight: { bsonType: "double", minimum: 0 }
          }
        },
        isActive: {
          bsonType: "bool"
        }
      }
    }
  }
})

// Insert valid products
db.shop_products.insertMany([
  {
    sku: "ELE-0001",
    name: "Wireless Mouse",
    price: 29.99,
    category: "Electronics",
    stock: NumberInt(100),
    tags: ["computer", "accessories"],
    isActive: true
  },
  {
    sku: "CLO-0001",
    name: "Cotton T-Shirt",
    price: 19.99,
    category: "Clothing",
    stock: NumberInt(200),
    dimensions: { length: 30, width: 20, height: 2, weight: 0.2 }
  }
])
```

### Exercise 3: Modify Existing Validation

```javascript
// Start with loose validation
db.createCollection("articles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title"],
      properties: {
        title: { bsonType: "string" }
      }
    }
  },
  validationAction: "warn"  // Start with warn
})

// Insert some documents
db.articles.insertMany([
  { title: "Article 1", content: "Content 1" },
  { title: "Article 2" },  // Missing content
  { title: "A" }  // Very short title
])

// Add stricter validation
db.runCommand({
  collMod: "articles",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "content", "author"],
      properties: {
        title: { bsonType: "string", minLength: 5, maxLength: 200 },
        content: { bsonType: "string", minLength: 10 },
        author: { bsonType: "string" },
        publishedAt: { bsonType: "date" },
        tags: {
          bsonType: "array",
          items: { bsonType: "string" }
        }
      }
    }
  },
  validationLevel: "moderate",  // Don't break existing docs
  validationAction: "error"
})

// Find documents that don't match new schema
db.articles.find({
  $nor: [{
    $and: [
      { title: { $type: "string" } },
      { content: { $type: "string" } },
      { author: { $type: "string" } }
    ]
  }]
})
```

### Exercise 4: Complex Validation Rules

```javascript
// Create collection with business rules
db.createCollection("reservations", {
  validator: {
    $and: [
      {
        $jsonSchema: {
          bsonType: "object",
          required: ["guestName", "roomType", "checkIn", "checkOut", "guests"],
          properties: {
            guestName: { bsonType: "string", minLength: 2 },
            roomType: { enum: ["single", "double", "suite", "penthouse"] },
            checkIn: { bsonType: "date" },
            checkOut: { bsonType: "date" },
            guests: { bsonType: "int", minimum: 1, maximum: 6 },
            specialRequests: { bsonType: "string", maxLength: 500 }
          }
        }
      },
      // Business rule: checkOut must be after checkIn
      { $expr: { $gt: ["$checkOut", "$checkIn"] } }
    ]
  }
})

// Valid reservation
db.reservations.insertOne({
  guestName: "John Smith",
  roomType: "double",
  checkIn: new Date("2024-03-01"),
  checkOut: new Date("2024-03-05"),
  guests: NumberInt(2)
})

// Invalid: checkOut before checkIn (should fail)
try {
  db.reservations.insertOne({
    guestName: "Jane Doe",
    roomType: "single",
    checkIn: new Date("2024-03-10"),
    checkOut: new Date("2024-03-05"),  // Before checkIn!
    guests: NumberInt(1)
  })
} catch (e) {
  print("Correctly rejected: checkOut before checkIn")
}
```

---

[← Previous: References and Joins](13-references-and-joins.md) | [Next: Schema Design Patterns →](15-schema-design-patterns.md)
