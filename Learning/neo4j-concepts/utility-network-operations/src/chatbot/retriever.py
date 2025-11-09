"""Retriever module for fetching relevant context from utility network database."""

from typing import List, Dict, Any, Optional
from src.connection import Neo4jConnection
from src.chatbot.embeddings import EmbeddingsGenerator, create_embeddings_generator


class UtilityNetworkRetriever:
    """Retrieve relevant information from utility network for RAG chatbot."""
    
    def __init__(self, connection: Neo4jConnection, use_case: str = "qa"):
        """
        Initialize retriever.
        
        Args:
            connection: Neo4j database connection
            use_case: Embedding model use case ('qa', 'general', 'best_quality')
        """
        self.conn = connection
        # Use recommended embeddings for question-answering
        self.embeddings = create_embeddings_generator(use_case)
    
    def retrieve_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive customer information.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer information dictionary
        """
        query = """
        MATCH (c:Customer {id: $customer_id})
        OPTIONAL MATCH (c)-[:HAS_METER]->(m:Meter)
        OPTIONAL MATCH (c)-[cons:CONSUMES]->()
        OPTIONAL MATCH (c)-[:HAS_BILL]->(b:Bill)
        OPTIONAL MATCH (c)<-[:REPORTED_BY]-(sr:ServiceRequest)
        
        WITH c, 
             collect(DISTINCT m {.*}) as meters,
             sum(cons.consumption_liters) as total_consumption,
             collect(DISTINCT b {.*}) as bills,
             collect(DISTINCT sr {.*}) as service_requests
        
        RETURN c {
            .*,
            meters: meters,
            total_consumption: total_consumption,
            bills: bills,
            service_requests: service_requests
        } as customer_data
        """
        
        result = self.conn.execute_query(query, {"customer_id": customer_id})
        return result[0]["customer_data"] if result else {}
    
    def retrieve_pipeline_info(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Retrieve pipeline information.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Pipeline information dictionary
        """
        query = """
        MATCH (p:PipelineSegment {id: $pipeline_id})
        OPTIONAL MATCH (p)-[:CONNECTS_TO]-(connected:PipelineSegment)
        OPTIONAL MATCH (p)<-[:MONITORS]-(m:Meter)
        OPTIONAL MATCH (p)<-[:AFFECTS]-(i:Incident)
        
        RETURN p {
            .*,
            connected_pipelines: collect(DISTINCT connected.id),
            meters: collect(DISTINCT m.id),
            incidents: collect(DISTINCT i {.id, .type, .severity, .status})
        } as pipeline_data
        """
        
        result = self.conn.execute_query(query, {"pipeline_id": pipeline_id})
        return result[0]["pipeline_data"] if result else {}
    
    def retrieve_incident_info(self, incident_id: str) -> Dict[str, Any]:
        """
        Retrieve incident information.
        
        Args:
            incident_id: Incident ID
            
        Returns:
            Incident information dictionary
        """
        query = """
        MATCH (i:Incident {id: $incident_id})
        OPTIONAL MATCH (i)-[:AFFECTS]->(p:PipelineSegment)
        OPTIONAL MATCH (i)-[:AFFECTS]->(c:Customer)
        
        RETURN i {
            .*,
            affected_pipelines: collect(DISTINCT p.id),
            affected_customers: collect(DISTINCT c.id)
        } as incident_data
        """
        
        result = self.conn.execute_query(query, {"incident_id": incident_id})
        return result[0]["incident_data"] if result else {}
    
    def search_similar_incidents(self, description: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar past incidents using semantic search.
        
        Args:
            description: Incident description
            limit: Maximum number of results
            
        Returns:
            List of similar incidents
        """
        # Generate embedding for query
        query_embedding = self.embeddings.generate_embedding(description)
        
        # Get all incidents
        query = """
        MATCH (i:Incident)
        WHERE i.status IN ['resolved', 'closed']
        RETURN i {.*} as incident
        ORDER BY i.reported_date DESC
        LIMIT 100
        """
        
        incidents = self.conn.execute_query(query)
        
        # Calculate similarity scores
        scored_incidents = []
        for record in incidents:
            incident = record["incident"]
            incident_text = f"{incident.get('type', '')} {incident.get('description', '')}"
            incident_embedding = self.embeddings.generate_embedding(incident_text)
            
            similarity = self.embeddings.calculate_similarity(query_embedding, incident_embedding)
            
            scored_incidents.append({
                "incident": incident,
                "similarity": similarity
            })
        
        # Sort by similarity and return top results
        scored_incidents.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_incidents[:limit]
    
    def retrieve_consumption_summary(self, customer_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Retrieve customer consumption summary.
        
        Args:
            customer_id: Customer ID
            days: Number of days to analyze
            
        Returns:
            Consumption summary
        """
        query = """
        MATCH (c:Customer {id: $customer_id})-[cons:CONSUMES]->()
        WHERE cons.consumption_date > datetime() - duration({days: $days})
        
        WITH c,
             count(cons) as reading_count,
             sum(cons.consumption_liters) as total,
             avg(cons.consumption_liters) as average,
             min(cons.consumption_liters) as minimum,
             max(cons.consumption_liters) as maximum
        
        RETURN {
            customer_id: c.id,
            period_days: $days,
            reading_count: reading_count,
            total_consumption: total,
            average_daily: average,
            min_daily: minimum,
            max_daily: maximum
        } as summary
        """
        
        result = self.conn.execute_query(query, {
            "customer_id": customer_id,
            "days": days
        })
        
        return result[0]["summary"] if result else {}
    
    def retrieve_billing_summary(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer billing summary.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Billing summary
        """
        query = """
        MATCH (c:Customer {id: $customer_id})-[:HAS_BILL]->(b:Bill)
        
        WITH c,
             count(b) as total_bills,
             sum(CASE WHEN b.status = 'paid' THEN b.amount_due ELSE 0 END) as total_paid,
             sum(CASE WHEN b.status = 'unpaid' THEN b.amount_due ELSE 0 END) as total_unpaid,
             sum(CASE WHEN b.status = 'overdue' THEN b.amount_due ELSE 0 END) as total_overdue
        
        RETURN {
            customer_id: c.id,
            total_bills: total_bills,
            total_paid: total_paid,
            total_unpaid: total_unpaid,
            total_overdue: total_overdue,
            account_balance: total_unpaid + total_overdue
        } as summary
        """
        
        result = self.conn.execute_query(query, {"customer_id": customer_id})
        return result[0]["summary"] if result else {}
    
    def retrieve_service_requests(self, customer_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve customer service requests.
        
        Args:
            customer_id: Customer ID
            status: Filter by status (optional)
            
        Returns:
            List of service requests
        """
        query = """
        MATCH (c:Customer {id: $customer_id})<-[:REPORTED_BY]-(sr:ServiceRequest)
        WHERE $status IS NULL OR sr.status = $status
        RETURN sr {.*} as request
        ORDER BY sr.created_date DESC
        """
        
        result = self.conn.execute_query(query, {
            "customer_id": customer_id,
            "status": status
        })
        
        return [record["request"] for record in result]
    
    def retrieve_network_status(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve network status information.
        
        Args:
            region: Filter by region (optional)
            
        Returns:
            Network status summary
        """
        query = """
        MATCH (p:PipelineSegment)
        WHERE $region IS NULL OR p.region = $region
        
        WITH count(p) as total_pipelines,
             sum(CASE WHEN p.status = 'active' THEN 1 ELSE 0 END) as active,
             sum(CASE WHEN p.status = 'maintenance' THEN 1 ELSE 0 END) as maintenance,
             avg(p.current_pressure_psi) as avg_pressure
        
        MATCH (i:Incident)
        WHERE i.status IN ['open', 'in_progress']
        AND ($region IS NULL OR i.region = $region)
        
        WITH total_pipelines, active, maintenance, avg_pressure,
             count(i) as active_incidents
        
        RETURN {
            region: $region,
            total_pipelines: total_pipelines,
            active_pipelines: active,
            maintenance_pipelines: maintenance,
            average_pressure: avg_pressure,
            active_incidents: active_incidents
        } as status
        """
        
        result = self.conn.execute_query(query, {"region": region})
        return result[0]["status"] if result else {}
    
    def retrieve_context_for_query(self, query: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve relevant context for a natural language query.
        
        Args:
            query: Natural language query
            customer_id: Customer ID for personalized context
            
        Returns:
            Relevant context dictionary
        """
        context = {}
        
        query_lower = query.lower()
        
        # Retrieve customer info if relevant
        if customer_id and any(word in query_lower for word in ['my', 'account', 'bill', 'usage', 'consumption']):
            context['customer'] = self.retrieve_customer_info(customer_id)
            context['consumption'] = self.retrieve_consumption_summary(customer_id)
            context['billing'] = self.retrieve_billing_summary(customer_id)
        
        # Retrieve service requests if relevant
        if customer_id and any(word in query_lower for word in ['request', 'service', 'issue', 'problem']):
            context['service_requests'] = self.retrieve_service_requests(customer_id)
        
        # Retrieve network status if relevant
        if any(word in query_lower for word in ['network', 'pipeline', 'pressure', 'outage', 'incident']):
            context['network_status'] = self.retrieve_network_status()
        
        # Search similar incidents if relevant
        if any(word in query_lower for word in ['incident', 'leak', 'burst', 'problem', 'issue']):
            context['similar_incidents'] = self.search_similar_incidents(query)
        
        return context
