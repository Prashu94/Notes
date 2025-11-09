// ===================================
// SAMPLE WATER NETWORK DATA
// ===================================
// This script creates a realistic water distribution network

// ===================================
// 1. CREATE STORAGE TANKS (Water Sources)
// ===================================

CREATE
  (tank1:StorageTank {
    id: 'TANK-001',
    name: 'North Reservoir',
    type: 'elevated',
    capacity_m3: 50000.0,
    current_level_m3: 45000.0,
    elevation_m: 150.0,
    status: 'operational',
    location: point({latitude: 40.7580, longitude: -73.9855}),
    commissioned_date: date('1995-06-15')
  }),
  (tank2:StorageTank {
    id: 'TANK-002',
    name: 'Central Reservoir',
    type: 'ground',
    capacity_m3: 75000.0,
    current_level_m3: 68000.0,
    elevation_m: 120.0,
    status: 'operational',
    location: point({latitude: 40.7480, longitude: -73.9755}),
    commissioned_date: date('2000-03-20')
  }),
  (tank3:StorageTank {
    id: 'TANK-003',
    name: 'South Reservoir',
    type: 'elevated',
    capacity_m3: 60000.0,
    current_level_m3: 55000.0,
    elevation_m: 140.0,
    status: 'operational',
    location: point({latitude: 40.7380, longitude: -73.9655}),
    commissioned_date: date('2005-08-10')
  });

// ===================================
// 2. CREATE PUMPING STATIONS
// ===================================

CREATE
  (pump1:PumpingStation {
    id: 'PUMP-001',
    name: 'North Main Pump',
    type: 'centrifugal',
    capacity_m3_per_hour: 500.0,
    pressure_bar: 6.5,
    power_kw: 150.0,
    status: 'operational',
    location: point({latitude: 40.7560, longitude: -73.9835}),
    efficiency_percent: 85.0,
    installed_date: date('2010-04-12')
  }),
  (pump2:PumpingStation {
    id: 'PUMP-002',
    name: 'Central Booster',
    type: 'multistage',
    capacity_m3_per_hour: 400.0,
    pressure_bar: 7.0,
    power_kw: 120.0,
    status: 'operational',
    location: point({latitude: 40.7460, longitude: -73.9735}),
    efficiency_percent: 88.0,
    installed_date: date('2012-09-25')
  }),
  (pump3:PumpingStation {
    id: 'PUMP-003',
    name: 'South Booster',
    type: 'centrifugal',
    capacity_m3_per_hour: 450.0,
    pressure_bar: 6.8,
    power_kw: 140.0,
    status: 'operational',
    location: point({latitude: 40.7360, longitude: -73.9635}),
    efficiency_percent: 86.0,
    installed_date: date('2015-06-18')
  });

// ===================================
// 3. CREATE PIPELINE SEGMENTS
// ===================================

CREATE
  // Main transmission pipelines
  (pipe1:PipelineSegment {
    id: 'PIPE-001',
    name: 'North Main Line',
    type: 'water',
    diameter_mm: 600.0,
    length_m: 2500.0,
    material: 'ductile_iron',
    pressure_rating_bar: 16.0,
    status: 'operational',
    region: 'North',
    start_location: point({latitude: 40.7580, longitude: -73.9855}),
    end_location: point({latitude: 40.7560, longitude: -73.9835}),
    installed_date: date('1995-06-15'),
    last_inspection_date: date('2024-05-20')
  }),
  (pipe2:PipelineSegment {
    id: 'PIPE-002',
    name: 'North Distribution A',
    type: 'water',
    diameter_mm: 400.0,
    length_m: 1800.0,
    material: 'ductile_iron',
    pressure_rating_bar: 16.0,
    status: 'operational',
    region: 'North',
    start_location: point({latitude: 40.7560, longitude: -73.9835}),
    end_location: point({latitude: 40.7540, longitude: -73.9815}),
    installed_date: date('1998-03-10'),
    last_inspection_date: date('2024-06-15')
  }),
  (pipe3:PipelineSegment {
    id: 'PIPE-003',
    name: 'North Distribution B',
    type: 'water',
    diameter_mm: 300.0,
    length_m: 1500.0,
    material: 'pvc',
    pressure_rating_bar: 12.0,
    status: 'operational',
    region: 'North',
    start_location: point({latitude: 40.7540, longitude: -73.9815}),
    end_location: point({latitude: 40.7520, longitude: -73.9795}),
    installed_date: date('2005-07-22'),
    last_inspection_date: date('2024-04-10')
  }),
  (pipe4:PipelineSegment {
    id: 'PIPE-004',
    name: 'Central Main Line',
    type: 'water',
    diameter_mm: 600.0,
    length_m: 2200.0,
    material: 'ductile_iron',
    pressure_rating_bar: 16.0,
    status: 'operational',
    region: 'Central',
    start_location: point({latitude: 40.7480, longitude: -73.9755}),
    end_location: point({latitude: 40.7460, longitude: -73.9735}),
    installed_date: date('2000-03-20'),
    last_inspection_date: date('2024-07-08')
  }),
  (pipe5:PipelineSegment {
    id: 'PIPE-005',
    name: 'Central Distribution A',
    type: 'water',
    diameter_mm: 400.0,
    length_m: 1600.0,
    material: 'ductile_iron',
    pressure_rating_bar: 16.0,
    status: 'operational',
    region: 'Central',
    start_location: point({latitude: 40.7460, longitude: -73.9735}),
    end_location: point({latitude: 40.7440, longitude: -73.9715}),
    installed_date: date('2002-11-15'),
    last_inspection_date: date('2024-05-30')
  }),
  (pipe6:PipelineSegment {
    id: 'PIPE-006',
    name: 'South Main Line',
    type: 'water',
    diameter_mm: 600.0,
    length_m: 2400.0,
    material: 'steel',
    pressure_rating_bar: 20.0,
    status: 'operational',
    region: 'South',
    start_location: point({latitude: 40.7380, longitude: -73.9655}),
    end_location: point({latitude: 40.7360, longitude: -73.9635}),
    installed_date: date('2005-08-10'),
    last_inspection_date: date('2024-08-12')
  }),
  (pipe7:PipelineSegment {
    id: 'PIPE-007',
    name: 'South Distribution A',
    type: 'water',
    diameter_mm: 350.0,
    length_m: 1700.0,
    material: 'pvc',
    pressure_rating_bar: 12.0,
    status: 'operational',
    region: 'South',
    start_location: point({latitude: 40.7360, longitude: -73.9635}),
    end_location: point({latitude: 40.7340, longitude: -73.9615}),
    installed_date: date('2008-04-18'),
    last_inspection_date: date('2024-03-25')
  }),
  (pipe8:PipelineSegment {
    id: 'PIPE-008',
    name: 'North-Central Connector',
    type: 'water',
    diameter_mm: 500.0,
    length_m: 3000.0,
    material: 'ductile_iron',
    pressure_rating_bar: 16.0,
    status: 'operational',
    region: 'North-Central',
    start_location: point({latitude: 40.7540, longitude: -73.9815}),
    end_location: point({latitude: 40.7460, longitude: -73.9735}),
    installed_date: date('2010-06-22'),
    last_inspection_date: date('2024-09-05')
  });

// ===================================
// 4. CREATE VALVES
// ===================================

CREATE
  (valve1:Valve {
    id: 'VALVE-001',
    name: 'North Main Valve',
    type: 'gate',
    diameter_mm: 600.0,
    status: 'open',
    position_percent: 100.0,
    location: point({latitude: 40.7570, longitude: -73.9845}),
    last_operated: datetime('2024-10-15T08:30:00')
  }),
  (valve2:Valve {
    id: 'VALVE-002',
    name: 'North Distribution Valve',
    type: 'butterfly',
    diameter_mm: 400.0,
    status: 'open',
    position_percent: 100.0,
    location: point({latitude: 40.7550, longitude: -73.9825}),
    last_operated: datetime('2024-09-20T14:15:00')
  }),
  (valve3:Valve {
    id: 'VALVE-003',
    name: 'Central Main Valve',
    type: 'gate',
    diameter_mm: 600.0,
    status: 'open',
    position_percent: 100.0,
    location: point({latitude: 40.7470, longitude: -73.9745}),
    last_operated: datetime('2024-10-01T10:00:00')
  });

// ===================================
// 5. CREATE SENSORS
// ===================================

CREATE
  (sensor1:Sensor {
    id: 'SENSOR-001',
    type: 'pressure',
    model: 'PressurePro-5000',
    status: 'active',
    location: point({latitude: 40.7560, longitude: -73.9835}),
    current_value: 6.5,
    unit: 'bar',
    threshold_min: 4.0,
    threshold_max: 10.0,
    last_reading_at: datetime('2024-11-09T10:30:00'),
    calibration_date: date('2024-06-01'),
    sampling_rate_hz: 0.1
  }),
  (sensor2:Sensor {
    id: 'SENSOR-002',
    type: 'flow',
    model: 'FlowMeter-3000',
    status: 'active',
    location: point({latitude: 40.7540, longitude: -73.9815}),
    current_value: 450.0,
    unit: 'm3/h',
    threshold_min: 100.0,
    threshold_max: 600.0,
    last_reading_at: datetime('2024-11-09T10:30:00'),
    calibration_date: date('2024-05-15'),
    sampling_rate_hz: 0.1
  }),
  (sensor3:Sensor {
    id: 'SENSOR-003',
    type: 'pressure',
    model: 'PressurePro-5000',
    status: 'active',
    location: point({latitude: 40.7460, longitude: -73.9735}),
    current_value: 7.0,
    unit: 'bar',
    threshold_min: 4.0,
    threshold_max: 10.0,
    last_reading_at: datetime('2024-11-09T10:30:00'),
    calibration_date: date('2024-07-10'),
    sampling_rate_hz: 0.1
  });

// ===================================
// 6. CREATE CUSTOMERS
// ===================================

CREATE
  (cust1:Customer {
    id: 'CUST-W-001',
    account_number: 'ACC-100001',
    name: 'North Residential Complex A',
    type: 'residential',
    status: 'active',
    region: 'North',
    address: '123 Main Street, Apt 1-50',
    location: point({latitude: 40.7525, longitude: -73.9800}),
    connection_date: date('2010-01-15'),
    average_consumption_m3: 250.0,
    num_units: 50,
    email: 'manager@northcomplex-a.com',
    phone: '+1-555-0101'
  }),
  (cust2:Customer {
    id: 'CUST-W-002',
    account_number: 'ACC-100002',
    name: 'Downtown Hotel',
    type: 'commercial',
    status: 'active',
    region: 'Central',
    address: '456 Business Ave',
    location: point({latitude: 40.7445, longitude: -73.9720}),
    connection_date: date('2005-06-20'),
    average_consumption_m3: 800.0,
    num_units: 1,
    email: 'facilities@downtownhotel.com',
    phone: '+1-555-0202'
  }),
  (cust3:Customer {
    id: 'CUST-W-003',
    account_number: 'ACC-100003',
    name: 'Manufacturing Plant Inc',
    type: 'industrial',
    status: 'active',
    region: 'South',
    address: '789 Industrial Blvd',
    location: point({latitude: 40.7345, longitude: -73.9620}),
    connection_date: date('2008-03-10'),
    average_consumption_m3: 2500.0,
    num_units: 1,
    email: 'utilities@manufacturing.com',
    phone: '+1-555-0303'
  }),
  (cust4:Customer {
    id: 'CUST-W-004',
    account_number: 'ACC-100004',
    name: 'Central Hospital',
    type: 'commercial',
    status: 'active',
    region: 'Central',
    address: '321 Healthcare Drive',
    location: point({latitude: 40.7450, longitude: -73.9725}),
    connection_date: date('2000-01-01'),
    average_consumption_m3: 1200.0,
    num_units: 1,
    email: 'facilities@centralhospital.org',
    phone: '+1-555-0404'
  }),
  (cust5:Customer {
    id: 'CUST-W-005',
    account_number: 'ACC-100005',
    name: 'North Single Family Home',
    type: 'residential',
    status: 'active',
    region: 'North',
    address: '555 Oak Lane',
    location: point({latitude: 40.7530, longitude: -73.9805}),
    connection_date: date('2015-09-01'),
    average_consumption_m3: 15.0,
    num_units: 1,
    email: 'john.doe@email.com',
    phone: '+1-555-0505'
  });

// ===================================
// 7. CREATE METERS
// ===================================

CREATE
  (meter1:Meter {
    id: 'METER-W-001',
    type: 'smart',
    model: 'SmartMeter-2000',
    status: 'active',
    location: point({latitude: 40.7525, longitude: -73.9800}),
    installed_date: date('2020-01-15'),
    last_reading: 12500.0,
    last_reading_at: datetime('2024-11-09T00:00:00'),
    unit: 'm3',
    accuracy_class: 'B'
  }),
  (meter2:Meter {
    id: 'METER-W-002',
    type: 'smart',
    model: 'SmartMeter-3000',
    status: 'active',
    location: point({latitude: 40.7445, longitude: -73.9720}),
    installed_date: date('2018-06-20'),
    last_reading: 45000.0,
    last_reading_at: datetime('2024-11-09T00:00:00'),
    unit: 'm3',
    accuracy_class: 'A'
  }),
  (meter3:Meter {
    id: 'METER-W-003',
    type: 'smart',
    model: 'IndustrialMeter-5000',
    status: 'active',
    location: point({latitude: 40.7345, longitude: -73.9620}),
    installed_date: date('2015-03-10'),
    last_reading: 125000.0,
    last_reading_at: datetime('2024-11-09T00:00:00'),
    unit: 'm3',
    accuracy_class: 'A'
  }),
  (meter4:Meter {
    id: 'METER-W-004',
    type: 'smart',
    model: 'SmartMeter-3000',
    status: 'active',
    location: point({latitude: 40.7450, longitude: -73.9725}),
    installed_date: date('2019-01-01'),
    last_reading: 68000.0,
    last_reading_at: datetime('2024-11-09T00:00:00'),
    unit: 'm3',
    accuracy_class: 'A'
  }),
  (meter5:Meter {
    id: 'METER-W-005',
    type: 'smart',
    model: 'SmartMeter-2000',
    status: 'active',
    location: point({latitude: 40.7530, longitude: -73.9805}),
    installed_date: date('2020-09-01'),
    last_reading: 850.0,
    last_reading_at: datetime('2024-11-09T00:00:00'),
    unit: 'm3',
    accuracy_class: 'B'
  });

// ===================================
// 8. CREATE RELATIONSHIPS
// ===================================

// Storage tanks to pumping stations
MATCH (tank:StorageTank {id: 'TANK-001'}), (pipe:PipelineSegment {id: 'PIPE-001'})
CREATE (tank)-[:SUPPLIES {flow_rate_m3h: 500.0, status: 'active'}]->(pipe);

MATCH (tank:StorageTank {id: 'TANK-002'}), (pipe:PipelineSegment {id: 'PIPE-004'})
CREATE (tank)-[:SUPPLIES {flow_rate_m3h: 400.0, status: 'active'}]->(pipe);

MATCH (tank:StorageTank {id: 'TANK-003'}), (pipe:PipelineSegment {id: 'PIPE-006'})
CREATE (tank)-[:SUPPLIES {flow_rate_m3h: 450.0, status: 'active'}]->(pipe);

// Pipeline connections
MATCH (p1:PipelineSegment {id: 'PIPE-001'}), (p2:PipelineSegment {id: 'PIPE-002'})
CREATE (p1)-[:CONNECTS_TO {joint_type: 'flanged', installed_date: date('1998-03-10')}]->(p2);

MATCH (p1:PipelineSegment {id: 'PIPE-002'}), (p2:PipelineSegment {id: 'PIPE-003'})
CREATE (p1)-[:CONNECTS_TO {joint_type: 'flanged', installed_date: date('2005-07-22')}]->(p2);

MATCH (p1:PipelineSegment {id: 'PIPE-004'}), (p2:PipelineSegment {id: 'PIPE-005'})
CREATE (p1)-[:CONNECTS_TO {joint_type: 'flanged', installed_date: date('2002-11-15')}]->(p2);

MATCH (p1:PipelineSegment {id: 'PIPE-006'}), (p2:PipelineSegment {id: 'PIPE-007'})
CREATE (p1)-[:CONNECTS_TO {joint_type: 'welded', installed_date: date('2008-04-18')}]->(p2);

MATCH (p1:PipelineSegment {id: 'PIPE-002'}), (p2:PipelineSegment {id: 'PIPE-008'})
CREATE (p1)-[:CONNECTS_TO {joint_type: 'flanged', installed_date: date('2010-06-22')}]->(p2);

MATCH (p1:PipelineSegment {id: 'PIPE-008'}), (p2:PipelineSegment {id: 'PIPE-005'})
CREATE (p1)-[:CONNECTS_TO {joint_type: 'flanged', installed_date: date('2010-06-22')}]->(p2);

// Valves control pipelines
MATCH (valve:Valve {id: 'VALVE-001'}), (pipe:PipelineSegment {id: 'PIPE-001'})
CREATE (valve)-[:CONTROLS {position: 'inline'}]->(pipe);

MATCH (valve:Valve {id: 'VALVE-002'}), (pipe:PipelineSegment {id: 'PIPE-002'})
CREATE (valve)-[:CONTROLS {position: 'inline'}]->(pipe);

MATCH (valve:Valve {id: 'VALVE-003'}), (pipe:PipelineSegment {id: 'PIPE-004'})
CREATE (valve)-[:CONTROLS {position: 'inline'}]->(pipe);

// Sensors monitor infrastructure
MATCH (sensor:Sensor {id: 'SENSOR-001'}), (pump:PumpingStation {id: 'PUMP-001'})
CREATE (sensor)-[:MONITORS {parameter: 'outlet_pressure', last_reading_at: datetime('2024-11-09T10:30:00')}]->(pump);

MATCH (sensor:Sensor {id: 'SENSOR-002'}), (pipe:PipelineSegment {id: 'PIPE-002'})
CREATE (sensor)-[:MONITORS {parameter: 'flow_rate', last_reading_at: datetime('2024-11-09T10:30:00')}]->(pipe);

MATCH (sensor:Sensor {id: 'SENSOR-003'}), (pump:PumpingStation {id: 'PUMP-002'})
CREATE (sensor)-[:MONITORS {parameter: 'outlet_pressure', last_reading_at: datetime('2024-11-09T10:30:00')}]->(pump);

// Meters measure customers
MATCH (meter:Meter {id: 'METER-W-001'}), (cust:Customer {id: 'CUST-W-001'})
CREATE (meter)-[:MEASURES {installation_date: date('2020-01-15')}]->(cust);

MATCH (meter:Meter {id: 'METER-W-002'}), (cust:Customer {id: 'CUST-W-002'})
CREATE (meter)-[:MEASURES {installation_date: date('2018-06-20')}]->(cust);

MATCH (meter:Meter {id: 'METER-W-003'}), (cust:Customer {id: 'CUST-W-003'})
CREATE (meter)-[:MEASURES {installation_date: date('2015-03-10')}]->(cust);

MATCH (meter:Meter {id: 'METER-W-004'}), (cust:Customer {id: 'CUST-W-004'})
CREATE (meter)-[:MEASURES {installation_date: date('2019-01-01')}]->(cust);

MATCH (meter:Meter {id: 'METER-W-005'}), (cust:Customer {id: 'CUST-W-005'})
CREATE (meter)-[:MEASURES {installation_date: date('2020-09-01')}]->(cust);

// ===================================
// Verification Query
// ===================================

// Count nodes and relationships
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC;
