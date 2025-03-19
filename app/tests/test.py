# tests/test_api.py
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.models import User, Wallet, Currency
from main import main_app
from api.wallet_api import CurrencyCreate, WalletResponse
import asyncio


# Fixtures
@pytest.fixture(scope="function")
async def test_user(async_session: AsyncSession):
    user = User(email="test@example.com", hashed_password="fakehashed")
    async_session.add(user)
    await async_session.commit()
    return user


@pytest.fixture(scope="function")
async def test_wallet(async_session: AsyncSession, test_user: User):
    wallet = Wallet(name="test_wallet", user_id=test_user.id)
    async_session.add(wallet)
    await async_session.commit()
    return wallet


@pytest.fixture(scope="function")
async def test_currency(async_session: AsyncSession, test_wallet: Wallet):
    currency = Currency(wallet_id=test_wallet.id, label="USD", amount=100.0)
    async_session.add(currency)
    await async_session.commit()
    return currency


# Auth override
async def override_current_user():
    return User(id=1, email="test@example.com")


async def override_get_session_getter():
    # Use your actual session getter override
    pass


main_app.dependency_overrides[get_current_auth_user] = override_current_user


# Tests
class TestCurrencyEndpoints:
    async def test_create_currency(
        self, async_client: AsyncClient, test_wallet: Wallet
    ):
        currency_data = {"wallet_id": test_wallet.id, "label": "EUR", "amount": 500.0}
        response = await async_client.post("/currency", json=currency_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["label"] == "EUR"
        assert data["amount"] == 500.0

    async def test_create_currency_invalid_wallet(self, async_client: AsyncClient):
        response = await async_client.post(
            "/currency", json={"wallet_id": 9999, "label": "EUR", "amount": 100.0}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestWalletEndpoints:
    async def test_get_wallets(
        self, async_client: AsyncClient, test_user: User, test_wallet: Wallet
    ):
        response = await async_client.get("/wallets")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "test_wallet"

    async def test_get_wallet_currencies(
        self, async_client: AsyncClient, test_wallet: Wallet, test_currency: Currency
    ):
        response = await async_client.get(f"/wallets/{test_wallet.name}/currencies")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["label"] == "USD"


class TestConversionEndpoints:
    @pytest.fixture(autouse=True)
    def mock_redis(self, mocker):
        mock_redis = mocker.patch("app.api.endpoints.get_mid_rates")
        mock_redis.return_value = {"USD": 3.95, "EUR": 4.45}
        return mock_redis

    async def test_get_converted_currencies(
        self, async_client: AsyncClient, test_currency: Currency
    ):
        response = await async_client.get("/currencies_converted")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sum"] == "395.00"
        assert len(data["currencies"]) == 1
        assert data["currencies"][0]["label"] == "PLN"

    async def test_get_wallet_converted_currencies(
        self, async_client: AsyncClient, test_wallet: Wallet, test_currency: Currency
    ):
        response = await async_client.get(
            f"/wallets/{test_wallet.name}/currencies_converted"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sum"] == "395.00"
        assert len(data["currencies"]) == 1
