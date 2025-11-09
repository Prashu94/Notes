// ===================================
// BASIC QUERIES FOR ENERGY GRID
// ===================================
// Common queries for daily operations

// ===================================
// 1. INFRASTRUCTURE QUERIES
// ===================================

// List all power plants with their details
MATCH (p:PowerPlant)
RETURN p.id, p.name, p.type, p.capacity_mw, p.status, p.operator
ORDER BY p.capacity_mw DESC;

// Find all substations in a region
MATCH (s:Substation {region: 'Northern'})
RETURN s.id, s.name, s.voltage_kv, s.capacity_mva, s.status
ORDER BY s.capacity_mva DESC;

// Get transmission lines with their capacity
MATCH (s1:Substation)-[t:TRANSMITS_TO]->(s2:Substation)
RETURN s1.name as from_station, s2.name as to_station, 
       t.capacity_mw, t.distance_km, t.status
ORDER BY t.capacity_mw DESC;

// Find all operational equipment
MATCH (n)
WHERE n.status = 'operational' AND 
      (n:PowerPlant OR n:Substation OR n:TransmissionLine)
RETURN labels(n)[0] as type, count(n) as count;

// ===================================
// 2. CUSTOMER QUERIES
// ===================================

// List all customers by type
MATCH (c:Customer)
RETURN c.type, count(c) as customer_count, 
       sum(c.average_consumption_kwh) as total_consumption
ORDER BY total_consumption DESC;

// Find high-consumption customers
MATCH (c:Customer)
WHERE c.average_consumption_kwh > 500000
RETURN c.id, c.name, c.type, c.average_consumption_kwh, c.region
ORDER BY c.average_consumption_kwh DESC;

// Get customers by region
MATCH (c:Customer {region: 'Northern'})
RETURN c.id, c.name, c.type, c.average_consumption_kwh
ORDER BY c.name;

// ===================================
// 3. POWER FLOW QUERIES
// ===================================

// Trace power flow from a specific plant
MATCH path = (p:PowerPlant {id: 'PP-001'})-[:GENERATES]->()
             -[:TRANSMITS_TO*0..5]->()-[:SUPPLIES_POWER]->(c:Customer)
RETURN p.name as power_plant, c.name as customer, 
       c.type as customer_type, length(path) as path_length
LIMIT 20;

// Find all power sources for a customer
MATCH path = (p:PowerPlant)-[:GENERATES]->()
             -[:TRANSMITS_TO*]->()-[:SUPPLIES_POWER]->(c:Customer {id: 'CUST-001'})
RETURN p.name as power_plant, p.type as plant_type, 
       p.capacity_mw, length(path) as hops
ORDER BY length(path);

// Map complete power network
MATCH (p:PowerPlant)-[g:GENERATES]->(s:Substation)
RETURN p.name as source, s.name as target, g.average_output_mw as capacity, 'GENERATES' as rel_type
UNION
MATCH (s1:Substation)-[t:TRANSMITS_TO]->(s2:Substation)
RETURN s1.name as source, s2.name as target, t.capacity_mw as capacity, 'TRANSMITS_TO' as rel_type
UNION
MATCH (s:Substation)-[sp:SUPPLIES_POWER]->(c:Customer)
RETURN s.name as source, c.name as target, sp.average_load_kw as capacity, 'SUPPLIES_POWER' as rel_type;

// ===================================
// 4. CAPACITY QUERIES
// ===================================

// Total generation capacity by type
MATCH (p:PowerPlant)
RETURN p.type, count(p) as plant_count, 
       sum(p.capacity_mw) as total_capacity_mw,
       avg(p.capacity_mw) as avg_capacity_mw
ORDER BY total_capacity_mw DESC;

// Substation utilization
MATCH (s:Substation)
OPTIONAL MATCH (s)-[:SUPPLIES_POWER]->(c:Customer)
WITH s, count(c) as customers, sum(c.average_consumption_kwh) as total_load
RETURN s.id, s.name, s.capacity_mva, customers, total_load,
       round(100.0 * total_load / (s.capacity_mva * 730), 2) as utilization_percent
ORDER BY utilization_percent DESC;

// Regional capacity analysis
MATCH (s:Substation)
RETURN s.region, count(s) as substations,
       sum(s.capacity_mva) as total_capacity_mva,
       avg(s.voltage_kv) as avg_voltage_kv
ORDER BY total_capacity_mva DESC;

// ===================================
// 5. RENEWABLE ENERGY QUERIES
// ===================================

// Renewable vs non-renewable capacity
MATCH (p:PowerPlant)
WITH p, CASE 
    WHEN p.type IN ['solar', 'wind', 'hydro'] THEN 'renewable'
    ELSE 'non-renewable'
END as category
RETURN category, count(p) as plant_count,
       sum(p.capacity_mw) as total_capacity,
       collect(DISTINCT p.type) as plant_types
ORDER BY total_capacity DESC;

// Renewable energy by region
MATCH (p:PowerPlant)-[:GENERATES]->(s:Substation)
WHERE p.type IN ['solar', 'wind', 'hydro']
RETURN s.region, p.type, count(p) as plants,
       sum(p.capacity_mw) as renewable_capacity_mw
ORDER BY s.region, renewable_capacity_mw DESC;

// Clean energy percentage
MATCH (p:PowerPlant)
WITH sum(p.capacity_mw) as total_capacity
MATCH (clean:PowerPlant)
WHERE clean.type IN ['solar', 'wind', 'hydro', 'nuclear']
WITH total_capacity, sum(clean.capacity_mw) as clean_capacity
RETURN round(100.0 * clean_capacity / total_capacity, 2) as clean_energy_percent,
       clean_capacity, total_capacity;

// ===================================
// 6. OPERATIONAL STATUS QUERIES
// ===================================

// Equipment status summary
MATCH (n)
WHERE n:PowerPlant OR n:Substation
RETURN labels(n)[0] as equipment_type, n.status,
       count(n) as count
ORDER BY equipment_type, count DESC;

// Find offline equipment
MATCH (n)
WHERE (n:PowerPlant OR n:Substation) AND n.status <> 'operational'
RETURN labels(n)[0] as type, n.id, n.name, n.status
ORDER BY type, n.name;

// Equipment needing attention
MATCH (p:PowerPlant)
WHERE p.status = 'maintenance' OR p.efficiency_percent < 30
RETURN p.id, p.name, p.type, p.status, p.efficiency_percent
ORDER BY p.efficiency_percent;

// ===================================
// 7. LOCATION-BASED QUERIES
// ===================================

// Find equipment near a location
MATCH (p:PowerPlant)
WHERE point.distance(p.location, point({latitude: 40.7128, longitude: -74.0060})) < 50000
RETURN p.id, p.name, p.type,
       round(point.distance(p.location, point({latitude: 40.7128, longitude: -74.0060})) / 1000, 2) as distance_km
ORDER BY distance_km;

// Equipment in a geographic region
MATCH (s:Substation)
WHERE s.location.latitude > 40.7 AND s.location.latitude < 41.0
  AND s.location.longitude > -74.0 AND s.location.longitude < -73.5
RETURN s.id, s.name, s.region, s.location
ORDER BY s.name;

// ===================================
// 8. CUSTOMER SERVICE QUERIES
// ===================================

// Find customers supplied by a substation
MATCH (s:Substation {id: 'SS-002'})-[:SUPPLIES_POWER]->(c:Customer)
RETURN c.id, c.name, c.type, c.average_consumption_kwh
ORDER BY c.average_consumption_kwh DESC;

// Customer power source summary
MATCH (c:Customer {id: 'CUST-001'})<-[:SUPPLIES_POWER]-(s:Substation)
RETURN c.name as customer, 
       collect(s.name) as supplying_substations,
       collect(s.voltage_kv) as voltages;

// Customers by tariff plan
MATCH (c:Customer)
RETURN c.tariff_plan, count(c) as customer_count,
       sum(c.average_consumption_kwh) as total_consumption
ORDER BY customer_count DESC;

// ===================================
// 9. QUICK STATISTICS
// ===================================

// Overall system statistics
MATCH (p:PowerPlant)
WITH sum(p.capacity_mw) as total_generation
MATCH (s:Substation)
WITH total_generation, sum(s.capacity_mva) as total_transmission
MATCH (c:Customer)
WITH total_generation, total_transmission, 
     sum(c.average_consumption_kwh) as total_consumption
RETURN total_generation as generation_capacity_mw,
       total_transmission as transmission_capacity_mva,
       total_consumption as monthly_consumption_kwh;

// Node and relationship counts
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {})
YIELD value
RETURN label, value.count as node_count
ORDER BY node_count DESC;

// ===================================
// 10. SEARCH QUERIES
// ===================================

// Search equipment by name
MATCH (n)
WHERE (n:PowerPlant OR n:Substation) AND n.name CONTAINS 'North'
RETURN labels(n)[0] as type, n.id, n.name, n.status
ORDER BY type, n.name;

// Find by ID pattern
MATCH (n)
WHERE n.id STARTS WITH 'PP-'
RETURN labels(n)[0] as type, n.id, n.name
ORDER BY n.id;

// ===================================
// END OF BASIC QUERIES
// ===================================
