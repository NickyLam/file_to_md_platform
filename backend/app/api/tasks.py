from collections.abc import Mapping
from hashlib import sha256
from secrets import token_urlsafe
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status

from backend.app.models import TaskRecord


task_store: dict[str, TaskRecord] = {}


def create_task(*, file_name: str, file_bytes: bytes) -> TaskRecord:
    file_type = file_name.rsplit(".", maxsplit=1)[-1].lower()
    task = TaskRecord.create(
        task_id=uuid4().hex,
        file_hash=sha256(file_bytes).hexdigest(),
        file_name=file_name,
        file_type=file_type,
        file_size=len(file_bytes),
        status="pending",
        access_token=token_urlsafe(24),
    )
    task_store[task.task_id] = task
    return task


def get_task(task_id: str) -> Optional[TaskRecord]:
    return task_store.get(task_id)


def list_tasks() -> Mapping[str, TaskRecord]:
    return task_store


def require_task_access(task_id: str, access_token: Optional[str]) -> TaskRecord:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access token required")

    task = get_task(task_id)
    if task is None or access_token != task.access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid access token")

    return task
