"""Leak detection example demonstrating leak detection and localization."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.infrastructure_repo import InfrastructureRepository
from src.repositories.incident_repo import IncidentRepository
from src.services.leak_detection import LeakDetectionService


def main():
    """Demonstrate leak detection capabilities."""
    
    print("=" * 60)
    print("Utility Network Operations - Leak Detection Example")
    print("=" * 60)
    
    conn = Neo4jConnection()
    infra_repo = InfrastructureRepository(conn)
    incident_repo = IncidentRepository(conn)
    leak_service = LeakDetectionService(infra_repo, incident_repo)
    
    # 1. Detect Leaks
    print("\n1. Running Leak Detection Analysis...")
    print("-" * 60)
    leaks = leak_service.detect_leaks()
    
    print(f"Suspected Leaks Found: {len(leaks)}")
    
    if leaks:
        print("\nTop 5 Suspected Leaks:")
        for leak in leaks[:5]:
            print(f"\n  Pipeline: {leak['pipeline_id']}")
            print(f"  Severity: {leak['severity']}")
            print(f"  Confidence: {leak['confidence']:.0f}%")
            print(f"  Indicators:")
            for indicator in leak['indicators']:
                print(f"    - {indicator}")
            if leak.get('estimated_loss_lpm'):
                print(f"  Estimated Loss: {leak['estimated_loss_lpm']:.2f} liters/minute")
    else:
        print("  ✓ No leaks detected")
    
    # 2. Localize Specific Leak
    if leaks:
        print("\n2. Localizing Leak (Most Severe)")
        print("-" * 60)
        
        most_severe = leaks[0]
        pipeline_id = most_severe['pipeline_id']
        
        localization = leak_service.localize_leak(pipeline_id)
        
        print(f"\nLeak Localization for {pipeline_id}:")
        print(f"  Location: ({localization['latitude']:.4f}, {localization['longitude']:.4f})")
        print(f"  Confidence: {localization['confidence']:.0f}%")
        
        print("\n  Localization Methods:")
        for method, result in localization['localization_methods'].items():
            print(f"    - {method}: {result}")
        
        print(f"\n  Affected Area: {localization['affected_area']:.0f} meter radius")
        
        if localization.get('nearby_pipelines'):
            print(f"\n  Nearby Pipelines at Risk: {len(localization['nearby_pipelines'])}")
            for pipe in localization['nearby_pipelines'][:3]:
                print(f"    - {pipe}")
        
        if localization.get('affected_customers'):
            print(f"\n  Potentially Affected Customers: {localization['affected_customers']}")
        
        # 3. Create Leak Incident
        print("\n3. Creating Leak Incident...")
        print("-" * 60)
        
        incident_id = leak_service.create_leak_incident(
            pipeline_id=pipeline_id,
            severity=most_severe['severity'],
            estimated_loss_lpm=most_severe.get('estimated_loss_lpm', 0),
            latitude=localization['latitude'],
            longitude=localization['longitude']
        )
        
        print(f"  ✓ Created incident: {incident_id}")
        print(f"  - Priority: High")
        print(f"  - Status: Under Investigation")
    
    # 4. Estimate Water Loss
    print("\n4. Water Loss Estimation")
    print("-" * 60)
    
    water_loss = leak_service.estimate_water_loss(days=30)
    
    print(f"Period: Last 30 days")
    print(f"Total Estimated Loss: {water_loss['total_loss_liters']:,.0f} liters")
    print(f"Daily Average: {water_loss['daily_average']:,.0f} liters/day")
    print(f"Cost Impact: ${water_loss['estimated_cost']:,.2f}")
    
    if water_loss.get('major_leaks'):
        print(f"\nMajor Contributing Leaks: {len(water_loss['major_leaks'])}")
        for leak in water_loss['major_leaks'][:3]:
            print(f"  - {leak['pipeline_id']}: {leak['estimated_loss']:,.0f} liters")
    
    # 5. Leak History
    print("\n5. Leak History Analysis")
    print("-" * 60)
    
    history = leak_service.get_leak_history(months=12)
    
    print(f"Period: Last 12 months")
    print(f"Total Leaks: {history['total_leaks']}")
    print(f"Active Leaks: {history['active_leaks']}")
    print(f"Resolved Leaks: {history['resolved_leaks']}")
    print(f"Average Resolution Time: {history['avg_resolution_time_hours']:.1f} hours")
    
    if history.get('monthly_breakdown'):
        print("\nMonthly Breakdown:")
        for month_data in history['monthly_breakdown'][:6]:
            print(f"  {month_data['month']}: {month_data['count']} leaks")
    
    if history.get('most_common_types'):
        print("\nMost Common Leak Types:")
        for leak_type in history['most_common_types'][:3]:
            print(f"  - {leak_type['type']}: {leak_type['count']} incidents")
    
    # 6. Leak-Prone Areas
    print("\n6. Leak-Prone Area Analysis")
    print("-" * 60)
    
    prone_areas = leak_service.get_leak_prone_areas()
    
    print(f"High-Risk Areas Identified: {len(prone_areas)}")
    
    for area in prone_areas[:5]:
        print(f"\n  Region: {area['region']}")
        print(f"  Leak Count: {area['leak_count']} (last 12 months)")
        print(f"  Risk Score: {area['risk_score']}/100")
        print(f"  Affected Pipelines: {area['pipeline_count']}")
        
        if area.get('contributing_factors'):
            print(f"  Contributing Factors:")
            for factor in area['contributing_factors']:
                print(f"    - {factor}")
        
        if area.get('recommendations'):
            print(f"  Recommendations:")
            for rec in area['recommendations'][:2]:
                print(f"    - {rec}")
    
    # 7. Detection Metrics
    print("\n7. Leak Detection Metrics")
    print("-" * 60)
    
    metrics = leak_service.get_leak_detection_metrics()
    
    print(f"Detection Accuracy: {metrics['detection_accuracy']:.1f}%")
    print(f"False Positive Rate: {metrics['false_positive_rate']:.1f}%")
    print(f"Average Detection Time: {metrics['avg_detection_time_hours']:.1f} hours")
    print(f"Average Localization Accuracy: {metrics['localization_accuracy']:.1f} meters")
    
    performance = metrics['performance']
    print(f"\nPerformance:")
    print(f"  - Scanned Pipelines: {performance['pipelines_scanned']}")
    print(f"  - Anomalies Detected: {performance['anomalies_detected']}")
    print(f"  - Confirmed Leaks: {performance['confirmed_leaks']}")
    print(f"  - Water Saved: {performance['water_saved_liters']:,.0f} liters")
    
    print("\n" + "=" * 60)
    print("✓ Leak detection demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
