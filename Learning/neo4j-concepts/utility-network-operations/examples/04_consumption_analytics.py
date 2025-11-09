"""Consumption analytics example demonstrating customer usage analysis."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.customer_repo import CustomerRepository
from src.services.consumption_analytics import ConsumptionAnalyticsService


def main():
    """Demonstrate consumption analytics capabilities."""
    
    print("=" * 60)
    print("Utility Network Operations - Consumption Analytics Example")
    print("=" * 60)
    
    conn = Neo4jConnection()
    customer_repo = CustomerRepository(conn)
    analytics_service = ConsumptionAnalyticsService(customer_repo)
    
    # Get a sample customer
    customers = conn.execute_query("MATCH (c:Customer) RETURN c.id as id LIMIT 1")
    if not customers:
        print("✗ No customers found. Run 02_load_sample_data.py first.")
        return
    
    customer_id = customers[0]['id']
    
    # 1. Analyze Customer Patterns
    print(f"\n1. Customer Consumption Pattern Analysis ({customer_id})")
    print("-" * 60)
    
    patterns = analytics_service.analyze_customer_patterns(customer_id, days=90)
    
    print(f"Analysis Period: {patterns['period_days']} days")
    print(f"Total Consumption: {patterns['total_consumption']:,.0f} liters")
    
    stats = patterns['statistics']
    print(f"\nStatistics:")
    print(f"  - Average Daily: {stats['average_daily']:.2f} liters")
    print(f"  - Min Daily: {stats['min_daily']:.2f} liters")
    print(f"  - Max Daily: {stats['max_daily']:.2f} liters")
    print(f"  - Std Dev: {stats['std_dev']:.2f}")
    
    if patterns.get('trend'):
        trend = patterns['trend']
        print(f"\nTrend: {trend['direction']} ({trend['percentage']:.1f}%)")
        print(f"  Description: {trend['description']}")
    
    if patterns.get('patterns_detected'):
        print(f"\nPatterns Detected:")
        for pattern in patterns['patterns_detected']:
            print(f"  - {pattern['type']}: {pattern['description']}")
    
    # 2. Detect Consumption Anomalies
    print(f"\n2. Consumption Anomaly Detection ({customer_id})")
    print("-" * 60)
    
    anomalies = analytics_service.detect_consumption_anomalies(customer_id, days=90)
    
    print(f"Anomalies Found: {len(anomalies)}")
    
    if anomalies:
        print("\nRecent Anomalies:")
        for anomaly in anomalies[:5]:
            print(f"\n  Date: {anomaly['date']}")
            print(f"  Consumption: {anomaly['consumption']:.2f} liters")
            print(f"  Expected: {anomaly['expected']:.2f} liters")
            print(f"  Deviation: {anomaly['deviation_percentage']:.1f}%")
            print(f"  Severity: {anomaly['severity']}")
            print(f"  Type: {anomaly['anomaly_type']}")
    
    # 3. Compare to Peers
    print(f"\n3. Peer Comparison Analysis ({customer_id})")
    print("-" * 60)
    
    comparison = analytics_service.compare_customer_to_peers(customer_id)
    
    print(f"Customer Consumption: {comparison['customer_consumption']:.2f} liters/day")
    print(f"Peer Average: {comparison['peer_average']:.2f} liters/day")
    print(f"Percentile: {comparison['percentile']:.0f}%")
    print(f"Category: {comparison['category']}")
    
    print(f"\nComparison:")
    if comparison['customer_consumption'] > comparison['peer_average']:
        diff = comparison['customer_consumption'] - comparison['peer_average']
        print(f"  Consuming {diff:.2f} liters/day MORE than peers ({comparison['percentage_difference']:.1f}%)")
    else:
        diff = comparison['peer_average'] - comparison['customer_consumption']
        print(f"  Consuming {diff:.2f} liters/day LESS than peers ({comparison['percentage_difference']:.1f}%)")
    
    if comparison.get('recommendations'):
        print(f"\nRecommendations:")
        for rec in comparison['recommendations']:
            print(f"  - {rec}")
    
    # 4. Forecast Future Consumption
    print(f"\n4. Consumption Forecasting ({customer_id})")
    print("-" * 60)
    
    forecast = analytics_service.forecast_consumption(customer_id, days_ahead=30)
    
    print(f"Forecast Period: Next {forecast['forecast_days']} days")
    print(f"Predicted Total: {forecast['predicted_total']:.0f} liters")
    print(f"Predicted Daily Average: {forecast['predicted_daily_average']:.2f} liters")
    print(f"Confidence: {forecast['confidence']:.1f}%")
    
    if forecast.get('prediction_range'):
        range_data = forecast['prediction_range']
        print(f"\nPrediction Range:")
        print(f"  - Low: {range_data['low']:.2f} liters/day")
        print(f"  - High: {range_data['high']:.2f} liters/day")
    
    if forecast.get('factors'):
        print(f"\nFactors Considered:")
        for factor in forecast['factors']:
            print(f"  - {factor}")
    
    # 5. Time of Day Analysis
    print("\n5. Time of Day Consumption Patterns")
    print("-" * 60)
    
    time_patterns = analytics_service.get_consumption_by_time_of_day()
    
    print("Average consumption by time period:")
    for period in time_patterns:
        print(f"\n  {period['time_period']}:")
        print(f"    Consumption: {period['avg_consumption']:.2f} liters")
        print(f"    % of Daily Total: {period['percentage_of_daily']:.1f}%")
        print(f"    Peak Hours: {', '.join(map(str, period['peak_hours']))}")
    
    # 6. High Consumers Report
    print("\n6. High Consumers Report")
    print("-" * 60)
    
    high_consumers = analytics_service.get_high_consumers_report(limit=10)
    
    print(f"Top {len(high_consumers)} High Consumers:")
    
    for i, consumer in enumerate(high_consumers, 1):
        print(f"\n  {i}. {consumer['customer_id']}")
        print(f"     Type: {consumer['type']}")
        print(f"     Avg Daily: {consumer['avg_daily_consumption']:.2f} liters")
        print(f"     Monthly: {consumer['monthly_consumption']:,.0f} liters")
        print(f"     Percentile: {consumer['percentile']:.0f}%")
        
        if consumer.get('cost_estimate'):
            print(f"     Est. Monthly Cost: ${consumer['cost_estimate']:.2f}")
    
    # 7. Overall Consumption Statistics
    print("\n7. Overall Consumption Statistics")
    print("-" * 60)
    
    overall_stats = analytics_service.get_consumption_statistics()
    
    print(f"Total Customers Analyzed: {overall_stats['total_customers']}")
    print(f"Total Consumption: {overall_stats['total_consumption']:,.0f} liters")
    print(f"Average per Customer: {overall_stats['avg_per_customer']:.2f} liters/day")
    
    print(f"\nBy Customer Type:")
    for ctype in overall_stats['by_type']:
        print(f"  {ctype['type']}:")
        print(f"    Count: {ctype['count']}")
        print(f"    Avg: {ctype['average']:.2f} liters/day")
        print(f"    Total: {ctype['total']:,.0f} liters")
    
    if overall_stats.get('trends'):
        trends = overall_stats['trends']
        print(f"\nRecent Trends:")
        print(f"  - Week over Week: {trends['wow_change']:.1f}%")
        print(f"  - Month over Month: {trends['mom_change']:.1f}%")
    
    # 8. Water Conservation Candidates
    print("\n8. Water Conservation Candidates")
    print("-" * 60)
    
    conservation = analytics_service.identify_water_conservation_candidates(limit=10)
    
    print(f"Candidates Identified: {len(conservation)}")
    print("\nTop candidates for conservation programs:")
    
    for candidate in conservation[:5]:
        print(f"\n  Customer: {candidate['customer_id']}")
        print(f"  Current Usage: {candidate['current_consumption']:.2f} liters/day")
        print(f"  Potential Savings: {candidate['potential_savings']:.2f} liters/day")
        print(f"  Savings Percentage: {candidate['savings_percentage']:.1f}%")
        print(f"  Reason: {candidate['reason']}")
        
        if candidate.get('recommendations'):
            print(f"  Recommendations:")
            for rec in candidate['recommendations'][:2]:
                print(f"    - {rec}")
    
    print("\n" + "=" * 60)
    print("✓ Consumption analytics demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
