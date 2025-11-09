"""Embeddings module for generating vector representations of utility network data."""

from typing import List, Dict, Any, Optional
import hashlib


class EmbeddingsGenerator:
    """Generate embeddings for utility network documents and queries."""
    
    def __init__(self, model_name: str = "sentence-transformers", model_path: Optional[str] = None):
        """
        Initialize embeddings generator.
        
        Args:
            model_name: Name of embedding model ('sentence-transformers', 'openai', 'mock')
            model_path: Path to HuggingFace model (default: 'all-MiniLM-L6-v2')
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        
        if model_name == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                model_path = model_path or 'all-MiniLM-L6-v2'
                self.model = SentenceTransformer(model_path)
                self.dimension = self.model.get_sentence_embedding_dimension()
                print(f"✓ Loaded HuggingFace model: {model_path} (dim: {self.dimension})")
            except ImportError:
                print("⚠ sentence-transformers not installed. Install with: pip install sentence-transformers")
                print("  Falling back to mock embeddings")
                self.model_name = "mock"
                self.dimension = 384
            except Exception as e:
                print(f"⚠ Error loading model: {e}")
                print("  Falling back to mock embeddings")
                self.model_name = "mock"
                self.dimension = 384
        elif model_name == "openai":
            self.dimension = 1536  # OpenAI ada-002 dimension
        else:
            self.dimension = 384  # Mock dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing embedding vector
        """
        if self.model_name == "sentence-transformers" and self.model is not None:
            # Use HuggingFace sentence-transformers
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        
        elif self.model_name == "openai":
            # Use OpenAI API (requires configuration)
            try:
                import openai
                response = openai.Embedding.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                return response['data'][0]['embedding']
            except Exception as e:
                print(f"⚠ OpenAI API error: {e}")
                return self._generate_mock_embedding(text)
        
        else:
            # Fallback to mock embeddings
            return self._generate_mock_embedding(text)
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding for testing/fallback.
        
        Args:
            text: Text to embed
            
        Returns:
            Mock embedding vector
        """
        # Simple hash-based mock embedding for demonstration
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        
        # Generate deterministic "embedding" from hash
        embedding = []
        for i in range(self.dimension):
            seed = hash_val + i
            val = (seed % 1000) / 1000.0 - 0.5  # Normalize to [-0.5, 0.5]
            embedding.append(val)
        
        return embedding
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.model_name == "sentence-transformers" and self.model is not None:
            # Batch encoding is more efficient
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.tolist()
        
        elif self.model_name == "openai":
            # OpenAI batch processing
            try:
                import openai
                response = openai.Embedding.create(
                    input=texts,
                    model="text-embedding-ada-002"
                )
                return [item['embedding'] for item in response['data']]
            except Exception as e:
                print(f"⚠ OpenAI API error: {e}")
                return [self._generate_mock_embedding(text) for text in texts]
        
        else:
            # Fallback
            return [self._generate_mock_embedding(text) for text in texts]
    
    def embed_pipeline(self, pipeline_data: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for pipeline data.
        
        Args:
            pipeline_data: Pipeline information dictionary
            
        Returns:
            Embedding vector
        """
        # Create text representation
        text = f"""
        Pipeline {pipeline_data.get('id', 'unknown')}
        Type: {pipeline_data.get('type', 'unknown')}
        Material: {pipeline_data.get('material', 'unknown')}
        Diameter: {pipeline_data.get('diameter_mm', 0)}mm
        Length: {pipeline_data.get('length_m', 0)}m
        Status: {pipeline_data.get('status', 'unknown')}
        Region: {pipeline_data.get('region', 'unknown')}
        Age: {pipeline_data.get('age_years', 0)} years
        """
        
        return self.generate_embedding(text.strip())
    
    def embed_customer(self, customer_data: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for customer data.
        
        Args:
            customer_data: Customer information dictionary
            
        Returns:
            Embedding vector
        """
        text = f"""
        Customer {customer_data.get('id', 'unknown')}
        Name: {customer_data.get('name', 'unknown')}
        Type: {customer_data.get('type', 'unknown')}
        City: {customer_data.get('city', 'unknown')}
        Status: {customer_data.get('status', 'unknown')}
        Account age: {customer_data.get('account_age_years', 0)} years
        """
        
        return self.generate_embedding(text.strip())
    
    def embed_incident(self, incident_data: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for incident data.
        
        Args:
            incident_data: Incident information dictionary
            
        Returns:
            Embedding vector
        """
        text = f"""
        Incident {incident_data.get('id', 'unknown')}
        Type: {incident_data.get('type', 'unknown')}
        Severity: {incident_data.get('severity', 'unknown')}
        Status: {incident_data.get('status', 'unknown')}
        Description: {incident_data.get('description', '')}
        Location: {incident_data.get('region', 'unknown')}
        """
        
        return self.generate_embedding(text.strip())
    
    def embed_service_request(self, request_data: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for service request data.
        
        Args:
            request_data: Service request information dictionary
            
        Returns:
            Embedding vector
        """
        text = f"""
        Service Request {request_data.get('id', 'unknown')}
        Type: {request_data.get('type', 'unknown')}
        Priority: {request_data.get('priority', 'unknown')}
        Status: {request_data.get('status', 'unknown')}
        Description: {request_data.get('description', '')}
        """
        
        return self.generate_embedding(text.strip())
    
    def calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        if len(emb1) != len(emb2):
            raise ValueError("Embeddings must have same dimension")
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        
        mag1 = sum(a * a for a in emb1) ** 0.5
        mag2 = sum(b * b for b in emb2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        similarity = dot_product / (mag1 * mag2)
        
        # Normalize to 0-1 range
        return (similarity + 1) / 2


# Example configurations for different embedding models
EMBEDDING_CONFIGS = {
    "all-MiniLM-L6-v2": {
        "model_name": "sentence-transformers",
        "model_path": "all-MiniLM-L6-v2",
        "dimension": 384,
        "description": "Fast, lightweight model (80MB). Good for general use.",
        "speed": "very fast",
        "quality": "good"
    },
    "all-mpnet-base-v2": {
        "model_name": "sentence-transformers",
        "model_path": "all-mpnet-base-v2",
        "dimension": 768,
        "description": "Best quality sentence-transformers model (420MB).",
        "speed": "moderate",
        "quality": "excellent"
    },
    "multi-qa-MiniLM-L6-cos-v1": {
        "model_name": "sentence-transformers",
        "model_path": "multi-qa-MiniLM-L6-cos-v1",
        "dimension": 384,
        "description": "Optimized for question-answering (80MB).",
        "speed": "very fast",
        "quality": "good"
    },
    "paraphrase-multilingual-MiniLM-L12-v2": {
        "model_name": "sentence-transformers",
        "model_path": "paraphrase-multilingual-MiniLM-L12-v2",
        "dimension": 384,
        "description": "Supports 50+ languages (420MB).",
        "speed": "fast",
        "quality": "good"
    },
    "openai-ada-002": {
        "model_name": "openai",
        "model_path": "text-embedding-ada-002",
        "dimension": 1536,
        "description": "OpenAI's embedding model. Requires API key.",
        "speed": "depends on API",
        "quality": "excellent"
    }
}


def get_recommended_model(use_case: str = "general") -> Dict[str, Any]:
    """
    Get recommended embedding model based on use case.
    
    Args:
        use_case: 'general', 'qa' (question-answering), 'multilingual', 'best_quality', 'fastest'
        
    Returns:
        Model configuration dictionary
    """
    recommendations = {
        "general": EMBEDDING_CONFIGS["all-MiniLM-L6-v2"],
        "qa": EMBEDDING_CONFIGS["multi-qa-MiniLM-L6-cos-v1"],
        "multilingual": EMBEDDING_CONFIGS["paraphrase-multilingual-MiniLM-L12-v2"],
        "best_quality": EMBEDDING_CONFIGS["all-mpnet-base-v2"],
        "fastest": EMBEDDING_CONFIGS["all-MiniLM-L6-v2"],
        "production": EMBEDDING_CONFIGS["openai-ada-002"]
    }
    
    return recommendations.get(use_case, EMBEDDING_CONFIGS["all-MiniLM-L6-v2"])


def create_embeddings_generator(use_case: str = "general") -> EmbeddingsGenerator:
    """
    Create embeddings generator with recommended settings.
    
    Args:
        use_case: Use case for embeddings
        
    Returns:
        Configured EmbeddingsGenerator instance
    """
    config = get_recommended_model(use_case)
    
    return EmbeddingsGenerator(
        model_name=config["model_name"],
        model_path=config.get("model_path")
    )


def install_instructions():
    """Print installation instructions for embedding models."""
    print("\n" + "="*60)
    print("EMBEDDING MODEL INSTALLATION")
    print("="*60)
    
    print("\n1. Install sentence-transformers (HuggingFace):")
    print("   pip install sentence-transformers")
    
    print("\n2. First run will download the model (~80-420MB depending on model)")
    
    print("\n3. For OpenAI embeddings:")
    print("   pip install openai")
    print("   export OPENAI_API_KEY='your-api-key'")
    
    print("\n4. Recommended models by use case:")
    for use_case, config in [
        ("General use", EMBEDDING_CONFIGS["all-MiniLM-L6-v2"]),
        ("Best quality", EMBEDDING_CONFIGS["all-mpnet-base-v2"]),
        ("Question answering", EMBEDDING_CONFIGS["multi-qa-MiniLM-L6-cos-v1"]),
        ("Multilingual", EMBEDDING_CONFIGS["paraphrase-multilingual-MiniLM-L12-v2"])
    ]:
        print(f"\n   {use_case}:")
        print(f"     Model: {config['model_path']}")
        print(f"     Size: {config['description']}")
        print(f"     Speed: {config['speed']}, Quality: {config['quality']}")
    
    print("\n" + "="*60)
