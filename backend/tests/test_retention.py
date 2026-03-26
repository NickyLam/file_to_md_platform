from pathlib import Path

from backend.app.services.retention import RetentionPolicy
from backend.app.services.storage import StorageService


def test_retention_can_remove_markdown_and_artifacts(tmp_path: Path) -> None:
    storage = StorageService(tmp_path / "storage")
    storage.write_raw("task-1", "input.docx", b"raw")
    storage.write_markdown("task-1", "# Example")
    storage.write_artifact("task-1", "warnings.txt", "warning")
    storage.write_temp_artifact("task-1", "scratch.txt", "temp")

    policy = RetentionPolicy(
        keep_raw=False,
        keep_markdown=False,
        keep_artifacts=False,
        keep_temporary_files=False,
    )
    policy.apply(storage, "task-1")

    assert not (storage.base_dir / "task-1").exists()
