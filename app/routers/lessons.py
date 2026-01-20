from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import List
import uuid

from app.supabase_client import get_client
from app.schemas import LessonCreate, LessonUpdate, LessonResponse, ReorderLessons
from app.services.r2_service import r2_service

router = APIRouter(prefix="/api/lessons", tags=["lessons"])

# Helper to get supabase client
def supabase_client():
    return get_client()


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(lesson: LessonCreate):
    """Create a new lesson"""
    # Verify chapter exists
    chapter_exists = (
        supabase_client.table("chapters")
        .select("id")
        .eq("id", str(lesson.chapter_id))
        .execute()
    )
    if not chapter_exists.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id '{lesson.chapter_id}' not found",
        )

    # Check unique slug
    existing = (
        supabase_client.table("lessons")
        .select("id")
        .eq("slug", lesson.slug)
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lesson with slug '{lesson.slug}' already exists",
        )

    # Prepare data (map schema fields to DB columns if necessary)
    data = lesson.model_dump()
    if "fileKey" in data:
        data["mdx_path"] = data.pop("fileKey")
    
    # Ensure foreign keys are strings
    data["chapter_id"] = str(data["chapter_id"])
    
    # Convert date objects to isoformat if needed, though supabase-py might handle it.
    if data.get("published_at"):
        data["published_at"] = data["published_at"].isoformat()

    result = supabase_client.table("lessons").insert(data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create lesson")
    
    # Map back for response if needed, although Pydantic might handle 'mdx_path' to 'fileKey' if aliases were set. 
    # But LessonBase defines 'fileKey'.
    # If DB returns 'mdx_path', we might need to map it back to 'fileKey' for the response model 
    # OR update schema to have mdx_path as alias.
    # For now, let's manually patch the response dict
    response_data = result.data[0]
    response_data["fileKey"] = response_data.get("mdx_path")
    
    return response_data


@router.get("/chapter/{chapter_id}", response_model=List[LessonResponse])
def list_lessons_by_chapter(chapter_id: uuid.UUID):
    """List all lessons for a chapter, ordered by position"""
    result = (
        supabase_client.table("lessons")
        .select("*")
        .eq("chapter_id", str(chapter_id))
        .order("position", descending=False)
        .execute()
    )
    
    lessons = result.data
    for l in lessons:
        l["fileKey"] = l.get("mdx_path")
        
    return lessons


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(lesson_id: uuid.UUID):
    """Get lesson by ID"""
    result = (
        supabase_client.table("lessons")
        .select("*")
        .eq("id", str(lesson_id))
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id '{lesson_id}' not found",
        )
    
    lesson = result.data
    lesson["fileKey"] = lesson.get("mdx_path")
    return lesson


@router.get("/slug/{slug}", response_model=LessonResponse)
def get_lesson_by_slug(slug: str):
    """Get lesson by slug"""
    result = (
        supabase_client.table("lessons")
        .select("*")
        .eq("slug", slug)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with slug '{slug}' not found",
        )

    lesson = result.data
    lesson["fileKey"] = lesson.get("mdx_path")
    return lesson


@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: uuid.UUID, lesson_update: LessonUpdate
):
    """Update lesson"""
    # Check existence
    existing = (
        supabase_client.table("lessons")
        .select("id")
        .eq("id", str(lesson_id))
        .execute()
    )
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id '{lesson_id}' not found",
        )

    update_data = lesson_update.model_dump(exclude_unset=True)
    if "fileKey" in update_data:
        update_data["mdx_path"] = update_data.pop("fileKey")
        
    if update_data.get("published_at"):
        update_data["published_at"] = update_data["published_at"].isoformat()

    if not update_data:
         # Return existing
         return get_lesson(lesson_id)

    result = (
        supabase_client.table("lessons")
        .update(update_data)
        .eq("id", str(lesson_id))
        .execute()
    )
    
    if not result.data:
         raise HTTPException(status_code=500, detail="Failed to update lesson")
    
    lesson = result.data[0]
    lesson["fileKey"] = lesson.get("mdx_path")
    return lesson


@router.post("/upload-content")
async def upload_lesson_content(
    file: UploadFile = File(...), lesson_id: uuid.UUID = Form(...)
):
    """Upload MDX content for a lesson to Supabase Storage"""
    try:
        if not file.filename or not file.filename.endswith(".mdx"):
            raise HTTPException(status_code=400, detail="Only .mdx files allowed")

        file_content = await file.read()
        
        # Path in bucket
        file_path = f"{lesson_id}.mdx"
        bucket_name = "lesson-content"
        
        # Upload (upsert=True to overwrite)
        # Try upload with upsert=true
        try:
            res = supabase_client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "text/markdown", "upsert": "true"}
            )
        except Exception as storage_err:
            print(f"Upload with upsert failed, trying update: {storage_err}")
            # Fallback to update if upload failed (e.g. if file strictly exists)
            try:
                res = supabase_client.storage.from_(bucket_name).update(
                    path=file_path,
                    file=file_content,
                    file_options={"content-type": "text/markdown", "upsert": "true"}
                )
            except Exception as update_err:
                 print(f"Update also failed: {update_err}")
                 raise HTTPException(status_code=500, detail=f"Storage save failed: {str(update_err)}")

        # Update DB 
        supabase_client.table("lessons").update({"mdx_path": file_path}).eq("id", str(lesson_id)).execute()

        return {"success": True, "file_key": file_path, "lesson_id": lesson_id}
    except Exception as e:
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-image")
async def upload_lesson_image(
    file: UploadFile = File(...), lesson_id: uuid.UUID = Form(...)
):
    """Upload an image for a lesson to Supabase Storage"""
    try:
        # Validate file type
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
        file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported image format")

        file_content = await file.read()
        
        # Path in bucket: lessons/{lesson_id}/{timestamp}_{filename}
        timestamp = int(uuid.uuid4().hex[:8], 16) # use some random bits
        safe_filename = "".join([c if c.isalnum() or c in "._-" else "_" for c in file.filename])
        file_path = f"{lesson_id}/{timestamp}_{safe_filename}"
        bucket_name = "lesson-images"
        
        # Upload
        upload_res = supabase_client.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type, "upsert": "true"}
        )

        # Check for error in upload result (depending on supabase-py version)
        # Note: If upload fails, it usually raises an exception, caught by except block.

        # Get public URL
        public_url = supabase_client.storage.from_(bucket_name).get_public_url(file_path)
        
        # Verify if it returns an object or string (new versions return string directly)
        if isinstance(public_url, dict):
            public_url = public_url.get("publicURL")

        print(f"Image uploaded to: {public_url}")
        return {"success": True, "url": public_url, "file_path": file_path}
    except Exception as e:
        print(f"Image Upload Error Detail: {str(e)}")
        # If bucket missing, inform the user
        if "bucket_not_found" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found. Please create it in Supabase Storage.")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


@router.get("/{lesson_id}/content")
def get_lesson_content(lesson_id: uuid.UUID):
    """Get lesson MDX content from Supabase Storage"""
    result = (
        supabase_client.table("lessons")
        .select("mdx_path")
        .eq("id", str(lesson_id))
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson not found"
        )
    
    mdx_path = result.data.get("mdx_path")

    if not mdx_path:
        # Return empty content or default template instead of 404/500 if just missing file
        return {"success": True, "content": "", "mdx_path": None}

    try:
        bucket_name = "lesson-content"
        data = supabase_client.storage.from_(bucket_name).download(mdx_path)
        content_str = data.decode('utf-8')
        return {"success": True, "content": content_str, "mdx_path": mdx_path}
    except Exception as e:
        print(f"Download Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch content: {str(e)}"
        )


@router.post("/reorder", response_model=dict)
def reorder_lessons(reorder_data: ReorderLessons):
    """Reorder lessons (for drag & drop)"""
    for item in reorder_data.lesson_positions:
        lesson_id = str(item["id"]) if isinstance(item["id"], uuid.UUID) else item["id"]
        new_position = item["position"]

        supabase_client.table("lessons").update({"position": new_position}).eq("id", lesson_id).execute()

    return {"success": True, "message": "Lessons reordered"}


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(lesson_id: uuid.UUID):
    """Delete lesson"""
    # Get lesson first to get mdx_path for R2 deletion
    existing = (
        supabase_client.table("lessons")
        .select("mdx_path")
        .eq("id", str(lesson_id))
        .single()
        .execute()
    )
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id '{lesson_id}' not found",
        )
    
    mdx_path = existing.data.get("mdx_path")

    # Delete from DB
    result = (
        supabase_client.table("lessons")
        .delete()
        .eq("id", str(lesson_id))
        .execute()
    )

    # Optionally delete from R2
    if mdx_path:
        try:
            r2_service.delete_lesson(mdx_path)
        except Exception as e:
            print(f"Warning: Could not delete R2 file: {e}")

    return None
