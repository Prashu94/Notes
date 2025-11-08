"""
Simple Neo4j example - Getting started
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


def main():
    # Connect to Neo4j
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        # Verify connection
        driver.verify_connectivity()
        print("✅ Connected to Neo4j successfully!\n")
        
        # Create some data
        with driver.session() as session:
            # Create nodes
            session.run("""
                CREATE (alice:Person {name: 'Alice', age: 30})
                CREATE (bob:Person {name: 'Bob', age: 35})
                CREATE (alice)-[:FRIENDS_WITH {since: 2020}]->(bob)
            """)
            print("✅ Created sample data\n")
            
            # Query data
            result = session.run("""
                MATCH (p:Person)
                RETURN p.name AS name, p.age AS age
                ORDER BY p.age
            """)
            
            print("📊 People in database:")
            for record in result:
                print(f"  - {record['name']}, age {record['age']}")
            
            print("\n✅ Example completed!")
            
            # Clean up
            session.run("MATCH (n:Person) DETACH DELETE n")
            print("🧹 Cleaned up test data")
    
    finally:
        driver.close()


if __name__ == "__main__":
    main()
