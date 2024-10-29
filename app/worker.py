"""Celery worker for the application."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Worker configurations:

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "fetch-events-every-hour": {
        "task": "app.tasks.fetch_events.fetch_events_task",
        "schedule": float(settings.CELERY_FETCH_EVENTS_SCHEDULE),
    },
}

celery_app.conf.beat_schedule_filename = (
    "/app/celerybeat-schedule/celerybeat-schedule"  # noqa: E501
)
celery_app.conf.beat_scheduler = "celery.beat.PersistentScheduler"

celery_app.conf.broker_connection_retry_on_startup = True

celery_app.autodiscover_tasks(["app.tasks.fetch_events"])
