from fastapi.testclient import TestClient

from app.main import app  # adjust if your app object lives elsewhere


def test_healthz():
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("ok") is True
