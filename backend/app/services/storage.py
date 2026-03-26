from pathlib import Path
from typing import Union


class StorageService:
    def __init__(self, base_dir: Union[Path, str]) -> None:
        self.base_dir = Path(base_dir)

    def _task_dir(self, task_id: str) -> Path:
        path = self.base_dir / task_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_markdown(self, task_id: str, markdown: str) -> Path:
        path = self._task_dir(task_id) / "result.md"
        path.write_text(markdown, encoding="utf-8")
        return path

    def read_markdown(self, task_id: str) -> str:
        path = self._task_dir(task_id) / "result.md"
        return path.read_text(encoding="utf-8")

    def write_artifact(self, task_id: str, name: str, content: Union[bytes, str]) -> Path:
        artifact_dir = self._task_dir(task_id) / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        path = artifact_dir / name
        data = content.encode("utf-8") if isinstance(content, str) else content
        path.write_bytes(data)
        return path
