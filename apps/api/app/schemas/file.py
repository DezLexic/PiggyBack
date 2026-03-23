from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FileCreate(BaseModel):
    path: str = Field(min_length=1, max_length=2048)
    content: str


class FileUpdate(BaseModel):
    content: str


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    path: str
    current_version_id: UUID | None
    content: str
    created_at: datetime
    updated_at: datetime


class FileVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_id: UUID
    content: str
    created_at: datetime
