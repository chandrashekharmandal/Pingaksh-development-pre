# b-secure Backend — Documentation Index

**Backend:** Django 5.x + Django REST Framework + Django Channels
**Language:** Python 3.12+
**Status:** v1.0.0

---

## Documents in This Folder

| File | What It Covers |
|---|---|
| [overview.md](./overview.md) | Project structure, local setup, settings architecture, URL routing, code conventions |
| [authentication.md](./authentication.md) | OTP login, JWT tokens, Google/Apple social auth, WebSocket auth middleware |
| [models.md](./models.md) | All Django models across every app, FSM states, DB indexes, migration strategy |
| [api_endpoints.md](./api_endpoints.md) | All REST API endpoints with request/response JSON examples, ViewSet code |
| [realtime.md](./realtime.md) | Django Channels WebSocket consumers, Redis channel layer, location tracking protocol |
| [payments.md](./payments.md) | Wallet system, Razorpay/Stripe top-up, booking payments, payouts, invoice PDF |
| [notifications.md](./notifications.md) | FCM push, SMS (Twilio), email (SendGrid), in-app notifications, all task types |
| [sos_and_safety.md](./sos_and_safety.md) | SOS trigger flow, escalation logic, check-in system, dead man's switch, incidents |
| [celery_tasks.md](./celery_tasks.md) | All Celery tasks, queue architecture, beat schedule, reliability patterns |
| [deployment.md](./deployment.md) | Docker, Docker Compose, AWS infrastructure, Nginx, GitHub Actions CI/CD |
| [testing.md](./testing.md) | pytest setup, model/API/service/WebSocket tests, factories, coverage |

---

## Quick Reference

### Start Development

```bash
# 1. Start infrastructure
docker-compose up -d db redis

# 2. Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements/development.txt

# 3. Run migrations
python manage.py migrate

# 4. Start API server
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# 5. Start Celery worker (separate terminal)
celery -A celery_app worker -Q high_priority,default -l info

# 6. Start Celery beat (separate terminal)
celery -A celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Key API Endpoints

| Purpose | Method | Endpoint |
|---|---|---|
| Send OTP | POST | `/api/auth/send-otp/` |
| Verify OTP | POST | `/api/auth/verify-otp/` |
| Create booking | POST | `/api/bookings/` |
| Trigger SOS | POST | `/api/sos/trigger/` |
| Wallet top-up | POST | `/api/payments/wallet/topup/initiate/` |
| Live tracking | WSS | `/ws/tracking/{booking_id}/?token=...` |
| Admin SOS feed | WSS | `/ws/sos/feed/?token=...` |
| Admin dashboard | WSS | `/ws/admin/dashboard/?token=...` |

### Django Apps

```
apps/
├── authentication    OTP, JWT, social auth
├── users             UserProfile, Address, EmergencyContact
├── guards            GuardProfile, GuardDocument, availability
├── bookings          Booking FSM, session OTP, broadcast
├── tracking          LocationSnapshot, WS consumers
├── payments          Wallet, transactions, payouts, invoices
├── notifications     FCM, SMS, email, in-app
├── sos               SOSAlert, Incident, escalation
├── reviews           Post-session ratings
├── admin_panel       Admin-only APIs and WS consumers
└── analytics         Aggregated daily stats
```

### Booking States

```
REQUESTED → BROADCAST → ACCEPTED → EN_ROUTE → ARRIVED → ACTIVE → COMPLETED
                                                                 → DISPUTED
             ↓
           EXPIRED (no guard found)
         ↘ CANCELLED (any state before ACTIVE)
```

### Run Tests

```bash
pytest --cov=apps --cov-report=term-missing -v
```

---

## Related Documentation

- [System Requirements](../system_requirements/requirements.md) — Full product requirements document
