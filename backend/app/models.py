from dataclasses import dataclass, field
from datetime import datetime, timezone


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
    updated_at: datetime = field(init=False)

    def __post_init__(self) -> None:
        if self.status not in TASK_STATUSES:
            raise ValueError(f"unsupported task status: {self.status}")
        object.__setattr__(self, "updated_at", self.created_at)


@dataclass(frozen=True)
class AuditLogRecord:
    audit_id: str
    task_id: str
    event_type: str
    ip_address: str
    device_id: str
    file_hash: str
    created_at: datetime = field(default_factory=utc_now)
