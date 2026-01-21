# Re-export all schemas for convenient imports
from app.schemas.course import (
    CourseBase,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseWithChapters,
)
from app.schemas.chapter import (
    ChapterBase,
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    ChapterWithLessons,
    ReorderChapters,
)
from app.schemas.lesson import (
    LessonBase,
    LessonCreate,
    LessonUpdate,
    LessonResponse,
    ReorderLessons,
)

__all__ = [
    # Course schemas
    "CourseBase",
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseWithChapters",
    # Chapter schemas
    "ChapterBase",
    "ChapterCreate",
    "ChapterUpdate",
    "ChapterResponse",
    "ChapterWithLessons",
    "ReorderChapters",
    # Lesson schemas
    "LessonBase",
    "LessonCreate",
    "LessonUpdate",
    "LessonResponse",
    "ReorderLessons",
]
