from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import jwt
import uuid

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    verify_refresh_token,
    revoke_refresh_token,
    get_password_hash,
    hash_token,
)
from app.db.models.user import User
from app.db.models.role import Role
from app.db.models.registration_request import RegistrationRequest
from app.db.session import get_db
from app.schemas.auth import (
    AuthUser,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    RegistrationRequestPayload,
    RegistrationVerifyPayload,
    RegistrationVerifyResponse,
    RegistrationCompletePayload,
)
from app.services.email import EmailDeliveryError, send_registration_verification_email
from app.utils.encryption import decrypt_value, encrypt_value

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "dev_encryption_key_change_in_production_32bytes")
REGISTRATION_TOKEN_TYPE = "registration"
GENERIC_REGISTRATION_RESPONSE = {
    "message": "If the email is valid, you'll receive verification instructions shortly."
}

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)

# Cookie settings for httpOnly tokens (environment-based security)
SECURE_COOKIES = os.getenv("SECURE_COOKIES", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Enforce secure cookies in production
if not SECURE_COOKIES and ENVIRONMENT == "production":
    raise RuntimeError(
        "SECURE_COOKIES must be True in production. "
        "Set SECURE_COOKIES=true in environment variables."
    )

COOKIE_SETTINGS = {
    "httponly": True,
    "secure": SECURE_COOKIES,  # True in production, configurable in dev
    "samesite": "strict",  # Stronger CSRF protection
    "path": "/",
}


def _get_user_roles(user: User) -> list[str]:
    return [role.name for role in (user.roles or [])]


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_email(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


def _user_exists(db: Session, email: str) -> bool:
    result = db.execute(
        text(
            """
            SELECT 1 FROM users
            WHERE pgp_sym_decrypt(decode(email, 'base64'), :key) = :email
            LIMIT 1
            """
        ),
        {"key": ENCRYPTION_KEY, "email": email},
    ).fetchone()
    return bool(result)


def _get_or_create_student_role(db: Session) -> Role:
    role = db.query(Role).filter(Role.name == "student").first()
    if role:
        return role
    role = Role(name="student", description="Student")
    db.add(role)
    db.flush()
    return role


def _create_registration_token(request_id: uuid.UUID, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.REGISTRATION_COMPLETION_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(request_id),
        "email": email,
        "type": REGISTRATION_TOKEN_TYPE,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_registration_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid registration token") from exc

    if payload.get("type") != REGISTRATION_TOKEN_TYPE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid registration token")
    return payload


@router.post("/register/request", status_code=status.HTTP_202_ACCEPTED)
def request_registration(
    payload: RegistrationRequestPayload,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    email = _normalize_email(payload.email)

    # Avoid enumeration by always returning 202 even if the email already exists
    if _user_exists(db, email):
        return GENERIC_REGISTRATION_RESPONSE

    email_hash = _hash_email(email)
    verification_token = secrets.token_urlsafe(32)
    token_hash = hash_token(verification_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.REGISTRATION_EMAIL_EXPIRE_MINUTES
    )

    registration = (
        db.query(RegistrationRequest)
        .filter(RegistrationRequest.email_hash == email_hash)
        .first()
    )
    encrypted_email = encrypt_value(db, email)
    if registration:
        registration.email = encrypted_email
        registration.token_hash = token_hash
        registration.status = "pending"
        registration.expires_at = expires_at
        registration.verified_at = None
        registration.completed_at = None
        registration.request_ip = request.client.host if request.client else None
        registration.user_agent = request.headers.get("user-agent")
        registration.updated_at = datetime.now(timezone.utc)
    else:
        registration = RegistrationRequest(
            email=encrypted_email,
            email_hash=email_hash,
            token_hash=token_hash,
            status="pending",
            expires_at=expires_at,
            request_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        db.add(registration)

    db.commit()

    verification_link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/register/verify?token={verification_token}"
    try:
        send_registration_verification_email(email, verification_link)
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=500, detail="Unable to send verification email") from exc

    return GENERIC_REGISTRATION_RESPONSE


@router.post("/register/verify", response_model=RegistrationVerifyResponse)
def verify_registration(
    payload: RegistrationVerifyPayload,
    db: Session = Depends(get_db),
) -> RegistrationVerifyResponse:
    token_hash = hash_token(payload.token)
    registration = (
        db.query(RegistrationRequest)
        .filter(
            RegistrationRequest.token_hash == token_hash,
            RegistrationRequest.status == "pending",
        )
        .first()
    )
    if not registration or registration.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    registration.status = "verified"
    registration.verified_at = datetime.now(timezone.utc)
    registration.expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.REGISTRATION_COMPLETION_EXPIRE_MINUTES
    )
    registration.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(registration)

    email = decrypt_value(db, registration.email)
    registration_token = _create_registration_token(registration.id, email)

    return RegistrationVerifyResponse(
        registration_token=registration_token,
        expires_at=registration.expires_at,
    )


@router.post("/register/complete", status_code=status.HTTP_201_CREATED)
def complete_registration(payload: RegistrationCompletePayload, db: Session = Depends(get_db)) -> dict:
    token_data = _decode_registration_token(payload.registration_token)
    registration_id = token_data.get("sub")
    email = _normalize_email(token_data.get("email", ""))

    if not registration_id or not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid registration token")

    try:
        registration_uuid = uuid.UUID(str(registration_id))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid registration token") from exc

    registration = (
        db.query(RegistrationRequest)
        .filter(RegistrationRequest.id == registration_uuid)
        .first()
    )
    if (
        not registration
        or registration.status != "verified"
        or registration.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration link is no longer valid")

    if _user_exists(db, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An account already exists for this email")

    user = User(
        email=encrypt_value(db, email),
        password_hash=get_password_hash(payload.password),
        first_name=encrypt_value(db, payload.first_name),
        last_name=encrypt_value(db, payload.last_name),
        status="active",
    )
    user.roles.append(_get_or_create_student_role(db))
    db.add(user)

    registration.status = "completed"
    registration.completed_at = datetime.now(timezone.utc)
    registration.updated_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Registration complete. You can now sign in."}


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
