from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("courses.id", ondelete="CASCADE"), 
        nullable=False
    )
    chapter_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("chapters.id", ondelete="CASCADE"), 
        nullable=True  # NULL = course-level quiz, NOT NULL = chapter quiz
    )
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default="Draft") # Draft, Published, Archived
    passing_score_percent = Column(Integer, nullable=False, default=70)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    course = relationship("Course", back_populates="quiz")
    chapter = relationship("Chapter", back_populates="quiz")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.position")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("quizzes.id", ondelete="CASCADE"), 
        nullable=False
    )
    position = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    points = Column(Integer, nullable=False, default=1)
    image_url = Column(Text, nullable=True)  # Optional image for question
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuizOption", back_populates="question", cascade="all, delete-orphan", order_by="QuizOption.position")

class QuizOption(Base):
    __tablename__ = "quiz_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("quiz_questions.id", ondelete="CASCADE"), 
        nullable=False
    )
    position = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    image_url = Column(Text, nullable=True)  # Optional image for option

    # Relationships
    question = relationship("QuizQuestion", back_populates="options")

    # Partial unique index for correct option per question
    # SQLAlchemy doesn't support partial unique indexes directly in __table_args__ reliably across all backends, 
    # but for Postgres we can use Index with postgresql_where
    __table_args__ = (
        UniqueConstraint("question_id", "position", name="unique_option_position_per_question"),
    )

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("quizzes.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id = Column(Text, ForeignKey("user.id", ondelete="CASCADE"), nullable=False) # FK to 'user' table which has text ID in Drizzle schema

    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    percent = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("QuizAttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")

class QuizAttemptAnswer(Base):
    __tablename__ = "quiz_attempt_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("quiz_attempts.id", ondelete="CASCADE"), 
        nullable=False
    )
    question_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("quiz_questions.id", ondelete="CASCADE"), 
        nullable=False
    )
    selected_option_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("quiz_options.id", ondelete="CASCADE"), 
        nullable=False
    )
    is_correct = Column(Boolean, nullable=False)
    earned_points = Column(Integer, nullable=False)

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
