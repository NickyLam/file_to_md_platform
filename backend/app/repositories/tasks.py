from backend.app.models import TaskRecord


INSERT_TASK_SQL = """
INSERT INTO tasks (
    task_id,
    file_hash,
    file_name,
    file_size,
    file_type,
    status,
    access_token,
    created_at,
    updated_at
) VALUES (
    :task_id,
    :file_hash,
    :file_name,
    :file_size,
    :file_type,
    :status,
    :access_token,
    :created_at,
    :updated_at
)
""".strip()


def task_params(task: TaskRecord) -> dict[str, object]:
    return {
        "task_id": task.task_id,
        "file_hash": task.file_hash,
        "file_name": task.file_name,
        "file_size": task.file_size,
        "file_type": task.file_type,
        "status": task.status,
        "access_token": task.access_token,
        "markdown_preview": task.markdown_preview,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
