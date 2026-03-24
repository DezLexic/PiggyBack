from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.auth import Caller, assert_project_permission
from app.db.deps import DbConn
from app.repos import files as files_repo
from app.repos import projects as projects_repo
from app.schemas import (
    BatchWriteRequest,
    BatchWriteResponse,
    FileWriteRequest,
    FileWriteResponse,
    SummaryWriteRequest,
)
from app.schemas.write import FileWriteFileInfo, FileWriteVersionInfo

router = APIRouter(tags=["write"])

SUMMARY_TYPE_TO_PATH = {
    "status": "status.md",
    "handoff": "handoff.md",
    "project": "project.md",
}


def _build_response(file_row: dict, version_id: UUID, version_created_at) -> FileWriteResponse:
    return FileWriteResponse(
        file=FileWriteFileInfo(
            id=file_row["id"],
            path=file_row["path"],
            current_version_id=file_row["current_version_id"],
        ),
        version=FileWriteVersionInfo(
            id=version_id,
            created_at=version_created_at,
        ),
    )


@router.post("/projects/{project_id}/files/write", response_model=FileWriteResponse)
def write_file(
    project_id: UUID, body: FileWriteRequest, conn: DbConn, caller: Caller
) -> FileWriteResponse:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    assert_project_permission(conn, caller, project_id, ("write",))
    file_row, version_id, version_created_at = files_repo.upsert_file(
        conn, project_id, body.path, body.content, append=(body.mode == "append")
    )
    return _build_response(file_row, version_id, version_created_at)


@router.post("/projects/{project_id}/files/append", response_model=FileWriteResponse)
def append_file(
    project_id: UUID, body: FileWriteRequest, conn: DbConn, caller: Caller
) -> FileWriteResponse:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    assert_project_permission(conn, caller, project_id, ("write",))
    file_row, version_id, version_created_at = files_repo.upsert_file(
        conn, project_id, body.path, body.content, append=True
    )
    return _build_response(file_row, version_id, version_created_at)


@router.post("/projects/{project_id}/summary", response_model=FileWriteResponse)
def write_summary(
    project_id: UUID, body: SummaryWriteRequest, conn: DbConn, caller: Caller
) -> FileWriteResponse:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    assert_project_permission(conn, caller, project_id, ("write",))
    path = SUMMARY_TYPE_TO_PATH[body.type]
    file_row, version_id, version_created_at = files_repo.upsert_file(
        conn, project_id, path, body.content, append=False
    )
    return _build_response(file_row, version_id, version_created_at)


@router.post("/projects/{project_id}/batch-write", response_model=BatchWriteResponse)
def batch_write(
    project_id: UUID, body: BatchWriteRequest, conn: DbConn, caller: Caller
) -> BatchWriteResponse:
    if projects_repo.get_project(conn, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    assert_project_permission(conn, caller, project_id, ("write",))
    results = []
    for item in body.writes:
        file_row, version_id, version_created_at = files_repo.upsert_file(
            conn, project_id, item.path, item.content, append=(item.mode == "append")
        )
        results.append(_build_response(file_row, version_id, version_created_at))
    return BatchWriteResponse(results=results)
