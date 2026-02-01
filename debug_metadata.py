
from app.database import Base
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.lesson import Lesson
from app.models.quiz import Quiz, QuizQuestion, QuizOption, QuizAttempt
from app.models.user import User

print("--- REGISTERED TABLES IN METADATA ---")
print(Base.metadata.tables.keys())
