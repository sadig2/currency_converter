from fastapi import APIRouter, Depends, Form, HTTPException, status
from core.schemas.user import UserRead, UserSchema
from auth.utils import hash_password, encode_jwt, validate_password
from pydantic import BaseModel
from core.models import db_helper


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


router = APIRouter(prefix="/jwt", tags=["jwt"])

john = UserSchema(
    username="john",
    password=hash_password("password1"),
    email="john@yahoo.com",
    active=True,
)

sam = UserSchema(
    username="sam",
    password=hash_password("password2"),
    email="sam@yahoo.com",
    active=True,
)

users_db: dict[str, UserSchema] = {
    john.username: john,
    sam.username: sam,
}


def validate_auth_user(username: str = Form(), password: str = Form()):
    unauth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password"
    )
    if not (user := users_db.get(username)):
        raise unauth_exc
    if validate_password(password=password, hashed_password=user.password):
        return user
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="user is not active"
        )
    raise unauth_exc


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(user: UserSchema = Depends(validate_auth_user)):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    }
    token = encode_jwt(jwt_payload)
    return TokenInfo(access_token=token, token_type="bearer")


# def get_current_user(): ...


# @router.post("/login1/", response_class=TokenInfo)
# def auth_real_user(user: UserRead, session=Depends(db_helper.get_session_getter)):
#     user = await get_user(session=session)


# @router.get("/users/me")
# def check_info(user: UserSchema = Depends(get_current_user)):
#     return {
#         user:
#        }
