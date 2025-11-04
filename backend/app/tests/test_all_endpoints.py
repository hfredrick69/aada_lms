"""Comprehensive API endpoint tests"""


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
    assert response.json()["verified"] is True


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
