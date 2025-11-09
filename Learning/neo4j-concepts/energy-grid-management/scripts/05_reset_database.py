"""
Database Reset Script

Cleans the database by removing all nodes and relationships.
Use with caution!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from connection import get_connection


def confirm_reset():
    """Ask user to confirm database reset."""
    print("\n" + "⚠️ " * 20)
    print("\n  WARNING: This will DELETE ALL DATA in your Neo4j database!")
    print("  This action cannot be undone.")
    print("\n" + "⚠️ " * 20 + "\n")
    
    response = input("Type 'DELETE EVERYTHING' to confirm: ")
    
    return response == "DELETE EVERYTHING"


def get_statistics(conn):
    """Get current database statistics."""
    query = """
    MATCH (n)
    RETURN count(n) as node_count
    """
    results = conn.execute_read(query)
    node_count = results[0]['node_count'] if results else 0
    
    query = """
    MATCH ()-[r]->()
    RETURN count(r) as rel_count
    """
    results = conn.execute_read(query)
    rel_count = results[0]['rel_count'] if results else 0
    
    return node_count, rel_count


def delete_all_data(conn):
    """Delete all nodes and relationships."""
    print("\n🗑️  Deleting all data...")
    
    # Delete in batches to avoid memory issues
    batch_size = 10000
    total_deleted = 0
    
    while True:
        query = f"""
        MATCH (n)
        WITH n LIMIT {batch_size}
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        results = conn.execute_write(query)
        deleted = results[0]['deleted'] if results else 0
        total_deleted += deleted
        
        if deleted > 0:
            print(f"  Deleted {deleted} nodes... (Total: {total_deleted})")
        
        if deleted < batch_size:
            break
    
    print(f"\n✅ Deleted {total_deleted} total nodes and their relationships")


def drop_constraints(conn):
    """Drop all constraints."""
    print("\n🗑️  Dropping constraints...")
    
    # Get all constraints
    query = "SHOW CONSTRAINTS"
    constraints = conn.execute_read(query)
    
    for constraint in constraints:
        constraint_name = constraint.get('name')
        if constraint_name:
            try:
                drop_query = f"DROP CONSTRAINT {constraint_name} IF EXISTS"
                conn.execute_write(drop_query)
                print(f"  Dropped constraint: {constraint_name}")
            except Exception as e:
                print(f"  ⚠️  Could not drop {constraint_name}: {e}")
    
    print(f"✅ Dropped {len(constraints)} constraint(s)")


def drop_indexes(conn):
    """Drop all indexes (except constraint-backing indexes)."""
    print("\n🗑️  Dropping indexes...")
    
    # Get all indexes
    query = "SHOW INDEXES"
    indexes = conn.execute_read(query)
    
    dropped = 0
    for index in indexes:
        index_name = index.get('name')
        # Skip constraint-backing indexes
        if index_name and 'constraint' not in index_name.lower():
            try:
                drop_query = f"DROP INDEX {index_name} IF EXISTS"
                conn.execute_write(drop_query)
                print(f"  Dropped index: {index_name}")
                dropped += 1
            except Exception as e:
                print(f"  ⚠️  Could not drop {index_name}: {e}")
    
    print(f"✅ Dropped {dropped} index(es)")


def verify_empty(conn):
    """Verify database is empty."""
    node_count, rel_count = get_statistics(conn)
    
    if node_count == 0 and rel_count == 0:
        print("\n✅ Database is now empty")
        return True
    else:
        print(f"\n⚠️  Database still has {node_count} nodes and {rel_count} relationships")
        return False


def main():
    """Main reset function."""
    print("\n" + "=" * 70)
    print(" Energy Grid Management - Database Reset")
    print("=" * 70)
    
    conn = get_connection()
    
    try:
        # Check connection
        if not conn.verify_connection():
            print("\n❌ Failed to connect to Neo4j")
            sys.exit(1)
        
        print("✅ Connected to Neo4j")
        
        # Show current statistics
        node_count, rel_count = get_statistics(conn)
        print(f"\nCurrent database:")
        print(f"  Nodes: {node_count}")
        print(f"  Relationships: {rel_count}")
        
        # Confirm reset
        if not confirm_reset():
            print("\n❌ Reset cancelled")
            sys.exit(0)
        
        # Perform reset
        delete_all_data(conn)
        drop_constraints(conn)
        drop_indexes(conn)
        
        # Verify
        verify_empty(conn)
        
        print("\n" + "=" * 70)
        print(" ✅ Database Reset Complete!")
        print("=" * 70)
        print("\nYou can now recreate the schema:")
        print("  python scripts/01_create_schema.py")
        print("  python scripts/02_load_sample_data.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during reset: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
