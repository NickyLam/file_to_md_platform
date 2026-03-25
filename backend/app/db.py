from pathlib import Path


MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"


def load_migration(name: str) -> str:
    return (MIGRATIONS_DIR / name).read_text(encoding="utf-8")
