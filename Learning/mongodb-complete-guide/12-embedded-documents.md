# Chapter 12: Embedded Documents

## Table of Contents
- [Embedded Documents Overview](#embedded-documents-overview)
- [Creating Embedded Documents](#creating-embedded-documents)
- [Querying Embedded Documents](#querying-embedded-documents)
- [Updating Embedded Documents](#updating-embedded-documents)
- [Embedded Arrays](#embedded-arrays)
- [Deeply Nested Documents](#deeply-nested-documents)
- [Indexing Embedded Documents](#indexing-embedded-documents)
- [Best Practices](#best-practices)
- [Summary](#summary)

---

## Embedded Documents Overview

Embedded documents (subdocuments) are documents nested within other documents, allowing you to store related data together in a single document.

### Structure

```javascript
// Document with embedded documents
{
  _id: ObjectId("..."),
  name: "John Doe",
  email: "john@example.com",
  
  // Single embedded document
  address: {
    street: "123 Main St",
    city: "New York",
    state: "NY",
    zipCode: "10001",
    country: "USA"
  },
  
  // Array of embedded documents
  phones: [
    { type: "home", number: "555-1234" },
    { type: "mobile", number: "555-5678" },
    { type: "work", number: "555-9012" }
  ]
}
```

### Benefits and Trade-offs

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Embedded Documents Characteristics                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✓ Benefits:                                                       │
│  • Atomic updates - entire document updated atomically             │
│  • Read performance - single query retrieves all data              │
│  • Data locality - related data stored together on disk            │
│  • Reduced complexity - no joins required                          │
│  • Schema flexibility - subdocuments can vary                      │
│                                                                     │
│  ✗ Trade-offs:                                                     │
│  • Document size limit (16MB)                                      │
│  • Duplication if embedded data shared                             │
│  • Complex updates for deeply nested data                          │
│  • Array growth can fragment documents                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Creating Embedded Documents

### Insert with Embedded Documents

```javascript
// Insert document with embedded subdocument
db.users.insertOne({
  name: "Alice Smith",
  email: "alice@example.com",
  profile: {
    avatar: "https://example.com/avatar.jpg",
    bio: "Software developer",
    location: {
      city: "San Francisco",
      country: "USA"
    }
  },
  createdAt: new Date()
})

// Insert with embedded array
db.products.insertOne({
  name: "Laptop",
  sku: "LAP001",
  price: 999.99,
  specifications: [
    { name: "CPU", value: "Intel i7" },
    { name: "RAM", value: "16GB" },
    { name: "Storage", value: "512GB SSD" },
    { name: "Display", value: "15.6 inch" }
  ],
  variants: [
    { color: "Silver", sku: "LAP001-S", stock: 50 },
    { color: "Black", sku: "LAP001-B", stock: 30 }
  ]
})
```

### Creating Embedded Documents with Update

```javascript
// Add embedded document to existing document
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $set: {
      address: {
        street: "456 Oak Ave",
        city: "Boston",
        state: "MA",
        zipCode: "02101"
      }
    }
  }
)

// Add to embedded array
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $push: {
      phones: { type: "work", number: "555-1111" }
    }
  }
)
```

---

## Querying Embedded Documents

### Dot Notation for Nested Fields

```javascript
// Query by embedded field value
db.users.find({ "address.city": "New York" })

// Query deeply nested field
db.users.find({ "profile.location.country": "USA" })

// Multiple conditions on embedded document
db.users.find({
  "address.city": "New York",
  "address.state": "NY"
})

// Comparison operators on embedded fields
db.products.find({
  "variants.stock": { $gt: 20 }
})
```

### Exact Subdocument Match

```javascript
// Exact match (order and fields must match exactly)
db.users.find({
  address: {
    street: "123 Main St",
    city: "New York",
    state: "NY",
    zipCode: "10001"
    // Must include ALL fields in exact order
  }
})

// Usually prefer dot notation for flexibility
db.users.find({
  "address.street": "123 Main St",
  "address.city": "New York"
})
```

### Querying Arrays of Embedded Documents

```javascript
// Sample data
db.orders.insertOne({
  orderId: "ORD001",
  items: [
    { product: "Laptop", qty: 1, price: 999 },
    { product: "Mouse", qty: 2, price: 25 },
    { product: "Keyboard", qty: 1, price: 75 }
  ]
})

// Match any array element
db.orders.find({ "items.product": "Laptop" })

// Match with $elemMatch (multiple conditions on same element)
db.orders.find({
  items: {
    $elemMatch: {
      product: "Mouse",
      qty: { $gte: 2 }
    }
  }
})

// Without $elemMatch (conditions can match different elements)
db.orders.find({
  "items.product": "Laptop",
  "items.qty": { $gte: 2 }
})
// This matches if ANY item is "Laptop" AND ANY item has qty >= 2
```

### Projection with Embedded Documents

```javascript
// Include specific embedded fields
db.users.find(
  { "address.city": "New York" },
  { 
    name: 1,
    "address.city": 1,
    "address.state": 1
  }
)

// Exclude embedded document
db.users.find(
  {},
  { profile: 0 }
)

// Project array element ($slice)
db.orders.find(
  { orderId: "ORD001" },
  { 
    orderId: 1,
    items: { $slice: 2 }  // First 2 items
  }
)

// Project matching array elements ($elemMatch projection)
db.orders.find(
  { "items.product": "Laptop" },
  {
    orderId: 1,
    items: { $elemMatch: { product: "Laptop" } }
  }
)

// Project first matching element ($)
db.orders.find(
  { "items.product": "Laptop" },
  { "items.$": 1 }
)
```

---

## Updating Embedded Documents

### Update Single Embedded Field

```javascript
// Update nested field using dot notation
db.users.updateOne(
  { _id: ObjectId("...") },
  { $set: { "address.city": "Brooklyn" } }
)

// Update multiple nested fields
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $set: {
      "address.city": "Brooklyn",
      "address.zipCode": "11201",
      "profile.location.city": "Brooklyn"
    }
  }
)
```

### Replace Entire Embedded Document

```javascript
// Replace entire subdocument
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $set: {
      address: {
        street: "789 New St",
        city: "Chicago",
        state: "IL",
        zipCode: "60601"
      }
    }
  }
)
```

### Update Array Elements

```javascript
// Update first matching array element ($)
db.orders.updateOne(
  { orderId: "ORD001", "items.product": "Mouse" },
  { $set: { "items.$.qty": 3 } }
)

// Update all array elements ($[])
db.orders.updateOne(
  { orderId: "ORD001" },
  { $inc: { "items.$[].qty": 1 } }  // Increment all quantities
)

// Update matching array elements ($[identifier])
db.orders.updateOne(
  { orderId: "ORD001" },
  { $set: { "items.$[elem].discounted": true } },
  { arrayFilters: [{ "elem.price": { $lt: 100 } }] }
)

// Update by array index
db.orders.updateOne(
  { orderId: "ORD001" },
  { $set: { "items.0.qty": 5 } }  // Update first item
)
```

### Add and Remove Array Elements

```javascript
// Add to array
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $push: {
      phones: { type: "fax", number: "555-9999" }
    }
  }
)

// Add multiple elements
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $push: {
      phones: {
        $each: [
          { type: "fax", number: "555-9999" },
          { type: "backup", number: "555-0000" }
        ]
      }
    }
  }
)

// Add unique only ($addToSet)
db.products.updateOne(
  { sku: "LAP001" },
  {
    $addToSet: {
      tags: "sale"  // Only adds if not already present
    }
  }
)

// Remove from array
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $pull: {
      phones: { type: "fax" }
    }
  }
)

// Remove by condition
db.orders.updateOne(
  { orderId: "ORD001" },
  {
    $pull: {
      items: { qty: { $lte: 0 } }
    }
  }
)
```

---

## Embedded Arrays

### Managing Array Size

```javascript
// Add with size limit using $slice
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $push: {
      recentActivity: {
        $each: [{ action: "login", date: new Date() }],
        $slice: -10  // Keep last 10 only
      }
    }
  }
)

// Add and sort
db.leaderboard.updateOne(
  { gameId: "game001" },
  {
    $push: {
      topScores: {
        $each: [{ player: "Alice", score: 9500 }],
        $sort: { score: -1 },
        $slice: 100  // Keep top 100
      }
    }
  }
)
```

### Working with Array Positions

```javascript
// Insert at specific position
db.playlists.updateOne(
  { _id: ObjectId("...") },
  {
    $push: {
      songs: {
        $each: [{ title: "New Song", artist: "Artist" }],
        $position: 0  // Insert at beginning
      }
    }
  }
)

// Remove first element
db.playlists.updateOne(
  { _id: ObjectId("...") },
  { $pop: { songs: -1 } }  // -1 = first, 1 = last
)

// Remove last element
db.playlists.updateOne(
  { _id: ObjectId("...") },
  { $pop: { songs: 1 } }
)
```

### Querying Array Size

```javascript
// Exact size match
db.users.find({ phones: { $size: 3 } })

// Size greater than (requires $expr or workaround)
db.users.find({
  $expr: { $gt: [{ $size: "$phones" }, 2] }
})

// Has at least one element
db.users.find({ "phones.0": { $exists: true } })

// Check specific index exists
db.users.find({ "phones.2": { $exists: true } })  // Has at least 3
```

---

## Deeply Nested Documents

### Creating Deep Nesting

```javascript
// Deeply nested structure
db.companies.insertOne({
  name: "Acme Corp",
  headquarters: {
    address: {
      building: {
        name: "Acme Tower",
        floor: 25,
        suite: "A"
      },
      street: "100 Corporate Blvd",
      city: "San Francisco"
    },
    contact: {
      phone: "555-1234",
      email: "hq@acme.com"
    }
  },
  departments: [
    {
      name: "Engineering",
      teams: [
        {
          name: "Backend",
          members: [
            { name: "Alice", role: "Lead" },
            { name: "Bob", role: "Developer" }
          ]
        },
        {
          name: "Frontend",
          members: [
            { name: "Charlie", role: "Lead" }
          ]
        }
      ]
    }
  ]
})
```

### Querying Deep Nesting

```javascript
// Query deeply nested field
db.companies.find({
  "headquarters.address.building.floor": 25
})

// Query nested array element
db.companies.find({
  "departments.teams.name": "Backend"
})

// Query with $elemMatch for precision
db.companies.find({
  departments: {
    $elemMatch: {
      name: "Engineering",
      teams: {
        $elemMatch: {
          name: "Backend",
          "members.name": "Alice"
        }
      }
    }
  }
})
```

### Updating Deep Nesting

```javascript
// Update deeply nested field
db.companies.updateOne(
  { name: "Acme Corp" },
  { $set: { "headquarters.address.building.floor": 26 } }
)

// Update nested array element
db.companies.updateOne(
  {
    name: "Acme Corp",
    "departments.teams.members.name": "Alice"
  },
  {
    $set: { "departments.$[dept].teams.$[team].members.$[member].role": "Senior Lead" }
  },
  {
    arrayFilters: [
      { "dept.name": "Engineering" },
      { "team.name": "Backend" },
      { "member.name": "Alice" }
    ]
  }
)
```

### Nesting Limitations

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Deep Nesting Considerations                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Practical Limits:                                                  │
│  • Max nesting depth: 100 levels (theoretical)                     │
│  • Recommended: Keep nesting to 3-4 levels                         │
│  • Document size: 16MB total                                       │
│                                                                     │
│  Challenges with Deep Nesting:                                     │
│  • Complex update syntax with array filters                        │
│  • Index limitations on nested arrays                              │
│  • Difficult to query specific nested elements                     │
│  • Harder to maintain and understand                               │
│                                                                     │
│  Recommendation:                                                    │
│  If nesting > 3 levels, consider:                                  │
│  • Flattening the structure                                        │
│  • Using references instead                                        │
│  • Restructuring your data model                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Indexing Embedded Documents

### Index on Embedded Field

```javascript
// Index single embedded field
db.users.createIndex({ "address.city": 1 })

// Compound index with embedded fields
db.users.createIndex({ 
  "address.city": 1, 
  "address.state": 1 
})

// Query uses the index
db.users.find({ "address.city": "New York" })
```

### Index on Embedded Arrays (Multikey Index)

```javascript
// Index on array field (creates multikey index)
db.products.createIndex({ "tags": 1 })

// Index on embedded array field
db.products.createIndex({ "specifications.name": 1 })

// Index for efficient array element queries
db.orders.createIndex({ "items.product": 1 })

// Compound multikey index
db.orders.createIndex({ 
  "items.product": 1, 
  "items.qty": 1 
})

// Note: Only one array field per compound index can be multikey
```

### Wildcard Indexes for Dynamic Embedded Documents

```javascript
// Wildcard index for all fields in embedded document
db.products.createIndex({ "attributes.$**": 1 })

// Useful when embedded document structure varies
db.products.insertMany([
  {
    name: "Shirt",
    attributes: { size: "M", color: "blue", material: "cotton" }
  },
  {
    name: "Electronics",
    attributes: { voltage: "110V", wattage: "500W" }
  }
])

// Both queries use the wildcard index
db.products.find({ "attributes.size": "M" })
db.products.find({ "attributes.voltage": "110V" })
```

---

## Best Practices

### 1. Keep Embedding Shallow

```javascript
// ❌ Too deeply nested
{
  level1: {
    level2: {
      level3: {
        level4: {
          level5: { data: "too deep" }
        }
      }
    }
  }
}

// ✓ Flatter structure
{
  category: "Electronics",
  subcategory: "Phones",
  type: "Smartphone",
  specs: { ram: "8GB", storage: "256GB" }
}
```

### 2. Control Array Growth

```javascript
// ❌ Unbounded array growth
{
  userId: 1,
  activities: []  // Can grow forever
}

// ✓ Bounded with $slice or separate collection
{
  userId: 1,
  recentActivities: []  // Keep last N
}

// Or use separate collection for large/unbounded arrays
db.activities.insertOne({
  userId: 1,
  action: "login",
  timestamp: new Date()
})
```

### 3. Embed for Query Patterns

```javascript
// If you always need user with address, embed
{
  name: "John",
  address: { city: "NYC", state: "NY" }
}

// If you sometimes need address independently, reference
{
  name: "John",
  addressId: ObjectId("...")
}
```

### 4. Consider Update Frequency

```javascript
// Embed when subdocument updates with parent
{
  order: {
    shippingAddress: { ... }  // Specific to this order
  }
}

// Reference when data changes independently
{
  order: {
    customerId: ObjectId("...")  // Customer info may change
  }
}
```

### 5. Use Appropriate Projections

```javascript
// Avoid returning large embedded arrays unnecessarily
db.posts.find(
  { authorId: userId },
  { 
    title: 1,
    excerpt: 1,
    // Don't include comments array
    comments: 0
  }
)

// Use $slice for arrays
db.posts.find(
  { _id: postId },
  {
    title: 1,
    comments: { $slice: -10 }  // Last 10 comments only
  }
)
```

---

## Summary

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Embedded Document** | Document nested within another document |
| **Dot Notation** | Access nested fields with `parent.child.field` |
| **Multikey Index** | Index on array fields |
| **$elemMatch** | Match multiple conditions on same array element |
| **Array Filters** | Target specific elements in nested updates |

### When to Embed

| Embed When | Avoid Embedding When |
|------------|---------------------|
| Data accessed together | Data grows unbounded |
| One-to-one relationship | Data shared across documents |
| One-to-few relationship | Independent access needed |
| Data changes with parent | Frequent independent updates |

### What's Next?

In the next chapter, we'll explore References and Joins using $lookup.

---

## Practice Questions

1. How do you query an embedded document field using dot notation?
2. What's the difference between exact subdocument match and dot notation query?
3. When should you use $elemMatch vs regular dot notation for arrays?
4. How do you update a specific element in a nested array?
5. What are the limitations of multikey indexes?
6. How do you control array growth in embedded documents?
7. What's the maximum nesting depth recommended for embedded documents?
8. How do wildcard indexes help with dynamic embedded documents?

---

## Hands-On Exercises

### Exercise 1: Create and Query Embedded Documents

```javascript
// Create a document with embedded structure
db.employees.insertOne({
  name: "Sarah Johnson",
  email: "sarah@company.com",
  department: "Engineering",
  contact: {
    phone: "555-1234",
    address: {
      street: "123 Tech Way",
      city: "Seattle",
      state: "WA",
      zip: "98101"
    }
  },
  skills: [
    { name: "JavaScript", level: "Expert", years: 8 },
    { name: "Python", level: "Intermediate", years: 4 },
    { name: "MongoDB", level: "Expert", years: 5 }
  ],
  projects: [
    { name: "Project Alpha", role: "Lead", status: "completed" },
    { name: "Project Beta", role: "Developer", status: "active" }
  ]
})

// Query exercises:

// 1. Find employees in Seattle
db.employees.find({ "contact.address.city": "Seattle" })

// 2. Find employees with expert JavaScript skills
db.employees.find({
  skills: {
    $elemMatch: { name: "JavaScript", level: "Expert" }
  }
})

// 3. Find employees leading active projects
db.employees.find({
  projects: {
    $elemMatch: { role: "Lead", status: "active" }
  }
})
```

### Exercise 2: Update Embedded Documents

```javascript
// Using the employee document from Exercise 1

// 1. Update the city to "Bellevue"
db.employees.updateOne(
  { name: "Sarah Johnson" },
  { $set: { "contact.address.city": "Bellevue" } }
)

// 2. Add a new skill
db.employees.updateOne(
  { name: "Sarah Johnson" },
  {
    $push: {
      skills: { name: "Go", level: "Beginner", years: 1 }
    }
  }
)

// 3. Update Python skill to Advanced
db.employees.updateOne(
  { name: "Sarah Johnson", "skills.name": "Python" },
  { $set: { "skills.$.level": "Advanced" } }
)

// 4. Mark Project Alpha as archived
db.employees.updateOne(
  { name: "Sarah Johnson" },
  { $set: { "projects.$[proj].status": "archived" } },
  { arrayFilters: [{ "proj.name": "Project Alpha" }] }
)
```

### Exercise 3: Work with Embedded Arrays

```javascript
// Create a shopping cart document
db.carts.insertOne({
  userId: ObjectId("..."),
  items: [
    { productId: "P001", name: "Laptop", price: 999, qty: 1 },
    { productId: "P002", name: "Mouse", price: 29, qty: 2 },
    { productId: "P003", name: "Keyboard", price: 79, qty: 1 }
  ],
  updatedAt: new Date()
})

// 1. Add a new item to the cart
db.carts.updateOne(
  { userId: ObjectId("...") },
  {
    $push: { items: { productId: "P004", name: "Monitor", price: 299, qty: 1 } },
    $set: { updatedAt: new Date() }
  }
)

// 2. Update quantity of Mouse to 3
db.carts.updateOne(
  { userId: ObjectId("..."), "items.productId": "P002" },
  {
    $set: { "items.$.qty": 3 },
    $set: { updatedAt: new Date() }
  }
)

// 3. Remove item with price less than 50
db.carts.updateOne(
  { userId: ObjectId("...") },
  {
    $pull: { items: { price: { $lt: 50 } } },
    $set: { updatedAt: new Date() }
  }
)

// 4. Calculate total (using aggregation)
db.carts.aggregate([
  { $match: { userId: ObjectId("...") } },
  { $unwind: "$items" },
  {
    $group: {
      _id: "$_id",
      total: { $sum: { $multiply: ["$items.price", "$items.qty"] } }
    }
  }
])
```

### Exercise 4: Indexing Practice

```javascript
// Create indexes for embedded documents
db.products.createIndex({ "specifications.name": 1, "specifications.value": 1 })
db.products.createIndex({ "variants.sku": 1 }, { unique: true })
db.products.createIndex({ "categories.name": 1 })

// Insert sample data
db.products.insertMany([
  {
    name: "Gaming Laptop",
    specifications: [
      { name: "CPU", value: "Intel i9" },
      { name: "RAM", value: "32GB" },
      { name: "GPU", value: "RTX 4090" }
    ],
    variants: [
      { sku: "GL001-B", color: "Black", stock: 10 },
      { sku: "GL001-S", color: "Silver", stock: 5 }
    ],
    categories: [
      { name: "Electronics", path: "/electronics" },
      { name: "Computers", path: "/electronics/computers" }
    ]
  }
])

// Queries using indexes
db.products.find({ "specifications.name": "CPU", "specifications.value": "Intel i9" })
db.products.find({ "variants.sku": "GL001-B" })
db.products.find({ "categories.name": "Electronics" })

// Check index usage
db.products.find({ "specifications.name": "CPU" }).explain("executionStats")
```

---

[← Previous: Data Modeling Concepts](11-data-modeling-concepts.md) | [Next: References and Joins →](13-references-and-joins.md)
