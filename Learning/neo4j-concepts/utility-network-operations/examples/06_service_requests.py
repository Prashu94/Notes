"""Service request management example."""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.incident_repo import IncidentRepository
from src.repositories.customer_repo import CustomerRepository
from src.services.service_request_manager import ServiceRequestManager
from src.models.service_request import RequestType


def main():
    """Demonstrate service request management."""
    
    print("=" * 60)
    print("Utility Network Operations - Service Request Management")
    print("=" * 60)
    
    conn = Neo4jConnection()
    incident_repo = IncidentRepository(conn)
    customer_repo = CustomerRepository(conn)
    sr_manager = ServiceRequestManager(incident_repo, customer_repo)
    
    # Get sample customer
    customers = conn.execute_query("MATCH (c:Customer) RETURN c.id as id LIMIT 1")
    if not customers:
        print("✗ No customers found")
        return
    
    customer_id = customers[0]['id']
    
    # 1. Create Service Request
    print(f"\n1. Creating Service Request for {customer_id}")
    print("-" * 60)
    
    request_id = sr_manager.create_service_request(
        customer_id=customer_id,
        request_type=RequestType.LEAK_REPORT,
        description="Water leak reported at property",
        location="123 Main St"
    )
    
    print(f"✓ Created request: {request_id}")
    
    # 2. Get Pending Requests
    print("\n2. Pending Service Requests")
    print("-" * 60)
    
    pending = sr_manager.get_pending_requests()
    
    print(f"Total Pending: {len(pending)}")
    
    if pending:
        print("\nSample Requests:")
        for req in pending[:5]:
            print(f"\n  {req['id']}")
            print(f"  Type: {req['type']}")
            print(f"  Priority: {req['priority']}")
            print(f"  Customer: {req['customer_id']}")
            print(f"  Age: {req.get('age_hours', 0):.1f} hours")
    
    # 3. Auto-Assign Requests
    print("\n3. Auto-Assigning Requests")
    print("-" * 60)
    
    assigned = sr_manager.auto_assign_requests()
    
    print(f"✓ Assigned {assigned['assigned_count']} requests")
    
    if assigned.get('assignments'):
        print("\nAssignments:")
        for assignment in assigned['assignments'][:3]:
            print(f"  {assignment['request_id']} → Technician {assignment['technician_id']}")
    
    # 4. Service Request Dashboard
    print("\n4. Service Request Dashboard")
    print("-" * 60)
    
    dashboard = sr_manager.get_service_request_dashboard()
    
    print(f"Total Requests: {dashboard['total_requests']}")
    print(f"  - Open: {dashboard['open_requests']}")
    print(f"  - In Progress: {dashboard['in_progress']}")
    print(f"  - Completed: {dashboard['completed_requests']}")
    print(f"  - Cancelled: {dashboard['cancelled_requests']}")
    
    print(f"\nBy Priority:")
    for priority in dashboard['by_priority']:
        print(f"  {priority['priority']}: {priority['count']}")
    
    print(f"\nBy Type:")
    for rtype in dashboard['by_type']:
        print(f"  {rtype['type']}: {rtype['count']}")
    
    print(f"\nPerformance:")
    print(f"  Avg Response Time: {dashboard['avg_response_time_hours']:.1f} hours")
    print(f"  Avg Resolution Time: {dashboard['avg_resolution_time_hours']:.1f} hours")
    print(f"  SLA Compliance: {dashboard['sla_compliance_rate']:.1f}%")
    
    # 5. Overdue Requests
    print("\n5. Overdue Service Requests")
    print("-" * 60)
    
    overdue = sr_manager.get_overdue_requests()
    
    print(f"Overdue Requests: {len(overdue)}")
    
    if overdue:
        print("\nMost Critical:")
        for req in overdue[:3]:
            print(f"\n  {req['id']}")
            print(f"  Priority: {req['priority']}")
            print(f"  Created: {req['created_date']}")
            print(f"  Overdue By: {req['overdue_hours']:.1f} hours")
            print(f"  Urgency Score: {req.get('urgency_score', 0)}/100")
    
    # 6. SLA Compliance
    print("\n6. SLA Compliance Report")
    print("-" * 60)
    
    sla = sr_manager.calculate_sla_compliance()
    
    print(f"Overall Compliance: {sla['overall_compliance']:.1f}%")
    print(f"Met SLA: {sla['met_sla']} requests")
    print(f"Missed SLA: {sla['missed_sla']} requests")
    
    print(f"\nBy Priority:")
    for priority in sla['by_priority']:
        print(f"  {priority['priority']}: {priority['compliance']:.1f}%")
    
    print(f"\nBy Type:")
    for rtype in sla['by_type']:
        print(f"  {rtype['type']}: {rtype['compliance']:.1f}%")
    
    # 7. Common Issues
    print("\n7. Common Issues Report")
    print("-" * 60)
    
    issues = sr_manager.get_common_issues_report()
    
    print("Most Common Issues:")
    for issue in issues[:5]:
        print(f"\n  {issue['type']}")
        print(f"  Count: {issue['count']}")
        print(f"  Avg Resolution: {issue['avg_resolution_hours']:.1f} hours")
        print(f"  Trend: {issue.get('trend', 'stable')}")
    
    # 8. Technician Workload
    print("\n8. Technician Workload Analysis")
    print("-" * 60)
    
    workload = sr_manager.get_technician_workload()
    
    print(f"Total Technicians: {len(workload)}")
    
    if workload:
        print("\nWorkload Distribution:")
        for tech in workload[:5]:
            print(f"\n  Technician {tech['technician_id']}")
            print(f"  Active Requests: {tech['active_requests']}")
            print(f"  Completed (30d): {tech['completed_last_30_days']}")
            print(f"  Avg Completion Time: {tech['avg_completion_hours']:.1f} hours")
            print(f"  Utilization: {tech.get('utilization', 0):.1f}%")
    
    print("\n" + "=" * 60)
    print("✓ Service request management demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
