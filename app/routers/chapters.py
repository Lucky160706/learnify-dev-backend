from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from app.supabase_client import get_client
from app.schemas import (
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    ChapterWithLessons,
    ReorderChapters,
)

router = APIRouter(prefix="/api/chapters", tags=["chapters"])

# Helper to get supabase client
def supabase_client():
    return get_client()


@router.post("/", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(chapter: ChapterCreate):
    """Create a new chapter"""
    # Verify course exists
    course_exists = (
        supabase_client().table("courses")
        .select("id")
        .eq("id", str(chapter.course_id))
        .execute()
    )
    if not course_exists.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id '{chapter.course_id}' not found",
        )

    # Check unique slug per course
    existing = (
        supabase_client().table("chapters")
        .select("id")
        .eq("course_id", str(chapter.course_id))
        .eq("slug", chapter.slug)
        .execute()
    )

    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chapter with slug '{chapter.slug}' already exists in this course",
        )

    data = chapter.model_dump()
    data["course_id"] = str(data["course_id"])
    result = supabase_client().table("chapters").insert(data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create chapter")
        
    return result.data[0]


@router.get("/course/{course_id}", response_model=List[ChapterWithLessons])
def list_chapters_by_course(course_id: uuid.UUID):
    """List all chapters for a course, ordered by position"""
    # Nested select: *, lessons(*)
    result = (
        supabase_client().table("chapters")
        .select("*, lessons(*)")
        .eq("course_id", str(course_id))
        .order("position", descending=False)
        .execute()
    )
    
    chapters = result.data
    # Sort lessons inside chapters
    for chapter in chapters:
        if chapter.get("lessons"):
             chapter["lessons"] = sorted(chapter["lessons"], key=lambda x: x.get("position", 0))

    return chapters


@router.get("/{chapter_id}", response_model=ChapterWithLessons)
def get_chapter(chapter_id: uuid.UUID):
    """Get chapter by ID with lessons"""
    result = (
        supabase_client().table("chapters")
        .select("*, lessons(*)")
        .eq("id", str(chapter_id))
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id '{chapter_id}' not found",
        )
    
    chapter = result.data[0]
    if chapter.get("lessons"):
             chapter["lessons"] = sorted(chapter["lessons"], key=lambda x: x.get("position", 0))

    return chapter


@router.put("/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    chapter_id: uuid.UUID, chapter_update: ChapterUpdate
):
    """Update chapter"""
    # Check existence
    existing = (
        supabase_client().table("chapters")
        .select("id")
        .eq("id", str(chapter_id))
        .execute()
    )
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id '{chapter_id}' not found",
        )

    update_data = chapter_update.model_dump(exclude_unset=True)
    if not update_data:
        return (
            supabase_client().table("chapters")
            .select("*")
            .eq("id", str(chapter_id))
            .single()
            .execute()
            .data
        )

    result = (
        supabase_client().table("chapters")
        .update(update_data)
        .eq("id", str(chapter_id))
        .execute()
    )
    
    if not result.data:
         raise HTTPException(status_code=500, detail="Failed to update chapter")

    return result.data[0]


@router.post("/reorder", response_model=dict)
def reorder_chapters(reorder_data: ReorderChapters):
    """Reorder chapters (for drag & drop)"""
    # Note: This is an expensive operation if done one by one. 
    # Supabase/Postgrest doesn't support bulk update easily.
    # We will do loop updates for now.
    
    for item in reorder_data.chapter_positions:
        chapter_id = (
            str(item["id"]) if isinstance(item["id"], uuid.UUID) else item["id"]
        )
        new_position = item["position"]

        supabase_client().table("chapters").update({"position": new_position}).eq("id", chapter_id).execute()

    return {"success": True, "message": "Chapters reordered"}


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(chapter_id: uuid.UUID):
    """Delete chapter (cascade delete lessons)"""
    # Assuming Supabase has Cascade ON DELETE on foreign keys set up in DB schema.
    # If not, we might need to manually delete lessons first, but RDBMS usually handle this.
    
    result = (
        supabase_client().table("chapters")
        .delete()
        .eq("id", str(chapter_id))
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id '{chapter_id}' not found",
        )

    return None
