from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from app.supabase_client import get_client
from app.schemas import CourseCreate, CourseUpdate, CourseResponse, CourseWithChapters

router = APIRouter(prefix="/api/courses", tags=["courses"])

# Helper to get supabase client
def supabase_client():
    return get_client()


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate):
    """Create a new course"""
    # Check if slug already exists
    existing = (
        supabase_client.table("courses")
        .select("id")
        .eq("slug", course.slug)
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with slug '{course.slug}' already exists",
        )

    # Insert
    data = course.model_dump()
    result = supabase_client.table("courses").insert(data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create course")
        
    return result.data[0]


@router.get("/", response_model=List[CourseWithChapters])
def list_courses(skip: int = 0, limit: int = 100, status: str = None):
    """List all courses with chapters and lessons"""
    query = supabase_client.table("courses").select("*, chapters(*, lessons(*))")

    if status:
        query = query.eq("status", status)

    result = query.range(skip, skip + limit - 1).execute()
    
    courses = result.data
    
    # Sort data locally since Supabase nested sorting is limited
    for course in courses:
        if course.get("chapters"):
            # Sort chapters
            course["chapters"].sort(key=lambda x: x.get("position", 0))
            for chapter in course["chapters"]:
                if chapter.get("lessons"):
                    # Sort lessons
                    chapter["lessons"].sort(key=lambda x: x.get("position", 0))
                    
    return courses


@router.get("/{course_id}", response_model=CourseWithChapters)
def get_course(course_id: uuid.UUID):
    """Get course by ID with chapters"""
    # Supabase select with nested resources
    # We want chapters and lessons. Note: Sorting within nested resources can be tricky in one query
    # Simple nested select: *, chapters(*, lessons(*))
    
    result = (
        supabase_client.table("courses")
        .select("*, chapters(*, lessons(*))")
        .eq("id", str(course_id))
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id '{course_id}' not found",
        )

    course = result.data[0]
    # Sort chapters by position
    if course.get("chapters"):
        for chapter in course["chapters"]:
            # Sort lessons by position
            if chapter.get("lessons"):
                chapter["lessons"] = sorted(chapter["lessons"], key=lambda x: x.get("position", 0))
        
        course["chapters"] = sorted(course["chapters"], key=lambda x: x.get("position", 0))

    return course


@router.get("/slug/{slug}", response_model=CourseWithChapters)
def get_course_by_slug(slug: str):
    """Get course by slug with chapters"""
    result = (
        supabase_client.table("courses")
        .select("*, chapters(*, lessons(*))")
        .eq("slug", slug)
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with slug '{slug}' not found",
        )

    course = result.data[0]
    
    # Sort chapters and lessons (since API might return them unsorted)
    if course.get("chapters"):
        for chapter in course["chapters"]:
            if chapter.get("lessons"):
                chapter["lessons"] = sorted(chapter["lessons"], key=lambda x: x.get("position", 0))
        
        course["chapters"] = sorted(course["chapters"], key=lambda x: x.get("position", 0))

    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: uuid.UUID, course_update: CourseUpdate):
    """Update course"""
    # Check existence
    existing = (
        supabase_client.table("courses")
        .select("id")
        .eq("id", str(course_id))
        .execute()
    )
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id '{course_id}' not found",
        )

    update_data = course_update.model_dump(exclude_unset=True)
    if not update_data:
        # Nothing to update, fetch and return
        return (
            supabase_client.table("courses")
            .select("*")
            .eq("id", str(course_id))
            .single()
            .execute()
            .data
        )

    result = (
        supabase_client.table("courses")
        .update(update_data)
        .eq("id", str(course_id))
        .execute()
    )
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update course")
        
    return result.data[0]


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: uuid.UUID):
    """Delete course"""
    result = (
        supabase_client.table("courses")
        .delete()
        .eq("id", str(course_id))
        .execute()
    )
    
    # Verify deletion (Supabase delete returns deleted rows)
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id '{course_id}' not found",
        )
    
    return None
