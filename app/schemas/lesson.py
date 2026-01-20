from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
import uuid


class LessonBase(BaseModel):
    title: str
    slug: str
    label: Optional[str] = None
    type: str = Field(pattern="^(Theory|Video|Assignment|Quiz)$")
    author_name: Optional[str] = None
    published_at: Optional[date] = None
    position: int
    status: str = Field(default="Draft", pattern="^(Draft|Published)$")
    fileKey: Optional[str] = None


class LessonCreate(LessonBase):
    chapter_id: uuid.UUID


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    label: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(Theory|Video|Assignment|Quiz)$")
    author_name: Optional[str] = None
    published_at: Optional[date] = None
    position: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(Draft|Published)$")
    fileKey: Optional[str] = None


class LessonResponse(LessonBase):
    id: uuid.UUID
    chapter_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReorderLessons(BaseModel):
    lesson_positions: list[dict]  # [{"id": "uuid", "position": 1}, ...]
