import asyncio
from decimal import ROUND_HALF_UP
from decimal import Decimal
import json
from locale import currency
from math import log
from fastapi import HTTPException, status, Form
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from core.models import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import UniqueConstraint, select
from core.models import db_helper
from .auth_endpoint.auth import UserCreate
from sqlalchemy.orm import selectinload
from crud.wallet import create_currency, create_wallet
from .auth_endpoint.auth import get_current_token_payload
from redis.asyncio import Redis
from .auth_endpoint.auth import UserCreate, get_current_auth_user
from core.config import settings


import logging
from core.models import Wallet, Currency

router = APIRouter(prefix="", tags=["wallet"])


class WalletResponse(BaseModel):
    user_id: int
    name: str
    id: int


class CurrencyCreate(BaseModel):
    label: str
    amount: Decimal
    wallet_id: int


class WalletCreate(BaseModel):
    name: str


class CurrencyResponse(BaseModel):
    id: int
    label: str
    amount: Decimal


class CurrencyAmount(BaseModel):
    amount: Decimal


class Converted(BaseModel):
    currencies: List[CurrencyResponse]
    sum: Decimal


@router.post("/wallet", response_model=WalletResponse)
async def create_wallet_endpoint(
    wallet: WalletCreate,
    db: AsyncSession = Depends(db_helper.get_session_getter),
    payload: dict = Depends(get_current_token_payload),
    user: UserCreate = Depends(get_current_auth_user),
):
    try:

        wallet = await create_wallet(session=db, user_id=user.id, name=wallet.name)

    except IntegrityError:
        logging.error("can't create wallet with same name ")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="can't create wallet because of unique constraints",
        )
    return wallet


@router.patch(
    "/currency/add_or_withdraw_funds/{currency_id}", response_model=CurrencyResponse
)
async def update_currency_amount(
    currency_id: int,
    currency_data: CurrencyAmount,
    db: AsyncSession = Depends(db_helper.get_session_getter),
    user: UserCreate = Depends(get_current_auth_user),
):
    try:
        result = await db.execute(
            select(Currency)
            .join(Wallet, Currency.wallet_id == Wallet.id)
            .filter(Currency.id == currency_id, Wallet.user_id == user.id)
            .with_for_update()
        )
        currency = result.scalar_one_or_none()

        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        if currency_data.amount < 0 and abs(currency_data.amount) > currency.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough funds",
            )
        currency.amount += currency_data.amount
        await db.commit()
        await db.refresh(currency)
        return currency

    except IntegrityError as e:
        await db.rollback()
        logging.error(f"Currency update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Db constrains violation",
        )


@router.put("/wallet/{wallet_id}", response_model=WalletResponse)
async def update_wallet_endpoint(
    wallet_id: int,
    wallet_data: WalletCreate,
    db: AsyncSession = Depends(db_helper.get_session_getter),
    user: UserCreate = Depends(get_current_auth_user),
):
    try:
        result = await db.execute(
            select(Wallet).filter(
                Wallet.id == wallet_id,
                Wallet.user_id == user.id,
            )
        )
        wallet = result.scalar_one_or_none()

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        wallet.name = wallet_data.name
        await db.commit()
        await db.refresh(wallet)
        return wallet

    except IntegrityError as e:
        await db.rollback()
        logging.error(f"Wallet update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet name must be unique for this user",
        )


@router.post("/currency", response_model=CurrencyResponse)
async def create_currency_endpoint(
    currency: CurrencyCreate,
    db: AsyncSession = Depends(db_helper.get_session_getter),
    payload: dict = Depends(get_current_token_payload),
    user: UserCreate = Depends(get_current_auth_user),
):
    stmt = await db.execute(select(Wallet).where(Wallet.id == currency.wallet_id))
    wallet = stmt.scalar_one_or_none()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no such wallet"
        )
    currency = await create_currency(
        session=db,
        wallet_id=currency.wallet_id,
        label=currency.label,
        amount=currency.amount,
    )
    return currency


@router.get("/currencies", response_model=List[CurrencyResponse])
async def get_currencies(
    db: AsyncSession = Depends(db_helper.get_session_getter),
    payload: dict = Depends(get_current_token_payload),
    current_user: UserCreate = Depends(get_current_auth_user),
):
    result = await db.execute(
        select(Wallet)
        .options(selectinload(Wallet.currencies))
        .where(Wallet.user_id == current_user.id)
    )
    wallets = result.scalars().all()
    all_currencies = []
    for wallet in wallets:
        all_currencies.extend(wallet.currencies)

    return all_currencies


async def get_mid_rates():
    redis = Redis.from_url(settings.REDIS_URL, socket_timeout=5)
    if not await redis.ping():
        logging.info("failed connection to redis")
        return

    rates = await redis.hgetall("mids")

    normal_dict = {
        key.decode(): json.loads(value.decode()) for key, value in rates.items()
    }
    return normal_dict


@router.get("/currencies_converted", response_model=Converted)
async def get_converted_currencies(
    db: AsyncSession = Depends(db_helper.get_session_getter),
    payload: dict = Depends(get_current_token_payload),
    current_user: UserCreate = Depends(get_current_auth_user),
):

    db_task = db.execute(
        select(Wallet)
        .options(selectinload(Wallet.currencies))
        .where(Wallet.user_id == current_user.id)
    )
    rates_task = get_mid_rates()

    result, rates = await asyncio.gather(db_task, rates_task)

    wallets = result.scalars().all()
    new_currencies = []
    result_sum = Decimal(0)
    for wallet in wallets:
        for cur in wallet.currencies:
            ratio = rates.get(cur.label.upper())
            new_amount = Decimal(ratio) * cur.amount
            new_amount_rounded = Decimal(new_amount).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            new_cur = CurrencyResponse(amount=new_amount_rounded, label="PLN")
            new_currencies.append(new_cur)
            result_sum += new_amount
            rounded_value = Decimal(result_sum).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
    return Converted(sum=rounded_value, currencies=new_currencies)


@router.get("/wallets", response_model=List[WalletResponse])
async def get_wallets(
    db: AsyncSession = Depends(db_helper.get_session_getter),
    payload: dict = Depends(get_current_token_payload),
    current_user: UserCreate = Depends(get_current_auth_user),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.wallets))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.wallets


@router.get("/wallets/{wallet_name}/currencies", response_model=List[CurrencyResponse])
async def get_currencies_by_wallet_id(
    wallet_name: str,
    db: AsyncSession = Depends(db_helper.get_session_getter),
    payload: dict = Depends(get_current_token_payload),
    user: UserCreate = Depends(get_current_auth_user),
):
    result = await db.execute(
        select(Wallet)
        .options(selectinload(Wallet.currencies))
        .where(Wallet.name == wallet_name, Wallet.user_id == user.id)
    )

    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="wallet not found")
    return [cur for cur in wallet.currencies]


async def get_rates():
    redis = Redis.from_url(settings.REDIS_URL, socket_timeout=5)
    if not await redis.ping():
        logging.info("failed connection to redis")
        return

    rates = await redis.hgetall("trade")

    normal_dict = {
        key.decode(): json.loads(value.decode()) for key, value in rates.items()
    }
    return normal_dict


@router.get("/wallets/{wallet_name}/currencies_converted", response_model=Converted)
async def get_converted_currencies_by_wallet_id(
    wallet_name: str,
    db: AsyncSession = Depends(db_helper.get_session_getter),
    payload: dict = Depends(get_current_token_payload),
    user: UserCreate = Depends(get_current_auth_user),
):
    # iat = payload.get("iat")
    result = await db.execute(
        select(Wallet)
        .options(selectinload(Wallet.currencies))
        .where(Wallet.name == wallet_name, Wallet.user_id == user.id)
    )

    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="wallet not found")

    rates = await get_rates()
    result_sum = Decimal(0)
    converted_currencies = []
    for cur in wallet.currencies:
        conversion_rate = rates.get(cur.label.upper()).get("ask")

        result = cur.amount * Decimal(conversion_rate)

        rounded_value = Decimal(result).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        result_sum += rounded_value
        new_cur = CurrencyResponse(label="PLN", amount=rounded_value)
        converted_currencies.append(new_cur)
    return Converted(currencies=converted_currencies, sum=result_sum)
