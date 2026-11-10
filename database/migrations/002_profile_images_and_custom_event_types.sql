-- MS College refinements: run once against an existing database.
-- Adds profile photo support and allows administrator-defined event categories.
ALTER TABLE users ADD COLUMN profile_image VARCHAR(255) NULL;
ALTER TABLE staff ADD COLUMN profile_image VARCHAR(255) NULL;
ALTER TABLE events MODIFY COLUMN event_type VARCHAR(50) NOT NULL DEFAULT 'other';
