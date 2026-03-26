from collections import deque
from datetime import datetime, timedelta
import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile, status

from backend.app.api.tasks import create_task
from backend.app.models import utc_now
from backend.app.services.storage import StorageService
from backend.app.worker import process_task


router = APIRouter()

SUPPORTED_EXTENSIONS = frozenset({"docx", "pdf", "xlsx"})
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))
UPLOAD_READ_CHUNK_BYTES = 1024 * 1024
UPLOAD_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("UPLOAD_RATE_LIMIT_MAX_REQUESTS", "20"))
UPLOAD_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("UPLOAD_RATE_LIMIT_WINDOW_SECONDS", "60"))
STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")
_upload_rate_window: dict[str, deque[datetime]] = {}


def _has_valid_signature(extension: str, content: bytes) -> bool:
    if extension == "pdf":
        return content.startswith(b"%PDF-")
    if extension in {"docx", "xlsx"}:
        return content.startswith(b"PK\x03\x04")
    return False


def _resolve_client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _enforce_upload_rate_limit(request: Request, now: datetime) -> None:
    window_start = now - timedelta(seconds=UPLOAD_RATE_LIMIT_WINDOW_SECONDS)
    for ip_address, entries in list(_upload_rate_window.items()):
        while entries and entries[0] < window_start:
            entries.popleft()
        if not entries:
            _upload_rate_window.pop(ip_address, None)

    client_ip = _resolve_client_ip(request)
    entries = _upload_rate_window.setdefault(client_ip, deque())
    if len(entries) >= UPLOAD_RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="upload rate limit exceeded")
    entries.append(now)


@router.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(background_tasks: BackgroundTasks, request: Request, file: UploadFile = File(...)) -> dict[str, str]:
    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unsupported file extension: {extension or 'unknown'}",
        )
    _enforce_upload_rate_limit(request, utc_now())

    chunks: list[bytes] = []
    total_size = 0
    while True:
        chunk = await file.read(UPLOAD_READ_CHUNK_BYTES)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"file too large: max {MAX_UPLOAD_BYTES} bytes",
            )
        chunks.append(chunk)
    contents = b"".join(chunks)
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty file is not allowed")
    if not _has_valid_signature(extension, contents):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"invalid file signature for .{extension}")

    task = create_task(file_name=file.filename or "", file_bytes=contents)
    storage = StorageService(STORAGE_DIR)
    source_path = storage.write_raw(task.task_id, file.filename or f"upload.{extension}", contents)
    background_tasks.add_task(process_task, task.task_id, source_path, storage)
    return {"task_id": task.task_id, "access_token": task.access_token}
