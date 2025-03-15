from fastapi.concurrency import asynccontextmanager
import uvicorn
from fastapi import FastAPI
import logging
from api import router as api_router
from core.config import settings
from core.models import db_helper, Base, User


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
main_app.include_router(api_router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app", reload=True, host=settings.run.host, port=settings.run.port
    )
