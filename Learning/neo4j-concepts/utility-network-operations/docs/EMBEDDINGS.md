# Embeddings Guide

## Overview

The embeddings module provides vector representations for utility network data, enabling semantic search and similarity-based retrieval for the RAG chatbot.

## Features

### Supported Models

1. **HuggingFace Sentence Transformers** (Recommended)
   - Fast, local inference
   - No API costs
   - Multiple model options
   - Offline capability

2. **OpenAI Embeddings**
   - High quality
   - Requires API key
   - Pay per use

3. **Mock Embeddings**
   - Fallback for testing
   - No dependencies

## Installation

```bash
# Install sentence-transformers (recommended)
pip install sentence-transformers

# Or for OpenAI
pip install openai
export OPENAI_API_KEY='your-key'
```

## Quick Start

```python
from src.chatbot.embeddings import create_embeddings_generator

# Create embeddings generator
embeddings = create_embeddings_generator("qa")  # Optimized for Q&A

# Generate embedding for text
text = "Water leak detected at Main Street"
embedding = embeddings.generate_embedding(text)

# Generate batch embeddings
texts = ["leak detected", "billing inquiry", "meter issue"]
embeddings_list = embeddings.generate_batch_embeddings(texts)

# Calculate similarity
similarity = embeddings.calculate_similarity(embedding1, embedding2)
```

## Available Models

### all-MiniLM-L6-v2 (Default)
- **Size**: 80MB
- **Dimension**: 384
- **Speed**: Very Fast
- **Quality**: Good
- **Best for**: General use, fast inference

### all-mpnet-base-v2
- **Size**: 420MB
- **Dimension**: 768
- **Speed**: Moderate
- **Quality**: Excellent
- **Best for**: Best quality results

### multi-qa-MiniLM-L6-cos-v1
- **Size**: 80MB
- **Dimension**: 384
- **Speed**: Very Fast
- **Quality**: Good
- **Best for**: Question-answering (RAG chatbot)

### paraphrase-multilingual-MiniLM-L12-v2
- **Size**: 420MB
- **Dimension**: 384
- **Speed**: Fast
- **Quality**: Good
- **Best for**: Multilingual support (50+ languages)

## Usage Examples

### Basic Usage

```python
from src.chatbot.embeddings import EmbeddingsGenerator

# Initialize with specific model
embeddings = EmbeddingsGenerator(
    model_name="sentence-transformers",
    model_path="all-MiniLM-L6-v2"
)

# Generate embeddings
text = "Pipeline pressure anomaly detected"
embedding = embeddings.generate_embedding(text)

print(f"Dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

### Batch Processing

```python
# More efficient for multiple texts
texts = [
    "Customer billing inquiry",
    "Leak detection alert",
    "Meter battery low"
]

embeddings = embeddings.generate_batch_embeddings(texts)
# Returns list of embedding vectors
```

### Semantic Search

```python
# Search for similar documents
query = "water pressure problem"
documents = [
    "Leak in downtown area",
    "Low water pressure reported",
    "Meter battery issue",
    "Pipeline burst"
]

# Generate embeddings
query_emb = embeddings.generate_embedding(query)
doc_embeddings = embeddings.generate_batch_embeddings(documents)

# Calculate similarities
results = []
for i, doc in enumerate(documents):
    similarity = embeddings.calculate_similarity(query_emb, doc_embeddings[i])
    results.append((doc, similarity))

# Sort by relevance
results.sort(key=lambda x: x[1], reverse=True)

for doc, score in results:
    print(f"[{score:.3f}] {doc}")
```

### Domain-Specific Embeddings

```python
# Embed pipeline data
pipeline_data = {
    "id": "PIPE-001",
    "type": "water_main",
    "material": "ductile_iron",
    "status": "active",
    "region": "Downtown"
}

pipeline_emb = embeddings.embed_pipeline(pipeline_data)

# Embed customer data
customer_data = {
    "id": "CUST-001",
    "name": "John Doe",
    "type": "residential",
    "city": "San Francisco"
}

customer_emb = embeddings.embed_customer(customer_data)
```

### Using Recommended Models

```python
from src.chatbot.embeddings import create_embeddings_generator

# Get recommended model for use case
qa_embeddings = create_embeddings_generator("qa")
general_embeddings = create_embeddings_generator("general")
multilingual_embeddings = create_embeddings_generator("multilingual")
best_quality_embeddings = create_embeddings_generator("best_quality")
```

## Model Selection Guide

### For RAG Chatbot (Recommended)
```python
embeddings = create_embeddings_generator("qa")
# Uses: multi-qa-MiniLM-L6-cos-v1
```

### For Production (Best Quality)
```python
embeddings = create_embeddings_generator("best_quality")
# Uses: all-mpnet-base-v2
```

### For Speed-Critical Applications
```python
embeddings = create_embeddings_generator("fastest")
# Uses: all-MiniLM-L6-v2
```

### For Multilingual Support
```python
embeddings = create_embeddings_generator("multilingual")
# Uses: paraphrase-multilingual-MiniLM-L12-v2
```

## Integration with OpenAI

```python
from src.chatbot.embeddings import EmbeddingsGenerator
import os

# Set API key
os.environ['OPENAI_API_KEY'] = 'your-api-key'

# Initialize with OpenAI
embeddings = EmbeddingsGenerator(model_name="openai")

# Use same API
embedding = embeddings.generate_embedding("text")
```

## Performance Considerations

### Model Download
- First run downloads model from HuggingFace
- Models cached locally (~/.cache/huggingface/)
- Subsequent runs load from cache

### Speed Comparison
| Model | Texts/sec | Batch Size | Use Case |
|-------|-----------|------------|----------|
| all-MiniLM-L6-v2 | ~1000 | 32 | General |
| all-mpnet-base-v2 | ~400 | 16 | Quality |
| OpenAI | ~100 | 100 | Production |

### Memory Usage
- all-MiniLM-L6-v2: ~300MB RAM
- all-mpnet-base-v2: ~800MB RAM
- OpenAI: Minimal (API call)

## Testing

```bash
# Run embeddings test
python tests/test_embeddings.py

# Run example demonstration
python examples/09_embeddings_demo.py
```

## Troubleshooting

### Module Not Found
```bash
pip install sentence-transformers torch
```

### CUDA/GPU Issues
```bash
# For CPU-only
pip install sentence-transformers torch --index-url https://download.pytorch.org/whl/cpu
```

### Slow First Run
- Normal - downloading model
- Check progress in terminal
- Models cache for future use

### Out of Memory
- Use smaller model (all-MiniLM-L6-v2)
- Reduce batch size
- Use OpenAI API instead

## API Reference

### EmbeddingsGenerator

```python
EmbeddingsGenerator(
    model_name: str = "sentence-transformers",
    model_path: Optional[str] = None
)
```

**Methods:**
- `generate_embedding(text: str) -> List[float]`
- `generate_batch_embeddings(texts: List[str]) -> List[List[float]]`
- `embed_pipeline(pipeline_data: Dict) -> List[float]`
- `embed_customer(customer_data: Dict) -> List[float]`
- `embed_incident(incident_data: Dict) -> List[float]`
- `calculate_similarity(emb1: List[float], emb2: List[float]) -> float`

### Helper Functions

```python
# Get model recommendations
get_recommended_model(use_case: str) -> Dict

# Create configured generator
create_embeddings_generator(use_case: str) -> EmbeddingsGenerator

# Show installation help
install_instructions()
```

## Best Practices

1. **Choose Right Model**
   - RAG/QA: Use `multi-qa-MiniLM-L6-cos-v1`
   - General: Use `all-MiniLM-L6-v2`
   - Quality: Use `all-mpnet-base-v2`

2. **Batch Processing**
   - Use `generate_batch_embeddings()` for multiple texts
   - More efficient than individual calls

3. **Caching**
   - Cache embeddings for frequently used texts
   - Store in database or memory

4. **Similarity Threshold**
   - 0.7-1.0: Very similar
   - 0.5-0.7: Somewhat similar
   - 0.0-0.5: Not similar

5. **Production Deployment**
   - Pre-download models in Docker image
   - Use GPU for better performance
   - Consider OpenAI for scale
