"""Script to verify the utility network database setup."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.infrastructure_repo import InfrastructureRepository
from src.repositories.customer_repo import CustomerRepository
from src.repositories.incident_repo import IncidentRepository
from src.repositories.billing_repo import BillingRepository


def verify_setup():
    """Verify that all data has been loaded correctly."""
    
    conn = Neo4jConnection()
    infra_repo = InfrastructureRepository(conn)
    customer_repo = CustomerRepository(conn)
    incident_repo = IncidentRepository(conn)
    billing_repo = BillingRepository(conn)
    
    print("Verifying Utility Network Operations Setup...")
    print("=" * 60)
    
    errors = []
    
    # 1. Check Node Counts
    print("\n1. Checking Node Counts...")
    node_labels = [
        "PipelineSegment",
        "Meter",
        "Customer",
        "StorageTank",
        "Incident",
        "ServiceRequest",
        "Bill"
    ]
    
    node_counts = {}
    for label in node_labels:
        query = f"MATCH (n:{label}) RETURN count(n) as count"
        result = conn.execute_query(query)
        count = result[0]["count"] if result else 0
        node_counts[label] = count
        print(f"   {label}: {count}")
        
        if count == 0:
            errors.append(f"No {label} nodes found")
    
    # 2. Check Relationships
    print("\n2. Checking Relationships...")
    relationship_types = [
        "CONNECTS_TO",
        "HAS_METER",
        "MONITORS",
        "CONSUMES",
        "HAS_BILL",
        "AFFECTS",
        "REPORTED_BY"
    ]
    
    rel_counts = {}
    for rel_type in relationship_types:
        query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
        result = conn.execute_query(query)
        count = result[0]["count"] if result else 0
        rel_counts[rel_type] = count
        print(f"   {rel_type}: {count}")
    
    # 3. Check Constraints
    print("\n3. Checking Constraints...")
    constraints = conn.execute_query("SHOW CONSTRAINTS")
    print(f"   Total Constraints: {len(constraints)}")
    
    expected_constraints = [
        "pipeline_id",
        "meter_id",
        "customer_id",
        "incident_id",
        "service_request_id",
        "bill_id"
    ]
    
    constraint_names = [c.get("name", "") for c in constraints]
    for expected in expected_constraints:
        found = any(expected in name for name in constraint_names)
        if not found:
            errors.append(f"Constraint '{expected}' not found")
    
    # 4. Check Indexes
    print("\n4. Checking Indexes...")
    indexes = conn.execute_query("SHOW INDEXES")
    print(f"   Total Indexes: {len(indexes)}")
    
    # 5. Test Repository Functions
    print("\n5. Testing Repository Functions...")
    
    # Test infrastructure repo
    try:
        stats = infra_repo.get_infrastructure_statistics()
        print(f"   ✓ Infrastructure Statistics: {stats}")
    except Exception as e:
        errors.append(f"Infrastructure statistics failed: {e}")
    
    # Test customer repo
    try:
        stats = customer_repo.get_customer_statistics()
        print(f"   ✓ Customer Statistics: {stats}")
    except Exception as e:
        errors.append(f"Customer statistics failed: {e}")
    
    # Test incident repo
    try:
        stats = incident_repo.get_incident_statistics()
        print(f"   ✓ Incident Statistics: {stats}")
    except Exception as e:
        errors.append(f"Incident statistics failed: {e}")
    
    # Test billing repo
    try:
        stats = billing_repo.get_billing_statistics()
        print(f"   ✓ Billing Statistics: {stats}")
    except Exception as e:
        errors.append(f"Billing statistics failed: {e}")
    
    # 6. Test Sample Queries
    print("\n6. Testing Sample Queries...")
    
    # Test network topology
    try:
        query = """
        MATCH path = (p1:PipelineSegment)-[:CONNECTS_TO*1..3]-(p2:PipelineSegment)
        WHERE p1.id < p2.id
        RETURN count(path) as paths
        LIMIT 1
        """
        result = conn.execute_query(query)
        path_count = result[0]["paths"] if result else 0
        print(f"   ✓ Network paths found: {path_count}")
    except Exception as e:
        errors.append(f"Network topology query failed: {e}")
    
    # Test customer-meter relationships
    try:
        query = """
        MATCH (c:Customer)-[:HAS_METER]->(m:Meter)
        RETURN count(*) as links
        """
        result = conn.execute_query(query)
        link_count = result[0]["links"] if result else 0
        print(f"   ✓ Customer-Meter links: {link_count}")
        
        if link_count == 0:
            errors.append("No customer-meter links found")
    except Exception as e:
        errors.append(f"Customer-meter query failed: {e}")
    
    # Test consumption data
    try:
        query = """
        MATCH (c:Customer)-[r:CONSUMES]->()
        RETURN count(r) as consumption_records
        """
        result = conn.execute_query(query)
        consumption_count = result[0]["consumption_records"] if result else 0
        print(f"   ✓ Consumption records: {consumption_count}")
        
        if consumption_count == 0:
            errors.append("No consumption records found")
    except Exception as e:
        errors.append(f"Consumption query failed: {e}")
    
    # 7. Check Data Quality
    print("\n7. Checking Data Quality...")
    
    # Check for orphaned nodes
    try:
        query = """
        MATCH (n)
        WHERE NOT (n)--()
        RETURN labels(n)[0] as label, count(n) as orphan_count
        """
        result = conn.execute_query(query)
        if result:
            for row in result:
                print(f"   ⚠ Orphaned {row['label']} nodes: {row['orphan_count']}")
    except Exception as e:
        print(f"   ⚠ Could not check for orphaned nodes: {e}")
    
    # Check for invalid data
    try:
        # Pipelines with invalid pressure
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.current_pressure_psi > p.max_pressure_psi
        RETURN count(p) as invalid_pressure
        """
        result = conn.execute_query(query)
        invalid_pressure = result[0]["invalid_pressure"] if result else 0
        if invalid_pressure > 0:
            print(f"   ⚠ Pipelines with invalid pressure: {invalid_pressure}")
    except Exception as e:
        print(f"   ⚠ Could not check pressure validity: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    
    if errors:
        print("✗ Verification completed with errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nSome components may not be working correctly.")
        return False
    else:
        print("✓ Verification successful!")
        print("\nAll components are working correctly.")
        print("\nDatabase Summary:")
        print(f"  - Total Nodes: {sum(node_counts.values())}")
        print(f"  - Total Relationships: {sum(rel_counts.values())}")
        print(f"  - Constraints: {len(constraints)}")
        print(f"  - Indexes: {len(indexes)}")
        print("\nYou can now run the example scripts:")
        print("  - python examples/01_basic_operations.py")
        print("  - python examples/02_network_monitoring.py")
        print("  - python examples/03_leak_detection.py")
        print("  - python examples/04_consumption_analytics.py")
        print("  - python examples/05_billing_operations.py")
        print("  - python examples/06_service_requests.py")
        print("  - python examples/07_predictive_maintenance.py")
        print("  - python examples/08_customer_chatbot_demo.py")
        return True


if __name__ == "__main__":
    try:
        success = verify_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
