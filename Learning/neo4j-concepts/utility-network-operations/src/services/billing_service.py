"""Billing service for billing and payment operations."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from ..repositories.billing_repo import BillingRepository
from ..repositories.customer_repo import CustomerRepository


class BillingService:
    """Service for billing operations and payment processing."""
    
    def __init__(self):
        """Initialize service with repositories."""
        self.billing_repo = BillingRepository()
        self.customer_repo = CustomerRepository()
    
    def generate_monthly_bills(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate bills for all customers for a given month.
        If year/month not provided, uses previous month.
        """
        if year is None or month is None:
            today = datetime.now()
            if today.month == 1:
                year = today.year - 1
                month = 12
            else:
                year = today.year
                month = today.month - 1
        
        # Rate structure
        tier_rates = {
            'residential': 0.05,  # $0.05 per m³
            'commercial': 0.08,   # $0.08 per m³
            'industrial': 0.06,   # $0.06 per m³
            'municipal': 0.04     # $0.04 per m³
        }
        
        bills_created = self.billing_repo.generate_monthly_bills(
            year=year,
            month=month,
            tier_rates=tier_rates
        )
        
        return {
            'period': f"{year}-{month:02d}",
            'bills_created': bills_created,
            'rates_applied': tier_rates
        }
    
    def calculate_bill_for_customer(
        self,
        customer_id: str,
        consumption: float,
        resource_type: str = 'water'
    ) -> Dict[str, Any]:
        """Calculate bill amount for a customer based on consumption."""
        customer = self.customer_repo.get_customer(customer_id)
        if not customer:
            return {'error': 'Customer not found'}
        
        customer_type = customer['type']
        
        # Base rates
        base_rates = {
            'water': {
                'residential': 0.05,
                'commercial': 0.08,
                'industrial': 0.06,
                'municipal': 0.04
            },
            'gas': {
                'residential': 0.12,
                'commercial': 0.15,
                'industrial': 0.10,
                'municipal': 0.08
            }
        }
        
        rates = base_rates.get(resource_type, base_rates['water'])
        base_rate = rates.get(customer_type, 0.05)
        
        # Calculate with tiered pricing for residential
        if customer_type == 'residential':
            amount = self._calculate_tiered_amount(consumption, base_rate)
        else:
            amount = consumption * base_rate
        
        # Add fixed charges
        fixed_charge = {
            'residential': 10.00,
            'commercial': 25.00,
            'industrial': 50.00,
            'municipal': 30.00
        }.get(customer_type, 10.00)
        
        total_amount = round(amount + fixed_charge, 2)
        
        return {
            'customer_id': customer_id,
            'customer_type': customer_type,
            'consumption': consumption,
            'resource_type': resource_type,
            'base_rate': base_rate,
            'variable_charges': round(amount, 2),
            'fixed_charges': fixed_charge,
            'total_amount': total_amount,
            'breakdown': self._get_tiered_breakdown(consumption, base_rate) if customer_type == 'residential' else None
        }
    
    def _calculate_tiered_amount(self, consumption: float, base_rate: float) -> float:
        """Calculate tiered pricing for residential customers."""
        amount = 0.0
        
        # Tier 1: 0-20 m³ at base rate
        if consumption <= 20:
            amount = consumption * base_rate
        else:
            amount = 20 * base_rate
            remaining = consumption - 20
            
            # Tier 2: 21-50 m³ at 1.2x base rate
            if remaining <= 30:
                amount += remaining * base_rate * 1.2
            else:
                amount += 30 * base_rate * 1.2
                
                # Tier 3: 51+ m³ at 1.5x base rate
                tier3 = remaining - 30
                amount += tier3 * base_rate * 1.5
        
        return amount
    
    def _get_tiered_breakdown(self, consumption: float, base_rate: float) -> List[Dict[str, Any]]:
        """Get detailed breakdown of tiered pricing."""
        breakdown = []
        
        # Tier 1
        tier1_consumption = min(consumption, 20)
        breakdown.append({
            'tier': 1,
            'range': '0-20 m³',
            'consumption': tier1_consumption,
            'rate': base_rate,
            'amount': round(tier1_consumption * base_rate, 2)
        })
        
        if consumption > 20:
            # Tier 2
            tier2_consumption = min(consumption - 20, 30)
            breakdown.append({
                'tier': 2,
                'range': '21-50 m³',
                'consumption': tier2_consumption,
                'rate': base_rate * 1.2,
                'amount': round(tier2_consumption * base_rate * 1.2, 2)
            })
        
        if consumption > 50:
            # Tier 3
            tier3_consumption = consumption - 50
            breakdown.append({
                'tier': 3,
                'range': '51+ m³',
                'consumption': tier3_consumption,
                'rate': base_rate * 1.5,
                'amount': round(tier3_consumption * base_rate * 1.5, 2)
            })
        
        return breakdown
    
    def process_payment(
        self,
        bill_id: str,
        amount_paid: float,
        payment_method: str = 'online',
        payment_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Process a payment for a bill."""
        success = self.billing_repo.record_payment(
            bill_id=bill_id,
            amount_paid=amount_paid,
            payment_date=payment_date,
            payment_method=payment_method
        )
        
        if success:
            bill = self.billing_repo.get_bill(bill_id)
            return {
                'success': True,
                'bill_id': bill_id,
                'amount_paid': amount_paid,
                'payment_method': payment_method,
                'bill_status': bill['status'] if bill else 'unknown',
                'remaining_balance': round(bill['amount'] - bill.get('amount_paid', 0), 2) if bill else 0
            }
        else:
            return {
                'success': False,
                'error': 'Payment processing failed'
            }
    
    def get_customer_billing_summary(
        self,
        customer_id: str,
        months: int = 12
    ) -> Dict[str, Any]:
        """Get billing summary for a customer."""
        bills = self.billing_repo.get_customer_bills(customer_id, limit=months)
        
        if not bills:
            return {
                'customer_id': customer_id,
                'total_bills': 0,
                'message': 'No billing history found'
            }
        
        total_billed = sum(b['amount'] for b in bills)
        total_paid = sum(b.get('amount_paid', 0) for b in bills)
        unpaid_bills = [b for b in bills if b['status'] == 'unpaid']
        
        return {
            'customer_id': customer_id,
            'period_months': months,
            'total_bills': len(bills),
            'total_billed': round(total_billed, 2),
            'total_paid': round(total_paid, 2),
            'total_outstanding': round(total_billed - total_paid, 2),
            'unpaid_bill_count': len(unpaid_bills),
            'average_bill_amount': round(total_billed / len(bills), 2),
            'payment_rate_percent': round((total_paid / total_billed) * 100, 1) if total_billed > 0 else 0,
            'recent_bills': [
                {
                    'bill_id': b['id'],
                    'period_end': b['billing_period_end'],
                    'amount': b['amount'],
                    'status': b['status'],
                    'due_date': b['due_date']
                }
                for b in bills[:6]
            ]
        }
    
    def get_overdue_accounts_report(self) -> List[Dict[str, Any]]:
        """Get report of accounts with overdue payments."""
        overdue_bills = self.billing_repo.get_overdue_bills()
        
        # Group by customer
        customer_overdue = {}
        for bill in overdue_bills:
            customer_id = bill['customer_id']
            if customer_id not in customer_overdue:
                customer_overdue[customer_id] = {
                    'customer_id': customer_id,
                    'customer_name': bill['customer_name'],
                    'overdue_bills': [],
                    'total_overdue': 0.0
                }
            
            customer_overdue[customer_id]['overdue_bills'].append({
                'bill_id': bill['b']['id'],
                'amount': bill['b']['amount'],
                'due_date': bill['b']['due_date'],
                'days_overdue': bill['days_overdue']
            })
            customer_overdue[customer_id]['total_overdue'] += bill['b']['amount']
        
        # Sort by total overdue amount
        report = sorted(
            customer_overdue.values(),
            key=lambda x: x['total_overdue'],
            reverse=True
        )
        
        return report
    
    def get_billing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive billing analytics."""
        stats = self.billing_repo.get_billing_statistics()
        revenue_trend = self.billing_repo.get_revenue_by_period(months=12)
        payment_methods = self.billing_repo.get_payment_methods_summary()
        
        return {
            'overall_statistics': stats,
            'revenue_trend_12_months': revenue_trend,
            'payment_methods': payment_methods,
            'collection_rate': stats.get('collection_rate_percent', 0),
            'overdue_rate': round(
                (stats.get('overdue_amount', 0) / stats.get('total_billed', 1)) * 100,
                1
            ) if stats.get('total_billed', 0) > 0 else 0
        }
    
    def send_payment_reminder(
        self,
        customer_id: str,
        days_before_due: int = 7
    ) -> Dict[str, Any]:
        """
        Send payment reminder to customer.
        (In real system, this would trigger email/SMS)
        """
        unpaid_bills = self.billing_repo.get_unpaid_bills(customer_id)
        
        upcoming_due = []
        for bill in unpaid_bills:
            due_date = datetime.fromisoformat(bill['b']['due_date'])
            days_until_due = (due_date - datetime.now()).days
            
            if 0 <= days_until_due <= days_before_due:
                upcoming_due.append({
                    'bill_id': bill['b']['id'],
                    'amount': bill['b']['amount'],
                    'due_date': bill['b']['due_date'],
                    'days_until_due': days_until_due
                })
        
        if upcoming_due:
            return {
                'customer_id': customer_id,
                'reminder_sent': True,
                'bills': upcoming_due,
                'total_amount_due': sum(b['amount'] for b in upcoming_due),
                'message': f"Payment reminder sent for {len(upcoming_due)} bill(s)"
            }
        else:
            return {
                'customer_id': customer_id,
                'reminder_sent': False,
                'message': 'No bills due in the reminder window'
            }
    
    def apply_late_fee(
        self,
        bill_id: str,
        late_fee_percent: float = 5.0
    ) -> bool:
        """Apply late fee to an overdue bill."""
        bill = self.billing_repo.get_bill(bill_id)
        if not bill:
            return False
        
        if bill['status'] != 'unpaid':
            return False
        
        due_date = datetime.fromisoformat(bill['due_date'])
        if datetime.now() <= due_date:
            return False
        
        # Calculate late fee
        late_fee = bill['amount'] * (late_fee_percent / 100)
        new_amount = bill['amount'] + late_fee
        
        # Update bill
        return self.billing_repo.update_bill(
            bill_id,
            {
                'amount': round(new_amount, 2),
                'late_fee_applied': late_fee,
                'late_fee_date': datetime.now().isoformat()
            }
        )
