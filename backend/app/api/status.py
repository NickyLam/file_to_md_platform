from typing import Optional

from fastapi import APIRouter, Header

from backend.app.api.tasks import require_task_access


router = APIRouter()


@router.get("/api/tasks/{task_id}")
def get_task_status(task_id: str, access_token: Optional[str] = Header(default=None, alias="X-Access-Token")) -> dict[str, object]:
    task = require_task_access(task_id, access_token)
    return {
        "task_id": task.task_id,
        "status": task.status,
        "file_name": task.file_name,
        "file_type": task.file_type,
        "file_size": task.file_size,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
