from importlib.resources import files


def load_migration(name: str) -> str:
    return (files("backend.migrations") / name).read_text(encoding="utf-8")
