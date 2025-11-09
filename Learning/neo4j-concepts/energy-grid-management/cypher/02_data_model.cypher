// ===================================
// DATA MODEL FOR ENERGY GRID
// ===================================
// This script defines the core graph data model structure

// ===================================
// NODE TYPES AND THEIR PROPERTIES
// ===================================

/*
PowerPlant:
  - id: Unique identifier (string)
  - name: Plant name (string)
  - type: Generation type (string: 'coal', 'nuclear', 'solar', 'wind', 'hydro', 'natural_gas')
  - capacity_mw: Generation capacity in megawatts (float)
  - efficiency_percent: Operational efficiency (float)
  - status: Current status (string: 'operational', 'maintenance', 'offline')
  - commissioned_date: Date of commissioning (date)
  - operator: Operating company (string)
  - location: Geographic coordinates (point)
  - emissions_tons_per_year: CO2 emissions (float)
  - description: Additional details (string)

Substation:
  - id: Unique identifier (string)
  - name: Substation name (string)
  - voltage_kv: Operating voltage in kilovolts (float)
  - capacity_mva: Transformer capacity in MVA (float)
  - type: Substation type (string: 'transmission', 'distribution', 'switching')
  - status: Current status (string: 'operational', 'maintenance', 'offline')
  - region: Geographic region (string)
  - location: Geographic coordinates (point)
  - commissioned_date: Date of commissioning (date)
  - num_transformers: Number of transformers (int)

TransmissionLine:
  - id: Unique identifier (string)
  - name: Line designation (string)
  - voltage_kv: Operating voltage (float)
  - capacity_mw: Power transmission capacity (float)
  - length_km: Physical length (float)
  - type: Line type (string: 'overhead', 'underground', 'submarine')
  - status: Current status (string: 'operational', 'maintenance', 'offline')
  - conductor_type: Wire material (string: 'aluminum', 'copper', 'acsr')
  - installed_date: Installation date (date)

Transformer:
  - id: Unique identifier (string)
  - name: Transformer name (string)
  - type: Transformer type (string: 'step-up', 'step-down', 'auto')
  - voltage_primary_kv: Primary voltage (float)
  - voltage_secondary_kv: Secondary voltage (float)
  - capacity_mva: Power capacity (float)
  - status: Current status (string)
  - efficiency_percent: Efficiency (float)
  - manufacturer: Manufacturer name (string)
  - installed_date: Installation date (date)
  - last_maintenance_date: Last maintenance (date)

Sensor:
  - id: Unique identifier (string)
  - type: Sensor type (string: 'voltage', 'current', 'temperature', 'power', 'frequency')
  - model: Device model (string)
  - status: Current status (string: 'active', 'inactive', 'faulty')
  - calibration_date: Last calibration (date)
  - sampling_rate_hz: Data sampling frequency (float)
  - accuracy_percent: Measurement accuracy (float)
  - installed_date: Installation date (date)

Customer:
  - id: Unique identifier (string)
  - name: Customer name (string)
  - type: Customer category (string: 'residential', 'commercial', 'industrial')
  - region: Geographic region (string)
  - location: Geographic coordinates (point)
  - contract_start_date: Service start date (date)
  - average_consumption_kwh: Monthly average usage (float)
  - peak_demand_kw: Peak demand (float)
  - tariff_plan: Pricing plan (string)

Incident:
  - id: Unique identifier (string)
  - type: Incident type (string: 'outage', 'fault', 'overload', 'equipment_failure')
  - severity: Impact level (string: 'low', 'medium', 'high', 'critical')
  - status: Current status (string: 'reported', 'investigating', 'resolved', 'closed')
  - cause: Root cause (string)
  - description: Detailed description (string)
  - occurred_at: Incident timestamp (datetime)
  - detected_at: Detection timestamp (datetime)
  - resolved_at: Resolution timestamp (datetime)
  - affected_customers_count: Number impacted (int)
  - estimated_cost: Financial impact (float)
  - resolution_notes: Resolution details (string)

Regulation:
  - id: Unique identifier (string)
  - code: Regulation code (string)
  - title: Regulation title (string)
  - description: Full description (string)
  - category: Regulation category (string: 'safety', 'environmental', 'operational', 'reporting')
  - authority: Issuing authority (string)
  - effective_date: Start date (date)
  - requirements: Compliance requirements (string)
  - penalty_description: Non-compliance penalty (string)

MaintenanceSchedule:
  - id: Unique identifier (string)
  - type: Maintenance type (string: 'preventive', 'corrective', 'predictive', 'emergency')
  - status: Current status (string: 'scheduled', 'in_progress', 'completed', 'cancelled')
  - scheduled_date: Planned date (date)
  - estimated_duration_hours: Expected duration (float)
  - actual_duration_hours: Actual duration (float)
  - priority: Priority level (string: 'low', 'medium', 'high', 'urgent')
  - cost: Maintenance cost (float)
  - technician: Assigned technician (string)
  - notes: Additional notes (string)

Location:
  - id: Unique identifier (string)
  - name: Location name (string)
  - type: Location type (string: 'region', 'city', 'zone')
  - coordinates: Geographic point (point)
  - population: Population count (int)
  - area_sq_km: Geographic area (float)

Document (for RAG):
  - id: Unique identifier (string)
  - title: Document title (string)
  - type: Document type (string: 'procedure', 'manual', 'regulation', 'report')
  - content: Full text content (string)
  - summary: Brief summary (string)
  - created_at: Creation timestamp (datetime)
  - updated_at: Last update (datetime)
  - author: Author name (string)
  - embedding: Vector embedding (list[float])

Chunk (for RAG):
  - id: Unique identifier (string)
  - text: Chunk text content (string)
  - chunk_index: Position in document (int)
  - embedding: Vector embedding (list[float])
  - token_count: Number of tokens (int)
*/

// ===================================
// RELATIONSHIP TYPES AND PROPERTIES
// ===================================

/*
GENERATES:
  (PowerPlant)-[:GENERATES]->(Substation)
  Properties:
    - active: Boolean indicating if generation is active
    - average_output_mw: Average power generated
    - established_date: Connection date

TRANSMITS_TO:
  (Substation)-[:TRANSMITS_TO]->(Substation)
  Properties:
    - capacity_mw: Transmission capacity
    - distance_km: Physical distance
    - line_id: Associated transmission line
    - loss_percent: Transmission loss
    - status: Link status

SUPPLIES_POWER:
  (Substation)-[:SUPPLIES_POWER]->(Customer)
  Properties:
    - connection_date: Service start date
    - average_load_kw: Average power consumption
    - contract_type: Service contract type

MONITORS:
  (Sensor)-[:MONITORS]->(Equipment)
  Properties:
    - parameter: What is being measured
    - last_reading: Most recent value
    - last_reading_at: Timestamp of last reading
    - unit: Measurement unit

LOCATED_AT:
  (Equipment|Customer)-[:LOCATED_AT]->(Location)
  Properties:
    - since: Date of location association

HAS_TRANSFORMER:
  (Substation)-[:HAS_TRANSFORMER]->(Transformer)
  Properties:
    - position: Physical position identifier
    - primary_usage: Main usage type

CAUSED_BY:
  (Incident)-[:CAUSED_BY]->(Equipment)
  Properties:
    - contribution_percent: Fault contribution

AFFECTS:
  (Incident)-[:AFFECTS]->(Customer|Substation|TransmissionLine)
  Properties:
    - impact_level: Severity of impact
    - duration_minutes: Length of impact

REQUIRES_MAINTENANCE:
  (Equipment)-[:REQUIRES_MAINTENANCE]->(MaintenanceSchedule)
  Properties:
    - reason: Maintenance reason
    - priority: Urgency level

COMPLIES_WITH:
  (PowerPlant|Substation|Equipment)-[:COMPLIES_WITH]->(Regulation)
  Properties:
    - compliance_status: Current compliance state
    - last_audit_date: Date of last audit
    - next_audit_date: Next scheduled audit

RELATED_TO:
  (Incident)-[:RELATED_TO]->(Incident)
  Properties:
    - relationship_type: How incidents are related
    - confidence: Relationship confidence score

CONTAINS:
  (Document)-[:CONTAINS]->(Chunk)
  Properties:
    - order: Chunk order in document

NEXT_CHUNK:
  (Chunk)-[:NEXT_CHUNK]->(Chunk)
  Properties:
    - None (sequential relationship)

MENTIONS:
  (Chunk)-[:MENTIONS]->(PowerPlant|Substation|Regulation|etc.)
  Properties:
    - mention_count: Number of times mentioned
    - context: Surrounding context
*/

// ===================================
// EXAMPLE PATTERNS
// ===================================

// Power flow from generation to consumption:
// (PowerPlant)-[:GENERATES]->(Substation)-[:TRANSMITS_TO*]->(Substation)-[:SUPPLIES_POWER]->(Customer)

// Equipment monitoring:
// (Sensor)-[:MONITORS]->(Equipment)-[:LOCATED_AT]->(Location)

// Incident impact chain:
// (Equipment)<-[:CAUSED_BY]-(Incident)-[:AFFECTS]->(Customer)

// Maintenance relationship:
// (Equipment)-[:REQUIRES_MAINTENANCE]->(MaintenanceSchedule)

// Compliance tracking:
// (Equipment)-[:COMPLIES_WITH]->(Regulation)

// RAG knowledge graph:
// (Document)-[:CONTAINS]->(Chunk)-[:MENTIONS]->(Entity)

// ===================================
// END OF DATA MODEL
// ===================================
