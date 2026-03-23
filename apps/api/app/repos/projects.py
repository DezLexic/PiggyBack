from __future__ import annotations

from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row


def create_project(conn: Connection, workspace_id: UUID, name: str) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO projects (workspace_id, name)
            VALUES (%s, %s)
            RETURNING id, workspace_id, name, created_at
            """,
            (workspace_id, name),
        )
        row = cur.fetchone()
    assert row is not None
    return dict(row)


def list_projects(conn: Connection, workspace_id: UUID) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, workspace_id, name, created_at
            FROM projects
            WHERE workspace_id = %s
            ORDER BY created_at ASC
            """,
            (workspace_id,),
        )
        return [dict(r) for r in cur.fetchall()]


def get_project(conn: Connection, project_id: UUID) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, workspace_id, name, created_at
            FROM projects
            WHERE id = %s
            """,
            (project_id,),
        )
        row = cur.fetchone()
    return dict(row) if row else None
