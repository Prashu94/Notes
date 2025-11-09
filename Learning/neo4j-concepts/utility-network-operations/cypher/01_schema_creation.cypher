// ===================================
// SCHEMA CREATION FOR UTILITY NETWORK
// ===================================
// This script creates indexes and constraints for optimal query performance

// ===================================
// CONSTRAINTS (Uniqueness & Existence)
// ===================================

// PipelineSegment constraints
CREATE CONSTRAINT pipeline_id_unique IF NOT EXISTS
FOR (p:PipelineSegment) REQUIRE p.id IS UNIQUE;

// PumpingStation constraints
CREATE CONSTRAINT pump_station_id_unique IF NOT EXISTS
FOR (p:PumpingStation) REQUIRE p.id IS UNIQUE;

// StorageTank constraints
CREATE CONSTRAINT storage_tank_id_unique IF NOT EXISTS
FOR (s:StorageTank) REQUIRE s.id IS UNIQUE;

// Meter constraints
CREATE CONSTRAINT meter_id_unique IF NOT EXISTS
FOR (m:Meter) REQUIRE m.id IS UNIQUE;

// Valve constraints
CREATE CONSTRAINT valve_id_unique IF NOT EXISTS
FOR (v:Valve) REQUIRE v.id IS UNIQUE;

// Sensor constraints
CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS
FOR (s:Sensor) REQUIRE s.id IS UNIQUE;

// Customer constraints
CREATE CONSTRAINT customer_id_unique IF NOT EXISTS
FOR (c:Customer) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT customer_account_unique IF NOT EXISTS
FOR (c:Customer) REQUIRE c.account_number IS UNIQUE;

// ServiceRequest constraints
CREATE CONSTRAINT service_request_id_unique IF NOT EXISTS
FOR (s:ServiceRequest) REQUIRE s.id IS UNIQUE;

// Incident constraints
CREATE CONSTRAINT incident_id_unique IF NOT EXISTS
FOR (i:Incident) REQUIRE i.id IS UNIQUE;

// MaintenanceSchedule constraints
CREATE CONSTRAINT maintenance_schedule_id_unique IF NOT EXISTS
FOR (m:MaintenanceSchedule) REQUIRE m.id IS UNIQUE;

// Bill constraints
CREATE CONSTRAINT bill_id_unique IF NOT EXISTS
FOR (b:Bill) REQUIRE b.id IS UNIQUE;

// Location constraints
CREATE CONSTRAINT location_id_unique IF NOT EXISTS
FOR (l:Location) REQUIRE l.id IS UNIQUE;

// Document constraints (for chatbot)
CREATE CONSTRAINT document_id_unique IF NOT EXISTS
FOR (d:Document) REQUIRE d.id IS UNIQUE;

// ===================================
// B-TREE INDEXES (Property Lookups)
// ===================================

// PipelineSegment indexes
CREATE INDEX pipeline_type_idx IF NOT EXISTS
FOR (p:PipelineSegment) ON (p.type);

CREATE INDEX pipeline_status_idx IF NOT EXISTS
FOR (p:PipelineSegment) ON (p.status);

CREATE INDEX pipeline_material_idx IF NOT EXISTS
FOR (p:PipelineSegment) ON (p.material);

CREATE INDEX pipeline_region_idx IF NOT EXISTS
FOR (p:PipelineSegment) ON (p.region);

// Customer indexes
CREATE INDEX customer_type_idx IF NOT EXISTS
FOR (c:Customer) ON (c.type);

CREATE INDEX customer_status_idx IF NOT EXISTS
FOR (c:Customer) ON (c.status);

CREATE INDEX customer_region_idx IF NOT EXISTS
FOR (c:Customer) ON (c.region);

// Meter indexes
CREATE INDEX meter_type_idx IF NOT EXISTS
FOR (m:Meter) ON (m.type);

CREATE INDEX meter_status_idx IF NOT EXISTS
FOR (m:Meter) ON (m.status);

// ServiceRequest indexes
CREATE INDEX service_request_status_idx IF NOT EXISTS
FOR (s:ServiceRequest) ON (s.status);

CREATE INDEX service_request_priority_idx IF NOT EXISTS
FOR (s:ServiceRequest) ON (s.priority);

CREATE INDEX service_request_type_idx IF NOT EXISTS
FOR (s:ServiceRequest) ON (s.type);

CREATE INDEX service_request_date_idx IF NOT EXISTS
FOR (s:ServiceRequest) ON (s.created_at);

// Incident indexes
CREATE INDEX incident_status_idx IF NOT EXISTS
FOR (i:Incident) ON (i.status);

CREATE INDEX incident_severity_idx IF NOT EXISTS
FOR (i:Incident) ON (i.severity);

CREATE INDEX incident_type_idx IF NOT EXISTS
FOR (i:Incident) ON (i.type);

CREATE INDEX incident_date_idx IF NOT EXISTS
FOR (i:Incident) ON (i.occurred_at);

// Bill indexes
CREATE INDEX bill_status_idx IF NOT EXISTS
FOR (b:Bill) ON (b.status);

CREATE INDEX bill_due_date_idx IF NOT EXISTS
FOR (b:Bill) ON (b.due_date);

CREATE INDEX bill_period_idx IF NOT EXISTS
FOR (b:Bill) ON (b.billing_period);

// Maintenance indexes
CREATE INDEX maintenance_status_idx IF NOT EXISTS
FOR (m:MaintenanceSchedule) ON (m.status);

CREATE INDEX maintenance_date_idx IF NOT EXISTS
FOR (m:MaintenanceSchedule) ON (m.scheduled_date);

// Composite indexes
CREATE INDEX customer_type_status_idx IF NOT EXISTS
FOR (c:Customer) ON (c.type, c.status);

CREATE INDEX incident_status_severity_idx IF NOT EXISTS
FOR (i:Incident) ON (i.status, i.severity);

// ===================================
// POINT INDEXES (Geospatial)
// ===================================

CREATE POINT INDEX location_coordinates_idx IF NOT EXISTS
FOR (l:Location) ON (l.coordinates);

CREATE POINT INDEX pipeline_start_location_idx IF NOT EXISTS
FOR (p:PipelineSegment) ON (p.start_location);

CREATE POINT INDEX pipeline_end_location_idx IF NOT EXISTS
FOR (p:PipelineSegment) ON (p.end_location);

CREATE POINT INDEX customer_location_idx IF NOT EXISTS
FOR (c:Customer) ON (c.location);

// ===================================
// TEXT INDEXES (String Search)
// ===================================

CREATE TEXT INDEX customer_name_text_idx IF NOT EXISTS
FOR (c:Customer) ON (c.name);

CREATE TEXT INDEX customer_address_text_idx IF NOT EXISTS
FOR (c:Customer) ON (c.address);

CREATE TEXT INDEX service_request_description_text_idx IF NOT EXISTS
FOR (s:ServiceRequest) ON (s.description);

// ===================================
// FULL-TEXT INDEXES (Advanced Search)
// ===================================

// Search across service requests
CREATE FULLTEXT INDEX service_request_search_idx IF NOT EXISTS
FOR (s:ServiceRequest) 
ON EACH [s.description, s.resolution_notes, s.type];

// Search across incidents
CREATE FULLTEXT INDEX incident_search_idx IF NOT EXISTS
FOR (i:Incident) 
ON EACH [i.description, i.cause, i.resolution_notes];

// Search across documents (for chatbot)
CREATE FULLTEXT INDEX document_search_idx IF NOT EXISTS
FOR (d:Document) 
ON EACH [d.title, d.content, d.summary];

// Search across customers
CREATE FULLTEXT INDEX customer_search_idx IF NOT EXISTS
FOR (c:Customer) 
ON EACH [c.name, c.address, c.email];

// ===================================
// VECTOR INDEXES (AI/ML Embeddings)
// ===================================

// Vector index for document embeddings (chatbot)
CREATE VECTOR INDEX document_embedding_idx IF NOT EXISTS
FOR (d:Document) ON (d.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Vector index for service request patterns
CREATE VECTOR INDEX service_request_embedding_idx IF NOT EXISTS
FOR (s:ServiceRequest) ON (s.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Vector index for consumption patterns
CREATE VECTOR INDEX consumption_pattern_idx IF NOT EXISTS
FOR (c:Customer) ON (c.consumption_embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 128,
    `vector.similarity_function`: 'cosine'
  }
};

// ===================================
// RELATIONSHIP INDEXES
// ===================================

CREATE INDEX connects_to_diameter_idx IF NOT EXISTS
FOR ()-[r:CONNECTS_TO]-() ON (r.joint_type);

CREATE INDEX consumes_date_idx IF NOT EXISTS
FOR ()-[r:CONSUMES]-() ON (r.date);

CREATE INDEX consumes_amount_idx IF NOT EXISTS
FOR ()-[r:CONSUMES]-() ON (r.amount);

CREATE INDEX monitors_timestamp_idx IF NOT EXISTS
FOR ()-[r:MONITORS]-() ON (r.last_reading_at);

// ===================================
// VERIFICATION
// ===================================

// Show all indexes
SHOW INDEXES;

// Show all constraints
SHOW CONSTRAINTS;
