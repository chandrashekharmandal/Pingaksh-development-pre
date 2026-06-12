"""
config package.

Exports the Celery app so that it's available as `config.celery_app`
and auto-discovered when Django starts.
"""

from celery_app import app as celery_app

__all__ = ("celery_app",)
