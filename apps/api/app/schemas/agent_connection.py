from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentConnectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=512)
    agent_type: str = Field(min_length=1, max_length=256)


class AgentConnectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    agent_type: str
    created_at: datetime
