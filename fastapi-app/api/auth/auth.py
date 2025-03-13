from fastapi import HTTPException, status

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from core.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import db_helper

from auth.utils import encode_jwt, validate_password, hash_password
from api.api_v1.crud.users import get_user, create_user


router = APIRouter(prefix="/authenticate", tags=["auth"])


# Schemas
class UserCreate(BaseModel):
    email: str
    password: str
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    email: str
    active: bool

    class Config:
        orm_mode = True


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenInfo)
async def login(
    user: UserLogin, db: AsyncSession = Depends(db_helper.get_session_getter)
):
    db_user = await db.execute(select(User).where(User.username == user.username))
    db_user = db_user.scalars().first()

    if not db_user or not validate_password(user.password, db_user.password.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    jwt_payload = {
        "sub": db_user.username,
        "username": db_user.username,
        "email": db_user.email,
    }

    token = encode_jwt(jwt_payload)

    return TokenInfo(
        access_token=token,
        token_type="bearer",
    )


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate, db: AsyncSession = Depends(db_helper.get_session_getter)
):
    existing_user = await get_user(db, user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = await create_user(db, user)
    return db_user
