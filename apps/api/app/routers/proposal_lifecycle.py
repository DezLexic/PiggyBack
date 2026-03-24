from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.auth import Caller, assert_project_permission
from app.db.deps import DbConn
from app.repos import files as files_repo
from app.repos import proposals as proposals_repo
from app.schemas import FileRead, ProposalAcceptedResponse, ProposedUpdateRead

router = APIRouter(tags=["proposals"])


@router.post("/proposals/{proposal_id}/accept", response_model=ProposalAcceptedResponse)
def accept_proposal(proposal_id: UUID, conn: DbConn, caller: Caller) -> ProposalAcceptedResponse:
    # Peek at the proposal to get file → project for permission check
    prop_row = proposals_repo.get_by_id(conn, proposal_id)
    if prop_row is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    file_row = files_repo.get_file(conn, prop_row["file_id"])
    assert file_row is not None
    assert_project_permission(conn, caller, file_row["project_id"], ())  # admin-only

    ok, prop, updated_file = proposals_repo.accept_proposal(conn, proposal_id)
    if not ok:
        raise HTTPException(
            status_code=409,
            detail=f"Proposal is not pending (status={prop['status']})",
        )
    assert updated_file is not None
    return ProposalAcceptedResponse(
        proposal=ProposedUpdateRead.model_validate(prop),
        file=FileRead.model_validate(updated_file),
    )


@router.post("/proposals/{proposal_id}/reject", response_model=ProposedUpdateRead)
def reject_proposal(proposal_id: UUID, conn: DbConn, caller: Caller) -> ProposedUpdateRead:
    prop_row = proposals_repo.get_by_id(conn, proposal_id)
    if prop_row is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    file_row = files_repo.get_file(conn, prop_row["file_id"])
    assert file_row is not None
    assert_project_permission(conn, caller, file_row["project_id"], ())  # admin-only

    ok, row = proposals_repo.reject_proposal(conn, proposal_id)
    if not ok:
        raise HTTPException(
            status_code=409,
            detail=f"Proposal is not pending (status={row['status']})",
        )
    return ProposedUpdateRead.model_validate(row)
