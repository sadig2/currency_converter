import asyncio
from decimal import Decimal
from auth.utils import hash_password
from sqlalchemy import delete

from sqlalchemy.ext.asyncio import AsyncSession


from core.models import User, Wallet, db_helper, Currency


async def delete_users(session: AsyncSession):
    try:
        await session.execute(delete(User))
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


async def create_currency(
    session: AsyncSession, wallet_id: int, label: str, amount: Decimal
):
    currency = Currency(wallet_id=wallet_id, label=label, amount=amount)
    session.add(currency)
    await session.commit()
    return currency


async def create_wallet(session: AsyncSession, user_id: int, name: str):
    wallet = Wallet(user_id=user_id, name=name)
    session.add(wallet)
    await session.commit()
    return wallet
