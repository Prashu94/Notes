# Neo4j Concepts - Code Examples for Energy and Utility Use Cases

This document provides an overview of the two comprehensive Neo4j code example projects covering energy grid management and utility network operations.

## 📁 Projects Overview

### 1. Energy Grid Management (`energy-grid-management/`)
A complete implementation for managing electrical power grids with Neo4j.

**Key Features:**
- ⚡ Power plant and substation management
- 🔌 Transmission line monitoring
- 📊 Load forecasting and grid optimization
- 🚨 Outage management and fault analysis
- 🔧 Predictive maintenance
- 🤖 RAG-powered grid operations chatbot

**Concepts Covered:**
- Graph modeling for infrastructure networks
- Real-time monitoring with IoT sensors
- Graph algorithms (pathfinding, centrality, network flow)
- Vector search for equipment similarity
- Time-series data in graphs
- Incident tracking and root cause analysis

### 2. Utility Network Operations (`utility-network-operations/`)
A complete implementation for water/gas utility network management.

**Key Features:**
- 💧 Water/gas pipeline network management
- 📊 Consumption tracking and analytics
- 🔍 Leak detection and localization
- 💰 Automated billing operations
- 📞 Service request management
- 🤖 Customer service chatbot

**Concepts Covered:**
- Graph modeling for distribution networks
- Flow analysis and pressure monitoring
- Anomaly detection algorithms
- Customer relationship management
- Billing and consumption analytics
- Geospatial queries for leak localization

## 🗂️ Project Structure

Both projects follow a consistent structure:

```
project-name/
├── README.md              # Comprehensive project documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── docker-compose.yml    # Neo4j setup with Docker
│
├── cypher/               # Cypher query scripts
│   ├── 01_schema_creation.cypher      # Indexes & constraints
│   ├── 02_data_model.cypher           # Data model definition
│   ├── 03_sample_data.cypher          # Sample data
│   ├── 04_basic_queries.cypher        # Common queries
│   ├── 05_advanced_queries.cypher     # Complex patterns
│   ├── 06_graph_algorithms.cypher     # GDS algorithms
│   └── 07_analytics_queries.cypher    # Reporting queries
│
├── src/                  # Python source code
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── connection.py     # Neo4j connection handling
│   ├── models/           # Data models (Pydantic)
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic
│   ├── algorithms/       # Graph algorithms
│   └── rag/             # RAG chatbot implementation
│
├── scripts/             # Setup and utility scripts
│   ├── 01_create_schema.py
│   ├── 02_load_sample_data.py
│   ├── 03_verify_setup.py
│   └── 04_generate_synthetic_data.py
│
├── examples/            # Usage examples and demos
│   ├── 01_basic_operations.py
│   ├── 02_[domain]_analysis.py
│   ├── ...
│   └── 08_chatbot_demo.py
│
├── tests/               # Unit tests
│   └── test_*.py
│
└── notebooks/           # Jupyter notebooks
    ├── 01_data_exploration.ipynb
    └── ...
```

## 🚀 Quick Start

### For Energy Grid Management:

```bash
cd energy-grid-management

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Neo4j credentials

# Initialize database
python scripts/01_create_schema.py
python scripts/02_load_sample_data.py

# Run examples
python examples/01_basic_operations.py
python examples/02_outage_analysis.py
python examples/08_rag_chatbot_demo.py
```

### For Utility Network Operations:

```bash
cd utility-network-operations

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Neo4j credentials

# Initialize database
python scripts/01_create_schema.py
python scripts/02_load_sample_data.py

# Run examples
python examples/01_basic_operations.py
python examples/02_leak_detection_demo.py
python examples/08_customer_chatbot_demo.py
```

## 📚 Neo4j Concepts Demonstrated

### Fundamentals
✅ **Graph Data Modeling**
- Nodes, relationships, and properties
- Labels and relationship types
- Property graphs vs. other models

✅ **Schema Design**
- Indexes (B-tree, text, point, vector, full-text)
- Constraints (unique, existence)
- Schema-optional flexibility

### Cypher Query Language
✅ **Basic Operations**
- CREATE, MATCH, WHERE, RETURN
- Relationship patterns
- Property filtering

✅ **Advanced Patterns**
- Variable-length paths
- OPTIONAL MATCH
- Pattern comprehensions
- Aggregations and grouping

✅ **Complex Queries**
- Subqueries
- UNION operations
- CASE expressions
- Date/time operations

### Advanced Concepts
✅ **Graph Algorithms**
- Shortest path
- Betweenness centrality
- PageRank
- Community detection
- Network flow

✅ **Vector Similarity Search**
- Document embeddings
- Semantic search
- K-nearest neighbors

✅ **Full-Text Search**
- Index creation
- Relevance scoring
- Multi-field search

✅ **Geospatial Queries**
- Point data types
- Distance calculations
- Spatial indexes

✅ **Performance Optimization**
- Query profiling
- Index usage
- Connection pooling
- Batch operations

### Python Integration
✅ **Neo4j Driver**
- Connection management
- Session handling
- Transaction control
- Parameterized queries

✅ **Architecture Patterns**
- Repository pattern
- Service layer
- Dependency injection
- Error handling

✅ **Data Processing**
- Batch operations
- Streaming results
- Data transformations

### RAG Implementation
✅ **Components**
- Document chunking
- Embedding generation
- Vector storage
- Retrieval strategies

✅ **LangChain Integration**
- Graph-enhanced retrieval
- Conversational chains
- Context management
- Prompt engineering

## 🎯 Use Cases Covered

### Energy Grid Management
1. **Infrastructure Management**: Model power plants, substations, transmission lines
2. **Outage Analysis**: Track incidents, identify root causes, find affected customers
3. **Load Forecasting**: Analyze consumption patterns, predict demand
4. **Fault Detection**: Early warning systems using sensor data
5. **Maintenance Planning**: Optimize schedules, prevent failures
6. **Grid Optimization**: Find optimal power routes, balance loads
7. **Compliance Tracking**: Monitor regulatory adherence

### Utility Network Operations
1. **Network Modeling**: Map water/gas pipelines, stations, storage
2. **Leak Detection**: Identify and localize leaks using flow/pressure data
3. **Consumption Analytics**: Track usage patterns, detect anomalies
4. **Billing Automation**: Generate bills based on meter readings
5. **Service Requests**: Manage customer tickets efficiently
6. **Predictive Maintenance**: Prevent infrastructure failures
7. **Customer Service**: AI-powered chatbot for support

## 🔧 Technology Stack

### Core Technologies
- **Neo4j 5.14+**: Graph database
- **Python 3.8+**: Programming language
- **neo4j-driver**: Official Python driver

### AI/ML Stack
- **LangChain**: RAG framework
- **OpenAI**: LLMs and embeddings
- **sentence-transformers**: Local embeddings
- **scikit-learn**: ML algorithms

### Development Tools
- **Pydantic**: Data validation
- **pytest**: Testing framework
- **Docker**: Containerization
- **Jupyter**: Interactive notebooks

## 📊 Sample Data

Both projects include:
- **Realistic sample data** with proper relationships
- **Synthetic data generators** for larger datasets
- **Time-series data** for analytics
- **Geographic data** for spatial queries

### Energy Grid Sample Data:
- 6 power plants (nuclear, solar, wind, coal, hydro, gas)
- 8 substations (transmission and distribution)
- 8 transmission lines
- 10 customers (industrial, commercial, residential)
- Full network connectivity

### Utility Network Sample Data:
- 3 storage tanks/reservoirs
- 3 pumping/compressor stations
- 8 pipeline segments
- 5 customers (residential, commercial, industrial)
- Smart meters and IoT sensors
- Service requests and billing records

## 🧪 Testing

Both projects include:
- Unit tests for all modules
- Integration tests for database operations
- Example scripts demonstrating functionality
- Jupyter notebooks for exploration

Run tests:
```bash
pytest tests/
pytest --cov=src tests/  # With coverage
```

## 📖 Documentation

Each project includes:
1. **README.md**: Complete project documentation
2. **Inline code documentation**: Docstrings for all functions
3. **Cypher comments**: Explanation of queries
4. **Example scripts**: Practical usage demonstrations
5. **Jupyter notebooks**: Interactive exploration

## 🔄 Comparison

| Aspect | Energy Grid | Utility Network |
|--------|-------------|-----------------|
| **Domain** | Electrical power | Water/Gas |
| **Focus** | Generation & transmission | Distribution & billing |
| **Key Entities** | Plants, substations, lines | Pipelines, meters, customers |
| **Main Analytics** | Load forecasting, outages | Leak detection, consumption |
| **Algorithms** | Centrality, network flow | Flow analysis, anomaly detection |
| **Chatbot Use** | Operations support | Customer service |

## 🎓 Learning Path

### For Beginners:
1. Start with **energy-grid-management** (simpler model)
2. Study `cypher/` scripts to understand queries
3. Run `examples/01_basic_operations.py`
4. Explore Jupyter notebooks

### For Advanced Users:
1. Study both projects' architecture
2. Implement graph algorithms in `algorithms/`
3. Build custom RAG implementations
4. Scale with synthetic data generators

## 💡 Key Takeaways

1. **Graph modeling naturally represents infrastructure networks**
2. **Cypher queries are more intuitive than SQL JOINs for relationships**
3. **Vector search enables semantic similarity in operational data**
4. **Graph algorithms provide powerful analytics**
5. **RAG chatbots can leverage graph relationships for better context**
6. **Python integration allows flexible application development**
7. **Proper indexing is crucial for performance at scale**

## 🤝 Contributing

These projects demonstrate best practices for:
- Graph data modeling
- Neo4j integration with Python
- Production-ready architecture
- Comprehensive documentation
- Testing and validation

Feel free to extend these examples for your specific use cases!

## 📄 License

MIT License - See individual project LICENSE files

---

**Built with ❤️ to demonstrate Neo4j capabilities in energy and utility sectors**
