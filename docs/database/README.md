# b-secure — Database Design Index

**Version:** 1.0.0

This folder contains the complete database design documentation for b-secure, split by service.

---

## Folder Structure

```
database/
├── README.md                  ← This file (index + overview)
│
├── postgres/                  ← Primary relational database
│   ├── schema.md              ← All tables, columns, data types, constraints
│   ├── indexes.md             ← Index strategy, GiST spatial indexes, partial indexes
│   ├── migrations.md          ← Migration workflow, PostGIS setup, data migrations
│   └── queries.md             ← Common queries, geospatial queries, analytics
│
├── redis/                     ← In-memory data store (multi-purpose)
│   ├── design.md              ← Key naming, TTLs, data structures, all use cases
│   └── celery_broker.md       ← Celery queue design, task payloads, monitoring
│
└── aws_s3/
    └── design.md              ← Bucket layout, IAM policies, lifecycle rules, access patterns
```

---

## Service Responsibilities

| Service | Role | Data Stored |
|---|---|---|
| **PostgreSQL + PostGIS** | Primary source of truth | All business data: users, guards, bookings, payments, SOS, reviews, analytics |
| **Redis** | Cache + real-time backbone | Sessions, rate limits, Django Channels pub/sub, Celery task queues, guard proximity cache |
| **AWS S3** | Object storage | Guard documents, profile photos, session recordings, invoice PDFs, static assets |

---

## High-Level Data Flow

```
Mobile App / Admin Panel
        │
        ▼
  Django API (DRF)
        │
        ├─── Reads/Writes ──────────────► PostgreSQL (primary data)
        │                                      │
        │                                 Read Replica
        │                                 (analytics queries)
        │
        ├─── Cache Lookups ─────────────► Redis
        │    Rate Limits
        │    Session Tokens
        │
        ├─── WebSocket Pub/Sub ─────────► Redis Channel Layer
        │    (guard location, SOS feed,
        │     admin dashboard events)
        │
        ├─── Async Task Queue ──────────► Redis (Celery broker)
        │    (notifications, payments,
        │     PDF generation)
        │
        └─── File Uploads/Downloads ────► AWS S3
             (documents, photos,
              recordings, invoices)
```

---

## Database Stats Estimates (Year 1 projections)

| Table | Estimated Rows | Growth Rate | Notes |
|---|---|---|---|
| `users_profile` | 100,000 | +5,000/month | Users + guards |
| `guards_profile` | 10,000 | +500/month | 10% of users are guards |
| `bookings_booking` | 500,000 | +50,000/month | Core transaction table |
| `tracking_location_snapshot` | 300,000,000 | ~1M/day | High volume — archived after 90 days |
| `payments_transaction` | 1,500,000 | +150,000/month | 3 transactions per booking avg |
| `notifications_log` | 5,000,000 | +500,000/month | ~10 notifs per booking |
| `sos_sosalert` | 5,000 | ~100/month | Low volume, high priority |

**Storage estimates (Year 1):**
- PostgreSQL: ~50 GB data + ~20 GB indexes
- Redis: ~2 GB peak (mostly ephemeral)
- S3: ~500 GB (documents + recordings + invoices)
