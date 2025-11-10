"""
Ollama integration for LLM and embeddings
"""
from typing import List, Optional, Any
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaLLMProvider:
    """Ollama LLM provider for text generation"""
    
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.9,
        streaming: bool = False,
    ):
        """
        Initialize Ollama LLM
        
        Args:
            model: Model name (e.g., llama3.2, mistral, etc.)
            base_url: Ollama server URL
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter
            streaming: Enable streaming output
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        
        callback_manager = None
        if streaming:
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        self.llm = Ollama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            callback_manager=callback_manager,
        )
        
        logger.info(f"Initialized Ollama LLM with model: {model}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        return self.llm.invoke(prompt)
    
    def get_llm(self) -> Ollama:
        """Get the underlying LLM instance"""
        return self.llm


class OllamaEmbeddingProvider:
    """Ollama embedding provider for vector representations"""
    
    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
    ):
        """
        Initialize Ollama embeddings
        
        Args:
            model: Embedding model name
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        
        self.embeddings = OllamaEmbeddings(
            model=model,
            base_url=base_url,
        )
        
        logger.info(f"Initialized Ollama embeddings with model: {model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents
        
        Args:
            texts: List of text documents
            
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)
    
    def get_embeddings(self) -> OllamaEmbeddings:
        """Get the underlying embeddings instance"""
        return self.embeddings


class OllamaModelManager:
    """Manage Ollama models - pull, list, remove"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize model manager
        
        Args:
            base_url: Ollama server URL
        """
        self.base_url = base_url
        import requests
        self.requests = requests
    
    def list_models(self) -> List[dict]:
        """List available models"""
        try:
            response = self.requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            logger.info(f"Found {len(models)} models")
            return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Pulling model: {model_name}")
            response = self.requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            )
            response.raise_for_status()
            logger.info(f"Successfully pulled model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def check_model_exists(self, model_name: str) -> bool:
        """
        Check if a model exists locally
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model exists
        """
        models = self.list_models()
        return any(model.get("name", "").startswith(model_name) for model in models)
    
    def ensure_model(self, model_name: str) -> bool:
        """
        Ensure a model exists, pull if necessary
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model is available
        """
        if self.check_model_exists(model_name):
            logger.info(f"Model {model_name} already exists")
            return True
        
        logger.info(f"Model {model_name} not found, pulling...")
        return self.pull_model(model_name)
