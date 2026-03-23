"""Apply ordered SQL migrations; track applied files in schema_migrations."""

from __future__ import annotations

import logging
from pathlib import Path

import psycopg

logger = logging.getLogger(__name__)


def _migrations_dir() -> Path:
    # apps/api/app/db/migrate.py -> apps/api/migrations
    return Path(__file__).resolve().parent.parent.parent / "migrations"


def _ensure_migration_table(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )


def run_migrations(dsn: str) -> None:
    migrations_dir = _migrations_dir()
    if not migrations_dir.is_dir():
        logger.warning("Migrations directory missing at %s; skipping", migrations_dir)
        return

    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        return

    with psycopg.connect(dsn, autocommit=True) as conn:
        _ensure_migration_table(conn)
        applied_rows = conn.execute("SELECT filename FROM schema_migrations").fetchall()
        applied = {row[0] for row in applied_rows}

        for path in sql_files:
            name = path.name
            if name in applied:
                continue
            logger.info("Applying migration %s", name)
            sql = path.read_text(encoding="utf-8")
            conn.execute(sql)
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (%s)",
                (name,),
            )
            applied.add(name)


def main() -> None:
    import os
    import sys

    logging.basicConfig(level=logging.INFO)
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL is not set", file=sys.stderr)
        sys.exit(1)
    run_migrations(dsn)
    print("Migrations applied.")


if __name__ == "__main__":
    main()
