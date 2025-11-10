"""
Main application - Neo4j RAG Knowledge Base with LangChain and Ollama
"""
import sys
from pathlib import Path
from typing import Optional
import argparse
import logging

from config import AppConfig
from document_loader import MultimodalDocumentLoader
from ollama_provider import OllamaLLMProvider, OllamaEmbeddingProvider, OllamaModelManager
from neo4j_kb import Neo4jKnowledgeBase
from rag_system import Neo4jRAGSystem, ConversationalRAG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jRAGApp:
    """Main application for Neo4j RAG Knowledge Base"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize application
        
        Args:
            config: Application configuration
        """
        self.config = config or AppConfig.from_env()
        self.config.validate()
        
        # Initialize components
        self.model_manager = None
        self.embedding_provider = None
        self.llm_provider = None
        self.knowledge_base = None
        self.rag_system = None
        
        logger.info("Neo4j RAG Application initialized")
    
    def setup(self):
        """Setup all components"""
        logger.info("Setting up application components...")
        
        # Setup Ollama models
        self.model_manager = OllamaModelManager(
            base_url=self.config.ollama.base_url
        )
        
        # Ensure required models are available
        logger.info(f"Checking for LLM model: {self.config.ollama.llm_model}")
        self.model_manager.ensure_model(self.config.ollama.llm_model)
        
        logger.info(f"Checking for embedding model: {self.config.ollama.embedding_model}")
        self.model_manager.ensure_model(self.config.ollama.embedding_model)
        
        # Initialize embedding provider
        self.embedding_provider = OllamaEmbeddingProvider(
            model=self.config.ollama.embedding_model,
            base_url=self.config.ollama.base_url,
        )
        
        # Initialize LLM provider
        self.llm_provider = OllamaLLMProvider(
            model=self.config.ollama.llm_model,
            base_url=self.config.ollama.base_url,
            temperature=self.config.ollama.temperature,
            top_k=self.config.ollama.top_k,
            top_p=self.config.ollama.top_p,
        )
        
        # Initialize Neo4j knowledge base
        self.knowledge_base = Neo4jKnowledgeBase(
            uri=self.config.neo4j.uri,
            username=self.config.neo4j.username,
            password=self.config.neo4j.password,
            database=self.config.neo4j.database,
            embedding_function=self.embedding_provider.get_embeddings(),
        )
        
        # Create indexes
        self.knowledge_base.create_indexes()
        
        logger.info("Application setup completed successfully")
    
    def load_documents(self, documents_path: Optional[str] = None):
        """
        Load and process documents into knowledge base
        
        Args:
            documents_path: Path to documents directory
        """
        if not self.knowledge_base:
            raise RuntimeError("Knowledge base not initialized. Call setup() first.")
        
        documents_path = documents_path or self.config.document.documents_path
        
        logger.info(f"Loading documents from: {documents_path}")
        
        # Initialize document loader
        loader = MultimodalDocumentLoader(
            chunk_size=self.config.document.chunk_size,
            chunk_overlap=self.config.document.chunk_overlap,
            supported_extensions=self.config.document.supported_extensions,
        )
        
        # Load and split documents
        chunks = loader.load_and_split(documents_path, is_directory=True)
        
        if not chunks:
            logger.warning("No documents found to load")
            return
        
        logger.info(f"Loaded and split into {len(chunks)} chunks")
        
        # Add documents to knowledge base
        self.knowledge_base.add_documents(chunks)
        
        logger.info("Documents successfully added to knowledge base")
    
    def initialize_rag(self, conversational: bool = False):
        """
        Initialize RAG system
        
        Args:
            conversational: Use conversational RAG with history
        """
        if not self.knowledge_base:
            raise RuntimeError("Knowledge base not initialized. Call setup() first.")
        
        if conversational:
            self.rag_system = ConversationalRAG(
                knowledge_base=self.knowledge_base,
                llm=self.llm_provider.get_llm(),
                retrieval_k=self.config.rag.retrieval_k,
            )
            logger.info("Initialized Conversational RAG system")
        else:
            self.rag_system = Neo4jRAGSystem(
                knowledge_base=self.knowledge_base,
                llm=self.llm_provider.get_llm(),
                retrieval_k=self.config.rag.retrieval_k,
                enable_hybrid_search=self.config.rag.enable_hybrid_search,
            )
            logger.info("Initialized standard RAG system")
    
    def query(self, question: str, verbose: bool = False) -> dict:
        """
        Query the knowledge base
        
        Args:
            question: User question
            verbose: Enable verbose output
            
        Returns:
            Query result
        """
        if not self.rag_system:
            raise RuntimeError("RAG system not initialized. Call initialize_rag() first.")
        
        return self.rag_system.query(question, return_source_documents=True, verbose=verbose)
    
    def start_chat(self, verbose: bool = False):
        """
        Start interactive chat session
        
        Args:
            verbose: Enable verbose output
        """
        if not self.rag_system:
            raise RuntimeError("RAG system not initialized. Call initialize_rag() first.")
        
        self.rag_system.chat(verbose=verbose)
    
    def get_stats(self) -> dict:
        """Get knowledge base statistics"""
        if not self.knowledge_base:
            return {"error": "Knowledge base not initialized"}
        
        return {
            "document_count": self.knowledge_base.get_document_count(),
            "llm_model": self.config.ollama.llm_model,
            "embedding_model": self.config.ollama.embedding_model,
            "neo4j_uri": self.config.neo4j.uri,
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.knowledge_base:
            self.knowledge_base.close()
        logger.info("Cleanup completed")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Neo4j RAG Knowledge Base with LangChain and Ollama"
    )
    
    parser.add_argument(
        "--mode",
        choices=["load", "query", "chat"],
        required=True,
        help="Operation mode: load documents, single query, or interactive chat"
    )
    
    parser.add_argument(
        "--documents",
        type=str,
        help="Path to documents directory (for load mode)"
    )
    
    parser.add_argument(
        "--question",
        type=str,
        help="Question to ask (for query mode)"
    )
    
    parser.add_argument(
        "--conversational",
        action="store_true",
        help="Enable conversational mode with history"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all documents from knowledge base before loading"
    )
    
    args = parser.parse_args()
    
    # Create and setup application
    app = Neo4jRAGApp()
    
    try:
        app.setup()
        
        if args.clear:
            logger.info("Clearing knowledge base...")
            app.knowledge_base.delete_all_documents()
        
        if args.mode == "load":
            if not args.documents:
                logger.error("--documents argument required for load mode")
                sys.exit(1)
            
            app.load_documents(args.documents)
            stats = app.get_stats()
            logger.info(f"Knowledge base stats: {stats}")
        
        elif args.mode == "query":
            if not args.question:
                logger.error("--question argument required for query mode")
                sys.exit(1)
            
            app.initialize_rag(conversational=args.conversational)
            result = app.query(args.question, verbose=args.verbose)
            
            print("\n" + "=" * 80)
            print("ANSWER:")
            print("=" * 80)
            print(result["answer"])
            
            if result.get("source_documents"):
                print("\n" + "=" * 80)
                print("SOURCE DOCUMENTS:")
                print("=" * 80)
                for i, doc in enumerate(result["source_documents"], 1):
                    print(f"\n[{i}] {doc.metadata.get('file_name', 'Unknown')}")
                    print("-" * 40)
                    preview = doc.page_content[:200] + "..."
                    print(preview)
        
        elif args.mode == "chat":
            app.initialize_rag(conversational=args.conversational)
            app.start_chat(verbose=args.verbose)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        sys.exit(1)
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
