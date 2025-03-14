from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from core.schemas.user import UserCreate, UserRead
from core.models.user import User
from auth.utils import hash_password


async def get_user(session: AsyncSession, user: UserRead):
    stmt = select(User).filter(User.email == user.email)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_user_by_username(session: AsyncSession, username: str):
    stmt = select(User).filter(User.username == username)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).order_by(User.id)
    result = await session.scalars(stmt)
    return result.all()


async def create_user(session: AsyncSession, user_create: UserCreate) -> User:
    user_dict = user_create.model_dump()
    user_dict["password"] = hash_password(user_dict["password"]).decode()
    user = User(**user_dict)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
