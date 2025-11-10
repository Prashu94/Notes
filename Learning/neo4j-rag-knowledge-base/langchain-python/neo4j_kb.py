"""
Neo4j Knowledge Graph Store with Vector Search
"""
from typing import List, Optional, Dict, Any
from langchain.schema import Document
from langchain_community.vectorstores import Neo4jVector
from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jKnowledgeBase:
    """Neo4j-based knowledge base with vector search capabilities"""
    
    def __init__(
        self,
        uri: str,
        username: str,
        password: str,
        database: str = "neo4j",
        embedding_function: Optional[Any] = None,
    ):
        """
        Initialize Neo4j knowledge base
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
            database: Database name
            embedding_function: Embedding function for vectors
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.embedding_function = embedding_function
        
        # Initialize Neo4j connections
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.graph = Neo4jGraph(
            url=uri,
            username=username,
            password=password,
            database=database
        )
        
        # Vector store will be initialized when documents are added
        self.vector_store: Optional[Neo4jVector] = None
        
        logger.info(f"Connected to Neo4j at {uri}")
    
    def create_indexes(self):
        """Create necessary indexes and constraints"""
        with self.driver.session(database=self.database) as session:
            # Create vector index for embeddings
            try:
                session.run("""
                    CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
                    FOR (d:Document)
                    ON d.embedding
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 768,
                        `vector.similarity_function`: 'cosine'
                    }}
                """)
                logger.info("Created vector index for documents")
            except Exception as e:
                logger.warning(f"Vector index might already exist: {e}")
            
            # Create text index for full-text search
            try:
                session.run("""
                    CREATE FULLTEXT INDEX document_content IF NOT EXISTS
                    FOR (d:Document)
                    ON EACH [d.content, d.title]
                """)
                logger.info("Created full-text index for documents")
            except Exception as e:
                logger.warning(f"Full-text index might already exist: {e}")
            
            # Create constraints
            try:
                session.run("""
                    CREATE CONSTRAINT document_id IF NOT EXISTS
                    FOR (d:Document)
                    REQUIRE d.id IS UNIQUE
                """)
                logger.info("Created unique constraint on document ID")
            except Exception as e:
                logger.warning(f"Constraint might already exist: {e}")
    
    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of Document objects
            batch_size: Number of documents to process in each batch
            
        Returns:
            List of document IDs
        """
        if not self.embedding_function:
            raise ValueError("Embedding function not set")
        
        logger.info(f"Adding {len(documents)} documents to Neo4j")
        
        # Initialize or update vector store
        if self.vector_store is None:
            self.vector_store = Neo4jVector.from_documents(
                documents=documents[:batch_size],
                embedding=self.embedding_function,
                url=self.uri,
                username=self.username,
                password=self.password,
                database=self.database,
                index_name="document_embeddings",
                node_label="Document",
                text_node_property="content",
                embedding_node_property="embedding",
            )
            
            # Add remaining documents in batches
            for i in range(batch_size, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                self.vector_store.add_documents(batch)
                logger.info(f"Processed {min(i + batch_size, len(documents))}/{len(documents)} documents")
        else:
            # Add all documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                self.vector_store.add_documents(batch)
                logger.info(f"Processed {min(i + batch_size, len(documents))}/{len(documents)} documents")
        
        # Create graph relationships
        self._create_document_relationships(documents)
        
        logger.info(f"Successfully added {len(documents)} documents")
        return [doc.metadata.get("id", str(i)) for i, doc in enumerate(documents)]
    
    def _create_document_relationships(self, documents: List[Document]):
        """Create relationships between documents based on metadata"""
        with self.driver.session(database=self.database) as session:
            for doc in documents:
                metadata = doc.metadata
                
                # Create source file node and relationship
                if "source" in metadata:
                    session.run("""
                        MERGE (f:File {path: $source})
                        SET f.name = $file_name,
                            f.type = $file_type
                        WITH f
                        MATCH (d:Document {content: $content})
                        MERGE (d)-[:FROM_FILE]->(f)
                    """, {
                        "source": metadata.get("source", ""),
                        "file_name": metadata.get("file_name", ""),
                        "file_type": metadata.get("file_type", ""),
                        "content": doc.page_content[:100]  # Use content prefix for matching
                    })
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search using vector embeddings
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar documents
        """
        if not self.vector_store:
            raise ValueError("No documents in knowledge base. Add documents first.")
        
        results = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter
        )
        
        logger.info(f"Found {len(results)} similar documents")
        return results
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        if not self.vector_store:
            raise ValueError("No documents in knowledge base. Add documents first.")
        
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        vector_weight: float = 0.7
    ) -> List[Document]:
        """
        Perform hybrid search combining vector and full-text search
        
        Args:
            query: Search query
            k: Number of results to return
            vector_weight: Weight for vector search (0-1)
            
        Returns:
            List of documents
        """
        # Vector search
        vector_results = self.similarity_search_with_score(query, k=k * 2)
        
        # Full-text search
        with self.driver.session(database=self.database) as session:
            text_results = session.run("""
                CALL db.index.fulltext.queryNodes('document_content', $query)
                YIELD node, score
                RETURN node.content AS content, score
                LIMIT $k
            """, {"query": query, "k": k * 2})
            
            text_docs = []
            for record in text_results:
                doc = Document(
                    page_content=record["content"],
                    metadata={"score": record["score"]}
                )
                text_docs.append((doc, record["score"]))
        
        # Combine and rerank results
        combined_results = self._combine_search_results(
            vector_results,
            text_docs,
            vector_weight
        )
        
        return [doc for doc, _ in combined_results[:k]]
    
    def _combine_search_results(
        self,
        vector_results: List[tuple[Document, float]],
        text_results: List[tuple[Document, float]],
        vector_weight: float
    ) -> List[tuple[Document, float]]:
        """Combine and normalize search results"""
        # Normalize scores
        def normalize_scores(results):
            if not results:
                return []
            scores = [score for _, score in results]
            min_score = min(scores)
            max_score = max(scores)
            score_range = max_score - min_score if max_score != min_score else 1
            
            return [
                (doc, (score - min_score) / score_range)
                for doc, score in results
            ]
        
        normalized_vector = normalize_scores(vector_results)
        normalized_text = normalize_scores(text_results)
        
        # Combine scores
        doc_scores = {}
        
        for doc, score in normalized_vector:
            key = doc.page_content[:100]
            doc_scores[key] = (doc, score * vector_weight)
        
        for doc, score in normalized_text:
            key = doc.page_content[:100]
            if key in doc_scores:
                existing_doc, existing_score = doc_scores[key]
                doc_scores[key] = (existing_doc, existing_score + score * (1 - vector_weight))
            else:
                doc_scores[key] = (doc, score * (1 - vector_weight))
        
        # Sort by combined score
        combined = sorted(doc_scores.values(), key=lambda x: x[1], reverse=True)
        return combined
    
    def get_document_count(self) -> int:
        """Get total number of documents in the knowledge base"""
        with self.driver.session(database=self.database) as session:
            result = session.run("MATCH (d:Document) RETURN count(d) as count")
            return result.single()["count"]
    
    def delete_all_documents(self):
        """Delete all documents from the knowledge base"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Deleted all documents from knowledge base")
        
        self.vector_store = None
    
    def close(self):
        """Close Neo4j connections"""
        self.driver.close()
        logger.info("Closed Neo4j connections")
