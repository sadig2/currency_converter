from fastapi.concurrency import asynccontextmanager
import uvicorn
from fastapi import FastAPI
import logging
from api import router as api_router
from core.config import settings
from core.models import db_helper, Base, User
from prometheus_client import make_asgi_app, Histogram, Counter
from fastapi import FastAPI, Request
import time  # Added for proper timing


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("report.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # startup
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)

# Prometheus metrics setup
metrics_app = make_asgi_app()
main_app.mount("/metrics", metrics_app)

# Define metrics with appropriate buckets
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint", "status_code"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 5, 10),
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)


@main_app.middleware("http")
async def monitor_requests(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        duration = time.time() - start_time
        # Record metrics with actual status code
        REQUEST_DURATION.labels(method, endpoint, status_code).observe(duration)
        REQUEST_COUNT.labels(method, endpoint, status_code).inc()

    return response


main_app.include_router(api_router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app", reload=True, host=settings.run.host, port=settings.run.port
    )
