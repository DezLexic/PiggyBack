from __future__ import annotations

from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row


def create_agent_connection(conn: Connection, name: str, agent_type: str) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO agent_connections (name, agent_type)
            VALUES (%s, %s)
            RETURNING id, name, agent_type, created_at
            """,
            (name, agent_type),
        )
        row = cur.fetchone()
    assert row is not None
    return dict(row)


def list_agent_connections(conn: Connection) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, name, agent_type, created_at
            FROM agent_connections
            ORDER BY created_at ASC
            """
        )
        return [dict(r) for r in cur.fetchall()]
