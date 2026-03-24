from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from psycopg import Connection

from app.core.config import settings
from app.db.deps import get_db
from app.repos import api_keys as api_keys_repo
from app.repos import permissions as permissions_repo

# These permission types grant read access to a project.
READ_PERMISSION_TYPES = ("read", "propose_update", "write")


@dataclass
class CallerInfo:
    is_admin: bool
    agent_connection_id: UUID | None = field(default=None)


def resolve_caller(
    conn: Annotated[Connection, Depends(get_db)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> CallerInfo:
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    if settings.admin_api_key and x_api_key == settings.admin_api_key:
        return CallerInfo(is_admin=True)
    key_record = api_keys_repo.verify_api_key(conn, x_api_key)
    if key_record is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    agent_id = key_record.get("agent_connection_id")
    return CallerInfo(
        is_admin=False,
        agent_connection_id=UUID(str(agent_id)) if agent_id else None,
    )


# Use as a route parameter type: `caller: Caller`
Caller = Annotated[CallerInfo, Depends(resolve_caller)]

# Backward-compatible alias for routes that only need 401 enforcement (no project check).
RequireApiKey = Caller


def assert_project_permission(
    conn: Connection,
    caller: CallerInfo,
    project_id: UUID,
    allowed_types: tuple[str, ...],
) -> None:
    """Raise 403 if the caller lacks one of the allowed_types on the project.

    Admin callers always pass.
    Pass an empty tuple to make a route admin-only (agents are always rejected).
    """
    if caller.is_admin:
        return
    if not allowed_types or caller.agent_connection_id is None:
        raise HTTPException(status_code=403, detail="Forbidden")
    for ptype in allowed_types:
        if permissions_repo.has_permission(conn, caller.agent_connection_id, project_id, ptype):
            return
    raise HTTPException(status_code=403, detail="Insufficient permissions on this project")
