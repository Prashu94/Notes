"""Anomaly detection algorithms for consumption and network behavior."""

from typing import List, Dict, Any, Optional
from statistics import mean, stdev
from datetime import datetime, timedelta

from ..connection import Neo4jConnection


class AnomalyDetection:
    """Algorithms for detecting anomalous patterns in consumption and network behavior."""
    
    def __init__(self):
        """Initialize with database connection."""
        self.conn = Neo4jConnection()
    
    def detect_consumption_anomalies(
        self,
        threshold_std_dev: float = 2.0,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Detect customers with anomalous consumption using statistical methods.
        Uses Z-score approach: anomaly if deviation > threshold * std_dev.
        """
        query = """
        MATCH (c:Customer)-[con:CONSUMES]->(r:Resource)
        WHERE date(con.date) >= date() - duration({days: $days})
        
        WITH c, r,
             collect(con.amount) as amounts,
             avg(con.amount) as avg_consumption,
             stdev(con.amount) as std_consumption,
             count(con) as reading_count
        WHERE reading_count >= 10 AND std_consumption IS NOT NULL
        
        // Find recent readings that exceed threshold
        MATCH (c)-[recent:CONSUMES]->(r)
        WHERE date(recent.date) >= date() - duration({days: 7})
          AND recent.amount > avg_consumption + ($threshold * std_consumption)
        
        WITH c, r, avg_consumption, std_consumption,
             recent.amount as anomalous_amount,
             recent.date as anomaly_date,
             (recent.amount - avg_consumption) / std_consumption as z_score
        
        RETURN c.id as customer_id,
               c.name as customer_name,
               c.type as customer_type,
               r.type as resource_type,
               round(avg_consumption, 2) as normal_avg,
               round(std_consumption, 2) as std_dev,
               round(anomalous_amount, 2) as anomalous_consumption,
               anomaly_date,
               round(z_score, 2) as z_score,
               round((anomalous_amount - avg_consumption) / avg_consumption * 100, 1) as percent_deviation
        ORDER BY z_score DESC
        LIMIT 50
        """
        
        result = self.conn.execute_query(
            query,
            days=days,
            threshold=threshold_std_dev
        )
        
        return result
    
    def detect_pressure_anomalies(
        self,
        window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Detect sudden pressure changes that may indicate problems.
        """
        # In a real system, this would analyze time-series pressure data
        # Simplified version using current vs expected pressure
        
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.current_pressure_bar IS NOT NULL
          AND p.max_pressure_bar IS NOT NULL
        
        WITH p,
             abs(p.current_pressure_bar - p.max_pressure_bar * 0.85) / (p.max_pressure_bar * 0.85) as deviation_ratio
        WHERE deviation_ratio > 0.20  // 20% deviation from expected
        
        RETURN p.id as pipeline_id,
               p.location as location,
               p.region as region,
               p.current_pressure_bar as current_pressure,
               p.max_pressure_bar * 0.85 as expected_pressure,
               round(deviation_ratio * 100, 1) as deviation_percent,
               CASE
                 WHEN p.current_pressure_bar < p.max_pressure_bar * 0.65 THEN 'critical_low'
                 WHEN p.current_pressure_bar < p.max_pressure_bar * 0.75 THEN 'low'
                 WHEN p.current_pressure_bar > p.max_pressure_bar * 0.95 THEN 'high'
                 ELSE 'moderate'
               END as anomaly_type
        ORDER BY deviation_ratio DESC
        LIMIT 30
        """
        
        result = self.conn.execute_query(query)
        
        return result
    
    def detect_meter_anomalies(self) -> Dict[str, Any]:
        """
        Detect anomalous meter behavior:
        - Stopped reporting
        - Unusual reading patterns
        - Sudden spikes
        """
        # Meters not reporting
        stale_query = """
        MATCH (m:Meter)
        WHERE m.last_reading_date IS NOT NULL
          AND duration.between(datetime(m.last_reading_date), datetime()).hours > 48
        RETURN m.id as meter_id,
               m.location as location,
               duration.between(datetime(m.last_reading_date), datetime()).hours as hours_since_last_reading
        ORDER BY hours_since_last_reading DESC
        LIMIT 20
        """
        
        stale_meters = self.conn.execute_query(stale_query)
        
        # Low battery meters
        battery_query = """
        MATCH (m:Meter)
        WHERE m.battery_level IS NOT NULL
          AND m.battery_level < 15
        RETURN m.id as meter_id,
               m.location as location,
               m.battery_level as battery_level
        ORDER BY battery_level ASC
        LIMIT 20
        """
        
        low_battery = self.conn.execute_query(battery_query)
        
        return {
            'stale_meters': {
                'count': len(stale_meters),
                'details': stale_meters
            },
            'low_battery_meters': {
                'count': len(low_battery),
                'details': low_battery
            }
        }
    
    def detect_seasonal_anomalies(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Detect consumption that doesn't match seasonal patterns.
        E.g., high water usage in winter could indicate leak.
        """
        query = """
        MATCH (c:Customer {id: $customer_id})-[con:CONSUMES]->(r:Resource)
        WHERE date(con.date) >= date() - duration({months: 12})
        
        WITH c, r,
             date.truncate('month', date(con.date)) as month,
             avg(con.amount) as monthly_avg
        
        WITH c, r,
             collect({month: toString(month), avg: monthly_avg}) as monthly_data,
             avg(monthly_avg) as overall_avg,
             stdev(monthly_avg) as std_dev
        
        UNWIND monthly_data as data
        WITH c, r, data, overall_avg, std_dev,
             abs(data.avg - overall_avg) / std_dev as z_score
        WHERE z_score > 1.5
        
        RETURN data.month as anomalous_month,
               round(data.avg, 2) as monthly_consumption,
               round(overall_avg, 2) as expected_avg,
               round(z_score, 2) as z_score,
               round((data.avg - overall_avg) / overall_avg * 100, 1) as percent_deviation
        ORDER BY z_score DESC
        """
        
        result = self.conn.execute_query(query, customer_id=customer_id)
        
        return {
            'customer_id': customer_id,
            'seasonal_anomalies': result,
            'anomaly_count': len(result)
        }
    
    def detect_network_topology_changes(
        self,
        baseline_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect unexpected changes in network topology.
        Useful for identifying unauthorized connections or equipment failures.
        """
        # This would typically compare current topology to a stored baseline
        # Simplified version: detect unusual connectivity patterns
        
        query = """
        MATCH (p:PipelineSegment)
        OPTIONAL MATCH (p)-[r:CONNECTS_TO]-()
        WITH p, count(r) as connection_count
        
        // Find nodes with unusual connection counts
        WHERE connection_count = 0 OR connection_count > 6
        
        RETURN p.id as pipeline_id,
               p.location as location,
               p.status as status,
               connection_count,
               CASE
                 WHEN connection_count = 0 THEN 'isolated'
                 WHEN connection_count > 6 THEN 'highly_connected'
               END as anomaly_type
        ORDER BY connection_count DESC
        """
        
        result = self.conn.execute_query(query)
        
        return {
            'topology_anomalies': result,
            'count': len(result),
            'recommendation': 'Review isolated and highly-connected nodes for errors'
        }
    
    def detect_correlated_anomalies(
        self,
        region: str,
        time_window_hours: int = 6
    ) -> Dict[str, Any]:
        """
        Detect multiple simultaneous anomalies in same region.
        Could indicate systemic issue or major incident.
        """
        # Find recent pressure anomalies
        pressure_query = """
        MATCH (p:PipelineSegment {region: $region})
        WHERE p.current_pressure_bar < p.max_pressure_bar * 0.7
        RETURN p.id as pipeline_id,
               p.location as location,
               'low_pressure' as anomaly_type
        """
        
        pressure_anomalies = self.conn.execute_query(query=pressure_query, region=region)
        
        # Find recent consumption spikes in region
        consumption_query = """
        MATCH (c:Customer {city: $region})-[con:CONSUMES]->(r:Resource)
        WHERE date(con.date) >= date() - duration({days: 1})
        WITH c, avg(con.amount) as avg_consumption
        WHERE avg_consumption > 100  // Arbitrary high threshold
        RETURN c.id as customer_id,
               'high_consumption' as anomaly_type
        LIMIT 10
        """
        
        consumption_anomalies = self.conn.execute_query(query=consumption_query, region=region)
        
        # Check if there are correlated anomalies
        total_anomalies = len(pressure_anomalies) + len(consumption_anomalies)
        is_correlated = total_anomalies > 5
        
        return {
            'region': region,
            'time_window_hours': time_window_hours,
            'pressure_anomalies': len(pressure_anomalies),
            'consumption_anomalies': len(consumption_anomalies),
            'total_anomalies': total_anomalies,
            'is_correlated': is_correlated,
            'severity': 'high' if is_correlated else 'normal',
            'details': {
                'pressure': pressure_anomalies[:5],
                'consumption': consumption_anomalies[:5]
            }
        }
    
    def calculate_anomaly_score(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Calculate overall anomaly score for a customer (0-100).
        Higher score = more anomalous behavior.
        """
        customer = self.conn.execute_query(
            "MATCH (c:Customer {id: $id}) RETURN c",
            id=customer_id
        )
        
        if not customer:
            return {'error': 'Customer not found'}
        
        customer = customer[0]['c']
        score = 0.0
        factors = []
        
        # Check payment history
        if customer.get('current_balance', 0) > 500:
            score += 15
            factors.append('high_outstanding_balance')
        
        # Check consumption deviation
        avg_consumption = customer.get('average_monthly_consumption', 0)
        if avg_consumption > 100:  # High consumer
            score += 10
            factors.append('high_consumption')
        
        # Check account status
        if customer.get('status') != 'active':
            score += 20
            factors.append('inactive_account')
        
        # Additional checks could include:
        # - Recent service requests
        # - Meter issues
        # - Historical incidents
        
        return {
            'customer_id': customer_id,
            'anomaly_score': round(score, 1),
            'risk_level': 'high' if score > 50 else 'medium' if score > 25 else 'low',
            'contributing_factors': factors
        }
