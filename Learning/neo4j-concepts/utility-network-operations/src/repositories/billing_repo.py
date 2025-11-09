"""Repository for billing operations."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from ..connection import Neo4jConnection


class BillingRepository:
    """Repository for managing billing and payment operations."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.conn = Neo4jConnection()
    
    def create_bill(
        self,
        bill_id: str,
        customer_id: str,
        amount: float,
        billing_period_start: datetime,
        billing_period_end: datetime,
        due_date: datetime,
        consumption: float = 0.0,
        resource_type: str = "water"
    ) -> str:
        """Create a new bill."""
        query = """
        MATCH (c:Customer {id: $customer_id})
        CREATE (b:Bill {
            id: $bill_id,
            customer_id: $customer_id,
            amount: $amount,
            consumption: $consumption,
            resource_type: $resource_type,
            billing_period_start: $period_start,
            billing_period_end: $period_end,
            due_date: $due_date,
            issue_date: $issue_date,
            status: 'unpaid',
            created_at: datetime()
        })
        CREATE (b)-[:BILLED_TO]->(c)
        RETURN b.id as id
        """
        result = self.conn.execute_query(
            query,
            bill_id=bill_id,
            customer_id=customer_id,
            amount=amount,
            consumption=consumption,
            resource_type=resource_type,
            period_start=billing_period_start.isoformat(),
            period_end=billing_period_end.isoformat(),
            due_date=due_date.isoformat(),
            issue_date=datetime.now().isoformat()
        )
        return result[0]['id'] if result else None
    
    def get_bill(self, bill_id: str) -> Optional[Dict[str, Any]]:
        """Get bill by ID."""
        query = """
        MATCH (b:Bill {id: $bill_id})
        RETURN b
        """
        result = self.conn.execute_query(query, bill_id=bill_id)
        return dict(result[0]['b']) if result else None
    
    def get_customer_bills(
        self,
        customer_id: str,
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """Get bills for a customer."""
        query = """
        MATCH (b:Bill)-[:BILLED_TO]->(c:Customer {id: $customer_id})
        RETURN b
        ORDER BY b.billing_period_end DESC
        LIMIT $limit
        """
        result = self.conn.execute_query(query, customer_id=customer_id, limit=limit)
        return [dict(r['b']) for r in result]
    
    def get_unpaid_bills(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all unpaid bills, optionally for a specific customer."""
        if customer_id:
            query = """
            MATCH (b:Bill {status: 'unpaid'})-[:BILLED_TO]->(c:Customer {id: $customer_id})
            RETURN b, c.name as customer_name
            ORDER BY b.due_date
            """
            result = self.conn.execute_query(query, customer_id=customer_id)
        else:
            query = """
            MATCH (b:Bill {status: 'unpaid'})-[:BILLED_TO]->(c:Customer)
            RETURN b, c.name as customer_name, c.id as customer_id
            ORDER BY b.due_date
            """
            result = self.conn.execute_query(query)
        
        return result
    
    def get_overdue_bills(self) -> List[Dict[str, Any]]:
        """Get all overdue bills."""
        query = """
        MATCH (b:Bill {status: 'unpaid'})-[:BILLED_TO]->(c:Customer)
        WHERE date(b.due_date) < date()
        WITH b, c, duration.between(date(b.due_date), date()).days as days_overdue
        RETURN b,
               c.id as customer_id,
               c.name as customer_name,
               days_overdue
        ORDER BY days_overdue DESC, b.amount DESC
        """
        result = self.conn.execute_query(query)
        return result
    
    def record_payment(
        self,
        bill_id: str,
        amount_paid: float,
        payment_date: Optional[datetime] = None,
        payment_method: str = "online"
    ) -> bool:
        """Record a payment for a bill."""
        if payment_date is None:
            payment_date = datetime.now()
        
        query = """
        MATCH (b:Bill {id: $bill_id})-[:BILLED_TO]->(c:Customer)
        SET b.status = CASE
            WHEN $amount_paid >= b.amount THEN 'paid'
            ELSE 'partial'
        END,
        b.amount_paid = coalesce(b.amount_paid, 0.0) + $amount_paid,
        b.payment_date = CASE
            WHEN b.payment_date IS NULL THEN $payment_date
            ELSE b.payment_date
        END,
        b.last_payment_date = $payment_date,
        b.payment_method = $payment_method
        
        WITH b, c, (b.amount - coalesce(b.amount_paid, 0.0)) as remaining
        SET c.current_balance = c.current_balance - $amount_paid,
            c.last_payment_date = $payment_date
        
        RETURN b.id as bill_id, b.status as status, remaining
        """
        result = self.conn.execute_query(
            query,
            bill_id=bill_id,
            amount_paid=amount_paid,
            payment_date=payment_date.isoformat(),
            payment_method=payment_method
        )
        return len(result) > 0
    
    def generate_monthly_bills(
        self,
        year: int,
        month: int,
        base_rate: float = 0.05,
        tier_rates: Optional[Dict[str, float]] = None
    ) -> int:
        """
        Generate bills for all customers for a given month.
        Returns number of bills created.
        """
        if tier_rates is None:
            tier_rates = {
                'residential': 0.05,
                'commercial': 0.08,
                'industrial': 0.06,
                'municipal': 0.04
            }
        
        # Get period dates
        period_start = datetime(year, month, 1)
        if month == 12:
            period_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        due_date = period_end + timedelta(days=30)
        
        # This would typically be done in a batch process
        # Here's a simplified version
        query = """
        MATCH (c:Customer {status: 'active'})
        WHERE c.average_monthly_consumption > 0
        WITH c,
             c.average_monthly_consumption as consumption,
             CASE c.type
                WHEN 'residential' THEN $rate_residential
                WHEN 'commercial' THEN $rate_commercial
                WHEN 'industrial' THEN $rate_industrial
                WHEN 'municipal' THEN $rate_municipal
                ELSE $base_rate
             END as rate
        
        CREATE (b:Bill {
            id: 'BILL-' + c.id + '-' + $period,
            customer_id: c.id,
            amount: round(consumption * rate, 2),
            consumption: consumption,
            resource_type: 'water',
            billing_period_start: $period_start,
            billing_period_end: $period_end,
            due_date: $due_date,
            issue_date: $issue_date,
            status: 'unpaid',
            created_at: datetime()
        })
        CREATE (b)-[:BILLED_TO]->(c)
        
        SET c.current_balance = c.current_balance + b.amount
        
        RETURN count(b) as bills_created
        """
        
        result = self.conn.execute_query(
            query,
            period=f"{year}-{month:02d}",
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            due_date=due_date.isoformat(),
            issue_date=datetime.now().isoformat(),
            base_rate=base_rate,
            rate_residential=tier_rates.get('residential', base_rate),
            rate_commercial=tier_rates.get('commercial', base_rate),
            rate_industrial=tier_rates.get('industrial', base_rate),
            rate_municipal=tier_rates.get('municipal', base_rate)
        )
        
        return result[0]['bills_created'] if result else 0
    
    def calculate_bill_amount(
        self,
        consumption: float,
        customer_type: str,
        base_rate: float = 0.05,
        tier_rates: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculate bill amount based on consumption and customer type."""
        if tier_rates is None:
            tier_rates = {
                'residential': 0.05,
                'commercial': 0.08,
                'industrial': 0.06,
                'municipal': 0.04
            }
        
        rate = tier_rates.get(customer_type, base_rate)
        
        # Apply tiered pricing for residential
        if customer_type == 'residential':
            if consumption <= 20:
                amount = consumption * rate
            elif consumption <= 50:
                amount = 20 * rate + (consumption - 20) * rate * 1.2
            else:
                amount = 20 * rate + 30 * rate * 1.2 + (consumption - 50) * rate * 1.5
        else:
            amount = consumption * rate
        
        return round(amount, 2)
    
    # Analytics
    def get_billing_statistics(self) -> Dict[str, Any]:
        """Get overall billing statistics."""
        query = """
        MATCH (b:Bill)
        WITH count(b) as total_bills,
             sum(b.amount) as total_billed,
             sum(CASE WHEN b.status = 'paid' THEN b.amount ELSE 0 END) as total_paid,
             sum(CASE WHEN b.status = 'unpaid' THEN b.amount ELSE 0 END) as total_outstanding
        MATCH (b:Bill {status: 'unpaid'})
        WHERE date(b.due_date) < date()
        WITH total_bills, total_billed, total_paid, total_outstanding,
             count(b) as overdue_count,
             sum(b.amount) as overdue_amount
        RETURN total_bills,
               round(total_billed, 2) as total_billed,
               round(total_paid, 2) as total_paid,
               round(total_outstanding, 2) as total_outstanding,
               overdue_count,
               round(overdue_amount, 2) as overdue_amount,
               round((total_paid * 100.0 / total_billed), 1) as collection_rate_percent
        """
        result = self.conn.execute_query(query)
        return result[0] if result else {}
    
    def get_revenue_by_period(self, months: int = 12) -> List[Dict[str, Any]]:
        """Get revenue aggregated by billing period."""
        query = """
        MATCH (b:Bill)
        WHERE date(b.billing_period_end) >= date() - duration({months: $months})
        WITH date.truncate('month', date(b.billing_period_end)) as month,
             sum(b.amount) as total_billed,
             sum(CASE WHEN b.status = 'paid' THEN b.amount ELSE 0 END) as total_paid,
             count(b) as bill_count
        RETURN toString(month) as period,
               round(total_billed, 2) as billed,
               round(total_paid, 2) as paid,
               bill_count
        ORDER BY period DESC
        """
        result = self.conn.execute_query(query, months=months)
        return result
    
    def get_payment_methods_summary(self) -> List[Dict[str, Any]]:
        """Get summary of payment methods used."""
        query = """
        MATCH (b:Bill)
        WHERE b.payment_method IS NOT NULL
        WITH b.payment_method as method,
             count(b) as transaction_count,
             sum(b.amount_paid) as total_amount
        RETURN method,
               transaction_count,
               round(total_amount, 2) as total_amount
        ORDER BY total_amount DESC
        """
        result = self.conn.execute_query(query)
        return result
