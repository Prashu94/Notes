"""Script to reset the utility network database."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection


def reset_database():
    """Delete all data and schema from the database."""
    
    conn = Neo4jConnection()
    
    print("Resetting Utility Network Operations Database...")
    print("=" * 60)
    print("\n⚠ WARNING: This will delete ALL data in the database!")
    
    # Ask for confirmation
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("\n✗ Reset cancelled.")
        return
    
    print("\n1. Deleting all relationships...")
    query = "MATCH ()-[r]->() DELETE r"
    conn.execute_query(query)
    print("   ✓ Relationships deleted")
    
    print("\n2. Deleting all nodes...")
    query = "MATCH (n) DELETE n"
    conn.execute_query(query)
    print("   ✓ Nodes deleted")
    
    print("\n3. Dropping constraints...")
    constraints = conn.execute_query("SHOW CONSTRAINTS")
    for constraint in constraints:
        constraint_name = constraint.get("name", "")
        if constraint_name:
            try:
                conn.execute_query(f"DROP CONSTRAINT {constraint_name}")
                print(f"   ✓ Dropped constraint: {constraint_name}")
            except Exception as e:
                print(f"   ⚠ Could not drop constraint {constraint_name}: {e}")
    
    print("\n4. Dropping indexes...")
    indexes = conn.execute_query("SHOW INDEXES")
    for index in indexes:
        index_name = index.get("name", "")
        index_type = index.get("type", "")
        
        # Skip system indexes
        if "system" in index_type.lower() or "lookup" in index_type.lower():
            continue
        
        if index_name:
            try:
                conn.execute_query(f"DROP INDEX {index_name}")
                print(f"   ✓ Dropped index: {index_name}")
            except Exception as e:
                print(f"   ⚠ Could not drop index {index_name}: {e}")
    
    # Verify database is empty
    print("\n5. Verifying database is empty...")
    node_count = conn.execute_query("MATCH (n) RETURN count(n) as count")[0]["count"]
    rel_count = conn.execute_query("MATCH ()-[r]->() RETURN count(r) as count")[0]["count"]
    
    print(f"   Nodes: {node_count}")
    print(f"   Relationships: {rel_count}")
    
    if node_count == 0 and rel_count == 0:
        print("\n" + "=" * 60)
        print("✓ Database reset complete!")
        print("\nTo rebuild the database, run:")
        print("  1. python scripts/01_create_schema.py")
        print("  2. python scripts/02_load_sample_data.py")
        print("  3. python scripts/03_verify_setup.py")
        print("  4. python scripts/04_generate_consumption_data.py")
    else:
        print("\n✗ Database may not be completely empty.")


if __name__ == "__main__":
    try:
        reset_database()
    except Exception as e:
        print(f"\n✗ Error resetting database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
