"""Billing operations example demonstrating billing and payment processing."""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.billing_repo import BillingRepository
from src.repositories.customer_repo import CustomerRepository
from src.services.billing_service import BillingService


def main():
    """Demonstrate billing operations."""
    
    print("=" * 60)
    print("Utility Network Operations - Billing Operations Example")
    print("=" * 60)
    
    conn = Neo4jConnection()
    billing_repo = BillingRepository(conn)
    customer_repo = CustomerRepository(conn)
    billing_service = BillingService(billing_repo, customer_repo)
    
    # Get sample customer
    customers = conn.execute_query("MATCH (c:Customer) RETURN c.id as id LIMIT 1")
    if not customers:
        print("✗ No customers found")
        return
    
    customer_id = customers[0]['id']
    
    # 1. Generate Monthly Bill
    print(f"\n1. Generating Monthly Bill for {customer_id}")
    print("-" * 60)
    
    bill_data = billing_service.generate_monthly_bills()
    print(f"✓ Generated {len(bill_data['bills_created'])} bills")
    print(f"Total Revenue: ${bill_data['total_revenue']:,.2f}")
    
    # 2. Calculate Bill for Customer
    print(f"\n2. Calculating Bill for {customer_id}")
    print("-" * 60)
    
    bill = billing_service.calculate_bill_for_customer(customer_id, consumption_liters=350)
    
    print(f"Consumption: {bill['consumption_liters']} liters")
    print(f"Base Amount: ${bill['base_amount']:.2f}")
    
    if bill.get('tiered_breakdown'):
        print("\nTiered Breakdown:")
        for tier in bill['tiered_breakdown']:
            print(f"  {tier['tier_name']}: {tier['liters']}L @ ${tier['rate']:.4f}/L = ${tier['amount']:.2f}")
    
    print(f"\nSubtotal: ${bill['subtotal']:.2f}")
    print(f"Taxes: ${bill['taxes']:.2f}")
    print(f"Total Amount: ${bill['total_amount']:.2f}")
    print(f"Due Date: {bill['due_date']}")
    
    # 3. Process Payment
    print("\n3. Processing Payment")
    print("-" * 60)
    
    # Get unpaid bill
    unpaid = billing_repo.get_unpaid_bills(limit=1)
    if unpaid:
        bill_id = unpaid[0]['id']
        amount = unpaid[0]['amount_due']
        
        payment = billing_service.process_payment(
            bill_id=bill_id,
            payment_amount=amount,
            payment_method="credit_card"
        )
        
        print(f"✓ Payment processed for bill {bill_id}")
        print(f"Amount: ${payment['amount_paid']:.2f}")
        print(f"Method: {payment['payment_method']}")
        print(f"New Status: {payment['new_status']}")
    
    # 4. Customer Billing Summary
    print(f"\n4. Customer Billing Summary ({customer_id})")
    print("-" * 60)
    
    summary = billing_service.get_customer_billing_summary(customer_id)
    
    print(f"Account Balance: ${summary['account_balance']:.2f}")
    print(f"Total Billed: ${summary['total_billed']:.2f}")
    print(f"Total Paid: ${summary['total_paid']:.2f}")
    print(f"Outstanding Amount: ${summary['outstanding_amount']:.2f}")
    
    print(f"\nBilling History: {summary['total_bills']} bills")
    print(f"  - Paid: {summary['paid_bills']}")
    print(f"  - Unpaid: {summary['unpaid_bills']}")
    print(f"  - Overdue: {summary['overdue_bills']}")
    
    if summary.get('payment_history'):
        print("\nRecent Payments:")
        for payment in summary['payment_history'][:3]:
            print(f"  - {payment['date']}: ${payment['amount']:.2f} ({payment['method']})")
    
    # 5. Overdue Accounts Report
    print("\n5. Overdue Accounts Report")
    print("-" * 60)
    
    overdue_report = billing_service.get_overdue_accounts_report()
    
    print(f"Total Overdue Accounts: {overdue_report['total_overdue']}")
    print(f"Total Overdue Amount: ${overdue_report['total_overdue_amount']:,.2f}")
    print(f"Avg Days Overdue: {overdue_report['avg_days_overdue']:.1f}")
    
    if overdue_report.get('accounts'):
        print("\nTop Overdue Accounts:")
        for account in overdue_report['accounts'][:5]:
            print(f"\n  Customer: {account['customer_id']}")
            print(f"  Amount: ${account['overdue_amount']:.2f}")
            print(f"  Days Overdue: {account['days_overdue']}")
            print(f"  Bills: {account['overdue_bills']}")
    
    # 6. Billing Analytics
    print("\n6. Billing Analytics")
    print("-" * 60)
    
    analytics = billing_service.get_billing_analytics()
    
    print(f"Total Revenue: ${analytics['total_revenue']:,.2f}")
    print(f"Collection Rate: {analytics['collection_rate']:.1f}%")
    print(f"Avg Bill Amount: ${analytics['avg_bill_amount']:.2f}")
    
    print("\nRevenue by Customer Type:")
    for ctype in analytics['revenue_by_type']:
        print(f"  {ctype['type']}: ${ctype['revenue']:,.2f} ({ctype['percentage']:.1f}%)")
    
    print("\nMonthly Trends:")
    for month in analytics['monthly_trends'][:3]:
        print(f"  {month['month']}: ${month['revenue']:,.2f} ({month['bills']} bills)")
    
    print("\n" + "=" * 60)
    print("✓ Billing operations demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
