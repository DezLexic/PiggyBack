from __future__ import annotations

from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row


def grant_permission(
    conn: Connection,
    project_id: UUID,
    agent_connection_id: UUID,
    permission_type: str,
) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO permissions (project_id, agent_connection_id, permission_type)
            VALUES (%s, %s, %s)
            RETURNING id, project_id, agent_connection_id, permission_type, created_at
            """,
            (project_id, agent_connection_id, permission_type),
        )
        row = cur.fetchone()
    assert row is not None
    return dict(row)


def list_permissions_for_project(conn: Connection, project_id: UUID) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, project_id, agent_connection_id, permission_type, created_at
            FROM permissions
            WHERE project_id = %s
            ORDER BY created_at ASC
            """,
            (project_id,),
        )
        return [dict(r) for r in cur.fetchall()]
