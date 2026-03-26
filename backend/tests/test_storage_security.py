from backend.app.services.storage import StorageService


def test_storage_sanitizes_nested_names(tmp_path):
    storage = StorageService(tmp_path / "storage")

    raw_path = storage.write_raw("task-1", "../raw.txt", b"raw")
    artifact_path = storage.write_artifact("task-1", "../../artifact.txt", b"artifact")
    temp_path = storage.write_temp_artifact("task-1", "subdir/../temp.txt", b"temp")

    assert raw_path.parent.name == "raw"
    assert artifact_path.parent.name == "artifacts"
    assert temp_path.parent.name == "temp"
