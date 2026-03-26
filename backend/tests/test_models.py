import re


def test_task_record_has_required_status_values():
    from backend.app.db import load_migration
    from backend.app.models import TaskRecord
    from backend.app.statuses import TASK_STATUSES

    task = TaskRecord(
        task_id="task_123",
        file_name="sample.docx",
        file_type="docx",
        file_hash="abc123",
        file_size=123,
        status="pending",
        access_token="token_123",
    )

    assert task.status in TASK_STATUSES
    assert task.created_at == task.updated_at
    assert TASK_STATUSES == {
        "pending",
        "running",
        "success",
        "failed",
        "success_with_warnings",
    }


def test_initial_migration_defines_tasks_and_audit_tables():
    from backend.app.db import load_migration

    sql = load_migration("001_init.sql")

    assert "CREATE TABLE tasks" in sql
    assert "CREATE TABLE audit_logs" in sql
    assert "CONSTRAINT tasks_status_check CHECK" in sql
    assert "CONSTRAINT audit_logs_status_check CHECK" in sql
    task_check = re.search(
        r"CONSTRAINT tasks_status_check CHECK \(\s*status IN \((.*?)\)\s*\)\s*",
        sql,
        re.S,
    )
    audit_check = re.search(
        r"CONSTRAINT audit_logs_status_check CHECK \(\s*task_status IN \((.*?)\)\s*\)\s*",
        sql,
        re.S,
    )
    assert task_check is not None
    assert audit_check is not None
    allowed_statuses = set(re.findall(r"'([^']+)'", task_check.group(1)))
    audit_statuses = set(re.findall(r"'([^']+)'", audit_check.group(1)))
    expected_statuses = {
        "pending",
        "running",
        "success",
        "failed",
        "success_with_warnings",
    }
    assert allowed_statuses == expected_statuses
    assert audit_statuses == expected_statuses
