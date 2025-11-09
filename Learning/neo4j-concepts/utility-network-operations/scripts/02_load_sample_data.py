"""Script to load sample data for utility network operations."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.models.pipeline import PipelineSegment, PipelineType, PipelineStatus, PipeMaterial
from src.models.meter import Meter, MeterType, MeterStatus
from src.models.customer import Customer, CustomerType, CustomerStatus
from src.models.service_request import ServiceRequest, RequestType, RequestStatus, RequestPriority
from src.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from src.repositories.infrastructure_repo import InfrastructureRepository
from src.repositories.customer_repo import CustomerRepository
from src.repositories.incident_repo import IncidentRepository
from src.repositories.billing_repo import BillingRepository


def load_sample_data():
    """Load comprehensive sample data for utility network."""
    
    conn = Neo4jConnection()
    infra_repo = InfrastructureRepository(conn)
    customer_repo = CustomerRepository(conn)
    incident_repo = IncidentRepository(conn)
    billing_repo = BillingRepository(conn)
    
    print("Loading Sample Data for Utility Network Operations...")
    print("=" * 60)
    
    # 1. Create Pipeline Network
    print("\n1. Creating Pipeline Network...")
    pipelines = []
    regions = ["North", "South", "East", "West", "Central"]
    
    for i in range(100):
        region = random.choice(regions)
        pipeline = PipelineSegment(
            id=f"PIPE-{i+1:04d}",
            type=random.choice(list(PipelineType)),
            diameter_mm=random.choice([100, 150, 200, 300, 400, 600]),
            length_m=random.randint(50, 500),
            material=random.choice(list(PipeMaterial)),
            installation_date=datetime.now() - timedelta(days=random.randint(365, 7300)),  # 1-20 years
            status=random.choice(list(PipelineStatus)),
            max_pressure_psi=random.randint(60, 150),
            current_pressure_psi=random.randint(50, 140),
            max_flow_rate_lpm=random.randint(1000, 10000),
            current_flow_rate_lpm=random.randint(500, 9000),
            latitude=37.7749 + random.uniform(-0.5, 0.5),
            longitude=-122.4194 + random.uniform(-0.5, 0.5),
            region=region
        )
        pipeline_id = infra_repo.create_pipeline(pipeline)
        pipelines.append(pipeline_id)
    
    # Connect pipelines (create network topology)
    connections = 0
    for i in range(len(pipelines) - 1):
        if random.random() < 0.7:  # 70% connection probability
            infra_repo.connect_pipelines(pipelines[i], pipelines[i+1])
            connections += 1
    
    # Add some cross-connections
    for _ in range(20):
        pipe1 = random.choice(pipelines)
        pipe2 = random.choice(pipelines)
        if pipe1 != pipe2:
            try:
                infra_repo.connect_pipelines(pipe1, pipe2)
                connections += 1
            except:
                pass
    
    print(f"   ✓ Created {len(pipelines)} pipeline segments")
    print(f"   ✓ Created {connections} connections")
    
    # 2. Create Storage Tanks
    print("\n2. Creating Storage Tanks...")
    tanks = []
    for i in range(10):
        capacity = random.choice([10000, 20000, 50000, 100000])
        current = random.randint(int(capacity * 0.3), int(capacity * 0.9))
        tank_data = {
            "id": f"TANK-{i+1:03d}",
            "name": f"Storage Tank {i+1}",
            "capacity_liters": capacity,
            "current_level_liters": current,
            "latitude": 37.7749 + random.uniform(-0.5, 0.5),
            "longitude": -122.4194 + random.uniform(-0.5, 0.5),
            "region": random.choice(regions),
            "type": random.choice(["Water", "Gas"])
        }
        tank_id = infra_repo.create_storage_tank(tank_data)
        tanks.append(tank_id)
        
        # Connect tank to nearby pipelines
        nearby_pipe = random.choice(pipelines)
        infra_repo.connect_tank_to_pipeline(tank_id, nearby_pipe)
    
    print(f"   ✓ Created {len(tanks)} storage tanks")
    
    # 3. Create Customers
    print("\n3. Creating Customers...")
    customers = []
    cities = ["San Francisco", "Oakland", "San Jose", "Berkeley", "Palo Alto"]
    
    for i in range(200):
        customer = Customer(
            id=f"CUST-{i+1:05d}",
            name=f"Customer {i+1}",
            type=random.choice(list(CustomerType)),
            status=random.choice(list(CustomerStatus)),
            email=f"customer{i+1}@example.com",
            phone=f"+1-555-{random.randint(1000, 9999)}",
            address=f"{random.randint(100, 9999)} Main Street",
            city=random.choice(cities),
            state="CA",
            zip_code=f"9{random.randint(4000, 4999)}",
            latitude=37.7749 + random.uniform(-0.5, 0.5),
            longitude=-122.4194 + random.uniform(-0.5, 0.5),
            registration_date=datetime.now() - timedelta(days=random.randint(30, 1825)),  # 1 month - 5 years
            last_payment_date=datetime.now() - timedelta(days=random.randint(0, 90)) if random.random() < 0.9 else None
        )
        customer_id = customer_repo.create_customer(customer)
        customers.append(customer_id)
    
    print(f"   ✓ Created {len(customers)} customers")
    
    # 4. Create and Link Meters
    print("\n4. Creating Meters...")
    meters = []
    for i in range(150):
        meter = Meter(
            id=f"METER-{i+1:05d}",
            serial_number=f"SN-{random.randint(100000, 999999)}",
            type=random.choice(list(MeterType)),
            status=random.choice(list(MeterStatus)),
            installation_date=datetime.now() - timedelta(days=random.randint(30, 1825)),
            last_reading_date=datetime.now() - timedelta(hours=random.randint(0, 48)),
            latitude=37.7749 + random.uniform(-0.5, 0.5),
            longitude=-122.4194 + random.uniform(-0.5, 0.5),
            battery_level=random.randint(10, 100),
            signal_strength=random.randint(50, 100)
        )
        meter_id = infra_repo.create_meter(meter)
        meters.append(meter_id)
        
        # Link meter to customer
        customer_id = random.choice(customers)
        infra_repo.link_meter_to_customer(meter_id, customer_id)
        
        # Link meter to pipeline
        pipeline_id = random.choice(pipelines)
        infra_repo.link_meter_to_pipeline(meter_id, pipeline_id)
    
    print(f"   ✓ Created {len(meters)} meters")
    
    # 5. Generate Consumption Data
    print("\n5. Generating Consumption History...")
    consumption_records = 0
    for customer_id in customers[:100]:  # First 100 customers
        # Generate 6 months of monthly consumption
        for month in range(6):
            consumption_date = datetime.now() - timedelta(days=30 * month)
            consumption = random.randint(50, 500)  # liters
            customer_repo.record_consumption(
                customer_id=customer_id,
                consumption_liters=consumption,
                consumption_date=consumption_date
            )
            consumption_records += 1
    
    print(f"   ✓ Generated {consumption_records} consumption records")
    
    # 6. Generate Meter Readings
    print("\n6. Generating Meter Readings...")
    reading_count = 0
    for meter_id in meters[:100]:  # First 100 meters
        # Generate 30 days of hourly readings
        for hours_ago in range(0, 720, 24):  # Daily readings for 30 days
            reading_date = datetime.now() - timedelta(hours=hours_ago)
            value = random.uniform(0, 1000)
            
            infra_repo.update_meter_reading(
                meter_id=meter_id,
                reading_value=value,
                reading_date=reading_date
            )
            reading_count += 1
    
    print(f"   ✓ Generated {reading_count} meter readings")
    
    # 7. Create Incidents
    print("\n7. Creating Incidents...")
    incidents = []
    for i in range(30):
        incident = Incident(
            id=f"INC-{i+1:05d}",
            type=random.choice(list(IncidentType)),
            severity=random.choice(list(IncidentSeverity)),
            status=random.choice(list(IncidentStatus)),
            description=f"Sample incident {i+1}",
            reported_date=datetime.now() - timedelta(days=random.randint(0, 30)),
            response_date=datetime.now() - timedelta(days=random.randint(0, 29)) if random.random() < 0.8 else None,
            resolution_date=datetime.now() - timedelta(days=random.randint(0, 28)) if random.random() < 0.5 else None,
            latitude=37.7749 + random.uniform(-0.5, 0.5),
            longitude=-122.4194 + random.uniform(-0.5, 0.5),
            customers_affected=random.randint(1, 50),
            estimated_water_loss_liters=random.randint(0, 10000) if random.random() < 0.5 else 0
        )
        incident_id = incident_repo.create_incident(incident)
        incidents.append(incident_id)
        
        # Link to infrastructure
        if random.random() < 0.7:
            pipeline_id = random.choice(pipelines)
            incident_repo.link_incident_to_infrastructure(incident_id, pipeline_id, "PipelineSegment")
        
        # Link to customers
        affected_count = random.randint(1, 5)
        for _ in range(affected_count):
            customer_id = random.choice(customers)
            incident_repo.link_incident_to_customer(incident_id, customer_id)
    
    print(f"   ✓ Created {len(incidents)} incidents")
    
    # 8. Create Service Requests
    print("\n8. Creating Service Requests...")
    service_requests = []
    for i in range(50):
        sr = ServiceRequest(
            id=f"SR-{i+1:05d}",
            customer_id=random.choice(customers),
            type=random.choice(list(RequestType)),
            priority=random.choice(list(RequestPriority)),
            status=random.choice(list(RequestStatus)),
            description=f"Sample service request {i+1}",
            created_date=datetime.now() - timedelta(days=random.randint(0, 60)),
            assigned_date=datetime.now() - timedelta(days=random.randint(0, 59)) if random.random() < 0.7 else None,
            completed_date=datetime.now() - timedelta(days=random.randint(0, 58)) if random.random() < 0.4 else None
        )
        sr_id = incident_repo.create_service_request(sr)
        service_requests.append(sr_id)
    
    print(f"   ✓ Created {len(service_requests)} service requests")
    
    # 9. Generate Bills
    print("\n9. Generating Bills...")
    bills = []
    for customer_id in customers[:100]:  # First 100 customers
        # Generate 3 months of bills
        for month in range(3):
            bill_date = datetime.now() - timedelta(days=30 * month)
            consumption = random.randint(50, 500)
            amount = consumption * 0.05  # $0.05 per liter
            
            bill = {
                "customer_id": customer_id,
                "billing_period_start": bill_date - timedelta(days=30),
                "billing_period_end": bill_date,
                "consumption_liters": consumption,
                "amount_due": amount,
                "due_date": bill_date + timedelta(days=15),
                "status": random.choice(["paid", "unpaid", "overdue"])
            }
            bill_id = billing_repo.create_bill(bill)
            bills.append(bill_id)
            
            # Record payment for some bills
            if bill["status"] == "paid":
                billing_repo.record_payment(
                    bill_id=bill_id,
                    payment_amount=amount,
                    payment_method=random.choice(["credit_card", "bank_transfer", "cash"])
                )
    
    print(f"   ✓ Generated {len(bills)} bills")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Sample data loading complete!")
    print("\nSummary:")
    print(f"  - Pipeline Segments: {len(pipelines)}")
    print(f"  - Pipeline Connections: {connections}")
    print(f"  - Storage Tanks: {len(tanks)}")
    print(f"  - Customers: {len(customers)}")
    print(f"  - Meters: {len(meters)}")
    print(f"  - Consumption Records: {consumption_records}")
    print(f"  - Meter Readings: {reading_count}")
    print(f"  - Incidents: {len(incidents)}")
    print(f"  - Service Requests: {len(service_requests)}")
    print(f"  - Bills: {len(bills)}")
    print("\nNext steps:")
    print("  1. Run: python scripts/03_verify_setup.py")
    print("  2. Run: python scripts/04_generate_consumption_data.py")


if __name__ == "__main__":
    try:
        load_sample_data()
    except Exception as e:
        print(f"\n✗ Error loading sample data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
