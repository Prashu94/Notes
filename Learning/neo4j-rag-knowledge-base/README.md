# Neo4j RAG Knowledge Base

A comprehensive implementation of Retrieval-Augmented Generation (RAG) using Neo4j graph database, LangChain, and Ollama for local LLM inference. Supports both standalone Python application and VSCode extension with GitHub Copilot Pro integration.

## Features

- **Multimodal Document Support**: Load and process PDF and TXT files
- **Neo4j Vector Search**: Efficient similarity search using graph database
- **Ollama Integration**: Local LLM inference without API costs
- **Dual Implementation**:
  - **Python Mode**: Pure LangChain-based implementation
  - **VSCode Extension**: GitHub Copilot Pro integration with Ollama embeddings
- **Interactive Chat**: Query your knowledge base conversationally
- **Hybrid Search**: Combine vector and full-text search
- **Rich Metadata**: Track document sources and relationships

## Architecture

```
┌─────────────────┐
│   Documents     │
│  (.pdf, .txt)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document Loader │
│  & Chunking     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Ollama      │
│   Embeddings    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Neo4j Graph   │
│  + Vector Index │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RAG System    │
│  LangChain/     │
│  Copilot Pro    │
└─────────────────┘
```

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Ollama (https://ollama.ai)
- Node.js 18+ (for VSCode extension)
- VSCode with GitHub Copilot Pro (for extension mode)

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd neo4j-rag-knowledge-base

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment

Edit `langchain-python/.env`:

```env
NEO4J_PASSWORD=your_secure_password
```

### 3. Start Services

```bash
# Neo4j is already started by setup.sh
# Check status
docker ps

# Start Ollama (if not running)
ollama serve
```

## Python Mode (LangChain)

### Activate Environment

```bash
cd langchain-python
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Load Documents

```bash
python main.py --mode load --documents ../sample-data
```

### Query Knowledge Base

```bash
python main.py --mode query --question "What is RAG?"
```

### Interactive Chat

```bash
python main.py --mode chat
```

### Advanced Options

```bash
# Clear knowledge base before loading
python main.py --mode load --documents ../sample-data --clear

# Enable conversational mode with history
python main.py --mode chat --conversational

# Verbose output
python main.py --mode query --question "Explain Neo4j" --verbose
```

## VSCode Extension Mode

### Build Extension

```bash
cd vscode-extension
npm install
npm run compile
```

### Run Extension

1. Open `vscode-extension` folder in VSCode
2. Press `F5` to launch Extension Development Host
3. In the new window, use commands:
   - `Ctrl+Shift+P` → "Neo4j RAG: Initialize Knowledge Base"
   - `Ctrl+Shift+P` → "Neo4j RAG: Load Documents"
   - `Ctrl+Shift+P` → "Neo4j RAG: Open Chat Interface"

### Configure Extension

In VSCode settings (`settings.json`):

```json
{
  "neo4jRagKb.neo4j.uri": "bolt://localhost:7687",
  "neo4jRagKb.neo4j.username": "neo4j",
  "neo4jRagKb.neo4j.password": "your_password",
  "neo4jRagKb.ollama.baseUrl": "http://localhost:11434",
  "neo4jRagKb.ollama.embeddingModel": "nomic-embed-text"
}
```

## Project Structure

```
neo4j-rag-knowledge-base/
├── langchain-python/          # Python implementation
│   ├── config.py              # Configuration management
│   ├── document_loader.py     # Document loading & chunking
│   ├── neo4j_kb.py            # Neo4j knowledge base
│   ├── ollama_provider.py     # Ollama LLM & embeddings
│   ├── rag_system.py          # RAG implementation
│   ├── main.py                # Main application
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
├── vscode-extension/          # VSCode extension
│   ├── src/
│   │   ├── extension.ts       # Extension entry point
│   │   ├── config.ts          # Configuration
│   │   ├── ollamaProvider.ts  # Ollama integration
│   │   ├── neo4jKb.ts         # Neo4j knowledge base
│   │   ├── documentLoader.ts  # Document loader
│   │   └── ragSystem.ts       # RAG with Copilot
│   ├── package.json           # Extension manifest
│   └── tsconfig.json          # TypeScript config
│
├── sample-data/               # Sample documents
│   ├── rag-introduction.txt
│   └── neo4j-guide.txt
│
├── docker-compose.yml         # Neo4j container
├── setup.sh                   # Setup script
└── README.md
```

## Configuration

### Neo4j Settings

- **URI**: `bolt://localhost:7687`
- **Browser**: `http://localhost:7474`
- **Username**: `neo4j`
- **Password**: Set in `.env` file

### Ollama Models

```bash
# Pull LLM model
ollama pull llama3.2

# Pull embedding model
ollama pull nomic-embed-text

# List available models
ollama list
```

### Document Processing

- **Chunk Size**: 1000 tokens (configurable)
- **Chunk Overlap**: 200 tokens (configurable)
- **Supported Formats**: PDF, TXT

### RAG Parameters

- **Retrieval K**: 5 documents (configurable)
- **Similarity Function**: Cosine similarity
- **Search Mode**: Vector or Hybrid

## API Reference

### Python API

```python
from config import AppConfig
from document_loader import MultimodalDocumentLoader
from ollama_provider import OllamaLLMProvider, OllamaEmbeddingProvider
from neo4j_kb import Neo4jKnowledgeBase
from rag_system import Neo4jRAGSystem

# Initialize
config = AppConfig.from_env()
embeddings = OllamaEmbeddingProvider(model="nomic-embed-text")
kb = Neo4jKnowledgeBase(
    uri=config.neo4j.uri,
    username=config.neo4j.username,
    password=config.neo4j.password,
    embedding_function=embeddings.get_embeddings()
)

# Load documents
loader = MultimodalDocumentLoader()
docs = loader.load_and_split("./data")
kb.add_documents(docs)

# Query
llm = OllamaLLMProvider(model="llama3.2")
rag = Neo4jRAGSystem(kb, llm.get_llm())
result = rag.query("What is RAG?")
print(result["answer"])
```

### VSCode Extension API

The extension provides these commands:
- `neo4j-rag-kb.initializeKB`
- `neo4j-rag-kb.loadDocuments`
- `neo4j-rag-kb.queryKB`
- `neo4j-rag-kb.openChat`
- `neo4j-rag-kb.clearKB`

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# View Neo4j logs
docker logs neo4j-rag-kb

# Restart Neo4j
docker-compose restart
```

### Ollama Issues

```bash
# Check Ollama status
ollama list

# Test Ollama
curl http://localhost:11434/api/tags

# Pull models again
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Python Environment

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Performance Tips

1. **Chunk Size**: Adjust based on document type (shorter for technical docs)
2. **Retrieval K**: More documents = better context but slower
3. **Hybrid Search**: Enable for better recall on keyword queries
4. **Batch Loading**: Load documents in batches for large datasets
5. **Index Optimization**: Ensure vector indexes are created

## Advanced Usage

### Custom Embedding Models

```python
# Use different Ollama model
embeddings = OllamaEmbeddingProvider(model="all-minilm")
```

### Filtered Search

```python
# Search with metadata filters
results = kb.similarity_search(
    query="What is RAG?",
    k=5,
    filter={"file_type": "pdf"}
)
```

### Conversational RAG

```python
# Enable conversation history
rag = ConversationalRAG(kb, llm, max_history=5)
result = rag.query("Tell me about Neo4j")
result = rag.query("What are its benefits?")  # Maintains context
```

## Security Considerations

- Change default Neo4j password in production
- Use environment variables for sensitive data
- Restrict Neo4j network access
- Validate user input before querying
- Implement rate limiting for production use

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- LangChain for RAG framework
- Neo4j for graph database
- Ollama for local LLM inference
- GitHub Copilot for AI assistance

## Support

For issues and questions:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review sample data in `/sample-data`

---

**Note**: This is a development/learning project. For production use, implement proper error handling, logging, monitoring, and security measures.
