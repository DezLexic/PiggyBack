from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation

from app.db.deps import DbConn
from app.repos import permissions as permissions_repo
from app.repos import projects as projects_repo
from app.schemas import PermissionGrant, PermissionRead

router = APIRouter(tags=["permissions"])


@router.post("/projects/{project_id}/permissions", response_model=PermissionRead)
def grant_project_permission(
    project_id: UUID,
    body: PermissionGrant,
    conn: DbConn,
) -> PermissionRead:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        row = permissions_repo.grant_permission(
            conn,
            project_id,
            body.agent_connection_id,
            body.permission_type,
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="Invalid agent_connection_id",
        ) from None
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Permission already granted for this agent, project, and type",
        ) from None
    except CheckViolation:
        raise HTTPException(
            status_code=400,
            detail="Invalid permission_type",
        ) from None
    return PermissionRead.model_validate(row)


@router.get("/projects/{project_id}/permissions", response_model=list[PermissionRead])
def list_project_permissions(project_id: UUID, conn: DbConn) -> list[PermissionRead]:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    rows = permissions_repo.list_permissions_for_project(conn, project_id)
    return [PermissionRead.model_validate(r) for r in rows]
