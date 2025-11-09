"""Network monitoring service for real-time network status."""

from typing import List, Dict, Any, Optional
from datetime import datetime

from ..repositories.infrastructure_repo import InfrastructureRepository
from ..repositories.incident_repo import IncidentRepository


class NetworkMonitoringService:
    """Service for monitoring utility network status and health."""
    
    def __init__(self):
        """Initialize service with repositories."""
        self.infrastructure_repo = InfrastructureRepository()
        self.incident_repo = IncidentRepository()
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get comprehensive network status."""
        # Get infrastructure stats
        infra_stats = self.infrastructure_repo.get_infrastructure_statistics()
        
        # Get active incidents
        active_incidents = self.incident_repo.get_active_incidents()
        critical_incidents = [i for i in active_incidents if i['i']['severity'] == 'critical']
        
        # Get anomalies
        pressure_anomalies = self.infrastructure_repo.get_pressure_anomalies()
        stale_meters = self.infrastructure_repo.get_stale_meters(max_age_hours=24)
        low_battery_meters = self.infrastructure_repo.get_low_battery_meters(threshold=20)
        
        # Calculate health score
        health_score = self._calculate_health_score(
            total_incidents=len(active_incidents),
            critical_incidents=len(critical_incidents),
            pressure_anomalies=len(pressure_anomalies),
            stale_meters=len(stale_meters)
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'infrastructure': infra_stats,
            'incidents': {
                'total_active': len(active_incidents),
                'critical': len(critical_incidents),
                'high': len([i for i in active_incidents if i['i']['severity'] == 'high']),
                'medium': len([i for i in active_incidents if i['i']['severity'] == 'medium']),
            },
            'anomalies': {
                'pressure_anomalies': len(pressure_anomalies),
                'stale_meters': len(stale_meters),
                'low_battery_meters': len(low_battery_meters),
            },
            'alerts': self._generate_alerts(
                critical_incidents,
                pressure_anomalies,
                stale_meters,
                low_battery_meters
            )
        }
    
    def _calculate_health_score(
        self,
        total_incidents: int,
        critical_incidents: int,
        pressure_anomalies: int,
        stale_meters: int
    ) -> float:
        """
        Calculate network health score (0-100).
        100 = perfect health, 0 = critical issues.
        """
        score = 100.0
        
        # Deduct for incidents
        score -= critical_incidents * 10
        score -= total_incidents * 2
        
        # Deduct for anomalies
        score -= pressure_anomalies * 3
        score -= stale_meters * 0.5
        
        return max(0.0, round(score, 1))
    
    def _generate_alerts(
        self,
        critical_incidents: List[Dict[str, Any]],
        pressure_anomalies: List[Dict[str, Any]],
        stale_meters: List[Dict[str, Any]],
        low_battery_meters: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate alert messages for critical issues."""
        alerts = []
        
        if critical_incidents:
            alerts.append({
                'level': 'critical',
                'message': f"{len(critical_incidents)} critical incident(s) require immediate attention"
            })
        
        if len(pressure_anomalies) > 5:
            alerts.append({
                'level': 'high',
                'message': f"{len(pressure_anomalies)} pipeline segments with abnormal pressure"
            })
        
        if len(stale_meters) > 10:
            alerts.append({
                'level': 'medium',
                'message': f"{len(stale_meters)} meters not reporting (possible communication issues)"
            })
        
        if len(low_battery_meters) > 20:
            alerts.append({
                'level': 'low',
                'message': f"{len(low_battery_meters)} meters with low battery"
            })
        
        return alerts
    
    def get_pressure_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get pressure monitoring dashboard data."""
        anomalies = self.infrastructure_repo.get_pressure_anomalies()
        
        low_pressure = [a for a in anomalies if a['pressure'] < a['max_pressure'] * 0.8]
        high_pressure = [a for a in anomalies if a['pressure'] > a['max_pressure']]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_anomalies': len(anomalies),
            'low_pressure_count': len(low_pressure),
            'high_pressure_count': len(high_pressure),
            'low_pressure_segments': [
                {
                    'id': a['p']['id'],
                    'current': a['pressure'],
                    'max': a['max_pressure'],
                    'percent': round((a['pressure'] / a['max_pressure']) * 100, 1),
                    'location': a['p'].get('location', 'Unknown')
                }
                for a in low_pressure[:10]
            ],
            'high_pressure_segments': [
                {
                    'id': a['p']['id'],
                    'current': a['pressure'],
                    'max': a['max_pressure'],
                    'percent': round((a['pressure'] / a['max_pressure']) * 100, 1),
                    'location': a['p'].get('location', 'Unknown')
                }
                for a in high_pressure[:10]
            ]
        }
    
    def get_meter_health_dashboard(self) -> Dict[str, Any]:
        """Get meter health monitoring dashboard."""
        stale_meters = self.infrastructure_repo.get_stale_meters(max_age_hours=24)
        low_battery = self.infrastructure_repo.get_low_battery_meters(threshold=20)
        faulty_meters = self.infrastructure_repo.get_meters_by_status('faulty')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'stale_meters': {
                'count': len(stale_meters),
                'details': [
                    {
                        'id': m['m']['id'],
                        'type': m['m']['type'],
                        'hours_old': m['hours_old'],
                        'location': m['m'].get('location', 'Unknown')
                    }
                    for m in stale_meters[:10]
                ]
            },
            'low_battery_meters': {
                'count': len(low_battery),
                'details': [
                    {
                        'id': m['m']['id'],
                        'battery_level': m['battery'],
                        'location': m['m'].get('location', 'Unknown')
                    }
                    for m in low_battery[:10]
                ]
            },
            'faulty_meters': {
                'count': len(faulty_meters),
                'meters': [m['id'] for m in faulty_meters[:10]]
            }
        }
    
    def get_regional_status(self) -> List[Dict[str, Any]]:
        """Get network status by region."""
        regional_summary = self.infrastructure_repo.get_regional_infrastructure_summary()
        
        # Enhance with incident data
        for region_data in regional_summary:
            region = region_data['region']
            
            # Get pipelines in region
            pipelines = self.infrastructure_repo.get_pipelines_by_region(region)
            pipeline_ids = [p['id'] for p in pipelines]
            
            # Count active incidents in region (simplified - would need more complex query in production)
            region_data['pipeline_count'] = len(pipeline_ids)
            region_data['status'] = 'healthy'  # Would calculate based on incidents
        
        return regional_summary
    
    def get_high_risk_infrastructure(self) -> Dict[str, Any]:
        """Get infrastructure components at high risk."""
        high_risk_pipelines = self.infrastructure_repo.get_high_risk_pipelines(risk_threshold=60.0)
        needs_inspection = self.infrastructure_repo.get_pipelines_needing_inspection()
        
        return {
            'high_risk_pipelines': {
                'count': len(high_risk_pipelines),
                'details': [
                    {
                        'id': p['p']['id'],
                        'age': p.get('age', 0),
                        'material': p['p']['material'],
                        'status': p['p']['status'],
                        'location': p['p'].get('location', 'Unknown')
                    }
                    for p in high_risk_pipelines[:20]
                ]
            },
            'needs_inspection': {
                'count': len(needs_inspection),
                'details': [
                    {
                        'id': p['p']['id'],
                        'last_inspection': p.get('last_inspection', 'never'),
                        'age': p['p'].get('age_years', 0),
                        'location': p['p'].get('location', 'Unknown')
                    }
                    for p in needs_inspection[:20]
                ]
            }
        }
    
    def get_storage_tank_status(self) -> List[Dict[str, Any]]:
        """Get storage tank status."""
        low_capacity_tanks = self.infrastructure_repo.get_low_capacity_tanks(threshold_percent=30.0)
        
        return [
            {
                'id': t['t']['id'],
                'type': t['t']['type'],
                'fill_percent': t['fill_percent'],
                'capacity_m3': t['t']['capacity_m3'],
                'current_level_m3': t['t']['current_level_m3'],
                'location': t['t'].get('location', 'Unknown'),
                'status': 'critical' if t['fill_percent'] < 10 else 'low'
            }
            for t in low_capacity_tanks
        ]
    
    def get_network_topology_overview(self) -> Dict[str, Any]:
        """Get network topology metrics."""
        topology = self.infrastructure_repo.get_network_topology_metrics()
        
        return {
            'nodes': topology.get('node_count', 0),
            'edges': topology.get('edge_count', 0),
            'diameter': topology.get('diameter', 0),
            'average_degree': topology.get('avg_degree', 0.0),
            'connectivity': self._assess_connectivity(topology)
        }
    
    def _assess_connectivity(self, topology: Dict[str, Any]) -> str:
        """Assess network connectivity based on topology metrics."""
        avg_degree = topology.get('avg_degree', 0.0)
        
        if avg_degree >= 3:
            return 'high'
        elif avg_degree >= 2:
            return 'medium'
        else:
            return 'low'
