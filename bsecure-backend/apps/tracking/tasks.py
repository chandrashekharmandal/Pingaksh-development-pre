"""
Celery tasks for the tracking app.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="apps.tracking.tasks.sync_guard_online_status")
def sync_guard_online_status():
    """
    Reconcile the bsecure:online:guards SET with heartbeat keys.
    Removes guards whose heartbeat key has expired (stale entries).
    Runs every 60 seconds via Celery beat.
    """
    try:
        from apps.tracking.online_status import sync_online_set

        removed = sync_online_set()
        if removed:
            logger.info(f"Removed {removed} stale guard(s) from online set")
        return {"removed": removed}
    except Exception as e:
        logger.error(f"Failed to sync guard online status: {e}")
        raise
