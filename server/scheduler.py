"""
News Scheduler
============
APScheduler integration for automatic news processing.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from server.services.automation import automation_service

logger = logging.getLogger(__name__)

scheduler = None


def init_scheduler():
    """Initialize and start the background scheduler."""
    global scheduler

    if scheduler and scheduler.running:
        return scheduler

    config = automation_service.get_status()
    if not config.get("enabled"):
        logger.info("Automation disabled, scheduler not started")
        return None

    interval_hours = config.get("interval_hours", 6)

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=run_automation,
        trigger=IntervalTrigger(hours=interval_hours),
        id="news_automation",
        name="News automation",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()

    logger.info(f"Scheduler started: runs every {interval_hours} hours")
    return scheduler


def run_automation():
    """Run the automation job (used by scheduler)."""
    logger.info("Running scheduled news automation...")
    result = automation_service.run_once()
    logger.info(f"Automation complete: {result}")
    return result


def shutdown_scheduler():
    """Shut down the scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None
