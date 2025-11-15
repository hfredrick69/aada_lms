"""Tests for enrollment agreement workflow."""
import base64
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.tests.utils import create_user_with_roles
from app.db.session import SessionLocal
from app.db.models.document import DocumentTemplate
from app.domain.enrollment.schema import get_enrollment_agreement_schema
from app.services.enrollment_pdf import SchemaDrivenPDFService

client = TestClient(app)

SAMPLE_PDF_BASE64 = (
    "JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRs"
    "YWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0"
    "aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0Zv"
    "bnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4"
    "NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYg"
    "L1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlw"
    "ZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBl"
    "IC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAo"
    "RDoyMDI1MTExMjE4MjM1OC0wNScwMCcpIC9DcmVhdG9yIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVw"
    "b3J0bGFiLmNvbSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjUxMTEyMTgyMzU4LTA1JzAwJykgL1Byb2R1"
    "Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKHVuc3Bl"
    "Y2lmaWVkKSAvVGl0bGUgKHVudGl0bGVkKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0Nv"
    "dW50IDEgL0tpZHMgWyAzIDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKNyAwIG9iago8PAovRmlsdGVyIFsg"
    "L0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAxNjkKPj4Kc3RyZWFtCkdhclcwXWFobjUmOzBe"
    "QEtoI01WXExJWzM8MFc3MD82RmhNNT11aVlLX0hpLiYuSFhHQVVUXzljckRwYStUTk5tXEthb1kqXkUxNG4vYV9P"
    "KylXRj47T10+O3BWal9HZiYyKEhbOUpRPDlbV19bQHQ/Y2hPXzovOVlNZEJsVjEoI2xJKiY9MWE9YzhcQCMsLVc/"
    "PUlrQk5bVSZgPF4vNk4qXGlqNTVsfj5lbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA4CjAwMDAwMDAwMDAgNjU1MzUg"
    "ZiAKMDAwMDAwMDA3MyAwMDAwMCBuIAowMDAwMDAwMTA0IDAwMDAwIG4gCjAwMDAwMDAyMTEgMDAwMDAgbiAKMDAw"
    "MDAwMDQxNCAwMDAwMCBuIAowMDAwMDAwNDgyIDAwMDAwIG4gCjAwMDAwMDA3NzggMDAwMDAgbiAKMDAwMDAwMDgz"
    "NyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9JRCAKWzw4NWUzYTgxYjUzNTIyYTc1NjlhNzMwNWYxNjM4M2QxYz48ODVl"
    "M2E4MWI1MzUyMmE3NTY5YTczMDVmMTYzODNkMWM+XQolIFJlcG9ydExhYiBnZW5lcmF0ZWQgUERGIGRvY3VtZW50"
    "IC0tIGRpZ2VzdCAoaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tKQoKL0luZm8gNSAwIFIKL1Jvb3QgNCAwIFIKL1Np"
    "emUgOAo+PgpzdGFydHhyZWYKMTA5NgolJUVPRgo="
)


def _create_template():
    template_dir = Path("app/static/documents/templates")
    template_dir.mkdir(parents=True, exist_ok=True)
    filename = f"test-enrollment-{uuid4().hex}.pdf"
    pdf_path = template_dir / filename
    pdf_path.write_bytes(base64.b64decode(SAMPLE_PDF_BASE64))

    session = SessionLocal()
    try:
        template = DocumentTemplate(
            id=uuid4(),
            name="Enrollment Agreement",
            version=f"test-{uuid4().hex[:6]}",
            description="Automated test template",
            file_path=str(Path("documents/templates") / filename),
            requires_counter_signature=True,
            is_active=True,
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        return template
    finally:
        session.close()


def _create_user(email: str, password: str, roles: list[str]):
    session = SessionLocal()
    try:
        user = create_user_with_roles(session, email=email, password=password, roles=roles)
        session.expunge_all()
        setattr(user, "email_plain", email)
        return user
    finally:
        session.close()


def _auth_headers(email: str, password: str) -> dict:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_send_enrollment_agreement():
    admin_email = "agreements.admin@test.edu"
    _create_user(admin_email, "AdminPass!23", ["admin"])
    student = _create_user("agreements.student@test.edu", "StudentPass!23", ["student"])
    template = _create_template()
    headers = _auth_headers(admin_email, "AdminPass!23")

    payload = {
        "user_id": str(student.id),
        "template_id": str(template.id),
        "course_type": "twenty_week",
        "signer_name": "QA Student",
        "signer_email": "qa.student@example.edu",
        "form_data": {"advisor_notes": "Playwright"},
    }
    response = client.post("/api/documents/enrollment/send", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user_id"] == str(student.id)
    assert body["course_type"] == "twenty_week"
    assert body["form_data"]["advisor_notes"] == "Playwright"
    assert body["form_data"]["course_label"] == "20-Week Course"
    assert body["status"] == "pending"
    assert body["signing_token"]


def test_student_cannot_send_enrollment_agreement():
    student_email = "agreements.self@test.edu"
    student = _create_user(student_email, "StudentPass!23", ["student"])
    _create_template()
    headers = _auth_headers(student_email, "StudentPass!23")

    payload = {
        "user_id": str(student.id),
        "course_type": "twenty_week",
    }
    response = client.post("/api/documents/enrollment/send", json=payload, headers=headers)
    assert response.status_code == 403


def test_admin_can_counter_sign_agreement():
    admin_email = "agreements.counter.admin@test.edu"
    registrar_email = "agreements.registrar@test.edu"
    _create_user(admin_email, "AdminPass!23", ["admin"])
    _create_user(registrar_email, "RegistrarPass!23", ["registrar"])
    student = _create_user("agreements.counter.student@test.edu", "StudentPass!23", ["student"])
    template = _create_template()

    headers_admin = _auth_headers(admin_email, "AdminPass!23")
    send_payload = {
        "user_id": str(student.id),
        "template_id": str(template.id),
        "course_type": "twenty_week",
    }
    response = client.post("/api/documents/enrollment/send", json=send_payload, headers=headers_admin)
    assert response.status_code == 200
    document_id = response.json()["id"]

    headers_registrar = _auth_headers(registrar_email, "RegistrarPass!23")
    counter_response = client.post(
        f"/api/documents/{document_id}/counter-sign",
        json={"typed_name": "Registrar QA", "signature_data": "YmFzZTY0LXNpZ25hdHVyZQ=="},
        headers=headers_registrar,
    )
    assert counter_response.status_code == 200, counter_response.text
    counter_body = counter_response.json()
    assert counter_body["status"] == "completed"
    assert counter_body["counter_signed_at"] is not None
    assert counter_body["signing_token"] is None


def test_admin_can_send_ad_hoc_enrollment_agreement():
    admin_email = "agreements.adhoc.admin@test.edu"
    _create_user(admin_email, "AdminPass!23", ["admin"])
    template = _create_template()
    headers = _auth_headers(admin_email, "AdminPass!23")

    payload = {
        "template_id": str(template.id),
        "course_type": "twenty_week",
        "signer_name": "Prospective Student",
        "signer_email": "prospect@example.com",
    }
    response = client.post("/api/documents/enrollment/send", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["lead_id"] is None
    assert body["user_id"] is None
    assert body["signer_email"] == "prospect@example.com"
    assert body["signer_name"] == "Prospective Student"


def test_public_sign_endpoint_includes_schema():
    admin_email = "agreements.schema.admin@test.edu"
    _create_user(admin_email, "AdminPass!23", ["admin"])
    student = _create_user("agreements.schema.student@test.edu", "StudentPass!23", ["student"])
    template = _create_template()

    headers = _auth_headers(admin_email, "AdminPass!23")
    payload = {
        "user_id": str(student.id),
        "template_id": str(template.id),
        "course_type": "twenty_week",
    }
    response = client.post("/api/documents/enrollment/send", json=payload, headers=headers)
    assert response.status_code == 200
    signing_token = response.json()["signing_token"]

    public_response = client.get(f"/api/public/sign/{signing_token}")
    assert public_response.status_code == 200
    body = public_response.json()
    schema = body.get("agreement_schema")
    assert schema, "schema should be included in the public signing payload"
    section_ids = [section["id"] for section in schema["sections"]]
    assert "acknowledgements" in section_ids


def test_schema_driven_pdf_service_generates(tmp_path):
    schema = get_enrollment_agreement_schema()
    pdf_service = SchemaDrivenPDFService(schema)
    document = SimpleNamespace(id=uuid4())
    signatures = [
        SimpleNamespace(
            signature_data="dGVzdA==",
            signature_type="student",
            typed_name="QA Student",
            signer_email="qa.student@example.edu",
            signed_at=datetime.now(timezone.utc),
        )
    ]
    output_path = tmp_path / "schema-agreement.pdf"
    success = pdf_service.generate_pdf(
        output_pdf_path=output_path,
        document=document,
        form_data={"student": {"first_name": "QA", "last_name": "Student"}},
        signatures=signatures,
    )
    assert success
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_public_advisors_endpoint():
    response = client.get("/api/public/sign/advisors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(entry["id"] == "mary_jones" for entry in data)
