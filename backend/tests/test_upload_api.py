from fastapi.testclient import TestClient


def test_upload_supported_file_creates_pending_task():
    from backend.app.api.tasks import task_store
    from backend.app.main import app

    task_store.clear()
    client = TestClient(app)
    payload = b"example document bytes"

    response = client.post(
        "/api/upload",
        files={"file": ("sample.docx", payload, "application/octet-stream")},
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"task_id", "access_token"}

    stored = task_store.get(body["task_id"])
    assert stored is not None
    assert stored.file_name == "sample.docx"
    assert stored.file_type == "docx"
    assert stored.file_size == len(payload)
    assert stored.status == "pending"
    assert stored.access_token == body["access_token"]
    assert len(stored.file_hash) == 64


def test_upload_rejects_unsupported_extension():
    from backend.app.api.tasks import task_store
    from backend.app.main import app

    task_store.clear()
    client = TestClient(app)

    response = client.post(
        "/api/upload",
        files={"file": ("sample.exe", b"not supported", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported file extension: exe"}
    assert task_store == {}
