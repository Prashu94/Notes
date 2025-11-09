"""Script to generate realistic consumption data with patterns."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import math

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.connection import Neo4jConnection
from src.repositories.customer_repo import CustomerRepository
from src.repositories.infrastructure_repo import InfrastructureRepository


def generate_consumption_data(months: int = 12):
    """
    Generate realistic consumption data with seasonal patterns, daily variations,
    and anomalies for testing analytics features.
    
    Args:
        months: Number of months of data to generate
    """
    
    conn = Neo4jConnection()
    customer_repo = CustomerRepository(conn)
    infra_repo = InfrastructureRepository(conn)
    
    print(f"Generating {months} months of consumption data...")
    print("=" * 60)
    
    # Get all customers
    query = "MATCH (c:Customer) RETURN c.id as id, c.type as type"
    customers = conn.execute_query(query)
    
    if not customers:
        print("✗ No customers found. Run 02_load_sample_data.py first.")
        return
    
    print(f"\nFound {len(customers)} customers")
    
    # Get all meters
    query = "MATCH (m:Meter) RETURN m.id as id"
    meters = conn.execute_query(query)
    
    print(f"Found {len(meters)} meters")
    
    # Generate consumption patterns
    print(f"\nGenerating consumption data for {months} months...")
    
    total_records = 0
    anomaly_count = 0
    
    for customer in customers:
        customer_id = customer["id"]
        customer_type = customer["type"]
        
        # Base consumption varies by customer type
        if customer_type == "residential":
            base_consumption = random.randint(100, 300)  # liters/day
            variability = 0.3  # 30% variation
        elif customer_type == "commercial":
            base_consumption = random.randint(500, 1500)
            variability = 0.4
        else:  # industrial
            base_consumption = random.randint(2000, 5000)
            variability = 0.5
        
        # Generate daily consumption for each month
        for month in range(months):
            days_in_month = 30
            month_start = datetime.now() - timedelta(days=30 * (months - month))
            
            for day in range(days_in_month):
                consumption_date = month_start + timedelta(days=day)
                
                # Seasonal variation (sinusoidal pattern)
                season_factor = 1 + 0.2 * math.sin(2 * math.pi * (month / 12))
                
                # Weekly variation (higher on weekends for residential)
                day_of_week = consumption_date.weekday()
                if customer_type == "residential" and day_of_week >= 5:
                    weekly_factor = 1.2
                else:
                    weekly_factor = 1.0
                
                # Random daily variation
                random_factor = 1 + random.uniform(-variability, variability)
                
                # Calculate daily consumption
                daily_consumption = base_consumption * season_factor * weekly_factor * random_factor
                
                # Introduce anomalies (5% chance)
                is_anomaly = random.random() < 0.05
                if is_anomaly:
                    anomaly_type = random.choice(["spike", "drop", "zero"])
                    if anomaly_type == "spike":
                        daily_consumption *= random.uniform(2.0, 4.0)  # Sudden spike
                    elif anomaly_type == "drop":
                        daily_consumption *= random.uniform(0.1, 0.3)  # Sudden drop
                    else:  # zero
                        daily_consumption = 0  # No consumption (leak or meter issue)
                    anomaly_count += 1
                
                # Record consumption
                customer_repo.record_consumption(
                    customer_id=customer_id,
                    consumption_liters=int(daily_consumption),
                    consumption_date=consumption_date
                )
                total_records += 1
        
        # Progress indicator
        if (customers.index(customer) + 1) % 20 == 0:
            print(f"   Processed {customers.index(customer) + 1}/{len(customers)} customers...")
    
    print(f"\n✓ Generated {total_records:,} consumption records")
    print(f"✓ Introduced {anomaly_count} anomalies for testing")
    
    # Generate meter readings
    print("\nGenerating meter readings...")
    reading_count = 0
    
    for meter in meters:
        meter_id = meter["id"]
        
        # Generate hourly readings for the last 30 days
        for hour in range(24 * 30):
            reading_date = datetime.now() - timedelta(hours=hour)
            
            # Simulate realistic meter readings (cumulative)
            base_reading = 1000 + (hour * random.uniform(1, 5))
            
            # Add some noise
            reading_value = base_reading + random.uniform(-10, 10)
            
            # Occasional anomalies (stale readings, spikes)
            if random.random() < 0.02:
                if random.random() < 0.5:
                    # Stale reading (same as previous)
                    reading_value = base_reading
                else:
                    # Spike
                    reading_value *= random.uniform(1.5, 2.0)
            
            infra_repo.update_meter_reading(
                meter_id=meter_id,
                reading_value=reading_value,
                reading_date=reading_date
            )
            reading_count += 1
        
        # Progress indicator
        if (meters.index(meter) + 1) % 20 == 0:
            print(f"   Processed {meters.index(meter) + 1}/{len(meters)} meters...")
    
    print(f"\n✓ Generated {reading_count:,} meter readings")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Consumption data generation complete!")
    print("\nData Characteristics:")
    print(f"  - Time Period: {months} months")
    print(f"  - Consumption Records: {total_records:,}")
    print(f"  - Meter Readings: {reading_count:,}")
    print(f"  - Anomalies: {anomaly_count}")
    print("\nPatterns Included:")
    print("  - Seasonal variations (sinusoidal)")
    print("  - Weekly patterns (weekend spikes for residential)")
    print("  - Random daily variations")
    print("  - Anomalies (spikes, drops, zero consumption)")
    print("\nThis data can be used to test:")
    print("  - Consumption analytics")
    print("  - Anomaly detection algorithms")
    print("  - Forecasting models")
    print("  - Peer comparison features")


def generate_pressure_data(days: int = 30):
    """Generate realistic pressure data for pipeline monitoring."""
    
    conn = Neo4jConnection()
    
    print(f"\nGenerating {days} days of pressure data...")
    
    # Get all pipelines
    query = "MATCH (p:PipelineSegment) RETURN p.id as id, p.max_pressure_psi as max_pressure"
    pipelines = conn.execute_query(query)
    
    if not pipelines:
        print("✗ No pipelines found.")
        return
    
    update_count = 0
    
    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        max_pressure = pipeline["max_pressure"] or 100
        
        # Generate hourly pressure readings
        for hour in range(24 * days):
            # Normal operation: 70-90% of max pressure
            normal_pressure = max_pressure * random.uniform(0.7, 0.9)
            
            # Daily variation (lower at night)
            hour_of_day = hour % 24
            if 0 <= hour_of_day < 6:
                normal_pressure *= 0.85  # Lower at night
            elif 6 <= hour_of_day < 9:
                normal_pressure *= 1.05  # Morning peak
            elif 17 <= hour_of_day < 21:
                normal_pressure *= 1.08  # Evening peak
            
            # Occasional anomalies (pressure drops indicating potential leaks)
            if random.random() < 0.01:
                normal_pressure *= random.uniform(0.4, 0.6)  # Pressure drop
            
            # Update pipeline pressure
            query = """
            MATCH (p:PipelineSegment {id: $pipeline_id})
            SET p.current_pressure_psi = $pressure,
                p.last_reading_date = $reading_date
            """
            conn.execute_query(query, {
                "pipeline_id": pipeline_id,
                "pressure": round(normal_pressure, 2),
                "reading_date": datetime.now() - timedelta(hours=hour)
            })
            update_count += 1
        
        if (pipelines.index(pipeline) + 1) % 20 == 0:
            print(f"   Processed {pipelines.index(pipeline) + 1}/{len(pipelines)} pipelines...")
    
    print(f"\n✓ Generated {update_count:,} pressure readings")


if __name__ == "__main__":
    try:
        # Generate consumption data
        generate_consumption_data(months=12)
        
        # Generate pressure data
        generate_pressure_data(days=30)
        
        print("\n" + "=" * 60)
        print("✓ All data generation complete!")
        print("\nNext steps:")
        print("  - Run python examples/03_leak_detection.py")
        print("  - Run python examples/04_consumption_analytics.py")
        
    except Exception as e:
        print(f"\n✗ Error generating data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
