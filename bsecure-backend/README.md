# b-secure Backend

Django 5.x + Django REST Framework + Django Channels backend for the b-secure security guard booking platform.

## Quick Start

```bash
# 1. Copy environment file
cp .env.example .env
# Edit .env with your values

# 2. Start infrastructure
docker-compose up -d db redis

# 3. Install dependencies
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements/development.txt

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start API server
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# 7. Start Celery worker (separate terminal)
celery -A celery_app worker -Q high_priority,default,low_priority -l info

# 8. Start Celery beat (separate terminal)
celery -A celery_app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Run Tests

```bash
pytest --cov=apps --cov-report=term-missing -v
```

## Documentation

See `docs/backend/` for full documentation.
