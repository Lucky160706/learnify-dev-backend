from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    func,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="Draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    course = relationship("Course", back_populates="chapters")
    lessons = relationship(
        "Lesson", back_populates="chapter", cascade="all, delete-orphan"
    )
    quiz = relationship("Quiz", back_populates="chapter", uselist=False)


    # Unique constraint
    __table_args__ = (
        UniqueConstraint("course_id", "slug", name="unique_chapter_slug_per_course"),
    )
