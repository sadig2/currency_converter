# auth/middleware.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from auth.utils import decode_jwt
from core.config import settings
import jwt


EXCLUDED_PATHS = ["/auth/login", "/docs", "/openapi.json", "/redoc"]


async def jwt_auth_middleware(request: Request, call_next):
    # Skip authentication for excluded paths (login, docs, etc.)
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing or invalid token"},
        )

    token = auth_header.split("Bearer ")[1]

    try:
        # Validate token and attach user data to request state
        payload = decode_jwt(token)
        request.state.user = payload  # Accessible in endpoints via `request.state.user`
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token expired"},
        )
    except (jwt.InvalidTokenError, jwt.DecodeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token"},
        )

    return await call_next(request)
