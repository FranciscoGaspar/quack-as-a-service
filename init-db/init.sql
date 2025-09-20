-- Database initialization for Quack as a Service
-- This script runs when PostgreSQL container starts

\echo 'Creating tables for Quack as a Service...'

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    qr_code VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create room equipment configurations table
CREATE TABLE IF NOT EXISTS room_equipment_configurations (
    id SERIAL PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL UNIQUE,
    equipment_weights JSONB NOT NULL DEFAULT '{}',
    entry_threshold FLOAT NOT NULL DEFAULT 70.0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    description VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create personal_entries table for equipment tracking when entering rooms
CREATE TABLE IF NOT EXISTS personal_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    room_name VARCHAR(100) NOT NULL,
    image_url VARCHAR(500),
    equipment JSONB NOT NULL DEFAULT '{}',
    -- New approval fields
    is_approved BOOLEAN,
    equipment_score FLOAT,
    approval_reason VARCHAR(500),
    entered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_personal_entries_user_id ON personal_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_personal_entries_room_name ON personal_entries(room_name);
CREATE INDEX IF NOT EXISTS idx_personal_entries_entered_at ON personal_entries(entered_at);
CREATE INDEX IF NOT EXISTS idx_personal_entries_equipment ON personal_entries USING GIN(equipment);
CREATE INDEX IF NOT EXISTS idx_personal_entries_is_approved ON personal_entries(is_approved);

-- Indexes for room equipment configurations
CREATE INDEX IF NOT EXISTS idx_room_equipment_configurations_room_name ON room_equipment_configurations(room_name);
CREATE INDEX IF NOT EXISTS idx_room_equipment_configurations_is_active ON room_equipment_configurations(is_active);
CREATE INDEX IF NOT EXISTS idx_room_equipment_configurations_weights ON room_equipment_configurations USING GIN(equipment_weights);

-- Insert default room equipment configurations
INSERT INTO room_equipment_configurations (room_name, equipment_weights, entry_threshold, description) VALUES 
    ('production-floor', 
     '{"mask": 35, "gloves": 30, "hairnet": 35}', 
     80.0, 
     'Production Floor - High safety requirements with mask, gloves, and hairnet'),
    ('assembly-line', 
     '{"gloves": 50, "hairnet": 50}', 
     70.0, 
     'Assembly Line - Moderate requirements with gloves and hairnet'),
    ('packaging-area', 
     '{"gloves": 100}', 
     60.0, 
     'Packaging Area - Basic hygiene requirements with gloves')
ON CONFLICT (room_name) DO NOTHING;

-- Insert sample users
INSERT INTO users (name) VALUES 
    ('Admin User'),
    ('Test User'),
    ('Alice Johnson'),
    ('Bob Smith')
ON CONFLICT DO NOTHING;

-- Insert sample personal entries (without approval status - will be calculated)
INSERT INTO personal_entries (user_id, room_name, image_url, equipment) VALUES 
    (1, 'production-floor', '/images/admin_production.jpg', '{"mask": true, "gloves": true, "hairnet": true}'),
    (2, 'assembly-line', '/images/test_assembly.jpg', '{"mask": false, "gloves": true, "hairnet": false}'),
    (3, 'packaging-area', '/images/alice_packaging.jpg', '{"mask": false, "gloves": true, "hairnet": false}'),
    (4, 'production-floor', '/images/bob_production.jpg', '{"mask": true, "gloves": false, "hairnet": false}')
ON CONFLICT DO NOTHING;

\echo 'Database initialization completed!'
\echo 'Sample data:'
\echo '- 3 room equipment configurations created'
\echo '- 4 users created'  
\echo '- 4 personal entries created'
\echo '- Indexes created for performance'
\echo '- New approval system ready!'
