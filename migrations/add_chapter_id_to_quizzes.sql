-- Migration: Add chapter_id to quizzes for per-chapter quiz support
-- Run this in Supabase SQL Editor

-- 1. Add chapter_id column (nullable FK to chapters)
ALTER TABLE quizzes ADD COLUMN chapter_id UUID NULL REFERENCES chapters(id) ON DELETE CASCADE;

-- 2. Drop existing unique constraint on course_id if it exists
-- (The SQLAlchemy model had unique=True on course_id)
-- Check and drop if exists:
DO $$ 
BEGIN
    -- Try to drop constraint by common naming patterns
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'quizzes_course_id_key') THEN
        ALTER TABLE quizzes DROP CONSTRAINT quizzes_course_id_key;
    END IF;
END $$;

-- Also check for unique index
DROP INDEX IF EXISTS quizzes_course_id_key;

-- 3. Create partial unique index: one quiz per chapter
CREATE UNIQUE INDEX IF NOT EXISTS unique_course_chapter_quiz 
ON quizzes(course_id, chapter_id) 
WHERE chapter_id IS NOT NULL;

-- 4. (Optional) Create partial unique index: one course-level quiz per course
-- Uncomment if you want to enforce only one final quiz per course
-- CREATE UNIQUE INDEX IF NOT EXISTS unique_course_final_quiz 
-- ON quizzes(course_id) 
-- WHERE chapter_id IS NULL;

-- Verify the migration
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'quizzes' AND column_name = 'chapter_id';
