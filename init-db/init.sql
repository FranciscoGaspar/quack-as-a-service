-- Database initialization for Quack as a Service
-- This script runs when PostgreSQL container starts

\echo 'Creating tables for Quack as a Service...'

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
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
    entered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_personal_entries_user_id ON personal_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_personal_entries_room_name ON personal_entries(room_name);
CREATE INDEX IF NOT EXISTS idx_personal_entries_entered_at ON personal_entries(entered_at);
CREATE INDEX IF NOT EXISTS idx_personal_entries_equipment ON personal_entries USING GIN(equipment);

-- Insert sample users
INSERT INTO users (name) VALUES 
    ('Admin User'),
    ('Test User'),
    ('Alice Johnson'),
    ('Bob Smith')
ON CONFLICT DO NOTHING;

-- Insert sample personal entries
INSERT INTO personal_entries (user_id, room_name, image_url, equipment) VALUES 
    (1, 'Laboratory A', '/images/admin_lab_a.jpg', '{"mask": true, "right_glove": true, "left_glove": false, "hairnet": true}'),
    (2, 'Clean Room B', '/images/test_clean_room.jpg', '{"mask": false, "right_glove": true, "left_glove": true, "hairnet": false}'),
    (3, 'Laboratory A', '/images/alice_lab_a.jpg', '{"mask": true, "right_glove": true, "left_glove": true, "hairnet": true, "safety_glasses": true}'),
    (4, 'Production Floor', '/images/bob_production.jpg', '{"mask": true, "right_glove": false, "left_glove": true, "hairnet": false, "safety_glasses": false}')
ON CONFLICT DO NOTHING;

\echo 'Database initialization completed!'
\echo 'Sample data:'
\echo '- 4 users created'
\echo '- 4 personal entries created'
\echo '- Indexes created for performance'
