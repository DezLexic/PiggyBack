from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

PermissionTypeLiteral = Literal["read", "propose_update"]


class PermissionGrant(BaseModel):
    agent_connection_id: UUID
    permission_type: PermissionTypeLiteral = Field(
        ...,
        description="read or propose_update",
    )


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    agent_connection_id: UUID
    permission_type: str
    created_at: datetime
