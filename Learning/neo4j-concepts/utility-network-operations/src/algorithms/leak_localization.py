"""Leak localization algorithms using graph analysis."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..connection import Neo4jConnection


class LeakLocalization:
    """Algorithms for localizing leaks using pressure patterns and graph topology."""
    
    def __init__(self):
        """Initialize with database connection."""
        self.conn = Neo4jConnection()
    
    def localize_by_pressure_gradient(
        self,
        suspected_area_pipeline_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Localize leak by analyzing pressure gradients across pipelines.
        Sharp pressure drops indicate proximity to leak.
        """
        if not suspected_area_pipeline_ids:
            return {'error': 'No pipeline IDs provided'}
        
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.id IN $pipeline_ids
          AND p.current_pressure_bar IS NOT NULL
          AND p.max_pressure_bar IS NOT NULL
        WITH p,
             ((p.max_pressure_bar - p.current_pressure_bar) / p.max_pressure_bar) * 100 as pressure_drop_percent
        
        // Find connected segments
        OPTIONAL MATCH (p)-[:CONNECTS_TO]-(neighbor:PipelineSegment)
        WHERE neighbor.current_pressure_bar IS NOT NULL
        WITH p, pressure_drop_percent,
             collect({
                 id: neighbor.id,
                 pressure: neighbor.current_pressure_bar
             }) as neighbors
        
        RETURN p.id as pipeline_id,
               p.location as location,
               p.latitude as latitude,
               p.longitude as longitude,
               p.current_pressure_bar as current_pressure,
               p.max_pressure_bar as max_pressure,
               round(pressure_drop_percent, 2) as pressure_drop_percent,
               neighbors
        ORDER BY pressure_drop_percent DESC
        """
        
        result = self.conn.execute_query(query, pipeline_ids=suspected_area_pipeline_ids)
        
        if not result:
            return {'error': 'No data found for specified pipelines'}
        
        # The pipeline with highest pressure drop is most likely leak location
        most_likely = result[0]
        
        return {
            'most_likely_location': {
                'pipeline_id': most_likely['pipeline_id'],
                'location': most_likely['location'],
                'latitude': most_likely.get('latitude'),
                'longitude': most_likely.get('longitude'),
                'pressure_drop_percent': most_likely['pressure_drop_percent'],
                'confidence': min(most_likely['pressure_drop_percent'] / 50.0, 1.0)  # 50%+ drop = high confidence
            },
            'all_candidates': result[:5],
            'method': 'pressure_gradient_analysis'
        }
    
    def localize_by_flow_balance(
        self,
        region: str
    ) -> Dict[str, Any]:
        """
        Localize leak using flow balance analysis.
        Inflow != Outflow indicates leak in that region.
        """
        query = """
        MATCH (p:PipelineSegment {region: $region})
        WHERE p.current_flow_rate IS NOT NULL
        
        // Calculate inflow (from connected upstream segments)
        OPTIONAL MATCH (upstream)-[r1:CONNECTS_TO]->(p)
        WHERE upstream.current_flow_rate IS NOT NULL
        WITH p, sum(upstream.current_flow_rate) as total_inflow
        
        // Calculate outflow (to connected downstream segments)
        OPTIONAL MATCH (p)-[r2:CONNECTS_TO]->(downstream)
        WHERE downstream.current_flow_rate IS NOT NULL
        WITH p, total_inflow, sum(downstream.current_flow_rate) as total_outflow
        
        // Flow imbalance indicates leak
        WITH p, total_inflow, total_outflow,
             total_inflow - total_outflow as flow_imbalance
        WHERE flow_imbalance > 5  // Threshold for significant imbalance
        
        RETURN p.id as pipeline_id,
               p.location as location,
               round(total_inflow, 2) as inflow,
               round(total_outflow, 2) as outflow,
               round(flow_imbalance, 2) as estimated_leak_rate,
               round((flow_imbalance / total_inflow) * 100, 2) as loss_percent
        ORDER BY flow_imbalance DESC
        LIMIT 10
        """
        
        result = self.conn.execute_query(query, region=region)
        
        return {
            'region': region,
            'leak_candidates': result,
            'method': 'flow_balance_analysis'
        }
    
    def triangulate_leak_location(
        self,
        sensor_readings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Triangulate leak location using multiple sensor readings.
        
        Args:
            sensor_readings: List of dicts with 'sensor_id', 'latitude', 'longitude', 'reading'
        """
        if len(sensor_readings) < 3:
            return {'error': 'Need at least 3 sensor readings for triangulation'}
        
        # Sort by reading intensity (lower pressure/higher flow = closer to leak)
        sorted_readings = sorted(
            sensor_readings,
            key=lambda x: x.get('reading', 0)
        )
        
        # Simple centroid calculation (real implementation would be more sophisticated)
        top_3 = sorted_readings[:3]
        
        avg_lat = sum(s.get('latitude', 0) for s in top_3) / 3
        avg_lon = sum(s.get('longitude', 0) for s in top_3) / 3
        
        return {
            'estimated_location': {
                'latitude': round(avg_lat, 6),
                'longitude': round(avg_lon, 6)
            },
            'confidence': 0.7,
            'method': 'sensor_triangulation',
            'sensors_used': [s['sensor_id'] for s in top_3],
            'search_radius_m': 100
        }
    
    def identify_leak_propagation_path(
        self,
        leak_pipeline_id: str,
        max_hops: int = 5
    ) -> Dict[str, Any]:
        """Identify how leak effects propagate through the network."""
        query = """
        MATCH (leak:PipelineSegment {id: $leak_id})
        
        // Find downstream affected segments
        MATCH path = (leak)-[:CONNECTS_TO*1..{max_hops}]->(downstream:PipelineSegment)
        WHERE downstream.current_pressure_bar IS NOT NULL
        WITH leak, downstream, length(path) as distance,
             [n IN nodes(path) | n.id] as path_nodes
        
        // Calculate pressure drop with distance
        RETURN downstream.id as affected_pipeline_id,
               downstream.location as location,
               distance as hops_from_leak,
               path_nodes,
               downstream.current_pressure_bar as current_pressure,
               CASE 
                 WHEN distance = 1 THEN 'high'
                 WHEN distance <= 2 THEN 'medium'
                 ELSE 'low'
               END as impact_level
        ORDER BY distance, current_pressure ASC
        """.format(max_hops=max_hops)
        
        result = self.conn.execute_query(query, leak_id=leak_pipeline_id)
        
        return {
            'leak_pipeline_id': leak_pipeline_id,
            'propagation_paths': result,
            'affected_count': len(result)
        }
    
    def estimate_leak_size(
        self,
        pipeline_id: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Estimate leak size based on pressure drop and pipe characteristics.
        """
        query = """
        MATCH (p:PipelineSegment {id: $pipeline_id})
        WHERE p.current_pressure_bar IS NOT NULL
          AND p.max_pressure_bar IS NOT NULL
          AND p.diameter_mm IS NOT NULL
        
        WITH p,
             p.max_pressure_bar - p.current_pressure_bar as pressure_drop,
             (p.max_pressure_bar - p.current_pressure_bar) / p.max_pressure_bar as pressure_drop_ratio
        
        RETURN p.id as pipeline_id,
               p.diameter_mm as diameter_mm,
               round(pressure_drop, 2) as pressure_drop_bar,
               round(pressure_drop_ratio * 100, 2) as pressure_drop_percent,
               // Simplified leak rate estimation (real calculation is complex hydraulics)
               round(pressure_drop * p.diameter_mm / 10, 2) as estimated_leak_rate_lpm,
               round(pressure_drop * p.diameter_mm / 10 * 60 * $hours, 2) as estimated_loss_liters
        """
        
        result = self.conn.execute_query(
            query,
            pipeline_id=pipeline_id,
            hours=time_window_hours
        )
        
        return result[0] if result else {}
    
    def find_isolation_valves(
        self,
        leak_pipeline_id: str,
        max_distance_hops: int = 3
    ) -> Dict[str, Any]:
        """
        Find valves that can be closed to isolate the leak.
        """
        query = """
        MATCH (leak:PipelineSegment {id: $leak_id})
        
        // Find nearby valves
        MATCH path = (leak)-[:CONNECTS_TO*0..{max_hops}]-(valve_pipe:PipelineSegment)
              -[:CONTROLS]-(valve:Valve)
        
        WITH valve, leak, length(path) as distance,
             [n IN nodes(path) | n.id] as path_through
        
        RETURN valve.id as valve_id,
               valve.location as location,
               valve.type as valve_type,
               valve.status as current_status,
               distance as hops_from_leak,
               path_through
        ORDER BY distance ASC
        LIMIT 10
        """.format(max_hops=max_distance_hops)
        
        result = self.conn.execute_query(query, leak_id=leak_pipeline_id)
        
        return {
            'leak_pipeline_id': leak_pipeline_id,
            'isolation_valves': result,
            'recommendation': 'Close valves to isolate leak zone' if result else 'No valves found in vicinity'
        }
    
    def calculate_affected_customers(
        self,
        leak_pipeline_id: str
    ) -> Dict[str, Any]:
        """Calculate which customers are affected by a leak."""
        query = """
        MATCH (leak:PipelineSegment {id: $leak_id})
        
        // Find customers downstream of leak
        MATCH (leak)-[:CONNECTS_TO*0..10]-(downstream:PipelineSegment)
              -[:CONNECTS_TO*0..5]-(meter:Meter)
              -[:MEASURES]->(customer:Customer)
        
        WITH DISTINCT customer, leak
        
        RETURN customer.id as customer_id,
               customer.name as customer_name,
               customer.type as customer_type,
               customer.address as address,
               customer.phone as phone
        ORDER BY customer.type, customer.name
        """
        
        result = self.conn.execute_query(query, leak_id=leak_pipeline_id)
        
        # Group by customer type
        by_type = {}
        for customer in result:
            ctype = customer['customer_type']
            if ctype not in by_type:
                by_type[ctype] = []
            by_type[ctype].append(customer)
        
        return {
            'leak_pipeline_id': leak_pipeline_id,
            'total_affected': len(result),
            'by_customer_type': {
                k: len(v) for k, v in by_type.items()
            },
            'affected_customers': result[:50],  # Limit to first 50
            'notification_required': len(result) > 0
        }
    
    def get_leak_history_pattern(
        self,
        location: str,
        radius_km: float = 2.0,
        days: int = 365
    ) -> Dict[str, Any]:
        """
        Analyze historical leak patterns in an area.
        Helps identify recurring problem zones.
        """
        query = """
        MATCH (i:Incident {type: 'leak'})
        WHERE i.location CONTAINS $location
          AND date(i.reported_date) >= date() - duration({days: $days})
        
        OPTIONAL MATCH (i)-[:AFFECTS]->(p:PipelineSegment)
        
        WITH i, p,
             date.truncate('month', date(i.reported_date)) as month
        
        RETURN toString(month) as month,
               count(i) as leak_count,
               collect(DISTINCT i.id) as incident_ids,
               collect(DISTINCT p.id) as affected_pipelines
        ORDER BY month DESC
        """
        
        result = self.conn.execute_query(
            query,
            location=location,
            days=days
        )
        
        total_leaks = sum(r['leak_count'] for r in result)
        
        return {
            'location': location,
            'period_days': days,
            'total_leaks': total_leaks,
            'monthly_pattern': result,
            'risk_level': 'high' if total_leaks > 10 else 'medium' if total_leaks > 5 else 'low'
        }
