from datetime import timedelta, datetime
import jwt
from core.config import settings
import bcrypt


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_time_delta: timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_time_delta:
        expire = now + expire_time_delta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "iat": now})
    encoded = jwt.encode(to_encode, private_key, algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=password.encode(), hashed_password=hashed_password.encode("utf-8")
    )
