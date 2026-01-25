# Chapter 36: Project - Knowledge Graph

## Project Overview

Build a comprehensive knowledge graph system that demonstrates:
- Entity extraction and linking
- Relationship inference
- Question answering over graphs
- Knowledge graph completion
- Integration with LLMs for RAG

---

## 36.1 Knowledge Graph Schema

### Domain: Technology & Companies

```
(:Entity {
    id: UUID,
    name: STRING,
    type: STRING,
    description: STRING,
    embedding: LIST<FLOAT>,
    aliases: LIST<STRING>,
    wikidata_id: STRING
})

(:Person {
    id: UUID,
    name: STRING,
    birthDate: DATE,
    nationality: STRING,
    occupation: LIST<STRING>,
    embedding: LIST<FLOAT>
})

(:Organization {
    id: UUID,
    name: STRING,
    type: STRING,  // Company, University, Government
    founded: DATE,
    headquarters: STRING,
    industry: LIST<STRING>,
    embedding: LIST<FLOAT>
})

(:Technology {
    id: UUID,
    name: STRING,
    type: STRING,  // Language, Framework, Database, etc.
    firstReleased: DATE,
    latestVersion: STRING,
    embedding: LIST<FLOAT>
})

(:Concept {
    id: UUID,
    name: STRING,
    category: STRING,
    description: STRING,
    embedding: LIST<FLOAT>
})

(:Document {
    id: UUID,
    title: STRING,
    url: STRING,
    content: STRING,
    publishedDate: DATE,
    source: STRING
})

(:Chunk {
    id: UUID,
    text: STRING,
    position: INT,
    embedding: LIST<FLOAT>
})

Relationships:
(Person)-[:FOUNDED {date}]->(Organization)
(Person)-[:WORKS_AT {role, since, until}]->(Organization)
(Person)-[:CREATED {year}]->(Technology)
(Organization)-[:ACQUIRED {date, price}]->(Organization)
(Organization)-[:USES]->(Technology)
(Organization)-[:COMPETES_WITH]->(Organization)
(Technology)-[:BUILT_WITH]->(Technology)
(Technology)-[:ALTERNATIVE_TO]->(Technology)
(Technology)-[:IMPLEMENTS]->(Concept)
(Entity)-[:RELATED_TO {weight, type}]->(Entity)
(Document)-[:MENTIONS]->(Entity)
(Document)-[:HAS_CHUNK]->(Chunk)
(Chunk)-[:MENTIONS]->(Entity)
```

### Setup

```cypher
// Constraints
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT org_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT tech_id IF NOT EXISTS FOR (t:Technology) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;

// Indexes
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX org_name IF NOT EXISTS FOR (o:Organization) ON (o.name);
CREATE INDEX tech_name IF NOT EXISTS FOR (t:Technology) ON (t.name);

// Full-text search
CREATE FULLTEXT INDEX entity_search IF NOT EXISTS 
FOR (e:Entity|Person|Organization|Technology|Concept) 
ON EACH [e.name, e.description];

// Vector indexes
CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
FOR (e:Entity) ON e.embedding
OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}};

CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
FOR (c:Chunk) ON c.embedding
OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}};
```

---

## 36.2 Entity Extraction and Linking

```python
# knowledge_graph/extraction.py
import spacy
from typing import List, Dict, Tuple
import uuid

class EntityExtractor:
    def __init__(self, db, embedding_service):
        self.db = db
        self.embedding_service = embedding_service
        self.nlp = spacy.load("en_core_web_lg")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text."""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity_type = self._map_spacy_type(ent.label_)
            if entity_type:
                entities.append({
                    'text': ent.text,
                    'type': entity_type,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'label': ent.label_
                })
        
        return entities
    
    def _map_spacy_type(self, spacy_label: str) -> str:
        """Map spaCy entity types to our schema."""
        mapping = {
            'PERSON': 'Person',
            'ORG': 'Organization',
            'PRODUCT': 'Technology',
            'GPE': 'Location',
            'DATE': None,  # Skip dates
            'MONEY': None,  # Skip money
        }
        return mapping.get(spacy_label)
    
    def link_entity(self, entity_text: str, entity_type: str) -> Dict:
        """Link extracted entity to existing knowledge graph entity."""
        def _find_match(tx, text, entity_type):
            # First try exact match
            result = tx.run(f"""
                MATCH (e:{entity_type})
                WHERE e.name = $text OR $text IN e.aliases
                RETURN e {{.*, nodeId: elementId(e)}} AS entity
                LIMIT 1
            """, text=entity_text)
            
            record = result.single()
            if record:
                return {'match': record['entity'], 'confidence': 1.0, 'method': 'exact'}
            
            # Try fuzzy match with full-text search
            result = tx.run("""
                CALL db.index.fulltext.queryNodes('entity_search', $text)
                YIELD node, score
                WHERE score > 0.5
                RETURN node {.*, nodeId: elementId(node)} AS entity, score
                ORDER BY score DESC
                LIMIT 3
            """, text=entity_text)
            
            records = list(result)
            if records:
                return {
                    'match': records[0]['entity'],
                    'confidence': records[0]['score'],
                    'method': 'fuzzy',
                    'alternatives': [r['entity'] for r in records[1:]]
                }
            
            return None
        
        with self.db.session() as session:
            return session.execute_read(_find_match, entity_text, entity_type)
    
    def create_or_link_entity(self, entity_text: str, entity_type: str,
                               context: str = None) -> Dict:
        """Create new entity or link to existing one."""
        # Try to link first
        linked = self.link_entity(entity_text, entity_type)
        
        if linked and linked['confidence'] > 0.8:
            return {'action': 'linked', 'entity': linked['match']}
        
        # Create new entity
        embedding = self.embedding_service.embed(
            f"{entity_text}. {context or ''}"
        )
        
        def _create(tx, entity_id, name, entity_type, embedding):
            result = tx.run(f"""
                CREATE (e:{entity_type} {{
                    id: $id,
                    name: $name,
                    embedding: $embedding,
                    createdAt: datetime()
                }})
                RETURN e {{.*, nodeId: elementId(e)}} AS entity
            """, id=entity_id, name=name, embedding=embedding)
            return result.single()['entity']
        
        entity_id = str(uuid.uuid4())
        with self.db.session() as session:
            entity = session.execute_write(
                _create, entity_id, entity_text, entity_type, embedding
            )
            return {'action': 'created', 'entity': entity}
    
    def process_document(self, doc_id: str, title: str, content: str,
                         url: str = None) -> Dict:
        """Process a document: extract entities, create chunks, link."""
        # Create document node
        doc = self._create_document(doc_id, title, content, url)
        
        # Create chunks
        chunks = self._chunk_text(content)
        chunk_nodes = []
        
        for i, chunk_text in enumerate(chunks):
            chunk_embedding = self.embedding_service.embed(chunk_text)
            chunk_node = self._create_chunk(doc_id, i, chunk_text, chunk_embedding)
            chunk_nodes.append(chunk_node)
            
            # Extract and link entities for this chunk
            entities = self.extract_entities(chunk_text)
            for entity in entities:
                result = self.create_or_link_entity(
                    entity['text'], 
                    entity['type'],
                    context=chunk_text[:200]
                )
                self._link_chunk_to_entity(chunk_node['id'], result['entity']['id'])
        
        return {
            'document': doc,
            'chunks': len(chunk_nodes),
            'entities_processed': sum(len(self.extract_entities(c)) for c in chunks)
        }
    
    def _chunk_text(self, text: str, chunk_size: int = 500, 
                    overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _create_document(self, doc_id: str, title: str, 
                         content: str, url: str) -> Dict:
        def _create(tx, doc_id, title, content, url):
            result = tx.run("""
                CREATE (d:Document {
                    id: $id,
                    title: $title,
                    content: $content,
                    url: $url,
                    createdAt: datetime()
                })
                RETURN d {.*} AS doc
            """, id=doc_id, title=title, content=content, url=url)
            return result.single()['doc']
        
        with self.db.session() as session:
            return session.execute_write(_create, doc_id, title, content, url)
    
    def _create_chunk(self, doc_id: str, position: int, 
                      text: str, embedding: List[float]) -> Dict:
        def _create(tx, chunk_id, doc_id, position, text, embedding):
            result = tx.run("""
                MATCH (d:Document {id: $docId})
                CREATE (c:Chunk {
                    id: $chunkId,
                    text: $text,
                    position: $position,
                    embedding: $embedding
                })
                CREATE (d)-[:HAS_CHUNK {position: $position}]->(c)
                RETURN c {.*} AS chunk
            """, chunkId=chunk_id, docId=doc_id, position=position,
                text=text, embedding=embedding)
            return result.single()['chunk']
        
        chunk_id = f"{doc_id}_chunk_{position}"
        with self.db.session() as session:
            return session.execute_write(
                _create, chunk_id, doc_id, position, text, embedding
            )
    
    def _link_chunk_to_entity(self, chunk_id: str, entity_id: str):
        def _link(tx, chunk_id, entity_id):
            tx.run("""
                MATCH (c:Chunk {id: $chunkId})
                MATCH (e) WHERE e.id = $entityId
                MERGE (c)-[:MENTIONS]->(e)
            """, chunkId=chunk_id, entityId=entity_id)
        
        with self.db.session() as session:
            session.execute_write(_link, chunk_id, entity_id)
```

---

## 36.3 Relationship Inference

```python
# knowledge_graph/inference.py
from typing import List, Dict

class RelationshipInferrer:
    def __init__(self, db, llm_service):
        self.db = db
        self.llm = llm_service
    
    def infer_relationships(self, entity_id: str) -> List[Dict]:
        """Use graph patterns to infer potential relationships."""
        def _infer(tx, entity_id):
            # Pattern 1: Entities mentioned in same chunks
            result = tx.run("""
                MATCH (e1)-[:MENTIONED_IN]->(:Chunk)<-[:MENTIONED_IN]-(e2)
                WHERE e1.id = $entityId AND e1 <> e2
                  AND NOT (e1)-[:RELATED_TO]-(e2)
                
                WITH e2, count(*) AS cooccurrences
                WHERE cooccurrences >= 2
                
                RETURN e2 {.id, .name, labels: labels(e2)} AS entity,
                       cooccurrences,
                       'co-occurrence' AS inferenceType
                ORDER BY cooccurrences DESC
                LIMIT 10
            """, entityId=entity_id)
            
            return [dict(r) for r in result]
        
        with self.db.session() as session:
            return session.execute_read(_infer, entity_id)
    
    def extract_relationship_with_llm(self, entity1: Dict, entity2: Dict,
                                       context: str) -> Dict:
        """Use LLM to determine relationship type."""
        prompt = f"""Given these two entities and context, determine their relationship:

Entity 1: {entity1['name']} (Type: {entity1.get('type', 'Unknown')})
Entity 2: {entity2['name']} (Type: {entity2.get('type', 'Unknown')})

Context: {context}

What is the relationship between Entity 1 and Entity 2?
Respond with JSON: {{"relationship": "RELATIONSHIP_TYPE", "direction": "e1_to_e2" or "e2_to_e1", "confidence": 0.0-1.0}}
"""
        
        response = self.llm.complete(prompt)
        return self._parse_llm_response(response)
    
    def create_inferred_relationship(self, entity1_id: str, entity2_id: str,
                                      rel_type: str, confidence: float,
                                      source: str = 'inference'):
        """Create a relationship with inference metadata."""
        def _create(tx, e1_id, e2_id, rel_type, confidence, source):
            tx.run(f"""
                MATCH (e1) WHERE e1.id = $e1Id
                MATCH (e2) WHERE e2.id = $e2Id
                MERGE (e1)-[r:{rel_type}]->(e2)
                SET r.confidence = $confidence,
                    r.source = $source,
                    r.inferredAt = datetime()
            """, e1Id=entity1_id, e2Id=entity2_id, 
                confidence=confidence, source=source)
        
        with self.db.session() as session:
            session.execute_write(
                _create, entity1_id, entity2_id, rel_type, confidence, source
            )
    
    def propagate_relationships(self):
        """Use graph rules to propagate relationships."""
        def _propagate(tx):
            # Rule: If A works_at B and B is_subsidiary_of C, then A works_at C
            tx.run("""
                MATCH (p:Person)-[:WORKS_AT]->(subsidiary:Organization)
                      -[:IS_SUBSIDIARY_OF]->(parent:Organization)
                WHERE NOT (p)-[:WORKS_AT]->(parent)
                MERGE (p)-[r:WORKS_AT]->(parent)
                SET r.inferred = true, r.rule = 'subsidiary_propagation'
            """)
            
            # Rule: If Tech A uses Tech B and Tech B uses Tech C, A likely uses C
            tx.run("""
                MATCH (a:Technology)-[:BUILT_WITH]->(b:Technology)
                      -[:BUILT_WITH]->(c:Technology)
                WHERE NOT (a)-[:BUILT_WITH]->(c) AND a <> c
                MERGE (a)-[r:BUILT_WITH]->(c)
                SET r.inferred = true, r.confidence = 0.7
            """)
        
        with self.db.session() as session:
            session.execute_write(_propagate)
```

---

## 36.4 Question Answering

```python
# knowledge_graph/qa.py
from typing import List, Dict, Optional

class KnowledgeGraphQA:
    def __init__(self, db, embedding_service, llm_service):
        self.db = db
        self.embedding_service = embedding_service
        self.llm = llm_service
    
    def answer_question(self, question: str) -> Dict:
        """Answer a question using the knowledge graph."""
        # Step 1: Extract entities from question
        question_entities = self._extract_question_entities(question)
        
        # Step 2: Retrieve relevant graph context
        graph_context = self._retrieve_graph_context(question, question_entities)
        
        # Step 3: Retrieve relevant document chunks
        doc_context = self._retrieve_document_context(question)
        
        # Step 4: Generate answer
        answer = self._generate_answer(question, graph_context, doc_context)
        
        return {
            'question': question,
            'answer': answer['text'],
            'confidence': answer['confidence'],
            'sources': {
                'entities': question_entities,
                'graph_facts': graph_context,
                'documents': doc_context
            }
        }
    
    def _extract_question_entities(self, question: str) -> List[Dict]:
        """Extract and link entities from the question."""
        # Use embedding similarity to find relevant entities
        question_embedding = self.embedding_service.embed(question)
        
        def _find_entities(tx, embedding):
            result = tx.run("""
                CALL db.index.vector.queryNodes('entity_embeddings', 5, $embedding)
                YIELD node, score
                WHERE score > 0.5
                RETURN node {.id, .name, labels: labels(node)} AS entity, score
            """, embedding=embedding)
            return [dict(r) for r in result]
        
        with self.db.session() as session:
            return session.execute_read(_find_entities, question_embedding)
    
    def _retrieve_graph_context(self, question: str, 
                                 entities: List[Dict]) -> List[Dict]:
        """Retrieve relevant facts from the knowledge graph."""
        if not entities:
            return []
        
        entity_ids = [e['entity']['id'] for e in entities]
        
        def _get_context(tx, entity_ids):
            result = tx.run("""
                MATCH (e)-[r]-(connected)
                WHERE e.id IN $entityIds
                RETURN e.name AS source,
                       type(r) AS relationship,
                       connected.name AS target,
                       labels(connected)[0] AS targetType,
                       r AS relationshipProperties
                LIMIT 50
            """, entityIds=entity_ids)
            return [dict(r) for r in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_context, entity_ids)
    
    def _retrieve_document_context(self, question: str) -> List[Dict]:
        """Retrieve relevant document chunks."""
        question_embedding = self.embedding_service.embed(question)
        
        def _search(tx, embedding):
            result = tx.run("""
                CALL db.index.vector.queryNodes('chunk_embeddings', 5, $embedding)
                YIELD node AS chunk, score
                
                MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)
                OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity)
                
                RETURN chunk.text AS text,
                       doc.title AS source,
                       score,
                       collect(DISTINCT entity.name) AS mentionedEntities
            """, embedding=embedding)
            return [dict(r) for r in result]
        
        with self.db.session() as session:
            return session.execute_read(_search, question_embedding)
    
    def _generate_answer(self, question: str, graph_context: List[Dict],
                         doc_context: List[Dict]) -> Dict:
        """Generate answer using LLM with retrieved context."""
        # Format graph context
        graph_facts = "\n".join([
            f"- {fact['source']} {fact['relationship'].replace('_', ' ')} {fact['target']}"
            for fact in graph_context
        ])
        
        # Format document context
        doc_texts = "\n\n".join([
            f"[{doc['source']}]: {doc['text']}"
            for doc in doc_context
        ])
        
        prompt = f"""Answer the question based on the following knowledge:

KNOWLEDGE GRAPH FACTS:
{graph_facts}

DOCUMENT EXCERPTS:
{doc_texts}

QUESTION: {question}

Provide a comprehensive answer based on the above information. 
If the information is insufficient, say so.
Include citations to sources where relevant."""

        response = self.llm.complete(prompt)
        
        return {
            'text': response,
            'confidence': self._estimate_confidence(graph_context, doc_context)
        }
    
    def _estimate_confidence(self, graph_context: List[Dict],
                              doc_context: List[Dict]) -> float:
        """Estimate answer confidence based on context quality."""
        graph_score = min(len(graph_context) / 10, 1.0) * 0.5
        doc_score = sum(d.get('score', 0) for d in doc_context[:3]) / 3 * 0.5
        return graph_score + doc_score
    
    def cypher_question(self, question: str) -> Dict:
        """Convert natural language question to Cypher query."""
        prompt = f"""Convert this question to a Cypher query for a knowledge graph.

Schema:
- (Person) -[:WORKS_AT]-> (Organization)
- (Person) -[:FOUNDED]-> (Organization)
- (Person) -[:CREATED]-> (Technology)
- (Organization) -[:USES]-> (Technology)
- (Technology) -[:BUILT_WITH]-> (Technology)

Question: {question}

Return only the Cypher query, no explanation."""

        cypher = self.llm.complete(prompt)
        
        # Execute the query
        with self.db.session() as session:
            try:
                result = session.run(cypher)
                data = [dict(r) for r in result]
                return {
                    'question': question,
                    'cypher': cypher,
                    'results': data,
                    'success': True
                }
            except Exception as e:
                return {
                    'question': question,
                    'cypher': cypher,
                    'error': str(e),
                    'success': False
                }
```

---

## 36.5 Knowledge Graph Completion

```python
# knowledge_graph/completion.py
from typing import List, Dict, Tuple

class KnowledgeGraphCompleter:
    def __init__(self, db):
        self.db = db
    
    def find_missing_relationships(self, entity_type: str = None,
                                    limit: int = 100) -> List[Dict]:
        """Find potential missing relationships using graph patterns."""
        def _find_missing(tx, entity_type, limit):
            type_filter = f"AND e1:{entity_type}" if entity_type else ""
            
            result = tx.run(f"""
                // Find entities that share many connections but aren't connected
                MATCH (e1)-[:RELATED_TO|WORKS_AT|USES*1..2]-(common)-[:RELATED_TO|WORKS_AT|USES*1..2]-(e2)
                WHERE e1 <> e2 {type_filter}
                  AND NOT (e1)--(e2)
                
                WITH e1, e2, count(DISTINCT common) AS sharedConnections
                WHERE sharedConnections >= 3
                
                RETURN e1 {{.id, .name, labels: labels(e1)}} AS entity1,
                       e2 {{.id, .name, labels: labels(e2)}} AS entity2,
                       sharedConnections,
                       'graph_pattern' AS method
                ORDER BY sharedConnections DESC
                LIMIT $limit
            """, limit=limit)
            
            return [dict(r) for r in result]
        
        with self.db.session() as session:
            return session.execute_read(_find_missing, entity_type, limit)
    
    def predict_link(self, entity1_id: str, entity2_id: str) -> Dict:
        """Predict likelihood of link between two entities."""
        def _predict(tx, e1_id, e2_id):
            result = tx.run("""
                MATCH (e1 {id: $e1Id}), (e2 {id: $e2Id})
                
                // Common neighbors
                OPTIONAL MATCH (e1)--(common)--(e2)
                WITH e1, e2, count(DISTINCT common) AS commonNeighbors
                
                // Path distance
                OPTIONAL MATCH path = shortestPath((e1)-[*..4]-(e2))
                WITH e1, e2, commonNeighbors, 
                     CASE WHEN path IS NULL THEN 999 ELSE length(path) END AS distance
                
                // Embedding similarity
                WITH e1, e2, commonNeighbors, distance,
                     gds.similarity.cosine(e1.embedding, e2.embedding) AS embeddingSimilarity
                
                // Calculate overall score
                WITH e1, e2, commonNeighbors, distance, embeddingSimilarity,
                     (commonNeighbors * 0.3) + 
                     ((5 - distance) / 5.0 * 0.3) + 
                     (embeddingSimilarity * 0.4) AS linkScore
                
                RETURN e1.name AS entity1,
                       e2.name AS entity2,
                       commonNeighbors,
                       distance,
                       embeddingSimilarity,
                       linkScore
            """, e1Id=entity1_id, e2Id=entity2_id)
            
            return dict(result.single())
        
        with self.db.session() as session:
            return session.execute_read(_predict, entity1_id, entity2_id)
    
    def suggest_entity_types(self, entity_id: str) -> List[Dict]:
        """Suggest additional types/labels for an entity."""
        def _suggest(tx, entity_id):
            result = tx.run("""
                MATCH (e {id: $entityId})
                
                // Find similar entities
                CALL db.index.vector.queryNodes('entity_embeddings', 20, e.embedding)
                YIELD node AS similar, score
                WHERE similar <> e AND score > 0.7
                
                // Get their labels
                WITH e, similar, score, labels(similar) AS similarLabels
                UNWIND similarLabels AS label
                
                // Filter to labels e doesn't have
                WITH label, count(*) AS frequency, avg(score) AS avgSimilarity
                WHERE NOT label IN labels(e) AND label <> 'Entity'
                
                RETURN label AS suggestedType,
                       frequency,
                       avgSimilarity AS confidence
                ORDER BY frequency DESC, avgSimilarity DESC
                LIMIT 5
            """, entityId=entity_id)
            
            return [dict(r) for r in result]
        
        with self.db.session() as session:
            return session.execute_read(_suggest, entity_id)
    
    def find_contradictions(self) -> List[Dict]:
        """Find potential contradictions in the knowledge graph."""
        def _find(tx):
            # Example: Person can't work at competing companies simultaneously
            result = tx.run("""
                MATCH (p:Person)-[r1:WORKS_AT]->(o1:Organization)
                      -[:COMPETES_WITH]->(o2:Organization)<-[r2:WORKS_AT]-(p)
                WHERE r1.until IS NULL AND r2.until IS NULL
                
                RETURN p.name AS person,
                       o1.name AS company1,
                       o2.name AS company2,
                       'simultaneous_competitors' AS contradictionType
            """)
            
            contradictions = [dict(r) for r in result]
            
            # Add more contradiction patterns...
            
            return contradictions
        
        with self.db.session() as session:
            return session.execute_read(_find)
```

---

## 36.6 API and Integration

```python
# knowledge_graph/api.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])

@router.post("/documents")
async def ingest_document(
    title: str,
    content: str,
    url: Optional[str] = None,
    extractor: EntityExtractor = Depends(get_extractor)
):
    """Ingest a document into the knowledge graph."""
    doc_id = str(uuid.uuid4())
    result = extractor.process_document(doc_id, title, content, url)
    return result

@router.get("/entities/search")
async def search_entities(
    query: str,
    limit: int = Query(20, ge=1, le=100),
    db = Depends(get_db)
):
    """Search for entities."""
    with db.session() as session:
        result = session.run("""
            CALL db.index.fulltext.queryNodes('entity_search', $query)
            YIELD node, score
            RETURN node {.id, .name, labels: labels(node)} AS entity, score
            ORDER BY score DESC
            LIMIT $limit
        """, query=query, limit=limit)
        return [dict(r) for r in result]

@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str, db = Depends(get_db)):
    """Get entity details with relationships."""
    with db.session() as session:
        result = session.run("""
            MATCH (e {id: $entityId})
            OPTIONAL MATCH (e)-[r]-(connected)
            RETURN e {.*, labels: labels(e)} AS entity,
                   collect({
                       type: type(r),
                       direction: CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END,
                       connected: connected {.id, .name, labels: labels(connected)}
                   }) AS relationships
        """, entityId=entity_id)
        
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Entity not found")
        return dict(record)

@router.get("/entities/{entity_id}/graph")
async def get_entity_subgraph(
    entity_id: str,
    depth: int = Query(2, ge=1, le=4),
    db = Depends(get_db)
):
    """Get subgraph around an entity."""
    with db.session() as session:
        result = session.run("""
            MATCH (center {id: $entityId})
            CALL apoc.path.subgraphAll(center, {
                maxLevel: $depth,
                relationshipFilter: null,
                labelFilter: null
            })
            YIELD nodes, relationships
            RETURN [n IN nodes | n {.id, .name, labels: labels(n)}] AS nodes,
                   [r IN relationships | {
                       source: startNode(r).id,
                       target: endNode(r).id,
                       type: type(r)
                   }] AS edges
        """, entityId=entity_id, depth=depth)
        
        return dict(result.single())

@router.post("/qa")
async def answer_question(
    question: str,
    qa_service: KnowledgeGraphQA = Depends(get_qa_service)
):
    """Answer a question using the knowledge graph."""
    return qa_service.answer_question(question)

@router.get("/completion/missing-links")
async def find_missing_links(
    entity_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    completer: KnowledgeGraphCompleter = Depends(get_completer)
):
    """Find potential missing relationships."""
    return completer.find_missing_relationships(entity_type, limit)
```

---

## Summary

This knowledge graph project demonstrates:

| Component | Purpose |
|-----------|---------|
| Entity Extraction | Convert text to structured entities |
| Entity Linking | Connect to existing knowledge |
| Relationship Inference | Discover implicit relationships |
| Question Answering | Natural language queries |
| Graph Completion | Fill knowledge gaps |

### Key Patterns

1. **Entity Resolution**: Fuzzy matching + embedding similarity
2. **Context Retrieval**: Graph traversal + vector search
3. **RAG Integration**: Combine graph facts with document chunks
4. **Knowledge Completion**: Pattern-based inference

---

## Exercises

### Exercise 36.1: Wikidata Integration
1. Link entities to Wikidata
2. Import additional facts
3. Handle entity disambiguation

### Exercise 36.2: Temporal Knowledge
1. Add temporal properties to relationships
2. Track knowledge changes over time
3. Query "as of" a specific date

### Exercise 36.3: Multi-lingual Support
1. Store entity names in multiple languages
2. Cross-lingual entity linking
3. Translate queries

---

## 🎉 Congratulations!

You've completed the comprehensive Neo4j guide covering:

- ✅ Graph database fundamentals
- ✅ Cypher query language mastery
- ✅ Data modeling best practices
- ✅ Performance optimization
- ✅ Graph Data Science algorithms
- ✅ Vector search and RAG
- ✅ Production application development
- ✅ Real-world projects

**Continue Learning:**
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Neo4j Community](https://community.neo4j.com/)
- [Graph Academy](https://graphacademy.neo4j.com/)
