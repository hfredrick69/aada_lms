"""
Rate Limiting Middleware

Implements rate limiting to prevent abuse of public endpoints.

Security Features:
- IP-based rate limiting
- Configurable limits per endpoint
- Sliding window algorithm
- In-memory cache (can be upgraded to Redis for production)
"""

from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple
import asyncio


class RateLimiter:
    """
    Simple in-memory rate limiter

    For production: Replace with Redis-based solution for distributed systems
    """

    def __init__(self):
        # Store: {ip_address: {endpoint: [(timestamp, count), ...]}}
        self._requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self._lock = asyncio.Lock()

    async def is_rate_limited(
        self,
        ip_address: str,
        endpoint: str,
        max_requests: int = 10,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Check if IP address is rate limited for endpoint

        Args:
            ip_address: Client IP address
            endpoint: API endpoint being accessed
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_limited: bool, requests_remaining: int)

        Security:
            - Sliding window prevents burst attacks
            - Per-endpoint tracking prevents cross-endpoint abuse
            - Automatic cleanup of old entries
        """
        async with self._lock:
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(seconds=window_seconds)

            # Get requests for this IP and endpoint
            requests = self._requests[ip_address][endpoint]

            # Remove old requests (cleanup)
            self._requests[ip_address][endpoint] = [
                req_time for req_time in requests
                if req_time > cutoff
            ]

            requests = self._requests[ip_address][endpoint]
            current_count = len(requests)

            if current_count >= max_requests:
                return True, 0

            # Add current request
            self._requests[ip_address][endpoint].append(now)

            return False, max_requests - current_count - 1

    async def cleanup_old_entries(self, max_age_hours: int = 24):
        """
        Periodic cleanup of old entries to prevent memory leaks

        Args:
            max_age_hours: Remove entries older than this

        Performance:
            - Should be called periodically (e.g., hourly)
            - Prevents unbounded memory growth
        """
        async with self._lock:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

            # Clean up old IPs
            ips_to_remove = []
            for ip, endpoints in self._requests.items():
                endpoints_to_remove = []
                for endpoint, requests in endpoints.items():
                    # Remove old requests
                    endpoints[endpoint] = [
                        req_time for req_time in requests
                        if req_time > cutoff
                    ]
                    # Mark empty endpoints for removal
                    if not endpoints[endpoint]:
                        endpoints_to_remove.append(endpoint)

                # Remove empty endpoints
                for endpoint in endpoints_to_remove:
                    del endpoints[endpoint]

                # Mark empty IPs for removal
                if not endpoints:
                    ips_to_remove.append(ip)

            # Remove empty IPs
            for ip in ips_to_remove:
                del self._requests[ip]


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request

    Args:
        request: FastAPI request object

    Returns:
        Client IP address

    Security:
        - Checks X-Forwarded-For for proxied requests
        - Falls back to direct client IP
        - Handles IPv6 addresses
    """
    # Check for proxied request
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take first IP if multiple proxies
        return forwarded_for.split(",")[0].strip()

    # Direct connection
    if request.client:
        return request.client.host

    return "unknown"


async def rate_limit_public_endpoints(
    request: Request,
    max_requests: int = 10,
    window_seconds: int = 60
):
    """
    Rate limit middleware for public endpoints

    Args:
        request: FastAPI request
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds

    Raises:
        HTTPException: 429 Too Many Requests if rate limited

    Security:
        - Prevents brute force attacks on public signing endpoints
        - Mitigates DoS attacks
        - Protects against token enumeration
    """
    ip_address = get_client_ip(request)
    endpoint = request.url.path

    is_limited, remaining = await rate_limiter.is_rate_limited(
        ip_address,
        endpoint,
        max_requests,
        window_seconds
    )

    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(window_seconds)}
        )

    # Add rate limit headers (informational)
    request.state.rate_limit_remaining = remaining
