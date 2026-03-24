from __future__ import annotations

import hashlib
import secrets
from typing import Any
from uuid import UUID

from psycopg import Connection
from psycopg.rows import dict_row


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_key() -> str:
    """Return a new plaintext key. Format: piggb_<48 hex chars>."""
    return "piggb_" + secrets.token_hex(24)


def create_api_key(
    conn: Connection,
    name: str,
    agent_connection_id: UUID | None = None,
) -> tuple[str, dict[str, Any]]:
    """Create a key row. Returns (plaintext_key, record) — plaintext shown once."""
    key = generate_key()
    key_hash = _hash(key)
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO api_keys (key_hash, name, agent_connection_id)
            VALUES (%s, %s, %s)
            RETURNING id, name, agent_connection_id, created_at
            """,
            (key_hash, name, agent_connection_id),
        )
        row = cur.fetchone()
    assert row is not None
    return key, dict(row)


def verify_api_key(conn: Connection, key: str) -> dict[str, Any] | None:
    """Return the key record if valid, else None."""
    key_hash = _hash(key)
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, name, agent_connection_id, created_at
            FROM api_keys
            WHERE key_hash = %s
            """,
            (key_hash,),
        )
        row = cur.fetchone()
    return dict(row) if row else None


def list_api_keys(conn: Connection) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, name, agent_connection_id, created_at
            FROM api_keys
            ORDER BY created_at ASC
            """
        )
        return [dict(r) for r in cur.fetchall()]
