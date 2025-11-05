"""
Security middleware for HIPAA/NIST compliance.

Implements:
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Audit logging for PHI access
- Request/response logging
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

from app.db.models.audit_log import AuditLog
from app.db.session import SessionLocal

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

        # Content Security Policy
        # Restricts resource loading to prevent XSS attacks
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",  # H5P CDN
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",  # H5P CDN
            "img-src 'self' data: https:",
            "font-src 'self' data: https://cdn.jsdelivr.net",  # H5P fonts
            "connect-src 'self' https:",
            "frame-ancestors 'self' http://localhost:5173 http://localhost:5174",  # Allow frontend iframes
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
