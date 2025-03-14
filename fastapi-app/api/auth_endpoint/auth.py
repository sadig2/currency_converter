from fastapi import HTTPException, status, Form
from jwt.exceptions import InvalidTokenError

from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends
from core.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import db_helper

from auth.utils import encode_jwt, validate_password, hash_password, decode_jwt
from crud.users import get_user, create_user, get_user_by_username


router = APIRouter(prefix="/authenticate", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/api/authenticate/login/",
)


# Schemas
class UserCreate(BaseModel):
    password: str
    username: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    username: str
    active: bool

    class Config:
        orm_mode = True


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    db: AsyncSession = Depends(db_helper.get_session_getter),
):
    db_user = await get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email",
        )

    if not validate_password(password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    return db_user


@router.post("/login/", response_model=TokenInfo)
async def login(
    user: UserCreate = Depends(validate_auth_user),
    # db: AsyncSession = Depends(db_helper.get_session_getter),
):

    jwt_payload = {
        "sub": user.username,
        "username": user.username,
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
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="user already registered")

    db_user = await create_user(db, user)
    return db_user


def get_current_token_payload(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    token: str = Depends(oauth2_scheme),
) -> dict:
    # token = credentials.credentials
    try:
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
            # detail=f"invalid token error",
        )
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    db: AsyncSession = Depends(db_helper.get_session_getter),
) -> UserCreate:
    username: str | None = payload.get("username")
    print(payload, "in payload")
    db_user = await get_user_by_username(db, username=username)
    if db_user:
        return db_user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )


@router.get("/users/me/")
async def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserCreate = Depends(get_current_auth_user),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "logged_in_at": iat,
    }
