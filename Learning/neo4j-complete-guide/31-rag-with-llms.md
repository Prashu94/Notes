# Chapter 31: RAG with Neo4j and LLMs

## Learning Objectives
By the end of this chapter, you will:
- Understand Retrieval-Augmented Generation (RAG)
- Build knowledge graphs for RAG systems
- Implement GraphRAG patterns
- Integrate Neo4j with LLMs
- Create production-ready RAG pipelines

---

## 31.1 Introduction to RAG

### What is RAG?

Retrieval-Augmented Generation combines:
1. **Retrieval**: Find relevant information from a knowledge base
2. **Augmentation**: Add retrieved context to the prompt
3. **Generation**: LLM generates response using context

### Why Graph-based RAG?

| Vector RAG | GraphRAG |
|------------|----------|
| Semantic similarity only | Semantic + structural |
| Independent chunks | Connected knowledge |
| Limited context | Rich relationships |
| May miss related info | Traverses connections |

### GraphRAG Advantages

- **Multi-hop reasoning**: Follow relationships across entities
- **Contextual retrieval**: Include related information
- **Explainable**: Show reasoning path
- **Structured knowledge**: Entities and relationships

---

## 31.2 Knowledge Graph for RAG

### Entity Extraction

```cypher
// Create entities from documents
CREATE (e:Entity {
    name: 'Neo4j',
    type: 'Technology',
    description: 'Graph database management system',
    embedding: $embedding
})

// Create relationships between entities
MATCH (e1:Entity {name: 'Neo4j'})
MATCH (e2:Entity {name: 'Cypher'})
CREATE (e1)-[:HAS_QUERY_LANGUAGE]->(e2)
```

### Document-Entity Linking

```cypher
// Link documents to entities mentioned
CREATE (d:Document {
    id: 'doc1',
    title: 'Getting Started with Neo4j',
    content: '...',
    embedding: $docEmbedding
})

// Entity mentions
MATCH (d:Document {id: 'doc1'})
MATCH (e:Entity {name: 'Neo4j'})
CREATE (d)-[:MENTIONS {count: 15, context: 'main topic'}]->(e)

// Create chunk structure
CREATE (c:Chunk {
    id: 'chunk_1',
    text: 'Neo4j is a graph database...',
    position: 1,
    embedding: $chunkEmbedding
})
CREATE (d)-[:HAS_CHUNK {position: 1}]->(c)
CREATE (c)-[:MENTIONS]->(e)
```

### Hierarchical Knowledge Structure

```cypher
// Topic hierarchy
CREATE (t1:Topic {name: 'Database'})
CREATE (t2:Topic {name: 'Graph Database'})
CREATE (t3:Topic {name: 'Neo4j'})

CREATE (t1)-[:HAS_SUBTOPIC]->(t2)
CREATE (t2)-[:HAS_SUBTOPIC]->(t3)

// Documents belong to topics
MATCH (d:Document {id: 'doc1'})
MATCH (t:Topic {name: 'Neo4j'})
CREATE (d)-[:ABOUT]->(t)
```

---

## 31.3 Retrieval Strategies

### Strategy 1: Vector-Only Retrieval

```cypher
// Simple vector search
CALL db.index.vector.queryNodes('chunk_embeddings', 5, $queryEmbedding)
YIELD node AS chunk, score
RETURN chunk.text AS context, score
ORDER BY score DESC
```

### Strategy 2: Vector + Entity Expansion

```cypher
// Vector search with entity context
CALL db.index.vector.queryNodes('chunk_embeddings', 5, $queryEmbedding)
YIELD node AS chunk, score

// Expand to related entities
MATCH (chunk)-[:MENTIONS]->(entity:Entity)
OPTIONAL MATCH (entity)-[r]-(related:Entity)

RETURN chunk.text AS chunkText,
       score,
       collect(DISTINCT entity.name) AS entities,
       collect(DISTINCT {
           entity: related.name,
           relationship: type(r)
       }) AS relatedEntities
ORDER BY score DESC
```

### Strategy 3: Entity-Centric Retrieval

```cypher
// Find entities similar to query
CALL db.index.vector.queryNodes('entity_embeddings', 3, $queryEmbedding)
YIELD node AS entity, score

// Get chunks mentioning these entities
MATCH (chunk:Chunk)-[:MENTIONS]->(entity)

// Get related entities for context
MATCH (entity)-[r]-(related:Entity)

RETURN entity.name,
       collect(DISTINCT chunk.text) AS relevantChunks,
       collect(DISTINCT {
           relation: type(r),
           entity: related.name,
           description: related.description
       }) AS entityContext
ORDER BY score DESC
```

### Strategy 4: Graph Traversal Retrieval

```cypher
// Start from query-matched entities
CALL db.index.vector.queryNodes('entity_embeddings', 2, $queryEmbedding)
YIELD node AS startEntity, score

// Traverse graph to gather context
MATCH path = (startEntity)-[*1..3]-(related)
WHERE related:Entity OR related:Chunk

WITH startEntity, score, 
     collect(DISTINCT CASE 
         WHEN related:Entity THEN {type: 'entity', data: related}
         WHEN related:Chunk THEN {type: 'chunk', data: related}
     END) AS context

RETURN startEntity.name AS anchor,
       score AS relevance,
       context
ORDER BY score DESC
```

### Strategy 5: Hybrid Retrieval

```cypher
// Combine multiple retrieval methods
// 1. Vector search on chunks
CALL db.index.vector.queryNodes('chunk_embeddings', 10, $queryEmbedding)
YIELD node AS chunk, score AS vectorScore
WITH collect({chunk: chunk, score: vectorScore}) AS vectorResults

// 2. Keyword search (if applicable)
CALL db.index.fulltext.queryNodes('chunk_fulltext', $keywords)
YIELD node AS keywordChunk, score AS keywordScore
WITH vectorResults, collect({chunk: keywordChunk, score: keywordScore}) AS keywordResults

// 3. Combine and deduplicate
WITH vectorResults + keywordResults AS allResults
UNWIND allResults AS result
WITH result.chunk AS chunk, max(result.score) AS bestScore
RETURN chunk.text, bestScore
ORDER BY bestScore DESC
LIMIT 5
```

---

## 31.4 Context Building

### Building Rich Context

```cypher
// Comprehensive context retrieval
CALL db.index.vector.queryNodes('chunk_embeddings', 5, $queryEmbedding)
YIELD node AS chunk, score

// Get document info
MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)

// Get adjacent chunks for continuity
OPTIONAL MATCH (doc)-[:HAS_CHUNK]->(prevChunk:Chunk)
WHERE prevChunk.position = chunk.position - 1
OPTIONAL MATCH (doc)-[:HAS_CHUNK]->(nextChunk:Chunk)
WHERE nextChunk.position = chunk.position + 1

// Get mentioned entities with their relationships
MATCH (chunk)-[:MENTIONS]->(entity:Entity)
OPTIONAL MATCH (entity)-[rel]-(related:Entity)

RETURN 
    doc.title AS source,
    prevChunk.text AS previousContext,
    chunk.text AS mainContext,
    nextChunk.text AS followingContext,
    score,
    collect(DISTINCT {
        entity: entity.name,
        type: entity.type,
        relations: collect(DISTINCT {type: type(rel), target: related.name})
    }) AS entities
ORDER BY score DESC
```

### Formatting Context for LLM

```python
def format_context_for_llm(results: list) -> str:
    """Format retrieved results into LLM-ready context."""
    context_parts = []
    
    for i, result in enumerate(results, 1):
        part = f"[Source {i}: {result['source']}]\n"
        
        # Add surrounding context if available
        if result.get('previousContext'):
            part += f"..{result['previousContext']}\n"
        
        part += f"{result['mainContext']}\n"
        
        if result.get('followingContext'):
            part += f"{result['followingContext']}..\n"
        
        # Add entity information
        if result.get('entities'):
            part += "\nRelated entities:\n"
            for entity in result['entities']:
                part += f"- {entity['entity']} ({entity['type']})"
                if entity.get('relations'):
                    relations = ', '.join([f"{r['type']} {r['target']}" 
                                          for r in entity['relations'][:3]])
                    part += f": {relations}"
                part += "\n"
        
        context_parts.append(part)
    
    return "\n---\n".join(context_parts)
```

---

## 31.5 LLM Integration

### OpenAI Integration

```python
import openai
from neo4j import GraphDatabase

class GraphRAG:
    def __init__(self, neo4j_uri, neo4j_auth, openai_api_key):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
        openai.api_key = openai_api_key
    
    def get_embedding(self, text: str) -> list:
        """Generate embedding for text."""
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    
    def retrieve_context(self, query: str, top_k: int = 5) -> list:
        """Retrieve relevant context from knowledge graph."""
        query_embedding = self.get_embedding(query)
        
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes('chunk_embeddings', $k, $embedding)
                YIELD node AS chunk, score
                MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)
                OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity:Entity)
                OPTIONAL MATCH (entity)-[r]-(related:Entity)
                RETURN doc.title AS source,
                       chunk.text AS content,
                       score,
                       collect(DISTINCT entity.name) AS entities,
                       collect(DISTINCT {rel: type(r), entity: related.name})[0..5] AS relations
                ORDER BY score DESC
            """, k=top_k, embedding=query_embedding)
            
            return [dict(r) for r in result]
    
    def generate_response(self, query: str, context: list) -> str:
        """Generate response using LLM with retrieved context."""
        # Format context
        context_text = "\n\n".join([
            f"[{r['source']}]\n{r['content']}\n"
            f"Entities: {', '.join(r['entities'])}"
            for r in context
        ])
        
        # Create prompt
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant that answers questions 
                based on the provided context. If the context doesn't contain 
                enough information, say so. Always cite your sources."""
            },
            {
                "role": "user",
                "content": f"""Context:
{context_text}

Question: {query}

Please answer based on the context provided."""
            }
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def query(self, question: str) -> dict:
        """Full RAG pipeline."""
        # Retrieve
        context = self.retrieve_context(question)
        
        # Generate
        answer = self.generate_response(question, context)
        
        return {
            'question': question,
            'answer': answer,
            'sources': [{'source': c['source'], 'score': c['score']} 
                       for c in context]
        }
```

### LangChain Integration

```python
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Initialize Neo4j connection
graph = Neo4jGraph(
    url="neo4j://localhost:7687",
    username="neo4j",
    password="password"
)

# Initialize vector store
vector_store = Neo4jVector.from_existing_index(
    OpenAIEmbeddings(),
    url="neo4j://localhost:7687",
    username="neo4j",
    password="password",
    index_name="chunk_embeddings",
    node_label="Chunk",
    text_node_property="text",
    embedding_node_property="embedding"
)

# Create retriever with graph enhancement
def enhanced_retriever(query: str, k: int = 5):
    # Vector search
    docs = vector_store.similarity_search(query, k=k)
    
    # Enhance with graph context
    for doc in docs:
        chunk_id = doc.metadata.get('id')
        if chunk_id:
            graph_context = graph.query(f"""
                MATCH (c:Chunk {{id: '{chunk_id}'}})-[:MENTIONS]->(e:Entity)
                OPTIONAL MATCH (e)-[r]-(related:Entity)
                RETURN e.name AS entity, type(r) AS relation, related.name AS related
                LIMIT 10
            """)
            doc.metadata['graph_context'] = graph_context
    
    return docs

# Create QA chain
qa_prompt = PromptTemplate(
    template="""Use the following context to answer the question.
    
Context:
{context}

Question: {question}

Answer:""",
    input_variables=["context", "question"]
)

llm = ChatOpenAI(model="gpt-4", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": qa_prompt}
)
```

---

## 31.6 Advanced RAG Patterns

### Multi-Step Reasoning

```python
class MultiStepGraphRAG:
    def __init__(self, driver, llm_client):
        self.driver = driver
        self.llm = llm_client
    
    def decompose_question(self, question: str) -> list:
        """Break complex question into sub-questions."""
        prompt = f"""Break down this question into simpler sub-questions 
        that can be answered independently:
        
        Question: {question}
        
        Return as JSON array of strings."""
        
        response = self.llm.complete(prompt)
        return json.loads(response)
    
    def answer_subquestion(self, subquestion: str) -> dict:
        """Answer a single sub-question."""
        context = self.retrieve_context(subquestion)
        answer = self.generate_answer(subquestion, context)
        return {'question': subquestion, 'answer': answer, 'context': context}
    
    def synthesize_answers(self, question: str, sub_answers: list) -> str:
        """Combine sub-answers into final response."""
        prompt = f"""Original question: {question}
        
        Sub-questions and answers:
        {json.dumps(sub_answers, indent=2)}
        
        Synthesize a comprehensive answer to the original question."""
        
        return self.llm.complete(prompt)
    
    def query(self, question: str) -> dict:
        """Multi-step RAG pipeline."""
        # Decompose
        sub_questions = self.decompose_question(question)
        
        # Answer each
        sub_answers = [self.answer_subquestion(sq) for sq in sub_questions]
        
        # Synthesize
        final_answer = self.synthesize_answers(question, sub_answers)
        
        return {
            'question': question,
            'answer': final_answer,
            'reasoning': sub_answers
        }
```

### Query-Focused Summarization

```cypher
// Get summaries of relevant entities
CALL db.index.vector.queryNodes('entity_embeddings', 5, $queryEmbedding)
YIELD node AS entity, score

// Get entity's document appearances
MATCH (chunk:Chunk)-[:MENTIONS]->(entity)
MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)

// Aggregate information about the entity
WITH entity, score,
     collect(DISTINCT doc.title) AS sources,
     collect(chunk.text)[0..3] AS sampleMentions

RETURN entity.name AS entityName,
       entity.description AS description,
       entity.type AS entityType,
       sources,
       sampleMentions,
       score
ORDER BY score DESC
```

### Fact Verification

```python
def verify_fact(self, statement: str) -> dict:
    """Verify a statement against the knowledge graph."""
    # Extract entities from statement
    entities = self.extract_entities(statement)
    
    with self.driver.session() as session:
        # Check if relationships exist
        verification_results = []
        for entity in entities:
            result = session.run("""
                MATCH (e:Entity {name: $name})
                OPTIONAL MATCH (e)-[r]-(related:Entity)
                RETURN e.name AS entity,
                       collect({
                           relation: type(r),
                           target: related.name,
                           targetType: related.type
                       }) AS relationships
            """, name=entity)
            
            record = result.single()
            if record:
                verification_results.append(dict(record))
    
    # Use LLM to verify
    prompt = f"""Given this statement: "{statement}"
    
    And this knowledge graph information:
    {json.dumps(verification_results, indent=2)}
    
    Verify if the statement is:
    1. SUPPORTED - Evidence supports the statement
    2. CONTRADICTED - Evidence contradicts the statement
    3. NOT ENOUGH INFO - Cannot verify from available information
    
    Explain your reasoning."""
    
    verification = self.llm.complete(prompt)
    return {'statement': statement, 'verification': verification}
```

---

## 31.7 Production Considerations

### Caching Embeddings

```python
import hashlib
from functools import lru_cache

class CachedEmbeddings:
    def __init__(self, embedding_func, cache_size=10000):
        self.embedding_func = embedding_func
        self._cache = {}
    
    def get_embedding(self, text: str) -> list:
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key not in self._cache:
            self._cache[cache_key] = self.embedding_func(text)
        return self._cache[cache_key]
```

### Rate Limiting

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = deque()
    
    def wait_if_needed(self):
        now = time.time()
        # Remove old calls
        while self.calls and now - self.calls[0] > 60:
            self.calls.popleft()
        
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            time.sleep(sleep_time)
        
        self.calls.append(time.time())
```

### Error Handling

```python
class RobustGraphRAG:
    def query(self, question: str, max_retries: int = 3) -> dict:
        for attempt in range(max_retries):
            try:
                context = self.retrieve_context(question)
                if not context:
                    return self.fallback_response(question)
                
                answer = self.generate_response(question, context)
                return {'answer': answer, 'sources': context}
            
            except openai.RateLimitError:
                time.sleep(2 ** attempt)
            except Exception as e:
                if attempt == max_retries - 1:
                    return self.error_response(str(e))
        
        return self.error_response("Max retries exceeded")
```

---

## 31.8 Complete RAG System

```python
from neo4j import GraphDatabase
import openai
from typing import List, Dict, Optional
import json

class ProductionGraphRAG:
    def __init__(self, neo4j_uri: str, neo4j_auth: tuple, 
                 openai_api_key: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
        openai.api_key = openai_api_key
        self.embedding_cache = {}
    
    def close(self):
        self.driver.close()
    
    def get_embedding(self, text: str) -> List[float]:
        """Get cached or compute embedding."""
        if text not in self.embedding_cache:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            self.embedding_cache[text] = response.data[0].embedding
        return self.embedding_cache[text]
    
    def retrieve_with_graph_context(self, query: str, 
                                     top_k: int = 5) -> List[Dict]:
        """Retrieve chunks with graph-enhanced context."""
        embedding = self.get_embedding(query)
        
        with self.driver.session() as session:
            result = session.run("""
                // Vector search
                CALL db.index.vector.queryNodes('chunk_embeddings', $k, $embedding)
                YIELD node AS chunk, score
                
                // Get document
                MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)
                
                // Get surrounding chunks
                OPTIONAL MATCH (doc)-[:HAS_CHUNK]->(prev:Chunk)
                WHERE prev.position = chunk.position - 1
                OPTIONAL MATCH (doc)-[:HAS_CHUNK]->(next:Chunk)
                WHERE next.position = chunk.position + 1
                
                // Get mentioned entities with relationships
                OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity:Entity)
                OPTIONAL MATCH (entity)-[rel]-(related:Entity)
                
                RETURN 
                    chunk.text AS content,
                    doc.title AS source,
                    doc.url AS url,
                    score,
                    prev.text AS prevChunk,
                    next.text AS nextChunk,
                    collect(DISTINCT {
                        name: entity.name,
                        type: entity.type,
                        relations: collect(DISTINCT {
                            type: type(rel), 
                            target: related.name
                        })
                    }) AS entities
                ORDER BY score DESC
            """, k=top_k, embedding=embedding)
            
            return [dict(r) for r in result]
    
    def format_context(self, results: List[Dict]) -> str:
        """Format retrieved results for LLM."""
        parts = []
        for i, r in enumerate(results, 1):
            part = f"[Source {i}: {r['source']}]\n"
            
            if r.get('prevChunk'):
                part += f"...{r['prevChunk']}\n"
            
            part += r['content'] + "\n"
            
            if r.get('nextChunk'):
                part += f"{r['nextChunk']}...\n"
            
            # Add entity context
            entities = [e for e in r.get('entities', []) if e.get('name')]
            if entities:
                part += "\nRelated concepts: "
                entity_strs = []
                for e in entities[:5]:
                    e_str = f"{e['name']} ({e['type']})"
                    rels = [f"{rel['type']} {rel['target']}" 
                            for rel in e.get('relations', [])[:2] 
                            if rel.get('target')]
                    if rels:
                        e_str += f" - {', '.join(rels)}"
                    entity_strs.append(e_str)
                part += "; ".join(entity_strs)
            
            parts.append(part)
        
        return "\n\n---\n\n".join(parts)
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate answer using GPT-4."""
        messages = [
            {
                "role": "system",
                "content": """You are a knowledgeable assistant that answers 
                questions based on the provided context. Follow these rules:
                1. Only use information from the context
                2. If context is insufficient, say so
                3. Cite sources using [Source N] format
                4. Be concise but comprehensive"""
            },
            {
                "role": "user",
                "content": f"""Context:
{context}

Question: {query}

Please provide a well-structured answer based on the context."""
            }
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def query(self, question: str) -> Dict:
        """Execute full RAG pipeline."""
        # Retrieve
        results = self.retrieve_with_graph_context(question)
        
        if not results:
            return {
                'question': question,
                'answer': "I couldn't find relevant information to answer your question.",
                'sources': []
            }
        
        # Format context
        context = self.format_context(results)
        
        # Generate
        answer = self.generate_answer(question, context)
        
        return {
            'question': question,
            'answer': answer,
            'sources': [
                {
                    'title': r['source'],
                    'url': r.get('url'),
                    'relevance': r['score']
                }
                for r in results
            ]
        }

# Usage
rag = ProductionGraphRAG(
    "neo4j://localhost:7687",
    ("neo4j", "password"),
    "sk-..."
)

try:
    result = rag.query("How does Neo4j handle ACID transactions?")
    print(f"Answer: {result['answer']}\n")
    print("Sources:")
    for s in result['sources']:
        print(f"  - {s['title']} (relevance: {s['relevance']:.3f})")
finally:
    rag.close()
```

---

## Summary

### RAG Pipeline Components

| Component | Purpose |
|-----------|---------|
| Knowledge Graph | Store structured knowledge |
| Vector Index | Semantic similarity search |
| Entity Extraction | Structure unstructured data |
| Context Building | Assemble relevant information |
| LLM Integration | Generate natural language answers |

### Best Practices

1. **Chunk documents** appropriately for your use case
2. **Link chunks to entities** for graph context
3. **Combine vector + graph** retrieval
4. **Cache embeddings** for efficiency
5. **Cite sources** in generated answers

---

## Exercises

### Exercise 31.1: Build a QA System
1. Load documents into Neo4j
2. Extract and link entities
3. Implement RAG pipeline
4. Test with various questions

### Exercise 31.2: Multi-Hop Reasoning
1. Create complex knowledge graph
2. Implement graph traversal retrieval
3. Answer questions requiring multiple hops

### Exercise 31.3: Fact-Checking System
1. Build fact verification pipeline
2. Compare statements against knowledge graph
3. Generate explanations for verdicts

---

**Next Chapter: [Chapter 32: Python Driver Deep Dive](32-python-driver.md)**
