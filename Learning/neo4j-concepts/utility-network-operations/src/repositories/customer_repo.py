"""Repository for customer operations."""

from typing import List, Dict, Any, Optional
from datetime import datetime

from ..connection import Neo4jConnection
from ..models.customer import Customer, CustomerType, CustomerStatus


class CustomerRepository:
    """Repository for managing customers and consumption data."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.conn = Neo4jConnection()
    
    def create_customer(self, customer: Customer) -> str:
        """Create a new customer."""
        query = """
        CREATE (c:Customer $props)
        RETURN c.id as id
        """
        result = self.conn.execute_query(query, props=customer.to_neo4j_properties())
        return result[0]['id'] if result else None
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        query = """
        MATCH (c:Customer {id: $customer_id})
        RETURN c
        """
        result = self.conn.execute_query(query, customer_id=customer_id)
        return dict(result[0]['c']) if result else None
    
    def update_customer(self, customer_id: str, updates: Dict[str, Any]) -> bool:
        """Update customer properties."""
        query = """
        MATCH (c:Customer {id: $customer_id})
        SET c += $updates
        RETURN c.id as id
        """
        result = self.conn.execute_query(query, customer_id=customer_id, updates=updates)
        return len(result) > 0
    
    def delete_customer(self, customer_id: str) -> bool:
        """Delete customer (soft delete by setting status to inactive)."""
        query = """
        MATCH (c:Customer {id: $customer_id})
        SET c.status = 'inactive'
        RETURN c.id as id
        """
        result = self.conn.execute_query(query, customer_id=customer_id)
        return len(result) > 0
    
    def get_customers_by_type(self, customer_type: str) -> List[Dict[str, Any]]:
        """Get customers by type."""
        query = """
        MATCH (c:Customer {type: $customer_type})
        WHERE c.status = 'active'
        RETURN c
        ORDER BY c.name
        """
        result = self.conn.execute_query(query, customer_type=customer_type)
        return [dict(r['c']) for r in result]
    
    def get_customers_by_region(self, city: str) -> List[Dict[str, Any]]:
        """Get customers in a city/region."""
        query = """
        MATCH (c:Customer {city: $city})
        WHERE c.status = 'active'
        RETURN c
        ORDER BY c.name
        """
        result = self.conn.execute_query(query, city=city)
        return [dict(r['c']) for r in result]
    
    def get_high_consumers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top consumers by average monthly consumption."""
        query = """
        MATCH (c:Customer)
        WHERE c.status = 'active' AND c.average_monthly_consumption > 0
        RETURN c, c.average_monthly_consumption as consumption
        ORDER BY consumption DESC
        LIMIT $limit
        """
        result = self.conn.execute_query(query, limit=limit)
        return [dict(r['c']) for r in result]
    
    def get_overdue_customers(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get customers with overdue payments."""
        query = """
        MATCH (c:Customer)
        WHERE c.current_balance > 0
          AND (c.last_payment_date IS NULL
           OR duration.between(date(c.last_payment_date), date()).days > $days)
        RETURN c,
               c.current_balance as balance,
               coalesce(c.last_payment_date, 'never') as last_payment
        ORDER BY balance DESC
        """
        result = self.conn.execute_query(query, days=days)
        return [dict(r['c']) for r in result]
    
    def get_vip_customers(self) -> List[Dict[str, Any]]:
        """Get VIP customers (high-value, long-term, good payment history)."""
        query = """
        MATCH (c:Customer)
        WHERE c.status = 'active'
          AND duration.between(date(c.account_created_date), date()).years >= 5
          AND c.average_monthly_consumption > 50
          AND (c.current_balance = 0
           OR (c.last_payment_date IS NOT NULL
               AND duration.between(date(c.last_payment_date), date()).days <= 30))
        RETURN c,
               duration.between(date(c.account_created_date), date()).years as account_years,
               c.average_monthly_consumption as consumption
        ORDER BY consumption DESC
        """
        result = self.conn.execute_query(query)
        return [dict(r['c']) for r in result]
    
    # Consumption tracking
    def record_consumption(
        self,
        customer_id: str,
        amount: float,
        resource_type: str = "water",
        date: Optional[datetime] = None
    ) -> bool:
        """Record consumption for a customer."""
        if date is None:
            date = datetime.now()
        
        query = """
        MATCH (c:Customer {id: $customer_id})
        MERGE (r:Resource {type: $resource_type})
        CREATE (c)-[con:CONSUMES {
            amount: $amount,
            date: $date,
            recorded_at: datetime()
        }]->(r)
        RETURN con
        """
        result = self.conn.execute_query(
            query,
            customer_id=customer_id,
            amount=amount,
            resource_type=resource_type,
            date=date.isoformat()
        )
        return len(result) > 0
    
    def get_customer_consumption_history(
        self,
        customer_id: str,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """Get consumption history for a customer."""
        query = """
        MATCH (c:Customer {id: $customer_id})-[con:CONSUMES]->(r:Resource)
        WHERE date(con.date) >= date() - duration({days: $days})
        RETURN r.type as resource_type,
               con.date as date,
               con.amount as amount
        ORDER BY date DESC
        """
        result = self.conn.execute_query(query, customer_id=customer_id, days=days)
        return result
    
    def calculate_customer_consumption_stats(self, customer_id: str) -> Dict[str, Any]:
        """Calculate consumption statistics for a customer."""
        query = """
        MATCH (c:Customer {id: $customer_id})-[con:CONSUMES]->(r:Resource)
        WHERE date(con.date) >= date() - duration({months: 12})
        WITH c, r.type as resource_type,
             sum(con.amount) as total,
             avg(con.amount) as average,
             max(con.amount) as maximum,
             min(con.amount) as minimum,
             count(con) as reading_count
        RETURN resource_type,
               round(total, 2) as total_consumption,
               round(average, 2) as avg_consumption,
               round(maximum, 2) as max_consumption,
               round(minimum, 2) as min_consumption,
               reading_count
        """
        result = self.conn.execute_query(query, customer_id=customer_id)
        return result[0] if result else {}
    
    def detect_consumption_anomalies(
        self,
        customer_id: str,
        threshold_multiplier: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalous consumption patterns."""
        query = """
        MATCH (c:Customer {id: $customer_id})-[con:CONSUMES]->(r:Resource)
        WHERE date(con.date) >= date() - duration({months: 6})
        WITH c, r,
             avg(con.amount) as avg_consumption,
             stdev(con.amount) as std_consumption
        MATCH (c)-[recent:CONSUMES]->(r)
        WHERE date(recent.date) >= date() - duration({days: 7})
          AND recent.amount > avg_consumption + ($threshold * std_consumption)
        RETURN recent.date as date,
               recent.amount as consumption,
               round(avg_consumption, 2) as average,
               round(recent.amount - avg_consumption, 2) as deviation
        ORDER BY deviation DESC
        """
        result = self.conn.execute_query(
            query,
            customer_id=customer_id,
            threshold=threshold_multiplier
        )
        return result
    
    # Meter relationships
    def get_customer_meters(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all meters for a customer."""
        query = """
        MATCH (m:Meter)-[:MEASURES]->(c:Customer {id: $customer_id})
        RETURN m
        ORDER BY m.type, m.id
        """
        result = self.conn.execute_query(query, customer_id=customer_id)
        return [dict(r['m']) for r in result]
    
    def get_customers_by_meter(self, meter_id: str) -> List[Dict[str, Any]]:
        """Get customers served by a meter (usually 1, but could be multiple for commercial)."""
        query = """
        MATCH (m:Meter {id: $meter_id})-[:MEASURES]->(c:Customer)
        RETURN c
        """
        result = self.conn.execute_query(query, meter_id=meter_id)
        return [dict(r['c']) for r in result]
    
    # Analytics
    def get_customer_statistics(self) -> Dict[str, Any]:
        """Get overall customer statistics."""
        query = """
        MATCH (c:Customer)
        WITH count(c) as total_customers,
             count(CASE WHEN c.status = 'active' THEN 1 END) as active_customers
        MATCH (c:Customer)
        WHERE c.status = 'active'
        WITH total_customers, active_customers,
             sum(c.current_balance) as total_outstanding,
             avg(c.average_monthly_consumption) as avg_consumption
        MATCH (c:Customer)
        WHERE c.status = 'active'
        WITH total_customers, active_customers, total_outstanding, avg_consumption,
             count(CASE WHEN c.type = 'residential' THEN 1 END) as residential,
             count(CASE WHEN c.type = 'commercial' THEN 1 END) as commercial,
             count(CASE WHEN c.type = 'industrial' THEN 1 END) as industrial,
             count(CASE WHEN c.type = 'municipal' THEN 1 END) as municipal
        RETURN total_customers,
               active_customers,
               round(total_outstanding, 2) as total_outstanding_balance,
               round(avg_consumption, 2) as avg_monthly_consumption,
               residential,
               commercial,
               industrial,
               municipal
        """
        result = self.conn.execute_query(query)
        return result[0] if result else {}
    
    def get_consumption_by_region(self) -> List[Dict[str, Any]]:
        """Get consumption aggregated by city/region."""
        query = """
        MATCH (c:Customer)
        WHERE c.city IS NOT NULL AND c.status = 'active'
        WITH c.city as city,
             count(c) as customer_count,
             sum(c.average_monthly_consumption) as total_consumption,
             avg(c.average_monthly_consumption) as avg_consumption
        RETURN city,
               customer_count,
               round(total_consumption, 2) as total_monthly_consumption,
               round(avg_consumption, 2) as avg_per_customer
        ORDER BY total_consumption DESC
        """
        result = self.conn.execute_query(query)
        return result
    
    def get_consumption_by_type(self) -> List[Dict[str, Any]]:
        """Get consumption aggregated by customer type."""
        query = """
        MATCH (c:Customer)
        WHERE c.status = 'active'
        WITH c.type as customer_type,
             count(c) as customer_count,
             sum(c.average_monthly_consumption) as total_consumption,
             avg(c.average_monthly_consumption) as avg_consumption,
             sum(c.current_balance) as total_balance
        RETURN customer_type,
               customer_count,
               round(total_consumption, 2) as total_monthly_consumption,
               round(avg_consumption, 2) as avg_per_customer,
               round(total_balance, 2) as total_outstanding
        ORDER BY total_consumption DESC
        """
        result = self.conn.execute_query(query)
        return result
