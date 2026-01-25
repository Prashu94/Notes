# Chapter 69: Schema Validation

## Table of Contents
- [Schema Validation Overview](#schema-validation-overview)
- [JSON Schema Validation](#json-schema-validation)
- [Validation Rules](#validation-rules)
- [Complex Validation Patterns](#complex-validation-patterns)
- [Validation in Practice](#validation-in-practice)
- [Application-Level Validation](#application-level-validation)
- [Summary](#summary)

---

## Schema Validation Overview

### What is Schema Validation?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Document Validation Flow                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    ┌──────────────┐                                                 │
│    │   Document   │                                                 │
│    │   Insert/    │                                                 │
│    │   Update     │                                                 │
│    └──────┬───────┘                                                 │
│           │                                                         │
│           ▼                                                         │
│    ┌──────────────────┐                                            │
│    │ Schema Validator │                                            │
│    │  (JSON Schema)   │                                            │
│    └──────┬───────────┘                                            │
│           │                                                         │
│    ┌──────┴──────┐                                                  │
│    │             │                                                  │
│    ▼             ▼                                                  │
│  ┌─────┐    ┌────────┐                                             │
│  │Valid│    │Invalid │                                             │
│  └──┬──┘    └───┬────┘                                             │
│     │           │                                                   │
│     ▼           ▼                                                   │
│  ┌──────┐   ┌──────────────────┐                                   │
│  │Write │   │ Error 121        │                                   │
│  │to DB │   │ Document Failed  │                                   │
│  └──────┘   │ Validation       │                                   │
│             └──────────────────┘                                   │
│                                                                     │
│   Validation Levels:                                                │
│   • strict  - All inserts and updates validated                    │
│   • moderate - Existing valid documents skip validation            │
│                                                                     │
│   Validation Actions:                                               │
│   • error - Reject invalid documents (default)                     │
│   • warn  - Log warning but allow document                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Validation Options

| Option | Description | Values |
|--------|-------------|--------|
| validationLevel | When to validate | `strict`, `moderate` |
| validationAction | What to do on failure | `error`, `warn` |

---

## JSON Schema Validation

### Basic Schema Creation

```javascript
// Create collection with JSON Schema validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name", "createdAt"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "must be a valid email address"
        },
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 100,
          description: "must be a string between 2-100 characters"
        },
        age: {
          bsonType: "int",
          minimum: 0,
          maximum: 150,
          description: "must be an integer between 0-150"
        },
        status: {
          enum: ["active", "inactive", "pending"],
          description: "can only be active, inactive, or pending"
        },
        createdAt: {
          bsonType: "date",
          description: "must be a date"
        }
      },
      additionalProperties: false
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
```

### Modify Existing Collection Validation

```javascript
// Add or update validation rules
db.runCommand({
  collMod: "products",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price", "category"],
      properties: {
        name: {
          bsonType: "string",
          minLength: 1,
          maxLength: 200
        },
        price: {
          bsonType: ["double", "int", "decimal"],
          minimum: 0,
          description: "must be a positive number"
        },
        category: {
          bsonType: "string",
          enum: ["electronics", "clothing", "food", "books", "other"]
        },
        inventory: {
          bsonType: "int",
          minimum: 0
        },
        tags: {
          bsonType: "array",
          items: {
            bsonType: "string"
          },
          maxItems: 10
        }
      }
    }
  },
  validationLevel: "moderate"
})
```

### BSON Types Reference

| BSON Type | Description | Example Values |
|-----------|-------------|----------------|
| `string` | String | "hello" |
| `int` | 32-bit integer | 42 |
| `long` | 64-bit integer | NumberLong(42) |
| `double` | Double | 3.14 |
| `decimal` | Decimal128 | NumberDecimal("3.14") |
| `bool` | Boolean | true, false |
| `date` | Date | ISODate("2024-01-01") |
| `objectId` | ObjectId | ObjectId(...) |
| `array` | Array | [1, 2, 3] |
| `object` | Embedded document | { key: value } |
| `null` | Null | null |
| `binData` | Binary data | BinData(...) |

---

## Validation Rules

### String Validation

```javascript
db.createCollection("articles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      properties: {
        // Length constraints
        title: {
          bsonType: "string",
          minLength: 5,
          maxLength: 200
        },
        // Pattern matching (regex)
        slug: {
          bsonType: "string",
          pattern: "^[a-z0-9-]+$",
          description: "must contain only lowercase letters, numbers, and hyphens"
        },
        // Enumeration
        status: {
          bsonType: "string",
          enum: ["draft", "published", "archived"]
        },
        // URL pattern
        website: {
          bsonType: "string",
          pattern: "^https?:\\/\\/.+",
          description: "must be a valid URL"
        },
        // Phone number pattern
        phone: {
          bsonType: "string",
          pattern: "^\\+?[1-9]\\d{1,14}$",
          description: "must be a valid E.164 phone number"
        }
      }
    }
  }
})
```

### Number Validation

```javascript
db.createCollection("transactions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      properties: {
        // Range constraints
        amount: {
          bsonType: ["double", "decimal"],
          minimum: 0.01,
          maximum: 1000000,
          description: "amount must be between 0.01 and 1,000,000"
        },
        // Exclusive bounds
        discount: {
          bsonType: "double",
          exclusiveMinimum: 0,
          exclusiveMaximum: 1,
          description: "discount must be between 0 and 1 (exclusive)"
        },
        // Integer only
        quantity: {
          bsonType: "int",
          minimum: 1
        },
        // Multiple of (not supported in MongoDB JSON Schema)
        // Use $expr for complex numeric validation
      }
    }
  }
})
```

### Array Validation

```javascript
db.createCollection("orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      properties: {
        // Array with item validation
        items: {
          bsonType: "array",
          minItems: 1,
          maxItems: 100,
          items: {
            bsonType: "object",
            required: ["productId", "quantity", "price"],
            properties: {
              productId: {
                bsonType: "objectId"
              },
              quantity: {
                bsonType: "int",
                minimum: 1
              },
              price: {
                bsonType: "double",
                minimum: 0
              }
            }
          },
          description: "must have 1-100 items"
        },
        // Array of strings
        tags: {
          bsonType: "array",
          uniqueItems: true,
          items: {
            bsonType: "string",
            maxLength: 50
          }
        },
        // Array of enums
        categories: {
          bsonType: "array",
          items: {
            enum: ["sale", "featured", "new", "clearance"]
          }
        }
      }
    }
  }
})
```

### Nested Object Validation

```javascript
db.createCollection("customers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email", "address"],
      properties: {
        name: {
          bsonType: "string"
        },
        email: {
          bsonType: "string",
          pattern: "^[^@]+@[^@]+\\.[^@]+$"
        },
        // Nested object validation
        address: {
          bsonType: "object",
          required: ["street", "city", "country"],
          properties: {
            street: {
              bsonType: "string",
              minLength: 1
            },
            city: {
              bsonType: "string",
              minLength: 1
            },
            state: {
              bsonType: "string"
            },
            postalCode: {
              bsonType: "string",
              pattern: "^[0-9]{5}(-[0-9]{4})?$"
            },
            country: {
              bsonType: "string",
              minLength: 2,
              maxLength: 2,
              description: "must be ISO 3166-1 alpha-2 country code"
            }
          },
          additionalProperties: false
        },
        // Multiple addresses
        shippingAddresses: {
          bsonType: "array",
          maxItems: 5,
          items: {
            bsonType: "object",
            required: ["label", "street", "city", "country"],
            properties: {
              label: {
                enum: ["home", "work", "other"]
              },
              street: { bsonType: "string" },
              city: { bsonType: "string" },
              state: { bsonType: "string" },
              postalCode: { bsonType: "string" },
              country: { bsonType: "string" },
              isDefault: { bsonType: "bool" }
            }
          }
        }
      }
    }
  }
})
```

---

## Complex Validation Patterns

### Conditional Validation (oneOf, anyOf, allOf)

```javascript
// Order validation with conditional rules
db.createCollection("payments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["amount", "method", "status"],
      properties: {
        amount: {
          bsonType: "double",
          minimum: 0.01
        },
        method: {
          enum: ["credit_card", "bank_transfer", "paypal", "crypto"]
        },
        status: {
          enum: ["pending", "completed", "failed", "refunded"]
        }
      },
      // Conditional validation based on payment method
      oneOf: [
        {
          // Credit card requires card details
          properties: {
            method: { const: "credit_card" },
            cardDetails: {
              bsonType: "object",
              required: ["last4", "brand", "expiryMonth", "expiryYear"],
              properties: {
                last4: {
                  bsonType: "string",
                  pattern: "^[0-9]{4}$"
                },
                brand: {
                  enum: ["visa", "mastercard", "amex", "discover"]
                },
                expiryMonth: {
                  bsonType: "int",
                  minimum: 1,
                  maximum: 12
                },
                expiryYear: {
                  bsonType: "int",
                  minimum: 2024
                }
              }
            }
          },
          required: ["cardDetails"]
        },
        {
          // Bank transfer requires bank details
          properties: {
            method: { const: "bank_transfer" },
            bankDetails: {
              bsonType: "object",
              required: ["bankName", "accountLast4"],
              properties: {
                bankName: { bsonType: "string" },
                accountLast4: {
                  bsonType: "string",
                  pattern: "^[0-9]{4}$"
                },
                routingNumber: { bsonType: "string" }
              }
            }
          },
          required: ["bankDetails"]
        },
        {
          // PayPal requires email
          properties: {
            method: { const: "paypal" },
            paypalEmail: {
              bsonType: "string",
              pattern: "^[^@]+@[^@]+\\.[^@]+$"
            }
          },
          required: ["paypalEmail"]
        },
        {
          // Crypto requires wallet address
          properties: {
            method: { const: "crypto" },
            cryptoDetails: {
              bsonType: "object",
              required: ["currency", "walletAddress"],
              properties: {
                currency: {
                  enum: ["BTC", "ETH", "USDT", "USDC"]
                },
                walletAddress: { bsonType: "string" },
                transactionHash: { bsonType: "string" }
              }
            }
          },
          required: ["cryptoDetails"]
        }
      ]
    }
  }
})
```

### Using $expr for Complex Validation

```javascript
// Validation with expression operators
db.runCommand({
  collMod: "orders",
  validator: {
    $and: [
      // JSON Schema for structure
      {
        $jsonSchema: {
          bsonType: "object",
          required: ["items", "subtotal", "total"],
          properties: {
            items: {
              bsonType: "array",
              minItems: 1
            },
            subtotal: { bsonType: "double" },
            discount: { bsonType: "double" },
            tax: { bsonType: "double" },
            total: { bsonType: "double" }
          }
        }
      },
      // Expression-based validation
      {
        $expr: {
          $and: [
            // Total must equal subtotal - discount + tax
            {
              $eq: [
                "$total",
                { $add: [{ $subtract: ["$subtotal", { $ifNull: ["$discount", 0] }] }, { $ifNull: ["$tax", 0] }] }
              ]
            },
            // Discount cannot exceed subtotal
            {
              $lte: [{ $ifNull: ["$discount", 0] }, "$subtotal"]
            }
          ]
        }
      }
    ]
  }
})
```

### Date Validation

```javascript
db.createCollection("events", {
  validator: {
    $and: [
      {
        $jsonSchema: {
          bsonType: "object",
          required: ["name", "startDate", "endDate"],
          properties: {
            name: { bsonType: "string" },
            startDate: { bsonType: "date" },
            endDate: { bsonType: "date" },
            registrationDeadline: { bsonType: "date" }
          }
        }
      },
      // End date must be after start date
      {
        $expr: {
          $gt: ["$endDate", "$startDate"]
        }
      },
      // Registration deadline must be before start date (if exists)
      {
        $expr: {
          $or: [
            { $eq: [{ $type: "$registrationDeadline" }, "missing"] },
            { $lt: ["$registrationDeadline", "$startDate"] }
          ]
        }
      }
    ]
  }
})
```

### Cross-Field Validation

```javascript
db.createCollection("subscriptions", {
  validator: {
    $and: [
      {
        $jsonSchema: {
          bsonType: "object",
          required: ["plan", "price", "billingCycle"],
          properties: {
            plan: {
              enum: ["basic", "standard", "premium", "enterprise"]
            },
            price: {
              bsonType: "double",
              minimum: 0
            },
            billingCycle: {
              enum: ["monthly", "yearly"]
            },
            features: {
              bsonType: "array",
              items: { bsonType: "string" }
            }
          }
        }
      },
      // Price validation based on plan
      {
        $expr: {
          $switch: {
            branches: [
              { case: { $eq: ["$plan", "basic"] }, then: { $lte: ["$price", 10] } },
              { case: { $eq: ["$plan", "standard"] }, then: { $and: [{ $gte: ["$price", 10] }, { $lte: ["$price", 50] }] } },
              { case: { $eq: ["$plan", "premium"] }, then: { $and: [{ $gte: ["$price", 50] }, { $lte: ["$price", 200] }] } },
              { case: { $eq: ["$plan", "enterprise"] }, then: { $gte: ["$price", 200] } }
            ],
            default: false
          }
        }
      }
    ]
  }
})
```

---

## Validation in Practice

### E-Commerce Product Schema

```javascript
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["sku", "name", "price", "status", "category"],
      properties: {
        sku: {
          bsonType: "string",
          pattern: "^[A-Z]{2,4}-[0-9]{4,8}$",
          description: "SKU format: 2-4 uppercase letters, dash, 4-8 digits"
        },
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 200
        },
        description: {
          bsonType: "string",
          maxLength: 5000
        },
        price: {
          bsonType: "object",
          required: ["amount", "currency"],
          properties: {
            amount: {
              bsonType: ["double", "decimal"],
              minimum: 0
            },
            currency: {
              bsonType: "string",
              enum: ["USD", "EUR", "GBP", "CAD", "AUD"]
            },
            compareAtAmount: {
              bsonType: ["double", "decimal", "null"],
              minimum: 0
            }
          }
        },
        status: {
          enum: ["draft", "active", "inactive", "archived"]
        },
        category: {
          bsonType: "object",
          required: ["main"],
          properties: {
            main: { bsonType: "string" },
            sub: { bsonType: "string" },
            tags: {
              bsonType: "array",
              items: { bsonType: "string" },
              maxItems: 20
            }
          }
        },
        inventory: {
          bsonType: "object",
          properties: {
            quantity: {
              bsonType: "int",
              minimum: 0
            },
            trackInventory: { bsonType: "bool" },
            allowBackorder: { bsonType: "bool" },
            lowStockThreshold: {
              bsonType: "int",
              minimum: 0
            }
          }
        },
        variants: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["sku", "price"],
            properties: {
              sku: { bsonType: "string" },
              name: { bsonType: "string" },
              price: {
                bsonType: ["double", "decimal"],
                minimum: 0
              },
              attributes: {
                bsonType: "object",
                additionalProperties: {
                  bsonType: "string"
                }
              },
              inventory: {
                bsonType: "int",
                minimum: 0
              }
            }
          }
        },
        images: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["url"],
            properties: {
              url: {
                bsonType: "string",
                pattern: "^https?://.+"
              },
              alt: { bsonType: "string" },
              position: { bsonType: "int" }
            }
          }
        },
        seo: {
          bsonType: "object",
          properties: {
            title: {
              bsonType: "string",
              maxLength: 70
            },
            description: {
              bsonType: "string",
              maxLength: 160
            },
            slug: {
              bsonType: "string",
              pattern: "^[a-z0-9-]+$"
            }
          }
        },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      },
      additionalProperties: false
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})

// Create indexes
db.products.createIndex({ sku: 1 }, { unique: true })
db.products.createIndex({ "seo.slug": 1 }, { unique: true, sparse: true })
db.products.createIndex({ "category.main": 1, "category.sub": 1 })
db.products.createIndex({ status: 1 })
```

### User Profile Schema

```javascript
db.createCollection("userProfiles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "email", "profile"],
      properties: {
        userId: { bsonType: "objectId" },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        profile: {
          bsonType: "object",
          required: ["firstName", "lastName"],
          properties: {
            firstName: {
              bsonType: "string",
              minLength: 1,
              maxLength: 50
            },
            lastName: {
              bsonType: "string",
              minLength: 1,
              maxLength: 50
            },
            displayName: {
              bsonType: "string",
              maxLength: 100
            },
            avatar: {
              bsonType: "string",
              pattern: "^https?://.+"
            },
            bio: {
              bsonType: "string",
              maxLength: 500
            },
            dateOfBirth: { bsonType: "date" },
            gender: {
              enum: ["male", "female", "other", "prefer_not_to_say", null]
            },
            locale: {
              bsonType: "string",
              pattern: "^[a-z]{2}(-[A-Z]{2})?$"
            },
            timezone: { bsonType: "string" }
          }
        },
        contact: {
          bsonType: "object",
          properties: {
            phone: {
              bsonType: "string",
              pattern: "^\\+?[1-9]\\d{1,14}$"
            },
            address: {
              bsonType: "object",
              properties: {
                street: { bsonType: "string" },
                city: { bsonType: "string" },
                state: { bsonType: "string" },
                postalCode: { bsonType: "string" },
                country: {
                  bsonType: "string",
                  minLength: 2,
                  maxLength: 2
                }
              }
            }
          }
        },
        preferences: {
          bsonType: "object",
          properties: {
            newsletter: { bsonType: "bool" },
            notifications: {
              bsonType: "object",
              properties: {
                email: { bsonType: "bool" },
                push: { bsonType: "bool" },
                sms: { bsonType: "bool" }
              }
            },
            theme: {
              enum: ["light", "dark", "system"]
            }
          }
        },
        social: {
          bsonType: "object",
          additionalProperties: {
            bsonType: "string"
          }
        },
        metadata: {
          bsonType: "object",
          properties: {
            createdAt: { bsonType: "date" },
            updatedAt: { bsonType: "date" },
            lastLoginAt: { bsonType: "date" },
            emailVerified: { bsonType: "bool" },
            phoneVerified: { bsonType: "bool" }
          }
        }
      }
    }
  }
})
```

### View Current Validation Rules

```javascript
// Get collection validation info
db.getCollectionInfos({ name: "products" })[0].options.validator

// Or using runCommand
db.runCommand({
  listCollections: 1,
  filter: { name: "products" }
}).cursor.firstBatch[0].options
```

---

## Application-Level Validation

### JavaScript/Node.js Validation with Joi

```javascript
const Joi = require('joi')

// Define schema with Joi (more flexible than MongoDB validation)
const userSchema = Joi.object({
  email: Joi.string()
    .email()
    .required()
    .lowercase()
    .trim(),
  
  password: Joi.string()
    .min(8)
    .max(100)
    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .required()
    .messages({
      'string.pattern.base': 'Password must contain uppercase, lowercase, number, and special character'
    }),
  
  name: Joi.object({
    first: Joi.string().min(1).max(50).required(),
    last: Joi.string().min(1).max(50).required()
  }).required(),
  
  age: Joi.number()
    .integer()
    .min(13)
    .max(120)
    .optional(),
  
  phone: Joi.string()
    .pattern(/^\+?[1-9]\d{1,14}$/)
    .optional(),
  
  address: Joi.object({
    street: Joi.string().required(),
    city: Joi.string().required(),
    state: Joi.string().optional(),
    postalCode: Joi.string().required(),
    country: Joi.string().length(2).uppercase().required()
  }).optional(),
  
  preferences: Joi.object({
    newsletter: Joi.boolean().default(false),
    theme: Joi.string().valid('light', 'dark', 'system').default('system')
  }).default()
})

// Validation function
async function validateAndCreate(db, userData) {
  // Validate with Joi
  const { error, value } = userSchema.validate(userData, {
    abortEarly: false,  // Return all errors
    stripUnknown: true  // Remove unknown fields
  })
  
  if (error) {
    const errors = error.details.map(d => ({
      field: d.path.join('.'),
      message: d.message
    }))
    
    return {
      success: false,
      error: 'VALIDATION_ERROR',
      errors
    }
  }
  
  // Add metadata
  value.createdAt = new Date()
  value.updatedAt = new Date()
  
  // Hash password before storing
  value.password = await hashPassword(value.password)
  
  try {
    const result = await db.collection('users').insertOne(value)
    return { success: true, id: result.insertedId }
  } catch (dbError) {
    // Handle MongoDB validation errors
    if (dbError.code === 11000) {
      return {
        success: false,
        error: 'DUPLICATE_KEY',
        message: 'Email already exists'
      }
    }
    throw dbError
  }
}
```

### Python Validation with Pydantic

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import re

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

class Address(BaseModel):
    street: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    state: Optional[str] = None
    postal_code: str = Field(..., alias='postalCode')
    country: str = Field(..., min_length=2, max_length=2)
    
    class Config:
        populate_by_name = True

class UserPreferences(BaseModel):
    newsletter: bool = False
    theme: str = Field(default='system', pattern='^(light|dark|system)$')

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50, alias='firstName')
    last_name: str = Field(..., min_length=1, max_length=50, alias='lastName')
    phone: Optional[str] = None
    address: Optional[Address] = None
    preferences: UserPreferences = UserPreferences()
    
    @validator('password')
    def password_strength(cls, v):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])', v):
            raise ValueError(
                'Password must contain uppercase, lowercase, number, and special character'
            )
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    class Config:
        populate_by_name = True

class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    email: str
    password_hash: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[Address] = None
    preferences: UserPreferences
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Usage
async def create_user(db, user_data: dict):
    try:
        # Validate input
        user = UserCreate(**user_data)
        
        # Convert to DB model
        db_user = {
            'email': user.email.lower(),
            'password_hash': hash_password(user.password),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'address': user.address.dict() if user.address else None,
            'preferences': user.preferences.dict(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = await db.users.insert_one(db_user)
        return {'success': True, 'id': str(result.inserted_id)}
        
    except ValidationError as e:
        return {
            'success': False,
            'error': 'VALIDATION_ERROR',
            'errors': e.errors()
        }
```

### Validation Middleware Pattern

```javascript
// Validation middleware factory
function validateBody(schema) {
  return async (req, res, next) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false,
      stripUnknown: true
    })
    
    if (error) {
      return res.status(400).json({
        error: 'VALIDATION_ERROR',
        message: 'Request body validation failed',
        details: error.details.map(d => ({
          field: d.path.join('.'),
          message: d.message
        }))
      })
    }
    
    req.validatedBody = value
    next()
  }
}

// Schema definitions
const schemas = {
  createUser: Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().min(8).required(),
    name: Joi.string().min(2).required()
  }),
  
  updateUser: Joi.object({
    email: Joi.string().email(),
    name: Joi.string().min(2)
  }).min(1)  // At least one field required
}

// Usage in routes
app.post('/users', 
  validateBody(schemas.createUser),
  async (req, res) => {
    const result = await userService.create(req.validatedBody)
    res.json(result)
  }
)

app.patch('/users/:id',
  validateBody(schemas.updateUser),
  async (req, res) => {
    const result = await userService.update(req.params.id, req.validatedBody)
    res.json(result)
  }
)
```

---

## Summary

### Validation Comparison

| Feature | MongoDB JSON Schema | Application (Joi/Pydantic) |
|---------|---------------------|----------------------------|
| Enforcement | Database level | Application level |
| Flexibility | Limited | High |
| Error messages | Basic | Customizable |
| Cross-field | Via $expr | Native support |
| Async validation | No | Yes |
| Custom rules | Limited | Unlimited |
| Performance | Faster | Adds overhead |

### Best Practices

| Practice | Description |
|----------|-------------|
| Dual validation | Use both application and DB validation |
| Strict in dev | Use `validationAction: "error"` in development |
| Moderate for migration | Use `validationLevel: "moderate"` during schema changes |
| Clear error messages | Provide descriptive `description` fields |
| Test validation | Unit test validation rules |
| Version schemas | Track schema changes over time |

### Common Patterns

```javascript
// Pattern: Validation helper function
async function validateAndInsert(collection, schema, document) {
  // Application-level validation
  const { error, value } = schema.validate(document)
  if (error) {
    return { success: false, errors: error.details }
  }
  
  try {
    // Database-level validation happens automatically
    const result = await collection.insertOne(value)
    return { success: true, id: result.insertedId }
  } catch (dbError) {
    if (dbError.code === 121) {
      return { success: false, error: 'DB_VALIDATION', message: dbError.message }
    }
    throw dbError
  }
}
```

---

## Practice Questions

1. What is the difference between `validationLevel: "strict"` and `"moderate"`?
2. How do you implement conditional validation based on field values?
3. What BSON types are available for schema validation?
4. How do you validate that an end date is after a start date?
5. When should you use application-level vs database-level validation?
6. How do you handle validation errors from bulk operations?
7. What is `additionalProperties` and when should you use it?
8. How do you update validation rules on an existing collection?

---

[← Previous: Error Handling](68-error-handling.md) | [Next: Data Migration →](70-data-migration.md)
