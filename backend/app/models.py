from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from backend.app.statuses import TASK_STATUSES


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, init=False)
class TaskRecord:
    task_id: str
    file_hash: str
    file_name: str
    file_type: str
    status: str
    file_size: int
    access_token: str
    markdown_preview: Optional[str]
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        *,
        task_id: str,
        file_hash: str,
        file_name: str,
        file_type: str,
        file_size: int,
        status: str,
        access_token: str,
        markdown_preview: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        if status not in TASK_STATUSES:
            raise ValueError(f"unsupported task status: {status}")

        created_value = created_at or utc_now()
        updated_value = created_value if updated_at is None else updated_at

        object.__setattr__(self, "task_id", task_id)
        object.__setattr__(self, "file_hash", file_hash)
        object.__setattr__(self, "file_name", file_name)
        object.__setattr__(self, "file_type", file_type)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "file_size", file_size)
        object.__setattr__(self, "access_token", access_token)
        object.__setattr__(self, "markdown_preview", markdown_preview)
        object.__setattr__(self, "created_at", created_value)
        object.__setattr__(self, "updated_at", updated_value)

    @classmethod
    def create(
        cls,
        *,
        task_id: str,
        file_hash: str,
        file_name: str,
        file_type: str,
        file_size: int,
        status: str,
        access_token: str,
        markdown_preview: Optional[str] = None,
    ) -> "TaskRecord":
        return cls(
            task_id=task_id,
            file_hash=file_hash,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            status=status,
            access_token=access_token,
            markdown_preview=markdown_preview,
        )


@dataclass(frozen=True)
class AuditLogRecord:
    audit_id: str
    task_id: str
    event_type: str
    ip_address: str
    device_id: str
    file_hash: str
    task_status: str
    duration_ms: Optional[int] = None
    failure_reason_code: Optional[str] = None
    engine_version: Optional[str] = None
    ocr_enabled: bool = False
    model_enabled: bool = False
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.task_status not in TASK_STATUSES:
            raise ValueError(f"unsupported task status: {self.task_status}")
