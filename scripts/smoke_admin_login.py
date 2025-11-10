#!/usr/bin/env python3
"""Simple smoke test that verifies admin login + /auth/me with CORS headers."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Tuple

import requests


DEFAULT_API_BASE = os.getenv("SMOKE_API_BASE", os.getenv("SMOKE_API_BASE_URL", "http://localhost:8000/api"))
DEFAULT_ORIGIN = os.getenv("SMOKE_ADMIN_ORIGIN", "http://localhost:5173")
DEFAULT_EMAIL = os.getenv("SMOKE_ADMIN_EMAIL", "admin@aada.edu")
DEFAULT_PASSWORD = os.getenv("SMOKE_ADMIN_PASSWORD", "AdminPass!23")


class SmokeFailure(Exception):
    """Raised when the smoke test observes a failure condition."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test for admin login and /auth/me endpoint")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="API base URL including /api prefix")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN, help="Origin header to emulate admin portal")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="Admin email credential")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Admin password credential")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    return parser.parse_args()


def ensure_cors_header(response: requests.Response, origin: str) -> None:
    allow_origin = response.headers.get("access-control-allow-origin")
    if allow_origin != origin:
        raise SmokeFailure(
            f"CORS header mismatch. Expected {origin!r} but got {allow_origin!r}"
        )


def run_smoke(api_base: str, origin: str, email: str, password: str, timeout: int) -> Tuple[str, list[str]]:
    session = requests.Session()
    headers = {"Origin": origin, "Content-Type": "application/json"}

    login_resp = session.post(
        f"{api_base}/auth/login",
        json={"email": email, "password": password},
        headers=headers,
        timeout=timeout,
    )
    if login_resp.status_code != 200:
        raise SmokeFailure(f"Login failed: {login_resp.status_code} {login_resp.text}")
    ensure_cors_header(login_resp, origin)

    me_resp = session.get(f"{api_base}/auth/me", headers=headers, timeout=timeout)
    if me_resp.status_code != 200:
        raise SmokeFailure(f"/auth/me failed: {me_resp.status_code} {me_resp.text}")
    ensure_cors_header(me_resp, origin)

    payload = me_resp.json()
    if payload.get("email") != email:
        raise SmokeFailure(f"Unexpected email in /auth/me response: {payload}")

    return payload.get("first_name", ""), payload.get("roles", [])


def main() -> None:
    args = parse_args()
    try:
        first_name, roles = run_smoke(
            api_base=args.api_base.rstrip("/"),
            origin=args.origin.rstrip("/"),
            email=args.email,
            password=args.password,
            timeout=args.timeout,
        )
    except SmokeFailure as exc:
        print(f"❌ Admin smoke test failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"❌ Network error during smoke test: {exc}", file=sys.stderr)
        sys.exit(1)

    role_list = ", ".join(roles) if roles else "no roles reported"
    print(f"✅ Admin smoke test passed. Authenticated as {first_name or 'admin'} ({role_list}).")


if __name__ == "__main__":
    main()
