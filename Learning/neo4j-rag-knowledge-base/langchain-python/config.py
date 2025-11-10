"""
Configuration settings for Neo4j RAG Knowledge Base
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Neo4jConfig:
    """Neo4j database configuration"""
    uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "password")
    database: str = os.getenv("NEO4J_DATABASE", "neo4j")


@dataclass
class OllamaConfig:
    """Ollama model configuration"""
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_model: str = os.getenv("OLLAMA_LLM_MODEL", "llama3.2")
    embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    top_k: int = int(os.getenv("OLLAMA_TOP_K", "40"))
    top_p: float = float(os.getenv("OLLAMA_TOP_P", "0.9"))


@dataclass
class DocumentConfig:
    """Document processing configuration"""
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    supported_extensions: tuple = (".pdf", ".txt")
    documents_path: str = os.getenv("DOCUMENTS_PATH", "../sample-data")


@dataclass
class RAGConfig:
    """RAG system configuration"""
    retrieval_k: int = int(os.getenv("RETRIEVAL_K", "5"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    enable_hybrid_search: bool = os.getenv("ENABLE_HYBRID_SEARCH", "true").lower() == "true"
    enable_reranking: bool = os.getenv("ENABLE_RERANKING", "false").lower() == "true"


class AppConfig:
    """Main application configuration"""
    
    def __init__(self):
        self.neo4j = Neo4jConfig()
        self.ollama = OllamaConfig()
        self.document = DocumentConfig()
        self.rag = RAGConfig()
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables"""
        return cls()
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        required_fields = [
            (self.neo4j.uri, "NEO4J_URI"),
            (self.neo4j.username, "NEO4J_USERNAME"),
            (self.neo4j.password, "NEO4J_PASSWORD"),
            (self.ollama.base_url, "OLLAMA_BASE_URL"),
        ]
        
        for value, name in required_fields:
            if not value:
                raise ValueError(f"Required configuration {name} is not set")
        
        return True
