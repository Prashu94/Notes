"""
Water Distribution Network Data Model

This file documents the data model for water/gas utility network management.
"""

# =============================================================================
# NODE LABELS AND PROPERTIES
# =============================================================================

"""
STORAGE TANK NODES
------------------
Label: StorageTank
Properties:
  - id: STRING (unique identifier)
  - name: STRING (tank name)
  - capacity_m3: FLOAT (storage capacity in cubic meters)
  - current_level_m3: FLOAT (current water level)
  - type: STRING (elevated, ground, underground)
  - location: POINT (geographic coordinates)
  - material: STRING (steel, concrete, composite)
  - install_date: DATE
  - status: STRING (operational, maintenance, offline)

Example:
CREATE (t:StorageTank {
    id: 'TANK-001',
    name: 'North Reservoir',
    capacity_m3: 50000.0,
    current_level_m3: 42000.0,
    type: 'ground',
    location: point({latitude: 40.7589, longitude: -73.9851}),
    material: 'concrete',
    install_date: date('2015-06-15'),
    status: 'operational'
})
"""

"""
PUMPING STATION NODES
---------------------
Label: PumpingStation
Properties:
  - id: STRING (unique identifier)
  - name: STRING (station name)
  - capacity_m3_per_hour: FLOAT (pumping capacity)
  - power_consumption_kw: FLOAT (electrical power requirement)
  - num_pumps: INTEGER (number of pumps)
  - location: POINT (geographic coordinates)
  - operator: STRING (operating company)
  - efficiency_percent: FLOAT (operational efficiency)
  - status: STRING (operational, maintenance, offline)

Example:
CREATE (ps:PumpingStation {
    id: 'PUMP-001',
    name: 'Central Pumping Station',
    capacity_m3_per_hour: 500.0,
    power_consumption_kw: 150.0,
    num_pumps: 3,
    location: point({latitude: 40.7489, longitude: -73.9951}),
    operator: 'City Water Authority',
    efficiency_percent: 88.5,
    status: 'operational'
})
"""

"""
PIPELINE NODES
--------------
Label: Pipeline
Properties:
  - id: STRING (unique identifier)
  - name: STRING (pipeline identifier)
  - diameter_mm: INTEGER (pipe diameter in millimeters)
  - length_m: FLOAT (pipeline length in meters)
  - material: STRING (PVC, steel, cast_iron, HDPE)
  - install_date: DATE
  - pressure_rating_bar: FLOAT (maximum pressure rating)
  - flow_rate_m3_per_hour: FLOAT (design flow rate)
  - status: STRING (operational, maintenance, offline)

Example:
CREATE (p:Pipeline {
    id: 'PIPE-001',
    name: 'Main Distribution Line 1',
    diameter_mm: 600,
    length_m: 2500.0,
    material: 'steel',
    install_date: date('2018-03-20'),
    pressure_rating_bar: 16.0,
    flow_rate_m3_per_hour: 300.0,
    status: 'operational'
})
"""

"""
VALVE NODES
-----------
Label: Valve
Properties:
  - id: STRING (unique identifier)
  - type: STRING (gate, ball, butterfly, check)
  - size_mm: INTEGER (valve size in millimeters)
  - location: POINT (geographic coordinates)
  - is_automated: BOOLEAN (true if remotely controlled)
  - current_position: STRING (open, closed, partial)
  - install_date: DATE
  - status: STRING (operational, maintenance, offline)

Example:
CREATE (v:Valve {
    id: 'VALVE-001',
    type: 'gate',
    size_mm: 400,
    location: point({latitude: 40.7489, longitude: -73.9851}),
    is_automated: true,
    current_position: 'open',
    install_date: date('2019-11-10'),
    status: 'operational'
})
"""

"""
SENSOR/IOT DEVICE NODES
-----------------------
Label: Sensor
Properties:
  - id: STRING (unique identifier)
  - type: STRING (pressure, flow, level, quality, temperature)
  - model: STRING (sensor model number)
  - install_date: DATE
  - last_calibration: DATE
  - reading_interval_seconds: INTEGER
  - location: POINT (geographic coordinates)
  - status: STRING (operational, maintenance, offline)

Example:
CREATE (s:Sensor {
    id: 'SENSOR-001',
    type: 'pressure',
    model: 'PRE-5000X',
    install_date: date('2021-01-15'),
    last_calibration: date('2024-01-10'),
    reading_interval_seconds: 60,
    location: point({latitude: 40.7389, longitude: -73.9751}),
    status: 'operational'
})
"""

"""
CUSTOMER NODES
--------------
Label: Customer
Properties:
  - id: STRING (unique identifier)
  - name: STRING (customer name)
  - type: STRING (residential, commercial, industrial)
  - account_number: STRING
  - address: STRING
  - location: POINT (geographic coordinates)
  - average_consumption_m3: FLOAT (monthly average)
  - connection_date: DATE
  - meter_id: STRING (water meter identifier)

Example:
CREATE (c:Customer {
    id: 'CUST-001',
    name: 'Downtown Office Complex',
    type: 'commercial',
    account_number: 'ACC-12345',
    address: '123 Main Street',
    location: point({latitude: 40.7289, longitude: -73.9651}),
    average_consumption_m3: 1500.0,
    connection_date: date('2010-05-20'),
    meter_id: 'METER-001'
})
"""

"""
SMART METER NODES
-----------------
Label: SmartMeter
Properties:
  - id: STRING (unique identifier)
  - model: STRING (meter model)
  - install_date: DATE
  - last_reading_date: DATETIME
  - reading_m3: FLOAT (current reading)
  - flow_rate_m3_per_hour: FLOAT (current flow)
  - status: STRING (operational, maintenance, offline)

Example:
CREATE (m:SmartMeter {
    id: 'METER-001',
    model: 'WATER-SMART-3000',
    install_date: date('2020-08-15'),
    last_reading_date: datetime('2024-01-15T14:30:00'),
    reading_m3: 12500.5,
    flow_rate_m3_per_hour: 2.5,
    status: 'operational'
})
"""

# =============================================================================
# RELATIONSHIP TYPES
# =============================================================================

"""
SUPPLIES RELATIONSHIP
--------------------
Type: SUPPLIES
From: StorageTank | PumpingStation
To: Pipeline | Customer | PumpingStation
Properties:
  - flow_rate_m3_per_hour: FLOAT
  - pressure_bar: FLOAT
  - priority: INTEGER (1=high, 5=low)

Example:
MATCH (tank:StorageTank {id: 'TANK-001'})
MATCH (pipe:Pipeline {id: 'PIPE-001'})
CREATE (tank)-[:SUPPLIES {
    flow_rate_m3_per_hour: 250.0,
    pressure_bar: 8.5,
    priority: 1
}]->(pipe)
"""

"""
CONNECTS_TO RELATIONSHIP
-----------------------
Type: CONNECTS_TO
From: Pipeline
To: Pipeline | PumpingStation | StorageTank | Customer
Properties:
  - junction_type: STRING (tee, cross, reducer)
  - install_date: DATE

Example:
MATCH (p1:Pipeline {id: 'PIPE-001'})
MATCH (p2:Pipeline {id: 'PIPE-002'})
CREATE (p1)-[:CONNECTS_TO {
    junction_type: 'tee',
    install_date: date('2018-03-25')
}]->(p2)
"""

"""
CONTROLS RELATIONSHIP
--------------------
Type: CONTROLS
From: Valve
To: Pipeline
Properties:
  - position: STRING (open, closed, partial)
  - control_type: STRING (manual, automated)

Example:
MATCH (valve:Valve {id: 'VALVE-001'})
MATCH (pipe:Pipeline {id: 'PIPE-001'})
CREATE (valve)-[:CONTROLS {
    position: 'open',
    control_type: 'automated'
}]->(pipe)
"""

"""
MONITORS RELATIONSHIP
--------------------
Type: MONITORS
From: Sensor
To: Pipeline | PumpingStation | StorageTank | Valve
Properties:
  - measurement_type: STRING (pressure, flow, level, quality)
  - last_reading: FLOAT
  - last_reading_time: DATETIME
  - unit: STRING (bar, m3/h, m3, pH, etc.)

Example:
MATCH (sensor:Sensor {id: 'SENSOR-001'})
MATCH (pipe:Pipeline {id: 'PIPE-001'})
CREATE (sensor)-[:MONITORS {
    measurement_type: 'pressure',
    last_reading: 8.2,
    last_reading_time: datetime(),
    unit: 'bar'
}]->(pipe)
"""

"""
MEASURES RELATIONSHIP
--------------------
Type: MEASURES
From: SmartMeter
To: Customer
Properties:
  - billing_cycle: STRING (monthly)
  - last_bill_date: DATE
  - current_reading_m3: FLOAT

Example:
MATCH (meter:SmartMeter {id: 'METER-001'})
MATCH (customer:Customer {id: 'CUST-001'})
CREATE (meter)-[:MEASURES {
    billing_cycle: 'monthly',
    last_bill_date: date('2024-01-01'),
    current_reading_m3: 12500.5
}]->(customer)
"""

# =============================================================================
# COMMON QUERY PATTERNS
# =============================================================================

"""
1. Find all components in the water network:
   MATCH (n)
   WHERE n:StorageTank OR n:PumpingStation OR n:Pipeline OR n:Valve
   RETURN labels(n)[0] as type, count(n) as count

2. Trace water flow from source to customer:
   MATCH path = (source:StorageTank)-[:SUPPLIES|CONNECTS_TO*]->(customer:Customer)
   RETURN path

3. Find all sensors monitoring a pipeline:
   MATCH (s:Sensor)-[r:MONITORS]->(p:Pipeline {id: 'PIPE-001'})
   RETURN s.type, s.id, r.measurement_type, r.last_reading

4. Identify critical infrastructure (highly connected):
   MATCH (n)
   WHERE n:PumpingStation OR n:StorageTank
   OPTIONAL MATCH (n)-[r]-(connected)
   WITH n, count(r) as connection_count
   WHERE connection_count > 3
   RETURN n.name, labels(n)[0] as type, connection_count
   ORDER BY connection_count DESC

5. Find customers with high consumption:
   MATCH (c:Customer)
   WHERE c.average_consumption_m3 > 1000
   RETURN c.name, c.type, c.average_consumption_m3
   ORDER BY c.average_consumption_m3 DESC
"""
