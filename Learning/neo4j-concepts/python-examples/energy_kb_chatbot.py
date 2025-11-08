"""
Energy & Utility Knowledge Base with RAG Chatbot
Complete implementation for chatting with domain-specific knowledge base
"""

import os
import uuid
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from neo4j import GraphDatabase
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import BaseRetriever, Document, HumanMessage, AIMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class EnergyKnowledgeBase:
    """Energy & Utility Knowledge Base with RAG Chatbot"""
    
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
    
    def ingest_document(self, content: str, title: str, doc_type: str,
                       metadata: Dict = None) -> str:
        """Ingest document into knowledge base"""
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
    
    def create_chat_session(self, session_name: str = None) -> str:
        """Create a new chat session"""
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

Current Question: {question}

Provide a comprehensive answer with citations:"""

        # Create memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create conversational chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=memory,
            return_source_documents=True,
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
        """Send message in chat session"""
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
    
    def search(self, query: str, filters: Dict = None, k: int = 5) -> List[Dict]:
        """Search knowledge base with hybrid approach"""
        embedding = self.embeddings.embed_query(query)
        filter_clause = self._build_filter_clause(filters)
        
        cypher = f"""
        CALL db.index.vector.queryNodes('document_embeddings', $k * 2, $embedding)
        YIELD node AS chunk, score
        
        MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        WHERE {filter_clause}
        
        OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity)
        
        WITH chunk, doc, score, collect(DISTINCT entity.name) AS entities
        
        RETURN chunk.text AS text,
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
            record = result.single()
            return dict(record) if record else {}
    
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
        
        return " AND ".join(conditions) if conditions else "true"
    
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
        query_lower = query.lower()
        
        energy_terms = [
            "transformer", "generator", "substation", "transmission",
            "distribution", "meter", "outage", "voltage", "power plant",
            "renewable", "solar", "wind", "grid", "ferc", "nerc"
        ]
        
        found = [term for term in energy_terms if term in query_lower]
        return found


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
        
        WITH c
        UNWIND $entities AS entity
        
        MERGE (e:Entity {name: entity.name})
        ON CREATE SET e.type = entity.type, e.createdAt = datetime()
        
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
        # Simple extraction - in production, use NER model
        entities = []
        
        # Common equipment types
        equipment_keywords = ["transformer", "generator", "turbine", "breaker", "substation"]
        for keyword in equipment_keywords:
            if keyword in text.lower():
                entities.append({"name": keyword.title(), "type": "Equipment"})
        
        # Regulations
        if "NERC" in text or "OSHA" in text or "FERC" in text:
            for word in text.split():
                if any(reg in word for reg in ["NERC", "OSHA", "FERC"]):
                    entities.append({"name": word, "type": "Regulation"})
        
        return entities[:10]  # Limit entities


class EnergyUtilityRetriever(BaseRetriever):
    """Custom retriever for energy sector knowledge base"""
    
    def __init__(self, driver, embeddings, database="neo4j", k: int = 5):
        super().__init__()
        self.driver = driver
        self.embeddings = embeddings
        self.database = database
        self.k = k
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents with energy sector context"""
        query_embedding = self.embeddings.embed_query(query)
        
        cypher = """
        CALL db.index.vector.queryNodes('document_embeddings', $k, $embedding)
        YIELD node AS chunk, score
        
        MATCH (chunk)<-[:CONTAINS]-(doc:Document)
        OPTIONAL MATCH (chunk)-[:MENTIONS]->(entity)
        
        WITH chunk, doc, score,
             collect(DISTINCT {name: entity.name, type: labels(entity)[0]}) AS entities
        
        RETURN chunk.text AS text,
               doc.title AS title,
               doc.type AS docType,
               doc.date AS date,
               score,
               entities
        ORDER BY score DESC
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, k=self.k, embedding=query_embedding)
            
            documents = []
            for record in result:
                context = record["text"]
                
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


# Example usage
if __name__ == "__main__":
    # Initialize KB
    kb = EnergyKnowledgeBase()
    
    # Create chat session
    session_id = kb.create_chat_session("Demo Session")
    
    # Ask questions
    questions = [
        "What are the safety requirements for transformer maintenance?",
        "What PPE is required?",
        "Tell me about recent incidents"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        response = kb.chat(session_id, question)
        print(f"\nA: {response['answer']}")
        print(f"\nSources: {len(response['sources'])} documents")
    
    kb.close()
