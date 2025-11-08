# Neo4j Python Examples

Complete Python implementation examples for Neo4j concepts and RAG systems.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=your_api_key
```

### 3. Initialize Neo4j Database

Run the setup script to create indexes and constraints:

```bash
python setup_database.py
```

## Examples

### Basic Examples

1. **simple_example.py** - Getting started with Neo4j
   ```bash
   python simple_example.py
   ```

2. **connection_manager.py** - Connection management patterns
3. **crud_operations.py** - Complete CRUD examples

### Application Examples

4. **social_network_app.py** - Complete social network implementation
5. **movie_recommendations.py** - Movie recommendation system

### RAG Examples

6. **rag_basic.py** - Basic RAG implementation
7. **rag_app.py** - Complete RAG application
8. **document_processor.py** - Document ingestion
9. **custom_retrievers.py** - LangChain custom retrievers

### Advanced Examples

10. **graph_algorithms.py** - Using Neo4j GDS
11. **batch_import.py** - Efficient data import
12. **performance_testing.py** - Performance benchmarks

## File Structure

```
python-examples/
├── README.md
├── requirements.txt
├── .env.example
├── setup_database.py
│
├── basic/
│   ├── simple_example.py
│   ├── connection_manager.py
│   └── crud_operations.py
│
├── applications/
│   ├── social_network_app.py
│   └── movie_recommendations.py
│
├── rag/
│   ├── rag_basic.py
│   ├── rag_app.py
│   ├── document_processor.py
│   └── custom_retrievers.py
│
├── advanced/
│   ├── graph_algorithms.py
│   ├── batch_import.py
│   └── performance_testing.py
│
└── tests/
    ├── test_basic.py
    ├── test_rag.py
    └── conftest.py
```

## Running Examples

Each example is standalone and can be run directly:

```bash
# Basic example
python simple_example.py

# Social network app
python social_network_app.py

# RAG application
python rag_app.py
```

## Testing

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/test_basic.py -v
```

## Common Issues

### Connection Error

```
neo4j.exceptions.ServiceUnavailable: Failed to establish connection
```

**Solution**: Ensure Neo4j is running and credentials are correct.

### Import Error

```
ModuleNotFoundError: No module named 'neo4j'
```

**Solution**: Install dependencies with `pip install -r requirements.txt`

### API Key Error

```
openai.error.AuthenticationError: Incorrect API key
```

**Solution**: Check your `OPENAI_API_KEY` in `.env` file.

## Resources

- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

## License

MIT License - See main repository for details.
