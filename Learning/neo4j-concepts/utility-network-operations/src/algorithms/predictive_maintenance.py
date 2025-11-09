"""Predictive maintenance algorithms for infrastructure management."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..connection import Neo4jConnection


class PredictiveMaintenance:
    """Algorithms for predicting equipment failures and optimizing maintenance schedules."""
    
    def __init__(self):
        """Initialize with database connection."""
        self.conn = Neo4jConnection()
    
    def predict_pipeline_failures(
        self,
        time_horizon_days: int = 180
    ) -> List[Dict[str, Any]]:
        """
        Predict which pipelines are likely to fail in the next period.
        Based on age, material, incident history, and condition.
        """
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.age_years IS NOT NULL
        
        // Calculate risk factors
        WITH p,
             // Age factor (0-40 points)
             CASE
               WHEN p.age_years > 50 THEN 40
               WHEN p.age_years > 30 THEN 30
               WHEN p.age_years > 20 THEN 20
               ELSE p.age_years * 0.5
             END as age_score,
             
             // Material factor (0-30 points)
             CASE p.material
               WHEN 'cast_iron' THEN 30
               WHEN 'steel' THEN 20
               WHEN 'ductile_iron' THEN 15
               WHEN 'copper' THEN 10
               ELSE 5
             END as material_score,
             
             // Status factor (0-30 points)
             CASE p.status
               WHEN 'failed' THEN 30
               WHEN 'maintenance' THEN 20
               ELSE 0
             END as status_score
        
        // Check incident history
        OPTIONAL MATCH (p)<-[:AFFECTS]-(i:Incident)
        WHERE date(i.reported_date) >= date() - duration({years: 1})
        WITH p, age_score, material_score, status_score,
             count(i) * 5 as incident_score  // 5 points per incident
        
        WITH p,
             age_score + material_score + status_score + incident_score as risk_score
        WHERE risk_score > 50
        
        // Calculate failure probability
        WITH p, risk_score,
             CASE
               WHEN risk_score > 80 THEN 0.75
               WHEN risk_score > 65 THEN 0.50
               ELSE 0.25
             END as failure_probability
        
        RETURN p.id as pipeline_id,
               p.location as location,
               p.age_years as age,
               p.material as material,
               p.status as current_status,
               round(risk_score, 1) as risk_score,
               round(failure_probability, 2) as failure_probability,
               CASE
                 WHEN risk_score > 80 THEN 'critical'
                 WHEN risk_score > 65 THEN 'high'
                 WHEN risk_score > 50 THEN 'medium'
                 ELSE 'low'
               END as priority
        ORDER BY risk_score DESC, failure_probability DESC
        LIMIT 50
        """
        
        result = self.conn.execute_query(query)
        
        return result
    
    def calculate_remaining_useful_life(
        self,
        pipeline_id: str
    ) -> Dict[str, Any]:
        """
        Estimate remaining useful life of a pipeline segment.
        Based on age, condition, material properties, and degradation rate.
        """
        query = """
        MATCH (p:PipelineSegment {id: $pipeline_id})
        
        // Typical lifespan by material (years)
        WITH p,
             CASE p.material
               WHEN 'PVC' THEN 50
               WHEN 'HDPE' THEN 50
               WHEN 'ductile_iron' THEN 75
               WHEN 'steel' THEN 60
               WHEN 'copper' THEN 50
               WHEN 'cast_iron' THEN 40
               ELSE 50
             END as expected_lifespan,
             coalesce(p.age_years, 0) as current_age
        
        // Calculate incidents to adjust degradation
        OPTIONAL MATCH (p)<-[:AFFECTS]-(i:Incident)
        WITH p, expected_lifespan, current_age,
             count(i) as incident_count
        
        // Adjust for maintenance history
        WITH p, expected_lifespan, current_age, incident_count,
             CASE
               WHEN p.last_inspection_date IS NOT NULL
                    AND duration.between(date(p.last_inspection_date), date()).days < 365
               THEN 1.1  // 10% bonus for recent inspection
               ELSE 1.0
             END as maintenance_factor
        
        // Calculate RUL
        WITH p, expected_lifespan, current_age, incident_count, maintenance_factor,
             (expected_lifespan - current_age) * maintenance_factor - (incident_count * 2) as rul_years
        
        RETURN p.id as pipeline_id,
               current_age,
               expected_lifespan,
               incident_count,
               round(rul_years, 1) as remaining_useful_life_years,
               CASE
                 WHEN rul_years < 5 THEN 'replace_soon'
                 WHEN rul_years < 10 THEN 'monitor_closely'
                 WHEN rul_years < 20 THEN 'routine_maintenance'
                 ELSE 'good_condition'
               END as recommendation
        """
        
        result = self.conn.execute_query(query, pipeline_id=pipeline_id)
        
        return result[0] if result else {}
    
    def generate_maintenance_schedule(
        self,
        months_ahead: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Generate optimal maintenance schedule based on risk and priority.
        """
        # Get high-risk pipelines
        at_risk = self.predict_pipeline_failures(time_horizon_days=180)
        
        # Prioritize by risk score
        schedule = []
        current_date = datetime.now()
        
        for idx, pipeline in enumerate(at_risk[:30]):  # Top 30
            risk_score = pipeline['risk_score']
            
            # Schedule sooner for higher risk
            if risk_score > 80:
                days_until = 7  # Within 1 week
            elif risk_score > 65:
                days_until = 30  # Within 1 month
            else:
                days_until = 90  # Within 3 months
            
            scheduled_date = current_date + timedelta(days=days_until)
            
            schedule.append({
                'pipeline_id': pipeline['pipeline_id'],
                'location': pipeline['location'],
                'risk_score': pipeline['risk_score'],
                'priority': pipeline['priority'],
                'scheduled_date': scheduled_date.strftime('%Y-%m-%d'),
                'maintenance_type': self._determine_maintenance_type(pipeline),
                'estimated_duration_hours': self._estimate_maintenance_duration(pipeline),
                'estimated_cost': self._estimate_maintenance_cost(pipeline)
            })
        
        return sorted(schedule, key=lambda x: x['scheduled_date'])
    
    def _determine_maintenance_type(self, pipeline: Dict[str, Any]) -> str:
        """Determine type of maintenance needed."""
        risk = pipeline['risk_score']
        
        if risk > 80:
            return 'replacement'
        elif risk > 70:
            return 'major_repair'
        elif risk > 60:
            return 'inspection_and_repair'
        else:
            return 'preventive_inspection'
    
    def _estimate_maintenance_duration(self, pipeline: Dict[str, Any]) -> float:
        """Estimate maintenance duration in hours."""
        maintenance_type = self._determine_maintenance_type(pipeline)
        
        durations = {
            'replacement': 48,
            'major_repair': 24,
            'inspection_and_repair': 12,
            'preventive_inspection': 4
        }
        
        return durations.get(maintenance_type, 8)
    
    def _estimate_maintenance_cost(self, pipeline: Dict[str, Any]) -> float:
        """Estimate maintenance cost in USD."""
        maintenance_type = self._determine_maintenance_type(pipeline)
        
        base_costs = {
            'replacement': 50000,
            'major_repair': 15000,
            'inspection_and_repair': 5000,
            'preventive_inspection': 1000
        }
        
        return base_costs.get(maintenance_type, 3000)
    
    def optimize_maintenance_routes(
        self,
        scheduled_maintenance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize routes for maintenance crews to minimize travel.
        Groups nearby maintenance tasks.
        """
        # This would use actual geocoordinates and routing algorithms
        # Simplified grouping by location string
        
        by_location = {}
        for task in scheduled_maintenance:
            location = task.get('location', 'Unknown')
            if location not in by_location:
                by_location[location] = []
            by_location[location].append(task)
        
        routes = []
        for location, tasks in by_location.items():
            if len(tasks) > 1:
                routes.append({
                    'location': location,
                    'task_count': len(tasks),
                    'tasks': tasks,
                    'total_duration_hours': sum(t.get('estimated_duration_hours', 0) for t in tasks),
                    'total_cost': sum(t.get('estimated_cost', 0) for t in tasks)
                })
        
        return {
            'total_locations': len(by_location),
            'consolidated_routes': len(routes),
            'routes': sorted(routes, key=lambda x: x['task_count'], reverse=True)
        }
    
    def detect_maintenance_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify opportunities for proactive maintenance.
        Look for patterns that suggest preventive action.
        """
        query = """
        MATCH (p:PipelineSegment)
        WHERE p.age_years > 20
          AND (p.last_inspection_date IS NULL
               OR duration.between(date(p.last_inspection_date), date()).days > 730)
        
        WITH p
        ORDER BY p.age_years DESC
        LIMIT 30
        
        RETURN p.id as pipeline_id,
               p.location as location,
               p.age_years as age,
               coalesce(p.last_inspection_date, 'never') as last_inspection,
               'overdue_inspection' as opportunity_type,
               'Schedule inspection to prevent failures' as recommendation
        """
        
        result = self.conn.execute_query(query)
        
        return result
    
    def calculate_cost_benefit_analysis(
        self,
        pipeline_id: str
    ) -> Dict[str, Any]:
        """
        Perform cost-benefit analysis for maintenance vs replacement.
        """
        # Get pipeline data
        pipeline = self.conn.execute_query(
            "MATCH (p:PipelineSegment {id: $id}) RETURN p",
            id=pipeline_id
        )
        
        if not pipeline:
            return {'error': 'Pipeline not found'}
        
        pipeline = pipeline[0]['p']
        age = pipeline.get('age_years', 0)
        
        # Get RUL
        rul_data = self.calculate_remaining_useful_life(pipeline_id)
        rul = rul_data.get('remaining_useful_life_years', 10)
        
        # Calculate costs
        annual_maintenance_cost = 2000  # Base annual maintenance
        repair_cost = 15000
        replacement_cost = 50000
        
        # Cost of continuing with repairs
        years_until_replacement = max(rul, 5)
        total_repair_costs = (annual_maintenance_cost * years_until_replacement) + repair_cost
        
        # Risk costs (potential failure costs)
        failure_probability = 0.05 * (age / 10)  # Increases with age
        failure_cost = 100000  # Cost of emergency repair + damages
        expected_failure_cost = failure_probability * failure_cost * years_until_replacement
        
        total_keep_cost = total_repair_costs + expected_failure_cost
        
        # Compare to replacement
        savings = total_keep_cost - replacement_cost
        
        return {
            'pipeline_id': pipeline_id,
            'age': age,
            'remaining_useful_life': rul,
            'option_repair': {
                'annual_maintenance': annual_maintenance_cost,
                'repair_cost': repair_cost,
                'years_of_use': years_until_replacement,
                'total_cost': round(total_keep_cost, 2),
                'risk_cost': round(expected_failure_cost, 2)
            },
            'option_replace': {
                'replacement_cost': replacement_cost,
                'expected_lifespan': 50
            },
            'recommendation': 'replace_now' if savings > 0 else 'maintain_and_monitor',
            'potential_savings': round(abs(savings), 2) if savings > 0 else 0,
            'break_even_years': round(replacement_cost / annual_maintenance_cost, 1)
        }
    
    def predict_meter_battery_replacement(
        self,
        months_ahead: int = 6
    ) -> List[Dict[str, Any]]:
        """Predict which meters will need battery replacement soon."""
        query = """
        MATCH (m:Meter)
        WHERE m.battery_level IS NOT NULL
          AND m.battery_level < 40
        
        // Estimate months until replacement needed (battery at 10%)
        WITH m,
             ((m.battery_level - 10) / 5.0) as estimated_months_remaining
        WHERE estimated_months_remaining <= $months
        
        RETURN m.id as meter_id,
               m.location as location,
               m.battery_level as current_battery_level,
               round(estimated_months_remaining, 1) as months_until_replacement,
               CASE
                 WHEN estimated_months_remaining < 1 THEN 'urgent'
                 WHEN estimated_months_remaining < 3 THEN 'high'
                 ELSE 'medium'
               END as priority
        ORDER BY estimated_months_remaining ASC
        """
        
        result = self.conn.execute_query(query, months=months_ahead)
        
        return result
