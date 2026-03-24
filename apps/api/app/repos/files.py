from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row


def _row_file_read(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "project_id": row["project_id"],
        "path": row["path"],
        "current_version_id": row["current_version_id"],
        "content": row["content"] if row["content"] is not None else "",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_file(conn: Connection, project_id: UUID, path: str, content: str) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO files (project_id, path)
            VALUES (%s, %s)
            RETURNING id, project_id, path, current_version_id, created_at, updated_at
            """,
            (project_id, path),
        )
        file_row = cur.fetchone()
        assert file_row is not None
        file_id = file_row["id"]
        cur.execute(
            """
            INSERT INTO file_versions (file_id, content)
            VALUES (%s, %s)
            RETURNING id
            """,
            (file_id, content),
        )
        ver = cur.fetchone()
        assert ver is not None
        version_id = ver["id"]
        cur.execute(
            """
            UPDATE files
            SET current_version_id = %s, updated_at = %s
            WHERE id = %s
            """,
            (version_id, datetime.now(UTC), file_id),
        )
    out = get_file(conn, file_id)
    assert out is not None
    return out


def list_files(conn: Connection, project_id: UUID) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT f.id, f.project_id, f.path, f.current_version_id,
                   f.created_at, f.updated_at, v.content AS content
            FROM files f
            LEFT JOIN file_versions v ON v.id = f.current_version_id
            WHERE f.project_id = %s
            ORDER BY f.path ASC
            """,
            (project_id,),
        )
        return [_row_file_read(dict(r)) for r in cur.fetchall()]


def get_file(conn: Connection, file_id: UUID) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT f.id, f.project_id, f.path, f.current_version_id,
                   f.created_at, f.updated_at, v.content AS content
            FROM files f
            LEFT JOIN file_versions v ON v.id = f.current_version_id
            WHERE f.id = %s
            """,
            (file_id,),
        )
        row = cur.fetchone()
    return _row_file_read(dict(row)) if row else None


def update_file_content(conn: Connection, file_id: UUID, content: str) -> dict[str, Any] | None:
    existing = get_file(conn, file_id)
    if existing is None:
        return None
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO file_versions (file_id, content)
            VALUES (%s, %s)
            RETURNING id
            """,
            (file_id, content),
        )
        ver = cur.fetchone()
        assert ver is not None
        version_id = ver["id"]
        cur.execute(
            """
            UPDATE files
            SET current_version_id = %s, updated_at = %s
            WHERE id = %s
            """,
            (version_id, datetime.now(UTC), file_id),
        )
    return get_file(conn, file_id)


def get_file_by_path(conn: Connection, project_id: UUID, path: str) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT f.id, f.project_id, f.path, f.current_version_id,
                   f.created_at, f.updated_at, v.content AS content
            FROM files f
            LEFT JOIN file_versions v ON v.id = f.current_version_id
            WHERE f.project_id = %s AND f.path = %s
            """,
            (project_id, path),
        )
        row = cur.fetchone()
    return _row_file_read(dict(row)) if row else None


def upsert_file(
    conn: Connection, project_id: UUID, path: str, content: str, append: bool = False
) -> tuple[dict[str, Any], UUID, datetime]:
    """Create or replace a file. If append=True and the file exists, prepend existing content."""
    existing = get_file_by_path(conn, project_id, path)
    if existing is None:
        row = create_file(conn, project_id, path, content)
        assert row["current_version_id"] is not None
        # Fetch version created_at
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, created_at FROM file_versions WHERE id = %s",
                (row["current_version_id"],),
            )
            ver = cur.fetchone()
        assert ver is not None
        return row, ver["id"], ver["created_at"]
    else:
        final_content = existing["content"] + "\n" + content if append else content
        updated = update_file_content(conn, existing["id"], final_content)
        assert updated is not None
        assert updated["current_version_id"] is not None
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, created_at FROM file_versions WHERE id = %s",
                (updated["current_version_id"],),
            )
            ver = cur.fetchone()
        assert ver is not None
        return updated, ver["id"], ver["created_at"]


def list_versions(conn: Connection, file_id: UUID) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, file_id, content, created_at
            FROM file_versions
            WHERE file_id = %s
            ORDER BY created_at ASC
            """,
            (file_id,),
        )
        return [dict(r) for r in cur.fetchall()]
