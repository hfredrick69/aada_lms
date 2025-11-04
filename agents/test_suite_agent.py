#!/usr/bin/env python3
"""
Test Suite Expansion Agent
---------------------------
Creates comprehensive test cases for all API endpoints.
"""

import subprocess
import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[Test Suite] {ts} | {msg}"
    print(entry)
    with open(LOG_DIR / "test_suite.log", "a") as f:
        f.write(entry + "\n")


def create_users_tests():
    """Create tests for users API"""
    log("Creating users API tests...")

    test_content = '''"""Test users API endpoints"""
import pytest
from uuid import uuid4


def test_list_users(client, admin_token):
    """Test GET /users"""
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(client, admin_token):
    """Test POST /users"""
    data = {
        "email": "newuser@aada.edu",
        "password": "securepass123",
        "first_name": "New",
        "last_name": "User"
    }
    response = client.post("/users", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@aada.edu"


def test_create_duplicate_user(client, admin_token, test_user):
    """Test creating user with duplicate email fails"""
    data = {
        "email": test_user.email,
        "password": "password",
        "first_name": "Dupe",
        "last_name": "User"
    }
    response = client.post("/users", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400


def test_get_user(client, admin_token, test_user):
    """Test GET /users/{user_id}"""
    response = client.get(f"/users/{test_user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == str(test_user.id)


def test_update_user(client, admin_token, test_user):
    """Test PUT /users/{user_id}"""
    data = {"first_name": "Updated", "status": "inactive"}
    response = client.put(f"/users/{test_user.id}", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


def test_delete_user(client, admin_token, db):
    """Test DELETE /users/{user_id}"""
    from app.db.models.user import User
    from app.core.security import hash_password

    # Create temp user to delete
    temp_user = User(
        id=uuid4(),
        email="deleteme@aada.edu",
        password_hash=hash_password("password"),
        first_name="Delete",
        last_name="Me"
    )
    db.add(temp_user)
    db.commit()

    response = client.delete(f"/users/{temp_user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
'''

    test_path = BACKEND_DIR / "app" / "tests" / "test_users_api.py"
    test_path.write_text(test_content)
    log(f"✅ Created {test_path}")


def create_roles_tests():
    """Create tests for roles API"""
    log("Creating roles API tests...")

    test_content = '''"""Test roles API endpoints"""
import pytest


def test_list_roles(client):
    """Test GET /roles"""
    response = client.get("/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_role(client, admin_token):
    """Test POST /roles"""
    data = {
        "name": "TestRole",
        "description": "Test role description"
    }
    response = client.post("/roles", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "TestRole"


def test_create_duplicate_role(client, admin_token):
    """Test creating duplicate role fails"""
    data = {"name": "Admin", "description": "Duplicate"}
    response = client.post("/roles", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400


def test_delete_role(client, admin_token, db):
    """Test DELETE /roles/{role_id}"""
    from app.db.models.role import Role
    from uuid import uuid4

    # Create temp role to delete
    temp_role = Role(id=uuid4(), name="DeleteMe", description="Temporary")
    db.add(temp_role)
    db.commit()

    response = client.delete(f"/roles/{temp_role.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
'''

    test_path = BACKEND_DIR / "app" / "tests" / "test_roles_api.py"
    test_path.write_text(test_content)
    log(f"✅ Created {test_path}")


def create_comprehensive_endpoint_tests():
    """Create tests for remaining endpoints"""
    log("Creating comprehensive endpoint tests...")

    test_content = '''"""Comprehensive API endpoint tests"""
import pytest


def test_programs_list(client, auth_headers):
    """Test GET /programs"""
    response = client.get("/programs", headers=auth_headers)
    assert response.status_code == 200


def test_enrollments_list(client, auth_headers):
    """Test GET /enrollments"""
    response = client.get("/enrollments", headers=auth_headers)
    assert response.status_code == 200


def test_attendance_crud(client, auth_headers, test_user, test_module):
    """Test attendance CRUD operations"""
    # Create
    data = {
        "user_id": str(test_user.id),
        "module_id": str(test_module.id),
        "session_type": "live",
        "started_at": "2025-01-01T10:00:00Z",
        "ended_at": "2025-01-01T11:00:00Z"
    }
    response = client.post("/attendance", json=data, headers=auth_headers)
    assert response.status_code == 201

    attendance_id = response.json()["id"]

    # Read
    response = client.get(f"/attendance/{attendance_id}", headers=auth_headers)
    assert response.status_code == 200

    # Update
    update_data = {"session_type": "lab"}
    response = client.put(f"/attendance/{attendance_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    # Delete
    response = client.delete(f"/attendance/{attendance_id}", headers=auth_headers)
    assert response.status_code == 204


def test_skills_crud(client, auth_headers, test_user, test_module):
    """Test skills checkoff CRUD"""
    data = {
        "user_id": str(test_user.id),
        "module_id": str(test_module.id),
        "skill_code": "TEST_SKILL_001",
        "status": "pending"
    }
    response = client.post("/skills", json=data, headers=auth_headers)
    assert response.status_code == 201

    skill_id = response.json()["id"]

    # Approve skill
    update_data = {
        "status": "approved",
        "evaluator_name": "Dr. Test",
        "evaluator_license": "LIC-12345"
    }
    response = client.put(f"/skills/{skill_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200


def test_externship_verification(client, auth_headers, test_user):
    """Test externship creation and verification"""
    data = {
        "user_id": str(test_user.id),
        "site_name": "Test Clinic",
        "supervisor_name": "Dr. Supervisor",
        "total_hours": 120,
        "verified": True,
        "verification_doc_url": "https://example.com/doc.pdf"
    }
    response = client.post("/externships", json=data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["verified"] == True


def test_credentials_issuance(client, auth_headers, test_user, test_program):
    """Test credential issuance"""
    data = {
        "user_id": str(test_user.id),
        "program_id": str(test_program.id),
        "credential_type": "certificate"
    }
    response = client.post("/credentials", json=data, headers=auth_headers)
    assert response.status_code == 201
    assert "cert_serial" in response.json()


def test_transcript_generation(client, auth_headers, test_user, test_program):
    """Test transcript generation"""
    data = {
        "user_id": str(test_user.id),
        "program_id": str(test_program.id)
    }
    response = client.post("/transcripts", json=data, headers=auth_headers)
    assert response.status_code == 201
    assert "gpa" in response.json()


def test_complaint_workflow(client, auth_headers, test_user):
    """Test complaint workflow from submission to resolution"""
    # Submit complaint
    data = {
        "user_id": str(test_user.id),
        "category": "Academic",
        "details": "Test complaint details"
    }
    response = client.post("/complaints", json=data, headers=auth_headers)
    assert response.status_code == 201

    complaint_id = response.json()["id"]

    # Update to in_review
    update_data = {"status": "in_review"}
    response = client.put(f"/complaints/{complaint_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    # Resolve complaint
    resolve_data = {
        "status": "resolved",
        "resolution_notes": "Complaint addressed successfully"
    }
    response = client.put(f"/complaints/{complaint_id}", json=resolve_data, headers=auth_headers)
    assert response.status_code == 200


def test_xapi_statements(client, auth_headers):
    """Test xAPI statement creation and filtering"""
    data = {
        "actor": {"mbox": "mailto:test@aada.edu", "name": "Test Student"},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {"id": "http://aada.edu/modules/test"}
    }
    response = client.post("/xapi/statements", json=data, headers=auth_headers)
    assert response.status_code == 201

    # Filter by agent
    response = client.get("/xapi/statements?agent=test@aada.edu", headers=auth_headers)
    assert response.status_code == 200


def test_compliance_reports(client, auth_headers):
    """Test compliance report generation"""
    resources = ["attendance", "credentials", "complaints", "externships"]

    for resource in resources:
        response = client.get(f"/reports/compliance/{resource}?format=csv", headers=auth_headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
'''

    test_path = BACKEND_DIR / "app" / "tests" / "test_all_endpoints.py"
    test_path.write_text(test_content)
    log(f"✅ Created {test_path}")


def run_tests():
    """Execute all tests"""
    log("Running test suite...")

    try:
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            cwd=BACKEND_DIR / "app",
            capture_output=True,
            text=True,
            timeout=300
        )

        log("Test results:")
        log(result.stdout)

        if result.returncode != 0:
            log("Some tests failed:")
            log(result.stderr)

    except subprocess.TimeoutExpired:
        log("⚠️ Tests timed out after 5 minutes")
    except Exception as e:
        log(f"❌ Error running tests: {e}")


def main():
    log("===== Test Suite Expansion Agent Starting =====")

    try:
        create_users_tests()
        create_roles_tests()
        create_comprehensive_endpoint_tests()

        log("✅ Test suite expanded")

        # Optionally run tests
        # run_tests()

    except Exception as e:
        log(f"❌ Error: {e}")
        raise

    log("===== Test Suite Expansion Agent Complete =====")


if __name__ == "__main__":
    main()
