from fastapi.concurrency import asynccontextmanager
import uvicorn
from fastapi import FastAPI
import logging
from api import router as api_router
from core.config import settings
from core.models import db_helper, Base, User
from prometheus_client import make_asgi_app, Histogram, Counter
from fastapi import FastAPI, Request


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
main_app.mount("/metrics", metrics_app)  # Endpoint for Prometheus to scrape

# Define metrics
REQUEST_TIME = Histogram(
    "http_request_duration_seconds",
    "Time spent processing a request",
    ["method", "path", "status_code"],
)
REQUEST_COUNT = Counter(
    "http_requests_total", "Total number of requests", ["method", "path", "status_code"]
)


# Middleware to track request time and count
@main_app.middleware("http")
async def monitor_requests(request: Request, call_next):
    method = request.method
    path = request.url.path

    with REQUEST_TIME.labels(method, path, 200).time():
        response = await call_next(request)
        REQUEST_COUNT.labels(method, path, response.status_code).inc()
        return response


main_app.include_router(api_router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app", reload=True, host=settings.run.host, port=settings.run.port
    )
