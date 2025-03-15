import asyncio
from decimal import Decimal
from auth.utils import hash_password
from sqlalchemy import delete
import logging

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


async def create_user(session: AsyncSession, username: str, email: str, password: str):
    user = User(username=username, email=email, password=hash_password(password))
    session.add(user)
    await session.commit()
    return user


async def main():
    async with db_helper.session_factory() as session:
        await delete_users(session=session)
        user1 = await create_user(
            session=session, username="sadig", email="clanzu2", password="qwerty"
        )
        user2 = await create_user(
            session=session, username="nie_sadig", email="yahoo", password="qwerty"
        )

        wallet1 = await create_wallet(session, user_id=user1.id, name="lucky_wallet")
        wallet2 = await create_wallet(session, user_id=user1.id, name="bd")
        wallet3 = await create_wallet(session, user_id=user2.id, name="bad_days")
        wallet4 = await create_wallet(session, user_id=user2.id, name="bd")

        await create_currency(session, wallet_id=wallet1.id, label="usd", amount=245.3)
        await create_currency(session, wallet_id=wallet1.id, label="eur", amount=600)
        await create_currency(session, wallet_id=wallet2.id, label="usd", amount=945.3)
        await create_currency(session, wallet_id=wallet2.id, label="eur", amount=800)
        await create_currency(session, wallet_id=wallet3.id, label="usd", amount=345.3)
        await create_currency(session, wallet_id=wallet3.id, label="eur", amount=300)
        await create_currency(session, wallet_id=wallet4.id, label="eur", amount=533.2)
        await create_currency(session, wallet_id=wallet4.id, label="usd", amount=400.2)

        # print(wallet1.currencies)


if __name__ == "__main__":
    asyncio.run(main())
