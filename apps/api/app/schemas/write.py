from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreatedBy(BaseModel):
    type: str
    name: str


class FileWriteRequest(BaseModel):
    path: str = Field(min_length=1, max_length=2048)
    content: str
    mode: Literal["replace", "append"] = "replace"
    created_by: CreatedBy | None = None


class FileWriteVersionInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime


class FileWriteFileInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    path: str
    current_version_id: UUID | None


class FileWriteResponse(BaseModel):
    file: FileWriteFileInfo
    version: FileWriteVersionInfo


class SummaryWriteRequest(BaseModel):
    type: Literal["status", "handoff", "project"]
    content: str
    created_by: CreatedBy | None = None


class BatchWriteItem(BaseModel):
    path: str = Field(min_length=1, max_length=2048)
    content: str
    mode: Literal["replace", "append"] = "replace"


class BatchWriteRequest(BaseModel):
    writes: list[BatchWriteItem] = Field(min_length=1)
    created_by: CreatedBy | None = None


class BatchWriteResponse(BaseModel):
    results: list[FileWriteResponse]
