from __future__ import annotations

from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row


def create_proposal(conn: Connection, file_id: UUID, proposed_content: str) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO proposed_updates (file_id, proposed_content)
            VALUES (%s, %s)
            RETURNING id, file_id, proposed_content, status, created_at
            """,
            (file_id, proposed_content),
        )
        row = cur.fetchone()
    assert row is not None
    return dict(row)


def list_proposals(conn: Connection, file_id: UUID) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, file_id, proposed_content, status, created_at
            FROM proposed_updates
            WHERE file_id = %s
            ORDER BY created_at DESC
            """,
            (file_id,),
        )
        return [dict(r) for r in cur.fetchall()]
