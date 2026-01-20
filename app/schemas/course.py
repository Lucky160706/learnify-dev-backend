from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class CourseBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    small_description: Optional[str] = None
    cover_image: str
    status: str = Field(default="Draft", pattern="^(Draft|Published)$")
    file_key: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    small_description: Optional[str] = None
    cover_image: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(Draft|Published)$")
    file_key: Optional[str] = None


class CourseResponse(CourseBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class CourseWithChapters(CourseResponse):
    chapters: list["ChapterWithLessons"] = []

    class Config:
        from_attributes = True

from app.schemas.chapter import ChapterWithLessons
CourseWithChapters.model_rebuild()
