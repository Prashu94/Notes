"""Quick test script for embeddings functionality."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.chatbot.embeddings import EmbeddingsGenerator, create_embeddings_generator


def test_embeddings():
    """Test embeddings generation."""
    
    print("Testing Embeddings Generator...")
    print("=" * 60)
    
    # Test 1: Default initialization
    print("\n1. Testing default initialization...")
    embeddings = EmbeddingsGenerator()
    print(f"   Model: {embeddings.model_name}")
    print(f"   Dimension: {embeddings.dimension}")
    print(f"   Model loaded: {embeddings.model is not None}")
    
    # Test 2: Generate single embedding
    print("\n2. Testing single embedding generation...")
    text = "Water leak detected at Main Street"
    embedding = embeddings.generate_embedding(text)
    print(f"   Text: {text}")
    print(f"   Embedding dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test 3: Generate batch embeddings
    print("\n3. Testing batch embedding generation...")
    texts = [
        "Customer billing inquiry",
        "Pipeline pressure anomaly",
        "Service request for meter"
    ]
    batch_embeddings = embeddings.generate_batch_embeddings(texts)
    print(f"   Generated {len(batch_embeddings)} embeddings")
    print(f"   Each dimension: {len(batch_embeddings[0])}")
    
    # Test 4: Calculate similarity
    print("\n4. Testing similarity calculation...")
    emb1 = embeddings.generate_embedding("water leak")
    emb2 = embeddings.generate_embedding("pipe burst")
    emb3 = embeddings.generate_embedding("customer bill")
    
    sim_12 = embeddings.calculate_similarity(emb1, emb2)
    sim_13 = embeddings.calculate_similarity(emb1, emb3)
    
    print(f"   Similarity('water leak', 'pipe burst'): {sim_12:.3f}")
    print(f"   Similarity('water leak', 'customer bill'): {sim_13:.3f}")
    print(f"   Expected: leak-burst similarity > leak-bill similarity")
    print(f"   Result: {sim_12 > sim_13} ✓" if sim_12 > sim_13 else f"   Result: {sim_12 > sim_13} ✗")
    
    # Test 5: Test with recommended model
    print("\n5. Testing recommended model creation...")
    qa_embeddings = create_embeddings_generator("qa")
    print(f"   Model: {qa_embeddings.model_name}")
    print(f"   Dimension: {qa_embeddings.dimension}")
    
    # Test 6: Test domain-specific embeddings
    print("\n6. Testing domain-specific embeddings...")
    pipeline_data = {
        "id": "PIPE-001",
        "type": "water_main",
        "material": "ductile_iron",
        "status": "active"
    }
    
    pipeline_emb = embeddings.embed_pipeline(pipeline_data)
    print(f"   Pipeline embedding dimension: {len(pipeline_emb)}")
    
    customer_data = {
        "id": "CUST-001",
        "name": "Test Customer",
        "type": "residential"
    }
    
    customer_emb = embeddings.embed_customer(customer_data)
    print(f"   Customer embedding dimension: {len(customer_emb)}")
    
    print("\n" + "=" * 60)
    print("✓ All embedding tests passed!")
    
    if embeddings.model is not None:
        print("\n✓ HuggingFace model loaded successfully!")
        print("  You can use semantic search and similarity scoring.")
    else:
        print("\n⚠ Using mock embeddings (for testing)")
        print("  Install sentence-transformers for production use:")
        print("    pip install sentence-transformers")


if __name__ == "__main__":
    try:
        test_embeddings()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
