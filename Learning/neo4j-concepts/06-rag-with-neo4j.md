# RAG with Neo4j and LangChain - Complete Guide

## Table of Contents
1. [Introduction to RAG](#introduction-to-rag)
2. [Why Neo4j for RAG?](#why-neo4j-for-rag)
3. [RAG Architecture](#rag-architecture)
4. [Setup and Installation](#setup-and-installation)
5. [Vector Search in Neo4j](#vector-search-in-neo4j)
6. [Graph-Based RAG](#graph-based-rag)
7. [Hybrid Search Strategies](#hybrid-search-strategies)
8. [LangChain Integration](#langchain-integration)

---

## Introduction to RAG

### What is RAG?

**RAG (Retrieval Augmented Generation)** is a technique that enhances Large Language Models (LLMs) by retrieving relevant information from a knowledge base before generating responses.

**Traditional LLM:**
```
User Question → LLM → Answer
```

**RAG System:**
```
User Question → Retrieve Relevant Context → LLM + Context → Enhanced Answer
```

### Key Benefits

1. **Up-to-date Information**: Access current data not in training set
2. **Reduced Hallucination**: Ground responses in actual data
3. **Domain-Specific Knowledge**: Leverage proprietary information
4. **Citation & Traceability**: Source attribution for answers
5. **Cost-Effective**: No need to retrain models

### RAG Pipeline Steps

1. **Indexing**: Convert documents to embeddings and store
2. **Retrieval**: Find relevant documents for a query
3. **Augmentation**: Combine query with retrieved context
4. **Generation**: LLM generates answer using context

---

## Why Neo4j for RAG?

### Traditional Vector-Only RAG Limitations

**Standard Vector Search:**
- Only considers semantic similarity
- No relationship context
- Flat document structure
- Limited by embedding quality

### Neo4j Graph-Enhanced RAG Advantages

1. **Contextual Relationships**
   - Understand connections between entities
   - Navigate related information
   - Preserve document structure

2. **Multi-Hop Reasoning**
   - Follow relationship chains
   - Find indirect connections
   - Complex query patterns

3. **Hybrid Search**
   - Combine vector similarity + graph traversal
   - Keyword + semantic + structural search
   - Weighted result fusion

4. **Metadata Filtering**
   - Filter by properties before/after vector search
   - Temporal constraints
   - Access control

5. **Explainable Results**
   - Show relationship paths
   - Visualize result provenance
   - Transparent reasoning

### Use Cases

- **Knowledge Graphs**: Wikipedia, product catalogs, scientific papers
- **Enterprise Search**: Document management, internal wikis
- **Customer Support**: FAQ systems, troubleshooting guides
- **Research**: Academic papers with citations
- **Legal/Compliance**: Regulations with cross-references

---

## RAG Architecture

### Standard RAG Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

1. INDEXING PHASE (Offline)
   ┌──────────────┐
   │  Documents   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐      ┌──────────────┐
   │   Chunking   │─────▶│  Embeddings  │
   └──────────────┘      └──────┬───────┘
                                │
                                ▼
                         ┌─────────────┐
                         │   Neo4j     │
                         │ Vector Index│
                         └─────────────┘

2. RETRIEVAL PHASE (Online)
   ┌──────────────┐
   │ User Query   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐      ┌──────────────┐
   │ Embed Query  │─────▶│ Vector Search│
   └──────────────┘      └──────┬───────┘
                                │
                                ▼
                         ┌─────────────┐
                         │  Relevant   │
                         │  Documents  │
                         └──────┬──────┘
                                │
3. GENERATION PHASE                │
                                   ▼
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │ User Query + │─────▶│     LLM      │─────▶│   Answer     │
   │   Context    │      │  (GPT-4)     │      └──────────────┘
   └──────────────┘      └──────────────┘
```

### Graph-Enhanced RAG Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             GRAPH-ENHANCED RAG ARCHITECTURE                 │
└─────────────────────────────────────────────────────────────┘

1. KNOWLEDGE GRAPH CONSTRUCTION
   ┌──────────────┐
   │  Documents   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────────────────────────────┐
   │  NLP Processing & Entity Extraction      │
   │  - Named Entity Recognition (NER)        │
   │  - Relationship Extraction               │
   │  - Coreference Resolution                │
   └──────┬───────────────────────────────────┘
          │
          ▼
   ┌─────────────────────────────────────────┐
   │           Neo4j Knowledge Graph         │
   │                                         │
   │  (:Document)-[:CONTAINS]→(:Chunk)      │
   │  (:Chunk)-[:MENTIONS]→(:Entity)        │
   │  (:Entity)-[:RELATED_TO]→(:Entity)     │
   │  (:Chunk {embedding: vector})          │
   └─────────────────────────────────────────┘

2. HYBRID RETRIEVAL
   ┌──────────────┐
   │ User Query   │
   └──────┬───────┘
          │
          ├─────────────────┬─────────────────┬──────────────┐
          │                 │                 │              │
          ▼                 ▼                 ▼              ▼
   ┌──────────┐      ┌──────────┐    ┌──────────┐   ┌──────────┐
   │ Vector   │      │  Graph   │    │ Keyword  │   │Metadata  │
   │ Search   │      │Traversal │    │  Search  │   │ Filter   │
   └────┬─────┘      └────┬─────┘    └────┬─────┘   └────┬─────┘
        │                 │               │              │
        └─────────────────┴───────────────┴──────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Result    │
                   │   Fusion    │
                   └──────┬──────┘
                          │
3. CONTEXT ENRICHMENT      │
                          ▼
   ┌────────────────────────────────────────┐
   │  Graph Context Expansion               │
   │  - Related entities                    │
   │  - Relationship paths                  │
   │  - Connected documents                 │
   └────────┬───────────────────────────────┘
            │
            ▼
   ┌────────────────┐      ┌──────────────┐      ┌──────────────┐
   │ Query + Rich   │─────▶│     LLM      │─────▶│   Answer +   │
   │ Graph Context  │      │              │      │   Sources    │
   └────────────────┘      └──────────────┘      └──────────────┘
```

---

## Setup and Installation

### Install Required Packages

```bash
# Core packages
pip install neo4j langchain langchain-community langchain-openai

# Embeddings
pip install openai tiktoken

# Text processing
pip install pypdf python-docx unstructured

# Additional utilities
pip install python-dotenv numpy pandas
```

### Environment Setup

Create `.env` file:
```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Optional: Other LLM providers
ANTHROPIC_API_KEY=your_anthropic_key
COHERE_API_KEY=your_cohere_key
```

### Neo4j Database Setup

```cypher
// Create vector index for embeddings
CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
FOR (c:Chunk)
ON (c.embedding)
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 1536,  // OpenAI ada-002 dimension
        `vector.similarity_function`: 'cosine'
    }
}

// Create constraints
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;

// Create indexes for better query performance
CREATE INDEX document_title IF NOT EXISTS FOR (d:Document) ON (d.title);
CREATE INDEX chunk_text IF NOT EXISTS FOR (c:Chunk) ON (c.text);
CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type);

// Create full-text search index
CREATE FULLTEXT INDEX chunk_text_fulltext IF NOT EXISTS
FOR (c:Chunk) ON EACH [c.text, c.title];
```

---

## Vector Search in Neo4j

### Understanding Vector Embeddings

**Embeddings** are dense numerical representations of text that capture semantic meaning.

```python
from openai import OpenAI

client = OpenAI()

# Generate embedding for text
def get_embedding(text: str) -> list[float]:
    """Generate OpenAI embedding for text"""
    response = client.embeddings.create(
        model="text-embedding-3-small",  # or text-embedding-ada-002
        input=text
    )
    return response.data[0].embedding

# Example
text = "Neo4j is a graph database"
embedding = get_embedding(text)
print(f"Embedding dimension: {len(embedding)}")  # 1536 for ada-002
print(f"First 5 values: {embedding[:5]}")
```

### Storing Embeddings in Neo4j

```python
from neo4j import GraphDatabase
import uuid

def store_document_with_embedding(driver, text: str, metadata: dict):
    """Store document chunk with embedding in Neo4j"""
    
    # Generate embedding
    embedding = get_embedding(text)
    
    query = """
    CREATE (c:Chunk {
        id: $id,
        text: $text,
        embedding: $embedding,
        createdAt: datetime()
    })
    SET c += $metadata
    RETURN c
    """
    
    chunk_id = str(uuid.uuid4())
    
    with driver.session() as session:
        result = session.run(
            query,
            id=chunk_id,
            text=text,
            embedding=embedding,
            metadata=metadata
        )
        return result.single()["c"]
```

### Vector Similarity Search

```python
def vector_search(driver, query_text: str, k: int = 5):
    """Perform vector similarity search"""
    
    # Generate query embedding
    query_embedding = get_embedding(query_text)
    
    query = """
    CALL db.index.vector.queryNodes('document_embeddings', $k, $embedding)
    YIELD node, score
    RETURN node.id AS id,
           node.text AS text,
           score
    ORDER BY score DESC
    """
    
    with driver.session() as session:
        result = session.run(query, k=k, embedding=query_embedding)
        return [dict(record) for record in result]

# Usage
results = vector_search(driver, "What is graph database?", k=5)
for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result['score']:.4f}")
    print(f"   Text: {result['text'][:100]}...\n")
```

### Similarity Functions

Neo4j supports three similarity functions:

1. **Cosine Similarity** (most common)
   - Range: -1 to 1 (1 = identical)
   - Best for normalized vectors
   - Default for embeddings

2. **Euclidean Distance**
   - Range: 0 to ∞ (0 = identical)
   - Measures absolute distance

3. **Dot Product**
   - Range: -∞ to ∞
   - Faster but requires normalized vectors

```cypher
// Create index with different similarity functions
CREATE VECTOR INDEX cosine_idx FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {`vector.similarity_function`: 'cosine'}}

CREATE VECTOR INDEX euclidean_idx FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {`vector.similarity_function`: 'euclidean'}}
```

---

## Graph-Based RAG

### Building Knowledge Graph from Documents

```python
import re
from typing import List, Dict, Tuple

class DocumentProcessor:
    """Process documents into knowledge graph"""
    
    def __init__(self, driver, openai_client):
        self.driver = driver
        self.client = openai_client
    
    def chunk_text(self, text: str, chunk_size: int = 1000, 
                   overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities using LLM"""
        prompt = f"""
        Extract key entities from this text. Return as JSON array with format:
        [{{"name": "entity name", "type": "PERSON|ORGANIZATION|LOCATION|CONCEPT"}}]
        
        Text: {text[:500]}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        # Parse JSON response
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return []
    
    def process_document(self, doc_id: str, title: str, content: str, 
                        metadata: dict = None):
        """Process document into knowledge graph"""
        
        # 1. Create document node
        self._create_document(doc_id, title, metadata or {})
        
        # 2. Chunk text
        chunks = self.chunk_text(content)
        
        # 3. Process each chunk
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            
            # Generate embedding
            embedding = self._get_embedding(chunk_text)
            
            # Extract entities
            entities = self.extract_entities(chunk_text)
            
            # Store in graph
            self._store_chunk_with_entities(
                doc_id, chunk_id, chunk_text, embedding, 
                entities, i, len(chunks)
            )
    
    def _create_document(self, doc_id: str, title: str, metadata: dict):
        """Create document node"""
        query = """
        MERGE (d:Document {id: $id})
        SET d.title = $title,
            d += $metadata,
            d.createdAt = datetime()
        RETURN d
        """
        
        with self.driver.session() as session:
            session.run(query, id=doc_id, title=title, metadata=metadata)
    
    def _store_chunk_with_entities(self, doc_id: str, chunk_id: str, 
                                   text: str, embedding: list, 
                                   entities: list, position: int, 
                                   total_chunks: int):
        """Store chunk with entities and relationships"""
        query = """
        MATCH (d:Document {id: $docId})
        
        CREATE (c:Chunk {
            id: $chunkId,
            text: $text,
            embedding: $embedding,
            position: $position,
            totalChunks: $totalChunks,
            createdAt: datetime()
        })
        
        CREATE (d)-[:CONTAINS]->(c)
        
        // Create entities and relationships
        WITH c
        UNWIND $entities AS entity
        MERGE (e:Entity {name: entity.name})
        ON CREATE SET e.type = entity.type
        MERGE (c)-[:MENTIONS]->(e)
        
        RETURN c, collect(e) AS entities
        """
        
        with self.driver.session() as session:
            session.run(
                query,
                docId=doc_id,
                chunkId=chunk_id,
                text=text,
                embedding=embedding,
                position=position,
                totalChunks=total_chunks,
                entities=entities
            )
    
    def _get_embedding(self, text: str) -> list:
        """Generate embedding"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
```

### Graph-Enhanced Retrieval

```python
def hybrid_search(driver, query_text: str, k: int = 5):
    """
    Hybrid search combining vector similarity and graph traversal
    """
    
    query_embedding = get_embedding(query_text)
    
    query = """
    // 1. Vector search for relevant chunks
    CALL db.index.vector.queryNodes('document_embeddings', $k, $embedding)
    YIELD node AS chunk, score
    
    // 2. Expand to related entities and documents
    MATCH (chunk)-[:MENTIONS]->(entity:Entity)
    OPTIONAL MATCH (chunk)<-[:CONTAINS]-(doc:Document)
    
    // 3. Find related chunks through shared entities
    OPTIONAL MATCH (entity)<-[:MENTIONS]-(relatedChunk:Chunk)
    WHERE relatedChunk <> chunk
    
    WITH chunk, doc, score,
         collect(DISTINCT entity.name) AS entities,
         collect(DISTINCT {
             id: relatedChunk.id,
             text: relatedChunk.text
         })[..3] AS relatedChunks
    
    RETURN chunk.id AS chunkId,
           chunk.text AS text,
           doc.title AS documentTitle,
           score,
           entities,
           relatedChunks
    ORDER BY score DESC
    LIMIT $k
    """
    
    with driver.session() as session:
        result = session.run(query, k=k, embedding=query_embedding)
        return [dict(record) for record in result]
```

### Multi-Hop Reasoning

```python
def multi_hop_search(driver, query_text: str, max_hops: int = 2):
    """
    Perform multi-hop search following entity relationships
    """
    
    query_embedding = get_embedding(query_text)
    
    query = """
    // Find initial relevant chunks
    CALL db.index.vector.queryNodes('document_embeddings', 3, $embedding)
    YIELD node AS startChunk, score
    
    // Follow entity relationships up to max hops
    MATCH path = (startChunk)-[:MENTIONS]->(e1:Entity)
                 -[:RELATED_TO*0..$maxHops]-(e2:Entity)
                 <-[:MENTIONS]-(endChunk:Chunk)
    
    WHERE startChunk <> endChunk
    
    WITH startChunk, endChunk, path, score,
         [e IN nodes(path) WHERE e:Entity | e.name] AS entityPath
    
    RETURN DISTINCT
           startChunk.text AS startText,
           endChunk.text AS endText,
           entityPath,
           length(path) AS pathLength,
           score
    ORDER BY score DESC, pathLength ASC
    LIMIT 10
    """
    
    with driver.session() as session:
        result = session.run(
            query, 
            embedding=query_embedding, 
            maxHops=max_hops
        )
        return [dict(record) for record in result]
```

---

## Hybrid Search Strategies

### 1. Vector + Keyword Search

```python
def vector_keyword_hybrid(driver, query_text: str, k: int = 10):
    """Combine vector similarity with full-text search"""
    
    query_embedding = get_embedding(query_text)
    
    query = """
    // Vector search
    CALL db.index.vector.queryNodes('document_embeddings', $k, $embedding)
    YIELD node AS vectorChunk, score AS vectorScore
    
    WITH collect({chunk: vectorChunk, score: vectorScore, type: 'vector'}) AS vectorResults
    
    // Keyword search
    CALL db.index.fulltext.queryNodes('chunk_text_fulltext', $queryText)
    YIELD node AS keywordChunk, score AS keywordScore
    LIMIT $k
    
    WITH vectorResults + collect({chunk: keywordChunk, score: keywordScore, type: 'keyword'}) AS allResults
    
    // Combine and deduplicate
    UNWIND allResults AS result
    WITH result.chunk AS chunk,
         max(result.score) AS maxScore,
         collect(DISTINCT result.type) AS sources
    
    RETURN chunk.id AS id,
           chunk.text AS text,
           maxScore AS score,
           sources
    ORDER BY maxScore DESC
    LIMIT $k
    """
    
    with driver.session() as session:
        result = session.run(
            query, 
            k=k, 
            embedding=query_embedding, 
            queryText=query_text
        )
        return [dict(record) for record in result]
```

### 2. Metadata Filtering

```python
def filtered_vector_search(driver, query_text: str, filters: dict, k: int = 5):
    """Vector search with metadata filters"""
    
    query_embedding = get_embedding(query_text)
    
    # Build filter conditions
    filter_conditions = []
    for key, value in filters.items():
        if isinstance(value, list):
            filter_conditions.append(f"chunk.{key} IN ${key}")
        else:
            filter_conditions.append(f"chunk.{key} = ${key}")
    
    where_clause = " AND ".join(filter_conditions) if filter_conditions else "true"
    
    query = f"""
    CALL db.index.vector.queryNodes('document_embeddings', $k * 3, $embedding)
    YIELD node AS chunk, score
    
    WHERE {where_clause}
    
    OPTIONAL MATCH (chunk)<-[:CONTAINS]-(doc:Document)
    
    RETURN chunk.id AS id,
           chunk.text AS text,
           doc.title AS documentTitle,
           score
    ORDER BY score DESC
    LIMIT $k
    """
    
    params = {
        'k': k,
        'embedding': query_embedding,
        **filters
    }
    
    with driver.session() as session:
        result = session.run(query, **params)
        return [dict(record) for record in result]

# Usage
results = filtered_vector_search(
    driver,
    "machine learning",
    filters={
        "category": "AI",
        "year": [2023, 2024],
        "language": "en"
    },
    k=5
)
```

### 3. Reciprocal Rank Fusion

```python
def reciprocal_rank_fusion(driver, query_text: str, k: int = 10):
    """
    Advanced fusion using Reciprocal Rank Fusion (RRF)
    Combines multiple retrieval methods with better ranking
    """
    
    query_embedding = get_embedding(query_text)
    
    query = """
    // Method 1: Vector search
    CALL db.index.vector.queryNodes('document_embeddings', $k * 2, $embedding)
    YIELD node AS chunk, score
    WITH collect({chunk: chunk, score: score, method: 'vector'}) AS vectorResults
    
    // Method 2: Keyword search
    CALL db.index.fulltext.queryNodes('chunk_text_fulltext', $queryText)
    YIELD node AS chunk, score
    LIMIT $k * 2
    WITH vectorResults, collect({chunk: chunk, score: score, method: 'keyword'}) AS keywordResults
    
    // Method 3: Graph-based (entities)
    MATCH (chunk:Chunk)-[:MENTIONS]->(e:Entity)
    WHERE toLower(e.name) CONTAINS toLower($queryText)
    WITH vectorResults, keywordResults, 
         collect({chunk: chunk, score: 1.0, method: 'graph'}) AS graphResults
    
    // Combine all results
    WITH vectorResults + keywordResults + graphResults AS allResults
    
    UNWIND allResults AS result
    WITH result.chunk AS chunk,
         result.method AS method,
         result.score AS score
    
    // Calculate RRF score: 1 / (k + rank)
    WITH chunk, method, score,
         row_number() OVER (PARTITION BY method ORDER BY score DESC) AS rank
    WITH chunk.id AS id,
         chunk.text AS text,
         sum(1.0 / (60 + rank)) AS rrfScore,
         collect(DISTINCT method) AS methods
    
    RETURN id, text, rrfScore, methods
    ORDER BY rrfScore DESC
    LIMIT $k
    """
    
    with driver.session() as session:
        result = session.run(
            query,
            k=k,
            embedding=query_embedding,
            queryText=query_text
        )
        return [dict(record) for record in result]
```

---

## LangChain Integration

### Neo4j Vector Store with LangChain

```python
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Initialize components
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create Neo4j vector store
vector_store = Neo4jVector.from_existing_graph(
    embedding=embeddings,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="document_embeddings",
    node_label="Chunk",
    text_node_properties=["text"],
    embedding_node_property="embedding"
)

# Create retriever
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# Create LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# Query
response = qa_chain.invoke({"query": "What is a graph database?"})
print(response["result"])
print("\nSources:")
for doc in response["source_documents"]:
    print(f"- {doc.page_content[:100]}...")
```

### Custom Retriever with Graph Context

```python
from langchain.schema import BaseRetriever, Document
from typing import List

class GraphEnhancedRetriever(BaseRetriever):
    """Custom retriever that uses graph context"""
    
    def __init__(self, driver, embeddings, k: int = 5):
        self.driver = driver
        self.embeddings = embeddings
        self.k = k
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve documents with graph context"""
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        cypher_query = """
        CALL db.index.vector.queryNodes('document_embeddings', $k, $embedding)
        YIELD node AS chunk, score
        
        // Get document context
        MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        
        // Get entities mentioned
        MATCH (chunk)-[:MENTIONS]->(entity:Entity)
        
        // Get related chunks through entities
        OPTIONAL MATCH (entity)<-[:MENTIONS]-(related:Chunk)
        WHERE related <> chunk
        
        WITH chunk, doc, score,
             collect(DISTINCT entity.name) AS entities,
             collect(DISTINCT related.text)[..2] AS relatedContexts
        
        RETURN chunk.text AS text,
               doc.title AS title,
               doc.id AS docId,
               score,
               entities,
               relatedContexts
        ORDER BY score DESC
        """
        
        with self.driver.session() as session:
            result = session.run(
                cypher_query,
                k=self.k,
                embedding=query_embedding
            )
            
            documents = []
            for record in result:
                # Build rich context
                context = record["text"]
                if record["relatedContexts"]:
                    context += "\n\nRelated context:\n" + "\n".join(record["relatedContexts"])
                
                doc = Document(
                    page_content=context,
                    metadata={
                        "title": record["title"],
                        "doc_id": record["docId"],
                        "score": record["score"],
                        "entities": record["entities"]
                    }
                )
                documents.append(doc)
            
            return documents
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Async version"""
        return self.get_relevant_documents(query)

# Usage
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
retriever = GraphEnhancedRetriever(driver, embeddings, k=5)

# Use in chain
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4"),
    retriever=retriever,
    return_source_documents=True
)
```

### Advanced RAG with Citations

```python
from langchain.prompts import PromptTemplate

# Custom prompt with citations
prompt_template = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, say so - don't make up an answer.
Always cite your sources by referring to the document titles.

Context:
{context}

Question: {question}

Answer (with citations):
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# Create chain with custom prompt
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4", temperature=0),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

# Query with citations
response = qa_chain.invoke({
    "query": "Explain the benefits of graph databases for RAG systems"
})

print("Answer:", response["result"])
print("\nSources used:")
for i, doc in enumerate(response["source_documents"], 1):
    print(f"{i}. {doc.metadata.get('title', 'Unknown')} "
          f"(Score: {doc.metadata.get('score', 0):.4f})")
    print(f"   Entities: {', '.join(doc.metadata.get('entities', []))}")
```

---

**Next:** See [07-rag-implementation.md](07-rag-implementation.md) for complete working RAG application code.
