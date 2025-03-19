# tests/test_api.py
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.fastapi.main import main_app
from core.models import User, Wallet, Currency
from api.wallet_api import CurrencyCreate, WalletResponse
import asyncio
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.test"))


# Common Fixtures (put in conftest.py)
@pytest.fixture
async def async_client():
    async with AsyncClient(app=main_app, base_url="http://localgost:8000") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_session(test_db):
    async with test_db.session() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def cleanup_db(async_session: AsyncSession):
    yield
    await async_session.rollback()
    # Add more cleanup logic as needed
