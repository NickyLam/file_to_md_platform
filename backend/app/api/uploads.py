from pathlib import Path
import os

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from backend.app.api.tasks import create_task
from backend.app.services.storage import StorageService
from backend.app.worker import process_task


router = APIRouter()

SUPPORTED_EXTENSIONS = frozenset({"docx", "pdf", "xlsx"})
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))
UPLOAD_READ_CHUNK_BYTES = 1024 * 1024
STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")


def _has_valid_signature(extension: str, content: bytes) -> bool:
    if extension == "pdf":
        return content.startswith(b"%PDF-")
    if extension in {"docx", "xlsx"}:
        return content.startswith(b"PK\x03\x04")
    return False


@router.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> dict[str, str]:
    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unsupported file extension: {extension or 'unknown'}",
        )

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
