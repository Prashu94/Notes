"""Prompts for utility network chatbot."""

from typing import Dict, Any


SYSTEM_PROMPT = """You are a helpful AI assistant for a utility network operations system. 
You have access to information about:
- Water and gas pipeline networks
- Customer accounts and consumption data
- Billing information
- Service requests and incidents
- Network monitoring and maintenance

Your role is to:
1. Answer customer questions accurately and professionally
2. Provide relevant information from the utility network database
3. Help customers understand their usage, bills, and service requests
4. Alert customers to any relevant incidents or service disruptions
5. Guide customers on how to report issues or request services

Always be:
- Professional and courteous
- Clear and concise
- Accurate with data
- Helpful and proactive
- Security-conscious (never share sensitive data of other customers)
"""


def create_rag_prompt(query: str, context: Dict[str, Any]) -> str:
    """
    Create RAG prompt with query and retrieved context.
    
    Args:
        query: User's question
        context: Retrieved context from database
        
    Returns:
        Formatted prompt with context
    """
    prompt_parts = [SYSTEM_PROMPT]
    
    prompt_parts.append("\n\n### RELEVANT CONTEXT ###\n")
    
    # Add customer context
    if 'customer' in context and context['customer']:
        customer = context['customer']
        prompt_parts.append(f"\n**Customer Information:**")
        prompt_parts.append(f"- ID: {customer.get('id')}")
        prompt_parts.append(f"- Name: {customer.get('name')}")
        prompt_parts.append(f"- Type: {customer.get('type')}")
        prompt_parts.append(f"- Status: {customer.get('status')}")
        prompt_parts.append(f"- City: {customer.get('city')}")
        
        if customer.get('meters'):
            prompt_parts.append(f"- Active Meters: {len(customer['meters'])}")
    
    # Add consumption context
    if 'consumption' in context and context['consumption']:
        cons = context['consumption']
        prompt_parts.append(f"\n**Consumption Summary (last {cons.get('period_days')} days):**")
        prompt_parts.append(f"- Total: {cons.get('total_consumption', 0):,.0f} liters")
        prompt_parts.append(f"- Average Daily: {cons.get('average_daily', 0):.2f} liters")
        prompt_parts.append(f"- Min/Max: {cons.get('min_daily', 0):.0f}/{cons.get('max_daily', 0):.0f} liters")
    
    # Add billing context
    if 'billing' in context and context['billing']:
        billing = context['billing']
        prompt_parts.append(f"\n**Billing Summary:**")
        prompt_parts.append(f"- Total Bills: {billing.get('total_bills', 0)}")
        prompt_parts.append(f"- Paid: ${billing.get('total_paid', 0):.2f}")
        prompt_parts.append(f"- Unpaid: ${billing.get('total_unpaid', 0):.2f}")
        prompt_parts.append(f"- Overdue: ${billing.get('total_overdue', 0):.2f}")
        prompt_parts.append(f"- Account Balance: ${billing.get('account_balance', 0):.2f}")
    
    # Add service requests context
    if 'service_requests' in context and context['service_requests']:
        requests = context['service_requests']
        prompt_parts.append(f"\n**Service Requests ({len(requests)} total):**")
        for req in requests[:3]:
            prompt_parts.append(f"- {req.get('id')}: {req.get('type')} - {req.get('status')}")
    
    # Add network status context
    if 'network_status' in context and context['network_status']:
        status = context['network_status']
        prompt_parts.append(f"\n**Network Status:**")
        prompt_parts.append(f"- Total Pipelines: {status.get('total_pipelines', 0)}")
        prompt_parts.append(f"- Active: {status.get('active_pipelines', 0)}")
        prompt_parts.append(f"- Average Pressure: {status.get('average_pressure', 0):.2f} PSI")
        prompt_parts.append(f"- Active Incidents: {status.get('active_incidents', 0)}")
    
    # Add similar incidents context
    if 'similar_incidents' in context and context['similar_incidents']:
        incidents = context['similar_incidents']
        prompt_parts.append(f"\n**Similar Past Incidents:**")
        for item in incidents[:3]:
            incident = item['incident']
            similarity = item['similarity']
            prompt_parts.append(f"- {incident.get('type')} (Similarity: {similarity:.0%})")
            prompt_parts.append(f"  Status: {incident.get('status')}, Resolution: {incident.get('resolution_date')}")
    
    prompt_parts.append("\n\n### USER QUESTION ###\n")
    prompt_parts.append(query)
    
    prompt_parts.append("\n\n### INSTRUCTIONS ###")
    prompt_parts.append("Based on the context provided above, answer the user's question accurately and professionally.")
    prompt_parts.append("If the context doesn't contain enough information, acknowledge that and provide general guidance.")
    prompt_parts.append("Always prioritize customer satisfaction and security.")
    
    return "\n".join(prompt_parts)


SAMPLE_PROMPTS = {
    "billing": [
        "What is my current account balance?",
        "When is my next bill due?",
        "How much did I use last month?",
        "Why is my bill higher than usual?",
        "Can I see my payment history?"
    ],
    
    "consumption": [
        "How much water am I using?",
        "Is my usage higher than normal?",
        "How does my usage compare to similar customers?",
        "What are my peak usage hours?",
        "Can you show me my consumption trends?"
    ],
    
    "service_requests": [
        "I want to report a leak",
        "What's the status of my service request?",
        "How long until my issue is resolved?",
        "I need to schedule a meter reading",
        "Can I cancel my service request?"
    ],
    
    "network": [
        "Are there any outages in my area?",
        "What's the current water pressure?",
        "Is there scheduled maintenance nearby?",
        "Why is my water pressure low?",
        "Are there any incidents affecting my service?"
    ],
    
    "general": [
        "How do I pay my bill?",
        "What payment methods are accepted?",
        "How can I reduce my water usage?",
        "What should I do if I smell gas?",
        "How do I update my account information?"
    ]
}


def get_sample_prompts(category: str = None) -> list:
    """
    Get sample prompts for testing or demonstration.
    
    Args:
        category: Prompt category (billing, consumption, service_requests, network, general)
        
    Returns:
        List of sample prompts
    """
    if category and category in SAMPLE_PROMPTS:
        return SAMPLE_PROMPTS[category]
    
    # Return all prompts
    all_prompts = []
    for prompts in SAMPLE_PROMPTS.values():
        all_prompts.extend(prompts)
    return all_prompts
