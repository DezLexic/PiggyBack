from __future__ import annotations

from fastapi import APIRouter

from app.db.deps import DbConn
from app.repos import agent_connections as agents_repo
from app.schemas import AgentConnectionCreate, AgentConnectionRead

router = APIRouter(tags=["agent_connections"])


@router.post("/agent-connections", response_model=AgentConnectionRead)
def create_agent_connection(body: AgentConnectionCreate, conn: DbConn) -> AgentConnectionRead:
    row = agents_repo.create_agent_connection(conn, body.name, body.agent_type)
    return AgentConnectionRead.model_validate(row)


@router.get("/agent-connections", response_model=list[AgentConnectionRead])
def list_agent_connections(conn: DbConn) -> list[AgentConnectionRead]:
    rows = agents_repo.list_agent_connections(conn)
    return [AgentConnectionRead.model_validate(r) for r in rows]
