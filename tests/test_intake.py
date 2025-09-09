from fastapi.testclient import TestClient

from app.main import app

<<<<<<< HEAD
=======

>>>>>>> main
def test_intake_requires_authentication():
    client = TestClient(app)
    res = client.get("/api/intake/questions")
    assert res.status_code == 403
