"""Leak detection service for identifying and localizing leaks."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..repositories.infrastructure_repo import InfrastructureRepository
from ..repositories.incident_repo import IncidentRepository
from ..models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus


class LeakDetectionService:
    """Service for detecting and localizing leaks in the network."""
    
    def __init__(self):
        """Initialize service with repositories."""
        self.infrastructure_repo = InfrastructureRepository()
        self.incident_repo = IncidentRepository()
    
    def detect_leaks(self) -> List[Dict[str, Any]]:
        """
        Detect potential leaks based on multiple indicators:
        - Abnormal pressure drops
        - Unusual flow rates
        - Pressure-flow correlations
        """
        potential_leaks = []
        
        # Check pressure anomalies
        pressure_anomalies = self.infrastructure_repo.get_pressure_anomalies()
        for anomaly in pressure_anomalies:
            pipeline = anomaly['p']
            
            # Low pressure is a leak indicator
            if pipeline.get('current_pressure_bar', 0) < pipeline.get('max_pressure_bar', 0) * 0.7:
                potential_leaks.append({
                    'pipeline_id': pipeline['id'],
                    'type': 'pressure_drop',
                    'severity': self._calculate_leak_severity(pipeline),
                    'confidence': 0.7,
                    'location': pipeline.get('location', 'Unknown'),
                    'current_pressure': pipeline.get('current_pressure_bar'),
                    'expected_pressure': pipeline.get('max_pressure_bar'),
                    'pressure_drop_percent': round(
                        (1 - pipeline.get('current_pressure_bar', 0) / pipeline.get('max_pressure_bar', 1)) * 100,
                        1
                    )
                })
        
        return potential_leaks
    
    def _calculate_leak_severity(self, pipeline: Dict[str, Any]) -> str:
        """Calculate leak severity based on pressure drop and pipe characteristics."""
        current = pipeline.get('current_pressure_bar', 0)
        max_pressure = pipeline.get('max_pressure_bar', 1)
        drop_percent = (1 - current / max_pressure) * 100
        
        diameter = pipeline.get('diameter_mm', 0)
        
        # Larger pipes + bigger pressure drops = more severe
        if drop_percent > 50 and diameter > 300:
            return 'critical'
        elif drop_percent > 40 or (drop_percent > 30 and diameter > 500):
            return 'high'
        elif drop_percent > 30:
            return 'medium'
        else:
            return 'low'
    
    def localize_leak(
        self,
        pipeline_id: str,
        search_radius_hops: int = 3
    ) -> Dict[str, Any]:
        """
        Localize a leak by analyzing neighboring pipeline segments.
        Returns probable location and affected area.
        """
        # Get the suspected pipeline
        pipeline = self.infrastructure_repo.get_pipeline(pipeline_id)
        if not pipeline:
            return {'error': 'Pipeline not found'}
        
        # In a real system, we would:
        # 1. Analyze pressure gradients in connected segments
        # 2. Check flow direction
        # 3. Correlate with sensor data
        # 4. Use hydraulic modeling
        
        # Simplified localization
        return {
            'suspected_pipeline_id': pipeline_id,
            'location': pipeline.get('location', 'Unknown'),
            'latitude': pipeline.get('latitude'),
            'longitude': pipeline.get('longitude'),
            'confidence': 0.75,
            'search_radius_m': pipeline.get('length_m', 0) / 2,
            'recommended_actions': [
                'Deploy field team for visual inspection',
                'Check nearby meter readings',
                'Review SCADA data for flow anomalies',
                'Isolate segment if pressure continues to drop'
            ]
        }
    
    def create_leak_incident(
        self,
        pipeline_id: str,
        severity: str = 'high',
        description: Optional[str] = None
    ) -> str:
        """Create an incident for a detected leak."""
        pipeline = self.infrastructure_repo.get_pipeline(pipeline_id)
        if not pipeline:
            return None
        
        if description is None:
            description = f"Potential leak detected on pipeline {pipeline_id} due to abnormal pressure"
        
        incident = Incident(
            id=f"INC-LEAK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            type=IncidentType.LEAK,
            severity=IncidentSeverity(severity),
            status=IncidentStatus.REPORTED,
            description=description,
            reported_date=datetime.now(),
            location=pipeline.get('location'),
            latitude=pipeline.get('latitude'),
            longitude=pipeline.get('longitude')
        )
        
        incident_id = self.incident_repo.create_incident(incident)
        
        # Link incident to pipeline
        if incident_id:
            self.incident_repo.link_incident_to_infrastructure(
                incident_id,
                pipeline_id,
                'PipelineSegment'
            )
        
        return incident_id
    
    def estimate_water_loss(
        self,
        pipeline_id: str,
        leak_duration_hours: float
    ) -> Dict[str, Any]:
        """Estimate water loss from a leak."""
        pipeline = self.infrastructure_repo.get_pipeline(pipeline_id)
        if not pipeline:
            return {'error': 'Pipeline not found'}
        
        # Simplified calculation based on pipe diameter and pressure
        diameter_mm = pipeline.get('diameter_mm', 100)
        pressure_bar = pipeline.get('current_pressure_bar', 3.0)
        
        # Approximate flow rate through leak (liters per minute)
        # This is a simplified formula; real calculations are complex
        leak_area_cm2 = (diameter_mm / 10) * 0.1  # Assume small leak
        flow_rate_lpm = leak_area_cm2 * pressure_bar * 10
        
        total_loss_liters = flow_rate_lpm * 60 * leak_duration_hours
        
        # Cost estimate (assuming $0.002 per liter)
        estimated_cost = total_loss_liters * 0.002
        
        return {
            'pipeline_id': pipeline_id,
            'leak_duration_hours': leak_duration_hours,
            'estimated_flow_rate_lpm': round(flow_rate_lpm, 2),
            'estimated_total_loss_liters': round(total_loss_liters, 2),
            'estimated_total_loss_m3': round(total_loss_liters / 1000, 2),
            'estimated_cost_usd': round(estimated_cost, 2)
        }
    
    def get_leak_history(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get historical leak incidents."""
        leak_incidents = self.incident_repo.get_incidents_by_type('leak')
        
        # Filter by date
        cutoff = datetime.now() - timedelta(days=days)
        recent_leaks = [
            inc for inc in leak_incidents
            if datetime.fromisoformat(inc['reported_date']) >= cutoff
        ]
        
        return recent_leaks
    
    def get_leak_prone_areas(self) -> List[Dict[str, Any]]:
        """Identify areas prone to leaks based on historical data."""
        # Get leak history
        leaks = self.get_leak_history(days=365)
        
        # Group by location/region
        location_counts = {}
        for leak in leaks:
            location = leak.get('location', 'Unknown')
            if location not in location_counts:
                location_counts[location] = {
                    'location': location,
                    'leak_count': 0,
                    'recent_leaks': []
                }
            location_counts[location]['leak_count'] += 1
            location_counts[location]['recent_leaks'].append({
                'id': leak['id'],
                'date': leak['reported_date'],
                'severity': leak['severity']
            })
        
        # Sort by leak count
        prone_areas = sorted(
            location_counts.values(),
            key=lambda x: x['leak_count'],
            reverse=True
        )
        
        return prone_areas[:10]
    
    def get_leak_detection_metrics(self) -> Dict[str, Any]:
        """Get leak detection performance metrics."""
        leak_incidents = self.incident_repo.get_incidents_by_type('leak')
        
        total_leaks = len(leak_incidents)
        
        # Calculate detection and response times
        detection_times = []
        response_times = []
        
        for incident in leak_incidents:
            if incident.get('confirmed_date'):
                reported = datetime.fromisoformat(incident['reported_date'])
                confirmed = datetime.fromisoformat(incident['confirmed_date'])
                detection_time = (confirmed - reported).total_seconds() / 3600
                detection_times.append(detection_time)
            
            if incident.get('resolved_date'):
                reported = datetime.fromisoformat(incident['reported_date'])
                resolved = datetime.fromisoformat(incident['resolved_date'])
                response_time = (resolved - reported).total_seconds() / 3600
                response_times.append(response_time)
        
        avg_detection = sum(detection_times) / len(detection_times) if detection_times else 0
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_leaks': total_leaks,
            'avg_detection_time_hours': round(avg_detection, 2),
            'avg_response_time_hours': round(avg_response, 2),
            'active_leaks': len([l for l in leak_incidents if l['status'] not in ['resolved', 'closed']]),
            'resolved_leaks': len([l for l in leak_incidents if l['status'] in ['resolved', 'closed']])
        }
