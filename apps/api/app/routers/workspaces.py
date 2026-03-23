from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db.deps import DbConn
from app.repos import projects as projects_repo
from app.repos import workspaces as workspaces_repo
from app.schemas import ProjectCreate, ProjectRead, WorkspaceCreate, WorkspaceRead

router = APIRouter(tags=["workspaces"])


@router.post("/workspaces", response_model=WorkspaceRead)
def create_workspace(body: WorkspaceCreate, conn: DbConn) -> WorkspaceRead:
    row = workspaces_repo.create_workspace(conn, body.name)
    return WorkspaceRead.model_validate(row)


@router.get("/workspaces", response_model=list[WorkspaceRead])
def list_workspaces(conn: DbConn) -> list[WorkspaceRead]:
    rows = workspaces_repo.list_workspaces(conn)
    return [WorkspaceRead.model_validate(r) for r in rows]


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(workspace_id: UUID, conn: DbConn) -> WorkspaceRead:
    row = workspaces_repo.get_workspace(conn, workspace_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceRead.model_validate(row)


@router.post("/workspaces/{workspace_id}/projects", response_model=ProjectRead)
def create_project(
    workspace_id: UUID,
    body: ProjectCreate,
    conn: DbConn,
) -> ProjectRead:
    if workspaces_repo.get_workspace(conn, workspace_id) is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    row = projects_repo.create_project(conn, workspace_id, body.name)
    return ProjectRead.model_validate(row)


@router.get("/workspaces/{workspace_id}/projects", response_model=list[ProjectRead])
def list_projects(workspace_id: UUID, conn: DbConn) -> list[ProjectRead]:
    if workspaces_repo.get_workspace(conn, workspace_id) is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    rows = projects_repo.list_projects(conn, workspace_id)
    return [ProjectRead.model_validate(r) for r in rows]
