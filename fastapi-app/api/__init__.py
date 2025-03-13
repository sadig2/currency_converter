from fastapi import APIRouter
from .api_v1 import router as api_v1_router
from .auth.auth import router as auth_router
from core.config import settings


router = APIRouter(
    prefix=settings.api.prefix,
)
router.include_router(api_v1_router)
router.include_router(auth_router)
