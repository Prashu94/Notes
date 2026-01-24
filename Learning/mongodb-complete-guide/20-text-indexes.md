# Chapter 20: Text Indexes

## Table of Contents
- [Introduction to Text Indexes](#introduction-to-text-indexes)
- [Creating Text Indexes](#creating-text-indexes)
- [Text Search Queries](#text-search-queries)
- [Text Search Operators](#text-search-operators)
- [Text Score and Sorting](#text-score-and-sorting)
- [Language Support](#language-support)
- [Compound Text Indexes](#compound-text-indexes)
- [Wildcard Text Indexes](#wildcard-text-indexes)
- [Limitations and Alternatives](#limitations-and-alternatives)
- [Summary](#summary)

---

## Introduction to Text Indexes

Text indexes enable full-text search capabilities in MongoDB, allowing you to search for words and phrases within string content.

### Text Index Capabilities

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Text Index Features                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✓ Word Stemming                                                   │
│    • "running", "runs", "ran" → "run"                              │
│                                                                     │
│  ✓ Stop Words Removal                                              │
│    • Ignores: "the", "a", "an", "is", etc.                        │
│                                                                     │
│  ✓ Case Insensitive                                                │
│    • "MongoDB" matches "mongodb", "MONGODB"                        │
│                                                                     │
│  ✓ Diacritics Insensitive                                          │
│    • "café" matches "cafe"                                         │
│                                                                     │
│  ✓ Multiple Languages                                              │
│    • 15+ languages supported                                       │
│                                                                     │
│  ✓ Phrase Search                                                   │
│    • "\"exact phrase\"" matching                                   │
│                                                                     │
│  ✓ Negation                                                        │
│    • Exclude words with "-word"                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Creating Text Indexes

### Single Field Text Index

```javascript
// Create text index on single field
db.articles.createIndex({ content: "text" })

// With custom name
db.articles.createIndex(
  { content: "text" },
  { name: "content_text_index" }
)
```

### Multiple Fields Text Index

```javascript
// Text index on multiple fields
db.articles.createIndex({
  title: "text",
  content: "text",
  tags: "text"
})

// Note: Only ONE text index per collection allowed
```

### Weighted Fields

```javascript
// Assign different weights to fields
db.articles.createIndex(
  {
    title: "text",
    content: "text",
    tags: "text"
  },
  {
    weights: {
      title: 10,    // Title matches worth 10x
      content: 5,   // Content matches worth 5x
      tags: 1       // Tags default weight
    },
    name: "weighted_text_index"
  }
)

// Higher weight = higher relevance score for matches
```

### Text Index Options

```javascript
db.articles.createIndex(
  { content: "text" },
  {
    // Index name
    name: "content_text",
    
    // Language for stemming
    default_language: "english",
    
    // Field containing language per document
    language_override: "lang",
    
    // Text index version
    textIndexVersion: 3
  }
)
```

---

## Text Search Queries

### Basic Text Search

```javascript
// Setup
db.articles.insertMany([
  {
    title: "MongoDB Tutorial",
    content: "MongoDB is a NoSQL database that stores data in documents",
    tags: ["mongodb", "database", "tutorial"]
  },
  {
    title: "Introduction to Databases",
    content: "Databases are essential for storing and retrieving data",
    tags: ["database", "introduction"]
  },
  {
    title: "Node.js and MongoDB",
    content: "Learn how to use MongoDB with Node.js applications",
    tags: ["nodejs", "mongodb", "javascript"]
  }
])

db.articles.createIndex({ title: "text", content: "text", tags: "text" })

// Basic search
db.articles.find({ $text: { $search: "mongodb" } })

// Search multiple words (OR)
db.articles.find({ $text: { $search: "mongodb nodejs" } })
// Matches documents containing "mongodb" OR "nodejs"
```

### Phrase Search

```javascript
// Exact phrase search (wrap in escaped quotes)
db.articles.find({
  $text: { $search: "\"NoSQL database\"" }
})
// Only matches exact phrase "NoSQL database"

// Phrase with other terms
db.articles.find({
  $text: { $search: "tutorial \"NoSQL database\"" }
})
```

### Negation

```javascript
// Exclude words with minus sign
db.articles.find({
  $text: { $search: "database -mongodb" }
})
// Matches "database" but NOT "mongodb"

// Multiple exclusions
db.articles.find({
  $text: { $search: "database -mongodb -nodejs" }
})
```

### Combined Search

```javascript
// Complex search: phrase + word + negation
db.articles.find({
  $text: { $search: "\"NoSQL database\" tutorial -introduction" }
})
// Must have "NoSQL database" AND "tutorial"
// Must NOT have "introduction"
```

---

## Text Search Operators

### $text Operator

```javascript
// Full $text syntax
db.collection.find({
  $text: {
    $search: "search terms",
    $language: "english",           // Override default language
    $caseSensitive: false,          // Default: false
    $diacriticSensitive: false      // Default: false
  }
})
```

### Case Sensitive Search

```javascript
// Case sensitive search
db.articles.find({
  $text: {
    $search: "MongoDB",
    $caseSensitive: true
  }
})
// Only matches exact case "MongoDB"
```

### Diacritic Sensitive Search

```javascript
// Documents
db.places.insertMany([
  { name: "Café Paris" },
  { name: "Cafe Roma" },
  { name: "CAFÉ Berlin" }
])

db.places.createIndex({ name: "text" })

// Default: diacritic insensitive
db.places.find({ $text: { $search: "cafe" } })
// Matches all three

// Diacritic sensitive
db.places.find({
  $text: {
    $search: "café",
    $diacriticSensitive: true
  }
})
// Matches only "Café Paris" and "CAFÉ Berlin"
```

---

## Text Score and Sorting

### Text Score ($meta)

```javascript
// Get relevance score for each match
db.articles.find(
  { $text: { $search: "mongodb database" } },
  { score: { $meta: "textScore" } }
)

// Example result:
{
  "_id": 1,
  "title": "MongoDB Tutorial",
  "content": "...",
  "score": 2.5  // Relevance score
}
```

### Sorting by Score

```javascript
// Sort by relevance (highest first)
db.articles.find(
  { $text: { $search: "mongodb database tutorial" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })

// Descending relevance is default
// Higher score = more relevant
```

### Score Calculation

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Text Score Factors                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Score is affected by:                                             │
│                                                                     │
│  1. Term Frequency                                                 │
│     • More occurrences = higher score                              │
│                                                                     │
│  2. Field Weight                                                   │
│     • Weighted fields multiply score                               │
│                                                                     │
│  3. Number of Search Terms Matched                                 │
│     • More matches = higher score                                  │
│                                                                     │
│  4. Document Length                                                │
│     • Normalized by document length                                │
│                                                                     │
│  Example with weights { title: 10, content: 1 }:                   │
│  • "mongodb" in title: 10 × base_score                            │
│  • "mongodb" in content: 1 × base_score                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Language Support

### Supported Languages

```javascript
// Languages with stemming support
const languages = [
  "danish", "dutch", "english", "finnish", "french",
  "german", "hungarian", "italian", "norwegian",
  "portuguese", "romanian", "russian", "spanish",
  "swedish", "turkish"
]

// Special values
// "none" - no language-specific processing
```

### Per-Document Language

```javascript
// Set language per document
db.articles.insertMany([
  {
    title: "Hello World",
    content: "This is English content",
    language: "english"
  },
  {
    title: "Bonjour le Monde",
    content: "Ceci est du contenu en français",
    language: "french"
  },
  {
    title: "Hola Mundo",
    content: "Este es contenido en español",
    language: "spanish"
  }
])

// Create index with language_override
db.articles.createIndex(
  { title: "text", content: "text" },
  { language_override: "language" }
)

// Each document uses its specified language for stemming
```

### No Language Processing

```javascript
// Use "none" for technical content or identifiers
db.products.createIndex(
  { sku: "text", model: "text" },
  { default_language: "none" }
)

// No stemming: "ABC-123" stays "ABC-123"
```

---

## Compound Text Indexes

### Text with Other Fields

```javascript
// Compound index: regular field + text
db.products.createIndex({
  category: 1,           // Regular ascending index
  description: "text"    // Text index
})

// Query must include equality on prefix fields
db.products.find({
  category: "electronics",
  $text: { $search: "wireless bluetooth" }
})

// This won't efficiently use the index:
db.products.find({
  $text: { $search: "wireless bluetooth" }
})
// Missing category prefix
```

### Text Index with Sort

```javascript
// Compound: prefix + text + suffix
db.articles.createIndex({
  status: 1,
  content: "text",
  createdAt: -1
})

// Efficient query
db.articles.find({
  status: "published",
  $text: { $search: "mongodb tutorial" }
}).sort({ createdAt: -1 })
```

### Practical Example

```javascript
// E-commerce product search
db.products.createIndex({
  category: 1,
  brand: 1,
  name: "text",
  description: "text"
})

// Search within category and brand
db.products.find({
  category: "Laptops",
  brand: "Dell",
  $text: { $search: "gaming lightweight" }
})
```

---

## Wildcard Text Indexes

### Index All String Fields

```javascript
// Wildcard text index - index all string fields
db.content.createIndex({ "$**": "text" })

// Searches all string fields in document
db.content.find({ $text: { $search: "mongodb" } })
```

### Wildcard with Weights

```javascript
// Wildcard with specific weights
db.articles.createIndex(
  { "$**": "text" },
  {
    weights: {
      title: 10,
      "metadata.tags": 5
    }
  }
)
```

### When to Use Wildcard

```javascript
// Good for:
// - Heterogeneous documents
// - Unknown schema
// - Full document search

// Caution:
// - Larger index size
// - Slower index builds
// - May index unnecessary fields
```

---

## Limitations and Alternatives

### Text Index Limitations

```javascript
// 1. One text index per collection
db.collection.createIndex({ field1: "text" })
db.collection.createIndex({ field2: "text" })  // Error!

// 2. Cannot combine with other special indexes
// No: { location: "2dsphere", content: "text" }

// 3. Hint not supported for text queries
db.collection.find({ $text: { $search: "term" } }).hint("index")
// Error: hint not allowed with $text

// 4. No partial match (prefix search)
// "mong" won't match "mongodb"

// 5. $text in aggregation only as first stage
db.collection.aggregate([
  { $match: { $text: { $search: "term" } } },  // Must be first
  { $project: { ... } }
])
```

### Alternatives to Text Indexes

```javascript
// 1. Regular Expression (small datasets)
db.articles.find({ content: /mongodb/i })
// Flexible but slow without index

// 2. Atlas Search (MongoDB Atlas)
// Full Lucene-based search
// Fuzzy matching, autocomplete, facets
// Recommended for advanced search

// 3. External Search Engines
// Elasticsearch, Solr, Algolia
// For complex search requirements
```

### Regex vs Text Search

```javascript
// Regex: Partial match, no index (usually)
db.products.find({ name: /^lap/i })  // Prefix match works with index
db.products.find({ name: /laptop/i }) // Full scan

// Text: Word match, uses index
db.products.find({ $text: { $search: "laptop" } })  // Exact word
// Won't match "laptops" without stemming
```

---

## Summary

### Text Index Features

| Feature | Description |
|---------|-------------|
| **Stemming** | Reduces words to root form |
| **Stop Words** | Common words ignored |
| **Case Insensitive** | Default behavior |
| **Weights** | Prioritize fields |
| **Multi-language** | 15+ languages |

### Query Operators

| Operator | Description |
|----------|-------------|
| **$text** | Text search operator |
| **$search** | Search terms |
| **$language** | Language override |
| **$caseSensitive** | Enable case matching |
| **$meta: "textScore"** | Relevance score |

### What's Next?

In the next chapter, we'll explore Geospatial Indexes for location-based queries.

---

## Practice Questions

1. Why can you only have one text index per collection?
2. How do you search for an exact phrase?
3. What's the difference between case sensitive and insensitive search?
4. How do field weights affect text search results?
5. When would you use language_override?
6. How do you exclude words from text search?
7. What are the limitations of text search compared to full-text search engines?
8. When should you use a wildcard text index?

---

## Hands-On Exercises

### Exercise 1: Basic Text Search

```javascript
// Setup
db.text_articles.drop()
db.text_articles.insertMany([
  {
    title: "Getting Started with MongoDB",
    content: "MongoDB is a popular NoSQL database that stores data in flexible documents.",
    author: "John Doe",
    tags: ["mongodb", "database", "beginner"]
  },
  {
    title: "Advanced MongoDB Queries",
    content: "Learn about aggregation pipelines, complex queries, and optimization techniques.",
    author: "Jane Smith",
    tags: ["mongodb", "queries", "advanced"]
  },
  {
    title: "Introduction to NoSQL Databases",
    content: "NoSQL databases provide flexible schemas and horizontal scaling capabilities.",
    author: "Bob Wilson",
    tags: ["nosql", "database", "introduction"]
  },
  {
    title: "MongoDB vs PostgreSQL",
    content: "Comparing document databases with relational databases for different use cases.",
    author: "Alice Brown",
    tags: ["mongodb", "postgresql", "comparison"]
  }
])

// Create text index
db.text_articles.createIndex({
  title: "text",
  content: "text",
  tags: "text"
})

// Search for "mongodb"
print("Articles about MongoDB:")
db.text_articles.find({ $text: { $search: "mongodb" } })
  .forEach(doc => print("  -", doc.title))

// Search for phrase "NoSQL database"
print("\nArticles with 'NoSQL database' phrase:")
db.text_articles.find({ $text: { $search: "\"NoSQL database\"" } })
  .forEach(doc => print("  -", doc.title))

// Search with negation
print("\nArticles about database but not postgresql:")
db.text_articles.find({ $text: { $search: "database -postgresql" } })
  .forEach(doc => print("  -", doc.title))
```

### Exercise 2: Weighted Text Search

```javascript
// Drop and recreate with weights
db.text_articles.dropIndexes()

db.text_articles.createIndex(
  {
    title: "text",
    content: "text",
    tags: "text"
  },
  {
    weights: {
      title: 10,
      tags: 5,
      content: 1
    }
  }
)

// Search and show scores
print("Search results with scores:")
db.text_articles.find(
  { $text: { $search: "mongodb database" } },
  { score: { $meta: "textScore" }, title: 1 }
).sort({ score: { $meta: "textScore" } })
  .forEach(doc => {
    print(`  ${doc.score.toFixed(2)}: ${doc.title}`)
  })
```

### Exercise 3: Multi-language Search

```javascript
// Setup
db.text_multilang.drop()
db.text_multilang.insertMany([
  {
    title: "Learning English",
    content: "English is a widely spoken language around the world",
    lang: "english"
  },
  {
    title: "Aprender Español",
    content: "El español es un idioma hermoso con muchos hablantes",
    lang: "spanish"
  },
  {
    title: "Apprendre le Français",
    content: "Le français est parlé dans de nombreux pays",
    lang: "french"
  }
])

// Create index with language override
db.text_multilang.createIndex(
  { title: "text", content: "text" },
  { language_override: "lang" }
)

// Search in English
print("Search 'language':")
db.text_multilang.find({ $text: { $search: "language" } })
  .forEach(doc => print("  -", doc.title))

// Search in Spanish (stemming applies)
print("\nSearch 'idioma':")
db.text_multilang.find({ $text: { $search: "idioma" } })
  .forEach(doc => print("  -", doc.title))
```

### Exercise 4: Compound Text Index

```javascript
// Setup
db.text_products.drop()
db.text_products.insertMany([
  {
    category: "Electronics",
    brand: "Sony",
    name: "Wireless Headphones",
    description: "High quality wireless headphones with noise cancellation"
  },
  {
    category: "Electronics",
    brand: "Apple",
    name: "AirPods Pro",
    description: "Wireless earbuds with active noise cancellation"
  },
  {
    category: "Electronics",
    brand: "Samsung",
    name: "Galaxy Buds",
    description: "Wireless earbuds with premium sound quality"
  },
  {
    category: "Audio",
    brand: "Bose",
    name: "QuietComfort Headphones",
    description: "Premium wireless headphones with superior noise cancellation"
  }
])

// Create compound text index
db.text_products.createIndex({
  category: 1,
  brand: 1,
  name: "text",
  description: "text"
})

// Search within category
print("Electronics with 'wireless':")
db.text_products.find({
  category: "Electronics",
  $text: { $search: "wireless" }
}).forEach(doc => print(`  - ${doc.brand} ${doc.name}`))

// Search within category and brand
print("\nSony products with 'noise':")
db.text_products.find({
  category: "Electronics",
  brand: "Sony",
  $text: { $search: "noise" }
}).forEach(doc => print(`  - ${doc.name}`))
```

### Exercise 5: Text Search in Aggregation

```javascript
// Search with aggregation pipeline
print("Search with aggregation:")
db.text_articles.aggregate([
  // Text search must be first stage
  {
    $match: { $text: { $search: "mongodb" } }
  },
  // Add text score
  {
    $addFields: {
      score: { $meta: "textScore" }
    }
  },
  // Sort by score
  {
    $sort: { score: -1 }
  },
  // Project specific fields
  {
    $project: {
      title: 1,
      author: 1,
      score: 1,
      _id: 0
    }
  }
]).forEach(doc => {
  print(`  ${doc.score.toFixed(2)}: "${doc.title}" by ${doc.author}`)
})
```

---

[← Previous: Multikey Indexes](19-multikey-indexes.md) | [Next: Geospatial Indexes →](21-geospatial-indexes.md)
