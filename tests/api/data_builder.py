
import uuid
from sqlalchemy.orm import Session
from app.models.course import Course
from app.models.quiz import Quiz, QuizQuestion, QuizOption, QuizAttempt
from app.models.user import User

class DataBuilder:
    def __init__(self, db: Session):
        self.db = db

    def seed_user(self, id=None, email=None, name="Test User"):
        if not id: id = str(uuid.uuid4())
        if not email: email = f"{id}@example.com"
        user = User(id=id, email=email, name=name)
        self.db.add(user)
        self.db.commit()
        return user

    def seed_course(self, title="Test Course", slug=None):
        suffix = uuid.uuid4().hex[:8]
        if not slug: slug = f"test-course-{suffix}"
        course = Course(
            id=uuid.uuid4(),
            title=f"{title} {suffix}",
            slug=slug,
            cover_image="https://example.com/image.jpg",
            description="Test Description",
            small_description="Small test",
            status="Published",
            file_key="test-key"
        )
        self.db.add(course)
        self.db.commit()
        return course

    def seed_quiz(self, course_id, title="Test Quiz", status="Published"):
        quiz = Quiz(
            id=uuid.uuid4(),
            course_id=course_id,
            title=title,
            status=status,
            passing_score_percent=70
        )
        self.db.add(quiz)
        self.db.commit()
        return quiz

    def seed_question(self, quiz_id, prompt="What is 1+1?", position=0, points=1):
        q = QuizQuestion(
            id=uuid.uuid4(),
            quiz_id=quiz_id,
            prompt=prompt,
            position=position,
            points=points
        )
        self.db.add(q)
        self.db.commit()
        return q

    def seed_option(self, question_id, content, is_correct=False, position=None):
        if position is None:
            from sqlalchemy import func
            current_max = self.db.query(func.max(QuizOption.position)).filter(QuizOption.question_id == question_id).scalar()
            position = (current_max + 1) if current_max is not None else 0
            
        o = QuizOption(
            id=uuid.uuid4(),
            question_id=question_id,
            content=content,
            is_correct=is_correct,
            position=position
        )
        self.db.add(o)
        self.db.commit()
        return o
