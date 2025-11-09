"""Script to create Neo4j schema (constraints and indexes) for utility network."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection


def create_schema():
    """Create all constraints and indexes for the utility network database."""
    
    conn = Neo4jConnection()
    
    print("Creating Neo4j schema for Utility Network Operations...")
    print("=" * 60)
    
    # Constraints (ensure uniqueness and existence)
    constraints = [
        # PipelineSegment
        "CREATE CONSTRAINT pipeline_id IF NOT EXISTS FOR (p:PipelineSegment) REQUIRE p.id IS UNIQUE",
        
        # Meter
        "CREATE CONSTRAINT meter_id IF NOT EXISTS FOR (m:Meter) REQUIRE m.id IS UNIQUE",
        "CREATE CONSTRAINT meter_serial IF NOT EXISTS FOR (m:Meter) REQUIRE m.serial_number IS UNIQUE",
        
        # Customer
        "CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE",
        
        # StorageTank
        "CREATE CONSTRAINT tank_id IF NOT EXISTS FOR (t:StorageTank) REQUIRE t.id IS UNIQUE",
        
        # Incident
        "CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE",
        
        # ServiceRequest
        "CREATE CONSTRAINT service_request_id IF NOT EXISTS FOR (sr:ServiceRequest) REQUIRE sr.id IS UNIQUE",
        
        # Bill
        "CREATE CONSTRAINT bill_id IF NOT EXISTS FOR (b:Bill) REQUIRE b.id IS UNIQUE",
        
        # Sensor (if used)
        "CREATE CONSTRAINT sensor_id IF NOT EXISTS FOR (s:Sensor) REQUIRE s.id IS UNIQUE",
        
        # Valve (if used)
        "CREATE CONSTRAINT valve_id IF NOT EXISTS FOR (v:Valve) REQUIRE v.id IS UNIQUE",
    ]
    
    # Indexes (improve query performance)
    indexes = [
        # Pipeline indexes
        "CREATE INDEX pipeline_region IF NOT EXISTS FOR (p:PipelineSegment) ON (p.region)",
        "CREATE INDEX pipeline_type IF NOT EXISTS FOR (p:PipelineSegment) ON (p.type)",
        "CREATE INDEX pipeline_status IF NOT EXISTS FOR (p:PipelineSegment) ON (p.status)",
        "CREATE INDEX pipeline_material IF NOT EXISTS FOR (p:PipelineSegment) ON (p.material)",
        
        # Meter indexes
        "CREATE INDEX meter_status IF NOT EXISTS FOR (m:Meter) ON (m.status)",
        "CREATE INDEX meter_type IF NOT EXISTS FOR (m:Meter) ON (m.type)",
        "CREATE INDEX meter_battery IF NOT EXISTS FOR (m:Meter) ON (m.battery_level)",
        
        # Customer indexes
        "CREATE INDEX customer_type IF NOT EXISTS FOR (c:Customer) ON (c.type)",
        "CREATE INDEX customer_status IF NOT EXISTS FOR (c:Customer) ON (c.status)",
        "CREATE INDEX customer_city IF NOT EXISTS FOR (c:Customer) ON (c.city)",
        "CREATE INDEX customer_name IF NOT EXISTS FOR (c:Customer) ON (c.name)",
        
        # Incident indexes
        "CREATE INDEX incident_type IF NOT EXISTS FOR (i:Incident) ON (i.type)",
        "CREATE INDEX incident_severity IF NOT EXISTS FOR (i:Incident) ON (i.severity)",
        "CREATE INDEX incident_status IF NOT EXISTS FOR (i:Incident) ON (i.status)",
        "CREATE INDEX incident_date IF NOT EXISTS FOR (i:Incident) ON (i.reported_date)",
        
        # ServiceRequest indexes
        "CREATE INDEX sr_status IF NOT EXISTS FOR (sr:ServiceRequest) ON (sr.status)",
        "CREATE INDEX sr_priority IF NOT EXISTS FOR (sr:ServiceRequest) ON (sr.priority)",
        "CREATE INDEX sr_type IF NOT EXISTS FOR (sr:ServiceRequest) ON (sr.type)",
        "CREATE INDEX sr_customer IF NOT EXISTS FOR (sr:ServiceRequest) ON (sr.customer_id)",
        "CREATE INDEX sr_date IF NOT EXISTS FOR (sr:ServiceRequest) ON (sr.created_date)",
        
        # Bill indexes
        "CREATE INDEX bill_status IF NOT EXISTS FOR (b:Bill) ON (b.status)",
        "CREATE INDEX bill_customer IF NOT EXISTS FOR (b:Bill) ON (b.customer_id)",
        "CREATE INDEX bill_due_date IF NOT EXISTS FOR (b:Bill) ON (b.due_date)",
        
        # Geospatial indexes (for location-based queries)
        "CREATE POINT INDEX pipeline_location IF NOT EXISTS FOR (p:PipelineSegment) ON (p.latitude, p.longitude)",
        "CREATE POINT INDEX customer_location IF NOT EXISTS FOR (c:Customer) ON (c.latitude, c.longitude)",
        "CREATE POINT INDEX incident_location IF NOT EXISTS FOR (i:Incident) ON (i.latitude, i.longitude)",
    ]
    
    # Create constraints
    print("\n1. Creating Constraints...")
    for constraint in constraints:
        try:
            conn.execute_query(constraint)
            # Extract constraint name
            constraint_name = constraint.split("CONSTRAINT")[1].split("IF")[0].strip()
            print(f"   ✓ {constraint_name}")
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"   ✗ Error: {e}")
    
    # Create indexes
    print("\n2. Creating Indexes...")
    for index in indexes:
        try:
            conn.execute_query(index)
            # Extract index name
            index_name = index.split("INDEX")[1].split("IF")[0].strip()
            print(f"   ✓ {index_name}")
        except Exception as e:
            if "already exists" not in str(e).lower():
                print(f"   ✗ Error: {e}")
    
    # Verify schema
    print("\n3. Verifying Schema...")
    constraints_result = conn.execute_query("SHOW CONSTRAINTS")
    indexes_result = conn.execute_query("SHOW INDEXES")
    
    print(f"   Total Constraints: {len(constraints_result)}")
    print(f"   Total Indexes: {len(indexes_result)}")
    
    print("\n" + "=" * 60)
    print("✓ Schema creation complete!")
    print("\nNext steps:")
    print("  1. Run: python scripts/02_load_sample_data.py")
    print("  2. Run: python scripts/03_verify_setup.py")


if __name__ == "__main__":
    try:
        create_schema()
    except Exception as e:
        print(f"\n✗ Error creating schema: {e}")
        sys.exit(1)
