from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException
from psycopg.errors import UniqueViolation

from app.auth import READ_PERMISSION_TYPES, Caller, assert_project_permission
from app.db.deps import DbConn
from app.repos import files as files_repo
from app.repos import projects as projects_repo
from app.schemas import FileCreate, FileRead, ProjectRead

router = APIRouter(tags=["projects"])


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, conn: DbConn, caller: Caller) -> ProjectRead:
    row = projects_repo.get_project(conn, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    assert_project_permission(conn, caller, project_id, READ_PERMISSION_TYPES)
    return ProjectRead.model_validate(row)


@router.post("/projects/{project_id}/files", response_model=FileRead)
def create_file(project_id: UUID, body: FileCreate, conn: DbConn, caller: Caller) -> FileRead:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    assert_project_permission(conn, caller, project_id, ("write",))
    try:
        row = files_repo.create_file(conn, project_id, body.path, body.content)
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="A file with this path already exists in the project",
        ) from None
    return FileRead.model_validate(row)


@router.get("/projects/{project_id}/files", response_model=list[FileRead])
def list_files(project_id: UUID, conn: DbConn, caller: Caller) -> list[FileRead]:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    assert_project_permission(conn, caller, project_id, READ_PERMISSION_TYPES)
    rows = files_repo.list_files(conn, project_id)
    return [FileRead.model_validate(r) for r in rows]
