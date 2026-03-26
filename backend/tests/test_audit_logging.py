from backend.app.api.tasks import create_task
from backend.app.services.audit import build_audit_record


def test_audit_log_never_stores_full_markdown() -> None:
    task = create_task(file_name="sample.docx", file_bytes=b"payload")

    record = build_audit_record(
        task=task,
        event_type="task_completed",
        ip_address="127.0.0.1",
        device_id="device-123",
        engine_version="1.0.0",
    )

    assert record.markdown_text is None
    assert record.audit_log.task_id == task.task_id


def test_audit_log_ids_are_unique() -> None:
    task = create_task(file_name="sample.docx", file_bytes=b"payload-2")

    first = build_audit_record(
        task=task,
        event_type="task_completed",
        ip_address="127.0.0.1",
        device_id="device-123",
    )
    second = build_audit_record(
        task=task,
        event_type="task_completed",
        ip_address="127.0.0.1",
        device_id="device-123",
    )

    assert first.audit_log.audit_id != second.audit_log.audit_id
