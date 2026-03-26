from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from backend.app.models import AuditLogRecord, TaskRecord
from backend.app.repositories.audit import audit_log_params


@dataclass(frozen=True)
class AuditCapture:
    audit_log: AuditLogRecord
    markdown_text: Optional[str] = None


def build_audit_record(
    *,
    task: TaskRecord,
    event_type: str,
    ip_address: str,
    device_id: str,
    duration_ms: Optional[int] = None,
    failure_reason_code: Optional[str] = None,
    engine_version: Optional[str] = None,
    ocr_enabled: bool = False,
    model_enabled: bool = False,
) -> AuditCapture:
    return AuditCapture(
        audit_log=AuditLogRecord(
            audit_id=uuid4().hex,
            task_id=task.task_id,
            event_type=event_type,
            ip_address=ip_address,
            device_id=device_id,
            file_hash=task.file_hash,
            task_status=task.status,
            duration_ms=duration_ms,
            failure_reason_code=failure_reason_code,
            engine_version=engine_version,
            ocr_enabled=ocr_enabled,
            model_enabled=model_enabled,
        ),
        markdown_text=None,
    )


def audit_params(capture: AuditCapture) -> dict[str, object]:
    return audit_log_params(capture.audit_log)
