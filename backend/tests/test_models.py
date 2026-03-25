from pathlib import Path
import re


def test_task_record_has_required_status_values():
    from backend.app.models import TASK_STATUSES, TaskRecord

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
    migration_path = Path(__file__).resolve().parents[1] / "migrations" / "001_init.sql"
    sql = migration_path.read_text(encoding="utf-8")

    assert "CREATE TABLE tasks" in sql
    assert "CREATE TABLE audit_logs" in sql
    assert "CONSTRAINT tasks_status_check CHECK" in sql
    allowed_statuses = set(re.findall(r"'([^']+)'", sql))
    assert allowed_statuses == {
        "pending",
        "running",
        "success",
        "failed",
        "success_with_warnings",
    }
