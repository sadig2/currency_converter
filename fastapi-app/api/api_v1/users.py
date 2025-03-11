from fastapi import APIRouter, Depends
from crud.users import get_all_users
from core.schemas.user import UserRead
from typing import List
from core.models import db_helper


router = APIRouter(tags=["Users"])


@router.get("", response_model=List[UserRead])
async def get_users(session=Depends(db_helper.get_session_getter)):
    users = await get_all_users(session=session)
    return users
