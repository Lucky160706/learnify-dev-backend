from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True, index=True)
    description = Column(Text)
    small_description = Column(Text)
    cover_image = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="Draft")
    file_key = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    chapters = relationship(
        "Chapter", back_populates="course", cascade="all, delete-orphan"
    )
    quiz = relationship("Quiz", back_populates="course", uselist=False, cascade="all, delete-orphan")