"""Consumption analytics service for analyzing usage patterns."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from statistics import mean, stdev

from ..repositories.customer_repo import CustomerRepository
from ..repositories.infrastructure_repo import InfrastructureRepository


class ConsumptionAnalyticsService:
    """Service for analyzing customer consumption patterns and anomalies."""
    
    def __init__(self):
        """Initialize service with repositories."""
        self.customer_repo = CustomerRepository()
        self.infrastructure_repo = InfrastructureRepository()
    
    def analyze_customer_patterns(
        self,
        customer_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """Analyze consumption patterns for a customer."""
        # Get consumption history
        history = self.customer_repo.get_customer_consumption_history(customer_id, days)
        
        if not history:
            return {'error': 'No consumption data found'}
        
        # Calculate statistics
        amounts = [h['amount'] for h in history]
        
        stats = {
            'customer_id': customer_id,
            'period_days': days,
            'total_readings': len(amounts),
            'total_consumption': round(sum(amounts), 2),
            'average_consumption': round(mean(amounts), 2),
            'max_consumption': round(max(amounts), 2),
            'min_consumption': round(min(amounts), 2),
            'std_deviation': round(stdev(amounts), 2) if len(amounts) > 1 else 0,
        }
        
        # Identify trends
        if len(amounts) >= 7:
            recent_avg = mean(amounts[:7])
            older_avg = mean(amounts[-7:])
            percent_change = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
            
            if percent_change > 20:
                trend = 'increasing'
            elif percent_change < -20:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            stats['trend'] = trend
            stats['trend_percent'] = round(percent_change, 1)
        
        # Detect seasonality (simplified)
        stats['pattern'] = self._detect_pattern(amounts)
        
        return stats
    
    def _detect_pattern(self, amounts: List[float]) -> str:
        """Detect consumption pattern (steady, variable, cyclic)."""
        if len(amounts) < 10:
            return 'insufficient_data'
        
        std = stdev(amounts)
        avg = mean(amounts)
        
        coefficient_of_variation = (std / avg) * 100 if avg > 0 else 0
        
        if coefficient_of_variation < 15:
            return 'steady'
        elif coefficient_of_variation > 40:
            return 'highly_variable'
        else:
            return 'moderate_variation'
    
    def detect_consumption_anomalies(
        self,
        threshold_multiplier: float = 2.0,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Detect customers with anomalous consumption."""
        # Get all active customers
        customers = self.customer_repo.get_customers_by_type('residential')
        customers.extend(self.customer_repo.get_customers_by_type('commercial'))
        customers.extend(self.customer_repo.get_customers_by_type('industrial'))
        
        anomalies = []
        
        for customer in customers:
            customer_id = customer['id']
            
            # Check for anomalies
            customer_anomalies = self.customer_repo.detect_consumption_anomalies(
                customer_id,
                threshold_multiplier
            )
            
            if customer_anomalies:
                anomalies.append({
                    'customer_id': customer_id,
                    'customer_name': customer['name'],
                    'customer_type': customer['type'],
                    'anomaly_count': len(customer_anomalies),
                    'recent_anomalies': customer_anomalies[:3]
                })
        
        return anomalies
    
    def compare_customer_to_peers(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """Compare customer consumption to similar customers."""
        customer = self.customer_repo.get_customer(customer_id)
        if not customer:
            return {'error': 'Customer not found'}
        
        # Get peer customers (same type and city)
        peers = self.customer_repo.get_customers_by_type(customer['type'])
        if customer.get('city'):
            peers = [p for p in peers if p.get('city') == customer['city']]
        
        # Calculate peer statistics
        peer_consumptions = [
            p['average_monthly_consumption']
            for p in peers
            if p['average_monthly_consumption'] > 0
        ]
        
        if not peer_consumptions:
            return {'error': 'No peer data available'}
        
        customer_consumption = customer['average_monthly_consumption']
        peer_avg = mean(peer_consumptions)
        peer_std = stdev(peer_consumptions) if len(peer_consumptions) > 1 else 0
        
        # Calculate percentile
        below_customer = len([p for p in peer_consumptions if p < customer_consumption])
        percentile = (below_customer / len(peer_consumptions)) * 100
        
        # Determine status
        if customer_consumption > peer_avg + 2 * peer_std:
            status = 'significantly_above_average'
        elif customer_consumption > peer_avg + peer_std:
            status = 'above_average'
        elif customer_consumption < peer_avg - 2 * peer_std:
            status = 'significantly_below_average'
        elif customer_consumption < peer_avg - peer_std:
            status = 'below_average'
        else:
            status = 'average'
        
        return {
            'customer_id': customer_id,
            'customer_consumption': customer_consumption,
            'peer_count': len(peers),
            'peer_average': round(peer_avg, 2),
            'peer_std_deviation': round(peer_std, 2),
            'percentile': round(percentile, 1),
            'status': status,
            'difference_from_average': round(customer_consumption - peer_avg, 2),
            'percent_difference': round(((customer_consumption - peer_avg) / peer_avg) * 100, 1) if peer_avg > 0 else 0
        }
    
    def forecast_consumption(
        self,
        customer_id: str,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """Forecast future consumption based on historical patterns."""
        # Get historical data
        history = self.customer_repo.get_customer_consumption_history(
            customer_id,
            days=180
        )
        
        if len(history) < 30:
            return {'error': 'Insufficient historical data'}
        
        # Simple trend-based forecast
        amounts = [h['amount'] for h in history]
        recent_avg = mean(amounts[:30])
        older_avg = mean(amounts[-30:])
        
        # Calculate growth rate
        growth_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        
        # Forecast
        forecast_amount = recent_avg * (1 + growth_rate)
        
        return {
            'customer_id': customer_id,
            'forecast_period_days': forecast_days,
            'forecasted_daily_avg': round(forecast_amount, 2),
            'forecasted_total': round(forecast_amount * forecast_days, 2),
            'current_daily_avg': round(recent_avg, 2),
            'growth_rate_percent': round(growth_rate * 100, 2),
            'confidence': 'medium',
            'method': 'trend_based'
        }
    
    def get_consumption_by_time_of_day(
        self,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze consumption patterns by time of day."""
        # In a real system, this would analyze hourly consumption data
        # This is a simplified placeholder
        
        return {
            'customer_id': customer_id or 'all',
            'peak_hours': [7, 8, 18, 19, 20],
            'off_peak_hours': [0, 1, 2, 3, 4, 5, 23],
            'note': 'Hourly data analysis requires time-series consumption data'
        }
    
    def get_high_consumers_report(
        self,
        limit: int = 20,
        customer_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get report of highest consumers."""
        customers = self.customer_repo.get_high_consumers(limit=limit)
        
        if customer_type:
            customers = [c for c in customers if c['c']['type'] == customer_type]
        
        return [
            {
                'rank': idx + 1,
                'customer_id': c['c']['id'],
                'customer_name': c['c']['name'],
                'customer_type': c['c']['type'],
                'monthly_consumption': c['consumption'],
                'annual_estimate': round(c['consumption'] * 12, 2),
                'city': c['c'].get('city', 'Unknown')
            }
            for idx, c in enumerate(customers)
        ]
    
    def get_consumption_statistics(self) -> Dict[str, Any]:
        """Get overall consumption statistics."""
        stats = self.customer_repo.get_customer_statistics()
        
        by_region = self.customer_repo.get_consumption_by_region()
        by_type = self.customer_repo.get_consumption_by_type()
        
        return {
            'overall': stats,
            'by_region': by_region,
            'by_customer_type': by_type
        }
    
    def identify_water_conservation_candidates(
        self,
        threshold_percentile: float = 75.0
    ) -> List[Dict[str, Any]]:
        """Identify customers who could benefit from conservation programs."""
        high_consumers = self.customer_repo.get_high_consumers(limit=100)
        
        candidates = []
        
        for consumer in high_consumers:
            customer = consumer['c']
            consumption = consumer['consumption']
            
            # Compare to peers
            comparison = self.compare_customer_to_peers(customer['id'])
            
            if comparison.get('percentile', 0) >= threshold_percentile:
                candidates.append({
                    'customer_id': customer['id'],
                    'customer_name': customer['name'],
                    'customer_type': customer['type'],
                    'monthly_consumption': consumption,
                    'percentile': comparison.get('percentile'),
                    'percent_above_average': comparison.get('percent_difference'),
                    'potential_savings_percent': min(30, comparison.get('percent_difference', 0) / 2),
                    'recommended_actions': [
                        'Water audit',
                        'Leak detection service',
                        'Efficiency upgrade incentives',
                        'Smart irrigation consultation'
                    ] if customer['type'] == 'residential' else [
                        'Commercial water audit',
                        'Process optimization review',
                        'Equipment efficiency assessment'
                    ]
                })
        
        return candidates[:20]
