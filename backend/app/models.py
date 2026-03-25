from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


TASK_STATUSES = {
    "pending",
    "running",
    "success",
    "failed",
    "success_with_warnings",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    file_hash: str
    file_name: str
    file_type: str
    status: str
    file_size: int
    access_token: str
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.status not in TASK_STATUSES:
            raise ValueError(f"unsupported task status: {self.status}")

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
    ) -> "TaskRecord":
        created_at = utc_now()
        return cls(
            task_id=task_id,
            file_hash=file_hash,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            status=status,
            access_token=access_token,
            created_at=created_at,
            updated_at=created_at,
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
