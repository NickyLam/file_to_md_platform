from backend.app.models import AuditLogRecord


INSERT_AUDIT_LOG_SQL = """
INSERT INTO audit_logs (
    audit_id,
    task_id,
    event_type,
    ip_address,
    device_id,
    file_hash,
    created_at
) VALUES (
    :audit_id,
    :task_id,
    :event_type,
    :ip_address,
    :device_id,
    :file_hash,
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
        "created_at": audit_log.created_at,
    }
