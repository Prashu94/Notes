"""
Load Forecasting Service for Energy Grid
Predicts future load and capacity requirements.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from neo4j import Driver

from ..repositories.infrastructure_repo import InfrastructureRepository
from ..repositories.analytics_repo import AnalyticsRepository


class LoadForecastingService:
    """Service for forecasting energy load and capacity planning."""
    
    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver."""
        self.driver = driver
    
    def get_current_load_profile(self) -> Dict[str, Any]:
        """Get current load profile across the grid."""
        with self.driver.session() as session:
            analytics_repo = AnalyticsRepository(session)
            capacity_analysis = analytics_repo.get_capacity_analysis()
            customer_segmentation = analytics_repo.get_customer_segmentation()
            regional_performance = analytics_repo.get_regional_performance()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "capacity_analysis": capacity_analysis,
            "customer_segmentation": customer_segmentation,
            "regional_breakdown": regional_performance
        }
    
    def forecast_load_growth(
        self,
        years: int = 5,
        annual_growth_rate: float = 0.03  # 3% default
    ) -> Dict[str, Any]:
        """Forecast load growth over specified years."""
        with self.driver.session() as session:
            query = """
            MATCH (c:Customer)
            WITH c.type as customer_type,
                 sum(c.consumption_mw) as current_load
            
            RETURN 
                customer_type,
                current_load,
                current_load * (1 + $growth_rate) as year_1_load,
                current_load * power((1 + $growth_rate), 2) as year_2_load,
                current_load * power((1 + $growth_rate), 3) as year_3_load,
                current_load * power((1 + $growth_rate), 4) as year_4_load,
                current_load * power((1 + $growth_rate), 5) as year_5_load
            ORDER BY current_load DESC
            """
            
            result = session.run(query, growth_rate=annual_growth_rate)
            forecasts_by_type = [dict(record) for record in result]
            
            # Calculate total
            total_forecast = {
                "current": sum(f["current_load"] for f in forecasts_by_type),
                "year_1": sum(f["year_1_load"] for f in forecasts_by_type),
                "year_2": sum(f["year_2_load"] for f in forecasts_by_type),
                "year_3": sum(f["year_3_load"] for f in forecasts_by_type),
                "year_4": sum(f["year_4_load"] for f in forecasts_by_type),
                "year_5": sum(f["year_5_load"] for f in forecasts_by_type)
            }
            
            return {
                "parameters": {
                    "years": years,
                    "annual_growth_rate": annual_growth_rate,
                    "growth_rate_pct": annual_growth_rate * 100
                },
                "total_forecast_mw": total_forecast,
                "by_customer_type": forecasts_by_type
            }
    
    def identify_capacity_gaps(
        self,
        years: int = 5,
        growth_rate: float = 0.03
    ) -> Dict[str, Any]:
        """Identify future capacity gaps by region."""
        with self.driver.session() as session:
            query = """
            MATCH (l:Location)
            
            // Get current capacity
            OPTIONAL MATCH (l)<-[:LOCATED_IN]-(pp:PowerPlant {status: 'operational'})
            WITH l, sum(pp.capacity_mw) as current_capacity
            
            // Get current consumption
            OPTIONAL MATCH (l)<-[:LOCATED_IN]-(c:Customer)
            WITH l, current_capacity, sum(c.consumption_mw) as current_consumption
            
            // Calculate future load
            WITH l, current_capacity, current_consumption,
                 current_consumption * power((1 + $growth_rate), $years) as future_consumption
            
            // Calculate gap
            WITH l, current_capacity, current_consumption, future_consumption,
                 future_consumption - current_capacity as capacity_gap
            
            WHERE capacity_gap > 0
            
            RETURN 
                l.name as region,
                l.state as state,
                current_capacity,
                current_consumption,
                (current_consumption / current_capacity * 100) as current_utilization_pct,
                future_consumption,
                capacity_gap,
                (capacity_gap / future_consumption * 100) as gap_pct,
                CASE 
                    WHEN capacity_gap > 100 THEN 'CRITICAL'
                    WHEN capacity_gap > 50 THEN 'HIGH'
                    WHEN capacity_gap > 20 THEN 'MEDIUM'
                    ELSE 'LOW'
                END as priority
            ORDER BY capacity_gap DESC
            """
            
            result = session.run(query, years=years, growth_rate=growth_rate)
            return [dict(record) for record in result]
    
    def recommend_capacity_additions(
        self,
        years: int = 5,
        growth_rate: float = 0.03,
        target_reserve_margin: float = 0.15  # 15% reserve
    ) -> List[Dict[str, Any]]:
        """Recommend new capacity additions by region."""
        gaps = self.identify_capacity_gaps(years, growth_rate)
        
        recommendations = []
        
        for gap in gaps:
            # Calculate required capacity including reserve margin
            required_additional_capacity = gap["capacity_gap"] * (1 + target_reserve_margin)
            
            # Suggest mix of generation types
            renewable_target = 0.4  # 40% renewable
            conventional_target = 0.6  # 60% conventional
            
            recommendation = {
                "region": gap["region"],
                "state": gap["state"],
                "priority": gap["priority"],
                "current_capacity_mw": gap["current_capacity"],
                "projected_demand_mw": gap["future_consumption"],
                "capacity_gap_mw": gap["capacity_gap"],
                "recommended_addition_mw": required_additional_capacity,
                "reserve_margin_pct": target_reserve_margin * 100,
                "suggested_mix": {
                    "total_mw": required_additional_capacity,
                    "renewable_mw": required_additional_capacity * renewable_target,
                    "conventional_mw": required_additional_capacity * conventional_target,
                    "breakdown": {
                        "solar_mw": required_additional_capacity * 0.2,
                        "wind_mw": required_additional_capacity * 0.15,
                        "natural_gas_mw": required_additional_capacity * 0.4,
                        "storage_mw": required_additional_capacity * 0.05
                    }
                },
                "estimated_investment_millions": required_additional_capacity * 1.5  # $1.5M per MW
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def analyze_peak_demand_patterns(self) -> Dict[str, Any]:
        """Analyze peak demand by customer type and region."""
        with self.driver.session() as session:
            query = """
            // By customer type
            MATCH (c:Customer)
            WITH c.type as customer_type,
                 max(c.consumption_mw) as peak_demand,
                 avg(c.consumption_mw) as avg_demand,
                 count(c) as customer_count
            
            RETURN customer_type, peak_demand, avg_demand, customer_count
            ORDER BY peak_demand DESC
            """
            
            result = session.run(query)
            by_type = [dict(record) for record in result]
            
            # By region
            query_region = """
            MATCH (l:Location)<-[:LOCATED_IN]-(c:Customer)
            WITH l.name as region,
                 sum(c.consumption_mw) as total_demand,
                 max(c.consumption_mw) as peak_individual,
                 count(c) as customer_count
            
            RETURN region, total_demand, peak_individual, customer_count
            ORDER BY total_demand DESC
            """
            
            result_region = session.run(query_region)
            by_region = [dict(record) for record in result_region]
            
            return {
                "by_customer_type": by_type,
                "by_region": by_region
            }
    
    def simulate_load_scenario(
        self,
        scenario_name: str,
        customer_growth: Dict[str, float],  # Growth by customer type
        new_capacity: Dict[str, float] = None  # New capacity by type
    ) -> Dict[str, Any]:
        """Simulate a load scenario with custom parameters."""
        with self.driver.session() as session:
            # Get current state
            query = """
            MATCH (c:Customer)
            WITH c.type as customer_type,
                 sum(c.consumption_mw) as current_consumption,
                 count(c) as customer_count
            RETURN customer_type, current_consumption, customer_count
            """
            
            result = session.run(query)
            current_state = {record["customer_type"]: dict(record) for record in result}
            
            # Apply scenario growth rates
            projected_state = {}
            for ctype, data in current_state.items():
                growth_factor = customer_growth.get(ctype, 1.0)
                projected_state[ctype] = {
                    "customer_type": ctype,
                    "current_consumption": data["current_consumption"],
                    "projected_consumption": data["current_consumption"] * growth_factor,
                    "growth_factor": growth_factor,
                    "growth_pct": (growth_factor - 1) * 100
                }
            
            # Get current capacity
            capacity_query = """
            MATCH (pp:PowerPlant {status: 'operational'})
            RETURN 
                sum(pp.capacity_mw) as total_capacity,
                sum(CASE WHEN pp.type IN ['solar', 'wind', 'hydro'] 
                    THEN pp.capacity_mw ELSE 0 END) as renewable_capacity
            """
            
            cap_result = session.run(capacity_query)
            cap_record = cap_result.single()
            current_capacity = dict(cap_record)
            
            # Calculate projected capacity
            additional_capacity = sum(new_capacity.values()) if new_capacity else 0
            projected_capacity = current_capacity["total_capacity"] + additional_capacity
            
            # Calculate balance
            total_projected_consumption = sum(
                ps["projected_consumption"] for ps in projected_state.values()
            )
            
            return {
                "scenario_name": scenario_name,
                "current_state": current_state,
                "projected_state": projected_state,
                "current_capacity_mw": current_capacity["total_capacity"],
                "projected_capacity_mw": projected_capacity,
                "additional_capacity_mw": additional_capacity,
                "total_projected_consumption_mw": total_projected_consumption,
                "supply_demand_balance": {
                    "capacity_mw": projected_capacity,
                    "demand_mw": total_projected_consumption,
                    "surplus_deficit_mw": projected_capacity - total_projected_consumption,
                    "utilization_pct": (total_projected_consumption / projected_capacity * 100) if projected_capacity > 0 else 0
                }
            }
    
    def get_comprehensive_forecast(
        self,
        years: int = 5,
        growth_rate: float = 0.03
    ) -> Dict[str, Any]:
        """Get comprehensive load forecast with recommendations."""
        current_profile = self.get_current_load_profile()
        growth_forecast = self.forecast_load_growth(years, growth_rate)
        capacity_gaps = self.identify_capacity_gaps(years, growth_rate)
        recommendations = self.recommend_capacity_additions(years, growth_rate)
        peak_patterns = self.analyze_peak_demand_patterns()
        
        return {
            "forecast_date": datetime.now().isoformat(),
            "parameters": {
                "forecast_years": years,
                "annual_growth_rate": growth_rate,
                "growth_rate_pct": growth_rate * 100
            },
            "current_profile": current_profile,
            "growth_forecast": growth_forecast,
            "capacity_gaps": capacity_gaps,
            "recommendations": recommendations,
            "peak_demand_analysis": peak_patterns,
            "summary": {
                "regions_with_gaps": len(capacity_gaps),
                "total_capacity_gap_mw": sum(g["capacity_gap"] for g in capacity_gaps),
                "total_recommended_investment_millions": sum(r["estimated_investment_millions"] for r in recommendations),
                "critical_regions": len([g for g in capacity_gaps if g["priority"] == "CRITICAL"])
            }
        }
