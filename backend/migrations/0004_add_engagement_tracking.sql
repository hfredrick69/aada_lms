-- Add engagement tracking fields to module_progress table
-- Run this migration: docker exec aada_lms-db-1 psql -U aada_admin -d aada_lms -f /migrations/0004_add_engagement_tracking.sql

ALTER TABLE module_progress
ADD COLUMN IF NOT EXISTS last_scroll_position INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS active_time_seconds INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS sections_viewed JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS last_accessed_at TIMESTAMP WITH TIME ZONE;

-- Add index on last_accessed_at for performance
CREATE INDEX IF NOT EXISTS idx_module_progress_last_accessed
ON module_progress(last_accessed_at);

-- Add comment for documentation
COMMENT ON COLUMN module_progress.last_scroll_position IS 'Last scroll position in pixels for resume functionality';
COMMENT ON COLUMN module_progress.active_time_seconds IS 'Total active time (page focused + user activity)';
COMMENT ON COLUMN module_progress.sections_viewed IS 'Array of section IDs that student has scrolled through';
COMMENT ON COLUMN module_progress.last_accessed_at IS 'Timestamp of last progress update';
