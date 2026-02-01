from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List
import uuid
from app.services.quiz_service import QuizService
from app.schemas.quiz import (
    Quiz, QuizUpdate, QuizAttemptCreate, QuizAttemptResult, 
    QuizUser, QuizAttempt
)
from app.supabase_client import get_client


router = APIRouter(prefix="/api", tags=["quiz"])

# --- USER ENDPOINTS ---

@router.get("/courses/{course_id}/quizzes", response_model=List[QuizUser])
def get_course_quizzes(course_id: str):
    """Get all published quizzes for a course"""
    return QuizService.get_quizzes_by_course(course_id)

@router.get("/courses/{course_id}/quiz", response_model=QuizUser)
def get_course_quiz(course_id: str):
    """Get the course-level published quiz (chapter_id IS NULL)"""
    quiz = QuizService.get_course_level_quiz(course_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="No published course-level quiz found")
    return quiz

# --- CHAPTER QUIZ ENDPOINTS ---

@router.get("/courses/{course_id}/chapters/{chapter_id}/quiz", response_model=QuizUser)
def get_chapter_quiz(course_id: str, chapter_id: str):
    """Get the published quiz for a specific chapter"""
    quiz = QuizService.get_quiz_by_chapter(course_id, chapter_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="No published quiz found for this chapter")
    return quiz

@router.get("/quizzes/{quiz_id}", response_model=QuizUser)
def get_quiz(quiz_id: str):
    """Get a specific published quiz"""
    quiz = QuizService.get_quiz_by_id(quiz_id)
    if not quiz or quiz["status"] != "Published":
        raise HTTPException(status_code=404, detail="Quiz not found or not published")
    return quiz

@router.post("/quizzes/{quiz_id}/attempts", response_model=QuizAttemptResult)
def submit_quiz_attempt(
    quiz_id: str, 
    attempt: QuizAttemptCreate, 
    user_id: str
):
    """Submit a quiz attempt and get results"""
    quiz = QuizService.get_quiz_by_id(quiz_id)
    if not quiz or quiz["status"] != "Published":
        raise HTTPException(status_code=404, detail="Published quiz not found")
    
    result = QuizService.submit_attempt(quiz_id, user_id, attempt)
    return {
        "attempt_id": result["id"],
        "score": result["score"],
        "max_score": result["max_score"],
        "percent": result["percent"],
        "passed": result["passed"],
        "breakdown": result["answers"]
    }

@router.get("/quizzes/{quiz_id}/attempts/me", response_model=List[QuizAttempt])
def get_my_attempts(
    quiz_id: str,
    user_id: str
):
    """Get my previous attempts for a specific quiz"""
    return QuizService.get_user_attempts(quiz_id, user_id)

@router.get("/users/{user_id}/attempts", response_model=List[dict])
def get_user_history(user_id: str):
    """Get all quiz attempts for a user"""
    return QuizService.get_user_all_attempts(user_id)


# --- ADMIN ENDPOINTS ---

@router.get("/admin/courses/{course_id}/quizzes", response_model=List[Quiz])
def admin_get_course_quizzes(course_id: str):
    """Get all quizzes for course for admin"""
    return QuizService.get_quizzes_admin(course_id)

@router.get("/admin/courses/{course_id}/chapters/{chapter_id}/quizzes", response_model=List[Quiz])
def admin_get_chapter_quizzes(course_id: str, chapter_id: str):
    """Get all quizzes for a specific chapter (admin)"""
    return QuizService.get_quizzes_admin_by_chapter(course_id, chapter_id)

@router.get("/admin/quizzes/{quiz_id}", response_model=Quiz)
def admin_get_quiz(quiz_id: str):
    """Get a specific quiz for admin"""
    quiz = QuizService.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/admin/courses/{course_id}/quiz", response_model=Quiz)
def admin_create_quiz_draft(course_id: str, title: str = "Untitled Quiz"):
    """Create a new course-level quiz draft"""
    return QuizService.create_quiz_draft(course_id, title)

@router.post("/admin/courses/{course_id}/chapters/{chapter_id}/quiz", response_model=Quiz)
def admin_create_chapter_quiz_draft(course_id: str, chapter_id: str, title: str = "Chapter Quiz"):
    """Create a new chapter-level quiz draft"""
    return QuizService.create_quiz_draft_for_chapter(course_id, chapter_id, title)


@router.put("/admin/quizzes/{quiz_id}", response_model=Quiz)
def admin_update_quiz(quiz_id: str, updates: QuizUpdate):
    """Update quiz content (meta + questions + options)"""
    return QuizService.update_quiz(quiz_id, updates)

@router.post("/admin/quizzes/{quiz_id}/publish", response_model=Quiz)
def admin_publish_quiz(quiz_id: str):
    """Publish the quiz"""
    updates = QuizUpdate(status="Published")
    return QuizService.update_quiz(quiz_id, updates)

@router.post("/admin/quizzes/{quiz_id}/archive", response_model=Quiz)
def admin_archive_quiz(quiz_id: str):
    """Archive the quiz"""
    updates = QuizUpdate(status="Archived")
    return QuizService.update_quiz(quiz_id, updates)

@router.get("/admin/quizzes/{quiz_id}/analytics", response_model=List[dict])
def admin_get_quiz_analytics(quiz_id: str):
    """Get attempt analytics for admin"""
    return QuizService.get_quiz_analytics(quiz_id)

@router.delete("/admin/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_quiz(quiz_id: str):
    """Delete a quiz"""
    success = QuizService.delete_quiz(quiz_id)
    if not success:
        raise HTTPException(status_code=404, detail="Quiz not found or failed to delete")
    return

# --- IMAGE UPLOAD ---

ALLOWED_CONTENT_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/admin/quizzes/{quiz_id}/upload")
async def admin_upload_quiz_image(
    quiz_id: str,
    file: UploadFile = File(...)
):
    """
    Upload an image for a quiz question or option.
    Returns the public URL to be used when saving the quiz.
    """
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    unique_filename = f"quiz-media/{quiz_id}/{uuid.uuid4()}.{ext}"
    
    try:
        client = get_client()
        # Upload to Supabase Storage
        result = client.storage.from_("quiz-media").upload(
            path=unique_filename,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        public_url = client.storage.from_("quiz-media").get_public_url(unique_filename)
        
        return {
            "url": public_url,
            "path": unique_filename,
            "content_type": file.content_type,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

