from pathlib import Path
from zipfile import ZipFile

from fastapi.testclient import TestClient


def _write_docx(path: Path, text: str) -> None:
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>
</w:document>
"""
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)


def test_status_requires_access_token():
    from backend.app.main import app

    client = TestClient(app)
    response = client.get("/api/tasks/123")

    assert response.status_code == 401


def test_status_rejects_invalid_access_token():
    from backend.app.api.tasks import create_task, task_store
    from backend.app.main import app
    from backend.app.worker import task_markdowns

    task_store.clear()
    task_markdowns.clear()
    task = create_task(file_name="sample.docx", file_bytes=b"example")
    client = TestClient(app)

    response = client.get(f"/api/tasks/{task.task_id}", headers={"X-Access-Token": "wrong"})

    assert response.status_code == 401


def test_status_returns_task_state_with_valid_access_token():
    from backend.app.api.tasks import create_task, task_store
    from backend.app.main import app
    from backend.app.worker import task_markdowns

    task_store.clear()
    task_markdowns.clear()
    task = create_task(file_name="sample.docx", file_bytes=b"example")
    client = TestClient(app)

    response = client.get(f"/api/tasks/{task.task_id}", headers={"X-Access-Token": task.access_token})

    assert response.status_code == 200
    assert response.json()["task_id"] == task.task_id
    assert response.json()["status"] == "pending"


def test_status_returns_markdown_after_successful_conversion(tmp_path: Path):
    from backend.app.api.tasks import create_task, task_store
    from backend.app.main import app
    from backend.app.services.storage import StorageService
    from backend.app.worker import process_task, task_markdowns

    task_store.clear()
    task_markdowns.clear()
    source = tmp_path / "sample.docx"
    _write_docx(source, "Converted body")
    task = create_task(file_name="sample.docx", file_bytes=source.read_bytes())
    storage = StorageService(tmp_path / "storage")
    process_task(task.task_id, source, storage)

    client = TestClient(app)
    response = client.get(f"/api/tasks/{task.task_id}", headers={"X-Access-Token": task.access_token})

    assert response.status_code == 200
    assert response.json()["markdown"].startswith("# Converted body")


def test_worker_marks_empty_markdown_as_failed(tmp_path: Path):
    from backend.app.api.tasks import create_task, task_store
    from backend.app.converters.base import ConversionResult
    from backend.app.services.storage import StorageService
    from backend.app.worker import CONVERTERS, process_task, task_markdowns

    task_store.clear()
    task_markdowns.clear()
    source = tmp_path / "sample.docx"
    _write_docx(source, "ignored")
    task = create_task(file_name="sample.docx", file_bytes=source.read_bytes())
    storage = StorageService(tmp_path / "storage")
    original = CONVERTERS["docx"]

    try:
        CONVERTERS["docx"] = lambda _: ConversionResult(markdown="", warnings=("no text",))
        updated = process_task(task.task_id, source, storage)
    finally:
        CONVERTERS["docx"] = original

    assert updated.status == "failed"
    assert task_store[task.task_id].status == "failed"
    assert not (storage.base_dir / task.task_id).exists()
