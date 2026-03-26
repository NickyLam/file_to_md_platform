from dataclasses import dataclass

from backend.app.services.storage import StorageService


@dataclass(frozen=True)
class RetentionPolicy:
    keep_raw: bool = True
    keep_markdown: bool = True
    keep_artifacts: bool = True
    keep_temporary_files: bool = True

    def apply(self, storage: StorageService, task_id: str) -> None:
        if not self.keep_raw:
            storage.delete_raw(task_id)
        if not self.keep_markdown:
            storage.delete_markdown(task_id)
        if not self.keep_artifacts:
            storage.delete_artifacts(task_id)
        if not self.keep_temporary_files:
            storage.delete_temp_artifacts(task_id)
        if not self.keep_raw and not self.keep_markdown and not self.keep_artifacts and not self.keep_temporary_files:
            storage.cleanup_task(task_id)
