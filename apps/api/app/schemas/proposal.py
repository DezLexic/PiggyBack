from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProposedUpdateCreate(BaseModel):
    proposed_content: str


class ProposedUpdateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_id: UUID
    proposed_content: str
    status: str
    created_at: datetime
