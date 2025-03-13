import asyncio
from decimal import Decimal
import select
from sqlalchemy import delete

from sqlalchemy.ext.asyncio import AsyncSession


from core.models import User, Wallet, db_helper


async def delete_users(session: AsyncSession):
    try:
        await session.execute(delete(User))
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


async def create_wallet(
    session: AsyncSession, user_id: int, currency: str, amount: Decimal
):
    wallet = Wallet(user_id=user_id, currency=currency, amount=amount)
    session.add(wallet)
    await session.commit()
    return wallet


async def create_user(session: AsyncSession, username: str, email: str, password: str):
    user = User(username=username, email=email, password=password)
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

        await create_wallet(session, user_id=user1.id, currency="usd", amount=1000)
        await create_wallet(session, user_id=user2.id, currency="eur", amount=5000)


if __name__ == "__main__":
    asyncio.run(main())
