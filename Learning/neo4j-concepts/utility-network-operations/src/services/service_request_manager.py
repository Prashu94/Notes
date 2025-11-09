"""Service request manager for handling customer service tickets."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..repositories.incident_repo import IncidentRepository
from ..repositories.customer_repo import CustomerRepository
from ..models.service_request import ServiceRequest, RequestType, RequestStatus, RequestPriority


class ServiceRequestManager:
    """Service for managing customer service requests and work orders."""
    
    def __init__(self):
        """Initialize service with repositories."""
        self.incident_repo = IncidentRepository()
        self.customer_repo = CustomerRepository()
    
    def create_service_request(
        self,
        customer_id: str,
        request_type: str,
        description: str,
        priority: Optional[str] = None,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> str:
        """Create a new service request."""
        # Auto-determine priority if not provided
        if priority is None:
            priority = self._determine_priority(request_type)
        
        request_id = f"SR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        request = ServiceRequest(
            id=request_id,
            type=RequestType(request_type),
            priority=RequestPriority(priority),
            status=RequestStatus.PENDING,
            customer_id=customer_id,
            description=description,
            created_date=datetime.now(),
            location=location,
            latitude=latitude,
            longitude=longitude
        )
        
        return self.incident_repo.create_service_request(request)
    
    def _determine_priority(self, request_type: str) -> str:
        """Auto-determine priority based on request type."""
        critical_types = ['emergency', 'no_water', 'no_gas']
        high_types = ['leak_report', 'water_quality']
        
        if request_type in critical_types:
            return 'critical'
        elif request_type in high_types:
            return 'high'
        else:
            return 'medium'
    
    def assign_request(
        self,
        request_id: str,
        assigned_to: str,
        scheduled_date: Optional[datetime] = None,
        estimated_duration_hours: Optional[float] = None
    ) -> bool:
        """Assign service request to a technician/team."""
        success = self.incident_repo.assign_service_request(
            request_id,
            assigned_to,
            scheduled_date
        )
        
        if success and estimated_duration_hours:
            self.incident_repo.update_service_request(
                request_id,
                {'estimated_duration_hours': estimated_duration_hours}
            )
        
        return success
    
    def update_request_status(
        self,
        request_id: str,
        new_status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update service request status."""
        updates = {'status': new_status}
        
        if new_status == 'in_progress':
            # No additional fields needed
            pass
        elif new_status == 'on_hold' and notes:
            updates['notes'] = notes
        
        return self.incident_repo.update_service_request(request_id, updates)
    
    def complete_request(
        self,
        request_id: str,
        resolution_notes: str,
        actual_duration_hours: Optional[float] = None,
        customer_satisfaction: Optional[int] = None
    ) -> bool:
        """Complete a service request."""
        success = self.incident_repo.complete_service_request(
            request_id,
            resolution_notes,
            actual_duration_hours
        )
        
        if success and customer_satisfaction:
            self.incident_repo.update_service_request(
                request_id,
                {'customer_satisfaction': customer_satisfaction}
            )
        
        return success
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending (unassigned) requests sorted by priority."""
        return self.incident_repo.get_pending_service_requests()
    
    def get_overdue_requests(self) -> List[Dict[str, Any]]:
        """Get requests that are overdue based on SLA."""
        return self.incident_repo.get_overdue_service_requests()
    
    def get_customer_requests(
        self,
        customer_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get service request history for a customer."""
        return self.incident_repo.get_customer_service_requests(customer_id, limit)
    
    def get_service_request_dashboard(self) -> Dict[str, Any]:
        """Get dashboard view of service requests."""
        pending = self.incident_repo.get_pending_service_requests()
        overdue = self.incident_repo.get_overdue_service_requests()
        critical = self.incident_repo.get_service_requests_by_priority('critical')
        high = self.incident_repo.get_service_requests_by_priority('high')
        
        # Calculate average response time for recently completed requests
        stats = self.incident_repo.get_service_request_statistics(days=30)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'pending_requests': len(pending),
            'overdue_requests': len(overdue),
            'critical_priority': len(critical),
            'high_priority': len(high),
            'sla_metrics': {
                'avg_resolution_hours': stats.get('avg_resolution_hours', 0),
                'avg_customer_satisfaction': stats.get('avg_customer_satisfaction', 0),
                'resolution_rate_percent': stats.get('resolution_rate_percent', 0)
            },
            'top_pending': [
                {
                    'id': req['sr']['id'],
                    'type': req['sr']['type'],
                    'priority': req['sr']['priority'],
                    'customer_id': req['sr']['customer_id'],
                    'age_hours': req['age_hours'],
                    'description': req['sr']['description'][:100]
                }
                for req in pending[:10]
            ],
            'overdue_list': [
                {
                    'id': req['sr']['id'],
                    'type': req['sr']['type'],
                    'priority': req['sr']['priority'],
                    'hours_overdue': req['hours_overdue'],
                    'sla_hours': req['sla_hours']
                }
                for req in overdue[:10]
            ]
        }
    
    def get_technician_workload(self, technician_id: str) -> Dict[str, Any]:
        """Get workload summary for a technician."""
        # This would query service requests assigned to the technician
        # Simplified version:
        
        return {
            'technician_id': technician_id,
            'active_requests': 0,  # Would query from database
            'scheduled_today': 0,
            'total_estimated_hours': 0,
            'message': 'Technician workload tracking requires additional query implementation'
        }
    
    def auto_assign_requests(
        self,
        team_size: int = 5
    ) -> Dict[str, Any]:
        """
        Auto-assign pending requests to available technicians.
        This is a simplified version; real implementation would consider:
        - Technician location
        - Skills/specialization
        - Current workload
        - Request location
        """
        pending = self.incident_repo.get_pending_service_requests()
        
        if not pending:
            return {
                'message': 'No pending requests to assign',
                'assigned_count': 0
            }
        
        assigned_count = 0
        
        for idx, request in enumerate(pending[:20]):  # Limit to 20
            # Simple round-robin assignment
            technician_id = f"TECH-{(idx % team_size) + 1:03d}"
            
            success = self.assign_request(
                request['sr']['id'],
                technician_id,
                scheduled_date=datetime.now() + timedelta(hours=2)
            )
            
            if success:
                assigned_count += 1
        
        return {
            'message': f'Auto-assigned {assigned_count} requests',
            'assigned_count': assigned_count,
            'pending_remaining': len(pending) - assigned_count
        }
    
    def get_common_issues_report(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get report of most common service request types."""
        return self.incident_repo.get_most_common_issues(limit=10)
    
    def calculate_sla_compliance(self, days: int = 30) -> Dict[str, Any]:
        """Calculate SLA compliance metrics."""
        stats = self.incident_repo.get_service_request_statistics(days=days)
        
        # SLA targets by priority
        sla_targets = {
            'critical': 4,   # 4 hours
            'high': 48,      # 48 hours
            'medium': 120,   # 5 days
            'low': 240       # 10 days
        }
        
        return {
            'period_days': days,
            'total_requests': stats.get('total_requests', 0),
            'resolved_requests': stats.get('resolved', 0),
            'avg_resolution_hours': stats.get('avg_resolution_hours', 0),
            'resolution_rate': stats.get('resolution_rate_percent', 0),
            'sla_targets': sla_targets,
            'customer_satisfaction': stats.get('avg_customer_satisfaction', 0),
            'compliance_status': 'good' if stats.get('resolution_rate_percent', 0) > 85 else 'needs_improvement'
        }
    
    def escalate_request(
        self,
        request_id: str,
        escalation_reason: str
    ) -> bool:
        """Escalate a service request to higher priority."""
        request = self.incident_repo.get_service_request(request_id)
        if not request:
            return False
        
        current_priority = request['priority']
        
        # Escalate priority
        priority_order = ['low', 'medium', 'high', 'critical']
        current_idx = priority_order.index(current_priority)
        
        if current_idx < len(priority_order) - 1:
            new_priority = priority_order[current_idx + 1]
            
            return self.incident_repo.update_service_request(
                request_id,
                {
                    'priority': new_priority,
                    'escalated': True,
                    'escalation_reason': escalation_reason,
                    'escalation_date': datetime.now().isoformat()
                }
            )
        
        return False
    
    def link_request_to_incident(
        self,
        request_id: str,
        incident_id: str
    ) -> bool:
        """Link a service request to a related incident."""
        return self.incident_repo.link_service_request_to_incident(
            request_id,
            incident_id
        )
