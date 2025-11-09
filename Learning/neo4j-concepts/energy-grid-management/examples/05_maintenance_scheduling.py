"""
Example 5: Maintenance Scheduling
Demonstrates predictive maintenance and scheduling operations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.services.maintenance_scheduler import MaintenanceSchedulerService
from src.services.fault_analysis import FaultAnalysisService
from datetime import datetime, timedelta
import json


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print(f"{'=' * 80}\n")


def main():
    # Connect to Neo4j
    conn = Neo4jConnection()
    driver = conn.get_driver()
    
    if not driver:
        print("Failed to connect to Neo4j")
        return
    
    try:
        # Initialize services
        maintenance_service = MaintenanceSchedulerService(driver)
        fault_service = FaultAnalysisService(driver)
        
        # 1. Get Maintenance Priorities
        print_section("1. MAINTENANCE PRIORITIES")
        priorities = maintenance_service.get_maintenance_priorities()
        
        print(f"Found {len(priorities)} components needing maintenance:\n")
        for i, component in enumerate(priorities[:10], 1):
            print(f"{i}. {component['component_name']} ({component['component_type']})")
            print(f"   Status: {component['status']}")
            print(f"   Incidents (1 year): {component['incident_count']}")
            print(f"   Faulty Sensors: {component['faulty_sensors']}")
            print(f"   Priority Score: {component['priority_score']}")
            print()
        
        # 2. Identify High-Risk Components
        print_section("2. HIGH-RISK COMPONENTS")
        high_risk = maintenance_service.identify_high_risk_components()
        
        print(f"Found {len(high_risk)} high-risk components:\n")
        for component in high_risk[:5]:
            print(f"⚠️  {component['component_name']} ({component['component_type']})")
            print(f"   Location: {component['location']}")
            print(f"   Risk Level: {component['risk_level']}")
            print(f"   Risk Score: {component['risk_score']}")
            print(f"   Recent Incidents: {component['recent_incidents']}")
            print(f"   Sensor Alarms: {component['alarms']}")
            print(f"   Faulty Sensors: {component['faulty_sensors']}")
            print()
        
        # 3. Schedule Maintenance
        print_section("3. SCHEDULE PREVENTIVE MAINTENANCE")
        
        if priorities:
            # Schedule maintenance for top priority component
            top_component = priorities[0]
            scheduled_date = datetime.now() + timedelta(days=7)
            
            maintenance_id = maintenance_service.schedule_preventive_maintenance(
                component_id=top_component['component_id'],
                component_type=top_component['component_type'],
                maintenance_type="preventive_inspection",
                scheduled_date=scheduled_date,
                duration_hours=8,
                notes=f"Scheduled due to {top_component['incident_count']} recent incidents"
            )
            
            print(f"✅ Scheduled maintenance: {maintenance_id}")
            print(f"   Component: {top_component['component_name']}")
            print(f"   Type: Preventive Inspection")
            print(f"   Date: {scheduled_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Duration: 8 hours")
        
        # 4. Get Maintenance Calendar
        print_section("4. MAINTENANCE CALENDAR (Next 30 Days)")
        calendar = maintenance_service.get_maintenance_calendar()
        
        if calendar:
            print(f"Scheduled maintenance activities: {len(calendar)}\n")
            for activity in calendar:
                print(f"📅 {activity['maintenance_type']}")
                print(f"   Component: {activity['component_name']} ({activity['component_type']})")
                print(f"   Date: {activity['scheduled_date']}")
                print(f"   Duration: {activity['duration_hours']} hours")
                print(f"   Location: {activity['location']}")
                print(f"   Status: {activity['status']}")
                print()
        else:
            print("No maintenance scheduled in the next 30 days")
        
        # 5. Assess Maintenance Impact
        print_section("5. MAINTENANCE IMPACT ASSESSMENT")
        
        if priorities:
            component = priorities[0]
            impact = maintenance_service.assess_maintenance_impact(
                component['component_id'],
                component['component_type']
            )
            
            print(f"Impact of taking {component['component_name']} offline:\n")
            print(f"Component Type: {impact['component_type']}")
            print(f"Current Status: {impact['current_status']}")
            print(f"Location: {impact['location']}")
            print(f"Directly Affected Customers: {impact['directly_affected_customers']}")
            print(f"Total Affected Customers: {impact['total_affected_customers']}")
            print(f"Total Affected Load: {impact['total_affected_load_mw']:.2f} MW")
            
            if impact['affected_customer_list']:
                print(f"\nTop affected customers:")
                for customer in sorted(
                    impact['affected_customer_list'],
                    key=lambda x: x['consumption_mw'],
                    reverse=True
                )[:5]:
                    print(f"  • {customer['name']} ({customer['type']}): {customer['consumption_mw']:.2f} MW")
        
        # 6. Optimize Maintenance Schedule
        print_section("6. OPTIMIZED MAINTENANCE SCHEDULE")
        optimized = maintenance_service.optimize_maintenance_schedule()
        
        print(f"Generated optimized schedule for {len(optimized)} components:\n")
        for item in optimized[:5]:
            component = item['component']
            impact = item['impact']
            
            print(f"🔧 {component['component_name']}")
            print(f"   Priority: {component['priority']}")
            print(f"   Priority Score: {component['priority_score']}")
            print(f"   Suggested Date: {item['suggested_date']}")
            print(f"   Duration: {item['suggested_duration_hours']} hours")
            print(f"   Affected Customers: {impact['total_affected_customers']}")
            print(f"   Affected Load: {impact['total_affected_load_mw']:.2f} MW")
            print(f"   Has Conflicts: {'Yes' if item['has_conflicts'] else 'No'}")
            print()
        
        # 7. Predict Failure Risk
        print_section("7. FAILURE RISK PREDICTION")
        failure_risks = fault_service.predict_failure_risk()
        
        print(f"Components at risk of failure: {len(failure_risks)}\n")
        for component in failure_risks[:10]:
            print(f"{'🔴' if component['risk_level'] == 'IMMINENT' else '🟡'} "
                  f"{component['component_name']} ({component['component_type']})")
            print(f"   Location: {component['location']}")
            print(f"   Status: {component['status']}")
            print(f"   Risk Level: {component['risk_level']}")
            print(f"   Risk Score: {component['failure_risk_score']}")
            print(f"   Recent Incidents: {component['recent_incidents']}")
            print(f"   Sensor Alarms: {component['alarm_count']}/{component['total_sensors']}")
            print(f"   Recommendation: {component['recommendation']}")
            print()
        
        # 8. Get Comprehensive Recommendations
        print_section("8. COMPREHENSIVE MAINTENANCE RECOMMENDATIONS")
        recommendations = maintenance_service.get_maintenance_recommendations()
        
        summary = recommendations['summary']
        print("Summary:")
        print(f"  • Components needing maintenance: {summary['components_needing_maintenance']}")
        print(f"  • High-risk components: {summary['high_risk_count']}")
        print(f"  • Require immediate action: {summary['recommended_immediate_action']}")
        
        print("\nTop Priorities:")
        for component in recommendations['priorities'][:5]:
            print(f"  {component['component_name']}: Priority Score {component['priority_score']}")
        
        print("\nCritical Risk Components:")
        critical = [c for c in recommendations['high_risk_components'] 
                   if c['risk_level'] == 'CRITICAL']
        if critical:
            for component in critical[:3]:
                print(f"  ⚠️  {component['component_name']}")
                print(f"      Risk Score: {component['risk_score']}")
                print(f"      Recent Incidents: {component['recent_incidents']}")
        else:
            print("  ✅ No critical risk components")
        
        # 9. Check Maintenance Conflicts
        print_section("9. CHECK SCHEDULING CONFLICTS")
        
        if priorities:
            component = priorities[0]
            proposed_date = datetime.now() + timedelta(days=14)
            
            conflicts = maintenance_service.check_maintenance_conflicts(
                component['component_id'],
                component['component_type'],
                proposed_date,
                duration_hours=8
            )
            
            print(f"Checking conflicts for {component['component_name']}")
            print(f"Proposed date: {proposed_date.strftime('%Y-%m-%d %H:%M')}\n")
            
            if conflicts:
                print(f"Found {len(conflicts)} conflicts:\n")
                for conflict in conflicts:
                    print(f"  ⚠️  {conflict['conflicting_component_name']}")
                    print(f"      Scheduled: {conflict['scheduled_date']}")
                    print(f"      Duration: {conflict['duration_hours']} hours")
            else:
                print("✅ No scheduling conflicts found")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ENERGY GRID MAINTENANCE SCHEDULING DEMONSTRATION")
    print("=" * 80)
    
    main()
    
    print("\n" + "=" * 80)
    print("Demonstration Complete!")
    print("=" * 80 + "\n")
