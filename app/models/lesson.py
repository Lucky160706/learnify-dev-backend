from sqlalchemy import Column, String, Text, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True, index=True)
    label = Column(Text)
    type = Column(String(20), nullable=False)
    author_name = Column(Text)
    published_at = Column(Date)
    position = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="Draft")
    mdx_path = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    chapter = relationship("Chapter", back_populates="lessons")
