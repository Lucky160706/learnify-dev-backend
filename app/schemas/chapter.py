from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class ChapterBase(BaseModel):
    title: str
    slug: str
    position: int
    status: str = Field(default="Draft", pattern="^(Draft|Published)$")


class ChapterCreate(ChapterBase):
    course_id: uuid.UUID


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    position: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(Draft|Published)$")


class ChapterResponse(ChapterBase):
    id: uuid.UUID
    course_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterWithLessons(ChapterResponse):
    lessons: list = []

    class Config:
        from_attributes = True


class ReorderChapters(BaseModel):
    chapter_positions: list[dict[str, int]]  # [{"id": "uuid", "position": 1}, ...]
