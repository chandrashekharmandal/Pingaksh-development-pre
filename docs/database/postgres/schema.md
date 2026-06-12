# PostgreSQL Schema — b-secure

**Engine:** PostgreSQL 16 + PostGIS 3.4
**Encoding:** UTF-8
**Timezone:** UTC (application converts to IST for display)
**Default PK type:** UUID (gen_random_uuid())

---

## Table of Contents

1. [Extensions](#1-extensions)
2. [Schema Conventions](#2-schema-conventions)
3. [Entity Relationship Diagram](#3-entity-relationship-diagram)
4. [auth_otp_token](#4-auth_otp_token)
5. [users_profile](#5-users_profile)
6. [users_address](#6-users_address)
7. [users_emergency_contact](#7-users_emergency_contact)
8. [guards_profile](#8-guards_profile)
9. [guards_document](#9-guards_document)
10. [guards_availability](#10-guards_availability)
11. [guards_blackout_date](#11-guards_blackout_date)
12. [bookings_booking](#12-bookings_booking)
13. [bookings_broadcast](#13-bookings_broadcast)
14. [bookings_checkin](#14-bookings_checkin)
15. [tracking_location_snapshot](#15-tracking_location_snapshot)
16. [payments_wallet](#16-payments_wallet)
17. [payments_transaction](#17-payments_transaction)
18. [payments_order](#18-payments_order)
19. [payments_payout](#19-payments_payout)
20. [payments_payout_bookings](#20-payments_payout_bookings-m2m)
21. [notifications_log](#21-notifications_log)
22. [notifications_preference](#22-notifications_preference)
23. [sos_alert](#23-sos_alert)
24. [sos_emergency_contact_alert](#24-sos_emergency_contact_alert)
25. [sos_incident](#25-sos_incident)
26. [sos_incident_evidence](#26-sos_incident_evidence)
27. [reviews_review](#27-reviews_review)
28. [analytics_daily_stats](#28-analytics_daily_stats)
29. [Django System Tables](#29-django-system-tables)

---

## 1. Extensions

```sql
-- Required extensions (run once on new DB)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";         -- UUID generation
CREATE EXTENSION IF NOT EXISTS "postgis";           -- Geospatial types + functions
CREATE EXTENSION IF NOT EXISTS "postgis_topology";  -- Topology support
CREATE EXTENSION IF NOT EXISTS "pg_trgm";           -- Trigram text search
CREATE EXTENSION IF NOT EXISTS "btree_gist";        -- GiST index on B-tree types (for exclusion constraints)
```

---

## 2. Schema Conventions

| Convention | Rule | Example |
|---|---|---|
| Primary key | UUID, `gen_random_uuid()` default | `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` |
| Timestamps | `created_at`, `updated_at` on every table | `TIMESTAMPTZ NOT NULL DEFAULT NOW()` |
| Soft delete | `is_deleted BOOLEAN DEFAULT FALSE` + `deleted_at TIMESTAMPTZ` | On users and guards only |
| Enum-style fields | `VARCHAR` with `CHECK` constraint or PostgreSQL `ENUM` type | `status VARCHAR(20) CHECK (status IN (...))` |
| Foreign keys | Always named `{referenced_table_singular}_id` | `user_id UUID REFERENCES users_profile(id)` |
| Geospatial | PostGIS `GEOGRAPHY(Point, 4326)` for lat/lng | `current_location GEOGRAPHY(POINT, 4326)` |
| Monetary values | `NUMERIC(10,2)` — never FLOAT for money | `amount NUMERIC(10,2) NOT NULL` |
| JSON fields | `JSONB` (not JSON) for indexable JSON | `skills JSONB DEFAULT '[]'` |
| Table names | `{app}_{model}` snake_case | `bookings_booking`, `guards_profile` |

---

## 3. Entity Relationship Diagram

```
users_profile ──────────────────── guards_profile (1:1)
     │  │  │                              │  │  │
     │  │  └── users_address (1:N)        │  │  └── guards_document (1:N)
     │  │                                 │  └───── guards_availability (1:N)
     │  └────── users_emergency_contact   └──────── guards_blackout_date (1:N)
     │           (1:N)
     │
     └── payments_wallet (1:1)
              │
              └── payments_transaction (1:N)

users_profile ──── bookings_booking ──── guards_profile
                        │
           ┌────────────┼────────────────────┐
           │            │                    │
    bookings_broadcast  │             bookings_checkin
    (1:N)               │             (1:N)
                        │
           ┌────────────┼────────────────────┐
           │            │                    │
  tracking_location   sos_alert         sos_incident
  _snapshot (1:N)     (1:N)             (1:N)
                                             │
                                    sos_incident_evidence
                                    (1:N)

    bookings_booking ── payments_payout (M:N via payments_payout_bookings)
    bookings_booking ── reviews_review (1:1)
    bookings_booking ── payments_transaction (1:N)
    bookings_booking ── payments_order (1:N, nullable)
```

---

## 4. auth_otp_token

Stores hashed OTP codes for phone-based authentication.

```sql
CREATE TABLE auth_otp_token (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20)  NOT NULL,
    otp_hash     CHAR(64)     NOT NULL,                        -- SHA-256 hex, never plaintext
    purpose      VARCHAR(20)  NOT NULL DEFAULT 'LOGIN'
                              CHECK (purpose IN ('LOGIN','PHONE_CHANGE','TRANSACTION')),
    is_used      BOOLEAN      NOT NULL DEFAULT FALSE,
    attempt_count SMALLINT    NOT NULL DEFAULT 0
                              CHECK (attempt_count >= 0 AND attempt_count <= 5),
    expires_at   TIMESTAMPTZ  NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_otp_phone_lookup
    ON auth_otp_token (phone_number, is_used, expires_at DESC);
```

**Retention:** Rows deleted nightly by Celery task if older than 24 hours.

---

## 5. users_profile

Central user account. Serves regular users, guards, admin, and staff roles.
This is Django's `AUTH_USER_MODEL`.

```sql
CREATE TABLE users_profile (
    -- Identity
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number     VARCHAR(20)  NOT NULL UNIQUE,
    email            VARCHAR(254) UNIQUE,
    full_name        VARCHAR(150) NOT NULL DEFAULT '',
    gender           VARCHAR(20)  DEFAULT ''
                                  CHECK (gender IN ('','MALE','FEMALE','OTHER','PREFER_NOT_TO_SAY')),
    date_of_birth    DATE,
    profile_photo    VARCHAR(512),                              -- S3 key

    -- Role
    role             VARCHAR(10)  NOT NULL DEFAULT 'USER'
                                  CHECK (role IN ('USER','GUARD','ADMIN','STAFF')),

    -- Social auth
    google_id        VARCHAR(128) UNIQUE,
    apple_id         VARCHAR(128) UNIQUE,

    -- Push notifications
    fcm_token        VARCHAR(512) NOT NULL DEFAULT '',

    -- Account status
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    is_suspended     BOOLEAN      NOT NULL DEFAULT FALSE,
    suspension_reason TEXT        NOT NULL DEFAULT '',
    suspension_ends_at TIMESTAMPTZ,
    is_deleted       BOOLEAN      NOT NULL DEFAULT FALSE,
    deleted_at       TIMESTAMPTZ,

    -- Django auth fields
    password         VARCHAR(128) NOT NULL DEFAULT '!',        -- Unusable for OTP users
    is_staff         BOOLEAN      NOT NULL DEFAULT FALSE,
    is_superuser     BOOLEAN      NOT NULL DEFAULT FALSE,
    last_login       TIMESTAMPTZ,

    -- Timestamps
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Constraints
ALTER TABLE users_profile
    ADD CONSTRAINT users_profile_phone_e164
    CHECK (phone_number ~ '^\+[1-9]\d{6,14}$');              -- E.164 format

-- Indexes
CREATE INDEX idx_users_role_active     ON users_profile (role, is_active) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_google_id       ON users_profile (google_id) WHERE google_id IS NOT NULL;
CREATE INDEX idx_users_apple_id        ON users_profile (apple_id) WHERE apple_id IS NOT NULL;
CREATE INDEX idx_users_fcm_token       ON users_profile (fcm_token) WHERE fcm_token != '';
CREATE INDEX idx_users_created_at      ON users_profile (created_at DESC);
```

---

## 6. users_address

Saved delivery/service addresses per user.

```sql
CREATE TABLE users_address (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID         NOT NULL REFERENCES users_profile(id) ON DELETE CASCADE,
    label       VARCHAR(20)  NOT NULL DEFAULT 'HOME'
                             CHECK (label IN ('HOME','OFFICE','OTHER')),
    custom_label VARCHAR(50) NOT NULL DEFAULT '',
    line1       VARCHAR(255) NOT NULL,
    line2       VARCHAR(255) NOT NULL DEFAULT '',
    city        VARCHAR(100) NOT NULL,
    state       VARCHAR(100) NOT NULL,
    pincode     VARCHAR(10)  NOT NULL,
    country     VARCHAR(50)  NOT NULL DEFAULT 'India',
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    is_default  BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Only one default address per user
CREATE UNIQUE INDEX idx_address_one_default
    ON users_address (user_id)
    WHERE is_default = TRUE;

CREATE INDEX idx_address_user ON users_address (user_id);
```

---

## 7. users_emergency_contact

Emergency contacts for SOS alerts. Max 5 per user (enforced in application layer).

```sql
CREATE TABLE users_emergency_contact (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID         NOT NULL REFERENCES users_profile(id) ON DELETE CASCADE,
    name         VARCHAR(150) NOT NULL,
    phone_number VARCHAR(20)  NOT NULL,
    relationship VARCHAR(20)  NOT NULL DEFAULT 'OTHER'
                              CHECK (relationship IN
                                ('SPOUSE','PARENT','SIBLING','CHILD','FRIEND','COLLEAGUE','OTHER')),
    is_primary   BOOLEAN      NOT NULL DEFAULT FALSE,
    is_verified  BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Only one primary contact per user
CREATE UNIQUE INDEX idx_emergency_contact_one_primary
    ON users_emergency_contact (user_id)
    WHERE is_primary = TRUE;

CREATE INDEX idx_emergency_contact_user ON users_emergency_contact (user_id);
```

---

## 8. guards_profile

Extended profile for security guards. OneToOne with `users_profile`.

```sql
CREATE TABLE guards_profile (
    id                        UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                   UUID         NOT NULL UNIQUE REFERENCES users_profile(id) ON DELETE CASCADE,

    -- Professional details
    guard_type                VARCHAR(10)  NOT NULL DEFAULT 'UNARMED'
                                           CHECK (guard_type IN
                                             ('UNARMED','ARMED','FEMALE','CPO','EVENT','K9')),
    years_of_experience       SMALLINT     NOT NULL DEFAULT 0 CHECK (years_of_experience >= 0),
    bio                       VARCHAR(500) NOT NULL DEFAULT '',
    languages_spoken          JSONB        NOT NULL DEFAULT '[]',
    skills                    JSONB        NOT NULL DEFAULT '[]',

    -- Verification
    verification_status       VARCHAR(25)  NOT NULL DEFAULT 'PENDING'
                                           CHECK (verification_status IN
                                             ('PENDING','UNDER_REVIEW','ACTIVE',
                                              'SUSPENDED','BANNED','DOCUMENTS_REJECTED')),
    verified_at               TIMESTAMPTZ,
    verified_by_id            UUID         REFERENCES users_profile(id) ON DELETE SET NULL,

    -- Live location (PostGIS Geography — accurate distance calculations)
    current_location          GEOGRAPHY(POINT, 4326),          -- (lng, lat) WGS84
    last_location_update      TIMESTAMPTZ,
    is_online                 BOOLEAN      NOT NULL DEFAULT FALSE,

    -- Denormalized rating cache (updated by trigger/signal on new review)
    average_rating            NUMERIC(3,2) NOT NULL DEFAULT 0.00
                                           CHECK (average_rating >= 0 AND average_rating <= 5),
    total_reviews             INTEGER      NOT NULL DEFAULT 0 CHECK (total_reviews >= 0),
    total_sessions_completed  INTEGER      NOT NULL DEFAULT 0 CHECK (total_sessions_completed >= 0),

    -- Payout details (stored encrypted at rest via RDS encryption)
    bank_account_number       VARCHAR(20)  NOT NULL DEFAULT '',
    bank_ifsc_code            VARCHAR(11)  NOT NULL DEFAULT '',
    upi_id                    VARCHAR(50)  NOT NULL DEFAULT '',
    payout_preference         VARCHAR(5)   NOT NULL DEFAULT 'UPI'
                                           CHECK (payout_preference IN ('BANK','UPI')),

    -- Working preferences
    preferred_work_radius_km  SMALLINT     NOT NULL DEFAULT 10,
    max_daily_hours           SMALLINT     NOT NULL DEFAULT 12,

    created_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Spatial index for proximity queries (the most critical index in the DB)
CREATE INDEX idx_guards_location_gist
    ON guards_profile USING GIST (current_location);

-- Partial index: only online, active guards (used by booking matching)
CREATE INDEX idx_guards_available
    ON guards_profile (guard_type, average_rating DESC)
    WHERE verification_status = 'ACTIVE' AND is_online = TRUE;

CREATE INDEX idx_guards_verification_status
    ON guards_profile (verification_status, created_at DESC);
```

---

## 9. guards_document

Documents uploaded for verification. One row per document type per guard.

```sql
CREATE TABLE guards_document (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    guard_id        UUID         NOT NULL REFERENCES guards_profile(id) ON DELETE CASCADE,
    document_type   VARCHAR(25)  NOT NULL
                                 CHECK (document_type IN
                                   ('GOVT_ID','POLICE_CERT','PSARA_LICENSE',
                                    'TRAINING_CERT','ARMED_LICENSE','PROFILE_PHOTO','ADDRESS_PROOF')),
    file            VARCHAR(512) NOT NULL,                  -- S3 key (private bucket)
    file_name       VARCHAR(255) NOT NULL,
    status          VARCHAR(15)  NOT NULL DEFAULT 'UPLOADED'
                                 CHECK (status IN
                                   ('UPLOADED','UNDER_REVIEW','APPROVED','REJECTED','EXPIRED')),
    expiry_date     DATE,
    expiry_reminder_sent BOOLEAN NOT NULL DEFAULT FALSE,

    -- Admin review
    reviewed_by_id  UUID         REFERENCES users_profile(id) ON DELETE SET NULL,
    review_notes    TEXT         NOT NULL DEFAULT '',
    reviewed_at     TIMESTAMPTZ,

    uploaded_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),    -- alias for created_at
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    UNIQUE (guard_id, document_type)                        -- one doc per type per guard
);

CREATE INDEX idx_guard_doc_status   ON guards_document (status, created_at DESC);
CREATE INDEX idx_guard_doc_expiry   ON guards_document (expiry_date)
    WHERE expiry_date IS NOT NULL AND status = 'APPROVED';
```

---

## 10. guards_availability

Recurring weekly availability schedule.

```sql
CREATE TABLE guards_availability (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    guard_id    UUID        NOT NULL REFERENCES guards_profile(id) ON DELETE CASCADE,
    weekday     SMALLINT    NOT NULL CHECK (weekday BETWEEN 0 AND 6),  -- 0=Mon, 6=Sun
    start_time  TIME        NOT NULL,
    end_time    TIME        NOT NULL,
    is_available BOOLEAN    NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (guard_id, weekday),
    CHECK (end_time > start_time)
);
```

---

## 11. guards_blackout_date

Specific unavailable dates for a guard.

```sql
CREATE TABLE guards_blackout_date (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    guard_id   UUID        NOT NULL REFERENCES guards_profile(id) ON DELETE CASCADE,
    date       DATE        NOT NULL,
    reason     VARCHAR(200) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (guard_id, date)
);

CREATE INDEX idx_blackout_guard_date ON guards_blackout_date (guard_id, date);
```

---

## 12. bookings_booking

Core transaction record. Uses FSM for state management.

```sql
CREATE TABLE bookings_booking (
    id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Participants
    user_id               UUID         NOT NULL REFERENCES users_profile(id) ON DELETE RESTRICT,
    guard_id              UUID         REFERENCES guards_profile(id) ON DELETE RESTRICT,

    -- Service details
    service_type          VARCHAR(10)  NOT NULL
                                       CHECK (service_type IN ('HOURLY','DAILY','WEEKLY','MONTHLY')),
    guard_type_requested  VARCHAR(10)  NOT NULL
                                       CHECK (guard_type_requested IN
                                         ('UNARMED','ARMED','FEMALE','CPO','EVENT')),

    -- State machine field
    status                VARCHAR(15)  NOT NULL DEFAULT 'REQUESTED'
                                       CHECK (status IN
                                         ('REQUESTED','BROADCAST','ACCEPTED','EN_ROUTE',
                                          'ARRIVED','ACTIVE','COMPLETED','CANCELLED',
                                          'DISPUTED','EXPIRED')),

    -- Scheduling
    scheduled_start       TIMESTAMPTZ  NOT NULL,
    scheduled_end         TIMESTAMPTZ  NOT NULL,
    is_immediate          BOOLEAN      NOT NULL DEFAULT TRUE,

    -- Session lifecycle timestamps
    guard_accepted_at     TIMESTAMPTZ,
    guard_arrived_at      TIMESTAMPTZ,
    session_started_at    TIMESTAMPTZ,
    session_ended_at      TIMESTAMPTZ,

    -- Service location
    service_address       TEXT         NOT NULL,
    service_latitude      NUMERIC(9,6) NOT NULL,
    service_longitude     NUMERIC(9,6) NOT NULL,

    -- Pricing
    base_rate_per_hour    NUMERIC(8,2) NOT NULL,
    surge_multiplier      NUMERIC(4,2) NOT NULL DEFAULT 1.00,
    promo_discount        NUMERIC(8,2) NOT NULL DEFAULT 0.00,
    total_amount          NUMERIC(10,2),
    platform_fee          NUMERIC(8,2),
    guard_earnings        NUMERIC(8,2),
    tax_amount            NUMERIC(8,2),

    -- OTP verification (hashed)
    start_otp_hash        CHAR(64)     NOT NULL DEFAULT '',
    end_otp_hash          CHAR(64)     NOT NULL DEFAULT '',

    -- Cancellation
    cancelled_by_id       UUID         REFERENCES users_profile(id) ON DELETE SET NULL,
    cancellation_reason   TEXT         NOT NULL DEFAULT '',
    cancelled_at          TIMESTAMPTZ,

    -- Recurring
    is_recurring          BOOLEAN      NOT NULL DEFAULT FALSE,
    recurrence_rule       JSONB,
    parent_booking_id     UUID         REFERENCES bookings_booking(id) ON DELETE SET NULL,

    -- Invoice
    invoice_s3_key        VARCHAR(512),

    -- Admin
    admin_notes           TEXT         NOT NULL DEFAULT '',
    is_flagged            BOOLEAN      NOT NULL DEFAULT FALSE,

    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    -- Constraints
    CHECK (scheduled_end > scheduled_start)
);

-- Indexes (see indexes.md for full index strategy)
CREATE INDEX idx_booking_user_status     ON bookings_booking (user_id, status, created_at DESC);
CREATE INDEX idx_booking_guard_status    ON bookings_booking (guard_id, status) WHERE guard_id IS NOT NULL;
CREATE INDEX idx_booking_status_time     ON bookings_booking (status, scheduled_start);
CREATE INDEX idx_booking_active          ON bookings_booking (user_id, guard_id, session_started_at)
    WHERE status = 'ACTIVE';
CREATE INDEX idx_booking_recurring       ON bookings_booking (parent_booking_id)
    WHERE is_recurring = TRUE;
```

---

## 13. bookings_broadcast

Tracks which guards received each booking request and their response.

```sql
CREATE TABLE bookings_broadcast (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id           UUID        NOT NULL REFERENCES bookings_booking(id) ON DELETE CASCADE,
    guard_id             UUID        NOT NULL REFERENCES guards_profile(id) ON DELETE CASCADE,
    response             VARCHAR(10) NOT NULL DEFAULT 'SENT'
                                     CHECK (response IN ('SENT','ACCEPTED','DECLINED','TIMEOUT')),
    broadcast_radius_km  SMALLINT    NOT NULL,
    sent_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at         TIMESTAMPTZ,

    UNIQUE (booking_id, guard_id)
);

CREATE INDEX idx_broadcast_booking ON bookings_broadcast (booking_id);
CREATE INDEX idx_broadcast_guard   ON bookings_broadcast (guard_id, sent_at DESC);
```

---

## 14. bookings_checkin

Guard check-ins during long active sessions (daily, weekly, monthly).

```sql
CREATE TABLE bookings_checkin (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id  UUID         NOT NULL REFERENCES bookings_booking(id) ON DELETE CASCADE,
    guard_id    UUID         NOT NULL REFERENCES guards_profile(id) ON DELETE CASCADE,
    latitude    NUMERIC(9,6) NOT NULL,
    longitude   NUMERIC(9,6) NOT NULL,
    notes       VARCHAR(200) NOT NULL DEFAULT '',
    is_auto     BOOLEAN      NOT NULL DEFAULT FALSE,    -- TRUE = system auto-created
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_checkin_booking_time ON bookings_checkin (booking_id, created_at DESC);
```

---

## 15. tracking_location_snapshot

High-volume time-series table. Guard GPS positions during active sessions.

```sql
CREATE TABLE tracking_location_snapshot (
    id               UUID             PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id       UUID             NOT NULL REFERENCES bookings_booking(id) ON DELETE CASCADE,
    guard_id         UUID             NOT NULL REFERENCES guards_profile(id) ON DELETE CASCADE,
    location         GEOGRAPHY(POINT, 4326) NOT NULL,   -- PostGIS point (lng, lat)
    accuracy_meters  REAL,
    speed_kmh        REAL,
    bearing_degrees  REAL,
    timestamp        TIMESTAMPTZ      NOT NULL,          -- Explicit (not created_at) for replay accuracy
    created_at       TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- Primary query pattern: all points for a session in time order
CREATE INDEX idx_location_booking_time
    ON tracking_location_snapshot (booking_id, timestamp ASC);

-- Guard history queries
CREATE INDEX idx_location_guard_time
    ON tracking_location_snapshot (guard_id, timestamp DESC);

-- Partition by month to manage growth (optional — enable when table > 50M rows)
-- CREATE TABLE tracking_location_snapshot_2026_01 PARTITION OF tracking_location_snapshot
--     FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

**Retention policy:** Rows older than 90 days deleted weekly by Celery task.
**Volume:** ~1 update/4 seconds per active guard = ~21,600 rows/guard/day

---

## 16. payments_wallet

One wallet per user. Balance never goes negative (enforced by `CHECK` and application `SELECT FOR UPDATE`).

```sql
CREATE TABLE payments_wallet (
    id              UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID          NOT NULL UNIQUE REFERENCES users_profile(id) ON DELETE CASCADE,
    balance         NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (balance >= 0),
    locked_balance  NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (locked_balance >= 0),
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
```

---

## 17. payments_transaction

Immutable ledger. Rows are never updated — only inserted.

```sql
CREATE TABLE payments_transaction (
    id                    UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id             UUID          NOT NULL REFERENCES payments_wallet(id) ON DELETE RESTRICT,
    transaction_type      VARCHAR(20)   NOT NULL
                                        CHECK (transaction_type IN
                                          ('TOPUP','BOOKING_DEBIT','BOOKING_LOCK','BOOKING_UNLOCK',
                                           'REFUND','PROMO_CREDIT','REFERRAL_BONUS',
                                           'ADMIN_CREDIT','ADMIN_DEBIT')),
    amount                NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    balance_before        NUMERIC(10,2) NOT NULL,
    balance_after         NUMERIC(10,2) NOT NULL,
    status                VARCHAR(10)   NOT NULL DEFAULT 'PENDING'
                                        CHECK (status IN ('PENDING','SUCCESS','FAILED','REFUNDED')),
    booking_id            UUID          REFERENCES bookings_booking(id) ON DELETE SET NULL,
    gateway               VARCHAR(10)   NOT NULL DEFAULT 'INTERNAL'
                                        CHECK (gateway IN ('RAZORPAY','STRIPE','INTERNAL')),
    gateway_order_id      VARCHAR(100)  NOT NULL DEFAULT '',
    gateway_payment_id    VARCHAR(100)  NOT NULL DEFAULT '',
    gateway_signature     VARCHAR(256)  NOT NULL DEFAULT '',
    description           VARCHAR(255)  NOT NULL DEFAULT '',
    admin_note            TEXT          NOT NULL DEFAULT '',
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_txn_wallet_time       ON payments_transaction (wallet_id, created_at DESC);
CREATE INDEX idx_txn_booking           ON payments_transaction (booking_id, transaction_type);
CREATE INDEX idx_txn_gateway_payment   ON payments_transaction (gateway_payment_id)
    WHERE gateway_payment_id != '';
CREATE INDEX idx_txn_status_type       ON payments_transaction (status, transaction_type);
```

---

## 18. payments_order

Payment gateway order before payment is completed.

```sql
CREATE TABLE payments_order (
    id                UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID          NOT NULL REFERENCES users_profile(id) ON DELETE RESTRICT,
    amount            NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    currency          CHAR(3)       NOT NULL DEFAULT 'INR',
    purpose           VARCHAR(20)   NOT NULL DEFAULT 'WALLET_TOPUP'
                                    CHECK (purpose IN ('WALLET_TOPUP','BOOKING')),
    status            VARCHAR(10)   NOT NULL DEFAULT 'CREATED'
                                    CHECK (status IN ('CREATED','ATTEMPTED','PAID','FAILED','EXPIRED')),
    gateway           VARCHAR(10)   NOT NULL CHECK (gateway IN ('RAZORPAY','STRIPE')),
    gateway_order_id  VARCHAR(100)  NOT NULL UNIQUE,
    gateway_response  JSONB,
    booking_id        UUID          REFERENCES bookings_booking(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_order_user_status       ON payments_order (user_id, status);
CREATE INDEX idx_order_gateway_order_id  ON payments_order (gateway_order_id);
```

---

## 19. payments_payout

Earnings payouts to guards via bank transfer or UPI.

```sql
CREATE TABLE payments_payout (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    guard_id            UUID          NOT NULL REFERENCES guards_profile(id) ON DELETE RESTRICT,
    amount              NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    status              VARCHAR(15)   NOT NULL DEFAULT 'PENDING'
                                      CHECK (status IN
                                        ('PENDING','PROCESSING','COMPLETED','FAILED','ON_HOLD')),
    period_start        DATE          NOT NULL,
    period_end          DATE          NOT NULL,
    razorpay_payout_id  VARCHAR(100)  NOT NULL DEFAULT '',
    bank_reference      VARCHAR(100)  NOT NULL DEFAULT '',
    failure_reason      TEXT          NOT NULL DEFAULT '',
    processed_at        TIMESTAMPTZ,
    processed_by_id     UUID          REFERENCES users_profile(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CHECK (period_end >= period_start),
    UNIQUE (guard_id, period_start, period_end)        -- Prevent duplicate payouts for same period
);

CREATE INDEX idx_payout_guard_status  ON payments_payout (guard_id, status);
CREATE INDEX idx_payout_status_period ON payments_payout (status, period_start);
```

---

## 20. payments_payout_bookings (M2M)

Junction table linking payouts to the bookings they cover.

```sql
CREATE TABLE payments_payout_bookings (
    id         BIGSERIAL   PRIMARY KEY,
    payout_id  UUID        NOT NULL REFERENCES payments_payout(id) ON DELETE CASCADE,
    booking_id UUID        NOT NULL REFERENCES bookings_booking(id) ON DELETE CASCADE,

    UNIQUE (payout_id, booking_id)
);

CREATE INDEX idx_payout_booking_payout   ON payments_payout_bookings (payout_id);
CREATE INDEX idx_payout_booking_booking  ON payments_payout_bookings (booking_id);
```

---

## 21. notifications_log

Full audit trail of every notification sent.

```sql
CREATE TABLE notifications_log (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id         UUID        NOT NULL REFERENCES users_profile(id) ON DELETE CASCADE,
    channel              VARCHAR(10) NOT NULL
                                     CHECK (channel IN ('PUSH','SMS','EMAIL','IN_APP','WHATSAPP')),
    notification_type    VARCHAR(50) NOT NULL,
    title                VARCHAR(255) NOT NULL DEFAULT '',
    body                 TEXT        NOT NULL,
    data                 JSONB       NOT NULL DEFAULT '{}',
    status               VARCHAR(10) NOT NULL DEFAULT 'QUEUED'
                                     CHECK (status IN ('QUEUED','SENT','DELIVERED','FAILED','BOUNCED')),
    provider_message_id  VARCHAR(255) NOT NULL DEFAULT '',
    failure_reason       TEXT        NOT NULL DEFAULT '',
    is_read              BOOLEAN     NOT NULL DEFAULT FALSE,
    read_at              TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Unread in-app notifications (badge count + inbox query)
CREATE INDEX idx_notif_unread
    ON notifications_log (recipient_id, created_at DESC)
    WHERE is_read = FALSE AND channel = 'IN_APP';

CREATE INDEX idx_notif_type_status  ON notifications_log (notification_type, status);
```

---

## 22. notifications_preference

User opt-in/out settings per notification channel.

```sql
CREATE TABLE notifications_preference (
    id               UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID    NOT NULL UNIQUE REFERENCES users_profile(id) ON DELETE CASCADE,
    push_enabled     BOOLEAN NOT NULL DEFAULT TRUE,
    sms_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    email_enabled    BOOLEAN NOT NULL DEFAULT TRUE,
    marketing_push   BOOLEAN NOT NULL DEFAULT FALSE,
    marketing_email  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 23. sos_alert

Mission-critical SOS events. Writes are always synchronous.

```sql
CREATE TABLE sos_alert (
    id                       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                  UUID         NOT NULL REFERENCES users_profile(id) ON DELETE RESTRICT,
    booking_id               UUID         REFERENCES bookings_booking(id) ON DELETE SET NULL,
    trigger_method           VARCHAR(20)  NOT NULL
                                          CHECK (trigger_method IN
                                            ('BUTTON','SHAKE','AUTO_CHECKIN',
                                             'GUARD_OFFLINE','GUARD_DISTRESS')),
    status                   VARCHAR(15)  NOT NULL DEFAULT 'TRIGGERED'
                                          CHECK (status IN
                                            ('TRIGGERED','ACKNOWLEDGED','RESPONDING',
                                             'RESOLVED','FALSE_ALARM')),

    -- Location at time of trigger
    latitude                 NUMERIC(9,6) NOT NULL,
    longitude                NUMERIC(9,6) NOT NULL,
    location_accuracy_meters REAL,

    -- Response tracking
    assigned_to_id           UUID         REFERENCES users_profile(id) ON DELETE SET NULL,
    acknowledged_at          TIMESTAMPTZ,
    resolved_at              TIMESTAMPTZ,
    resolution_notes         TEXT         NOT NULL DEFAULT '',

    -- Optional audio recording
    recording_file           VARCHAR(512),                    -- S3 key

    created_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Open alerts only (small set, always fast)
CREATE INDEX idx_sos_open
    ON sos_alert (created_at DESC)
    WHERE status NOT IN ('RESOLVED', 'FALSE_ALARM');

CREATE INDEX idx_sos_user    ON sos_alert (user_id, created_at DESC);
CREATE INDEX idx_sos_booking ON sos_alert (booking_id) WHERE booking_id IS NOT NULL;
```

---

## 24. sos_emergency_contact_alert

Tracks which emergency contacts were notified per SOS.

```sql
CREATE TABLE sos_emergency_contact_alert (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sos_alert_id    UUID        NOT NULL REFERENCES sos_alert(id) ON DELETE CASCADE,
    contact_name    VARCHAR(150) NOT NULL,
    contact_phone   VARCHAR(20) NOT NULL,
    sms_sent        BOOLEAN     NOT NULL DEFAULT FALSE,
    sms_delivered   BOOLEAN     NOT NULL DEFAULT FALSE,
    call_attempted  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sos_contact_sos ON sos_emergency_contact_alert (sos_alert_id);
```

---

## 25. sos_incident

User or guard filed incident reports (retrospective, separate from SOS).

```sql
CREATE TABLE sos_incident (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id     UUID         NOT NULL REFERENCES bookings_booking(id) ON DELETE RESTRICT,
    filed_by_id    UUID         NOT NULL REFERENCES users_profile(id) ON DELETE RESTRICT,
    incident_type  VARCHAR(30)  NOT NULL
                                CHECK (incident_type IN
                                  ('GUARD_MISCONDUCT','GUARD_NO_SHOW','GUARD_EARLY_DEPARTURE',
                                   'THREATENING_BEHAVIOUR','THEFT','PROPERTY_DAMAGE',
                                   'DANGEROUS_CLIENT','SAFETY_CONCERN','OTHER')),
    severity       VARCHAR(10)  NOT NULL DEFAULT 'MEDIUM'
                                CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    description    TEXT         NOT NULL,
    status         VARCHAR(15)  NOT NULL DEFAULT 'OPEN'
                                CHECK (status IN ('OPEN','IN_REVIEW','RESOLVED','CLOSED')),
    assigned_to_id UUID         REFERENCES users_profile(id) ON DELETE SET NULL,
    resolution_notes TEXT       NOT NULL DEFAULT '',
    resolved_at    TIMESTAMPTZ,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_incident_status   ON sos_incident (status, created_at DESC);
CREATE INDEX idx_incident_booking  ON sos_incident (booking_id);
CREATE INDEX idx_incident_severity ON sos_incident (severity, status);
```

---

## 26. sos_incident_evidence

Photo/video evidence attached to incidents.

```sql
CREATE TABLE sos_incident_evidence (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id  UUID        NOT NULL REFERENCES sos_incident(id) ON DELETE CASCADE,
    file         VARCHAR(512) NOT NULL,                  -- S3 key
    file_type    VARCHAR(10) NOT NULL CHECK (file_type IN ('IMAGE','VIDEO')),
    description  VARCHAR(255) NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_incident ON sos_incident_evidence (incident_id);
```

---

## 27. reviews_review

Post-session ratings. One review per completed booking.

```sql
CREATE TABLE reviews_review (
    id                     UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id             UUID       NOT NULL UNIQUE REFERENCES bookings_booking(id) ON DELETE RESTRICT,
    reviewer_id            UUID       NOT NULL REFERENCES users_profile(id) ON DELETE RESTRICT,
    guard_id               UUID       NOT NULL REFERENCES guards_profile(id) ON DELETE RESTRICT,

    -- Ratings 1-5
    overall_rating         SMALLINT   NOT NULL CHECK (overall_rating BETWEEN 1 AND 5),
    punctuality_rating     SMALLINT   CHECK (punctuality_rating BETWEEN 1 AND 5),
    professionalism_rating SMALLINT   CHECK (professionalism_rating BETWEEN 1 AND 5),
    communication_rating   SMALLINT   CHECK (communication_rating BETWEEN 1 AND 5),
    alertness_rating       SMALLINT   CHECK (alertness_rating BETWEEN 1 AND 5),

    comment                VARCHAR(1000) NOT NULL DEFAULT '',
    is_flagged             BOOLEAN    NOT NULL DEFAULT FALSE,
    flag_reason            VARCHAR(255) NOT NULL DEFAULT '',
    is_hidden              BOOLEAN    NOT NULL DEFAULT FALSE,

    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_review_guard        ON reviews_review (guard_id, overall_rating DESC, created_at DESC);
CREATE INDEX idx_review_reviewer     ON reviews_review (reviewer_id);
CREATE INDEX idx_review_flagged      ON reviews_review (is_flagged) WHERE is_flagged = TRUE;
```

**Trigger to update guard's `average_rating` after insert/update:**

```sql
CREATE OR REPLACE FUNCTION update_guard_average_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE guards_profile
    SET
        average_rating = (
            SELECT COALESCE(AVG(overall_rating::NUMERIC), 0)
            FROM reviews_review
            WHERE guard_id = NEW.guard_id AND is_hidden = FALSE
        ),
        total_reviews = (
            SELECT COUNT(*)
            FROM reviews_review
            WHERE guard_id = NEW.guard_id AND is_hidden = FALSE
        )
    WHERE id = NEW.guard_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_guard_rating
    AFTER INSERT OR UPDATE ON reviews_review
    FOR EACH ROW EXECUTE FUNCTION update_guard_average_rating();
```

---

## 28. analytics_daily_stats

Pre-aggregated daily metrics for instant admin dashboard reads.

```sql
CREATE TABLE analytics_daily_stats (
    id                     BIGSERIAL     PRIMARY KEY,
    date                   DATE          NOT NULL UNIQUE,

    -- Bookings
    total_bookings         INTEGER       NOT NULL DEFAULT 0,
    completed_bookings     INTEGER       NOT NULL DEFAULT 0,
    cancelled_bookings     INTEGER       NOT NULL DEFAULT 0,
    disputed_bookings      INTEGER       NOT NULL DEFAULT 0,
    hourly_bookings        INTEGER       NOT NULL DEFAULT 0,
    daily_bookings         INTEGER       NOT NULL DEFAULT 0,
    weekly_bookings        INTEGER       NOT NULL DEFAULT 0,
    monthly_bookings       INTEGER       NOT NULL DEFAULT 0,

    -- Revenue
    gross_revenue          NUMERIC(12,2) NOT NULL DEFAULT 0,
    platform_fees_collected NUMERIC(12,2) NOT NULL DEFAULT 0,
    guard_earnings_paid    NUMERIC(12,2) NOT NULL DEFAULT 0,
    refunds_issued         NUMERIC(12,2) NOT NULL DEFAULT 0,

    -- Users & Guards
    new_users              INTEGER       NOT NULL DEFAULT 0,
    active_users           INTEGER       NOT NULL DEFAULT 0,
    new_guards             INTEGER       NOT NULL DEFAULT 0,
    active_guards          INTEGER       NOT NULL DEFAULT 0,

    -- Safety
    sos_alerts             INTEGER       NOT NULL DEFAULT 0,
    incidents_filed        INTEGER       NOT NULL DEFAULT 0,

    created_at             TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_daily_stats_date ON analytics_daily_stats (date DESC);
```

---

## 29. Django System Tables

Django creates these automatically. Documented here for completeness.

| Table | Purpose |
|---|---|
| `django_migrations` | Migration history — which migrations have been applied |
| `django_content_type` | Content type framework — used by permissions |
| `auth_permission` | Permission definitions |
| `auth_group` | User groups |
| `auth_group_permissions` | M2M: groups ↔ permissions |
| `users_profile_groups` | M2M: users ↔ groups |
| `users_profile_user_permissions` | M2M: users ↔ direct permissions |
| `django_session` | Server-side sessions (if not using JWT-only) |
| `django_admin_log` | Django admin action log |
| `token_blacklist_outstandingtoken` | JWT outstanding tokens (SimpleJWT) |
| `token_blacklist_blacklistedtoken` | Blacklisted refresh tokens (SimpleJWT) |
| `django_celery_beat_periodictask` | Celery beat schedule (stored in DB) |
| `django_celery_beat_crontabschedule` | Crontab schedule definitions |
| `django_celery_results_taskresult` | Celery task result storage |
