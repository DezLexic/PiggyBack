from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.auth import RequireApiKey
from app.db.deps import DbConn
from app.repos import proposals as proposals_repo
from app.schemas import FileRead, ProposalAcceptedResponse, ProposedUpdateRead

router = APIRouter(tags=["proposals"])


@router.post("/proposals/{proposal_id}/accept", response_model=ProposalAcceptedResponse)
def accept_proposal(proposal_id: UUID, conn: DbConn, _auth: RequireApiKey) -> ProposalAcceptedResponse:
    ok, prop, file_row = proposals_repo.accept_proposal(conn, proposal_id)
    if not ok and prop is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if not ok:
        raise HTTPException(
            status_code=409,
            detail=f"Proposal is not pending (status={prop['status']})",
        )
    assert file_row is not None
    return ProposalAcceptedResponse(
        proposal=ProposedUpdateRead.model_validate(prop),
        file=FileRead.model_validate(file_row),
    )


@router.post("/proposals/{proposal_id}/reject", response_model=ProposedUpdateRead)
def reject_proposal(proposal_id: UUID, conn: DbConn, _auth: RequireApiKey) -> ProposedUpdateRead:
    ok, row = proposals_repo.reject_proposal(conn, proposal_id)
    if not ok and row is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if not ok:
        raise HTTPException(
            status_code=409,
            detail=f"Proposal is not pending (status={row['status']})",
        )
    return ProposedUpdateRead.model_validate(row)
