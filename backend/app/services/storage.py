from pathlib import Path
import shutil
from typing import Union


class StorageService:
    def __init__(self, base_dir: Union[Path, str]) -> None:
        self.base_dir = Path(base_dir)

    def _task_dir(self, task_id: str) -> Path:
        path = self.base_dir / task_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _safe_name(self, name: str) -> str:
        safe_name = Path(name).name
        return safe_name or "artifact"

    def write_markdown(self, task_id: str, markdown: str) -> Path:
        path = self._task_dir(task_id) / "result.md"
        path.write_text(markdown, encoding="utf-8")
        return path

    def write_raw(self, task_id: str, name: str, content: Union[bytes, str]) -> Path:
        raw_dir = self._task_dir(task_id) / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        path = raw_dir / self._safe_name(name)
        data = content.encode("utf-8") if isinstance(content, str) else content
        path.write_bytes(data)
        return path

    def read_markdown(self, task_id: str) -> str:
        path = self.base_dir / task_id / "result.md"
        return path.read_text(encoding="utf-8")

    def write_artifact(self, task_id: str, name: str, content: Union[bytes, str]) -> Path:
        artifact_dir = self._task_dir(task_id) / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        path = artifact_dir / self._safe_name(name)
        data = content.encode("utf-8") if isinstance(content, str) else content
        path.write_bytes(data)
        return path

    def delete_markdown(self, task_id: str) -> None:
        path = self.base_dir / task_id / "result.md"
        if path.exists():
            path.unlink()

    def delete_raw(self, task_id: str) -> None:
        raw_dir = self.base_dir / task_id / "raw"
        if raw_dir.exists():
            for child in raw_dir.iterdir():
                if child.is_file():
                    child.unlink()
            raw_dir.rmdir()

    def delete_artifacts(self, task_id: str) -> None:
        artifact_dir = self.base_dir / task_id / "artifacts"
        if artifact_dir.exists():
            for child in artifact_dir.iterdir():
                if child.is_file():
                    child.unlink()
            artifact_dir.rmdir()

    def write_temp_artifact(self, task_id: str, name: str, content: Union[bytes, str]) -> Path:
        temp_dir = self._task_dir(task_id) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        path = temp_dir / self._safe_name(name)
        data = content.encode("utf-8") if isinstance(content, str) else content
        path.write_bytes(data)
        return path

    def delete_temp_artifacts(self, task_id: str) -> None:
        temp_dir = self.base_dir / task_id / "temp"
        if temp_dir.exists():
            for child in temp_dir.iterdir():
                if child.is_file():
                    child.unlink()
            temp_dir.rmdir()

    def cleanup_task(self, task_id: str) -> None:
        path = self.base_dir / task_id
        if path.exists():
            shutil.rmtree(path)
