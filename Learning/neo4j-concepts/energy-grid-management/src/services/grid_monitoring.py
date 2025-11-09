"""
Grid Monitoring Service

Real-time monitoring of grid health and performance.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..repositories import InfrastructureRepository

logger = logging.getLogger(__name__)


class GridMonitoringService:
    """Service for monitoring grid operations."""
    
    def __init__(self, infrastructure_repo: Optional[InfrastructureRepository] = None):
        """Initialize service with repository."""
        self.infra_repo = infrastructure_repo or InfrastructureRepository()
    
    def get_grid_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive grid health status.
        
        Returns:
            Dictionary with health metrics including:
            - Overall status
            - Component counts
            - Capacity utilization
            - Critical alerts
        """
        stats = self.infra_repo.get_system_statistics()
        capacity_data = self.infra_repo.get_total_generation_capacity()
        
        # Check operational status
        plants = self.infra_repo.get_all_power_plants()
        substations = self.infra_repo.get_all_substations()
        
        operational_plants = [p for p in plants if p.get('status') == 'operational']
        operational_substations = [s for s in substations if s.get('status') == 'operational']
        
        # Calculate metrics
        plant_availability = (len(operational_plants) / len(plants) * 100) if plants else 0
        substation_availability = (len(operational_substations) / len(substations) * 100) if substations else 0
        
        # Overall health score (simple average)
        health_score = (plant_availability + substation_availability) / 2
        
        # Determine status
        if health_score >= 95:
            status = "HEALTHY"
        elif health_score >= 85:
            status = "WARNING"
        else:
            status = "CRITICAL"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": status,
            "health_score": round(health_score, 2),
            "components": {
                "power_plants": {
                    "total": len(plants),
                    "operational": len(operational_plants),
                    "availability_percent": round(plant_availability, 2)
                },
                "substations": {
                    "total": len(substations),
                    "operational": len(operational_substations),
                    "availability_percent": round(substation_availability, 2)
                }
            },
            "capacity": {
                "total_generation_mw": stats.get('total_generation', 0),
                "total_transmission_mva": stats.get('total_transmission', 0),
                "renewable_percent": round(capacity_data.get('renewable_percent', 0), 2)
            },
            "customers": {
                "total": stats.get('customer_count', 0),
                "total_consumption_kwh": stats.get('total_consumption', 0)
            }
        }
    
    def get_critical_components(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify critical components that need attention.
        
        Returns:
            Dictionary with lists of components by severity.
        """
        critical = []
        warning = []
        
        # Check power plants
        plants = self.infra_repo.get_all_power_plants()
        for plant in plants:
            if plant.get('status') == 'offline':
                critical.append({
                    "type": "PowerPlant",
                    "id": plant['id'],
                    "name": plant['name'],
                    "issue": "Offline",
                    "severity": "CRITICAL"
                })
            elif plant.get('status') == 'maintenance':
                warning.append({
                    "type": "PowerPlant",
                    "id": plant['id'],
                    "name": plant['name'],
                    "issue": "Under Maintenance",
                    "severity": "WARNING"
                })
        
        # Check substations
        substations = self.infra_repo.get_all_substations()
        for substation in substations:
            if substation.get('status') == 'offline':
                critical.append({
                    "type": "Substation",
                    "id": substation['id'],
                    "name": substation['name'],
                    "issue": "Offline",
                    "severity": "CRITICAL"
                })
            elif substation.get('status') == 'maintenance':
                warning.append({
                    "type": "Substation",
                    "id": substation['id'],
                    "name": substation['name'],
                    "issue": "Under Maintenance",
                    "severity": "WARNING"
                })
        
        return {
            "critical": critical,
            "warning": warning,
            "total_issues": len(critical) + len(warning)
        }
    
    def get_renewable_energy_report(self) -> Dict[str, Any]:
        """
        Generate renewable energy production report.
        
        Returns:
            Report with renewable energy statistics.
        """
        renewable_plants = self.infra_repo.get_renewable_plants()
        capacity_data = self.infra_repo.get_total_generation_capacity()
        
        # Group by type
        by_type = {}
        for plant in renewable_plants:
            plant_type = plant['type']
            if plant_type not in by_type:
                by_type[plant_type] = {
                    "count": 0,
                    "total_capacity_mw": 0,
                    "plants": []
                }
            by_type[plant_type]["count"] += 1
            by_type[plant_type]["total_capacity_mw"] += plant['capacity_mw']
            by_type[plant_type]["plants"].append({
                "id": plant['id'],
                "name": plant['name'],
                "capacity_mw": plant['capacity_mw'],
                "status": plant['status']
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_renewable_capacity_mw": capacity_data.get('renewable_capacity', 0),
                "renewable_percentage": round(capacity_data.get('renewable_percent', 0), 2),
                "plant_count": len(renewable_plants)
            },
            "by_type": by_type
        }
    
    def get_regional_overview(self) -> List[Dict[str, Any]]:
        """
        Get overview of grid operations by region.
        
        Returns:
            List of regional statistics.
        """
        regional_data = self.infra_repo.get_regional_capacity()
        
        for region_info in regional_data:
            # Calculate utilization if we have data
            if region_info.get('total_capacity') and region_info.get('total_consumption'):
                # Convert consumption from kWh to MW (rough estimate)
                consumption_mw = region_info['total_consumption'] / 1000
                capacity_mw = region_info['total_capacity']
                utilization = min((consumption_mw / capacity_mw * 100), 100) if capacity_mw > 0 else 0
                region_info['utilization_percent'] = round(utilization, 2)
            else:
                region_info['utilization_percent'] = 0
        
        return regional_data
    
    def check_power_flow_to_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Check power flow status for a specific customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Power flow status including sources and path info.
        """
        sources = self.infra_repo.get_power_sources_for_customer(customer_id)
        
        if not sources:
            return {
                "customer_id": customer_id,
                "status": "NO_SOURCES",
                "message": "No power sources found for customer",
                "sources": []
            }
        
        # Group by plant type
        by_type = {}
        for source in sources:
            plant_type = source['plant_type']
            if plant_type not in by_type:
                by_type[plant_type] = []
            by_type[plant_type].append({
                "plant_id": source['plant_id'],
                "plant_name": source['plant_name'],
                "capacity_mw": source['capacity_mw'],
                "path_length": source['path_length']
            })
        
        return {
            "customer_id": customer_id,
            "status": "CONNECTED",
            "total_sources": len(sources),
            "sources_by_type": by_type,
            "shortest_path_length": min(s['path_length'] for s in sources)
        }
    
    def analyze_transmission_network(self) -> Dict[str, Any]:
        """
        Analyze transmission network topology and health.
        
        Returns:
            Network analysis including connectivity and bottlenecks.
        """
        lines = self.infra_repo.get_all_transmission_lines()
        substations = self.infra_repo.get_all_substations()
        
        if not lines:
            return {
                "status": "NO_DATA",
                "message": "No transmission lines found"
            }
        
        # Calculate statistics
        total_capacity = sum(line['capacity_mw'] for line in lines)
        total_distance = sum(line['distance_km'] for line in lines)
        avg_loss = sum(line['loss_percent'] for line in lines) / len(lines) if lines else 0
        
        # Count operational vs offline
        operational_lines = [l for l in lines if l.get('status') == 'operational']
        
        # Find highest capacity lines
        top_lines = sorted(lines, key=lambda x: x['capacity_mw'], reverse=True)[:5]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_lines": len(lines),
                "operational_lines": len(operational_lines),
                "total_capacity_mw": round(total_capacity, 2),
                "total_distance_km": round(total_distance, 2),
                "average_loss_percent": round(avg_loss, 2)
            },
            "top_capacity_lines": [
                {
                    "line_id": line['line_id'],
                    "from": line['from_name'],
                    "to": line['to_name'],
                    "capacity_mw": line['capacity_mw'],
                    "status": line['status']
                }
                for line in top_lines
            ]
        }
    
    def get_capacity_utilization(self) -> Dict[str, Any]:
        """
        Calculate system-wide capacity utilization.
        
        Returns:
            Capacity utilization metrics.
        """
        stats = self.infra_repo.get_system_statistics()
        
        total_generation = stats.get('total_generation', 0)
        total_consumption = stats.get('total_consumption', 0)  # in kWh
        
        # Convert consumption to MW (rough average)
        consumption_mw = total_consumption / 1000
        
        utilization_percent = 0
        if total_generation > 0:
            utilization_percent = min((consumption_mw / total_generation * 100), 100)
        
        # Calculate headroom
        headroom_mw = max(total_generation - consumption_mw, 0)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_capacity_mw": round(total_generation, 2),
            "current_consumption_mw": round(consumption_mw, 2),
            "utilization_percent": round(utilization_percent, 2),
            "available_headroom_mw": round(headroom_mw, 2),
            "status": "NORMAL" if utilization_percent < 85 else "HIGH" if utilization_percent < 95 else "CRITICAL"
        }
