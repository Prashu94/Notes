"""
Setup Neo4j database with required indexes and constraints
Run this script once before using the applications
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


def setup_database():
    """Create all necessary indexes and constraints"""
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    print("🔧 Setting up Neo4j database...\n")
    
    try:
        with driver.session() as session:
            
            # ===== CONSTRAINTS =====
            print("📋 Creating constraints...")
            
            constraints = [
                "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
                "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
                "CREATE CONSTRAINT user_userId IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE",
                "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
                "CREATE CONSTRAINT movie_movieId IF NOT EXISTS FOR (m:Movie) REQUIRE m.movieId IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"  ✅ {constraint.split('FOR')[0].strip()}")
                except Exception as e:
                    print(f"  ⚠️  Constraint may already exist: {str(e)[:50]}")
            
            # ===== INDEXES =====
            print("\n📇 Creating indexes...")
            
            indexes = [
                "CREATE INDEX document_title IF NOT EXISTS FOR (d:Document) ON (d.title)",
                "CREATE INDEX chunk_text IF NOT EXISTS FOR (c:Chunk) ON (c.text)",
                "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
                "CREATE INDEX user_username IF NOT EXISTS FOR (u:User) ON (u.username)",
                "CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title)",
                "CREATE INDEX movie_year IF NOT EXISTS FOR (m:Movie) ON (m.year)",
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    print(f"  ✅ {index.split('FOR')[0].strip()}")
                except Exception as e:
                    print(f"  ⚠️  Index may already exist: {str(e)[:50]}")
            
            # ===== FULL-TEXT INDEXES =====
            print("\n🔍 Creating full-text indexes...")
            
            fulltext_indexes = [
                """
                CREATE FULLTEXT INDEX chunk_text_fulltext IF NOT EXISTS
                FOR (c:Chunk) ON EACH [c.text]
                """,
                """
                CREATE FULLTEXT INDEX movie_search IF NOT EXISTS
                FOR (m:Movie) ON EACH [m.title, m.plot]
                """,
            ]
            
            for ft_index in fulltext_indexes:
                try:
                    session.run(ft_index)
                    print(f"  ✅ Full-text index created")
                except Exception as e:
                    print(f"  ⚠️  Full-text index may already exist: {str(e)[:50]}")
            
            # ===== VECTOR INDEX =====
            print("\n🎯 Creating vector index...")
            
            vector_index = """
            CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
            FOR (c:Chunk) ON (c.embedding)
            OPTIONS {
                indexConfig: {
                    `vector.dimensions`: 1536,
                    `vector.similarity_function`: 'cosine'
                }
            }
            """
            
            try:
                session.run(vector_index)
                print("  ✅ Vector index created (OpenAI ada-002: 1536 dimensions)")
            except Exception as e:
                print(f"  ⚠️  Vector index may already exist: {str(e)[:50]}")
            
            # ===== VERIFY =====
            print("\n✅ Verifying setup...")
            
            # Count indexes
            result = session.run("SHOW INDEXES YIELD name, type")
            indexes_list = list(result)
            print(f"  📊 Total indexes: {len(indexes_list)}")
            
            # Count constraints
            result = session.run("SHOW CONSTRAINTS YIELD name")
            constraints_list = list(result)
            print(f"  📊 Total constraints: {len(constraints_list)}")
            
            print("\n🎉 Database setup completed successfully!")
            print("\n💡 You can now run the example applications.")
    
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        raise
    
    finally:
        driver.close()


if __name__ == "__main__":
    setup_database()
