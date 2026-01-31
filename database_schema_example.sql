-- Example Database Schema for Logistics AI System
-- This shows what the database implementation should look like

-- Core Tables
CREATE TABLE trucks (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'idle',
    current_location_lat DECIMAL(10, 8),
    current_location_lng DECIMAL(11, 8),
    current_load_id VARCHAR(50),
    driver_id VARCHAR(50),
    capacity_kg DECIMAL(10, 2) DEFAULT 10000,
    fuel_level_percent DECIMAL(5, 2) DEFAULT 100,
    total_distance_km DECIMAL(10, 2) DEFAULT 0,
    total_deliveries INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loads (
    id VARCHAR(50) PRIMARY KEY,
    description TEXT NOT NULL,
    weight_kg DECIMAL(10, 2) NOT NULL,
    volume_m3 DECIMAL(10, 3),
    priority VARCHAR(20) DEFAULT 'normal',
    pickup_location_lat DECIMAL(10, 8) NOT NULL,
    pickup_location_lng DECIMAL(11, 8) NOT NULL,
    pickup_location_address TEXT,
    delivery_location_lat DECIMAL(10, 8) NOT NULL,
    delivery_location_lng DECIMAL(11, 8) NOT NULL,
    delivery_location_address TEXT,
    pickup_window_start TIMESTAMP,
    pickup_window_end TIMESTAMP,
    delivery_deadline TIMESTAMP,
    assigned_truck_id VARCHAR(50),
    assigned_route_id VARCHAR(50),
    picked_up_at TIMESTAMP,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_truck_id) REFERENCES trucks(id)
);

CREATE TABLE routes (
    id VARCHAR(50) PRIMARY KEY,
    truck_id VARCHAR(50) NOT NULL,
    origin_lat DECIMAL(10, 8) NOT NULL,
    origin_lng DECIMAL(11, 8) NOT NULL,
    destination_lat DECIMAL(10, 8) NOT NULL,
    destination_lng DECIMAL(11, 8) NOT NULL,
    estimated_distance_km DECIMAL(10, 2),
    estimated_duration_minutes INTEGER,
    estimated_fuel_consumption_liters DECIMAL(8, 2),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    actual_distance_km DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES trucks(id)
);

CREATE TABLE gps_readings (
    id SERIAL PRIMARY KEY,
    truck_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    speed_kmh DECIMAL(6, 2) DEFAULT 0,
    heading DECIMAL(5, 2) DEFAULT 0,
    accuracy_meters DECIMAL(6, 2) DEFAULT 10,
    FOREIGN KEY (truck_id) REFERENCES trucks(id)
);

CREATE TABLE traffic_conditions (
    id SERIAL PRIMARY KEY,
    segment_id VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL,
    speed_kmh DECIMAL(6, 2) DEFAULT 0,
    delay_minutes INTEGER DEFAULT 0,
    incident_description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Decision Tables
CREATE TABLE issues (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    affected_truck_ids TEXT[], -- JSON array
    affected_load_ids TEXT[],   -- JSON array
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    metadata JSONB
);

CREATE TABLE decisions (
    id VARCHAR(50) PRIMARY KEY,
    scenario_id VARCHAR(50),
    action_type VARCHAR(50) NOT NULL,
    parameters JSONB,
    score DECIMAL(3, 2),
    confidence DECIMAL(3, 2),
    rationale TEXT,
    llm_verified BOOLEAN DEFAULT FALSE,
    human_approved BOOLEAN DEFAULT FALSE,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP
);

CREATE TABLE control_loop_cycles (
    id SERIAL PRIMARY KEY,
    cycle_id VARCHAR(50) NOT NULL,
    phase VARCHAR(20) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    issues_detected INTEGER DEFAULT 0,
    decisions_made INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Indexes for Performance
CREATE INDEX idx_trucks_status ON trucks(status);
CREATE INDEX idx_trucks_location ON trucks(current_location_lat, current_location_lng);
CREATE INDEX idx_loads_priority ON loads(priority);
CREATE INDEX idx_loads_assigned_truck ON loads(assigned_truck_id);
CREATE INDEX idx_gps_readings_truck_time ON gps_readings(truck_id, timestamp);
CREATE INDEX idx_traffic_timestamp ON traffic_conditions(timestamp);
CREATE INDEX idx_issues_severity ON issues(severity);
CREATE INDEX idx_decisions_approved ON decisions(human_approved);