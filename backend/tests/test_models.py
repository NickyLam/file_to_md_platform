from pathlib import Path


def test_task_record_has_required_status_values():
    from backend.app.models import TASK_STATUSES, TaskRecord

    task = TaskRecord(
        task_id="task_123",
        file_name="sample.docx",
        file_type="docx",
        file_hash="abc123",
        status="pending",
    )

    assert task.status in TASK_STATUSES
    assert TASK_STATUSES == {
        "pending",
        "running",
        "success",
        "failed",
        "success_with_warnings",
    }


def test_initial_migration_defines_tasks_and_audit_tables():
    migration_path = Path("backend/migrations/001_init.sql")
    sql = migration_path.read_text(encoding="utf-8")

    assert "CREATE TABLE tasks" in sql
    assert "CREATE TABLE audit_logs" in sql
    assert "success_with_warnings" in sql
