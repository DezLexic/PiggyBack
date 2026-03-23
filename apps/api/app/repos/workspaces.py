from __future__ import annotations

from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row


def create_workspace(conn: Connection, name: str) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO workspaces (name)
            VALUES (%s)
            RETURNING id, name, created_at
            """,
            (name,),
        )
        row = cur.fetchone()
    assert row is not None
    return dict(row)


def list_workspaces(conn: Connection) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, name, created_at FROM workspaces ORDER BY created_at ASC"
        )
        return [dict(r) for r in cur.fetchall()]


def get_workspace(conn: Connection, workspace_id: UUID) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, name, created_at FROM workspaces WHERE id = %s",
            (workspace_id,),
        )
        row = cur.fetchone()
    return dict(row) if row else None
