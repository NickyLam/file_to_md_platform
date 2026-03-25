from fastapi.testclient import TestClient


def test_app_imports_and_exposes_healthcheck():
    from backend.app.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
