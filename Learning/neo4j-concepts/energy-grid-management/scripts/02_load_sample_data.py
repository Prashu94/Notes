#!/usr/bin/env python3
"""
Setup Script 2: Load Sample Data

This script loads sample power grid data into the database.
Run this after creating the schema.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connection import get_connection, close_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def read_cypher_file(filename: str) -> str:
    """Read Cypher script from file."""
    cypher_dir = Path(__file__).parent.parent / "cypher"
    file_path = cypher_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Cypher file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return f.read()


def execute_cypher_script(connection, script: str) -> None:
    """Execute a complete Cypher script."""
    try:
        connection.execute_write(script)
        logger.info("✓ Script executed successfully")
    except Exception as e:
        logger.error(f"✗ Failed to execute script: {e}")
        raise


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Loading Sample Data into Energy Grid Database")
    logger.info("=" * 60)
    
    connection = None
    
    try:
        # Connect to database
        logger.info("\n1. Connecting to Neo4j...")
        connection = get_connection()
        
        if not connection.verify_connection():
            logger.error("Failed to connect to Neo4j")
            sys.exit(1)
        
        logger.info("✓ Connected successfully")
        
        # Check if data already exists
        logger.info("\n2. Checking existing data...")
        node_count = connection.get_node_count()
        
        if node_count > 0:
            logger.warning(f"⚠ Database already contains {node_count} nodes")
            response = input("Do you want to continue and add more data? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Operation cancelled")
                sys.exit(0)
        
        # Load sample data
        logger.info("\n3. Loading sample data...")
        data_script = read_cypher_file("03_sample_data.cypher")
        execute_cypher_script(connection, data_script)
        logger.info("✓ Sample data loaded")
        
        # Verify data load
        logger.info("\n4. Verifying data load...")
        
        node_count = connection.get_node_count()
        rel_count = connection.get_relationship_count()
        
        logger.info(f"✓ Total nodes: {node_count}")
        logger.info(f"✓ Total relationships: {rel_count}")
        
        # Show node distribution
        logger.info("\n5. Node distribution by label:")
        label_counts = connection.get_label_counts()
        for label, count in label_counts.items():
            logger.info(f"   • {label}: {count}")
        
        # Show relationship distribution
        logger.info("\n6. Relationship distribution by type:")
        rel_counts = connection.get_relationship_type_counts()
        for rel_type, count in rel_counts.items():
            logger.info(f"   • {rel_type}: {count}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Sample data loaded successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n✗ Error during data load: {e}")
        sys.exit(1)
    
    finally:
        if connection:
            close_connection()


if __name__ == "__main__":
    main()
