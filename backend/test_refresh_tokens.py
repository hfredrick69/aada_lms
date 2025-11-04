#!/usr/bin/env python3
"""Test refresh token flow."""
import requests


BASE_URL = "http://localhost:8000/api"


def test_login():
    """Test login returns both access and refresh tokens."""
    print("1. Testing login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "user1@aada.edu", "password": "Pass123!Word"}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response keys: {list(data.keys())}")

    if response.status_code != 200:
        print(f"   Error: {data}")

    assert "access_token" in data, f"Missing access_token. Response: {data}"
    assert "refresh_token" in data, "Missing refresh_token"
    assert "token_type" in data, "Missing token_type"

    print("   ✓ Login successful - both tokens received")
    return data["access_token"], data["refresh_token"]


def test_access_token(access_token):
    """Test access token works for authenticated endpoints."""
    print("\n2. Testing access token...")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   User: {data.get('email')}")

    assert response.status_code == 200, "Access token failed"
    assert "email" in data, "Missing user data"
    print("   ✓ Access token works")
    return data


def test_refresh(refresh_token):
    """Test refresh token can get new access token."""
    print("\n3. Testing refresh token...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()

    assert response.status_code == 200, "Refresh failed"
    assert "access_token" in data, "Missing new access_token"
    assert "refresh_token" in data, "Missing new refresh_token"

    print("   ✓ Token refresh successful - new tokens received")
    return data["access_token"], data["refresh_token"]


def test_old_refresh_token_revoked(old_refresh_token):
    """Test old refresh token is revoked (token rotation)."""
    print("\n4. Testing old refresh token is revoked...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": old_refresh_token}
    )
    print(f"   Status: {response.status_code}")

    assert response.status_code == 401, "Old token should be revoked"
    print("   ✓ Old refresh token correctly revoked")


def test_logout(refresh_token):
    """Test logout revokes refresh token."""
    print("\n5. Testing logout...")
    response = requests.post(
        f"{BASE_URL}/auth/logout",
        json={"refresh_token": refresh_token}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Message: {data.get('message')}")

    assert response.status_code == 200, "Logout failed"
    print("   ✓ Logout successful")

    # Try to use the token after logout
    print("\n6. Testing token is invalid after logout...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    print(f"   Status: {response.status_code}")

    assert response.status_code == 401, "Token should be revoked after logout"
    print("   ✓ Token correctly revoked after logout")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Refresh Token Flow")
    print("=" * 60)

    try:
        # Test login and get tokens
        access_token, refresh_token = test_login()

        # Test access token works
        test_access_token(access_token)

        # Test refresh and get new tokens
        new_access_token, new_refresh_token = test_refresh(refresh_token)

        # Test old token is revoked
        test_old_refresh_token_revoked(refresh_token)

        # Test new access token works
        test_access_token(new_access_token)

        # Test logout
        test_logout(new_refresh_token)

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
