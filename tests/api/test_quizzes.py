
import pytest
from tests.api.data_builder import DataBuilder

def test_user_get_published_quiz_no_leakage(client, db_session):
    builder = DataBuilder(db_session)
    user = builder.seed_user()
    course = builder.seed_course()
    quiz = builder.seed_quiz(course.id)
    q = builder.seed_question(quiz.id)
    builder.seed_option(q.id, "Correct", is_correct=True)
    builder.seed_option(q.id, "Wrong", is_correct=False)
    
    response = client.get(f"/api/courses/{course.id}/quiz")
    assert response.status_code == 200
    data = response.json()
    
    assert data["title"] == quiz.title
    # Security Check: deep scan for leakage
    questions = data["questions"]
    for q_data in questions:
        for opt in q_data["options"]:
            assert "is_correct" not in opt
            assert "isCorrect" not in opt

def test_user_get_draft_quiz_returns_404(client, db_session):
    builder = DataBuilder(db_session)
    course = builder.seed_course()
    builder.seed_quiz(course.id, status="Draft")
    
    response = client.get(f"/api/courses/{course.id}/quiz")
    assert response.status_code == 404

def test_submit_perfect_attempt(client, db_session):
    builder = DataBuilder(db_session)
    user = builder.seed_user(id="perfect-user")
    course = builder.seed_course()
    quiz = builder.seed_quiz(course.id)
    q = builder.seed_question(quiz.id, points=10)
    opt_correct = builder.seed_option(q.id, "Correct", is_correct=True)
    builder.seed_option(q.id, "Wrong", is_correct=False)
    
    payload = {
        "answers": [
            {"question_id": str(q.id), "selected_option_id": str(opt_correct.id)}
        ]
    }
    
    response = client.post(f"/api/courses/{course.id}/quiz/attempts?user_id={user.id}", json=payload)
    assert response.status_code == 200
    result = response.json()
    
    assert result["score"] == 10
    assert result["percent"] == 100
    assert result["passed"] is True

def test_submit_failing_attempt(client, db_session):
    builder = DataBuilder(db_session)
    user = builder.seed_user(id="failing-user")
    course = builder.seed_course()
    quiz = builder.seed_quiz(course.id)
    q = builder.seed_question(quiz.id, points=10)
    builder.seed_option(q.id, "Correct", is_correct=True)
    opt_wrong = builder.seed_option(q.id, "Wrong", is_correct=False)
    
    payload = {
        "answers": [
            {"question_id": str(q.id), "selected_option_id": str(opt_wrong.id)}
        ]
    }
    
    response = client.post(f"/api/courses/{course.id}/quiz/attempts?user_id={user.id}", json=payload)
    assert response.status_code == 200
    result = response.json()
    
    assert result["score"] == 0
    assert result["percent"] == 0
    assert result["passed"] is False

def test_admin_get_quiz_includes_correct_answers(client, db_session):
    builder = DataBuilder(db_session)
    course = builder.seed_course()
    quiz = builder.seed_quiz(course.id)
    q = builder.seed_question(quiz.id)
    builder.seed_option(q.id, "Correct", is_correct=True)
    
    response = client.get(f"/api/admin/courses/{course.id}/quiz")
    assert response.status_code == 200
    data = response.json()
    
    assert data["questions"][0]["options"][0]["is_correct"] is True
