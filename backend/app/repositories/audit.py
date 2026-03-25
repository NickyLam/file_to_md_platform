from backend.app.models import AuditLogRecord


INSERT_AUDIT_LOG_SQL = """
INSERT INTO audit_logs (
    audit_id,
    task_id,
    event_type,
    ip_address,
    device_id,
    file_hash,
    task_status,
    duration_ms,
    failure_reason_code,
    engine_version,
    ocr_enabled,
    model_enabled,
    created_at
) VALUES (
    :audit_id,
    :task_id,
    :event_type,
    :ip_address,
    :device_id,
    :file_hash,
    :task_status,
    :duration_ms,
    :failure_reason_code,
    :engine_version,
    :ocr_enabled,
    :model_enabled,
    :created_at
)
""".strip()


def audit_log_params(audit_log: AuditLogRecord) -> dict[str, object]:
    return {
        "audit_id": audit_log.audit_id,
        "task_id": audit_log.task_id,
        "event_type": audit_log.event_type,
        "ip_address": audit_log.ip_address,
        "device_id": audit_log.device_id,
        "file_hash": audit_log.file_hash,
        "task_status": audit_log.task_status,
        "duration_ms": audit_log.duration_ms,
        "failure_reason_code": audit_log.failure_reason_code,
        "engine_version": audit_log.engine_version,
        "ocr_enabled": audit_log.ocr_enabled,
        "model_enabled": audit_log.model_enabled,
        "created_at": audit_log.created_at,
    }
