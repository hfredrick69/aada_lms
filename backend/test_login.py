#!/usr/bin/env python3
"""Quick test script to verify login works after encryption"""
import requests
import json

response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "admin@aada.edu", "password": "AdminPass!23"}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("\n✅ LOGIN SUCCESSFUL!")
else:
    print(f"\n❌ LOGIN FAILED: {response.json().get('detail')}")
