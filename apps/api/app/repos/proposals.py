from __future__ import annotations

from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row

from app.repos import files as files_repo


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


def get_by_id(conn: Connection, proposal_id: UUID) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, file_id, proposed_content, status, created_at
            FROM proposed_updates
            WHERE id = %s
            """,
            (proposal_id,),
        )
        row = cur.fetchone()
    return dict(row) if row else None


def accept_proposal(
    conn: Connection,
    proposal_id: UUID,
) -> tuple[bool, dict[str, Any] | None, dict[str, Any] | None]:
    """Returns (ok, proposal_row, file_row). ok False + None, None => not found;
    ok False + proposal_row, None => not pending (conflict)."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            UPDATE proposed_updates
            SET status = 'accepted'
            WHERE id = %s AND status = 'pending'
            RETURNING id, file_id, proposed_content, status, created_at
            """,
            (proposal_id,),
        )
        claimed = cur.fetchone()
    if not claimed:
        existing = get_by_id(conn, proposal_id)
        if existing is None:
            return False, None, None
        return False, existing, None

    file_id = claimed["file_id"]
    content = claimed["proposed_content"]
    files_repo.update_file_content(conn, file_id, content)
    proposal = get_by_id(conn, proposal_id)
    file_row = files_repo.get_file(conn, file_id)
    assert proposal is not None and file_row is not None
    return True, proposal, file_row


def reject_proposal(
    conn: Connection,
    proposal_id: UUID,
) -> tuple[bool, dict[str, Any] | None]:
    """Returns (ok, row). ok False + None => not found; ok False + row => not pending."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            UPDATE proposed_updates
            SET status = 'rejected'
            WHERE id = %s AND status = 'pending'
            RETURNING id, file_id, proposed_content, status, created_at
            """,
            (proposal_id,),
        )
        updated = cur.fetchone()
    if updated:
        return True, dict(updated)
    existing = get_by_id(conn, proposal_id)
    if existing is None:
        return False, None
    return False, existing
