from fastapi import APIRouter
from .auth_endpoint.auth import router as auth_router
from .wallet_api import router as wallet_router
from core.config import settings


router = APIRouter(
    prefix="",
)
router.include_router(auth_router)
router.include_router(wallet_router)
