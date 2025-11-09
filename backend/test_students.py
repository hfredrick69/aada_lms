#!/usr/bin/env python3
"""Test script to verify students endpoint returns decrypted data"""
import requests
import json

# First, login as admin
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "admin@aada.edu", "password": "AdminPass!23"}
)

if login_response.status_code != 200:
    print(f"❌ LOGIN FAILED: {login_response.json().get('detail')}")
    exit(1)

access_token = login_response.json()["access_token"]
print("✅ Login successful")

# Now test the students endpoint
students_response = requests.get(
    "http://localhost:8000/api/students",
    headers={"Authorization": f"Bearer {access_token}"}
)

print(f"\nStatus Code: {students_response.status_code}")
print(f"\nResponse:\n{json.dumps(students_response.json(), indent=2)}")

# Check if data is decrypted (should be readable email, not base64)
students = students_response.json()
if students:
    first_student = students[0]
    email = first_student.get("email", "")
    first_name = first_student.get("first_name", "")

    # Check if it looks like base64 encrypted data (long random string)
    if len(email) > 50 or "@" not in email:
        print(f"\n❌ DATA STILL ENCRYPTED! Email: {email[:50]}...")
    else:
        print(f"\n✅ DATA IS DECRYPTED! Email: {email}, Name: {first_name}")
else:
    print("\n⚠️  No students found")
