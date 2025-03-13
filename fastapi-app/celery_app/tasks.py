from .worker import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def debug_task():
    logger.info("DEBUG TASK EXECUTED - THIS SHOULD APPEAR IN DOCKER LOGS")
    print("PRINT STATEMENT - THIS SHOULD ALSO APPEAR")
    return "Success"
