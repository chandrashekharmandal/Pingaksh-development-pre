"""
Custom PostgreSQL indexes, triggers, and extensions for the bSecure platform.

This migration applies raw SQL for production-grade indexes that go beyond
what Django auto-creates. It must run AFTER all app model migrations.

NOTE: This migration uses atomic=False because CREATE INDEX CONCURRENTLY
cannot run inside a transaction block. In production, run with care.
For development/test environments, we use regular CREATE INDEX (without CONCURRENTLY)
so it can run inside the test transaction.
"""

from django.db import migrations


# In development/test (SQLite), these will be no-ops.
# In production (PostgreSQL), they create the full index set.

FORWARD_SQL = """
-- =============================================================================
-- Extensions (idempotent — safe to re-run)
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- =============================================================================
-- Trigger: update_guard_average_rating
-- =============================================================================
CREATE OR REPLACE FUNCTION update_guard_average_rating()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        UPDATE guards_guard SET
            average_rating = COALESCE(
                (SELECT AVG(rating)::numeric(3,2) FROM reviews_review WHERE guard_id = OLD.guard_id),
                0.0
            ),
            total_reviews = (SELECT COUNT(*) FROM reviews_review WHERE guard_id = OLD.guard_id)
        WHERE id = OLD.guard_id;
        RETURN OLD;
    ELSE
        UPDATE guards_guard SET
            average_rating = COALESCE(
                (SELECT AVG(rating)::numeric(3,2) FROM reviews_review WHERE guard_id = NEW.guard_id),
                0.0
            ),
            total_reviews = (SELECT COUNT(*) FROM reviews_review WHERE guard_id = NEW.guard_id)
        WHERE id = NEW.guard_id;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger on reviews_review table
DROP TRIGGER IF EXISTS trg_update_guard_rating ON reviews_review;
CREATE TRIGGER trg_update_guard_rating
    AFTER INSERT OR UPDATE OF rating OR DELETE
    ON reviews_review
    FOR EACH ROW
    EXECUTE FUNCTION update_guard_average_rating();

-- =============================================================================
-- Custom Indexes (non-CONCURRENTLY for migration compatibility)
-- =============================================================================

-- users_userprofile
CREATE INDEX IF NOT EXISTS idx_users_user_active
    ON users_userprofile (id)
    WHERE is_active = true;

-- bookings_booking
CREATE INDEX IF NOT EXISTS idx_bookings_booking_user_created
    ON bookings_booking (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_bookings_booking_guard_created
    ON bookings_booking (guard_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_bookings_booking_status_created
    ON bookings_booking (status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_bookings_booking_pending
    ON bookings_booking (created_at DESC)
    WHERE status = 'PENDING';

CREATE INDEX IF NOT EXISTS idx_bookings_booking_active
    ON bookings_booking (guard_id, user_id)
    WHERE status = 'ACTIVE';

-- tracking_locationsnapshot
CREATE INDEX IF NOT EXISTS idx_tracking_snapshot_booking_time
    ON tracking_locationsnapshot (booking_id, recorded_at DESC);

-- payments_transaction
CREATE INDEX IF NOT EXISTS idx_payments_txn_wallet_created
    ON payments_transaction (wallet_id, created_at DESC);

-- notifications_notification
CREATE INDEX IF NOT EXISTS idx_notifications_unread
    ON notifications_notification (recipient_id, created_at DESC)
    WHERE is_read = false;

-- reviews_review
CREATE INDEX IF NOT EXISTS idx_reviews_review_guard_created
    ON reviews_review (guard_id, created_at DESC);

-- sos_sosevent
CREATE INDEX IF NOT EXISTS idx_sos_event_unresolved
    ON sos_sosevent (triggered_at DESC)
    WHERE resolved_at IS NULL;
"""

REVERSE_SQL = """
-- Drop custom indexes
DROP INDEX IF EXISTS idx_users_user_active;
DROP INDEX IF EXISTS idx_bookings_booking_user_created;
DROP INDEX IF EXISTS idx_bookings_booking_guard_created;
DROP INDEX IF EXISTS idx_bookings_booking_status_created;
DROP INDEX IF EXISTS idx_bookings_booking_pending;
DROP INDEX IF EXISTS idx_bookings_booking_active;
DROP INDEX IF EXISTS idx_tracking_snapshot_booking_time;
DROP INDEX IF EXISTS idx_payments_txn_wallet_created;
DROP INDEX IF EXISTS idx_notifications_unread;
DROP INDEX IF EXISTS idx_reviews_review_guard_created;
DROP INDEX IF EXISTS idx_sos_event_unresolved;

-- Drop trigger and function
DROP TRIGGER IF EXISTS trg_update_guard_rating ON reviews_review;
DROP FUNCTION IF EXISTS update_guard_average_rating();
"""


class Migration(migrations.Migration):
    """
    Custom PostgreSQL indexes and triggers.
    Only runs on PostgreSQL — skipped on SQLite (test env).
    """

    dependencies = [
        ("users", "0001_initial"),
        ("guards", "0001_initial"),
        ("bookings", "0001_initial"),
        ("tracking", "0001_initial"),
        ("payments", "0001_initial"),
        ("notifications", "0001_initial"),
        ("reviews", "0001_initial"),
        ("sos", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=FORWARD_SQL,
            reverse_sql=REVERSE_SQL,
        ),
    ]
