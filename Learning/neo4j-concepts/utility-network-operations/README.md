# Utility Network Operations with Neo4j

A comprehensive implementation demonstrating Neo4j graph database for managing water and gas utility networks, customer services, and operations.

## 🎯 Overview

This project showcases real-world utility network management using Neo4j to model:
- **Infrastructure**: Water/gas pipelines, pumping stations, storage facilities, meters
- **Customer Management**: Accounts, consumption tracking, billing, service requests
- **Operations**: Leak detection, pressure monitoring, maintenance, emergency response
- **Analytics**: Consumption patterns, anomaly detection, predictive maintenance
- **Smart Utilities**: IoT sensor networks, real-time monitoring, automated alerts

## 📊 Data Model

### Nodes
- **PipelineSegment**: Water/gas pipeline infrastructure
- **PumpingStation**: Water pumps and gas compressor stations
- **StorageTank**: Water reservoirs and gas storage facilities
- **Meter**: Smart meters for consumption tracking
- **Valve**: Control valves for flow management
- **Sensor**: IoT devices monitoring network conditions
- **Customer**: Residential, commercial, and industrial accounts
- **ServiceRequest**: Customer service tickets and work orders
- **Incident**: Leaks, bursts, contamination events
- **MaintenanceSchedule**: Planned maintenance activities
- **Bill**: Customer billing records
- **Consumption**: Historical usage data

### Relationships
- **CONNECTS_TO** → (Pipeline)-[:CONNECTS_TO]->(Pipeline)
- **SUPPLIES** → (Station)-[:SUPPLIES]->(Pipeline)
- **MEASURES** → (Meter)-[:MEASURES]->(Customer)
- **MONITORS** → (Sensor)-[:MONITORS]->(Infrastructure)
- **CONTROLS** → (Valve)-[:CONTROLS]->(Pipeline)
- **REPORTED_BY** → (ServiceRequest)-[:REPORTED_BY]->(Customer)
- **AFFECTS** → (Incident)-[:AFFECTS]->(Customer|Infrastructure)
- **REQUIRES_MAINTENANCE** → (Infrastructure)-[:REQUIRES_MAINTENANCE]->(Schedule)
- **CONSUMES** → (Customer)-[:CONSUMES {amount, date}]->(Resource)

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
cd neo4j-concepts/utility-network-operations
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
utility-network-operations/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── docker-compose.yml                 # Neo4j local setup
│
├── cypher/                            # Cypher query scripts
│   ├── 01_schema_creation.cypher     # Indexes and constraints
│   ├── 02_data_model.cypher          # Core data model
│   ├── 03_water_network_sample.cypher # Sample water network
│   ├── 04_gas_network_sample.cypher  # Sample gas network
│   ├── 05_customer_data.cypher       # Customer and billing data
│   ├── 06_basic_queries.cypher       # Common queries
│   ├── 07_analytics_queries.cypher   # Analytics and reporting
│   └── 08_anomaly_detection.cypher   # Anomaly detection queries
│
├── src/                               # Python source code
│   ├── __init__.py
│   ├── config.py                      # Configuration management
│   ├── connection.py                  # Neo4j connection handler
│   ├── models/                        # Data models
│   │   ├── __init__.py
│   │   ├── pipeline.py
│   │   ├── meter.py
│   │   ├── customer.py
│   │   ├── service_request.py
│   │   └── incident.py
│   ├── repositories/                  # Data access layer
│   │   ├── __init__.py
│   │   ├── infrastructure_repo.py
│   │   ├── customer_repo.py
│   │   ├── billing_repo.py
│   │   └── incident_repo.py
│   ├── services/                      # Business logic
│   │   ├── __init__.py
│   │   ├── network_monitoring.py
│   │   ├── leak_detection.py
│   │   ├── consumption_analytics.py
│   │   ├── billing_service.py
│   │   └── service_request_manager.py
│   ├── algorithms/                    # Graph algorithms
│   │   ├── __init__.py
│   │   ├── flow_analysis.py
│   │   ├── leak_localization.py
│   │   ├── anomaly_detection.py
│   │   └── predictive_maintenance.py
│   └── chatbot/                       # Customer service chatbot
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
│   ├── 04_generate_consumption_data.py
│   └── 05_reset_database.py
│
├── examples/                          # Usage examples
│   ├── 01_basic_operations.py
│   ├── 02_leak_detection_demo.py
│   ├── 03_consumption_analysis.py
│   ├── 04_anomaly_detection.py
│   ├── 05_billing_operations.py
│   ├── 06_service_request_management.py
│   ├── 07_network_optimization.py
│   └── 08_customer_chatbot_demo.py
│
├── tests/                             # Unit tests
│   ├── __init__.py
│   ├── test_connection.py
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_algorithms.py
│
└── notebooks/                         # Jupyter notebooks
    ├── 01_network_exploration.ipynb
    ├── 02_consumption_patterns.ipynb
    └── 03_leak_analytics.ipynb
```

## 🔧 Key Features

### 1. Network Monitoring
```python
from src.services.network_monitoring import NetworkMonitor

monitor = NetworkMonitor()
# Get real-time network status
status = monitor.get_network_status()
# Identify pressure anomalies
anomalies = monitor.detect_pressure_anomalies()
```

### 2. Leak Detection
```python
from src.services.leak_detection import LeakDetector

detector = LeakDetector()
# Detect potential leaks based on flow patterns
leaks = detector.detect_leaks()
# Localize leak location
location = detector.localize_leak(incident_id)
```

### 3. Consumption Analytics
```python
from src.services.consumption_analytics import ConsumptionAnalyzer

analyzer = ConsumptionAnalyzer()
# Analyze consumption patterns
patterns = analyzer.analyze_patterns(customer_id)
# Detect unusual consumption
anomalies = analyzer.detect_anomalies()
```

### 4. Billing Operations
```python
from src.services.billing_service import BillingService

billing = BillingService()
# Generate monthly bills
billing.generate_monthly_bills()
# Calculate consumption charges
charges = billing.calculate_charges(customer_id, usage_kwh)
```

### 5. Service Request Management
```python
from src.services.service_request_manager import ServiceRequestManager

sr_manager = ServiceRequestManager()
# Create new service request
sr_manager.create_request(customer_id, issue_type, description)
# Assign to technician
sr_manager.assign_request(request_id, technician_id)
```

### 6. Predictive Maintenance
```python
from src.algorithms.predictive_maintenance import PredictiveMaintenance

predictor = PredictiveMaintenance()
# Predict equipment failures
at_risk = predictor.predict_failures()
# Optimize maintenance schedule
schedule = predictor.optimize_schedule()
```

### 7. Customer Service Chatbot
```python
from src.chatbot.chatbot import UtilityCustomerBot

chatbot = UtilityCustomerBot()
# Customer queries
response = chatbot.ask("What's my current water bill?")
response = chatbot.ask("Report a leak at 123 Main Street")
response = chatbot.ask("What's my average monthly consumption?")
```

## 📝 Example Queries

### Network Infrastructure
```cypher
// Find all pipelines in a region
MATCH (p:PipelineSegment {region: 'Downtown'})
RETURN p.id, p.type, p.diameter_mm, p.length_m, p.material

// Trace water flow from source to customer
MATCH path = (tank:StorageTank)-[:SUPPLIES]->()-[:CONNECTS_TO*]->()
             -[:MEASURES]->(meter:Meter)-[:MEASURES]->(customer:Customer)
WHERE customer.id = 'CUST-001'
RETURN path
```

### Leak Detection
```cypher
// Find potential leaks (high flow, low pressure)
MATCH (s:Sensor)-[:MONITORS]->(p:PipelineSegment)
WHERE s.type = 'pressure' AND s.current_value < s.threshold_min
   OR s.type = 'flow' AND s.current_value > s.threshold_max
RETURN p.id, p.location, s.type, s.current_value

// Find customers affected by incident
MATCH (i:Incident)-[:AFFECTS]->(c:Customer)
WHERE i.status = 'active'
RETURN i.id, i.type, count(c) as affected_customers
```

### Consumption Analysis
```cypher
// Find high consumers
MATCH (c:Customer)-[con:CONSUMES]->(r:Resource)
WHERE date(con.date) >= date('2024-01-01')
RETURN c.id, c.name, sum(con.amount) as total_consumption
ORDER BY total_consumption DESC
LIMIT 10

// Detect consumption anomalies
MATCH (c:Customer)-[con:CONSUMES]->(r:Resource)
WHERE date(con.date) = date('2024-11-01')
WITH c, avg(con.amount) as avg_consumption, stdev(con.amount) as std_consumption
MATCH (c)-[recent:CONSUMES]->(r)
WHERE date(recent.date) = date('2024-11-09')
  AND abs(recent.amount - avg_consumption) > 2 * std_consumption
RETURN c.id, c.name, recent.amount, avg_consumption
```

## 🎓 Concepts Covered

### Neo4j Fundamentals
- ✅ Graph modeling for network infrastructure
- ✅ Node and relationship patterns
- ✅ Property graphs with time series data
- ✅ Multi-label nodes

### Cypher Query Language
- ✅ Pattern matching for network traversal
- ✅ Variable-length paths
- ✅ Aggregations and analytics
- ✅ Temporal queries
- ✅ Statistical functions

### Advanced Concepts
- ✅ Geospatial indexes and queries
- ✅ Vector similarity for pattern matching
- ✅ Graph algorithms (flow, shortest path)
- ✅ Time series analysis
- ✅ Anomaly detection

### Python Integration
- ✅ Repository pattern
- ✅ Service layer architecture
- ✅ Transaction management
- ✅ Batch processing
- ✅ Real-time monitoring

### RAG Chatbot
- ✅ Customer service automation
- ✅ Knowledge graph retrieval
- ✅ Context-aware responses
- ✅ Multi-turn conversations

## 🚦 Usage Examples

Run the example scripts to see the system in action:

```bash
# Basic operations
python examples/01_basic_operations.py

# Leak detection demo
python examples/02_leak_detection_demo.py

# Consumption analysis
python examples/03_consumption_analysis.py

# Customer chatbot
python examples/08_customer_chatbot_demo.py
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_services.py::test_leak_detection
```

## 🐳 Docker Setup

Run Neo4j locally with Docker:

```bash
docker-compose up -d
# Neo4j Browser: http://localhost:7474
# Bolt: bolt://localhost:7687
```

## 🔍 Common Use Cases

1. **Leak Detection**: Early detection and localization of water/gas leaks
2. **Consumption Monitoring**: Track and analyze customer usage patterns
3. **Billing Automation**: Automated meter reading and bill generation
4. **Service Request Management**: Efficient handling of customer requests
5. **Network Optimization**: Optimize pressure and flow distribution
6. **Predictive Maintenance**: Prevent infrastructure failures
7. **Customer Service**: AI-powered chatbot for customer support
8. **Regulatory Compliance**: Track and report compliance metrics

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

---

Built with ❤️ using Neo4j, Python, and LangChain
