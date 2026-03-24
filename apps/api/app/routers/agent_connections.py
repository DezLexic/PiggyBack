from __future__ import annotations

from fastapi import APIRouter

from app.db.deps import DbConn
from app.repos import agent_connections as agents_repo
from app.repos import api_keys as api_keys_repo
from app.schemas import AgentConnectionCreate, AgentConnectionCreated, AgentConnectionRead

router = APIRouter(tags=["agent_connections"])


@router.post("/agent-connections", response_model=AgentConnectionCreated)
def create_agent_connection(body: AgentConnectionCreate, conn: DbConn) -> AgentConnectionCreated:
    agent = agents_repo.create_agent_connection(conn, body.name, body.agent_type)
    plaintext_key, _ = api_keys_repo.create_api_key(conn, body.name, agent["id"])
    return AgentConnectionCreated(**agent, api_key=plaintext_key)


@router.get("/agent-connections", response_model=list[AgentConnectionRead])
def list_agent_connections(conn: DbConn) -> list[AgentConnectionRead]:
    rows = agents_repo.list_agent_connections(conn)
    return [AgentConnectionRead.model_validate(r) for r in rows]
