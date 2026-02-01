from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from app.supabase_client import get_client

class QuizService:
    @staticmethod
    def supabase_client():
        return get_client()

    @staticmethod
    def get_quizzes_by_course(course_id: str, published_only: bool = True) -> List[dict]:
        query = QuizService.supabase_client().table("quizzes").select("*, questions:quiz_questions(*, options:quiz_options(*))").eq("course_id", str(course_id))
        if published_only:
            query = query.eq("status", "Published")
        
        result = query.execute()
        return result.data

    @staticmethod
    def get_quiz_by_id(quiz_id: str) -> Optional[dict]:
        result = QuizService.supabase_client().table("quizzes").select("*, questions:quiz_questions(*, options:quiz_options(*))").eq("id", str(quiz_id)).limit(1).execute()
        if not result.data:
            return None
        
        quiz = result.data[0]
        # Sort questions and options by position
        if quiz.get("questions"):
            quiz["questions"] = sorted(quiz["questions"], key=lambda x: x.get("position", 0))
            for q in quiz["questions"]:
                if q.get("options"):
                    q["options"] = sorted(q["options"], key=lambda x: x.get("position", 0))
        return quiz

    @staticmethod
    def get_quizzes_admin(course_id: str) -> List[dict]:
        result = QuizService.supabase_client().table("quizzes").select("*, questions:quiz_questions(*, options:quiz_options(*))").eq("course_id", str(course_id)).execute()
        return result.data

    @staticmethod
    def create_quiz_draft(course_id: str, title: str) -> dict:
        # Creates a course-level quiz (chapter_id = NULL)
        new_quiz = {
            "course_id": str(course_id),
            "chapter_id": None,  # Course-level quiz
            "title": title,
            "status": "Draft"
        }
        result = QuizService.supabase_client().table("quizzes").insert(new_quiz).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create quiz draft")
        
        quiz = result.data[0]
        quiz["questions"] = []
        return quiz

    # --- CHAPTER QUIZ METHODS ---

    @staticmethod
    def get_course_level_quiz(course_id: str, published_only: bool = True) -> Optional[dict]:
        """Get the course-level quiz (chapter_id IS NULL)"""
        query = QuizService.supabase_client().table("quizzes").select(
            "*, questions:quiz_questions(*, options:quiz_options(*))"
        ).eq("course_id", str(course_id)).is_("chapter_id", "null")
        
        if published_only:
            query = query.eq("status", "Published")
        
        result = query.limit(1).execute()
        if not result.data:
            return None
        
        quiz = result.data[0]
        # Sort questions and options by position
        if quiz.get("questions"):
            quiz["questions"] = sorted(quiz["questions"], key=lambda x: x.get("position", 0))
            for q in quiz["questions"]:
                if q.get("options"):
                    q["options"] = sorted(q["options"], key=lambda x: x.get("position", 0))
        return quiz

    @staticmethod
    def get_quiz_by_chapter(course_id: str, chapter_id: str, published_only: bool = True) -> Optional[dict]:
        """Get the quiz for a specific chapter"""
        query = QuizService.supabase_client().table("quizzes").select(
            "*, questions:quiz_questions(*, options:quiz_options(*))"
        ).eq("course_id", str(course_id)).eq("chapter_id", str(chapter_id))
        
        if published_only:
            query = query.eq("status", "Published")
        
        result = query.limit(1).execute()
        if not result.data:
            return None
        
        quiz = result.data[0]
        # Sort questions and options by position
        if quiz.get("questions"):
            quiz["questions"] = sorted(quiz["questions"], key=lambda x: x.get("position", 0))
            for q in quiz["questions"]:
                if q.get("options"):
                    q["options"] = sorted(q["options"], key=lambda x: x.get("position", 0))
        return quiz

    @staticmethod
    def create_quiz_draft_for_chapter(course_id: str, chapter_id: str, title: str) -> dict:
        """Create a quiz draft for a specific chapter"""
        # Check if quiz already exists for this chapter
        existing = QuizService.supabase_client().table("quizzes").select("id").eq(
            "course_id", str(course_id)
        ).eq("chapter_id", str(chapter_id)).limit(1).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=409, 
                detail="A quiz already exists for this chapter"
            )
        
        new_quiz = {
            "course_id": str(course_id),
            "chapter_id": str(chapter_id),
            "title": title,
            "status": "Draft"
        }
        result = QuizService.supabase_client().table("quizzes").insert(new_quiz).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create chapter quiz draft")
        
        quiz = result.data[0]
        quiz["questions"] = []
        return quiz

    @staticmethod
    def get_quizzes_admin_by_chapter(course_id: str, chapter_id: str) -> List[dict]:
        """Admin: Get all quizzes for a specific chapter (any status)"""
        result = QuizService.supabase_client().table("quizzes").select(
            "*, questions:quiz_questions(*, options:quiz_options(*))"
        ).eq("course_id", str(course_id)).eq("chapter_id", str(chapter_id)).execute()
        return result.data


    @staticmethod
    def update_quiz(quiz_id: str, updates: any) -> dict:
        # meta updates
        meta = {}
        if updates.title is not None: meta["title"] = updates.title
        if updates.description is not None: meta["description"] = updates.description
        if updates.passing_score_percent is not None: meta["passing_score_percent"] = updates.passing_score_percent
        if updates.status is not None: meta["status"] = updates.status
        
        client = QuizService.supabase_client()
        
        if meta:
            meta["updated_at"] = datetime.utcnow().isoformat()
            client.table("quizzes").update(meta).eq("id", str(quiz_id)).execute()

        if updates.questions is not None:
            # Delete existing questions (cascade will handle options)
            client.table("quiz_questions").delete().eq("quiz_id", str(quiz_id)).execute()
            
            for q_idx, q_data in enumerate(updates.questions):
                new_q_payload = {
                    "quiz_id": str(quiz_id),
                    "prompt": q_data.prompt,
                    "position": q_data.position,
                    "points": q_data.points,
                    "image_url": q_data.image_url  # Include image URL
                }
                q_result = client.table("quiz_questions").insert(new_q_payload).execute()
                if not q_result.data: continue
                
                q_id = q_result.data[0]["id"]
                
                options_payload = []
                for o_data in q_data.options:
                    options_payload.append({
                        "question_id": q_id,
                        "content": o_data.content,
                        "position": o_data.position,
                        "is_correct": o_data.is_correct,
                        "image_url": o_data.image_url  # Include image URL
                    })
                
                if options_payload:
                    client.table("quiz_options").insert(options_payload).execute()


        return QuizService.get_quiz_by_id(quiz_id)

    @staticmethod
    def submit_attempt(quiz_id: str, user_id: str, attempt_data: any) -> dict:
        quiz = QuizService.get_quiz_by_id(quiz_id)
        if not quiz or quiz["status"] != "Published":
            raise HTTPException(status_code=404, detail="Published quiz not found")

        # Prep for grading
        questions_map = {q["id"]: q for q in quiz["questions"]}
        total_points = sum(q.get("points", 1) for q in quiz["questions"])
        earned_score = 0
        
        client = QuizService.supabase_client()
        
        # Create attempt record
        attempt_payload = {
            "quiz_id": str(quiz_id),
            "user_id": user_id,
            "score": 0,
            "max_score": total_points,
            "percent": 0,
            "passed": False,
            "started_at": datetime.utcnow().isoformat(),
            "submitted_at": datetime.utcnow().isoformat()
        }
        att_result = client.table("quiz_attempts").insert(attempt_payload).execute()
        if not att_result.data:
            raise HTTPException(status_code=500, detail="Failed to create attempt")
        
        attempt_id = att_result.data[0]["id"]
        answers_payload = []
        graded_answers = []

        for ans in attempt_data.answers:
            q_id = str(ans.question_id)
            if q_id not in questions_map: continue
            
            q = questions_map[q_id]
            correct_opt = next((o for o in q["options"] if o["is_correct"]), None)
            
            is_correct = str(ans.selected_option_id) == str(correct_opt["id"]) if correct_opt else False
            points = q.get("points", 1) if is_correct else 0
            earned_score += points
            
            ans_record = {
                "attempt_id": attempt_id,
                "question_id": q_id,
                "selected_option_id": str(ans.selected_option_id),
                "is_correct": is_correct,
                "earned_points": points
            }
            answers_payload.append(ans_record)
            graded_answers.append(ans_record)

        if answers_payload:
            client.table("quiz_attempt_answers").insert(answers_payload).execute()

        # Update attempt score
        percent = int((earned_score / total_points * 100)) if total_points > 0 else 0
        final_update = {
            "score": earned_score,
            "percent": percent,
            "passed": percent >= quiz.get("passing_score_percent", 70)
        }
        client.table("quiz_attempts").update(final_update).eq("id", attempt_id).execute()
        
        # Return summary
        return {
            "id": attempt_id,
            "score": earned_score,
            "max_score": total_points,
            "percent": percent,
            "passed": final_update["passed"],
            "answers": graded_answers
        }

    @staticmethod
    def get_user_attempts(quiz_id: str, user_id: str) -> List[dict]:
        result = QuizService.supabase_client().table("quiz_attempts").select("*, answers:quiz_attempt_answers(*)").eq("quiz_id", str(quiz_id)).eq("user_id", user_id).order("submitted_at", desc=True).execute()
        return result.data

    @staticmethod
    def get_user_all_attempts(user_id: str) -> List[dict]:
        """Get all quiz attempts for a user with quiz titles"""
        result = QuizService.supabase_client().table("quiz_attempts").select("*, quiz:quizzes(title)").eq("user_id", user_id).order("submitted_at", desc=True).execute()
        return result.data

    @staticmethod
    def get_quiz_analytics(quiz_id: str) -> List[dict]:
        """Get all attempts for a quiz (Removed join with user table due to missing table)"""
        client = QuizService.supabase_client()
        
        # Fetch all attempts for the specific quiz
        attempts_result = client.table("quiz_attempts").select("*").eq("quiz_id", str(quiz_id)).order("submitted_at", desc=True).execute()
        attempts = attempts_result.data
        if not attempts:
            return []

        # Return attempts directly as user table is not available for joining
        return attempts

    @staticmethod
    def delete_quiz(quiz_id: str) -> bool:
        """Delete a quiz and all associated data"""
        client = QuizService.supabase_client()
        # Cascade delete should handle questions, options, attempts if set up in DB
        # But to be safe/clear, we delete the quiz (parent)
        result = client.table("quizzes").delete().eq("id", str(quiz_id)).execute()
        return bool(result.data)
