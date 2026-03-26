from collections.abc import Mapping
from datetime import datetime, timedelta
from hashlib import sha256
import os
from secrets import token_urlsafe
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status

from backend.app.models import TaskRecord, utc_now


task_store: dict[str, TaskRecord] = {}
TASK_STORE_TTL_SECONDS = int(os.getenv("TASK_STORE_TTL_SECONDS", "3600"))
TASK_STORE_MAX_ITEMS = int(os.getenv("TASK_STORE_MAX_ITEMS", "2000"))


def _evict_tasks(now: datetime) -> None:
    expired_before = now - timedelta(seconds=TASK_STORE_TTL_SECONDS)
    stale_ids = [task_id for task_id, task in task_store.items() if task.updated_at < expired_before]
    for task_id in stale_ids:
        task_store.pop(task_id, None)

    if len(task_store) <= TASK_STORE_MAX_ITEMS:
        return

    oldest = sorted(task_store.items(), key=lambda item: item[1].updated_at)
    overflow = len(task_store) - TASK_STORE_MAX_ITEMS
    for task_id, _task in oldest[:overflow]:
        task_store.pop(task_id, None)


def create_task(*, file_name: str, file_bytes: bytes) -> TaskRecord:
    _evict_tasks(utc_now())
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
    _evict_tasks(utc_now())
    return task_store.get(task_id)


def list_tasks() -> Mapping[str, TaskRecord]:
    _evict_tasks(utc_now())
    return task_store


def require_task_access(task_id: str, access_token: Optional[str]) -> TaskRecord:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="access token required")

    task = get_task(task_id)
    if task is None or access_token != task.access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid access token")

    return task
