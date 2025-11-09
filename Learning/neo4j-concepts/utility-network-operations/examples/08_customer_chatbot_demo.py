"""Customer chatbot demonstration."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.chatbot.chatbot import UtilityNetworkChatbot
from src.chatbot.prompts import get_sample_prompts


def main():
    """Demonstrate RAG chatbot capabilities."""
    
    print("=" * 60)
    print("Utility Network Operations - Customer Chatbot Demo")
    print("=" * 60)
    
    conn = Neo4jConnection()
    chatbot = UtilityNetworkChatbot(conn)
    
    # Get sample customer
    customers = conn.execute_query("MATCH (c:Customer) RETURN c.id as id LIMIT 1")
    if not customers:
        print("✗ No customers found")
        return
    
    customer_id = customers[0]['id']
    
    print(f"\nCustomer ID: {customer_id}")
    print("\nDemonstrating various query types...")
    
    # 1. Billing Query
    print("\n" + "="*60)
    print("1. BILLING QUERY")
    print("="*60)
    query = "What is my current account balance?"
    print(f"User: {query}")
    
    response = chatbot.chat(query, customer_id)
    print(f"\nChatbot: {response['response']}")
    print(f"\nSources: {', '.join(response['sources'])}")
    
    # 2. Consumption Query
    print("\n" + "="*60)
    print("2. CONSUMPTION QUERY")
    print("="*60)
    query = "How much water am I using?"
    print(f"User: {query}")
    
    response = chatbot.chat(query, customer_id)
    print(f"\nChatbot: {response['response']}")
    print(f"\nSources: {', '.join(response['sources'])}")
    
    # 3. Service Request Query
    print("\n" + "="*60)
    print("3. SERVICE REQUEST QUERY")
    print("="*60)
    query = "I want to report a water leak at my property"
    print(f"User: {query}")
    
    response = chatbot.chat(query, customer_id)
    print(f"\nChatbot: {response['response']}")
    print(f"\nSources: {', '.join(response['sources'])}")
    
    # 4. Network Status Query
    print("\n" + "="*60)
    print("4. NETWORK STATUS QUERY")
    print("="*60)
    query = "Are there any outages in my area?"
    print(f"User: {query}")
    
    response = chatbot.chat(query, customer_id)
    print(f"\nChatbot: {response['response']}")
    print(f"\nSources: {', '.join(response['sources'])}")
    
    # 5. General Help Query
    print("\n" + "="*60)
    print("5. GENERAL HELP QUERY")
    print("="*60)
    query = "What can you help me with?"
    print(f"User: {query}")
    
    response = chatbot.chat(query, customer_id)
    print(f"\nChatbot: {response['response']}")
    print(f"\nSources: {', '.join(response['sources'])}")
    
    # 6. Show conversation history
    print("\n" + "="*60)
    print("6. CONVERSATION HISTORY")
    print("="*60)
    
    history = chatbot.get_conversation_history()
    print(f"Total messages: {len(history)}")
    
    # 7. Common questions
    print("\n" + "="*60)
    print("7. COMMON QUESTIONS HANDLER")
    print("="*60)
    
    common_questions = ["balance", "usage", "outage"]
    
    for q_type in common_questions:
        response = chatbot.handle_common_question(q_type, customer_id)
        print(f"\n{q_type.upper()}: {response['response'][:100]}...")
    
    # 8. Sample prompts
    print("\n" + "="*60)
    print("8. SAMPLE PROMPTS BY CATEGORY")
    print("="*60)
    
    categories = ["billing", "consumption", "service_requests", "network", "general"]
    
    for category in categories:
        prompts = get_sample_prompts(category)
        print(f"\n{category.upper()}:")
        for i, prompt in enumerate(prompts[:3], 1):
            print(f"  {i}. {prompt}")
    
    # 9. Interactive mode demonstration
    print("\n" + "="*60)
    print("9. CHATBOT CAPABILITIES SUMMARY")
    print("="*60)
    
    print("\nThe chatbot can handle:")
    print("✓ Billing and payment inquiries")
    print("✓ Water/gas consumption questions")
    print("✓ Service request creation and tracking")
    print("✓ Network status and outage information")
    print("✓ General account management")
    
    print("\nRAG Features:")
    print("✓ Retrieves relevant context from Neo4j database")
    print("✓ Semantic search for similar incidents")
    print("✓ Personalized responses based on customer data")
    print("✓ Multi-source information integration")
    print("✓ Conversation history tracking")
    
    print("\nIntegration Ready For:")
    print("- OpenAI GPT-4")
    print("- Anthropic Claude")
    print("- Local LLMs (Llama, etc.)")
    print("- Custom fine-tuned models")
    
    print("\n" + "="*60)
    print("✓ Customer chatbot demonstration completed!")
    print("="*60)


def interactive_mode():
    """Run chatbot in interactive mode."""
    
    print("\n" + "="*60)
    print("INTERACTIVE CHATBOT MODE")
    print("="*60)
    print("\nType 'exit' to quit, 'history' to see conversation")
    
    conn = Neo4jConnection()
    chatbot = UtilityNetworkChatbot(conn)
    
    # Get customer ID
    customers = conn.execute_query("MATCH (c:Customer) RETURN c.id as id LIMIT 1")
    customer_id = customers[0]['id'] if customers else None
    
    if customer_id:
        print(f"Logged in as: {customer_id}")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'history':
            history = chatbot.get_conversation_history()
            print("\nConversation History:")
            for msg in history:
                print(f"  {msg['role']}: {msg['content'][:80]}...")
            continue
        
        if not user_input:
            continue
        
        response = chatbot.chat(user_input, customer_id)
        print(f"\nChatbot: {response['response']}")


if __name__ == "__main__":
    try:
        # Run demonstration
        main()
        
        # Optionally run interactive mode
        # Uncomment to enable:
        # interactive_mode()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
