from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.auth import READ_PERMISSION_TYPES, Caller, assert_project_permission
from app.db.deps import DbConn
from app.repos import files as files_repo
from app.repos import proposals as proposals_repo
from app.schemas import (
    FileRead,
    FileUpdate,
    FileVersionRead,
    ProposedUpdateCreate,
    ProposedUpdateRead,
)

router = APIRouter(tags=["files"])


@router.get("/files/{file_id}", response_model=FileRead)
def get_file(file_id: UUID, conn: DbConn, caller: Caller) -> FileRead:
    row = files_repo.get_file(conn, file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    assert_project_permission(conn, caller, row["project_id"], READ_PERMISSION_TYPES)
    return FileRead.model_validate(row)


@router.patch("/files/{file_id}", response_model=FileRead)
def update_file(file_id: UUID, body: FileUpdate, conn: DbConn, caller: Caller) -> FileRead:
    row = files_repo.get_file(conn, file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    assert_project_permission(conn, caller, row["project_id"], ("write",))
    updated = files_repo.update_file_content(conn, file_id, body.content)
    assert updated is not None
    return FileRead.model_validate(updated)


@router.get("/files/{file_id}/versions", response_model=list[FileVersionRead])
def list_file_versions(file_id: UUID, conn: DbConn, caller: Caller) -> list[FileVersionRead]:
    row = files_repo.get_file(conn, file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    assert_project_permission(conn, caller, row["project_id"], READ_PERMISSION_TYPES)
    rows = files_repo.list_versions(conn, file_id)
    return [FileVersionRead.model_validate(r) for r in rows]


@router.post("/files/{file_id}/proposals", response_model=ProposedUpdateRead)
def create_proposal(
    file_id: UUID,
    body: ProposedUpdateCreate,
    conn: DbConn,
    caller: Caller,
) -> ProposedUpdateRead:
    row = files_repo.get_file(conn, file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    assert_project_permission(conn, caller, row["project_id"], ("propose_update", "write"))
    proposal = proposals_repo.create_proposal(conn, file_id, body.proposed_content)
    return ProposedUpdateRead.model_validate(proposal)


@router.get("/files/{file_id}/proposals", response_model=list[ProposedUpdateRead])
def list_proposals(file_id: UUID, conn: DbConn, caller: Caller) -> list[ProposedUpdateRead]:
    row = files_repo.get_file(conn, file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    assert_project_permission(conn, caller, row["project_id"], READ_PERMISSION_TYPES)
    rows = proposals_repo.list_proposals(conn, file_id)
    return [ProposedUpdateRead.model_validate(r) for r in rows]
