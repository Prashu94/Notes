# Chapter 30: Vector Search and Embeddings

## Learning Objectives
By the end of this chapter, you will:
- Understand vector embeddings and similarity search
- Configure Neo4j vector indexes
- Store and query vector embeddings
- Combine vector search with graph traversals
- Build semantic search applications

---

## 30.1 Introduction to Vector Search

### What are Embeddings?

Embeddings are dense numerical representations of data (text, images, etc.) in a continuous vector space where similar items are close together.

### Why Vector Search in Neo4j?

| Traditional Search | Vector Search |
|-------------------|---------------|
| Exact keyword match | Semantic similarity |
| Pattern matching | "Meaning" based |
| Limited to structure | Handles unstructured data |

### Use Cases

- **Semantic Search**: Find documents by meaning, not keywords
- **Recommendations**: Similar products/content
- **Question Answering**: Match questions to answers
- **Image Search**: Find similar images
- **RAG Systems**: Retrieve context for LLMs

---

## 30.2 Vector Indexes in Neo4j

### Creating a Vector Index

```cypher
// Create vector index
CREATE VECTOR INDEX movie_embeddings IF NOT EXISTS
FOR (m:Movie)
ON m.embedding
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
    }
}

// Alternative similarity functions
// cosine - for normalized vectors (most common)
// euclidean - for absolute distances
// dot_product - for magnitude-sensitive comparisons
```

### Index Configuration

```cypher
// Check existing vector indexes
SHOW INDEXES
YIELD name, type, labelsOrTypes, properties, options
WHERE type = 'VECTOR'
RETURN name, labelsOrTypes, properties, options

// Drop vector index
DROP INDEX movie_embeddings IF EXISTS
```

### Supported Dimensions

- Minimum: 1
- Maximum: 4096 (varies by version)
- Common: 384, 768, 1536 (depends on embedding model)

---

## 30.3 Storing Embeddings

### Creating Nodes with Embeddings

```cypher
// Store embedding as property
CREATE (m:Movie {
    title: 'The Matrix',
    year: 1999,
    embedding: [0.1, 0.2, 0.3, ...]  // 1536-dimensional vector
})

// Update existing node
MATCH (m:Movie {title: 'The Matrix'})
SET m.embedding = $embedding
```

### Batch Import Embeddings

```cypher
// Import from CSV with embeddings
LOAD CSV WITH HEADERS FROM 'file:///movies_with_embeddings.csv' AS row
CREATE (m:Movie {
    title: row.title,
    embedding: apoc.convert.fromJsonList(row.embedding)
})

// Using UNWIND for batch updates
UNWIND $movies AS movie
MATCH (m:Movie {title: movie.title})
SET m.embedding = movie.embedding
```

### Embedding Data Types

```cypher
// Embeddings must be lists of floats
// Valid
SET m.embedding = [0.1, 0.2, 0.3]

// Convert from string
SET m.embedding = apoc.convert.fromJsonList('[0.1, 0.2, 0.3]')

// Check embedding dimension
MATCH (m:Movie)
WHERE m.embedding IS NOT NULL
RETURN m.title, size(m.embedding) AS dimensions
LIMIT 5
```

---

## 30.4 Vector Similarity Search

### Basic Vector Search

```cypher
// Find similar movies using vector index
MATCH (m:Movie)
WHERE m.embedding IS NOT NULL
CALL db.index.vector.queryNodes(
    'movie_embeddings',
    10,
    $queryEmbedding
)
YIELD node, score
RETURN node.title AS movie, score
ORDER BY score DESC
```

### Search with Filters

```cypher
// Pre-filter then vector search
MATCH (m:Movie)
WHERE m.year >= 2000 AND m.embedding IS NOT NULL
WITH m
CALL db.index.vector.queryNodes(
    'movie_embeddings',
    10,
    $queryEmbedding
)
YIELD node, score
WHERE node = m
RETURN node.title, node.year, score
ORDER BY score DESC

// Post-filter vector results
CALL db.index.vector.queryNodes(
    'movie_embeddings',
    50,  // Get more results to filter
    $queryEmbedding
)
YIELD node, score
WHERE node.year >= 2000 AND node.rating > 7
RETURN node.title, node.year, node.rating, score
ORDER BY score DESC
LIMIT 10
```

### Hybrid Search (Vector + Graph)

```cypher
// Find similar movies and traverse to actors
CALL db.index.vector.queryNodes(
    'movie_embeddings',
    5,
    $queryEmbedding
)
YIELD node AS movie, score
MATCH (movie)<-[:ACTED_IN]-(actor:Person)
RETURN movie.title, score, collect(actor.name) AS actors
ORDER BY score DESC

// Find similar movies in user's preferred genres
MATCH (user:User {id: $userId})-[:PREFERS]->(genre:Genre)
WITH collect(genre) AS preferredGenres
CALL db.index.vector.queryNodes(
    'movie_embeddings',
    20,
    $queryEmbedding
)
YIELD node AS movie, score
MATCH (movie)-[:IN_GENRE]->(g:Genre)
WHERE g IN preferredGenres
RETURN movie.title, score, collect(g.name) AS genres
ORDER BY score DESC
LIMIT 10
```

---

## 30.5 Computing Similarity Manually

### Cosine Similarity

```cypher
// Manual cosine similarity calculation
MATCH (m1:Movie {title: 'The Matrix'}), (m2:Movie)
WHERE m1 <> m2 AND m2.embedding IS NOT NULL
WITH m1, m2,
     reduce(dot = 0.0, i IN range(0, size(m1.embedding)-1) | 
         dot + m1.embedding[i] * m2.embedding[i]) AS dotProduct,
     sqrt(reduce(sum = 0.0, x IN m1.embedding | sum + x*x)) AS norm1,
     sqrt(reduce(sum = 0.0, x IN m2.embedding | sum + x*x)) AS norm2
RETURN m2.title, 
       dotProduct / (norm1 * norm2) AS cosineSimilarity
ORDER BY cosineSimilarity DESC
LIMIT 10

// Using GDS function
MATCH (m1:Movie {title: 'The Matrix'}), (m2:Movie)
WHERE m1 <> m2 AND m2.embedding IS NOT NULL
RETURN m2.title,
       gds.similarity.cosine(m1.embedding, m2.embedding) AS similarity
ORDER BY similarity DESC
LIMIT 10
```

### Euclidean Distance

```cypher
// Manual Euclidean distance
MATCH (m1:Movie {title: 'The Matrix'}), (m2:Movie)
WHERE m1 <> m2 AND m2.embedding IS NOT NULL
WITH m1, m2,
     sqrt(reduce(sum = 0.0, i IN range(0, size(m1.embedding)-1) | 
         sum + (m1.embedding[i] - m2.embedding[i])^2)) AS distance
RETURN m2.title, distance
ORDER BY distance ASC
LIMIT 10

// Using GDS function
RETURN gds.similarity.euclidean([1,2,3], [4,5,6]) AS euclideanSimilarity
```

---

## 30.6 Generating Embeddings

### Using OpenAI Embeddings

```python
import openai
from neo4j import GraphDatabase

# Generate embedding
def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    response = openai.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

# Store in Neo4j
def store_embedding(driver, title: str, description: str):
    embedding = get_embedding(description)
    
    with driver.session() as session:
        session.run("""
            MATCH (m:Movie {title: $title})
            SET m.embedding = $embedding,
                m.embeddingModel = 'text-embedding-3-small'
        """, title=title, embedding=embedding)
```

### Using Sentence Transformers

```python
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

def generate_embeddings(texts: list) -> list:
    return model.encode(texts).tolist()

# Batch process movies
def embed_movies(driver):
    with driver.session() as session:
        # Get movies without embeddings
        result = session.run("""
            MATCH (m:Movie)
            WHERE m.embedding IS NULL
            RETURN m.title AS title, m.description AS description
            LIMIT 100
        """)
        
        movies = [dict(r) for r in result]
        
        # Generate embeddings
        texts = [m['description'] for m in movies]
        embeddings = generate_embeddings(texts)
        
        # Store embeddings
        for movie, embedding in zip(movies, embeddings):
            session.run("""
                MATCH (m:Movie {title: $title})
                SET m.embedding = $embedding
            """, title=movie['title'], embedding=embedding)
```

### Using Hugging Face

```python
from transformers import AutoTokenizer, AutoModel
import torch

model_name = 'sentence-transformers/all-mpnet-base-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text: str) -> list:
    inputs = tokenizer(text, return_tensors='pt', 
                       truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Mean pooling
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].tolist()
```

---

## 30.7 Vector Index Maintenance

### Updating Embeddings

```cypher
// Re-embed when content changes
MATCH (m:Movie {title: 'The Matrix'})
SET m.embedding = $newEmbedding,
    m.embeddingUpdated = datetime()

// Track embedding versions
MATCH (m:Movie {title: 'The Matrix'})
SET m.embeddingVersion = 2,
    m.embeddingModel = 'text-embedding-3-large'
```

### Monitoring Vector Index

```cypher
// Check index status
SHOW INDEXES
YIELD name, state, populationPercent
WHERE name = 'movie_embeddings'
RETURN *

// Index statistics
CALL db.index.vector.queryNodes.estimate('movie_embeddings')
```

---

## 30.8 Advanced Patterns

### Multi-Modal Search

```cypher
// Search with both text and image embeddings
CREATE VECTOR INDEX product_text_embeddings
FOR (p:Product) ON p.textEmbedding
OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}}

CREATE VECTOR INDEX product_image_embeddings
FOR (p:Product) ON p.imageEmbedding
OPTIONS {indexConfig: {`vector.dimensions`: 512, `vector.similarity_function`: 'cosine'}}

// Combined search
CALL db.index.vector.queryNodes('product_text_embeddings', 20, $textQuery)
YIELD node AS textMatch, score AS textScore
WITH collect({node: textMatch, score: textScore}) AS textResults
CALL db.index.vector.queryNodes('product_image_embeddings', 20, $imageQuery)
YIELD node AS imageMatch, score AS imageScore
WITH textResults, collect({node: imageMatch, score: imageScore}) AS imageResults
// Combine and rank results
UNWIND textResults + imageResults AS result
WITH result.node AS product, sum(result.score) AS combinedScore
RETURN product.name, combinedScore
ORDER BY combinedScore DESC
LIMIT 10
```

### Chunked Document Search

```cypher
// Store document chunks with parent reference
CREATE (d:Document {id: 'doc1', title: 'User Manual'})
CREATE (c1:Chunk {id: 'chunk1', text: '...', embedding: $emb1})
CREATE (c2:Chunk {id: 'chunk2', text: '...', embedding: $emb2})
CREATE (d)-[:HAS_CHUNK {position: 1}]->(c1)
CREATE (d)-[:HAS_CHUNK {position: 2}]->(c2)

// Search chunks, return parent documents
CALL db.index.vector.queryNodes('chunk_embeddings', 10, $query)
YIELD node AS chunk, score
MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)
RETURN doc.title, chunk.text, score
ORDER BY score DESC
```

### Contextual Search with Graph Context

```cypher
// Enrich search results with graph context
CALL db.index.vector.queryNodes('article_embeddings', 5, $query)
YIELD node AS article, score
// Get related articles
OPTIONAL MATCH (article)-[:REFERENCES]->(related:Article)
// Get authors
OPTIONAL MATCH (article)<-[:WROTE]-(author:Person)
// Get topics
OPTIONAL MATCH (article)-[:ABOUT]->(topic:Topic)
RETURN 
    article.title,
    score,
    collect(DISTINCT author.name) AS authors,
    collect(DISTINCT topic.name) AS topics,
    collect(DISTINCT related.title)[0..3] AS relatedArticles
ORDER BY score DESC
```

---

## 30.9 Python Integration

```python
from neo4j import GraphDatabase
from typing import List, Dict, Optional
import numpy as np

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class VectorSearchEngine:
    def __init__(self, uri, auth, embedding_func=None):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.embedding_func = embedding_func
    
    def close(self):
        self.driver.close()
    
    def create_vector_index(self, index_name: str, label: str,
                            property_name: str, dimensions: int,
                            similarity: str = 'cosine'):
        """Create a vector index."""
        with self.driver.session() as session:
            session.run(f"""
                CREATE VECTOR INDEX {index_name} IF NOT EXISTS
                FOR (n:{label})
                ON n.{property_name}
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {dimensions},
                        `vector.similarity_function`: '{similarity}'
                    }}
                }}
            """)
    
    def store_embedding(self, label: str, identifier: Dict,
                        embedding: List[float], properties: Dict = None):
        """Store embedding for a node."""
        with self.driver.session() as session:
            match_clause = ' AND '.join([f"n.{k} = ${k}" for k in identifier.keys()])
            set_clause = ', '.join([f"n.{k} = ${k}" for k in (properties or {}).keys()])
            
            query = f"""
                MATCH (n:{label})
                WHERE {match_clause}
                SET n.embedding = $embedding
                {', ' + set_clause if set_clause else ''}
            """
            
            params = {**identifier, 'embedding': embedding, **(properties or {})}
            session.run(query, params)
    
    def batch_store_embeddings(self, label: str, data: List[Dict]):
        """Batch store embeddings."""
        with self.driver.session() as session:
            session.run(f"""
                UNWIND $data AS item
                MATCH (n:{label} {{id: item.id}})
                SET n.embedding = item.embedding
            """, data=data)
    
    def semantic_search(self, index_name: str, query_text: str,
                        top_k: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform semantic search."""
        if not self.embedding_func:
            raise ValueError("Embedding function not provided")
        
        query_embedding = self.embedding_func(query_text)
        return self.vector_search(index_name, query_embedding, top_k, filters)
    
    def vector_search(self, index_name: str, query_embedding: List[float],
                      top_k: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform vector similarity search."""
        with self.driver.session() as session:
            if filters:
                filter_clause = ' AND '.join([f"node.{k} = ${k}" for k in filters.keys()])
                query = f"""
                    CALL db.index.vector.queryNodes($index, $k * 2, $embedding)
                    YIELD node, score
                    WHERE {filter_clause}
                    RETURN node, score
                    ORDER BY score DESC
                    LIMIT $k
                """
                params = {'index': index_name, 'k': top_k, 
                          'embedding': query_embedding, **filters}
            else:
                query = """
                    CALL db.index.vector.queryNodes($index, $k, $embedding)
                    YIELD node, score
                    RETURN node, score
                    ORDER BY score DESC
                """
                params = {'index': index_name, 'k': top_k, 
                          'embedding': query_embedding}
            
            result = session.run(query, params)
            return [{'node': dict(r['node']), 'score': r['score']} for r in result]
    
    def hybrid_search(self, index_name: str, query_embedding: List[float],
                      graph_expansion: str, top_k: int = 10) -> List[Dict]:
        """Vector search with graph traversal."""
        with self.driver.session() as session:
            query = f"""
                CALL db.index.vector.queryNodes($index, $k, $embedding)
                YIELD node, score
                {graph_expansion}
                RETURN node, score, related
                ORDER BY score DESC
            """
            
            result = session.run(query, index=index_name, k=top_k, 
                                 embedding=query_embedding)
            return [dict(r) for r in result]
    
    def find_similar_nodes(self, label: str, node_id: str,
                           index_name: str, top_k: int = 10) -> List[Dict]:
        """Find nodes similar to a given node."""
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (source:{label} {{id: $nodeId}})
                CALL db.index.vector.queryNodes($index, $k + 1, source.embedding)
                YIELD node, score
                WHERE node <> source
                RETURN node, score
                ORDER BY score DESC
                LIMIT $k
            """, nodeId=node_id, index=index_name, k=top_k)
            
            return [{'node': dict(r['node']), 'score': r['score']} for r in result]

# Usage with OpenAI
import openai

def openai_embedding(text: str) -> List[float]:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Initialize
engine = VectorSearchEngine(URI, AUTH, embedding_func=openai_embedding)

try:
    # Create index
    engine.create_vector_index('movie_embeddings', 'Movie', 
                               'embedding', 1536)
    
    # Semantic search
    results = engine.semantic_search(
        'movie_embeddings',
        "science fiction movie about artificial intelligence",
        top_k=5
    )
    
    print("Search Results:")
    for r in results:
        print(f"  {r['node'].get('title')}: {r['score']:.4f}")
    
    # Find similar to a specific movie
    similar = engine.find_similar_nodes('Movie', 'matrix_1999',
                                         'movie_embeddings', top_k=5)
    
    print("\nSimilar to The Matrix:")
    for s in similar:
        print(f"  {s['node'].get('title')}: {s['score']:.4f}")

finally:
    engine.close()
```

---

## Summary

### Vector Search Capabilities

| Feature | Description |
|---------|-------------|
| Vector Index | Native support for similarity search |
| Similarity Functions | Cosine, Euclidean, Dot Product |
| Hybrid Queries | Combine vectors with graph traversals |
| Filters | Pre/post filtering of results |

### Best Practices

1. **Choose right dimensions** for your embedding model
2. **Use cosine similarity** for normalized embeddings
3. **Combine with graph context** for richer results
4. **Batch embed** for efficiency
5. **Track embedding versions** when models change

---

## Exercises

### Exercise 30.1: Semantic Movie Search
1. Generate embeddings for movie descriptions
2. Create a vector index
3. Build a semantic search for movies

### Exercise 30.2: Hybrid Recommendations
1. Use vector similarity for initial candidates
2. Enhance with graph traversal
3. Personalize based on user preferences

### Exercise 30.3: Document QA System
1. Chunk documents and embed chunks
2. Search for relevant chunks
3. Return chunks with document context

---

**Next Chapter: [Chapter 31: RAG with Neo4j and LLMs](31-rag-with-llms.md)**
