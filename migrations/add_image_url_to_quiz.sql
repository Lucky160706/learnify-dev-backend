-- Migration: Add image_url columns for quiz questions and options
-- Run this in Supabase SQL Editor

-- 1. Add image_url column to quiz_questions
ALTER TABLE quiz_questions ADD COLUMN image_url TEXT NULL;

-- 2. Add image_url column to quiz_options  
ALTER TABLE quiz_options ADD COLUMN image_url TEXT NULL;

-- Verify the migration
SELECT table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name IN ('quiz_questions', 'quiz_options') 
AND column_name = 'image_url';
