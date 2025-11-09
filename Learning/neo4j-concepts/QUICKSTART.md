# Quick Start Guide - Neo4j Code Examples

Get up and running with the energy grid and utility network projects in minutes!

## 🎯 What You'll Build

### Energy Grid Management System
A production-ready system for managing electrical power infrastructure with:
- Real-time grid monitoring
- Outage detection and analysis
- Load forecasting
- Predictive maintenance
- AI-powered operations chatbot

### Utility Network Operations
A complete solution for water/gas utility management with:
- Network infrastructure mapping
- Leak detection and localization
- Consumption analytics
- Automated billing
- Customer service automation

## ⚡ 5-Minute Setup

### Step 1: Choose Your Project

```bash
cd neo4j-concepts

# For Energy Grid Management
cd energy-grid-management

# OR for Utility Network Operations
cd utility-network-operations
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate          # macOS/Linux
# OR
venv\Scripts\activate              # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Neo4j Connection

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Neo4j credentials
# For local Neo4j:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OR use Docker (see below)
```

### Step 4: Initialize Database

```bash
# Create schema (indexes and constraints)
python scripts/01_create_schema.py

# Load sample data
python scripts/02_load_sample_data.py

# Verify setup
python scripts/03_verify_setup.py
```

### Step 5: Run Examples

```bash
# Basic operations
python examples/01_basic_operations.py

# Domain-specific examples
# For Energy Grid:
python examples/02_outage_analysis.py
python examples/03_load_forecasting.py

# For Utility Network:
python examples/02_leak_detection_demo.py
python examples/03_consumption_analysis.py
```

## 🐳 Quick Start with Docker

Don't have Neo4j installed? Use Docker!

### Energy Grid Management

```bash
cd energy-grid-management

# Start Neo4j
docker-compose up -d

# Wait 30 seconds for Neo4j to start
sleep 30

# Neo4j Browser: http://localhost:7474
# Username: neo4j
# Password: password123

# Continue with Step 2 above
```

### Utility Network Operations

```bash
cd utility-network-operations

# Start Neo4j (on different ports to avoid conflicts)
docker-compose up -d

# Wait 30 seconds
sleep 30

# Neo4j Browser: http://localhost:7475
# Bolt: bolt://localhost:7688
# Username: neo4j
# Password: password123

# Continue with Step 2 above
```

## 🎓 First Steps Tutorial

### Energy Grid - Find Power Flow

```python
from src.connection import get_connection, close_connection

# Connect to Neo4j
conn = get_connection()

# Query: Trace power from plant to customer
query = """
MATCH path = (plant:PowerPlant)-[:GENERATES]->()
             -[:TRANSMITS_TO*]->()-[:SUPPLIES_POWER]->(customer:Customer)
WHERE plant.id = 'PP-001'
RETURN plant.name, customer.name, length(path) as hops
LIMIT 5
"""

results = conn.execute_read(query)
for r in results:
    print(f"{r['plant.name']} → {r['customer.name']} ({r['hops']} hops)")

close_connection()
```

### Utility Network - Detect Potential Leaks

```python
from src.connection import get_connection, close_connection

conn = get_connection()

# Query: Find pressure anomalies indicating leaks
query = """
MATCH (s:Sensor)-[:MONITORS]->(p:PipelineSegment)
WHERE s.type = 'pressure' 
  AND s.current_value < s.threshold_min
RETURN p.id, p.region, s.current_value, s.threshold_min
"""

results = conn.execute_read(query)
for r in results:
    print(f"⚠️  Leak suspected in {r['p.id']} - "
          f"Pressure: {r['s.current_value']} (min: {r['s.threshold_min']})")

close_connection()
```

## 📊 Sample Data Overview

### Energy Grid Sample Data
- **6 Power Plants**: Nuclear (1200MW), Solar (500MW), Wind (350MW), Coal (800MW), Hydro (600MW), Gas (950MW)
- **8 Substations**: 4 transmission (500kV), 4 distribution (230kV)
- **8 Transmission Lines**: Connecting substations in a ring topology
- **10 Customers**: Mix of industrial, commercial, and residential
- **Total Capacity**: 4,400 MW generation capacity

### Utility Network Sample Data
- **3 Storage Tanks**: 50,000-75,000 m³ capacity
- **3 Pumping Stations**: 400-500 m³/hour capacity
- **8 Pipeline Segments**: 1,500-3,000m lengths
- **5 Customers**: Residential, commercial, industrial
- **5 Smart Meters**: Real-time consumption tracking
- **3 IoT Sensors**: Pressure and flow monitoring

## 🔍 Explore the Data

### Using Neo4j Browser

1. Open Neo4j Browser: http://localhost:7474
2. Try these queries:

```cypher
// See all node types and counts
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC

// Visualize the network
MATCH p=()-[r]->() 
RETURN p 
LIMIT 100

// Find most connected nodes
MATCH (n)
RETURN n, size((n)--()) as connections
ORDER BY connections DESC
LIMIT 10
```

### Using Python Examples

```bash
# Interactive exploration
cd examples/
python 01_basic_operations.py

# See all available examples
ls -la examples/
```

## 📚 Next Steps

### Learn More
1. **Read the docs**: Check project README.md files
2. **Study Cypher**: Explore cypher/ directory
3. **Understand architecture**: Review src/ structure
4. **Run tests**: `pytest tests/`

### Build Your Own
1. **Modify data model**: Edit cypher/02_data_model.cypher
2. **Add queries**: Create new Cypher scripts
3. **Extend Python code**: Add services and algorithms
4. **Generate more data**: Use scripts/04_generate_synthetic_data.py

### Advanced Topics
1. **Graph Algorithms**: Implement pathfinding, centrality
2. **Vector Search**: Add document embeddings
3. **RAG Chatbot**: Build conversational AI
4. **Real-time Monitoring**: Stream sensor data
5. **Scale Up**: Generate large datasets

## 🆘 Troubleshooting

### Connection Issues

```bash
# Check Neo4j is running
docker ps

# View Neo4j logs
docker logs energy-grid-neo4j
# OR
docker logs utility-network-neo4j

# Restart Neo4j
docker-compose restart
```

### Import Errors

```bash
# Ensure virtual environment is activated
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Query Errors

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check connection
from src.connection import get_connection
conn = get_connection()
print("Connected:", conn.verify_connection())
```

### Database Empty

```bash
# Reload data
python scripts/02_load_sample_data.py

# Or reset and reload
python scripts/05_reset_database.py
python scripts/02_load_sample_data.py
```

## 💡 Pro Tips

1. **Start Simple**: Run basic examples first before advanced features
2. **Use Browser**: Visualize data in Neo4j Browser before writing code
3. **Read Comments**: All Cypher and Python files have detailed comments
4. **Check Examples**: 8+ example scripts demonstrate different features
5. **Test Incrementally**: Run small queries to understand data structure

## 🎯 Learning Checklist

- [ ] Set up development environment
- [ ] Connect to Neo4j database
- [ ] Load and verify sample data
- [ ] Run basic query examples
- [ ] Understand data model
- [ ] Explore Cypher queries
- [ ] Study Python architecture
- [ ] Run domain-specific examples
- [ ] Implement custom queries
- [ ] Build your own features

## 📖 Documentation

- **Project READMEs**: Comprehensive documentation in each project
- **CODE-EXAMPLES-README.md**: Overview of both projects
- **Inline Comments**: All code is well-documented
- **Example Scripts**: Practical demonstrations

## 🤝 Need Help?

1. Check project README.md files
2. Review example scripts
3. Read inline code comments
4. Explore Jupyter notebooks
5. Check Neo4j documentation: https://neo4j.com/docs/

## 🎉 You're Ready!

You now have:
- ✅ Two production-ready Neo4j projects
- ✅ Complete data models and schemas
- ✅ Sample data loaded and verified
- ✅ Working examples to learn from
- ✅ Tools to build your own features

Start exploring and building! 🚀
