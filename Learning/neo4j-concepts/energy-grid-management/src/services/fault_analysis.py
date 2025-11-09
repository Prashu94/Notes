"""
Fault Analysis Service for Energy Grid
Analyzes faults, identifies root causes, and predicts potential issues.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from neo4j import Driver

from ..models.incident import IncidentType, IncidentSeverity
from ..repositories.incident_repo import IncidentRepository
from ..repositories.sensor_repo import SensorRepository


class FaultAnalysisService:
    """Service for analyzing faults and predicting failures."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def analyze_fault_patterns(self, days: int = 90) -> Dict[str, Any]:
        """Analyze fault patterns over time."""
        with self.driver.session() as session:
            incident_repo = IncidentRepository(session)
            
            # Get incidents in time range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            incidents = incident_repo.get_incidents_in_date_range(start_date, end_date)
            
            # Get statistics
            stats_by_type = incident_repo.get_incident_stats_by_type()
            trend = incident_repo.get_incident_trend(days=days)
            affected_components = incident_repo.get_most_affected_components(limit=10)
            
            return {
                "time_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "total_incidents": len(incidents),
                "statistics_by_type": stats_by_type,
                "daily_trend": trend,
                "most_affected_components": affected_components,
                "severity_distribution": self._calculate_severity_distribution(incidents)
            }
    
    def identify_recurring_faults(self, threshold: int = 3) -> List[Dict[str, Any]]:
        """Identify components with recurring faults."""
        with self.driver.session() as session:
            query = """
            MATCH (i:Incident)-[:AFFECTS]->(component)
            WHERE i.reported_at >= datetime() - duration({days: 180})
            WITH component, 
                 labels(component)[0] as component_type,
                 count(i) as incident_count,
                 collect({
                     incident_id: i.incident_id,
                     type: i.type,
                     severity: i.severity,
                     reported_at: i.reported_at,
                     description: i.description
                 }) as incidents
            WHERE incident_count >= $threshold
            
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            
            RETURN 
                component_type,
                component.id as component_id,
                component.name as component_name,
                component.status as status,
                l.name as location,
                incident_count,
                incidents
            ORDER BY incident_count DESC
            """
            
            result = session.run(query, threshold=threshold)
            return [dict(record) for record in result]
    
    def analyze_fault_correlation(self) -> List[Dict[str, Any]]:
        """Identify correlated faults (incidents that occur together)."""
        with self.driver.session() as session:
            query = """
            // Find incidents that happened close in time
            MATCH (i1:Incident)-[:AFFECTS]->(c1)
            MATCH (i2:Incident)-[:AFFECTS]->(c2)
            WHERE i1.incident_id < i2.incident_id
              AND duration.between(i1.reported_at, i2.reported_at).minutes < 60
              AND c1 <> c2
            
            // Check if components are connected
            OPTIONAL MATCH path = shortestPath((c1)-[:CONNECTED_TO*..3]-(c2))
            
            WITH i1, i2, c1, c2, path,
                 CASE WHEN path IS NOT NULL THEN length(path) ELSE null END as distance
            
            RETURN 
                i1.incident_id as incident1_id,
                i1.type as incident1_type,
                i1.reported_at as incident1_time,
                labels(c1)[0] as component1_type,
                c1.id as component1_id,
                c1.name as component1_name,
                i2.incident_id as incident2_id,
                i2.type as incident2_type,
                i2.reported_at as incident2_time,
                labels(c2)[0] as component2_type,
                c2.id as component2_id,
                c2.name as component2_name,
                duration.between(i1.reported_at, i2.reported_at).minutes as time_diff_minutes,
                distance,
                CASE 
                    WHEN distance IS NOT NULL AND distance <= 1 THEN 'DIRECT'
                    WHEN distance IS NOT NULL AND distance <= 3 THEN 'INDIRECT'
                    ELSE 'UNCONNECTED'
                END as connection_type
            ORDER BY time_diff_minutes ASC
            LIMIT 50
            """
            
            result = session.run(query)
            return [dict(record) for record in result]
    
    def predict_failure_risk(self) -> List[Dict[str, Any]]:
        """Predict components at risk of failure based on multiple indicators."""
        with self.driver.session() as session:
            query = """
            MATCH (component)
            WHERE component:PowerPlant OR component:Substation OR component:TransmissionLine
            
            // Factor 1: Recent incident history
            OPTIONAL MATCH (component)<-[:AFFECTS]-(i:Incident)
            WHERE i.reported_at >= datetime() - duration({days: 90})
            WITH component, count(i) as recent_incidents
            
            // Factor 2: Sensor alarms
            OPTIONAL MATCH (component)<-[:MONITORS]-(s:Sensor)
            WHERE s.status = 'active'
            WITH component, recent_incidents,
                 count(s) as total_sensors,
                 count(CASE WHEN s.current_value < s.threshold_min 
                            OR s.current_value > s.threshold_max THEN 1 END) as alarm_count
            
            // Factor 3: Age/Status
            WITH component, recent_incidents, total_sensors, alarm_count,
                 CASE component.status
                     WHEN 'maintenance' THEN 2
                     WHEN 'operational' THEN 0
                     WHEN 'inactive' THEN 5
                     ELSE 1
                 END as status_score
            
            // Calculate failure risk score
            WITH component, recent_incidents, total_sensors, alarm_count, status_score,
                 (recent_incidents * 15 + 
                  alarm_count * 20 + 
                  status_score * 10 +
                  CASE WHEN total_sensors = 0 THEN 10 ELSE 0 END) as failure_risk_score
            
            WHERE failure_risk_score > 20
            
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            
            RETURN 
                labels(component)[0] as component_type,
                component.id as component_id,
                component.name as component_name,
                component.status as status,
                l.name as location,
                recent_incidents,
                total_sensors,
                alarm_count,
                failure_risk_score,
                CASE 
                    WHEN failure_risk_score > 80 THEN 'IMMINENT'
                    WHEN failure_risk_score > 60 THEN 'HIGH'
                    WHEN failure_risk_score > 40 THEN 'MEDIUM'
                    ELSE 'LOW'
                END as risk_level,
                CASE 
                    WHEN failure_risk_score > 80 THEN 'Immediate inspection required'
                    WHEN failure_risk_score > 60 THEN 'Schedule maintenance within 1 week'
                    WHEN failure_risk_score > 40 THEN 'Monitor closely, schedule maintenance within 1 month'
                    ELSE 'Continue normal monitoring'
                END as recommendation
            ORDER BY failure_risk_score DESC
            """
            
            result = session.run(query)
            return [dict(record) for record in result]
    
    def analyze_cascade_risk(self, component_id: str, component_type: str) -> Dict[str, Any]:
        """Analyze cascading failure risk if component fails."""
        with self.driver.session() as session:
            query = f"""
            MATCH (component:{component_type} {{id: $component_id}})
            
            // Find directly connected components
            MATCH path = (component)-[:CONNECTED_TO|SUPPLIES_TO*1..3]-(affected)
            WHERE affected <> component
            
            WITH component, affected, length(path) as distance
            
            // Get affected customers
            OPTIONAL MATCH (affected)-[:SUPPLIES_TO*0..2]->(c:Customer)
            WITH component, affected, distance, collect(DISTINCT c) as customers
            
            // Calculate impact
            WITH component, affected, distance, customers,
                 reduce(load = 0.0, c IN customers | load + c.consumption_mw) as affected_load
            
            RETURN 
                labels(affected)[0] as affected_component_type,
                affected.id as affected_component_id,
                affected.name as affected_component_name,
                affected.status as affected_status,
                distance as cascade_distance,
                size(customers) as affected_customers,
                affected_load as affected_load_mw,
                CASE 
                    WHEN distance = 1 THEN 'IMMEDIATE'
                    WHEN distance = 2 THEN 'SECONDARY'
                    ELSE 'TERTIARY'
                END as cascade_level
            ORDER BY distance, affected_load DESC
            """
            
            result = session.run(query, component_id=component_id)
            cascade_components = [dict(record) for record in result]
            
            # Calculate total impact
            total_affected_customers = sum(c["affected_customers"] for c in cascade_components)
            total_affected_load = sum(c["affected_load_mw"] for c in cascade_components)
            
            return {
                "trigger_component": {
                    "id": component_id,
                    "type": component_type
                },
                "cascade_components": cascade_components,
                "total_impact": {
                    "affected_components": len(cascade_components),
                    "affected_customers": total_affected_customers,
                    "affected_load_mw": total_affected_load,
                    "immediate_impact_components": len([c for c in cascade_components if c["cascade_level"] == "IMMEDIATE"]),
                    "secondary_impact_components": len([c for c in cascade_components if c["cascade_level"] == "SECONDARY"])
                }
            }
    
    def get_root_cause_analysis(self, incident_id: str) -> Dict[str, Any]:
        """Perform root cause analysis for an incident."""
        with self.driver.session() as session:
            incident_repo = IncidentRepository(session)
            sensor_repo = SensorRepository(session)
            
            # Get incident details
            incident = incident_repo.get_incident_by_id(incident_id)
            if not incident:
                return {}
            
            # Find affected component
            query = """
            MATCH (i:Incident {incident_id: $incident_id})-[:AFFECTS]->(component)
            OPTIONAL MATCH (component)-[:LOCATED_IN]->(l:Location)
            RETURN 
                labels(component)[0] as component_type,
                component.id as component_id,
                component.name as component_name,
                l.name as location
            """
            
            result = session.run(query, incident_id=incident_id)
            component_record = result.single()
            
            if not component_record:
                return {}
            
            component_id = component_record["component_id"]
            component_type = component_record["component_type"]
            
            # Get sensor readings around incident time
            sensors = sensor_repo.get_sensors_for_component(component_id, component_type)
            
            # Get related incidents
            related = incident_repo.get_incidents_by_component(component_id, component_type)
            
            # Analyze patterns
            potential_causes = []
            
            # Check for sensor alarms
            alarms = [s for s in sensors if s.is_in_alarm]
            if alarms:
                potential_causes.append({
                    "cause": "Sensor threshold violations detected",
                    "confidence": "HIGH",
                    "evidence": [f"{s.name}: {s.current_value} {s.unit} (threshold: {s.threshold_min}-{s.threshold_max})" for s in alarms]
                })
            
            # Check for recurring pattern
            if len(related) > 2:
                potential_causes.append({
                    "cause": "Recurring fault pattern",
                    "confidence": "MEDIUM",
                    "evidence": [f"Component has {len(related)} incidents in history"]
                })
            
            # Check for nearby incidents
            correlation = self._find_nearby_incidents(session, incident_id, incident.reported_at)
            if correlation:
                potential_causes.append({
                    "cause": "Correlated with nearby component failures",
                    "confidence": "MEDIUM",
                    "evidence": correlation
                })
            
            return {
                "incident": {
                    "incident_id": incident.incident_id,
                    "type": incident.type.value,
                    "severity": incident.severity.value,
                    "description": incident.description,
                    "reported_at": incident.reported_at.isoformat()
                },
                "affected_component": dict(component_record),
                "sensor_readings": [
                    {
                        "sensor_id": s.sensor_id,
                        "name": s.name,
                        "type": s.type.value,
                        "current_value": s.current_value,
                        "unit": s.unit,
                        "in_alarm": s.is_in_alarm,
                        "alarm_type": s.alarm_type
                    }
                    for s in sensors
                ],
                "incident_history": [
                    {
                        "incident_id": i.incident_id,
                        "type": i.type.value,
                        "reported_at": i.reported_at.isoformat()
                    }
                    for i in related[-5:]  # Last 5 incidents
                ],
                "potential_root_causes": potential_causes,
                "recommendations": self._generate_recommendations(potential_causes, incident)
            }
    
    def _calculate_severity_distribution(self, incidents: List) -> Dict[str, int]:
        """Calculate distribution of incidents by severity."""
        distribution = {}
        for incident in incidents:
            severity = incident.severity.value
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution
    
    def _find_nearby_incidents(self, session, incident_id: str, reported_at: datetime) -> List[str]:
        """Find incidents that occurred nearby in time."""
        query = """
        MATCH (i:Incident)
        WHERE i.incident_id <> $incident_id
          AND duration.between($reported_at, i.reported_at).minutes BETWEEN -30 AND 30
        RETURN i.incident_id as incident_id, i.description as description
        LIMIT 5
        """
        
        result = session.run(query, incident_id=incident_id, reported_at=reported_at.isoformat())
        return [f"{r['incident_id']}: {r['description']}" for r in result]
    
    def _generate_recommendations(self, potential_causes: List[Dict], incident) -> List[str]:
        """Generate recommendations based on root cause analysis."""
        recommendations = []
        
        if any("threshold violations" in c["cause"] for c in potential_causes):
            recommendations.append("Inspect sensors and verify calibration")
            recommendations.append("Review threshold settings for appropriateness")
        
        if any("Recurring" in c["cause"] for c in potential_causes):
            recommendations.append("Schedule comprehensive maintenance inspection")
            recommendations.append("Consider component replacement if failures persist")
        
        if any("Correlated" in c["cause"] for c in potential_causes):
            recommendations.append("Investigate upstream/downstream components")
            recommendations.append("Check for systemic issues affecting multiple components")
        
        if incident.severity == IncidentSeverity.CRITICAL:
            recommendations.append("Prioritize immediate action to prevent cascade failures")
        
        return recommendations
