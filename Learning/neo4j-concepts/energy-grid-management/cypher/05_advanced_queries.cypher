// ===================================
// ADVANCED QUERIES FOR ENERGY GRID
// ===================================
// Complex pattern matching and analytics

// ===================================
// 1. MULTI-HOP PATH QUERIES
// ===================================

// Find all paths from power plant to customer (any length)
MATCH path = (p:PowerPlant {id: 'PP-001'})-[:GENERATES]->()
             -[:TRANSMITS_TO*0..10]->()-[:SUPPLIES_POWER]->(c:Customer)
RETURN p.name as plant, c.name as customer, 
       [node in nodes(path) | labels(node)[0] + ': ' + node.name] as path_nodes,
       length(path) as path_length
ORDER BY path_length
LIMIT 10;

// Find shortest path between two substations
MATCH path = shortestPath(
    (s1:Substation {id: 'SS-001'})-[:TRANSMITS_TO*]-(s2:Substation {id: 'SS-005'})
)
RETURN [node in nodes(path) | node.name] as route,
       length(path) as hops,
       reduce(dist = 0, rel in relationships(path) | dist + rel.distance_km) as total_distance_km;

// Find alternative routes (top 3 shortest paths)
MATCH path = allShortestPaths(
    (s1:Substation {id: 'SS-001'})-[:TRANSMITS_TO*]-(s2:Substation {id: 'SS-005'})
)
RETURN [node in nodes(path) | node.name] as route,
       length(path) as hops
LIMIT 3;

// ===================================
// 2. AGGREGATION AND GROUPING
// ===================================

// Customer consumption by type and region
MATCH (c:Customer)
RETURN c.region, c.type,
       count(c) as customer_count,
       sum(c.average_consumption_kwh) as total_consumption,
       avg(c.average_consumption_kwh) as avg_consumption,
       min(c.average_consumption_kwh) as min_consumption,
       max(c.average_consumption_kwh) as max_consumption
ORDER BY c.region, total_consumption DESC;

// Power plant performance metrics
MATCH (p:PowerPlant)-[g:GENERATES]->(s:Substation)
WITH p, avg(g.average_output_mw) as avg_output
RETURN p.type,
       count(p) as plant_count,
       sum(p.capacity_mw) as total_capacity,
       sum(avg_output) as total_output,
       round(100.0 * sum(avg_output) / sum(p.capacity_mw), 2) as capacity_factor
ORDER BY capacity_factor DESC;

// Transmission efficiency by region
MATCH (s1:Substation)-[t:TRANSMITS_TO]->(s2:Substation)
RETURN s1.region as region,
       count(t) as transmission_lines,
       avg(t.capacity_mw) as avg_capacity,
       avg(t.loss_percent) as avg_loss_percent,
       sum(t.distance_km) as total_distance_km
ORDER BY avg_loss_percent;

// ===================================
// 3. CONDITIONAL LOGIC (CASE)
// ===================================

// Categorize power plants by size
MATCH (p:PowerPlant)
RETURN p.id, p.name, p.capacity_mw,
       CASE
           WHEN p.capacity_mw < 300 THEN 'Small'
           WHEN p.capacity_mw < 700 THEN 'Medium'
           WHEN p.capacity_mw < 1000 THEN 'Large'
           ELSE 'Very Large'
       END as size_category
ORDER BY p.capacity_mw DESC;

// Customer risk assessment
MATCH (c:Customer)<-[:SUPPLIES_POWER]-(s:Substation)
WITH c, count(DISTINCT s) as substation_count
RETURN c.id, c.name, c.type,
       substation_count,
       CASE
           WHEN substation_count = 1 THEN 'High Risk'
           WHEN substation_count = 2 THEN 'Medium Risk'
           ELSE 'Low Risk'
       END as supply_risk
ORDER BY substation_count;

// Equipment health status
MATCH (p:PowerPlant)
RETURN p.id, p.name, p.efficiency_percent,
       CASE
           WHEN p.efficiency_percent > 80 THEN 'Excellent'
           WHEN p.efficiency_percent > 60 THEN 'Good'
           WHEN p.efficiency_percent > 40 THEN 'Fair'
           ELSE 'Poor'
       END as health_status
ORDER BY p.efficiency_percent DESC;

// ===================================
// 4. OPTIONAL PATTERNS
// ===================================

// Substations with optional customer connections
MATCH (s:Substation)
OPTIONAL MATCH (s)-[:SUPPLIES_POWER]->(c:Customer)
WITH s, collect(c.name) as customers, count(c) as customer_count
RETURN s.id, s.name, s.region,
       CASE WHEN customer_count = 0 THEN [] ELSE customers END as customer_list,
       customer_count
ORDER BY customer_count DESC;

// Power plants with optional generation data
MATCH (p:PowerPlant)
OPTIONAL MATCH (p)-[g:GENERATES]->(s:Substation)
RETURN p.id, p.name, p.type, p.capacity_mw,
       CASE WHEN g IS NULL THEN 'Not Connected' ELSE 'Connected' END as status,
       coalesce(g.average_output_mw, 0) as current_output
ORDER BY p.name;

// ===================================
// 5. PATTERN COMPREHENSION
// ===================================

// Get all connected substations for each power plant
MATCH (p:PowerPlant)
RETURN p.name,
       [(p)-[:GENERATES]->(s:Substation) | s.name] as connected_substations,
       [(p)-[:GENERATES]->(s:Substation) | s.region] as regions
ORDER BY p.name;

// Customers with their supply chain
MATCH (c:Customer)
RETURN c.name,
       [(c)<-[:SUPPLIES_POWER]-(s:Substation) | {
           substation: s.name,
           voltage: s.voltage_kv,
           region: s.region
       }] as supply_sources
LIMIT 5;

// ===================================
// 6. COMPLEX FILTERS (WHERE)
// ===================================

// High-capacity renewable plants near specific location
MATCH (p:PowerPlant)
WHERE p.type IN ['solar', 'wind', 'hydro']
  AND p.capacity_mw > 400
  AND point.distance(p.location, point({latitude: 40.7128, longitude: -74.0060})) < 100000
RETURN p.id, p.name, p.type, p.capacity_mw,
       round(point.distance(p.location, point({latitude: 40.7128, longitude: -74.0060})) / 1000, 2) as distance_km
ORDER BY distance_km;

// Substations with high utilization in specific regions
MATCH (s:Substation)
WHERE s.region IN ['Northern', 'Central']
  AND s.capacity_mva > 1500
OPTIONAL MATCH (s)-[:SUPPLIES_POWER]->(c:Customer)
WITH s, sum(c.average_consumption_kwh) as total_load
WHERE total_load > 1000000
RETURN s.id, s.name, s.region, s.capacity_mva, total_load
ORDER BY total_load DESC;

// ===================================
// 7. SUBQUERIES
// ===================================

// Find substations supplying high-value customers
MATCH (s:Substation)
WHERE EXISTS {
    MATCH (s)-[:SUPPLIES_POWER]->(c:Customer)
    WHERE c.type = 'industrial' AND c.average_consumption_kwh > 500000
}
RETURN s.id, s.name, s.region
ORDER BY s.name;

// Power plants connected to critical infrastructure
MATCH (p:PowerPlant)
WHERE EXISTS {
    MATCH (p)-[:GENERATES]->(s:Substation)
    WHERE s.type = 'transmission' AND s.voltage_kv >= 500
}
RETURN p.id, p.name, p.type, p.capacity_mw
ORDER BY p.capacity_mw DESC;

// ===================================
// 8. NETWORK TOPOLOGY ANALYSIS
// ===================================

// Find hub substations (high degree centrality)
MATCH (s:Substation)
WITH s, 
     size((s)-[:TRANSMITS_TO]->()) as outgoing,
     size((s)<-[:TRANSMITS_TO]-()) as incoming,
     size((s)-[:SUPPLIES_POWER]->()) as customers
RETURN s.id, s.name, s.region,
       outgoing, incoming, customers,
       (outgoing + incoming + customers) as total_connections
ORDER BY total_connections DESC
LIMIT 10;

// Identify bottleneck transmission lines
MATCH (s1:Substation)-[t:TRANSMITS_TO]->(s2:Substation)
WITH t, s1, s2,
     size((s1)<-[:TRANSMITS_TO]-()) as s1_incoming,
     size((s2)-[:TRANSMITS_TO]->()) as s2_outgoing
WHERE s1_incoming > 2 OR s2_outgoing > 2
RETURN s1.name as from_station, s2.name as to_station,
       t.capacity_mw, t.distance_km,
       s1_incoming + s2_outgoing as traffic_indicator
ORDER BY traffic_indicator DESC
LIMIT 10;

// Find isolated or poorly connected nodes
MATCH (s:Substation)
WITH s, size((s)-[:TRANSMITS_TO]-()) as connections
WHERE connections <= 1
RETURN s.id, s.name, s.region, connections,
       CASE WHEN connections = 0 THEN 'Isolated' ELSE 'Single Connection' END as status
ORDER BY connections, s.name;

// ===================================
// 9. TEMPORAL QUERIES
// ===================================

// Equipment commissioned by year
MATCH (p:PowerPlant)
WITH p, date(p.commissioned_date).year as year
RETURN year, count(p) as plants_commissioned,
       sum(p.capacity_mw) as total_capacity_added
ORDER BY year DESC;

// Aging infrastructure analysis
MATCH (p:PowerPlant)
WITH p, duration.between(date(p.commissioned_date), date()).years as age
RETURN p.id, p.name, p.type, p.commissioned_date, age,
       CASE
           WHEN age < 10 THEN 'New'
           WHEN age < 25 THEN 'Mature'
           WHEN age < 40 THEN 'Aging'
           ELSE 'Legacy'
       END as age_category
ORDER BY age DESC;

// ===================================
// 10. COMPLEX AGGREGATIONS
// ===================================

// Multi-level aggregation: Regional capacity by plant type
MATCH (p:PowerPlant)-[:GENERATES]->(s:Substation)
WITH s.region as region, p.type as plant_type, 
     count(p) as plant_count, sum(p.capacity_mw) as capacity
ORDER BY region, capacity DESC
WITH region, 
     collect({type: plant_type, count: plant_count, capacity: capacity}) as breakdown,
     sum(capacity) as total_regional_capacity
RETURN region, total_regional_capacity, breakdown
ORDER BY total_regional_capacity DESC;

// Customer segmentation analysis
MATCH (c:Customer)
WITH c.type as customer_type,
     CASE
         WHEN c.average_consumption_kwh < 50000 THEN 'Small'
         WHEN c.average_consumption_kwh < 500000 THEN 'Medium'
         ELSE 'Large'
     END as size_category
RETURN customer_type, size_category, count(*) as customer_count
ORDER BY customer_type, size_category;

// ===================================
// 11. GRAPH PATTERN DETECTION
// ===================================

// Find triangular connections (redundancy patterns)
MATCH (s1:Substation)-[:TRANSMITS_TO]->(s2:Substation),
      (s2)-[:TRANSMITS_TO]->(s3:Substation),
      (s3)-[:TRANSMITS_TO]->(s1)
RETURN s1.name, s2.name, s3.name
LIMIT 10;

// Identify star topology patterns (central hubs)
MATCH (center:Substation)
WHERE size((center)-[:TRANSMITS_TO]->()) >= 3
MATCH (center)-[:TRANSMITS_TO]->(spoke:Substation)
WITH center, collect(spoke.name) as connected_stations
RETURN center.name as hub_station,
       center.region,
       size(connected_stations) as connection_count,
       connected_stations
ORDER BY connection_count DESC
LIMIT 5;

// ===================================
// END OF ADVANCED QUERIES
// ===================================
