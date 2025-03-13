from celery import Celery
from celery.signals import after_setup_logger
import logging
from core.config import settings

# Configure logging early
logger = logging.getLogger(__name__)


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["celery_app.tasks"],
)

celery_app.conf.update(
    worker_hijack_root_logger=False,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # "debug-task": {
        #     "task": "celery_app.tasks.debug_task",
        #     "schedule": 3.0,  # Every 30 seconds
        # },
        "money": {
            "task": "celery_app.tasks.update_exchange_rates",
            "schedule": 30.0,
        }
    },
)
