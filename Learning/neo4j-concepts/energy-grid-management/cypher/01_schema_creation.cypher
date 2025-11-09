// ===================================
// SCHEMA CREATION FOR ENERGY GRID
// ===================================
// This script creates indexes and constraints for optimal query performance

// ===================================
// CONSTRAINTS (Uniqueness & Existence)
// ===================================

// PowerPlant constraints
CREATE CONSTRAINT power_plant_id_unique IF NOT EXISTS
FOR (p:PowerPlant) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT power_plant_name_unique IF NOT EXISTS
FOR (p:PowerPlant) REQUIRE p.name IS UNIQUE;

// Substation constraints
CREATE CONSTRAINT substation_id_unique IF NOT EXISTS
FOR (s:Substation) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT substation_name_unique IF NOT EXISTS
FOR (s:Substation) REQUIRE s.name IS UNIQUE;

// TransmissionLine constraints
CREATE CONSTRAINT transmission_line_id_unique IF NOT EXISTS
FOR (t:TransmissionLine) REQUIRE t.id IS UNIQUE;

// Transformer constraints
CREATE CONSTRAINT transformer_id_unique IF NOT EXISTS
FOR (t:Transformer) REQUIRE t.id IS UNIQUE;

// Sensor constraints
CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS
FOR (s:Sensor) REQUIRE s.id IS UNIQUE;

// Customer constraints
CREATE CONSTRAINT customer_id_unique IF NOT EXISTS
FOR (c:Customer) REQUIRE c.id IS UNIQUE;

// Incident constraints
CREATE CONSTRAINT incident_id_unique IF NOT EXISTS
FOR (i:Incident) REQUIRE i.id IS UNIQUE;

// Regulation constraints
CREATE CONSTRAINT regulation_id_unique IF NOT EXISTS
FOR (r:Regulation) REQUIRE r.id IS UNIQUE;

// MaintenanceSchedule constraints
CREATE CONSTRAINT maintenance_id_unique IF NOT EXISTS
FOR (m:MaintenanceSchedule) REQUIRE m.id IS UNIQUE;

// Location constraints
CREATE CONSTRAINT location_id_unique IF NOT EXISTS
FOR (l:Location) REQUIRE l.id IS UNIQUE;

// Document constraints (for RAG)
CREATE CONSTRAINT document_id_unique IF NOT EXISTS
FOR (d:Document) REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
FOR (c:Chunk) REQUIRE c.id IS UNIQUE;

// ===================================
// B-TREE INDEXES (Property Lookups)
// ===================================

// PowerPlant indexes
CREATE INDEX power_plant_type_idx IF NOT EXISTS
FOR (p:PowerPlant) ON (p.type);

CREATE INDEX power_plant_status_idx IF NOT EXISTS
FOR (p:PowerPlant) ON (p.status);

CREATE INDEX power_plant_capacity_idx IF NOT EXISTS
FOR (p:PowerPlant) ON (p.capacity_mw);

// Substation indexes
CREATE INDEX substation_voltage_idx IF NOT EXISTS
FOR (s:Substation) ON (s.voltage_kv);

CREATE INDEX substation_status_idx IF NOT EXISTS
FOR (s:Substation) ON (s.status);

CREATE INDEX substation_region_idx IF NOT EXISTS
FOR (s:Substation) ON (s.region);

// Customer indexes
CREATE INDEX customer_type_idx IF NOT EXISTS
FOR (c:Customer) ON (c.type);

CREATE INDEX customer_region_idx IF NOT EXISTS
FOR (c:Customer) ON (c.region);

// Incident indexes
CREATE INDEX incident_status_idx IF NOT EXISTS
FOR (i:Incident) ON (i.status);

CREATE INDEX incident_severity_idx IF NOT EXISTS
FOR (i:Incident) ON (i.severity);

CREATE INDEX incident_type_idx IF NOT EXISTS
FOR (i:Incident) ON (i.type);

CREATE INDEX incident_date_idx IF NOT EXISTS
FOR (i:Incident) ON (i.occurred_at);

// Sensor indexes
CREATE INDEX sensor_type_idx IF NOT EXISTS
FOR (s:Sensor) ON (s.type);

CREATE INDEX sensor_status_idx IF NOT EXISTS
FOR (s:Sensor) ON (s.status);

// Maintenance indexes
CREATE INDEX maintenance_status_idx IF NOT EXISTS
FOR (m:MaintenanceSchedule) ON (m.status);

CREATE INDEX maintenance_date_idx IF NOT EXISTS
FOR (m:MaintenanceSchedule) ON (m.scheduled_date);

// Composite indexes for common queries
CREATE INDEX power_plant_type_status_idx IF NOT EXISTS
FOR (p:PowerPlant) ON (p.type, p.status);

CREATE INDEX incident_status_severity_idx IF NOT EXISTS
FOR (i:Incident) ON (i.status, i.severity);

// ===================================
// POINT INDEXES (Geospatial)
// ===================================

CREATE POINT INDEX location_coordinates_idx IF NOT EXISTS
FOR (l:Location) ON (l.coordinates);

CREATE POINT INDEX power_plant_location_idx IF NOT EXISTS
FOR (p:PowerPlant) ON (p.location);

CREATE POINT INDEX substation_location_idx IF NOT EXISTS
FOR (s:Substation) ON (s.location);

// ===================================
// TEXT INDEXES (String Search)
// ===================================

CREATE TEXT INDEX power_plant_name_text_idx IF NOT EXISTS
FOR (p:PowerPlant) ON (p.name);

CREATE TEXT INDEX customer_name_text_idx IF NOT EXISTS
FOR (c:Customer) ON (c.name);

CREATE TEXT INDEX incident_description_text_idx IF NOT EXISTS
FOR (i:Incident) ON (i.description);

// ===================================
// FULL-TEXT INDEXES (Advanced Search)
// ===================================

// Search across power plants
CREATE FULLTEXT INDEX power_plant_search_idx IF NOT EXISTS
FOR (p:PowerPlant) 
ON EACH [p.name, p.description, p.operator];

// Search across incidents
CREATE FULLTEXT INDEX incident_search_idx IF NOT EXISTS
FOR (i:Incident) 
ON EACH [i.description, i.cause, i.resolution_notes];

// Search across regulations
CREATE FULLTEXT INDEX regulation_search_idx IF NOT EXISTS
FOR (r:Regulation) 
ON EACH [r.title, r.description, r.requirements];

// Search across documents (for RAG)
CREATE FULLTEXT INDEX document_search_idx IF NOT EXISTS
FOR (d:Document) 
ON EACH [d.title, d.content, d.summary];

// ===================================
// VECTOR INDEXES (AI/ML Embeddings)
// ===================================

// Vector index for document embeddings (RAG)
CREATE VECTOR INDEX document_embedding_idx IF NOT EXISTS
FOR (d:Document) ON (d.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Vector index for chunk embeddings (RAG)
CREATE VECTOR INDEX chunk_embedding_idx IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Vector index for incident embeddings (similarity search)
CREATE VECTOR INDEX incident_embedding_idx IF NOT EXISTS
FOR (i:Incident) ON (i.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// ===================================
// RELATIONSHIP INDEXES
// ===================================

CREATE INDEX transmits_to_capacity_idx IF NOT EXISTS
FOR ()-[r:TRANSMITS_TO]-() ON (r.capacity_mw);

CREATE INDEX transmits_to_distance_idx IF NOT EXISTS
FOR ()-[r:TRANSMITS_TO]-() ON (r.distance_km);

CREATE INDEX monitors_timestamp_idx IF NOT EXISTS
FOR ()-[r:MONITORS]-() ON (r.last_reading_at);

// ===================================
// VERIFICATION
// ===================================

// Show all indexes
SHOW INDEXES;

// Show all constraints
SHOW CONSTRAINTS;
