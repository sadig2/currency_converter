from fastapi import APIRouter, Depends
from crud.users import get_all_users, create_user
from core.schemas.user import UserRead, UserCreate
from typing import List
from core.models import db_helper


router = APIRouter(tags=["Users"])


@router.get("", response_model=List[UserRead])
async def get_users(session=Depends(db_helper.get_session_getter)):
    users = await get_all_users(session=session)
    return users


@router.post("", response_model=UserRead)
async def create_users(
    user_create: UserCreate,
    session=Depends(db_helper.get_session_getter),
):
    user = await create_user(session=session, user_create=user_create)

    return user
