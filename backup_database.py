"""Create a consistent backup of the configured SQLite database."""
from datetime import datetime
from pathlib import Path
import sqlite3

from backend.app.config import settings


def main() -> None:
    if not settings.DATABASE_URL.startswith("sqlite:///"):
        raise SystemExit("Este utilitário suporta apenas DATABASE_URL SQLite.")

    database_path = Path(settings.DATABASE_URL.removeprefix("sqlite:///"))
    if not database_path.is_absolute():
        database_path = Path.cwd() / database_path
    if not database_path.exists():
        raise SystemExit(f"Banco não encontrado: {database_path}")

    backup_dir = database_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"{database_path.stem}-{timestamp}.db"

    source = sqlite3.connect(database_path)
    destination = sqlite3.connect(backup_path)
    try:
        source.backup(destination)
        result = destination.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            backup_path.unlink(missing_ok=True)
            raise SystemExit(f"Backup inválido: {result}")
    finally:
        destination.close()
        source.close()

    print(f"Backup criado: {backup_path}")
    print(f"Integridade: {result}")


if __name__ == "__main__":
    main()
