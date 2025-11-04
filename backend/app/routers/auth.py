from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt
import uuid

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

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)


def _get_user_roles(user: User) -> list[str]:
    return [role.name for role in (user.roles or [])]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication credentials")
    token = credentials.credentials
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

    return AuthUser(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=_get_user_roles(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> TokenResponse:
    user: User | None = db.query(User).filter(User.email == payload.email).first()
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

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Refresh an access token using a refresh token.

    This implements token rotation - the old refresh token is revoked
    and a new one is issued along with a new access token.
    """
    # Verify the refresh token and get user_id
    user_id = verify_refresh_token(payload.refresh_token, db)

    # Verify user still exists and is active
    user: User | None = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.status and user.status.lower() != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    # Revoke the old refresh token (token rotation)
    revoke_refresh_token(payload.refresh_token, db, reason="rotated")

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

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout")
def logout(
    payload: RefreshRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Logout by revoking the refresh token.

    The access token will still be valid until it expires (15 minutes),
    but no new tokens can be obtained.
    """
    revoke_refresh_token(payload.refresh_token, db, reason="logout")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AuthUser)
def me(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    return current_user
