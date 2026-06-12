-- =============================================================================
-- bSecure PostgreSQL Initialization Script
-- Runs automatically on first docker-compose up via /docker-entrypoint-initdb.d/
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "postgis_topology";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- =============================================================================
-- Trigger function: update guard average rating after review insert/update/delete
-- =============================================================================
CREATE OR REPLACE FUNCTION update_guard_average_rating()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE guards_guard SET
            average_rating = COALESCE(
                (SELECT AVG(rating) FROM reviews_review WHERE guard_id = OLD.guard_id),
                0.0
            ),
            total_reviews = (SELECT COUNT(*) FROM reviews_review WHERE guard_id = OLD.guard_id)
        WHERE id = OLD.guard_id;
        RETURN OLD;
    ELSE
        UPDATE guards_guard SET
            average_rating = COALESCE(
                (SELECT AVG(rating) FROM reviews_review WHERE guard_id = NEW.guard_id),
                0.0
            ),
            total_reviews = (SELECT COUNT(*) FROM reviews_review WHERE guard_id = NEW.guard_id)
        WHERE id = NEW.guard_id;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Trigger function: rebuild search_vector on guards_guard
-- =============================================================================
CREATE OR REPLACE FUNCTION guards_guard_search_vector_update()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.full_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.city, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.skills, ' '), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
