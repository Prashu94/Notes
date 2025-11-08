# Energy & Utility Knowledge Base with RAG Chatbot

A production-ready knowledge base system for the energy and utility sector using Neo4j, LangChain, and RAG (Retrieval Augmented Generation).

## Table of Contents
1. [Overview](#overview)
2. [Data Model](#data-model)
3. [Complete Implementation](#complete-implementation)
4. [Usage Examples](#usage-examples)
5. [Sample Data](#sample-data)
6. [Deployment](#deployment)

---

## Overview

### Use Case: Energy & Utility Knowledge Base

This system provides intelligent question-answering for:

- ⚡ **Regulations & Compliance**: Energy regulations, safety standards, permits
- 🏭 **Equipment & Assets**: Power plants, transformers, distribution networks
- 📊 **Operations**: Outage management, maintenance schedules, KPIs
- 🔧 **Technical Documentation**: Procedures, specifications, troubleshooting
- 📈 **Market Data**: Energy prices, demand forecasting, tariffs
- 🌱 **Sustainability**: Renewable energy, carbon emissions, ESG metrics

### Key Features

✅ **Conversational Interface**: Multi-turn dialogue with context
✅ **Graph-Enhanced RAG**: Leverages relationships between entities
✅ **Semantic Search**: Find relevant information across documents
✅ **Citation & Sources**: Traceable answers with source documents
✅ **Entity-Aware**: Understands equipment, locations, regulations
✅ **Temporal Queries**: Handle time-based questions (outages, schedules)
✅ **Multi-Document**: Synthesizes information from multiple sources

---

## Data Model

### Graph Schema

```
                    ┌─────────────────────┐
                    │     Document        │
                    │  (Regulation,       │
                    │   Procedure, etc.)  │
                    └──────┬──────────────┘
                           │ CONTAINS
                           ▼
                    ┌─────────────────────┐
                    │       Chunk         │
                    │  {text, embedding}  │
                    └──────┬──────────────┘
                           │ MENTIONS
                           ▼
     ┌─────────────────────────────────────────────────────┐
     │                    Entities                          │
     ├──────────┬──────────┬──────────┬──────────┬─────────┤
     │          │          │          │          │         │
 Equipment  Location  Regulation  Person   Company  Incident
     │          │          │          │          │         │
     └──────────┴──────────┴──────────┴──────────┴─────────┘
                           │
                    RELATES_TO (graph)
                           │
                    ┌──────▼──────┐
                    │ Relationships│
                    │   Between    │
                    │   Entities   │
                    └──────────────┘

Node Labels:
- Document: Regulations, procedures, reports
- Chunk: Text segments with embeddings
- Equipment: Transformers, generators, meters
- Location: Substations, power plants, regions
- Regulation: Safety codes, compliance rules
- Person: Engineers, operators, managers
- Company: Vendors, contractors, utilities
- Incident: Outages, accidents, violations
```

### Relationship Types

```cypher
// Document structure
(Document)-[:CONTAINS]->(Chunk)
(Chunk)-[:NEXT_CHUNK]->(Chunk)

// Entity mentions
(Chunk)-[:MENTIONS]->(Entity)

// Entity relationships
(Equipment)-[:LOCATED_AT]->(Location)
(Equipment)-[:MAINTAINED_BY]->(Company)
(Incident)-[:INVOLVES]->(Equipment)
(Incident)-[:OCCURRED_AT]->(Location)
(Regulation)-[:APPLIES_TO]->(Equipment)
(Document)-[:SUPERSEDES]->(Document)
(Document)-[:REFERENCES]->(Regulation)
```

---

## Complete Implementation

### Main Knowledge Base Application

```python
# energy_kb_chatbot.py

import os
import uuid
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date

from neo4j import GraphDatabase
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import BaseRetriever, Document, BaseMessage, HumanMessage, AIMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class EnergyKnowledgeBase:
    """
    Energy & Utility Knowledge Base with RAG Chatbot
    """
    
    def __init__(self):
        """Initialize knowledge base and chatbot"""
        # Neo4j connection
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_user = os.getenv("NEO4J_USER")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # OpenAI
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # Create specialized retriever
        self.retriever = EnergyUtilityRetriever(
            self.driver,
            self.embeddings,
            self.database
        )
        
        # Chat sessions storage
        self.chat_sessions = {}
        
        logger.info("Energy Knowledge Base initialized")
    
    def close(self):
        """Close connections"""
        if self.driver:
            self.driver.close()
    
    # ==================== DOCUMENT INGESTION ====================
    
    def ingest_document(self, content: str, title: str, doc_type: str,
                       metadata: Dict = None) -> str:
        """
        Ingest document into knowledge base
        
        Args:
            content: Document text content
            title: Document title
            doc_type: Type (regulation, procedure, report, manual)
            metadata: Additional metadata (date, version, author, etc.)
            
        Returns:
            Document ID
        """
        doc_id = str(uuid.uuid4())
        
        logger.info(f"Ingesting document: {title} ({doc_type})")
        
        processor = EnergyDocumentProcessor(
            self.driver,
            self.openai_client,
            self.database
        )
        
        processor.process_document(
            doc_id=doc_id,
            title=title,
            content=content,
            doc_type=doc_type,
            metadata=metadata or {}
        )
        
        logger.info(f"Document ingested: {doc_id}")
        return doc_id
    
    def ingest_from_file(self, file_path: str, doc_type: str,
                         metadata: Dict = None) -> str:
        """Ingest document from file"""
        from pathlib import Path
        
        title = Path(file_path).stem
        content = self._read_file(file_path)
        
        return self.ingest_document(content, title, doc_type, metadata)
    
    def _read_file(self, file_path: str) -> str:
        """Read document content"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            return "\n".join([page.extract_text() for page in reader.pages])
        elif ext in ['.docx', '.doc']:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    # ==================== CHATBOT INTERFACE ====================
    
    def create_chat_session(self, session_name: str = None) -> str:
        """
        Create a new chat session
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        # Custom prompt for energy sector
        system_template = """You are an expert AI assistant for an energy and utility company's knowledge base.
Your role is to help employees find information about:
- Energy regulations and compliance requirements
- Equipment specifications and maintenance procedures
- Safety protocols and incident reports
- Operational guidelines and best practices
- Market data and industry standards

Use the provided context to answer questions accurately. Always:
1. Cite specific documents and sections when possible
2. Highlight safety-critical information
3. Note if regulations or procedures have been superseded
4. Indicate if information may be outdated
5. Suggest related topics the user might want to explore

If you're unsure or the information isn't in the knowledge base, say so clearly.

Context from knowledge base:
{context}

Chat History:
{chat_history}

Current Question: {question}

Provide a comprehensive answer with citations:"""

        # Create memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create conversational chain
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            verbose=False
        )
        
        self.chat_sessions[session_id] = {
            "chain": chain,
            "memory": memory,
            "created_at": datetime.now(),
            "name": session_name or f"Session {session_id[:8]}"
        }
        
        logger.info(f"Created chat session: {session_id}")
        return session_id
    
    def chat(self, session_id: str, question: str) -> Dict:
        """
        Send message in chat session
        
        Args:
            session_id: Chat session ID
            question: User question
            
        Returns:
            Response with answer and sources
        """
        if session_id not in self.chat_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.chat_sessions[session_id]
        chain = session["chain"]
        
        logger.info(f"Processing question in session {session_id}: {question}")
        
        # Get response
        response = chain.invoke({"question": question})
        
        # Format sources
        sources = self._format_sources(response.get("source_documents", []))
        
        # Extract entities mentioned
        entities = self._extract_query_entities(question)
        
        return {
            "session_id": session_id,
            "question": question,
            "answer": response["answer"],
            "sources": sources,
            "entities_mentioned": entities,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        if session_id not in self.chat_sessions:
            return []
        
        memory = self.chat_sessions[session_id]["memory"]
        history = memory.load_memory_variables({})
        
        messages = []
        for msg in history.get("chat_history", []):
            messages.append({
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content
            })
        
        return messages
    
    def clear_chat_history(self, session_id: str):
        """Clear conversation history"""
        if session_id in self.chat_sessions:
            self.chat_sessions[session_id]["memory"].clear()
    
    def delete_chat_session(self, session_id: str):
        """Delete a chat session"""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
    
    # ==================== QUERY & SEARCH ====================
    
    def search(self, query: str, search_type: str = "hybrid", 
               filters: Dict = None, k: int = 5) -> List[Dict]:
        """
        Search knowledge base
        
        Args:
            query: Search query
            search_type: "vector", "keyword", "graph", or "hybrid"
            filters: Metadata filters (doc_type, date_range, etc.)
            k: Number of results
            
        Returns:
            List of relevant chunks with metadata
        """
        if search_type == "vector":
            return self._vector_search(query, filters, k)
        elif search_type == "keyword":
            return self._keyword_search(query, filters, k)
        elif search_type == "graph":
            return self._graph_search(query, k)
        else:
            return self._hybrid_search(query, filters, k)
    
    def _vector_search(self, query: str, filters: Dict, k: int) -> List[Dict]:
        """Vector similarity search"""
        embedding = self.embeddings.embed_query(query)
        
        # Build filter clause
        filter_clause = self._build_filter_clause(filters)
        
        cypher = f"""
        CALL db.index.vector.queryNodes('document_embeddings', $k * 2, $embedding)
        YIELD node AS chunk, score
        
        MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        WHERE {filter_clause}
        
        OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity)
        
        WITH chunk, doc, score, collect(DISTINCT entity.name) AS entities
        
        RETURN chunk.id AS chunkId,
               chunk.text AS text,
               doc.title AS documentTitle,
               doc.type AS documentType,
               doc.date AS documentDate,
               score,
               entities
        ORDER BY score DESC
        LIMIT $k
        """
        
        params = {"k": k, "embedding": embedding}
        if filters:
            params.update(filters)
        
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, params)
            return [dict(record) for record in result]
    
    def _keyword_search(self, query: str, filters: Dict, k: int) -> List[Dict]:
        """Full-text keyword search"""
        filter_clause = self._build_filter_clause(filters)
        
        cypher = f"""
        CALL db.index.fulltext.queryNodes('chunk_text_fulltext', $query)
        YIELD node AS chunk, score
        
        MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        WHERE {filter_clause}
        
        RETURN chunk.text AS text,
               doc.title AS documentTitle,
               doc.type AS documentType,
               score
        ORDER BY score DESC
        LIMIT $k
        """
        
        params = {"query": query, "k": k}
        if filters:
            params.update(filters)
        
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, params)
            return [dict(record) for record in result]
    
    def _graph_search(self, query: str, k: int) -> List[Dict]:
        """Graph-based search through entities"""
        embedding = self.embeddings.embed_query(query)
        
        cypher = """
        // Find initial chunks
        CALL db.index.vector.queryNodes('document_embeddings', 3, $embedding)
        YIELD node AS startChunk, score
        
        // Find related entities
        MATCH (startChunk)-[:MENTIONS]->(entity)
        
        // Find other chunks mentioning same entities
        MATCH (entity)<-[:MENTIONS]-(relatedChunk:Chunk)
        WHERE relatedChunk <> startChunk
        
        MATCH (relatedChunk)<-[:CONTAINS]-(doc:Document)
        
        WITH relatedChunk, doc, entity, score,
             count(DISTINCT entity) AS sharedEntities
        
        RETURN relatedChunk.text AS text,
               doc.title AS documentTitle,
               doc.type AS documentType,
               collect(DISTINCT entity.name) AS entities,
               sharedEntities,
               avg(score) AS score
        ORDER BY sharedEntities DESC, score DESC
        LIMIT $k
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, k=k, embedding=embedding)
            return [dict(record) for record in result]
    
    def _hybrid_search(self, query: str, filters: Dict, k: int) -> List[Dict]:
        """Hybrid search with RRF"""
        embedding = self.embeddings.embed_query(query)
        filter_clause = self._build_filter_clause(filters)
        
        cypher = f"""
        // Vector search
        CALL db.index.vector.queryNodes('document_embeddings', $k * 2, $embedding)
        YIELD node AS chunk, score
        WITH collect({{chunk: chunk, score: score, type: 'vector'}}) AS vectorResults
        
        // Keyword search
        CALL db.index.fulltext.queryNodes('chunk_text_fulltext', $query)
        YIELD node AS chunk, score
        LIMIT $k * 2
        
        WITH vectorResults + collect({{chunk: chunk, score: score, type: 'keyword'}}) AS allResults
        
        UNWIND allResults AS result
        WITH result.chunk AS chunk, result.score AS score, result.type AS searchType
        
        MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        WHERE {filter_clause}
        
        OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity)
        
        WITH chunk, doc, searchType, score,
             collect(DISTINCT entity.name) AS entities,
             row_number() OVER (PARTITION BY searchType ORDER BY score DESC) AS rank
        
        WITH chunk, doc, entities,
             sum(1.0 / (60 + rank)) AS rrfScore
        
        RETURN chunk.text AS text,
               doc.title AS documentTitle,
               doc.type AS documentType,
               doc.date AS documentDate,
               entities,
               rrfScore AS score
        ORDER BY rrfScore DESC
        LIMIT $k
        """
        
        params = {"k": k, "embedding": embedding, "query": query}
        if filters:
            params.update(filters)
        
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, params)
            return [dict(record) for record in result]
    
    def _build_filter_clause(self, filters: Dict) -> str:
        """Build WHERE clause from filters"""
        if not filters:
            return "true"
        
        conditions = []
        
        if "doc_type" in filters:
            conditions.append("doc.type = $doc_type")
        
        if "date_from" in filters:
            conditions.append("doc.date >= date($date_from)")
        
        if "date_to" in filters:
            conditions.append("doc.date <= date($date_to)")
        
        if "category" in filters:
            conditions.append("doc.category = $category")
        
        return " AND ".join(conditions) if conditions else "true"
    
    # ==================== ENTITY EXPLORATION ====================
    
    def find_equipment(self, name_pattern: str = None) -> List[Dict]:
        """Find equipment in knowledge base"""
        query = """
        MATCH (e:Equipment)
        WHERE $pattern IS NULL OR toLower(e.name) CONTAINS toLower($pattern)
        OPTIONAL MATCH (e)-[:LOCATED_AT]->(loc:Location)
        OPTIONAL MATCH (chunk:Chunk)-[:MENTIONS]->(e)
        OPTIONAL MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        
        WITH e, loc, count(DISTINCT doc) AS documentCount
        
        RETURN e.name AS equipment,
               e.type AS type,
               e.specs AS specifications,
               loc.name AS location,
               documentCount
        ORDER BY documentCount DESC
        LIMIT 20
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, pattern=name_pattern)
            return [dict(record) for record in result]
    
    def find_related_regulations(self, equipment_name: str) -> List[Dict]:
        """Find regulations related to equipment"""
        query = """
        MATCH (e:Equipment {name: $equipment})
        MATCH (reg:Regulation)-[:APPLIES_TO]->(e)
        OPTIONAL MATCH (doc:Document)-[:REFERENCES]->(reg)
        
        RETURN reg.name AS regulation,
               reg.code AS code,
               reg.description AS description,
               collect(DISTINCT doc.title) AS relatedDocuments
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, equipment=equipment_name)
            return [dict(record) for record in result]
    
    def find_incidents(self, filters: Dict = None) -> List[Dict]:
        """Find incidents (outages, accidents, etc.)"""
        where_conditions = []
        params = {}
        
        if filters:
            if "date_from" in filters:
                where_conditions.append("i.date >= date($date_from)")
                params["date_from"] = filters["date_from"]
            if "type" in filters:
                where_conditions.append("i.type = $type")
                params["type"] = filters["type"]
            if "location" in filters:
                where_conditions.append("loc.name = $location")
                params["location"] = filters["location"]
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = f"""
        MATCH (i:Incident)
        {where_clause}
        OPTIONAL MATCH (i)-[:INVOLVES]->(eq:Equipment)
        OPTIONAL MATCH (i)-[:OCCURRED_AT]->(loc:Location)
        
        RETURN i.id AS incidentId,
               i.type AS type,
               i.date AS date,
               i.description AS description,
               i.severity AS severity,
               collect(DISTINCT eq.name) AS equipmentInvolved,
               loc.name AS location
        ORDER BY i.date DESC
        LIMIT 50
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, params)
            return [dict(record) for record in result]
    
    # ==================== ANALYTICS ====================
    
    def get_kb_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        query = """
        MATCH (d:Document)
        OPTIONAL MATCH (d)-[:CONTAINS]->(c:Chunk)
        OPTIONAL MATCH (c)-[:MENTIONS]->(e)
        
        WITH count(DISTINCT d) AS docs,
             count(DISTINCT c) AS chunks,
             count(DISTINCT e) AS entities
        
        MATCH (eq:Equipment)
        WITH docs, chunks, entities, count(eq) AS equipment
        
        MATCH (reg:Regulation)
        WITH docs, chunks, entities, equipment, count(reg) AS regulations
        
        MATCH (inc:Incident)
        
        RETURN docs AS documents,
               chunks,
               entities,
               equipment,
               regulations,
               count(inc) AS incidents
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return dict(result.single())
    
    def get_document_coverage(self) -> List[Dict]:
        """Analyze document coverage by type"""
        query = """
        MATCH (d:Document)
        WITH d.type AS docType, count(d) AS count
        RETURN docType, count
        ORDER BY count DESC
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return [dict(record) for record in result]
    
    # ==================== HELPER METHODS ====================
    
    def _format_sources(self, documents: List[Document]) -> List[Dict]:
        """Format source documents"""
        sources = []
        seen_docs = set()
        
        for i, doc in enumerate(documents, 1):
            doc_title = doc.metadata.get("title", "Unknown")
            
            if doc_title not in seen_docs:
                sources.append({
                    "id": i,
                    "title": doc_title,
                    "type": doc.metadata.get("doc_type", ""),
                    "date": doc.metadata.get("date", ""),
                    "excerpt": doc.page_content[:200] + "...",
                    "entities": doc.metadata.get("entities", []),
                    "score": doc.metadata.get("score", 0)
                })
                seen_docs.add(doc_title)
        
        return sources
    
    def _extract_query_entities(self, query: str) -> List[str]:
        """Extract potential entities from query"""
        # Simple entity extraction - could be enhanced with NER
        query_lower = query.lower()
        
        # Common energy terms
        energy_terms = [
            "transformer", "generator", "substation", "transmission",
            "distribution", "meter", "outage", "voltage", "power plant",
            "renewable", "solar", "wind", "grid", "ferc", "nerc"
        ]
        
        found = [term for term in energy_terms if term in query_lower]
        return found


# ==================== DOCUMENT PROCESSOR ====================

class EnergyDocumentProcessor:
    """Process energy sector documents"""
    
    def __init__(self, driver, openai_client, database="neo4j"):
        self.driver = driver
        self.client = openai_client
        self.database = database
    
    def process_document(self, doc_id: str, title: str, content: str,
                        doc_type: str, metadata: dict):
        """Process document into knowledge graph"""
        
        # Create document node
        self._create_document(doc_id, title, doc_type, metadata)
        
        # Chunk text
        chunks = self._chunk_text(content)
        
        # Process each chunk
        for i, chunk_text in enumerate(chunks):
            self._process_chunk(doc_id, chunk_text, i, len(chunks))
    
    def _create_document(self, doc_id: str, title: str, doc_type: str, metadata: dict):
        """Create document node"""
        query = """
        CREATE (d:Document {
            id: $id,
            title: $title,
            type: $type,
            createdAt: datetime()
        })
        SET d += $metadata
        RETURN d
        """
        
        with self.driver.session(database=self.database) as session:
            session.run(query, id=doc_id, title=title, type=doc_type, metadata=metadata)
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            
            # Break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.5:
                    end = start + last_period + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def _process_chunk(self, doc_id: str, chunk_text: str, position: int, total: int):
        """Process a chunk"""
        chunk_id = f"{doc_id}_chunk_{position}"
        
        # Generate embedding
        embedding = self._get_embedding(chunk_text)
        
        # Extract entities
        entities = self._extract_energy_entities(chunk_text)
        
        # Store in Neo4j
        query = """
        MATCH (d:Document {id: $docId})
        
        CREATE (c:Chunk {
            id: $chunkId,
            text: $text,
            embedding: $embedding,
            position: $position,
            totalChunks: $total
        })
        
        CREATE (d)-[:CONTAINS]->(c)
        
        // Create entities
        WITH c
        UNWIND $entities AS entity
        
        CALL apoc.merge.node(
            [entity.type],
            {name: entity.name},
            {type: entity.entityType, createdAt: datetime()}
        ) YIELD node AS e
        
        MERGE (c)-[:MENTIONS]->(e)
        """
        
        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                docId=doc_id,
                chunkId=chunk_id,
                text=chunk_text,
                embedding=embedding,
                position=position,
                total=total,
                entities=entities
            )
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _extract_energy_entities(self, text: str) -> List[Dict]:
        """Extract energy-specific entities"""
        prompt = f"""
        Extract key entities from this energy/utility sector text. Focus on:
        - Equipment: transformers, generators, meters, etc.
        - Locations: substations, power plants, regions
        - Regulations: FERC, NERC, safety codes
        - Companies: utilities, vendors, contractors
        - Incidents: outages, accidents
        
        Return JSON array: [{{"name": "entity", "type": "Equipment|Location|Regulation|Company|Incident", "entityType": "specific type"}}]
        
        Text: {text[:800]}
        
        JSON array:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500
            )
            
            import json
            content = response.choices[0].message.content
            start = content.find('[')
            end = content.rfind(']') + 1
            
            if start != -1 and end != 0:
                entities = json.loads(content[start:end])
                return entities[:15]
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
        
        return []


# ==================== CUSTOM RETRIEVER ====================

class EnergyUtilityRetriever(BaseRetriever):
    """Custom retriever for energy sector knowledge base"""
    
    def __init__(self, driver, embeddings, database="neo4j", k: int = 5):
        self.driver = driver
        self.embeddings = embeddings
        self.database = database
        self.k = k
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents with energy sector context"""
        query_embedding = self.embeddings.embed_query(query)
        
        cypher = """
        // Vector search
        CALL db.index.vector.queryNodes('document_embeddings', $k, $embedding)
        YIELD node AS chunk, score
        
        // Get document and entity context
        MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity)
        
        // Find related chunks through shared entities
        OPTIONAL MATCH (entity)<-[:MENTIONS]-(relatedChunk:Chunk)
        WHERE relatedChunk <> chunk AND relatedChunk.position = chunk.position + 1
        
        WITH chunk, doc, score,
             collect(DISTINCT {name: entity.name, type: labels(entity)[0]}) AS entities,
             collect(DISTINCT relatedChunk.text)[..1] AS relatedContext
        
        RETURN chunk.text AS text,
               doc.title AS title,
               doc.type AS docType,
               doc.date AS date,
               score,
               entities,
               relatedContext
        ORDER BY score DESC
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, k=self.k, embedding=query_embedding)
            
            documents = []
            for record in result:
                # Build context
                context = record["text"]
                
                # Add related context
                if record["relatedContext"]:
                    context += "\n\n[Related content]\n" + "\n".join(record["relatedContext"])
                
                # Add entity context
                if record["entities"]:
                    entity_info = ", ".join([
                        f"{e['name']} ({e['type']})" 
                        for e in record["entities"] if e['name']
                    ])
                    context += f"\n\n[Entities: {entity_info}]"
                
                doc = Document(
                    page_content=context,
                    metadata={
                        "title": record["title"],
                        "doc_type": record["docType"],
                        "date": str(record["date"]) if record["date"] else "",
                        "score": record["score"],
                        "entities": [e["name"] for e in record["entities"] if e["name"]]
                    }
                )
                documents.append(doc)
            
            return documents
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Async version"""
        return self.get_relevant_documents(query)
```

---

## Usage Examples

### Example 1: Basic Setup and Ingestion

```python
# example_setup.py

from energy_kb_chatbot import EnergyKnowledgeBase

# Initialize knowledge base
kb = EnergyKnowledgeBase()

# Ingest a safety regulation
safety_regulation = """
NERC CIP-006-6 - Physical Security of BES Cyber Systems

1. PHYSICAL SECURITY PERIMETER
All critical cyber assets must be located within a Physical Security Perimeter (PSP).

1.1 Physical Access Controls
- Card reader systems at all entry points
- Video surveillance with 90-day retention
- Visitor logging and escort requirements

2. TRANSFORMER SPECIFICATIONS
Substation transformers rated above 100 MVA require:
- 24/7 monitored access control
- Intrusion detection systems
- Annual physical security audits

3. INCIDENT REPORTING
Any unauthorized physical access must be:
- Reported within 1 hour to security operations
- Documented in incident management system
- Investigated within 24 hours

Equipment Affected:
- High-voltage transformers (>100 MVA)
- Control center servers
- SCADA systems
- Emergency shutdown systems

Compliance Effective: January 1, 2024
"""

doc_id = kb.ingest_document(
    content=safety_regulation,
    title="NERC CIP-006-6 Physical Security Standard",
    doc_type="regulation",
    metadata={
        "date": "2024-01-01",
        "authority": "NERC",
        "category": "Physical Security",
        "version": "6.0"
    }
)

print(f"Document ingested: {doc_id}")

# Ingest maintenance procedure
maintenance_proc = """
TRANSFORMER MAINTENANCE PROCEDURE TM-2024-03

Quarterly Maintenance for 138kV Substations

EQUIPMENT: Power transformers at Dover Substation, Salem Substation

SCHEDULE: Q1-Q4 2024

PROCEDURE:

1. PRE-MAINTENANCE INSPECTION
- Visual inspection of transformer housing
- Check oil levels in conservator tank
- Inspect bushings for cracks or contamination
- Review temperature monitoring logs

2. OIL ANALYSIS
- Collect oil sample from drain valve
- Test for dissolved gas analysis (DGA)
- Check moisture content (<35 ppm)
- Verify dielectric strength (>30 kV)

3. COOLING SYSTEM CHECK
- Inspect radiator fins for blockage
- Test cooling fans (if applicable)
- Verify pump operation
- Clean filters

4. ELECTRICAL TESTS
- Measure winding resistance
- Perform turns ratio test
- Check insulation resistance (>1000 MΩ)
- Test protective relay functions

5. DOCUMENTATION
All results must be logged in AssetTracker system within 48 hours.

SAFETY REQUIREMENTS:
- Lock-out/Tag-out procedures mandatory
- Arc flash PPE required (40 cal/cm²)
- Two-person rule for energized work
- Emergency contacts: Operations Center 555-0100

RELATED REGULATIONS: OSHA 1910.269, NFPA 70E, NERC FAC-008

Last Updated: March 15, 2024
Next Review: September 2024
"""

kb.ingest_document(
    content=maintenance_proc,
    title="Transformer Maintenance Procedure TM-2024-03",
    doc_type="procedure",
    metadata={
        "date": "2024-03-15",
        "category": "Maintenance",
        "equipment_type": "Transformer",
        "locations": ["Dover Substation", "Salem Substation"]
    }
)

# Ingest incident report
incident_report = """
INCIDENT REPORT: IR-2024-0089

Date: April 12, 2024
Time: 14:32 EDT
Type: Equipment Failure - Unplanned Outage

LOCATION: Salem Substation, 138kV Bay 3

EQUIPMENT INVOLVED:
- Transformer T3 (Serial: TX-138-SA-003)
- Manufacturer: ABB, Model: ODT 750 MVA
- Installation Date: 2018
- Last Maintenance: March 5, 2024

INCIDENT SUMMARY:
At 14:32, protection relays detected sudden pressure rise in Transformer T3,
triggering automatic shutdown. Approximately 8,500 customers lost power.

ROOT CAUSE ANALYSIS:
Oil analysis revealed internal arcing fault in HV winding (Phase A).
Probable cause: insulation degradation due to thermal stress.

RESPONSE ACTIONS:
- Transformer isolated and de-energized (14:32)
- Load transferred to adjacent Bay 4 transformer (15:15)
- Power restored to customers (15:45)
- Failed transformer tagged for replacement

IMPACT:
- Customers affected: 8,500
- Outage duration: 73 minutes
- Load interrupted: 125 MW
- Estimated repair cost: $2.8M

CORRECTIVE ACTIONS:
1. Accelerate replacement procurement
2. Review thermal loading practices
3. Enhance oil condition monitoring frequency
4. Update transformer lifecycle management procedures

REGULATORY REPORTING:
- NERC Event reported: Yes (Loss >100 MW)
- State PUC notification: Completed 4/12 16:00
- DOE Form OE-417 submitted: 4/13 10:00

Investigation Status: Closed
Report Author: James Chen, Senior Engineer
Approved By: Sarah Williams, Operations Director
"""

kb.ingest_document(
    content=incident_report,
    title="Incident Report IR-2024-0089 - Salem Transformer Failure",
    doc_type="report",
    metadata={
        "date": "2024-04-12",
        "category": "Incident",
        "incident_type": "Equipment Failure",
        "severity": "High",
        "location": "Salem Substation"
    }
)

print("\n✅ Sample documents ingested!")
print("\nKnowledge Base Statistics:")
stats = kb.get_kb_statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")

kb.close()
```

### Example 2: Interactive Chatbot Session

```python
# example_chat.py

from energy_kb_chatbot import EnergyKnowledgeBase

kb = EnergyKnowledgeBase()

# Create chat session
session_id = kb.create_chat_session(session_name="Operations Q&A")

print(f"Chat session created: {session_id}\n")
print("=" * 60)

# Question 1: Safety requirements
print("\n👤 USER: What are the safety requirements for transformer maintenance?")

response1 = kb.chat(session_id, 
    "What are the safety requirements for transformer maintenance?")

print(f"\n🤖 ASSISTANT:\n{response1['answer']}\n")
print("📚 Sources:")
for source in response1['sources']:
    print(f"  [{source['id']}] {source['title']} ({source['type']})")

print("\n" + "=" * 60)

# Question 2: Follow-up with context
print("\n👤 USER: What PPE is required?")

response2 = kb.chat(session_id, "What PPE is required?")

print(f"\n🤖 ASSISTANT:\n{response2['answer']}\n")

print("\n" + "=" * 60)

# Question 3: Incident-related
print("\n👤 USER: Tell me about recent transformer failures at Salem Substation")

response3 = kb.chat(session_id, 
    "Tell me about recent transformer failures at Salem Substation")

print(f"\n🤖 ASSISTANT:\n{response3['answer']}\n")
print("📚 Sources:")
for source in response3['sources']:
    print(f"  [{source['id']}] {source['title']}")
    print(f"      Date: {source['date']}, Entities: {', '.join(source['entities'][:3])}")

print("\n" + "=" * 60)

# Question 4: Regulatory compliance
print("\n👤 USER: Which NERC regulations apply to physical security of transformers?")

response4 = kb.chat(session_id,
    "Which NERC regulations apply to physical security of transformers?")

print(f"\n🤖 ASSISTANT:\n{response4['answer']}\n")

# Show conversation history
print("\n" + "=" * 60)
print("\n📝 CONVERSATION HISTORY:")
history = kb.get_chat_history(session_id)
for i, msg in enumerate(history, 1):
    role = "👤 USER" if msg['role'] == 'user' else "🤖 ASSISTANT"
    preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
    print(f"{i}. {role}: {preview}")

kb.close()
```

### Example 3: Advanced Search and Analytics

```python
# example_search_analytics.py

from energy_kb_chatbot import EnergyKnowledgeBase
from datetime import datetime, timedelta

kb = EnergyKnowledgeBase()

print("=" * 60)
print("ADVANCED SEARCH & ANALYTICS")
print("=" * 60)

# 1. Hybrid search with filters
print("\n1️⃣ HYBRID SEARCH: Transformer maintenance procedures")
results = kb.search(
    query="transformer oil analysis testing procedures",
    search_type="hybrid",
    filters={
        "doc_type": "procedure",
        "date_from": "2024-01-01"
    },
    k=3
)

for i, result in enumerate(results, 1):
    print(f"\n[{i}] {result['documentTitle']}")
    print(f"    Type: {result['documentType']}, Score: {result['score']:.3f}")
    print(f"    Date: {result.get('documentDate', 'N/A')}")
    print(f"    Entities: {', '.join(result.get('entities', [])[:3])}")
    print(f"    Excerpt: {result['text'][:150]}...")

# 2. Find specific equipment
print("\n\n2️⃣ EQUIPMENT SEARCH: Transformers")
equipment = kb.find_equipment(name_pattern="transformer")

for eq in equipment[:5]:
    print(f"\n  • {eq['equipment']}")
    print(f"    Type: {eq.get('type', 'N/A')}")
    print(f"    Location: {eq.get('location', 'N/A')}")
    print(f"    Mentioned in {eq['documentCount']} documents")

# 3. Find related regulations
print("\n\n3️⃣ REGULATIONS: For transformer equipment")
if equipment:
    eq_name = equipment[0]['equipment']
    regulations = kb.find_related_regulations(eq_name)
    
    for reg in regulations:
        print(f"\n  📋 {reg['regulation']}")
        print(f"     Code: {reg.get('code', 'N/A')}")
        print(f"     Description: {reg.get('description', 'N/A')[:100]}...")

# 4. Recent incidents
print("\n\n4️⃣ INCIDENT ANALYSIS")
incidents = kb.find_incidents(filters={
    "date_from": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
    "type": "Equipment Failure"
})

print(f"\nFound {len(incidents)} incidents in last 6 months:")
for inc in incidents[:3]:
    print(f"\n  ⚠️  {inc['incidentId']} - {inc['type']}")
    print(f"     Date: {inc['date']}, Severity: {inc.get('severity', 'N/A')}")
    print(f"     Location: {inc.get('location', 'Unknown')}")
    print(f"     Equipment: {', '.join(inc.get('equipmentInvolved', []))}")
    print(f"     {inc.get('description', '')[:120]}...")

# 5. Knowledge base statistics
print("\n\n5️⃣ KNOWLEDGE BASE STATISTICS")
stats = kb.get_kb_statistics()
print("\n  📊 Content Summary:")
for key, value in stats.items():
    print(f"     {key.capitalize()}: {value}")

# 6. Document coverage analysis
print("\n  📁 Document Coverage by Type:")
coverage = kb.get_document_coverage()
for item in coverage:
    print(f"     {item['docType']}: {item['count']} documents")

kb.close()
```

### Example 4: Production Web API

```python
# web_api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from energy_kb_chatbot import EnergyKnowledgeBase

app = FastAPI(title="Energy Knowledge Base API")

# Initialize KB
kb = EnergyKnowledgeBase()

# Request/Response models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    question: str
    
class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[Dict]
    entities_mentioned: List[str]

class SearchRequest(BaseModel):
    query: str
    search_type: str = "hybrid"
    filters: Optional[Dict] = None
    k: int = 5

class IngestRequest(BaseModel):
    content: str
    title: str
    doc_type: str
    metadata: Optional[Dict] = None


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message"""
    try:
        # Create session if needed
        if not request.session_id:
            session_id = kb.create_chat_session()
        else:
            session_id = request.session_id
        
        # Get response
        response = kb.chat(session_id, request.question)
        
        return ChatResponse(**response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/session")
async def create_session(session_name: Optional[str] = None):
    """Create a new chat session"""
    session_id = kb.create_chat_session(session_name)
    return {"session_id": session_id}


@app.get("/chat/session/{session_id}/history")
async def get_history(session_id: str):
    """Get chat history"""
    history = kb.get_chat_history(session_id)
    return {"session_id": session_id, "history": history}


@app.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """Delete chat session"""
    kb.delete_chat_session(session_id)
    return {"message": "Session deleted"}


@app.post("/search")
async def search(request: SearchRequest):
    """Search knowledge base"""
    results = kb.search(
        query=request.query,
        search_type=request.search_type,
        filters=request.filters,
        k=request.k
    )
    return {"results": results}


@app.post("/ingest")
async def ingest_document(request: IngestRequest):
    """Ingest a new document"""
    doc_id = kb.ingest_document(
        content=request.content,
        title=request.title,
        doc_type=request.doc_type,
        metadata=request.metadata
    )
    return {"document_id": doc_id, "message": "Document ingested successfully"}


@app.get("/equipment")
async def list_equipment(name_pattern: Optional[str] = None):
    """Find equipment"""
    equipment = kb.find_equipment(name_pattern)
    return {"equipment": equipment}


@app.get("/incidents")
async def list_incidents(
    date_from: Optional[str] = None,
    incident_type: Optional[str] = None,
    location: Optional[str] = None
):
    """Find incidents"""
    filters = {}
    if date_from:
        filters["date_from"] = date_from
    if incident_type:
        filters["type"] = incident_type
    if location:
        filters["location"] = location
    
    incidents = kb.find_incidents(filters)
    return {"incidents": incidents}


@app.get("/statistics")
async def get_statistics():
    """Get KB statistics"""
    stats = kb.get_kb_statistics()
    coverage = kb.get_document_coverage()
    return {
        "statistics": stats,
        "coverage": coverage
    }


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    kb.close()


# Run with: uvicorn web_api:app --reload
```

---

## Sample Data

### Sample Data Loader

```python
# load_sample_data.py

from energy_kb_chatbot import EnergyKnowledgeBase
from datetime import datetime, timedelta

def load_sample_data():
    """Load comprehensive sample data for energy sector KB"""
    
    kb = EnergyKnowledgeBase()
    
    print("Loading sample energy & utility data...\n")
    
    # 1. REGULATIONS
    print("📋 Loading regulations...")
    
    regulations = [
        {
            "title": "NERC CIP-002-5.1 - Critical Cyber Asset Identification",
            "content": """
NERC CIP-002-5.1 - BES Cyber System Categorization

PURPOSE: Identify and categorize BES Cyber Systems to apply appropriate security measures.

CATEGORIZATION LEVELS:

HIGH IMPACT:
- Control centers managing >1500 MW
- Critical transmission substations (>500 kV)
- Generation facilities >1500 MW aggregate

MEDIUM IMPACT:
- Control centers managing 300-1500 MW
- Transmission substations 200-500 kV
- Generation facilities 300-1500 MW

LOW IMPACT:
- Systems below medium thresholds
- Distribution-only facilities

IDENTIFICATION REQUIREMENTS:
1. Annual review and update of asset inventory
2. Risk assessment for each cyber system
3. Documentation of categorization rationale
4. Senior management approval

PROTECTED CYBER ASSETS:
- SCADA systems
- Energy Management Systems (EMS)
- Supervisory control systems
- Communication networks
- Electronic access points

COMPLIANCE:
All entities must maintain categorization documentation and update within 90 days of changes.

Effective Date: April 1, 2016
            """,
            "type": "regulation",
            "metadata": {
                "date": "2016-04-01",
                "authority": "NERC",
                "category": "Cybersecurity",
                "code": "CIP-002-5.1"
            }
        },
        {
            "title": "OSHA 1910.269 - Electric Power Generation, Transmission, and Distribution",
            "content": """
OSHA 1910.269 - Safety Standards for Electric Power Operations

SCOPE: Covers work on electric power generation, transmission, and distribution installations.

PERSONAL PROTECTIVE EQUIPMENT (PPE):

Arc Flash Protection:
- Incident energy analysis required for systems >50V
- Arc-rated clothing based on calculated incident energy
- Face shields and insulating gloves for live work
- Flame-resistant clothing (minimum 4 cal/cm²)

Fall Protection:
- Required for work >4 feet
- Body harnesses and lanyards meeting ANSI Z359
- Anchor points rated 5,000 lbs minimum

WORK PRACTICES:

Energized Work:
- Permitted only when de-energizing creates greater hazard
- Written procedures required
- Two-person rule for voltage >600V
- Insulated tools and equipment mandatory

Lockout/Tagout:
- Energy isolation before maintenance
- Individual locks for each worker
- Verification of zero energy state
- Coordination with system operations

Clearance Distances:
- 10 feet minimum for 50kV lines
- 12 feet for 138kV systems
- 15 feet for 345kV systems

TRAINING REQUIREMENTS:
- Annual safety training mandatory
- Qualified electrical worker certification
- CPR and first aid certification
- Arc flash awareness training

EMERGENCY RESPONSE:
- Emergency procedures posted at all sites
- First aid equipment readily available
- Communication systems tested monthly
- Emergency contacts updated quarterly

Compliance Date: January 31, 2015
            """,
            "type": "regulation",
            "metadata": {
                "date": "2015-01-31",
                "authority": "OSHA",
                "category": "Safety",
                "code": "1910.269"
            }
        }
    ]
    
    for reg in regulations:
        kb.ingest_document(
            content=reg["content"],
            title=reg["title"],
            doc_type=reg["type"],
            metadata=reg["metadata"]
        )
    
    print(f"  ✅ Loaded {len(regulations)} regulations")
    
    # 2. PROCEDURES
    print("\n🔧 Loading procedures...")
    
    procedures = [
        {
            "title": "Substation Switching Procedure SSP-100",
            "content": """
SUBSTATION SWITCHING PROCEDURE SSP-100
High Voltage Disconnect Switch Operations

APPLICABLE EQUIPMENT:
- 138kV disconnect switches at all substations
- Circuit breakers rated 138kV and above
- Grounding switches and equipment

PRE-SWITCHING CHECKLIST:
1. Obtain switching clearance from System Operations
2. Verify switching order accuracy (switch ID, position)
3. Confirm load conditions and system stability
4. Check weather conditions (no lightning within 5 miles)
5. Inspect equipment condition visually

SWITCHING SEQUENCE:

Opening Procedure:
1. Confirm circuit breaker is OPEN
2. Open disconnect switch (from source side)
3. Open load-side disconnect
4. Close grounding switches
5. Apply safety grounds
6. Post safety tags

Closing Procedure:
1. Remove safety tags and grounds
2. Open grounding switches
3. Close load-side disconnect
4. Close source-side disconnect
5. Close circuit breaker (if authorized)

SAFETY REQUIREMENTS:
- Arc-rated PPE (40 cal/cm² minimum)
- Insulated hot sticks for HV switches
- Two-person crew required
- Communication maintained with System Operations
- Emergency shutdown procedures reviewed before work

VERIFICATION:
- Visual confirmation of switch position
- Three-way communication (field-ops-control)
- Position indicators checked
- Documentation completed in switching log

EMERGENCY CONTACTS:
- System Operations: 555-0100
- Emergency Services: 911
- Line Crew Supervisor: 555-0150

Last Revised: February 2024
Next Review: August 2024
            """,
            "type": "procedure",
            "metadata": {
                "date": "2024-02-15",
                "category": "Operations",
                "equipment_type": "Disconnect Switch",
                "voltage_class": "138kV"
            }
        },
        {
            "title": "Generator Startup Procedure GEN-START-01",
            "content": """
GENERATOR STARTUP PROCEDURE GEN-START-01
Combined Cycle Gas Turbine (CCGT) Plant

FACILITY: Riverside Power Station, Units 1-3
CAPACITY: 500 MW per unit (1500 MW total)

PRE-START CHECKLIST:

Turbine Inspection:
- Visual inspection of turbine housing
- Check vibration sensors operational
- Verify lubrication oil levels and pressure
- Test emergency shutdown systems
- Confirm cooling water flow

Electrical Systems:
- Generator excitation system tested
- Protection relays verified
- Synchronization equipment checked
- Auxiliary power supply confirmed

Gas System:
- Natural gas pressure verified (250-300 psi)
- Emergency fuel shut-off valve tested
- Gas leak detection system armed
- Emissions monitoring system active

STARTUP SEQUENCE:

Phase 1 - Auxiliary Systems (T-30 min):
1. Start cooling water circulation pumps
2. Energize lubrication oil system
3. Activate fire suppression system
4. Start control air compressors

Phase 2 - Turbine Purge (T-20 min):
1. Open turbine inlet guide vanes
2. Run purge cycle (5 minutes minimum)
3. Verify exhaust gas oxygen >19%
4. Confirm no combustible gas present

Phase 3 - Ignition (T-10 min):
1. Start fuel gas booster compressor
2. Light-off pilots and main burners
3. Monitor flame stability
4. Ramp to idle speed (3,000 RPM)

Phase 4 - Synchronization (T-5 min):
1. Accelerate to synchronous speed (3,600 RPM)
2. Adjust excitation for voltage matching
3. Verify phase angle alignment
4. Close generator breaker

Phase 5 - Loading (T+0):
1. Ramp load at 50 MW per 5 minutes
2. Monitor exhaust temperature
3. Adjust fuel/air ratio for emissions
4. Reach target output or grid request

MONITORING PARAMETERS:
- Vibration: <3.0 mils (alarm at 4.0)
- Bearing temperature: <180°F (alarm at 200°F)
- Exhaust temp: 900-1100°F normal range
- NOx emissions: <15 ppm @ 15% O2
- Generator winding temp: <250°F

ABNORMAL CONDITIONS:

Automatic Shutdown Triggers:
- Overspeed >110% (3,960 RPM)
- Low lubrication oil pressure <15 psi
- High vibration >5.0 mils
- Loss of flame detection
- Generator differential relay trip

ENVIRONMENTAL COMPLIANCE:
- Emissions monitoring required per EPA permit
- NOx, CO, and VOC limits enforced
- Continuous emissions monitoring system (CEMS) data logged
- Quarterly emissions reports to state DEQ

CONTACTS:
- Control Room: 555-0200
- Plant Manager: 555-0201
- Grid Operations: 555-0100

Approved by: Michael Torres, Plant Manager
Issue Date: January 10, 2024
            """,
            "type": "procedure",
            "metadata": {
                "date": "2024-01-10",
                "category": "Operations",
                "equipment_type": "Generator",
                "facility": "Riverside Power Station"
            }
        }
    ]
    
    for proc in procedures:
        kb.ingest_document(
            content=proc["content"],
            title=proc["title"],
            doc_type=proc["type"],
            metadata=proc["metadata"]
        )
    
    print(f"  ✅ Loaded {len(procedures)} procedures")
    
    # 3. TECHNICAL MANUALS
    print("\n📖 Loading technical documentation...")
    
    manuals = [
        {
            "title": "ABB Power Transformer Technical Manual - Model ODT-750",
            "content": """
ABB POWER TRANSFORMER TECHNICAL MANUAL
Model: ODT-750 (Oil-Immersed Distribution Transformer)
Rating: 750 MVA, 345/138 kV

SPECIFICATIONS:

Electrical:
- Rated Power: 750 MVA
- Primary Voltage: 345 kV ±10% (31 steps)
- Secondary Voltage: 138 kV
- Cooling: OFAF (Oil Forced Air Forced)
- Impedance: 12.5% on base
- Frequency: 60 Hz

Mechanical:
- Weight (total): 285,000 kg
- Oil volume: 95,000 liters
- Insulation class: 65°C rise
- Sound level: 75 dBA at 1 meter

MAINTENANCE SCHEDULE:

Daily (Automated Monitoring):
- Oil temperature (top and bottom)
- Load current per phase
- Tap changer position
- Cooling system status

Monthly Inspection:
- Visual inspection of bushings
- Check oil level in conservator
- Inspect radiator fans
- Review Buchholz relay status
- Check for oil leaks

Quarterly Oil Analysis:
- Dissolved Gas Analysis (DGA)
  * Hydrogen (H2): <100 ppm normal
  * Methane (CH4): <50 ppm
  * Ethane (C2H6): <30 ppm
  * Ethylene (C2H4): <75 ppm
  * Acetylene (C2H2): <3 ppm (critical)
  
- Oil Quality Tests:
  * Dielectric strength: >30 kV minimum
  * Moisture content: <35 ppm
  * Acidity: <0.2 mg KOH/g
  * Interfacial tension: >24 mN/m

Annual Tests:
- Winding resistance measurement
- Turns ratio test (all tap positions)
- Insulation resistance >1000 MΩ
- Power factor/tan delta test
- Frequency response analysis (FRA)

5-Year Major Inspection:
- Internal inspection (requires outage)
- Core and coil examination
- Tap changer maintenance
- Gasket replacement
- Complete oil replacement and filtration

ALARM THRESHOLDS:

Temperature:
- Top oil: 85°C (alarm), 95°C (trip)
- Winding hotspot: 110°C (alarm), 125°C (trip)

Pressure:
- Sudden pressure relay (Buchholz): Instant trip
- Pressure relief device: 7 psi above normal

Cooling:
- Loss of cooling alarm if >2 fans fail
- Trip if oil flow <60% rated

TROUBLESHOOTING:

High Temperature:
- Check cooling system operation
- Verify load conditions
- Inspect for blocked radiators
- Review oil circulation

Gas Generation (DGA):
- Acetylene indicates arcing
- Ethylene suggests thermal stress
- Hydrogen may indicate corona
- Carbon monoxide indicates cellulose degradation

Oil Contamination:
- High moisture: dry out or oil replacement
- Low dielectric strength: filtration required
- High acidity: reclaim or replace oil

SAFETY:

Arc Flash Hazard:
- Incident energy: 40 cal/cm² at working distance
- Arc flash boundary: 12 feet
- PPE category 4 required for energized work

Oil Spill Response:
- Contain with spill berms
- Notify environmental coordinator
- Use oil absorbent pads
- Document for regulatory reporting

EMERGENCY CONTACTS:
- ABB Service: 1-800-ABB-SERVICE
- Local Service Center: 555-0300
- Technical Support (24/7): 1-800-SUPPORT

Warranty: 5 years from installation
Serial Number Range: TX-750-2018-001 to TX-750-2018-050
            """,
            "type": "manual",
            "metadata": {
                "date": "2018-06-01",
                "manufacturer": "ABB",
                "equipment_type": "Transformer",
                "model": "ODT-750"
            }
        }
    ]
    
    for manual in manuals:
        kb.ingest_document(
            content=manual["content"],
            title=manual["title"],
            doc_type=manual["type"],
            metadata=manual["metadata"]
        )
    
    print(f"  ✅ Loaded {len(manuals)} technical manuals")
    
    # 4. INCIDENT REPORTS
    print("\n⚠️  Loading incident reports...")
    
    incidents = [
        {
            "title": "Incident Report IR-2024-0156 - Riverside Generator Trip",
            "content": """
INCIDENT REPORT: IR-2024-0156

INCIDENT TYPE: Unplanned Generator Trip
DATE: May 3, 2024, 09:45 PDT
FACILITY: Riverside Power Station, Unit 2
REPORTER: David Kim, Control Room Operator

EQUIPMENT INVOLVED:
- Generator Unit 2 (500 MW CCGT)
- Manufacturer: General Electric, Model 7FA
- Serial: GEN-GE-7FA-2019-002
- Last Maintenance: April 15, 2024

INCIDENT SUMMARY:
At 09:45, Generator Unit 2 experienced automatic trip during normal operation
at 450 MW output. Unit was synchronized and loaded for 14 hours prior to trip.

SEQUENCE OF EVENTS:

09:44:58 - Generator vibration alarm on bearing #2
09:45:12 - Vibration increased to 5.2 mils (trip setpoint 5.0)
09:45:15 - Automatic trip initiated by vibration protection
09:45:16 - Generator breaker opened, turbine emergency shutdown
09:45:30 - All auxiliary systems secured
09:50:00 - System Operations notified of unit unavailability

INITIAL FINDINGS:

Vibration Analysis:
- Bearing #2 vibration peaked at 5.4 mils
- Frequency analysis showed 1X rotational component
- Bearing temperature normal (165°F)
- No unusual noise reported by field personnel

Post-Trip Inspection:
- Visual inspection showed no obvious damage
- Alignment checked - within tolerance
- Lubrication oil analysis pending
- Borescope inspection scheduled for May 4

ROOT CAUSE ANALYSIS (Preliminary):
Probable cause: Bearing wear or misalignment. Contributing factors being investigated:
1. Recent maintenance activities (April 15)
2. Bearing oil quality and contamination
3. Foundation settlement or movement
4. Thermal expansion issues

IMPACT ASSESSMENT:

Grid Impact:
- 450 MW generation lost instantaneously
- System frequency dropped to 59.92 Hz (within normal)
- No customer outages resulted
- Adjacent units compensated for loss

Financial Impact:
- Lost revenue: ~$85,000 (estimated 48-hour outage)
- Repair costs: TBD pending inspection
- Replacement power costs: $45,000
- Total estimated impact: $130,000+

Reliability Impact:
- Forced outage rate calculation updated
- Availability factor impacted
- NERC Generating Availability Data System (GADS) report required

CORRECTIVE ACTIONS:

Immediate (Completed):
✅ Unit secured safely
✅ System Operations notified
✅ Initial inspection completed
✅ Alternate generation arranged

Short-term (In Progress):
🔄 Detailed vibration analysis
🔄 Bearing inspection and testing
🔄 Root cause investigation
🔄 Repair/replacement planning

Long-term (Planned):
📋 Review vibration monitoring system setpoints
📋 Enhance predictive maintenance program
📋 Evaluate bearing replacement schedule
📋 Update maintenance procedures if needed

REGULATORY REPORTING:

NERC:
- Event meets NERC EOP-004 reporting criteria (>500 MW loss capability)
- Initial report submitted May 3, 10:30
- Final report due June 2, 2024

FERC:
- Electric Emergency Incident reporting not required (no customer impact)

State PUC:
- Notification completed May 3, 14:00
- Outage extension notifications daily

LESSONS LEARNED:
1. Vibration trends should be monitored more closely
2. Consider lowering alarm thresholds for earlier warning
3. Review maintenance procedures for bearing work
4. Enhance coordination between maintenance and operations

INVESTIGATION STATUS: Open
TARGET RETURN TO SERVICE: May 5, 2024
ACTUAL RETURN TO SERVICE: [Pending]

APPROVALS:
Prepared by: David Kim, Control Room Operator
Reviewed by: Jennifer Lee, Operations Manager
Approved by: Michael Torres, Plant Manager

Report Date: May 3, 2024
Distribution: Operations, Maintenance, Engineering, Compliance
            """,
            "type": "report",
            "metadata": {
                "date": "2024-05-03",
                "category": "Incident",
                "incident_type": "Generator Trip",
                "severity": "Medium",
                "facility": "Riverside Power Station"
            }
        }
    ]
    
    for inc in incidents:
        kb.ingest_document(
            content=inc["content"],
            title=inc["title"],
            doc_type=inc["type"],
            metadata=inc["metadata"]
        )
    
    print(f"  ✅ Loaded {len(incidents)} incident reports")
    
    # Summary
    print("\n" + "=" * 60)
    print("LOADING COMPLETE!")
    print("=" * 60)
    
    stats = kb.get_kb_statistics()
    print("\n📊 Knowledge Base Statistics:")
    for key, value in stats.items():
        print(f"   {key.capitalize()}: {value}")
    
    kb.close()
    
    return True

if __name__ == "__main__":
    load_sample_data()
```

---

## Deployment

### 1. Database Setup

```python
# setup_energy_kb_database.py

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    """Create indexes and constraints for energy KB"""
    
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    )
    
    commands = [
        # Constraints
        "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
        "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT equipment_name IF NOT EXISTS FOR (e:Equipment) REQUIRE e.name IS UNIQUE",
        "CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
        "CREATE CONSTRAINT regulation_code IF NOT EXISTS FOR (r:Regulation) REQUIRE r.code IS UNIQUE",
        "CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE",
        
        # Indexes
        "CREATE INDEX document_type IF NOT EXISTS FOR (d:Document) ON (d.type)",
        "CREATE INDEX document_date IF NOT EXISTS FOR (d:Document) ON (d.date)",
        "CREATE INDEX chunk_position IF NOT EXISTS FOR (c:Chunk) ON (c.position)",
        "CREATE INDEX equipment_type IF NOT EXISTS FOR (e:Equipment) ON (e.type)",
        "CREATE INDEX incident_date IF NOT EXISTS FOR (i:Incident) ON (i.date)",
        "CREATE INDEX incident_severity IF NOT EXISTS FOR (i:Incident) ON (i.severity)",
        
        # Full-text indexes
        "CREATE FULLTEXT INDEX chunk_text_fulltext IF NOT EXISTS FOR (c:Chunk) ON EACH [c.text]",
        "CREATE FULLTEXT INDEX document_title_fulltext IF NOT EXISTS FOR (d:Document) ON EACH [d.title]",
        
        # Vector index
        "CREATE VECTOR INDEX document_embeddings IF NOT EXISTS FOR (c:Chunk) ON (c.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}"
    ]
    
    print("Setting up Energy Knowledge Base database schema...\n")
    
    with driver.session() as session:
        for i, cmd in enumerate(commands, 1):
            try:
                session.run(cmd)
                print(f"✅ [{i}/{len(commands)}] {cmd[:60]}...")
            except Exception as e:
                print(f"⚠️  [{i}/{len(commands)}] {str(e)[:80]}")
    
    print("\n✅ Database setup complete!")
    driver.close()

if __name__ == "__main__":
    setup_database()
```

### 2. Requirements

```txt
# requirements_energy_kb.txt

# Core
neo4j==5.14.0
python-dotenv==1.0.0

# LangChain
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.2

# OpenAI
openai==1.6.1

# Document Processing
pypdf==3.17.1
python-docx==1.1.0

# Web API (optional)
fastapi==0.108.0
uvicorn==0.25.0
pydantic==2.5.0

# Utilities
tenacity==8.2.3
pandas==2.1.4
```

### 3. Environment Configuration

```bash
# .env

# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key

# Application Settings
LOG_LEVEL=INFO
MAX_SESSIONS=100
SESSION_TIMEOUT=3600
```

### 4. Docker Deployment (Optional)

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements_energy_kb.txt .
RUN pip install --no-cache-dir -r requirements_energy_kb.txt

# Copy application
COPY energy_kb_chatbot.py .
COPY web_api.py .
COPY .env .

# Expose port
EXPOSE 8000

# Run API
CMD ["uvicorn", "web_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml

version: '3.8'

services:
  energy-kb-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
```

### 5. Quick Start Guide

```bash
# 1. Install dependencies
pip install -r requirements_energy_kb.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Setup database
python setup_energy_kb_database.py

# 4. Load sample data
python load_sample_data.py

# 5. Test chatbot
python example_chat.py

# 6. Run web API (optional)
uvicorn web_api:app --reload --port 8000
```

---

## Next Steps

1. **Customize for Your Domain**: Adapt entity types and relationships for your specific energy sector needs

2. **Add More Document Types**: Ingest your actual regulations, procedures, manuals, and reports

3. **Enhance Entity Extraction**: Implement domain-specific NER models for better entity recognition

4. **Build Web Interface**: Create a React/Vue frontend for the chatbot

5. **Add Authentication**: Implement user authentication and role-based access control

6. **Monitor and Optimize**: Track query performance and user satisfaction

7. **Integrate with Existing Systems**: Connect to SCADA, EMS, or document management systems

---

## Key Benefits for Energy & Utility Sector

✅ **Regulatory Compliance**: Quickly find applicable regulations and requirements  
✅ **Safety**: Instant access to safety procedures and PPE requirements  
✅ **Troubleshooting**: Search incident history and solutions  
✅ **Training**: Onboard new employees with conversational KB access  
✅ **Audit Support**: Traceable answers with source citations  
✅ **Operational Efficiency**: Reduce time searching for information  
✅ **Knowledge Preservation**: Capture and share institutional knowledge  

