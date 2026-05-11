from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginationParams(BaseModel):
    limit: int = 25
    offset: int = 0


class DateRange(BaseModel):
    start: date | None = None
    end: date | None = None


class TimestampedModel(ORMModel):
    id: str
    created_at: datetime

