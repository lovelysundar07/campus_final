-- MS College v3: publishable results and leaderboards
-- Apply once, after migrations 001 and 002. Back up the database first.
ALTER TABLE events ADD COLUMN results_published BOOLEAN NOT NULL DEFAULT FALSE;
