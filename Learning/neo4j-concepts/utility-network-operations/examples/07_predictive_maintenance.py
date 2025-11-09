"""Predictive maintenance example demonstrating ML-based maintenance scheduling."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.infrastructure_repo import InfrastructureRepository
from src.algorithms.predictive_maintenance import PredictiveMaintenance


def main():
    """Demonstrate predictive maintenance capabilities."""
    
    print("=" * 60)
    print("Utility Network - Predictive Maintenance Example")
    print("=" * 60)
    
    conn = Neo4jConnection()
    infra_repo = InfrastructureRepository(conn)
    pm = PredictiveMaintenance(infra_repo)
    
    # 1. Predict Pipeline Failures
    print("\n1. Pipeline Failure Prediction")
    print("-" * 60)
    
    predictions = pm.predict_pipeline_failures(risk_threshold=50)
    
    print(f"High Risk Pipelines: {len(predictions)}")
    
    if predictions:
        print("\nTop 5 Risk Pipelines:")
        for pred in predictions[:5]:
            print(f"\n  {pred['pipeline_id']}")
            print(f"  Failure Risk: {pred['failure_risk']}/100")
            print(f"  Remaining Useful Life: {pred['remaining_useful_life_days']} days")
            print(f"  Recommended Action: {pred['recommended_action']}")
            print(f"  Priority: {pred['priority']}")
            
            if pred.get('risk_factors'):
                print(f"  Risk Factors:")
                for factor in pred['risk_factors'][:3]:
                    print(f"    - {factor}")
    
    # 2. Calculate Remaining Useful Life
    print("\n2. Remaining Useful Life (RUL) Analysis")
    print("-" * 60)
    
    # Get sample pipeline
    pipelines = conn.execute_query("MATCH (p:PipelineSegment) RETURN p.id as id LIMIT 1")
    if pipelines:
        pipeline_id = pipelines[0]['id']
        
        rul = pm.calculate_remaining_useful_life(pipeline_id)
        
        print(f"Pipeline: {pipeline_id}")
        print(f"RUL: {rul['remaining_days']} days ({rul['remaining_years']:.1f} years)")
        print(f"Confidence: {rul['confidence']:.1f}%")
        print(f"Current Age: {rul['current_age_years']:.1f} years")
        print(f"Expected Lifetime: {rul['expected_lifetime_years']:.1f} years")
        
        if rul.get('degradation_factors'):
            print("\nDegradation Factors:")
            for factor in rul['degradation_factors']:
                print(f"  - {factor}")
    
    # 3. Generate Maintenance Schedule
    print("\n3. Maintenance Schedule Generation")
    print("-" * 60)
    
    schedule = pm.generate_maintenance_schedule(months_ahead=6)
    
    print(f"Total Maintenance Tasks: {len(schedule['tasks'])}")
    print(f"Period: {schedule['schedule_period']}")
    print(f"Total Estimated Cost: ${schedule['total_estimated_cost']:,.2f}")
    
    print("\nBy Month:")
    for month in schedule['monthly_breakdown']:
        print(f"  {month['month']}: {month['task_count']} tasks (${month['estimated_cost']:,.2f})")
    
    if schedule.get('tasks'):
        print("\nUpcoming Tasks (Next 5):")
        for task in schedule['tasks'][:5]:
            print(f"\n  Pipeline: {task['pipeline_id']}")
            print(f"  Type: {task['maintenance_type']}")
            print(f"  Scheduled: {task['recommended_date']}")
            print(f"  Priority: {task['priority']}")
            print(f"  Est. Cost: ${task['estimated_cost']:,.2f}")
            print(f"  Est. Duration: {task['estimated_duration_hours']} hours")
    
    # 4. Optimize Maintenance Routes
    print("\n4. Maintenance Route Optimization")
    print("-" * 60)
    
    if schedule.get('tasks'):
        task_ids = [task['pipeline_id'] for task in schedule['tasks'][:10]]
        
        routes = pm.optimize_maintenance_routes(
            pipeline_ids=task_ids,
            num_crews=2
        )
        
        print(f"Optimized Routes: {len(routes['routes'])}")
        print(f"Total Distance: {routes['total_distance_km']:.2f} km")
        print(f"Total Time: {routes['total_time_hours']:.2f} hours")
        print(f"Efficiency Gain: {routes.get('efficiency_gain', 0):.1f}%")
        
        if routes.get('routes'):
            for i, route in enumerate(routes['routes'], 1):
                print(f"\n  Crew {i}:")
                print(f"    Tasks: {len(route['tasks'])}")
                print(f"    Distance: {route['distance_km']:.2f} km")
                print(f"    Duration: {route['duration_hours']:.2f} hours")
                print(f"    Sequence: {' → '.join(route['sequence'][:5])}")
    
    # 5. Detect Maintenance Opportunities
    print("\n5. Maintenance Opportunity Detection")
    print("-" * 60)
    
    opportunities = pm.detect_maintenance_opportunities()
    
    print(f"Opportunities Found: {len(opportunities)}")
    
    if opportunities:
        print("\nTop Opportunities:")
        for opp in opportunities[:5]:
            print(f"\n  Location: {opp['location']}")
            print(f"  Pipelines: {opp['pipeline_count']}")
            print(f"  Combined Benefit: ${opp['combined_benefit']:,.2f}")
            print(f"  Cost Savings: {opp['cost_savings_percentage']:.1f}%")
            print(f"  Reason: {opp['reason']}")
    
    # 6. Cost-Benefit Analysis
    print("\n6. Cost-Benefit Analysis")
    print("-" * 60)
    
    if pipelines:
        cba = pm.calculate_cost_benefit_analysis(pipeline_id)
        
        print(f"Pipeline: {pipeline_id}")
        print(f"\nRepair Option:")
        print(f"  Cost: ${cba['repair_cost']:,.2f}")
        print(f"  Useful Life Extension: {cba['repair_life_extension_years']:.1f} years")
        
        print(f"\nReplace Option:")
        print(f"  Cost: ${cba['replacement_cost']:,.2f}")
        print(f"  New Useful Life: {cba['replacement_life_years']:.1f} years")
        
        print(f"\nRecommendation: {cba['recommendation']}")
        print(f"ROI: {cba['roi']:.1f}%")
        print(f"Payback Period: {cba['payback_years']:.1f} years")
        
        if cba.get('rationale'):
            print(f"\nRationale:")
            for reason in cba['rationale']:
                print(f"  - {reason}")
    
    # 7. Meter Battery Replacement Prediction
    print("\n7. Meter Battery Replacement Prediction")
    print("-" * 60)
    
    battery_pred = pm.predict_meter_battery_replacement(days_ahead=90)
    
    print(f"Meters Needing Replacement: {len(battery_pred)}")
    
    if battery_pred:
        print("\nNext 30 Days:")
        next_30 = [m for m in battery_pred if m['days_until_replacement'] <= 30]
        print(f"  {len(next_30)} meters")
        
        print("\n31-60 Days:")
        next_60 = [m for m in battery_pred if 30 < m['days_until_replacement'] <= 60]
        print(f"  {len(next_60)} meters")
        
        print("\n61-90 Days:")
        next_90 = [m for m in battery_pred if 60 < m['days_until_replacement'] <= 90]
        print(f"  {len(next_90)} meters")
        
        if next_30:
            print("\nUrgent (Next 30 Days):")
            for meter in next_30[:5]:
                print(f"  {meter['meter_id']}: {meter['days_until_replacement']} days")
                print(f"    Current: {meter['current_battery']}%")
                print(f"    Priority: {meter['priority']}")
    
    # 8. Summary Statistics
    print("\n8. Predictive Maintenance Summary")
    print("-" * 60)
    
    stats = {
        'high_risk_pipelines': len(predictions),
        'maintenance_tasks_6m': len(schedule.get('tasks', [])),
        'total_cost_6m': schedule.get('total_estimated_cost', 0),
        'battery_replacements_90d': len(battery_pred),
        'maintenance_opportunities': len(opportunities)
    }
    
    print(f"High Risk Pipelines: {stats['high_risk_pipelines']}")
    print(f"Planned Maintenance (6 months): {stats['maintenance_tasks_6m']} tasks")
    print(f"Estimated Budget (6 months): ${stats['total_cost_6m']:,.2f}")
    print(f"Battery Replacements (90 days): {stats['battery_replacements_90d']}")
    print(f"Optimization Opportunities: {stats['maintenance_opportunities']}")
    
    print("\n" + "=" * 60)
    print("✓ Predictive maintenance demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
