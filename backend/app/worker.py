from pathlib import Path
import os
from typing import Callable, Optional, Union

from backend.app.api.tasks import get_task, task_store
from backend.app.converters.base import ConversionResult
from backend.app.converters.docx import convert_docx
from backend.app.converters.pdf import convert_pdf
from backend.app.converters.xlsx import convert_xlsx
from backend.app.models import TaskRecord, utc_now
from backend.app.repositories.tasks import task_params
from backend.app.services.storage import StorageService


Converter = Callable[[Path], ConversionResult]

CONVERTERS: dict[str, Converter] = {
    "docx": convert_docx,
    "pdf": convert_pdf,
    "xlsx": convert_xlsx,
}
MARKDOWN_PREVIEW_MAX_CHARS = int(os.getenv("MARKDOWN_PREVIEW_MAX_CHARS", "20000"))


class ConversionWorker:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage
        self.task_snapshots: dict[str, dict[str, object]] = {}

    def process_task(self, task_id: str, source_path: Union[Path, str]) -> TaskRecord:
        task = get_task(task_id)
        if task is None:
            raise KeyError(f"task not found: {task_id}")

        running = self._set_status(task, "running")
        converter = CONVERTERS.get(running.file_type.lower())
        if converter is None:
            self._set_status(running, "failed")
            raise ValueError(f"unsupported file type: {running.file_type}")

        try:
            result = converter(Path(source_path))
            if not result.markdown.strip():
                self.storage.cleanup_task(task_id)
                return self._set_status(running, "failed", markdown_preview=None)
            self.storage.write_markdown(task_id, result.markdown)
            markdown_preview = result.markdown[:MARKDOWN_PREVIEW_MAX_CHARS]
            for artifact_name, artifact_data in result.artifacts.items():
                self.storage.write_artifact(task_id, artifact_name, artifact_data)
        except Exception:
            self.storage.cleanup_task(task_id)
            self._set_status(running, "failed", markdown_preview=None)
            raise

        final_status = "success_with_warnings" if result.warnings else "success"
        return self._set_status(running, final_status, markdown_preview=markdown_preview)

    def _set_status(self, task: TaskRecord, status: str, markdown_preview: Optional[str] = None) -> TaskRecord:
        updated = TaskRecord(
            task_id=task.task_id,
            file_hash=task.file_hash,
            file_name=task.file_name,
            file_type=task.file_type,
            file_size=task.file_size,
            status=status,
            access_token=task.access_token,
            markdown_preview=markdown_preview,
            created_at=task.created_at,
            updated_at=utc_now(),
        )
        task_store[task.task_id] = updated
        self.task_snapshots[task.task_id] = task_params(updated)
        return updated


def process_task(task_id: str, source_path: Union[Path, str], storage: StorageService) -> TaskRecord:
    return ConversionWorker(storage).process_task(task_id, source_path)
