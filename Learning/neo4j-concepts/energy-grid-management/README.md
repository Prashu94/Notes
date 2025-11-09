# Energy Grid Management System with Neo4j

A comprehensive implementation demonstrating Neo4j graph database for managing electrical power grid infrastructure, monitoring, and operations.

## 🎯 Overview

This project showcases real-world energy grid management using Neo4j to model:
- **Infrastructure**: Power plants, substations, transmission lines, transformers
- **Operations**: Real-time monitoring, outage management, maintenance scheduling
- **Analytics**: Load forecasting, grid optimization, fault analysis
- **Smart Grid**: IoT sensor integration, predictive maintenance
- **Compliance**: Regulatory tracking, safety audits, incident reporting

## 📊 Data Model

### Nodes
- **PowerPlant**: Generation facilities (coal, nuclear, solar, wind, hydro)
- **Substation**: Voltage transformation and distribution points
- **TransmissionLine**: High-voltage power transmission infrastructure
- **Transformer**: Voltage conversion equipment
- **Sensor**: IoT devices monitoring grid conditions
- **Customer**: End consumers (residential, commercial, industrial)
- **Incident**: Outages, faults, maintenance events
- **Regulation**: Compliance requirements and safety standards
- **MaintenanceSchedule**: Planned maintenance activities
- **LoadForecast**: Demand predictions

### Relationships
- **GENERATES** → (PowerPlant)-[:GENERATES]->(Substation)
- **TRANSMITS_TO** → (Substation)-[:TRANSMITS_TO]->(Substation)
- **SUPPLIES_POWER** → (Substation)-[:SUPPLIES_POWER]->(Customer)
- **MONITORS** → (Sensor)-[:MONITORS]->(Equipment)
- **LOCATED_AT** → (Equipment)-[:LOCATED_AT]->(Location)
- **CAUSED_BY** → (Incident)-[:CAUSED_BY]->(Equipment)
- **AFFECTS** → (Incident)-[:AFFECTS]->(Customer)
- **REQUIRES_MAINTENANCE** → (Equipment)-[:REQUIRES_MAINTENANCE]->(MaintenanceSchedule)
- **COMPLIES_WITH** → (Equipment)-[:COMPLIES_WITH]->(Regulation)

## 🚀 Quick Start

### Prerequisites
```bash
# Install Neo4j Desktop or use Neo4j AuraDB
# Python 3.8+
# pip package manager
```

### Installation

1. **Clone and navigate to project:**
```bash
cd neo4j-concepts/energy-grid-management
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Neo4j credentials
```

5. **Set up database:**
```bash
# Create schema (indexes and constraints)
python scripts/01_create_schema.py

# Load sample data
python scripts/02_load_sample_data.py

# Verify installation
python scripts/03_verify_setup.py
```

## 📁 Project Structure

```
energy-grid-management/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── docker-compose.yml                 # Neo4j local setup
│
├── cypher/                            # Cypher query scripts
│   ├── 01_schema_creation.cypher     # Indexes and constraints
│   ├── 02_data_model.cypher          # Core data model
│   ├── 03_sample_data.cypher         # Sample grid data
│   ├── 04_basic_queries.cypher       # Common queries
│   ├── 05_advanced_queries.cypher    # Complex pattern matching
│   ├── 06_graph_algorithms.cypher    # Pathfinding, centrality
│   └── 07_analytics_queries.cypher   # Operational analytics
│
├── src/                               # Python source code
│   ├── __init__.py
│   ├── config.py                      # Configuration management
│   ├── connection.py                  # Neo4j connection handler
│   ├── models/                        # Data models
│   │   ├── __init__.py
│   │   ├── power_plant.py
│   │   ├── substation.py
│   │   ├── transmission_line.py
│   │   ├── incident.py
│   │   └── sensor.py
│   ├── repositories/                  # Data access layer
│   │   ├── __init__.py
│   │   ├── infrastructure_repo.py
│   │   ├── incident_repo.py
│   │   ├── sensor_repo.py
│   │   └── analytics_repo.py
│   ├── services/                      # Business logic
│   │   ├── __init__.py
│   │   ├── grid_monitoring.py
│   │   ├── outage_management.py
│   │   ├── maintenance_scheduler.py
│   │   ├── load_forecasting.py
│   │   └── fault_analysis.py
│   ├── algorithms/                    # Graph algorithms
│   │   ├── __init__.py
│   │   ├── shortest_path.py
│   │   ├── centrality.py
│   │   ├── community_detection.py
│   │   └── network_flow.py
│   └── rag/                           # RAG chatbot
│       ├── __init__.py
│       ├── embeddings.py
│       ├── retriever.py
│       ├── chatbot.py
│       └── prompts.py
│
├── scripts/                           # Setup and utility scripts
│   ├── 01_create_schema.py
│   ├── 02_load_sample_data.py
│   ├── 03_verify_setup.py
│   ├── 04_generate_synthetic_data.py
│   └── 05_reset_database.py
│
├── examples/                          # Usage examples
│   ├── 01_basic_operations.py
│   ├── 02_outage_analysis.py
│   ├── 03_load_forecasting.py
│   ├── 04_fault_detection.py
│   ├── 05_maintenance_scheduling.py
│   ├── 06_graph_algorithms_demo.py
│   ├── 07_real_time_monitoring.py
│   └── 08_rag_chatbot_demo.py
│
├── tests/                             # Unit tests
│   ├── __init__.py
│   ├── test_connection.py
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_algorithms.py
│
└── notebooks/                         # Jupyter notebooks
    ├── 01_data_exploration.ipynb
    ├── 02_outage_analytics.ipynb
    └── 03_predictive_maintenance.ipynb
```

## 🔧 Key Features

### 1. Infrastructure Management
```python
from src.services.grid_monitoring import GridMonitor

monitor = GridMonitor()
# Get real-time grid status
status = monitor.get_grid_status()
# Identify critical infrastructure
critical = monitor.get_critical_nodes()
```

### 2. Outage Management
```python
from src.services.outage_management import OutageManager

outage_mgr = OutageManager()
# Report and analyze outages
outage_mgr.report_outage(substation_id, cause, affected_customers)
# Find alternative power routes
routes = outage_mgr.find_backup_routes(failed_line_id)
```

### 3. Predictive Maintenance
```python
from src.services.maintenance_scheduler import MaintenanceScheduler

scheduler = MaintenanceScheduler()
# Predict equipment failures
at_risk = scheduler.predict_failures()
# Optimize maintenance schedule
schedule = scheduler.optimize_schedule()
```

### 4. Load Forecasting
```python
from src.services.load_forecasting import LoadForecaster

forecaster = LoadForecaster()
# Forecast demand
forecast = forecaster.forecast_load(region_id, days=7)
# Identify peak demand periods
peaks = forecaster.identify_peaks()
```

### 5. Graph Algorithms
```python
from src.algorithms.shortest_path import find_optimal_route
from src.algorithms.centrality import identify_critical_nodes

# Find most efficient power transmission path
path = find_optimal_route(source_plant, destination_substation)

# Identify critical infrastructure
critical = identify_critical_nodes(algorithm='betweenness')
```

### 6. RAG-Powered Chatbot
```python
from src.rag.chatbot import EnergyGridChatbot

chatbot = EnergyGridChatbot()
# Ask natural language questions
response = chatbot.ask("What caused the outage in downtown region last week?")
response = chatbot.ask("Which substations need maintenance this month?")
response = chatbot.ask("Show me the power flow from Plant-001 to all customers")
```

## 📝 Example Queries

### Basic Infrastructure Queries
```cypher
// Find all power plants and their capacity
MATCH (p:PowerPlant)
RETURN p.name, p.type, p.capacity_mw
ORDER BY p.capacity_mw DESC

// Map power flow from generation to consumption
MATCH path = (plant:PowerPlant)-[:GENERATES]->()-[:TRANSMITS_TO*]->()-[:SUPPLIES_POWER]->(customer:Customer)
RETURN path
LIMIT 100
```

### Outage Analysis
```cypher
// Find all active outages and affected customers
MATCH (i:Incident {status: 'active'})-[:AFFECTS]->(c:Customer)
RETURN i.id, i.cause, count(c) as affected_customers
ORDER BY affected_customers DESC

// Identify equipment with most failures
MATCH (e:Equipment)<-[:CAUSED_BY]-(i:Incident)
RETURN e.id, e.type, count(i) as failure_count
ORDER BY failure_count DESC
```

### Network Analysis
```cypher
// Find critical substations (high betweenness centrality)
CALL gds.betweenness.stream('gridGraph')
YIELD nodeId, score
MATCH (s:Substation) WHERE id(s) = nodeId
RETURN s.name, score
ORDER BY score DESC
LIMIT 10

// Detect grid communities
CALL gds.louvain.stream('gridGraph')
YIELD nodeId, communityId
MATCH (n) WHERE id(n) = nodeId
RETURN communityId, collect(n.name) as members
```

## 🎓 Concepts Covered

### Neo4j Fundamentals
- ✅ Graph modeling for infrastructure networks
- ✅ Node and relationship creation
- ✅ Property graphs with metadata
- ✅ Labels and types

### Cypher Query Language
- ✅ CREATE, MATCH, WHERE, RETURN
- ✅ Pattern matching and traversals
- ✅ Aggregations and filtering
- ✅ Variable-length paths
- ✅ OPTIONAL MATCH
- ✅ MERGE (upsert operations)

### Advanced Concepts
- ✅ Indexes (B-tree, text, vector)
- ✅ Constraints (unique, existence)
- ✅ Transactions
- ✅ Graph Data Science algorithms
- ✅ Vector similarity search
- ✅ Full-text search

### Python Integration
- ✅ Neo4j Python driver
- ✅ Connection pooling
- ✅ Transaction management
- ✅ Parameterized queries
- ✅ Batch operations
- ✅ Error handling

### RAG Implementation
- ✅ Document embeddings
- ✅ Vector similarity search
- ✅ Graph-enhanced retrieval
- ✅ LangChain integration
- ✅ Conversational AI

## 🚦 Usage Examples

Run the example scripts to see the system in action:

```bash
# Basic operations
python examples/01_basic_operations.py

# Analyze recent outages
python examples/02_outage_analysis.py

# Load forecasting demo
python examples/03_load_forecasting.py

# Real-time monitoring
python examples/07_real_time_monitoring.py

# Interactive chatbot
python examples/08_rag_chatbot_demo.py
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_services.py::test_outage_management
```

## 📚 Documentation

Each module includes detailed docstrings. Generate documentation:

```bash
pip install pdoc3
pdoc --html --output-dir docs src
```

## 🐳 Docker Setup

Run Neo4j locally with Docker:

```bash
docker-compose up -d
# Neo4j Browser: http://localhost:7474
# Bolt: bolt://localhost:7687
```

## 🔍 Common Use Cases

1. **Outage Response**: Quickly identify affected areas and reroute power
2. **Maintenance Planning**: Optimize schedules to minimize downtime
3. **Load Balancing**: Distribute power efficiently across the grid
4. **Fault Detection**: Early warning system for equipment failures
5. **Compliance Reporting**: Track regulatory adherence
6. **Investment Planning**: Identify infrastructure upgrade priorities
7. **Emergency Response**: Coordinate response to natural disasters

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## 📞 Support

For questions or issues, please open a GitHub issue or contact the maintainers.

---

Built with ❤️ using Neo4j, Python, and LangChain
