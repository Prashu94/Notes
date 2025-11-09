// ===================================
// SAMPLE DATA FOR ENERGY GRID
// ===================================
// This script creates a realistic sample energy grid network

// Clear existing data (use with caution!)
// MATCH (n) DETACH DELETE n;

// ===================================
// 1. CREATE LOCATIONS
// ===================================

CREATE
  (loc1:Location {
    id: 'LOC-001',
    name: 'Northern Region',
    type: 'region',
    coordinates: point({latitude: 40.7128, longitude: -74.0060}),
    population: 2500000,
    area_sq_km: 5000.0
  }),
  (loc2:Location {
    id: 'LOC-002',
    name: 'Central Region',
    type: 'region',
    coordinates: point({latitude: 41.8781, longitude: -87.6298}),
    population: 1800000,
    area_sq_km: 3500.0
  }),
  (loc3:Location {
    id: 'LOC-003',
    name: 'Southern Region',
    type: 'region',
    coordinates: point({latitude: 29.7604, longitude: -95.3698}),
    population: 2200000,
    area_sq_km: 4200.0
  }),
  (loc4:Location {
    id: 'LOC-004',
    name: 'Eastern Region',
    type: 'region',
    coordinates: point({latitude: 39.9526, longitude: -75.1652}),
    population: 1600000,
    area_sq_km: 2800.0
  });

// ===================================
// 2. CREATE POWER PLANTS
// ===================================

CREATE
  (pp1:PowerPlant {
    id: 'PP-001',
    name: 'Riverside Nuclear Plant',
    type: 'nuclear',
    capacity_mw: 1200.0,
    efficiency_percent: 33.0,
    status: 'operational',
    commissioned_date: date('2005-06-15'),
    operator: 'National Power Corp',
    location: point({latitude: 40.8128, longitude: -74.1060}),
    emissions_tons_per_year: 0.0,
    description: 'Large-scale nuclear power generation facility'
  }),
  (pp2:PowerPlant {
    id: 'PP-002',
    name: 'Sunset Solar Farm',
    type: 'solar',
    capacity_mw: 500.0,
    efficiency_percent: 22.0,
    status: 'operational',
    commissioned_date: date('2018-03-20'),
    operator: 'Green Energy Inc',
    location: point({latitude: 29.8604, longitude: -95.4698}),
    emissions_tons_per_year: 0.0,
    description: 'Solar photovoltaic power generation'
  }),
  (pp3:PowerPlant {
    id: 'PP-003',
    name: 'Mountain Wind Farm',
    type: 'wind',
    capacity_mw: 350.0,
    efficiency_percent: 35.0,
    status: 'operational',
    commissioned_date: date('2016-09-10'),
    operator: 'Wind Power LLC',
    location: point({latitude: 41.9781, longitude: -87.7298}),
    emissions_tons_per_year: 0.0,
    description: 'Onshore wind turbine array'
  }),
  (pp4:PowerPlant {
    id: 'PP-004',
    name: 'Central Coal Plant',
    type: 'coal',
    capacity_mw: 800.0,
    efficiency_percent: 38.0,
    status: 'operational',
    commissioned_date: date('1985-11-05'),
    operator: 'Traditional Energy Co',
    location: point({latitude: 41.7781, longitude: -87.5298}),
    emissions_tons_per_year: 4500000.0,
    description: 'Coal-fired steam turbine power plant'
  }),
  (pp5:PowerPlant {
    id: 'PP-005',
    name: 'Riverside Hydro Dam',
    type: 'hydro',
    capacity_mw: 600.0,
    efficiency_percent: 90.0,
    status: 'operational',
    commissioned_date: date('1965-07-22'),
    operator: 'Hydro Power Authority',
    location: point({latitude: 40.0526, longitude: -75.2652}),
    emissions_tons_per_year: 0.0,
    description: 'Hydroelectric dam and reservoir'
  }),
  (pp6:PowerPlant {
    id: 'PP-006',
    name: 'Bay Natural Gas Plant',
    type: 'natural_gas',
    capacity_mw: 950.0,
    efficiency_percent: 58.0,
    status: 'operational',
    commissioned_date: date('2010-04-12'),
    operator: 'National Power Corp',
    location: point({latitude: 39.8526, longitude: -75.0652}),
    emissions_tons_per_year: 1200000.0,
    description: 'Combined cycle gas turbine plant'
  });

// ===================================
// 3. CREATE SUBSTATIONS
// ===================================

CREATE
  (ss1:Substation {
    id: 'SS-001',
    name: 'North Main Substation',
    voltage_kv: 500.0,
    capacity_mva: 2000.0,
    type: 'transmission',
    status: 'operational',
    region: 'Northern',
    location: point({latitude: 40.7528, longitude: -74.0460}),
    commissioned_date: date('2000-03-15'),
    num_transformers: 4
  }),
  (ss2:Substation {
    id: 'SS-002',
    name: 'North Distribution Hub',
    voltage_kv: 230.0,
    capacity_mva: 800.0,
    type: 'distribution',
    status: 'operational',
    region: 'Northern',
    location: point({latitude: 40.7328, longitude: -74.0260}),
    commissioned_date: date('2005-06-20'),
    num_transformers: 3
  }),
  (ss3:Substation {
    id: 'SS-003',
    name: 'Central Main Substation',
    voltage_kv: 500.0,
    capacity_mva: 1800.0,
    type: 'transmission',
    status: 'operational',
    region: 'Central',
    location: point({latitude: 41.9081, longitude: -87.6598}),
    commissioned_date: date('1998-09-10'),
    num_transformers: 4
  }),
  (ss4:Substation {
    id: 'SS-004',
    name: 'Central Distribution Hub',
    voltage_kv: 230.0,
    capacity_mva: 700.0,
    type: 'distribution',
    status: 'operational',
    region: 'Central',
    location: point({latitude: 41.8481, longitude: -87.5998}),
    commissioned_date: date('2002-11-25'),
    num_transformers: 2
  }),
  (ss5:Substation {
    id: 'SS-005',
    name: 'South Main Substation',
    voltage_kv: 500.0,
    capacity_mva: 1900.0,
    type: 'transmission',
    status: 'operational',
    region: 'Southern',
    location: point({latitude: 29.8004, longitude: -95.4098}),
    commissioned_date: date('2003-04-18'),
    num_transformers: 4
  }),
  (ss6:Substation {
    id: 'SS-006',
    name: 'South Distribution Hub',
    voltage_kv: 230.0,
    capacity_mva: 900.0,
    type: 'distribution',
    status: 'operational',
    region: 'Southern',
    location: point({latitude: 29.7204, longitude: -95.3298}),
    commissioned_date: date('2008-07-30'),
    num_transformers: 3
  }),
  (ss7:Substation {
    id: 'SS-007',
    name: 'East Main Substation',
    voltage_kv: 500.0,
    capacity_mva: 1600.0,
    type: 'transmission',
    status: 'operational',
    region: 'Eastern',
    location: point({latitude: 39.9926, longitude: -75.2052}),
    commissioned_date: date('2001-02-14'),
    num_transformers: 3
  }),
  (ss8:Substation {
    id: 'SS-008',
    name: 'East Distribution Hub',
    voltage_kv: 230.0,
    capacity_mva: 600.0,
    type: 'distribution',
    status: 'operational',
    region: 'Eastern',
    location: point({latitude: 39.9126, longitude: -75.1252}),
    commissioned_date: date('2006-08-22'),
    num_transformers: 2
  });

// ===================================
// 4. CREATE CUSTOMERS
// ===================================

CREATE
  (c1:Customer {
    id: 'CUST-001',
    name: 'Northside Manufacturing',
    type: 'industrial',
    region: 'Northern',
    location: point({latitude: 40.7428, longitude: -74.0360}),
    contract_start_date: date('2015-01-01'),
    average_consumption_kwh: 500000.0,
    peak_demand_kw: 750.0,
    tariff_plan: 'industrial-standard'
  }),
  (c2:Customer {
    id: 'CUST-002',
    name: 'Downtown Shopping Mall',
    type: 'commercial',
    region: 'Northern',
    location: point({latitude: 40.7228, longitude: -74.0160}),
    contract_start_date: date('2010-06-15'),
    average_consumption_kwh: 150000.0,
    peak_demand_kw: 220.0,
    tariff_plan: 'commercial-premium'
  }),
  (c3:Customer {
    id: 'CUST-003',
    name: 'Residential Complex A',
    type: 'residential',
    region: 'Northern',
    location: point({latitude: 40.7128, longitude: -73.9960}),
    contract_start_date: date('2012-03-20'),
    average_consumption_kwh: 25000.0,
    peak_demand_kw: 40.0,
    tariff_plan: 'residential-tiered'
  }),
  (c4:Customer {
    id: 'CUST-004',
    name: 'Central Steel Works',
    type: 'industrial',
    region: 'Central',
    location: point({latitude: 41.8581, longitude: -87.6098}),
    contract_start_date: date('2008-09-10'),
    average_consumption_kwh: 800000.0,
    peak_demand_kw: 1200.0,
    tariff_plan: 'industrial-heavy'
  }),
  (c5:Customer {
    id: 'CUST-005',
    name: 'Central Hospital',
    type: 'commercial',
    region: 'Central',
    location: point({latitude: 41.8681, longitude: -87.6198}),
    contract_start_date: date('2005-11-25'),
    average_consumption_kwh: 200000.0,
    peak_demand_kw: 300.0,
    tariff_plan: 'commercial-critical'
  }),
  (c6:Customer {
    id: 'CUST-006',
    name: 'South Chemical Plant',
    type: 'industrial',
    region: 'Southern',
    location: point({latitude: 29.7504, longitude: -95.3598}),
    contract_start_date: date('2013-04-18'),
    average_consumption_kwh: 950000.0,
    peak_demand_kw: 1400.0,
    tariff_plan: 'industrial-heavy'
  }),
  (c7:Customer {
    id: 'CUST-007',
    name: 'South University Campus',
    type: 'commercial',
    region: 'Southern',
    location: point({latitude: 29.7304, longitude: -95.3398}),
    contract_start_date: date('2000-08-01'),
    average_consumption_kwh: 180000.0,
    peak_demand_kw: 280.0,
    tariff_plan: 'commercial-standard'
  }),
  (c8:Customer {
    id: 'CUST-008',
    name: 'East Data Center',
    type: 'industrial',
    region: 'Eastern',
    location: point({latitude: 39.9626, longitude: -75.1552}),
    contract_start_date: date('2017-02-14'),
    average_consumption_kwh: 1200000.0,
    peak_demand_kw: 1800.0,
    tariff_plan: 'industrial-premium'
  }),
  (c9:Customer {
    id: 'CUST-009',
    name: 'Residential Complex B',
    type: 'residential',
    region: 'Eastern',
    location: point({latitude: 39.9426, longitude: -75.1352}),
    contract_start_date: date('2014-06-22'),
    average_consumption_kwh: 30000.0,
    peak_demand_kw: 50.0,
    tariff_plan: 'residential-tiered'
  }),
  (c10:Customer {
    id: 'CUST-010',
    name: 'East Office Park',
    type: 'commercial',
    region: 'Eastern',
    location: point({latitude: 39.9226, longitude: -75.1152}),
    contract_start_date: date('2016-09-30'),
    average_consumption_kwh: 120000.0,
    peak_demand_kw: 180.0,
    tariff_plan: 'commercial-standard'
  });

// ===================================
// 5. CREATE GENERATION RELATIONSHIPS
// ===================================

MATCH (pp:PowerPlant {id: 'PP-001'}), (ss:Substation {id: 'SS-001'})
CREATE (pp)-[:GENERATES {
  active: true,
  average_output_mw: 1100.0,
  established_date: date('2005-06-15')
}]->(ss);

MATCH (pp:PowerPlant {id: 'PP-002'}), (ss:Substation {id: 'SS-005'})
CREATE (pp)-[:GENERATES {
  active: true,
  average_output_mw: 420.0,
  established_date: date('2018-03-20')
}]->(ss);

MATCH (pp:PowerPlant {id: 'PP-003'}), (ss:Substation {id: 'SS-003'})
CREATE (pp)-[:GENERATES {
  active: true,
  average_output_mw: 280.0,
  established_date: date('2016-09-10')
}]->(ss);

MATCH (pp:PowerPlant {id: 'PP-004'}), (ss:Substation {id: 'SS-003'})
CREATE (pp)-[:GENERATES {
  active: true,
  average_output_mw: 750.0,
  established_date: date('1985-11-05')
}]->(ss);

MATCH (pp:PowerPlant {id: 'PP-005'}), (ss:Substation {id: 'SS-007'})
CREATE (pp)-[:GENERATES {
  active: true,
  average_output_mw: 550.0,
  established_date: date('1965-07-22')
}]->(ss);

MATCH (pp:PowerPlant {id: 'PP-006'}), (ss:Substation {id: 'SS-007'})
CREATE (pp)-[:GENERATES {
  active: true,
  average_output_mw: 900.0,
  established_date: date('2010-04-12')
}]->(ss);

// ===================================
// 6. CREATE TRANSMISSION RELATIONSHIPS
// ===================================

// Northern to Central
MATCH (ss1:Substation {id: 'SS-001'}), (ss2:Substation {id: 'SS-003'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 1500.0,
  distance_km: 120.5,
  line_id: 'TL-001',
  loss_percent: 2.3,
  status: 'operational'
}]->(ss2);

// Central to Southern
MATCH (ss1:Substation {id: 'SS-003'}), (ss2:Substation {id: 'SS-005'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 1400.0,
  distance_km: 185.7,
  line_id: 'TL-002',
  loss_percent: 2.8,
  status: 'operational'
}]->(ss2);

// Southern to Eastern
MATCH (ss1:Substation {id: 'SS-005'}), (ss2:Substation {id: 'SS-007'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 1300.0,
  distance_km: 210.3,
  line_id: 'TL-003',
  loss_percent: 3.1,
  status: 'operational'
}]->(ss2);

// Eastern to Northern (ring closure)
MATCH (ss1:Substation {id: 'SS-007'}), (ss2:Substation {id: 'SS-001'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 1200.0,
  distance_km: 95.8,
  line_id: 'TL-004',
  loss_percent: 1.9,
  status: 'operational'
}]->(ss2);

// Transmission to Distribution connections
MATCH (ss1:Substation {id: 'SS-001'}), (ss2:Substation {id: 'SS-002'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 800.0,
  distance_km: 5.2,
  line_id: 'TL-005',
  loss_percent: 0.5,
  status: 'operational'
}]->(ss2);

MATCH (ss1:Substation {id: 'SS-003'}), (ss2:Substation {id: 'SS-004'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 700.0,
  distance_km: 4.8,
  line_id: 'TL-006',
  loss_percent: 0.4,
  status: 'operational'
}]->(ss2);

MATCH (ss1:Substation {id: 'SS-005'}), (ss2:Substation {id: 'SS-006'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 900.0,
  distance_km: 6.1,
  line_id: 'TL-007',
  loss_percent: 0.6,
  status: 'operational'
}]->(ss2);

MATCH (ss1:Substation {id: 'SS-007'}), (ss2:Substation {id: 'SS-008'})
CREATE (ss1)-[:TRANSMITS_TO {
  capacity_mw: 600.0,
  distance_km: 4.5,
  line_id: 'TL-008',
  loss_percent: 0.4,
  status: 'operational'
}]->(ss2);

// ===================================
// 7. CREATE CUSTOMER SUPPLY RELATIONSHIPS
// ===================================

MATCH (ss:Substation {id: 'SS-002'}), (c:Customer {id: 'CUST-001'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2015-01-01'),
  average_load_kw: 625.0,
  contract_type: 'direct'
}]->(c);

MATCH (ss:Substation {id: 'SS-002'}), (c:Customer {id: 'CUST-002'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2010-06-15'),
  average_load_kw: 180.0,
  contract_type: 'standard'
}]->(c);

MATCH (ss:Substation {id: 'SS-002'}), (c:Customer {id: 'CUST-003'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2012-03-20'),
  average_load_kw: 35.0,
  contract_type: 'standard'
}]->(c);

MATCH (ss:Substation {id: 'SS-004'}), (c:Customer {id: 'CUST-004'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2008-09-10'),
  average_load_kw: 1000.0,
  contract_type: 'direct'
}]->(c);

MATCH (ss:Substation {id: 'SS-004'}), (c:Customer {id: 'CUST-005'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2005-11-25'),
  average_load_kw: 250.0,
  contract_type: 'priority'
}]->(c);

MATCH (ss:Substation {id: 'SS-006'}), (c:Customer {id: 'CUST-006'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2013-04-18'),
  average_load_kw: 1200.0,
  contract_type: 'direct'
}]->(c);

MATCH (ss:Substation {id: 'SS-006'}), (c:Customer {id: 'CUST-007'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2000-08-01'),
  average_load_kw: 240.0,
  contract_type: 'standard'
}]->(c);

MATCH (ss:Substation {id: 'SS-008'}), (c:Customer {id: 'CUST-008'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2017-02-14'),
  average_load_kw: 1500.0,
  contract_type: 'dedicated'
}]->(c);

MATCH (ss:Substation {id: 'SS-008'}), (c:Customer {id: 'CUST-009'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2014-06-22'),
  average_load_kw: 42.0,
  contract_type: 'standard'
}]->(c);

MATCH (ss:Substation {id: 'SS-008'}), (c:Customer {id: 'CUST-010'})
CREATE (ss)-[:SUPPLIES_POWER {
  connection_date: date('2016-09-30'),
  average_load_kw: 160.0,
  contract_type: 'standard'
}]->(c);

// ===================================
// Verification Query
// ===================================

// Count nodes and relationships
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC;
