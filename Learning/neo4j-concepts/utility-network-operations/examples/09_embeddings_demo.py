"""Example script demonstrating embeddings functionality."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.chatbot.embeddings import (
    EmbeddingsGenerator,
    EMBEDDING_CONFIGS,
    get_recommended_model,
    create_embeddings_generator,
    install_instructions
)


def main():
    """Demonstrate embeddings functionality."""
    
    print("=" * 60)
    print("Utility Network - Embeddings Example")
    print("=" * 60)
    
    # 1. Show available models
    print("\n1. Available Embedding Models")
    print("-" * 60)
    
    for model_name, config in EMBEDDING_CONFIGS.items():
        print(f"\n{model_name}:")
        print(f"  Description: {config['description']}")
        print(f"  Dimension: {config['dimension']}")
        print(f"  Speed: {config['speed']}")
        print(f"  Quality: {config['quality']}")
    
    # 2. Get recommendations
    print("\n2. Recommended Models by Use Case")
    print("-" * 60)
    
    use_cases = ["general", "qa", "multilingual", "best_quality", "fastest"]
    
    for use_case in use_cases:
        config = get_recommended_model(use_case)
        print(f"\n{use_case.upper()}:")
        print(f"  Model: {config.get('model_path', config['model_name'])}")
        print(f"  {config['description']}")
    
    # 3. Create embeddings generator
    print("\n3. Creating Embeddings Generator")
    print("-" * 60)
    
    # Try to create with HuggingFace model
    print("\nAttempting to load HuggingFace model...")
    embeddings = EmbeddingsGenerator(
        model_name="sentence-transformers",
        model_path="all-MiniLM-L6-v2"
    )
    
    print(f"Model: {embeddings.model_name}")
    print(f"Dimension: {embeddings.dimension}")
    
    # 4. Generate embeddings
    print("\n4. Generating Embeddings")
    print("-" * 60)
    
    sample_texts = [
        "Water leak detected at 123 Main Street",
        "Customer billing inquiry about monthly consumption",
        "Pipeline pressure anomaly in downtown region",
        "Service request for meter battery replacement",
        "Network outage affecting 50 customers"
    ]
    
    print("\nSample Texts:")
    for i, text in enumerate(sample_texts, 1):
        print(f"  {i}. {text}")
    
    print("\nGenerating embeddings...")
    embeddings_list = embeddings.generate_batch_embeddings(sample_texts)
    
    print(f"✓ Generated {len(embeddings_list)} embeddings")
    print(f"  Dimension: {len(embeddings_list[0])}")
    print(f"  First embedding (first 5 values): {embeddings_list[0][:5]}")
    
    # 5. Calculate similarity
    print("\n5. Calculating Similarity Scores")
    print("-" * 60)
    
    query = "Report a leak"
    query_embedding = embeddings.generate_embedding(query)
    
    print(f"\nQuery: '{query}'")
    print("\nSimilarity to sample texts:")
    
    similarities = []
    for i, text in enumerate(sample_texts):
        similarity = embeddings.calculate_similarity(query_embedding, embeddings_list[i])
        similarities.append((text, similarity))
        print(f"  {similarity:.3f} - {text}")
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    print(f"\nMost similar: {similarities[0][0]} ({similarities[0][1]:.3f})")
    
    # 6. Test domain-specific embeddings
    print("\n6. Domain-Specific Embeddings")
    print("-" * 60)
    
    pipeline_data = {
        "id": "PIPE-001",
        "type": "water_main",
        "material": "ductile_iron",
        "diameter_mm": 300,
        "length_m": 250,
        "status": "active",
        "region": "Downtown",
        "age_years": 15
    }
    
    customer_data = {
        "id": "CUST-001",
        "name": "John Doe",
        "type": "residential",
        "city": "San Francisco",
        "status": "active",
        "account_age_years": 5
    }
    
    print("\nGenerating pipeline embedding...")
    pipeline_emb = embeddings.embed_pipeline(pipeline_data)
    print(f"✓ Pipeline embedding: dimension {len(pipeline_emb)}")
    
    print("\nGenerating customer embedding...")
    customer_emb = embeddings.embed_customer(customer_data)
    print(f"✓ Customer embedding: dimension {len(customer_emb)}")
    
    # 7. Semantic search example
    print("\n7. Semantic Search Example")
    print("-" * 60)
    
    documents = [
        "Leak detected in downtown area affecting multiple customers",
        "Scheduled maintenance on water main pipeline",
        "Customer reported low water pressure",
        "Meter battery level below 20 percent",
        "Pipeline burst causing service interruption"
    ]
    
    search_query = "water pressure problem"
    
    print(f"\nDocuments: {len(documents)}")
    print(f"Search query: '{search_query}'")
    
    query_emb = embeddings.generate_embedding(search_query)
    doc_embeddings = embeddings.generate_batch_embeddings(documents)
    
    results = []
    for i, doc in enumerate(documents):
        similarity = embeddings.calculate_similarity(query_emb, doc_embeddings[i])
        results.append((doc, similarity))
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    print("\nSearch Results (ranked by relevance):")
    for i, (doc, score) in enumerate(results, 1):
        print(f"  {i}. [{score:.3f}] {doc}")
    
    # 8. Installation instructions
    print("\n8. Installation Instructions")
    print("-" * 60)
    
    if embeddings.model is None:
        print("\n⚠ HuggingFace model not loaded. Install dependencies:")
        install_instructions()
    else:
        print("\n✓ HuggingFace model loaded successfully!")
        print("\nTo use different models:")
        print("  embeddings = EmbeddingsGenerator('sentence-transformers', 'all-mpnet-base-v2')")
        print("\nTo use OpenAI (requires API key):")
        print("  embeddings = EmbeddingsGenerator('openai')")
    
    print("\n" + "=" * 60)
    print("✓ Embeddings demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
