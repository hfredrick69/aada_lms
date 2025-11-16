"""
Security middleware for HIPAA/NIST compliance.

Implements:
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- User context population from JWT
- Audit logging for PHI access
- Request/response logging
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
import jwt
import uuid

from app.core.config import settings
from app.db.models.audit_log import AuditLog
from app.db.models.user import User
from app.db.session import SessionLocal
from app.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses per HIPAA/NIST requirements.

    Headers added:
    - Strict-Transport-Security (HSTS)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Content-Security-Policy
    - Referrer-Policy
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # HSTS - Force HTTPS (31536000 seconds = 1 year)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Build frame-ancestors directive dynamically so hosted portals can embed backend pages (e.g. H5P iframe)
        default_frame_origins = [
            "http://localhost:5173",
            "http://localhost:5174",
        ]
        allowed_origins = [
            origin.strip()
            for origin in settings.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]
        frame_ancestors = []
        for origin in default_frame_origins + allowed_origins:
            if origin not in frame_ancestors:
                frame_ancestors.append(origin)
        frame_ancestors_directive = "frame-ancestors 'self' " + " ".join(frame_ancestors)

        # Content Security Policy
        # Restricts resource loading to prevent XSS attacks
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",  # H5P CDN
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",  # H5P CDN
            "img-src 'self' data: blob: https:",
            "media-src 'self' blob: data:",  # H5P audio/video
            "font-src 'self' data: https://cdn.jsdelivr.net",  # H5P fonts
            "connect-src 'self' https:",
            frame_ancestors_directive,  # Allow configured frontends to embed backend (H5P)
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer Policy - Don't leak referrer info
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        # Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response


class UserContextMiddleware(BaseHTTPMiddleware):
    """
    Populate request.state with user context from JWT token.

    This middleware extracts the JWT token from either:
    - Authorization header (Bearer token)
    - access_token cookie

    And populates:
    - request.state.user_id
    - request.state.user_email

    This allows AuditLoggingMiddleware to log the user without re-parsing the JWT.

    Security: This middleware does NOT enforce authentication. It only populates
    user context for logging purposes. Authentication is still enforced by
    route-level dependencies (get_current_user).
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Initialize user context as None
        request.state.user_id = None
        request.state.user_email = None

        # Try to extract JWT token
        token = None

        # Try Authorization header first (Bearer token)
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

        # Fall back to cookie
        if not token:
            token = request.cookies.get("access_token")

        # If we have a token, try to decode it and populate user context
        if token:
            try:
                # Decode JWT without verification (just for logging context)
                # Actual auth verification happens in get_current_user dependency
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                    options={"verify_exp": False}  # Don't fail on expired tokens for audit logging
                )

                user_id_str = payload.get("sub")
                if user_id_str:
                    try:
                        user_id = uuid.UUID(user_id_str)

                        # Fetch user from database to get email
                        db = SessionLocal()
                        try:
                            user = db.query(User).filter(User.id == user_id).first()
                            if user:
                                request.state.user_id = user_id
                                # Decrypt email for audit logging
                                try:
                                    request.state.user_email = decrypt_value(db, user.email)
                                    logger.debug(
                                        f"UserContext: Populated user_email={request.state.user_email} "
                                        f"for user_id={user_id}"
                                    )
                                except Exception as e:
                                    # If decryption fails, use encrypted value (better than nothing for audit)
                                    request.state.user_email = f"user_{user_id}"
                                    logger.warning(
                                        f"UserContext: Decryption failed for user {user_id}, "
                                        f"using fallback: {e}"
                                    )
                        finally:
                            db.close()
                    except (ValueError, TypeError) as e:
                        # Invalid user_id format, skip
                        logger.debug(f"UserContext: Invalid user_id format: {e}")
            except jwt.InvalidTokenError as e:
                # Invalid token, skip - will be caught by auth dependency later
                logger.debug(f"UserContext: Invalid JWT token: {e}")
            except Exception as e:
                # Log errors but don't fail the request
                logger.error(f"UserContext: Unexpected error: {e}", exc_info=True)

        # Continue with request
        response = await call_next(request)
        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all PHI access for HIPAA compliance audit trail.

    Logs:
    - User accessing the data
    - Resource accessed
    - Timestamp
    - IP address
    - Action performed
    """

    # PHI endpoints that require audit logging
    PHI_ENDPOINTS = [
        "/api/enrollments",
        "/api/transcripts",
        "/api/credentials",
        "/api/externships",
        "/api/attendance",
        "/api/skills",
        "/api/complaints",
        "/api/finance",
        "/api/users",  # Contains PII/PHI
    ]

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Check if this is a PHI endpoint
        is_phi_endpoint = any(
            request.url.path.startswith(endpoint)
            for endpoint in self.PHI_ENDPOINTS
        )

        # Get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        user_email = getattr(request.state, "user_email", None)

        # Get request metadata
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", None)

        # Process request
        response = await call_next(request)

        # Calculate request duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Write to database (async background task to avoid slowing response)
        try:
            db = SessionLocal()
            try:
                audit_entry = AuditLog(
                    user_id=user_id,
                    user_email=user_email,
                    method=request.method,
                    path=request.url.path,
                    endpoint=request.url.path.split("?")[0],  # Remove query params
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status_code=response.status_code,
                    duration_ms=int(duration_ms),
                    is_phi_access=is_phi_endpoint,
                    query_params=str(request.query_params) if request.query_params else None
                )
                db.add(audit_entry)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to write audit log to database: {e}")

        # Still log to stdout for real-time monitoring
        if is_phi_endpoint:
            logger.info(
                "PHI_ACCESS",
                extra={
                    "user_id": user_id,
                    "user_email": user_email,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "ip_address": ip_address,
                    "duration_ms": duration_ms,
                }
            )

        # Log all API requests (not just PHI)
        logger.debug(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {duration_ms:.2f}ms - "
            f"user:{user_email}"
        )

        return response
