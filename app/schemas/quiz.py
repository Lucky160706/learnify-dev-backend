from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# --- OPTIONS ---

class QuizOptionBase(BaseModel):
    content: str
    position: int
    image_url: Optional[str] = None  # Optional image for option

class QuizOptionCreate(QuizOptionBase):
    is_correct: bool

class QuizOption(QuizOptionBase):
    id: UUID
    question_id: UUID
    is_correct: bool

    class Config:
        from_attributes = True

class QuizOptionUser(QuizOptionBase):
    id: UUID
    # No is_correct for users

# --- QUESTIONS ---

class QuizQuestionBase(BaseModel):
    prompt: str
    position: int
    points: int = 1
    image_url: Optional[str] = None  # Optional image for question

class QuizQuestionCreate(QuizQuestionBase):
    options: List[QuizOptionCreate]

class QuizQuestion(QuizQuestionBase):
    id: UUID
    quiz_id: UUID
    options: List[QuizOption]

    class Config:
        from_attributes = True

class QuizQuestionUser(QuizQuestionBase):
    id: UUID
    options: List[QuizOptionUser]

# --- QUIZ ---

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    passing_score_percent: int = 70

class QuizCreate(QuizBase):
    pass

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    passing_score_percent: Optional[int] = None
    status: Optional[str] = None # Draft, Published, Archived
    questions: Optional[List[QuizQuestionCreate]] = None

class Quiz(QuizBase):
    id: UUID
    course_id: UUID
    chapter_id: Optional[UUID] = None  # NULL = course-level quiz, UUID = chapter quiz
    status: str
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    questions: List[QuizQuestion] = []

    class Config:
        from_attributes = True

class QuizUser(QuizBase):
    id: UUID
    course_id: UUID
    chapter_id: Optional[UUID] = None
    questions: List[QuizQuestionUser] = []

    class Config:
        from_attributes = True

# --- ATTEMPTS ---

class QuizAttemptAnswerBase(BaseModel):
    question_id: UUID
    selected_option_id: UUID

class QuizAttemptCreate(BaseModel):
    answers: List[QuizAttemptAnswerBase]

class QuizAttemptAnswer(QuizAttemptAnswerBase):
    id: Optional[UUID] = None
    is_correct: bool
    earned_points: int

    class Config:
        from_attributes = True

class QuizAttempt(BaseModel):
    id: UUID
    quiz_id: UUID
    user_id: str
    score: int
    max_score: int
    percent: int
    passed: bool
    started_at: datetime
    submitted_at: datetime
    answers: List[QuizAttemptAnswer]

    class Config:
        from_attributes = True

class QuizAttemptResult(BaseModel):
    attempt_id: UUID
    score: int
    max_score: int
    percent: int
    passed: bool
    breakdown: List[QuizAttemptAnswer]
