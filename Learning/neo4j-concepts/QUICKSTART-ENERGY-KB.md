# Quick Start: Energy Knowledge Base Chatbot

A 5-minute guide to get the Energy & Utility RAG chatbot running.

## Prerequisites

- Python 3.8+
- Neo4j instance (Desktop or Aura)
- OpenAI API key

## Installation

```bash
# 1. Install dependencies
pip install neo4j langchain langchain-openai langchain-community openai python-dotenv pypdf python-docx

# 2. Set environment variables
export NEO4J_URI="neo4j+s://your-instance.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
export OPENAI_API_KEY="sk-your-api-key"
```

## Quick Demo

### Step 1: Setup Database Schema

```python
from neo4j import GraphDatabase
import os

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

commands = [
    "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
    "CREATE FULLTEXT INDEX chunk_text_fulltext IF NOT EXISTS FOR (c:Chunk) ON EACH [c.text]",
    "CREATE VECTOR INDEX document_embeddings IF NOT EXISTS FOR (c:Chunk) ON (c.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}"
]

with driver.session() as session:
    for cmd in commands:
        session.run(cmd)

driver.close()
print("✅ Database setup complete!")
```

### Step 2: Ingest Sample Document

```python
from energy_kb_chatbot import EnergyKnowledgeBase

kb = EnergyKnowledgeBase()

# Sample safety regulation
safety_doc = """
OSHA 1910.269 - Electrical Safety Standards

PERSONAL PROTECTIVE EQUIPMENT (PPE):
- Arc flash protection required for live work
- Arc-rated clothing based on incident energy
- Minimum 4 cal/cm² flame-resistant clothing
- Face shields and insulating gloves mandatory

WORK PRACTICES:
- Lockout/Tagout required before maintenance
- Two-person rule for voltage >600V
- Emergency procedures must be posted
- Annual safety training mandatory

CLEARANCE DISTANCES:
- 10 feet minimum for 50kV lines
- 12 feet for 138kV systems
- 15 feet for 345kV systems
"""

doc_id = kb.ingest_document(
    content=safety_doc,
    title="OSHA 1910.269 - Electrical Safety",
    doc_type="regulation",
    metadata={"authority": "OSHA", "category": "Safety"}
)

print(f"✅ Document ingested: {doc_id}")
```

### Step 3: Start Chatting!

```python
# Create chat session
session_id = kb.create_chat_session("Demo Session")

# Ask questions
response = kb.chat(session_id, 
    "What PPE is required for electrical work?")

print(f"\n🤖 Answer:\n{response['answer']}\n")

print(f"📚 Sources:")
for source in response['sources']:
    print(f"  - {source['title']} ({source['type']})")

# Follow-up question (with context!)
response = kb.chat(session_id,
    "What about clearance distances for high voltage?")

print(f"\n🤖 Answer:\n{response['answer']}")

kb.close()
```

## Expected Output

```
🤖 Answer:
According to OSHA 1910.269, the following PPE is required for electrical work:

1. Arc Flash Protection:
   - Arc-rated clothing based on calculated incident energy
   - Minimum 4 cal/cm² flame-resistant clothing
   - Face shields for live work
   - Insulating gloves mandatory

2. Additional Requirements:
   - Equipment must be appropriate for voltage level
   - Two-person rule for work above 600V
   - Annual safety training required

📚 Sources:
  - OSHA 1910.269 - Electrical Safety (regulation)

🤖 Answer:
OSHA 1910.269 specifies the following clearance distances:
- 10 feet minimum for 50kV lines
- 12 feet for 138kV systems  
- 15 feet for 345kV systems

These distances must be maintained to prevent electrical accidents.
```

## Features Demonstrated

✅ **Conversational Memory**: Follow-up questions use context  
✅ **Source Citations**: Every answer references source documents  
✅ **Semantic Search**: Finds relevant info even with different wording  
✅ **Entity Awareness**: Understands equipment, regulations, locations  

## Next Steps

### Load More Documents

```python
# Load comprehensive sample data
# See load_sample_data.py in 08-energy-kb-implementation.md

# Or ingest your own documents:
kb.ingest_from_file("path/to/your/document.pdf", 
                     doc_type="manual",
                     metadata={"category": "Maintenance"})
```

### Advanced Search

```python
# Hybrid search with filters
results = kb.search(
    query="transformer maintenance procedures",
    filters={
        "doc_type": "procedure",
        "date_from": "2024-01-01"
    },
    k=5
)

for result in results:
    print(f"- {result['documentTitle']}")
    print(f"  Score: {result['score']:.3f}")
```

### Analytics

```python
# Get knowledge base statistics
stats = kb.get_kb_statistics()
print(f"Documents: {stats['documents']}")
print(f"Chunks: {stats['chunks']}")
print(f"Entities: {stats['entities']}")

# Find specific equipment
equipment = kb.find_equipment(name_pattern="transformer")
for eq in equipment:
    print(f"- {eq['equipment']}: {eq['documentCount']} mentions")
```

## Web API (Optional)

Deploy as a REST API:

```python
# Run the web server
uvicorn web_api:app --reload --port 8000

# Test with curl
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the safety requirements?"}'
```

## Common Issues

### Issue: "Vector index not found"
**Solution**: Wait 30-60 seconds after creating the vector index for it to become available.

### Issue: "OpenAI rate limit"
**Solution**: Add retry logic or upgrade your OpenAI plan.

### Issue: "No relevant documents found"
**Solution**: Ensure documents are ingested and vector embeddings are created.

## Production Checklist

Before deploying to production:

- [ ] Set up proper authentication
- [ ] Implement rate limiting
- [ ] Add monitoring and logging
- [ ] Configure backups for Neo4j
- [ ] Set up error alerting
- [ ] Test with production data volume
- [ ] Review security best practices
- [ ] Document API endpoints
- [ ] Create user documentation
- [ ] Set up CI/CD pipeline

## Resources

- Full Implementation: [08-energy-kb-implementation.md](08-energy-kb-implementation.md)
- RAG Concepts: [06-rag-with-neo4j.md](06-rag-with-neo4j.md)
- Python Code: [python-examples/energy_kb_chatbot.py](python-examples/energy_kb_chatbot.py)

## Use Cases Beyond Energy

This architecture works for any domain:

- **Healthcare**: Medical guidelines, patient care procedures
- **Legal**: Case law, regulations, contract analysis
- **Manufacturing**: Equipment manuals, quality procedures
- **Finance**: Compliance regulations, risk policies
- **IT**: Technical documentation, troubleshooting guides

Just adapt the entity types and document metadata to your domain!

---

**Need Help?** Check the full documentation in `08-energy-kb-implementation.md` for detailed examples, sample data, and deployment guides.
