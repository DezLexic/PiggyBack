from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.auth import RequireApiKey
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
def get_file(file_id: UUID, conn: DbConn) -> FileRead:
    row = files_repo.get_file(conn, file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileRead.model_validate(row)


@router.patch("/files/{file_id}", response_model=FileRead)
def update_file(file_id: UUID, body: FileUpdate, conn: DbConn, _auth: RequireApiKey) -> FileRead:
    row = files_repo.update_file_content(conn, file_id, body.content)
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileRead.model_validate(row)


@router.get("/files/{file_id}/versions", response_model=list[FileVersionRead])
def list_file_versions(file_id: UUID, conn: DbConn) -> list[FileVersionRead]:
    if files_repo.get_file(conn, file_id) is None:
        raise HTTPException(status_code=404, detail="File not found")
    rows = files_repo.list_versions(conn, file_id)
    return [FileVersionRead.model_validate(r) for r in rows]


@router.post("/files/{file_id}/proposals", response_model=ProposedUpdateRead)
def create_proposal(
    file_id: UUID,
    body: ProposedUpdateCreate,
    conn: DbConn,
    _auth: RequireApiKey,
) -> ProposedUpdateRead:
    if files_repo.get_file(conn, file_id) is None:
        raise HTTPException(status_code=404, detail="File not found")
    row = proposals_repo.create_proposal(conn, file_id, body.proposed_content)
    return ProposedUpdateRead.model_validate(row)


@router.get("/files/{file_id}/proposals", response_model=list[ProposedUpdateRead])
def list_proposals(file_id: UUID, conn: DbConn) -> list[ProposedUpdateRead]:
    if files_repo.get_file(conn, file_id) is None:
        raise HTTPException(status_code=404, detail="File not found")
    rows = proposals_repo.list_proposals(conn, file_id)
    return [ProposedUpdateRead.model_validate(r) for r in rows]
