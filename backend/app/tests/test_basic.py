from fastapi.testclient import TestClient
from app.main import app


def test_healthcheck():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("status") == "running"
