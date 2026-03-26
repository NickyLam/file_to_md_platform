from io import BytesIO
import zipfile

from fastapi.testclient import TestClient


def _docx_payload(text: str = "hello") -> bytes:
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>
</w:document>
"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", document)
    return buffer.getvalue()


def test_upload_supported_file_creates_task(monkeypatch, tmp_path):
    from backend.app.api.tasks import task_store
    from backend.app.api import uploads
    from backend.app.main import app

    task_store.clear()
    monkeypatch.setattr(uploads, "STORAGE_DIR", str(tmp_path / "storage"))
    client = TestClient(app)
    payload = _docx_payload("example")

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
    assert stored.status in {"pending", "running", "success", "success_with_warnings"}
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


def test_upload_rejects_invalid_file_signature():
    from backend.app.api.tasks import task_store
    from backend.app.main import app

    task_store.clear()
    client = TestClient(app)

    response = client.post(
        "/api/upload",
        files={"file": ("sample.docx", b"not-a-zip", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid file signature for .docx"}
    assert task_store == {}


def test_upload_rejects_file_too_large(monkeypatch):
    from backend.app.api.tasks import task_store
    from backend.app.api import uploads
    from backend.app.main import app

    task_store.clear()
    monkeypatch.setattr(uploads, "MAX_UPLOAD_BYTES", 8)
    client = TestClient(app)

    response = client.post(
        "/api/upload",
        files={"file": ("sample.pdf", b"%PDF-" + b"x" * 64, "application/pdf")},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "file too large: max 8 bytes"}
    assert task_store == {}


def test_upload_rate_limit_returns_429(monkeypatch, tmp_path):
    from backend.app.api.tasks import task_store
    from backend.app.api import uploads
    from backend.app.main import app

    task_store.clear()
    uploads._upload_rate_window.clear()
    monkeypatch.setattr(uploads, "STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setattr(uploads, "UPLOAD_RATE_LIMIT_MAX_REQUESTS", 1)
    monkeypatch.setattr(uploads, "UPLOAD_RATE_LIMIT_WINDOW_SECONDS", 60)
    client = TestClient(app)
    payload = _docx_payload("rate-limited")

    first = client.post(
        "/api/upload",
        files={"file": ("sample.docx", payload, "application/octet-stream")},
    )
    second = client.post(
        "/api/upload",
        files={"file": ("sample.docx", payload, "application/octet-stream")},
    )

    assert first.status_code == 201
    assert second.status_code == 429
    assert second.json() == {"detail": "upload rate limit exceeded"}
    uploads._upload_rate_window.clear()
