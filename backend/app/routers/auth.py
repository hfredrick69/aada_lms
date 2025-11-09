from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import jwt
import uuid
import os

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    verify_refresh_token,
    revoke_refresh_token,
)
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import AuthUser, LoginRequest, RefreshRequest, TokenResponse
from app.utils.encryption import decrypt_value

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "dev_encryption_key_change_in_production_32bytes")

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)

# Cookie settings for httpOnly tokens
COOKIE_SETTINGS = {
    "httponly": True,
    "secure": False,  # Set to True in production with HTTPS
    "samesite": "lax",
    "path": "/",
}


def _get_user_roles(user: User) -> list[str]:
    return [role.name for role in (user.roles or [])]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> AuthUser:
    """
    Get current user from either httpOnly cookie or Authorization header.
    Supports both authentication methods for backwards compatibility.
    """
    # Try to get token from Authorization header first, then fall back to cookie
    token = (credentials.credentials if credentials else None) or access_token

    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication credentials")

    try:
        payload = decode_token(token)
        subject = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from None

    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    try:
        user_id = uuid.UUID(str(subject))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from None

    user: User | None = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.status and user.status.lower() != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    # Decrypt PII fields
    decrypted_email = decrypt_value(db, user.email)
    decrypted_first_name = decrypt_value(db, user.first_name)
    decrypted_last_name = decrypt_value(db, user.last_name)

    return AuthUser(
        id=user.id,
        email=decrypted_email,
        first_name=decrypted_first_name,
        last_name=decrypted_last_name,
        roles=_get_user_roles(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
) -> TokenResponse:
    # Query user by decrypting email field in SQL
    result = db.execute(
        text("""
            SELECT id, email, password_hash, first_name, last_name, status
            FROM users
            WHERE pgp_sym_decrypt(decode(email, 'base64'), :key) = :email
            LIMIT 1
        """),
        {"key": ENCRYPTION_KEY, "email": payload.email}
    ).fetchone()

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Get full User object for roles relationship
    user: User | None = db.query(User).filter(User.id == result.id).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.status and user.status.lower() != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    # Create access token (short-lived)
    access_token = create_access_token(str(user.id))

    # Create refresh token (long-lived)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    refresh_token = create_refresh_token(
        user_id=user.id,
        db=db,
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Set httpOnly cookies for enhanced security
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=15 * 60,  # 15 minutes in seconds
        **COOKIE_SETTINGS
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        **COOKIE_SETTINGS
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    payload: Optional[RefreshRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token")
) -> TokenResponse:
    """
    Refresh an access token using a refresh token from cookie or request body.

    This implements token rotation - the old refresh token is revoked
    and a new one is issued along with a new access token.
    """
    # Get refresh token from cookie or request body
    token = refresh_token_cookie if refresh_token_cookie else (payload.refresh_token if payload else None)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    # Verify the refresh token and get user_id
    user_id = verify_refresh_token(token, db)

    # Verify user still exists and is active
    user: User | None = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.status and user.status.lower() != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    # Revoke the old refresh token (token rotation)
    revoke_refresh_token(token, db, reason="rotated")

    # Create new access token
    access_token = create_access_token(str(user.id))

    # Create new refresh token
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    new_refresh_token = create_refresh_token(
        user_id=user.id,
        db=db,
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Set httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=15 * 60,  # 15 minutes in seconds
        **COOKIE_SETTINGS
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        **COOKIE_SETTINGS
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    payload: Optional[RefreshRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token")
) -> dict:
    """
    Logout by revoking the refresh token and clearing cookies.

    The access token will still be valid until it expires (15 minutes),
    but no new tokens can be obtained.
    """
    # Get refresh token from cookie or request body
    token = refresh_token_cookie if refresh_token_cookie else (payload.refresh_token if payload else None)

    if token:
        revoke_refresh_token(token, db, reason="logout")

    # Clear httpOnly cookies
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AuthUser)
def me(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    return current_user
