from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.app.api.tasks import create_task


router = APIRouter()

SUPPORTED_EXTENSIONS = frozenset({"docx", "pdf", "xlsx"})


@router.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unsupported file extension: {extension or 'unknown'}",
        )

    contents = await file.read()
    task = create_task(file_name=file.filename or "", file_bytes=contents)
    return {"task_id": task.task_id, "access_token": task.access_token}
