from decimal import Decimal
from locale import currency
from fastapi import HTTPException, status, Form
from jwt.exceptions import InvalidTokenError
from typing import List
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends
from pytest import Session
from core.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import db_helper
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload
from crud.wallet import create_currency, create_wallet

from core.models import Wallet, Currency

router = APIRouter(prefix="", tags=["wallet"])


class WalletResponse(BaseModel):
    name: str
    id: int


class CurrencyCreate(BaseModel):
    label: str
    amount: Decimal
    wallet_id: int


class WalletCreate(BaseModel):
    name: str
    user_id: int


class CurrencyResponse(BaseModel):
    label: str
    amount: Decimal


@router.post("/wallet", response_model=WalletResponse)
async def create_wallet_endpoint(
    wallet: WalletCreate, db: AsyncSession = Depends(db_helper.get_session_getter)
):
    stmt = await db.execute(select(User).where(User.id == wallet.user_id))
    user = stmt.scalar_one_or_none()
    if not user:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="no such user"
        )
    wallet = await create_wallet(session=db, user_id=wallet.user_id, name=wallet.name)
    return wallet


@router.post("/currency", response_model=CurrencyResponse)
async def create_currency_endpoint(
    currency: CurrencyCreate, db: AsyncSession = Depends(db_helper.get_session_getter)
):
    stmt = await db.execute(select(Wallet).where(Wallet.id == currency.wallet_id))
    wallet = stmt.scalar_one_or_none()
    if not wallet:
        return HTTPException(detail="no such wallet")
    currency = await create_currency(
        session=db,
        wallet_id=currency.wallet_id,
        label=currency.label,
        amount=currency.amount,
    )
    return currency


@router.get("/users/{username}/wallets", response_model=List[WalletResponse])
async def get_wallets_by_username(
    username: str, db: AsyncSession = Depends(db_helper.get_session_getter)
):
    result = await db.execute(
        select(User)
        .where(User.username == username)
        .options(selectinload(User.wallets))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.wallets


@router.get("/wallets/{wallet_name}/currencies", response_model=List[CurrencyResponse])
async def get_currencies_by_wallet_id(
    wallet_name: str, db: AsyncSession = Depends(db_helper.get_session_getter)
):
    result = await db.execute(
        select(Wallet)
        .where(Wallet.name == wallet_name)
        .options(selectinload(Wallet.currencies))
    )

    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="wallet not found")
    return [cur for cur in wallet.currencies]


# Currency Endpoints
# --------------------------------------------------


@router.get("/users/{username}/currencies", response_model=List[CurrencyResponse])
async def get_user_currencies(
    username: str, db: AsyncSession = Depends(db_helper.get_session_getter)
):
    # Get user with wallets and their currencies
    stmt = (
        select(User)
        .options(selectinload(User.wallets).selectinload(Wallet.currencies))
        .where(User.username == username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    print([[cur for cur in wallet.currencies] for wallet in user.wallets], "here")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Extract unique currencies using dictionary comprehension
    return list(
        {
            currency.id: currency
            for wallet in user.wallets
            for currency in [wallet.currencies]
        }.values()
    )
